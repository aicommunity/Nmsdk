"""Author versioned native-contract recipes and pinned historical pattern inputs only.

No model process, compiler, test runner or remote host is invoked.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

BASE_BIN = "402867ffcf2b9d6fc145bbe5e16f016e15269054"
CONFIG_REL = Path("Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner")

HISTORY = {
    25: "TimeLearnerMatrix/W01/inputs/W01_CL25_N0_PSIoff",
    50: "TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff",
    100: "TimeLearnerMatrix/W02/inputs/W02_CL100_N0_PSIoff",
    200: "SelectivityPresynapticInhib/EXP30_span200ms_baseline",
    480: "TimeLearnerMatrix/W02/inputs/W02_CL480_N0_PSIoff",
}


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def record(relative: str, payload: bytes) -> dict:
    return {"path": relative, "bytes": len(payload), "sha256": sha(payload)}


def write(path: Path, payload: bytes, overwrite: bool) -> None:
    if len(payload) > 1024 * 1024:
        raise ValueError(f"source_input_exceeds_1MiB:{path}")
    if path.exists() and path.read_bytes() != payload and not overwrite:
        raise FileExistsError(f"refusing_to_replace_different_source:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def blob(root: Path, relative: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root / "Bin"), "show", f"{BASE_BIN}:{relative}"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def topology(carrier: str) -> dict:
    def section(name: str, parent: str, tap: int, length: int) -> dict:
        result = {"id": name, "parent": parent, "attach_segment": tap,
                  "carrier": carrier, "segments": length}
        if carrier == "NAxoneChainAndDelay":
            result["internode_delay_s"] = .002
        return result
    return {
        "schema_version": 1,
        "sections": [section("Left", "Root", 1, 3), section("Right", "Root", 2, 2),
                     section("Root", "", 0, 2)],
        "ports": {"main": "Left", "left": "Left", "right": "Right", "trunk": "Root"},
        "output_port": "main",
    }


def native_contracts(root: Path) -> dict:
    source_path = "Tests/Integration/Libraries/Test_PulseLib_AxoneLifecycle.cpp"
    source_bytes = (root / source_path).read_bytes()
    source = {"image": "NPGenerator", "cpp_class": "NPulseGenerator", "frequency_hz": 10,
              "pulse_width_s": .001, "amplitude": 1, "delay_s": .01,
              "frequency_deviation": 0, "stop_at_s": .5, "observe_until_s": .55}
    cases = []
    for frequency in (2000, 20000, 40000):
        for milliseconds in (1, 2, 5, 10, 20):
            case_id = f"delay_t{milliseconds}ms_f{frequency}"
            cases.append({"id": case_id, "model_frequency_hz": frequency,
                          "carrier": "NAxoneDelay", "delay_s": milliseconds / 1000,
                          "gtest_filter": f"P1Baseline/AxonePropagation.PreservesAllSparseSpikesThroughNativeScheduler/{case_id}"})
        for carrier, prefix, counts in (
            ("NAxoneChain", "chain", (1, 2, 3, 5, 7)),
            ("NAxoneChainAndDelay", "cad", (1, 2, 3, 4, 5)),
        ):
            for count in counts:
                case_id = f"{prefix}_n{count}_f{frequency}"
                case = {"id": case_id, "model_frequency_hz": frequency, "carrier": carrier,
                        "segment_count": count,
                        "gtest_filter": f"P1Baseline/AxonePropagation.PreservesAllSparseSpikesThroughNativeScheduler/{case_id}"}
                if carrier == "NAxoneChainAndDelay":
                    case["internode_delay_s"] = .002
                cases.append(case)
        for carrier in ("NAxoneChain", "NAxoneChainAndDelay"):
            case_id = f"{carrier}_f{frequency}"
            cases.append({"id": "tree_equivalence_" + case_id,
                          "model_frequency_hz": frequency, "carrier": carrier,
                          "topology": topology(carrier),
                          "gtest_filter": f"P1Tree/AxoneTreeEquivalence.MatchesExplicitTreeAtEveryNativeTick/{case_id}"})
    expected = re.findall(r'TEST_F\(AxoneLifecycle,\s*(\w+)\)', source_bytes.decode("utf-8"))
    if len(expected) < 13 or len(cases) != 51:
        raise ValueError("native_contract_case_inventory_changed")
    return {
        "kind": "axone_native_contract_inputs", "schema_version": 1,
        "protocol_id": "P1-native-contracts-v1", "status": "source_prepared",
        "scientific_result": None, "native_execution_performed": False,
        "test_target": "Test_PulseLib_StorageComponents",
        "test_source": record(source_path, source_bytes), "source": source,
        "lifecycle_filters": ["AxoneLifecycle.*", "AxoneTreeTopology.*"],
        "lifecycle_cases": expected, "cases": cases,
        "artifact_env": "TIMELEARNER_EXECUTION_OUTPUT",
        "artifact_subdirectory": "AxoneP1",
        "repeat": {"identical_initial_state_runs": 3, "separate_fresh_output_per_run": True},
        "artifact_admission": {
            "full_root_and_submodule_versions_required": True,
            "frozen_native_runtime_and_actual_loaded_libraries_required": True,
            "output_must_be_external_to_source_trees": True,
            "engineering_assertions_are_not_full_P1_scientific_admission": True,
        },
        "distinction": "Source Delay=10ms; historical serialized component-baseline uses Delay=0. Different fixtures, not duplicate execution of the same condition.",
    }


def matrix(payload: bytes, *, require_consistent: bool = True) -> tuple[list[list[Decimal]], dict]:
    tree = ET.fromstring(payload)
    datasets = [node for node in tree.iter() if node.get("Class") == "NDatasetMatrix"]
    if len(datasets) != 1:
        raise ValueError("expected_one_historical_dataset")
    params = datasets[0].find("Parameters")
    if params is None:
        raise ValueError("missing_dataset_parameters")
    def integer(name: str) -> int:
        return int(params.findtext(name, ""))
    samples, features, slots = integer("NumSamples"), integer("NumFeatures"), integer("MaxSpikesPerFeature")
    data = params.find("MatrixData")
    if data is None or features != 1 or slots != 4:
        raise ValueError("expected_single_feature_M4_history")
    rows = int(data.get("Rows", "-1"))
    values = [Decimal(value) for value in (data.text or "").split()]
    if int(data.get("Cols", "-1")) != 1 or rows != len(values) or rows % slots != 0:
        raise ValueError("historical_matrix_dimensions")
    consistent = rows == samples * slots
    if require_consistent and not consistent:
        raise ValueError("historical_overlay_sample_dimensions")
    if any(not value.is_finite() or value < 0 for value in values):
        raise ValueError("historical_matrix_values")
    return [values[index * slots:(index + 1) * slots] for index in range(rows // slots)], {
        "NumFeatures": features, "NumSamples": samples, "MaxSpikesPerFeature": slots,
        "stored_sample_blocks": rows // slots, "declared_dimensions_consistent": consistent,
        "Delay": params.findtext("Delay"), "LoopSamples": params.findtext("LoopSamples"),
        "AdvanceSampleAfterBurst": params.findtext("AdvanceSampleAfterBurst"),
    }


def pattern(isi: list[Decimal]) -> dict:
    cumulative, total = [], Decimal(0)
    for value in isi:
        total += value
        cumulative.append(total)
    relative = [value - cumulative[0] for value in cumulative]
    return {
        "historical_isi_decimal_s": [str(value) for value in isi],
        "historical_scheduled_from_burst_s": [float(value) for value in cumulative],
        "relative_to_first_decimal_s": [str(value) for value in relative],
        "relative_to_first_s": [float(value) for value in relative],
        "actual_nominal_span_s": float(relative[-1]),
    }


def historical_p2(root: Path) -> list[tuple[str, dict]]:
    results = []
    for nominal_span, folder in HISTORY.items():
        sources, sides, parameters = {}, {}, {}
        for side in ("Train", "Test"):
            sources[side], parameters[side] = [], {}
            for filename in ("Model_00.xml", "Parameters_00.xml"):
                relative = f"Configs/SpikeSamples/StructTrain/{folder}/{side}/{filename}"
                payload = blob(root, relative)
                try:
                    values, settings = matrix(payload, require_consistent=(filename == "Parameters_00.xml"))
                except ValueError as error:
                    raise ValueError(f"{relative}:{error}") from error
                sources[side].append(record(relative, payload))
                parameters[side][filename] = settings
                if filename == "Parameters_00.xml":
                    # The properties overlay, not the embedded factory dataset,
                    # declares the actual historical Test matrix.
                    sides[side] = values
        if len(sides["Train"]) != 1 or len(sides["Test"]) != 8:
            raise ValueError(f"unexpected_history_sample_count:{nominal_span}")
        target = sides["Train"][0]
        target_matches = [index for index, values in enumerate(sides["Test"]) if values == target]
        if len(target_matches) != 1:
            raise ValueError(f"historical_target_not_exact_unique:{nominal_span}")
        summary = pattern(target)
        # A label is not substituted for the precise rounded historical values.
        if abs(summary["actual_nominal_span_s"] - nominal_span / 1000) > 1e-6:
            raise ValueError(f"historical_span_mismatch:{nominal_span}")
        cases = [dict(id=f"matrix_{index}", role="target" if index == target_matches[0] else "legacy_foil",
                      **pattern(values)) for index, values in enumerate(sides["Test"])]
        times = [Decimal(str(value)) for value in summary["relative_to_first_decimal_s"]]
        for count in (1, 2, 3):
            cases.append({"id": f"prefix_{count}", "role": "prefix", "relative_to_first_s": [float(t) for t in times[:count]]})
        for omitted in range(4):
            cases.append({"id": f"omission_{omitted}", "role": "omission", "omitted_ordinal": omitted,
                          "relative_to_original_first_s": [float(t) for index, t in enumerate(times) if index != omitted]})
        results.append((f"P2/historical-patterns/span{nominal_span}ms.json", {
            "kind": "axone_P2_historical_pattern_inputs", "schema_version": 1,
            "protocol_id": "P2-manual-delay-v1", "status": "source_prepared_requires_native_materializer",
            "scientific_result": None, "training": False, "nominal_span_ms": nominal_span,
            "source_bin_commit": BASE_BIN, "historical_sources": sources,
            "historical_dataset_parameters": parameters, "target_matrix_index": target_matches[0],
            "load_order": ["Model_00.xml", "Parameters_00.xml"],
            "pattern_source": "Parameters_00.xml explicit dataset property overlay; native load still requires validation",
            "target": summary, "trials": cases,
            "proposed_source": {"image": "NDatasetMatrix", "generator_image": "NPulseGeneratorTransit",
                                "feature_count": 1, "pulse_width_s": .001, "amplitude": 1,
                                "first_event_offset_s": .01},
            "time_semantics": "Every branch receives every pulse. Prefixes and omissions preserve original absolute relative times; do not compact ISIs or shift remaining pulses.",
            "manual_delay_proposal": {
                "rule": "D_b = D_min + target_last - target_b; proposal only",
                "D_min_s": .001,
                "path_delay_s": [.001 + float(times[-1] - value) for value in times],
                "carrier": "NAxoneDelay", "then_segmented_carrier_requires_P1": True,
            },
            "pending_before_execution": [
                "native model materializer and effective graph inspection",
                "declare matched receiver profile and amplitude normalization",
                "declare complete observation window and threshold calibration protocol",
                "resolve actual grid-rounded source events and verify all output events",
            ],
        }))
    return results


def materialize(root: Path, output: Path, overwrite: bool) -> dict:
    root, output = root.resolve(), output.resolve()
    config_root = (root / CONFIG_REL).resolve()
    if output != config_root:
        raise ValueError("output_must_equal_axone_source_config_root")
    outputs = [("protocols/P1-native-contracts.json", native_contracts(root)), *historical_p2(root)]
    records = []
    for relative, document in outputs:
        payload = encode(document)
        write(output / relative, payload, overwrite)
        records.append(record(relative, payload))
    manifest = {"kind": "axone_stage_source_manifest", "schema_version": 1,
                "generator": "Scripts/StructTrain/AxoneTimeLearner/generate_stage_configs.py",
                "status": "source_prepared", "model_execution_performed": False,
                "files": records}
    write(output / "stage-source-manifest.json", encode(manifest), overwrite)
    return {"files": len(records) + 1, "native_cases": 51, "historical_spans": len(HISTORY),
            "model_execution_performed": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(materialize(args.repo_root, args.repo_root / CONFIG_REL, args.overwrite), ensure_ascii=False))


if __name__ == "__main__":
    main()
