#!/usr/bin/env python3
"""Extract the local historical evidence and prepare isolated replay inputs.

Only Python's standard library is needed. Source Office files and the four
verbatim configuration copies are never modified. Missing historical results
remain missing; cached spreadsheet values are not recalculated or invented.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "Docs/ClassicStructTrainExperiments"
CONFIGS = REPO / "Bin/Configs/StructTrainClassic"
REPORTS = REPO / "Reports/StructTrainClassic"
IDS = [22, 37, 45, 60, 64, 84, 90, 111, 129, 134]
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def workbook(path: Path) -> dict:
    """Return cell-addressed cached values plus formula text, without Excel."""
    result = {}
    with ZipFile(path) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(n.text or "" for n in si.findall(".//s:t", NS))
                       for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        rels = {e.get("Id"): e.get("Target") for e in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        for sheet in ET.fromstring(z.read("xl/workbook.xml")).find("s:sheets", NS):
            target = rels[sheet.get("{" + NS["r"] + "}id")]
            target = target.lstrip("/") if target.startswith("/") else "xl/" + target
            cells = {}
            for c in ET.fromstring(z.read(target)).findall(".//s:sheetData/s:row/s:c", NS):
                v, f = c.find("s:v", NS), c.find("s:f", NS)
                value = v.text if v is not None else None
                if c.get("t") == "s" and value is not None:
                    value = strings[int(value)]
                elif c.get("t") == "inlineStr":
                    value = "".join(n.text or "" for n in c.findall(".//s:t", NS))
                elif value is not None and c.get("t") not in ("str", "e", "b"):
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                if value is not None or f is not None:
                    cells[c.get("r")] = {"value": value, "formula": f.text if f is not None else None}
            result[sheet.get("name")] = cells
    return result


def value(cells, address, default=None):
    return cells.get(address, {}).get("value", default)


def vector(cells, row, cols):
    vs = [value(cells, f"{c}{row}") for c in cols]
    return vs if all(isinstance(v, (float, int)) for v in vs) else None


def column(index):
    text = ""
    while index:
        index, rem = divmod(index - 1, 26)
        text = chr(65 + rem) + text
    return text


def columns(start, count=5):
    number = 0
    for ch in start:
        number = number * 26 + ord(ch) - 64
    return [column(i) for i in range(number, number + count)]


def extract_evidence():
    protocols = workbook(ARCHIVE / "Эксперименты/Тестирование/Протоколы экспериментов.xlsx")
    data = protocols["Датасет"]
    dataset = []
    for row in range(2, 152):
        pattern = vector(data, row, list("BCDEF"))
        ident = value(data, f"A{row}")
        if ident != row - 1 or pattern is None or len(pattern) != 5:
            raise ValueError(f"Invalid archived dataset row {row}")
        dataset.append({"id": ident, "class": (ident - 1) // 50 + 1, "pattern": pattern,
                        "source": {"sheet": "Датасет", "range": f"A{row}:F{row}"}})
    cold = []
    cells = protocols["Корректность обучения с нуля"]
    for row in range(1, 97):
        label = value(cells, f"I{row}", "")
        if not isinstance(label, str) or not re.fullmatch(r"КО\.[123]\.\d+", label):
            continue
        for kind in ["learner", "trainer"]:
            cold.append({"case": label, "repeat": int(label.split(".")[1]), "id": value(cells, f"J{row}"),
                         "kind": kind, "pattern": vector(cells, row, columns("K")),
                         "dendrites": vector(cells, row, columns("U" if kind == "learner" else "P")),
                         "synapses": vector(cells, row, columns("AF" if kind == "learner" else "AA")),
                         "iterations": value(cells, f"{'BG' if kind == 'learner' else 'BJ'}{row}"),
                         "dendrite_iterations": value(cells, f"{'BH' if kind == 'learner' else 'BK'}{row}"),
                         "synapse_iterations": value(cells, f"{'BI' if kind == 'learner' else 'BL'}{row}"),
                         "source": {"sheet": "Корректность обучения с нуля", "row": row}})
    if len(cold) != 60:
        raise ValueError(f"Expected 60 cold references, got {len(cold)}")
    warm = []
    for repeat in range(1, 4):
        name = f"Коррект. обучения НЕ с нуля ({repeat})"
        cells = protocols[name]
        for row in range(3, 95):
            label = value(cells, f"J{row}", "")
            if isinstance(label, str) and label.startswith(f"КП.{repeat}."):
                warm.append({"case": label, "repeat": repeat,
                             "pattern": vector(cells, row, columns("M")),
                             "from_index": value(cells, f"K{row}"), "to_index": value(cells, f"L{row}"),
                             "dendrites": vector(cells, row, columns("AB")),
                             "synapses": vector(cells, row, columns("AG")),
                             "iterations": value(cells, f"BK{row}"), "source": {"sheet": name, "row": row}})
    if len(warm) != 270:
        raise ValueError(f"Expected 270 warm references, got {len(warm)}")
    modes = []
    cells = protocols["Режимы"]
    mode_patterns = [vector(cells, row, columns("T")) for row in range(5, 9)]
    for row in list(range(4, 32)) + list(range(35, 39)):
        modes.append({"case": f"mode-{row-3}" if row < 32 else f"pattern-change-{row-34}",
                      "source_row": row, "values": {c: value(cells, f"{c}{row}") for c in list("GHIJKLMNOPQR")}})
    structural_book = workbook(ARCHIVE / "Эксперименты/Инофрмация о длинах дендритов и числе синапсов.xlsx")
    structural = []
    cells = structural_book["Дендриты и синапсы"]
    for row in range(2, 152):
        for kind in ["learner", "trainer"]:
            structural.append({"id": row - 1, "kind": kind,
                               "dendrites": vector(cells, row, columns("L" if kind == "learner" else "G")),
                               "synapses": vector(cells, row, columns("W" if kind == "learner" else "R")),
                               "raw_synapses": [value(cells, f"{c}{row}") for c in columns("W" if kind == "learner" else "R")],
                               "source_row": row})
    recognition_book = workbook(ARCHIVE / "Эксперименты/Тестирование/Распознавание/Распознавание.xlsx")
    cells = recognition_book["Sheet1"]
    recognition = []
    current_id = None
    for c in columns("H", 22):
        ident = value(cells, f"{c}1")
        if isinstance(ident, (float, int)):
            current_id = int(ident)
        label = value(cells, f"{c}2")
        answers = [value(cells, f"{c}{r}") for r in range(3, 153)]
        if current_id is None or any(x not in (0, 1) for x in answers):
            raise ValueError(f"Invalid historical recognition column {c}")
        recognition.append({"id": current_id, "kind": "trainer" if str(label).startswith("NT") else "learner",
                            "variant": label, "answers": answers, "source_range": f"{c}1:{c}152"})
    research = workbook(ARCHIVE / "Эксперименты/Исследование/Обучение нескольким примерам.xlsx")
    return {"dataset": dataset, "cold": cold, "warm": warm, "modes": modes, "mode_patterns": mode_patterns,
            "structural": structural, "recognition": recognition, "research_sheets": research}


def set_parameter(params, name, text, typ="int"):
    node = params.find(name)
    if node is None:
        node = ET.SubElement(params, name, {"Type": typ, "PType": "257", "IoType": "17"})
    node.text = str(text)
    return node


def make_template(kind, pattern):
    source_name = "relearning_1" if kind == "learner" else "Autocreate2022.03.11 11_12_05"
    source = CONFIGS / source_name
    source_tree = ET.parse(source / "Parameters_00.xml")
    class_name = "NNeuronLearner" if kind == "learner" else "NNeuronTrainer"
    candidates = [n for n in source_tree.iter() if n.get("Class") == class_name]
    component = next((n for n in candidates if (n.findtext("Parameters/Activity") or "").strip() == "1"), candidates[0])
    root = ET.Element("Save", {"ModelName": "Model"})
    model = ET.SubElement(root, "Model", {"Class": "Model"})
    model.append(copy.deepcopy(source_tree.getroot().find("Model/Parameters")))
    ET.SubElement(model, "Links", {"Type": "ULinksList", "Size": "0"})
    subject = ET.SubElement(ET.SubElement(model, "Components"), "Subject", {"Class": class_name})
    params = copy.deepcopy(component.find("Parameters"))
    subject.append(params)
    for name in ["DataFromFile", "DendriteNeuronAmplitude", "SomaNeuronAmplitude", "NeuronAmplitude", "Output"]:
        node = params.find(name)
        if node is not None:
            params.remove(node)
    for name, text in {"Activity": 1, "StructureBuildMode": 1, "CalculateMode": 0 if kind == "learner" else 6,
                       "IsNeedToTrain": 1, "NumInputDendrite": 5, "MaxDendriteLength": 100,
                       "ExperimentMode": 0, "ExperimentNum": 0, "EnableDebug": 0}.items():
        if kind == "trainer" and name in ["ExperimentMode", "ExperimentNum"]:
            continue
        set_parameter(params, name, text, "bool" if name in ["Activity", "IsNeedToTrain", "ExperimentMode", "EnableDebug"] else "int")
    node = set_parameter(params, "InputPattern", "\n".join(format(v, ".17g") for v in pattern), "MDMatrix<double>")
    node.set("Rows", "5")
    node.set("Cols", "1")
    if kind == "learner":
        set_parameter(params, "DendriteLength", "1 1 1 1 1", "std::vector<int>")
        set_parameter(params, "NumSynapse", "1 1 1 1 1", "std::vector<int>")
        set_parameter(params, "InitialSomaPotential", "0 0 0 0 0", "std::vector<double>")
    ET.SubElement(subject, "Links", {"Type": "ULinksList", "Size": "0"})
    ET.SubElement(subject, "Components")
    output = CONFIGS / "Prepared" / kind
    output.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="\t")
    ET.ElementTree(root).write(output / "Model_00.xml", encoding="utf-8", xml_declaration=False)
    properties = copy.deepcopy(root)
    properties.tag = "SaveProperties"
    ET.ElementTree(properties).write(output / "Parameters_00.xml", encoding="utf-8", xml_declaration=False)
    project = (source / "project.ini").read_text(encoding="utf-8-sig")
    for name, val in {"ProjectAutoSaveFlag": 0, "ProjectAutoSaveStateFlag": 0, "DebugModeFlag": 0,
                      "MinInterstepsInterval": 0, "InitAfterLoadFlag": 1, "ResetAfterLoadFlag": 1}.items():
        project = re.sub(rf"(<{name}>).*?(</{name}>)", lambda m: m[1] + str(val) + m[2], project)
    (output / "project.ini").write_text(project, encoding="utf-8")
    (output / "Interface.xml").write_text("<Interfaces />\n", encoding="utf-8")
    return {"kind": kind, "config": str((output / "project.ini").relative_to(REPO)).replace("\\", "/"),
            "source": source_name, "reconstruction": "Scalar archived settings; native branch classes build fresh structure; no saved trained state reused."}


def prepare():
    source = ARCHIVE / "Эксперименты/Тестирование/Configs"
    copied = []
    for path in sorted(source.rglob("*")):
        if path.is_file():
            target = CONFIGS / path.relative_to(source)
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
            if sha(path) != sha(target):
                raise ValueError(f"Verbatim configuration differs: {target}")
            copied.append({"path": str(path.relative_to(source)), "sha256": sha(path)})
    evidence = extract_evidence()
    dataset = evidence["dataset"]
    sequence_path = source / "relearning_1/input_data.txt"
    sequence = []
    for line in sequence_path.read_text().splitlines():
        if not line.strip():
            continue
        pattern = list(map(float, line.split()))
        if len(pattern) != 5 or not all(math.isfinite(v) for v in pattern):
            raise ValueError("Invalid archived sequence")
        sample = min(dataset, key=lambda s: max(abs(a-b) for a, b in zip(s["pattern"], pattern)))
        if max(abs(a-b) for a, b in zip(sample["pattern"], pattern)) > 0.00006:
            raise ValueError("Sequence pattern not found in Iris")
        sequence.append({"id": sample["id"], "pattern": pattern})
    pairs = [(a["id"], b["id"]) for a, b in zip(sequence, sequence[1:])]
    if len(sequence) != 91 or len(set(pairs)) != 90 or any(a == b for a, b in pairs):
        raise ValueError("Archived transition coverage is not exactly 90 directed pairs")
    templates = [make_template(kind, dataset[21]["pattern"]) for kind in ["learner", "trainer"]]
    native = CONFIGS / "Prepared/native_relearning"
    shutil.copytree(source / "relearning_2", native, dirs_exist_ok=True)
    # Only compatibility changes in this diagnostic copy; its archived raw
    # structure is retained so console diagnostics can expose load differences.
    for filename in ["Model_00.xml", "Parameters_00.xml"]:
        p = native / filename
        tree = ET.parse(p)
        for component in tree.iter():
            if component.get("Class") == "NNeuronLearner":
                ps = component.find("Parameters")
                old = ps.find("DataFromFile")
                if old is not None:
                    ps.remove(old)
                inp = ps.find("InputPattern")
                inp.text = "\n".join(format(v, ".17g") for v in sequence[0]["pattern"])
        tree.write(p, encoding="utf-8")
    files = []
    for path in sorted(ARCHIVE.rglob("*")):
        if path.is_file():
            files.append({"path": str(path.relative_to(ARCHIVE)), "bytes": path.stat().st_size, "sha256": sha(path)})
    frozen = []
    seen = set()
    for reference in evidence["cold"]:
        if (reference["kind"], reference["id"]) not in [("trainer", 64), ("learner", 129)]:
            continue
        signature = (reference["kind"], reference["id"], tuple(reference["dendrites"]), tuple(reference["synapses"]))
        if signature not in seen:
            seen.add(signature)
            frozen.append(reference)
    recognition_models = []
    for index, reference in enumerate(evidence["recognition"]):
        candidates = [r for r in evidence["cold"] if r["kind"] == reference["kind"] and r["id"] == reference["id"]]
        variant_number = re.search(r"\((\d+)\)", str(reference["variant"]))
        if variant_number:
            candidates = [r for r in candidates if r["dendrites"][2] == int(variant_number[1])]
        if not candidates:
            raise ValueError(f"No archived structure for recognition model {reference['variant']}")
        recognition_models.append({**candidates[0], "variant_index": index, "recognition_variant": reference["variant"]})
    manifest = {"schema_version": 1, "source_root": str(ARCHIVE), "repository": str(REPO),
                "root_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
                "pulselib_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO / "Libraries/Nmsdk-PulseLib", text=True).strip(),
                "defaults": {"required_build_type": "Release", "repeats": 3, "time_step_hz": 2000, "spikes_frequency_hz": 1.5,
                             "max_iterations": 1000, "wall_timeout_seconds": 600,
                             "max_abs_dissynchronization": 0.005, "max_abs_amp_difference": 0.000285},
                "templates": templates, "selected_ids": IDS, "dataset": dataset, "warm_sequence": sequence,
                "mode_cases": evidence["modes"], "mode_patterns": evidence["mode_patterns"],
                "recognition_frozen": frozen,
                "recognition_models": recognition_models,
                "sources": files, "verbatim_configs": copied,
                "known_source_gaps": ["2_seria_NT has no Model_00.xml or Parameters_00.xml; trainer template is a documented reconstruction.",
                                      "The structural 150-example worksheet is incomplete and contains textual synapse alternatives.",
                                      "Exploratory output_data20 / output_data15 include incomplete final recordings.",
                                      "DataFromFile is not registered on autoPreset; all training sequences are controlled externally."]}
    write_json(CONFIGS / "Prepared/manifest.json", manifest)
    write_json(REPORTS / "archive-evidence.json", evidence)
    write_json(REPORTS / "preparation/source-inventory.json", {"files": files, "verbatim_configs": copied, "templates": templates})
    print(json.dumps({"source_files": len(files), "verbatim_files": len(copied), "dataset_rows": len(dataset),
                      "directed_transitions": len(set(pairs)), "cold_references": len(evidence["cold"]),
                      "warm_references": len(evidence["warm"]), "recognition_models": len(evidence["recognition"])}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    prepare()
