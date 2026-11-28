"""Materialize small, versioned P1 input configs; never run the model or a build."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def git_blob(repo: Path, commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{relative}"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return result.stdout


def source_manifest(relative: str, payload: bytes) -> dict:
    return {"path": relative, "bytes": len(payload), "sha256": digest(payload)}


def set_parameter(container: ET.Element, name: str, value: object) -> None:
    parameter = container.find(f"./Parameters/{name}")
    if parameter is None:
        raise ValueError(f"missing_parameter:{name}")
    parameter.text = str(value)


def patched_model(payload: bytes, row: dict) -> bytes:
    root = ET.fromstring(payload)
    model = root.find("./Model")
    if model is None:
        raise ValueError("missing_model")
    source = model.find("./Components/PGenerator")
    axon = model.find("./Components/AxoneUnderTest")
    if source is None or axon is None:
        raise ValueError("missing_source_or_axon")
    if source.get("Class") != "NPGenerator" or axon.get("Class") != row["class"]:
        raise ValueError("unexpected_template_component_class")
    # NPGenerator is the registered ordinary NPulseGenerator image in this fixture.
    for name, value in (
        ("Frequency", "10"), ("PulseLength", "0.001"),
        ("Amplitude", "1"), ("Delay", "0"), ("FrequencyDeviation", "0"),
    ):
        set_parameter(source, name, value)
    set_parameter(axon, row["length_param"], row["length_value"])
    if row["class"] == "NAxoneChainAndDelay":
        set_parameter(axon, "InternodeDelayTime", "0.002")
    ET.indent(root, space="\t")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def patched_project(payload: bytes, frequency: int, case_id: str) -> bytes:
    text = payload.decode("utf-8-sig").replace("\r\n", "\n")
    # Existing Rdk project files contain a <00> channel tag and are not standard XML.
    for name, value in (
        ("DefaultTimeStep", frequency), ("GlobalTimeStep", frequency),
        ("ProjectName", case_id), ("ProjectAutoSaveFlag", 0),
        ("ProjectAutoSaveStateFlag", 0),
    ):
        pattern = rf"(<{name}>)[^<]*(</{name}>)"
        text, count = re.subn(pattern, lambda match: f"{match[1]}{value}{match[2]}", text)
        if count != 1:
            raise ValueError(f"unexpected_project_field_count:{name}:{count}")
    return text.encode("utf-8")


def write_source(path: Path, payload: bytes, *, overwrite: bool) -> None:
    if len(payload) > 1024 * 1024:
        raise ValueError(f"source_config_exceeds_1MiB:{path.name}")
    if path.exists():
        if path.read_bytes() == payload:
            return
        if not overwrite:
            raise FileExistsError(f"refusing_to_replace_different_source:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def materialize(repo_root: Path, recipe_path: Path, output: Path, *, overwrite: bool = False) -> dict:
    repo_root, recipe_path, output = repo_root.resolve(), recipe_path.resolve(), output.resolve()
    config_root = (repo_root / "Bin/Configs").resolve()
    if not output.is_relative_to(config_root) or output == config_root:
        raise ValueError("output_must_be_below_Bin_Configs")
    recipe_bytes = recipe_path.read_bytes()
    recipe = json.loads(recipe_bytes)
    if recipe.get("kind") != "axone_component_config_recipe" or recipe.get("schema_version") != 1:
        raise ValueError("unsupported_recipe")
    commit = recipe["source_bin_commit"]
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("invalid_source_commit")
    frequencies = recipe["frequencies_hz"]
    if (not frequencies or any(type(value) is not int or value <= 0 for value in frequencies)
            or len(frequencies) != len(set(frequencies))):
        raise ValueError("invalid_frequencies")
    bin_repo = repo_root / "Bin"
    study = recipe["source_study"]
    if study != "Configs/SpikeSamples/NeuralElements/AxoneLengthDelayStudy":
        raise ValueError("unsupported_source_study")
    grid_path = f"{study}/grid_cells.tsv"
    grid_bytes = git_blob(bin_repo, commit, grid_path)
    rows = list(csv.DictReader(io.StringIO(grid_bytes.decode("utf-8-sig")), delimiter="\t"))
    if len(rows) != recipe["expected_legacy_cells"]:
        raise ValueError("unexpected_legacy_grid_size")
    allowed = {
        "NAxoneDelay": ("DelayTime", "delay"),
        "NAxoneChain": ("NumSegments", "chain"),
        "NAxoneChainAndDelay": ("NumNodes", "chain_and_delay"),
    }
    seen = set()
    for row in rows:
        if not re.fullmatch(r"[a-z0-9_]+", row["cell"]) or row["cell"] in seen:
            raise ValueError("invalid_or_duplicate_legacy_cell")
        seen.add(row["cell"])
        if allowed.get(row["class"]) != (row["length_param"], row["template"]):
            raise ValueError("unexpected_legacy_class_or_parameter")
        if row["class"] != "NAxoneDelay" and int(row["length_value"]) < 1:
            raise ValueError("invalid_structural_length")

    # All source bytes come from the pinned Git objects, independent of checkout EOL.
    template_names = ("Model_00.xml", "Parameters_00.xml", "Interface.xml", "History.xml", "project.ini")
    templates = {}
    for template in sorted({row["template"] for row in rows}):
        files = {}
        records = []
        for name in template_names:
            relative = f"{study}/templates/{template}/{name}"
            payload = git_blob(bin_repo, commit, relative)
            files[name] = payload
            records.append(source_manifest(relative, payload))
        templates[template] = (files, records)

    cases = []
    for frequency in frequencies:
        for row in rows:
            case_id = f'{row["cell"]}__f{frequency}'
            case_dir = output / case_id
            template_files, template_records = templates[row["template"]]
            payloads = {}
            for name in ("Model_00.xml", "Parameters_00.xml"):
                payloads[name] = patched_model(template_files[name], row)
            for name in ("Interface.xml", "History.xml"):
                # Preserve the declared GUI input, never copy any StatisticLog or result.
                payloads[name] = template_files[name].replace(b"\r\n", b"\n")
            payloads["project.ini"] = patched_project(template_files["project.ini"], frequency, case_id)
            condition = {
                "kind": "axone_component_initial_condition", "schema_version": 1,
                "protocol_id": recipe["protocol_id"], "case_id": case_id,
                "status": "prepared_requires_native_validation",
                "source_bin_commit": commit,
                "source_grid": source_manifest(grid_path, grid_bytes),
                "source_templates": template_records,
                "generator": {
                    "image_class": "NPGenerator", "cpp_class": "NPulseGenerator",
                    "frequency_hz": 10, "pulse_length_s": 0.001,
                    "amplitude": 1, "initial_delay_s": 0,
                },
                "axon": {
                    "class": row["class"], "length_parameter": row["length_param"],
                    "length_value": (float(row["length_value"]) if row["class"] == "NAxoneDelay" else int(row["length_value"])),
                    "length_unit": row["length_unit"],
                    "internode_delay_s": 0.002 if row["class"] == "NAxoneChainAndDelay" else None,
                },
                "frequency_hz": frequency, "model_duration_s": 0.5,
                "required_execution_host": "10.245.1.15",
                "runtime_outputs": "outside_source_checkout",
                "native_preflight": [
                    "verify_actual_frequency_and_derived_coefficients",
                    "verify_actual_segment_count_after_Build",
                    "verify_source_and_terminal_links",
                    "capture_actual_emissions_and_all_output_events",
                    "reserve_external_output_space",
                ],
                "input_files": [
                    source_manifest(name, payload) for name, payload in sorted(payloads.items())
                ],
                "scientific_result": None,
            }
            payloads["condition.json"] = encoded(condition)
            payloads["README.md"] = (
                f"# P1 {case_id}\n\n"
                "Подготовленный исходный конфиг; новое исполнение модели не выполнено.\n\n"
                f'Компонент {row["class"]}, {row["length_param"]}={row["length_value"]}; '
                f"частота расчёта {frequency} Гц.\n\n"
                "Источник — стандартный NPulseGenerator (образ NPGenerator), "
                "10 Гц, ширина 1 мс, амплитуда 1. Окно базового опыта 0,5 с.\n\n"
                "На .15 сначала проверить частоту, структуру после Build и реальные связи. "
                "Скопировать весь комплект в отдельный каталог запуска вне исходников. "
                "Запускать модель только из рабочей копии конфига. Не сохранять "
                "автосостояние или журналы в Bin/Configs.\n"
            ).encode("utf-8")
            for name, payload in payloads.items():
                write_source(case_dir / name, payload, overwrite=overwrite)
            cases.append({
                "case_id": case_id, "directory": case_id, "frequency_hz": frequency,
                "axon_class": row["class"],
                "files": [source_manifest(name, payload) for name, payload in sorted(payloads.items())],
            })

    manifest = {
        "kind": "axone_component_config_manifest", "schema_version": 1,
        "protocol_id": recipe["protocol_id"], "status": "prepared_requires_native_validation",
        "recipe": {"sha256": digest(recipe_bytes), "bytes": len(recipe_bytes)},
        "source_bin_commit": commit, "case_count": len(cases), "cases": cases,
        "scientific_result": None,
    }
    write_source(output / "manifest.json", encoded(manifest), overwrite=overwrite)
    return {
        "case_count": len(cases), "output": str(output),
        "native_execution_performed": False, "build_performed": False,
        "status": "prepared_requires_native_validation",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--recipe", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    base = root / "Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner"
    result = materialize(
        root, args.recipe or base / "protocols/P1-component-baseline.json",
        args.output or base / "P1/component-baseline", overwrite=args.overwrite,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
