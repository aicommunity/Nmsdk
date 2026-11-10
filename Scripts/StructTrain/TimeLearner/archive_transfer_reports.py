"""Audit complete native ModelArchive characterization; no learning verdict."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET

from .loaded_readout_reports import render, snapshot
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, number, parse_json_bytes, require
from .native_gate import audit_junit
from .plotting import plotting_runtime


def conditions():
    for prefix, precise, matrix in (("", False, False), ("precise-", True, False),
                                    ("matrix-precise-", True, True)):
        for boundary, frequency in itertools.product((False, True), (2000, 20000)):
            stem = prefix+("boundary" if boundary else "archive")
            yield f"{stem}-f{frequency}", stem, boundary, frequency, precise, matrix


def identity(value):
    require(value.get("kind") == "semantic_model_identity" and value.get("valid") is True and
            value.get("diagnostics") == [] and
            type(value.get("schema_version")) is int and value["schema_version"] in (1, 2),
            "archive_transfer_invalid_identity")
    model = value["model"]
    require(model["schema_version"] == value["schema_version"] and
            canonical_model_sha256(model) == value["sha256"], "archive_transfer_identity_digest")
    nodes = model["nodes"]
    require(isinstance(nodes, list) and nodes and len({n["path"] for n in nodes}) == len(nodes),
            "archive_transfer_invalid_nodes")
    def finite_bits(bits):
        require(type(bits) is str and re.fullmatch("[0-9a-f]{16}", bits), "archive_transfer_invalid_f64")
        value = struct.unpack(">d", bytes.fromhex(bits))[0]
        require(math.isfinite(value), "archive_transfer_nonfinite_parameter")
    for node in nodes:
        for prop in node["parameters"].values():
            data = prop["data"];kind = data["type"];values = data["value"]
            if kind == "binary64":finite_bits(values)
            elif kind == "binary64_vector":
                require(type(values) is list, "archive_transfer_invalid_vector")
                for v in values:finite_bits(v)
            elif kind == "binary64_matrix":
                rows, cols = data["rows"], data["columns"]
                require(type(rows) is str and type(cols) is str and rows.isdecimal() and cols.isdecimal(),
                        "archive_transfer_invalid_matrix")
                require(type(values) is list and len(values) == int(rows), "archive_transfer_invalid_matrix")
                for row in values:
                    require(type(row) is list and len(row) == int(cols), "archive_transfer_invalid_matrix")
                    for v in row:finite_bits(v)
    return model


def graph(value):
    require(type(value.get("native_xml")) is str and
            hashlib.sha256(value["native_xml"].encode()).hexdigest() == value["native_xml_sha256"],
            "archive_transfer_xml_digest")
    return identity(value["identity"])


def _read_case(folder, stem, boundary, frequency, precise, matrix):
    records = []
    def read(name):
        raw, record = snapshot(folder, name);records.append(record);return parse_json_bytes(raw)
    source = read(f"{stem}-fixture-{frequency}.json")
    child = read(f"{stem}-import-verification-{frequency}.json")
    require(set(source) == {"archive", "frequency_hz", "waveform", "actual_input", "soma", "time_s",
                            "kind", "schema_version", "complete", "window_begin_s", "window_end_s"} |
            ({"stimulus_port"} if boundary else set()) and
            set(child) == {"max_pairwise_error", "samples", "identity", "waveform", "actual_input", "soma",
                           "time_s", "max_soma_pairwise_error", "kind", "schema_version", "complete"},
            "archive_transfer_fixture_fields")
    require(source.get("kind") == "native_model_archive_transfer_fixture" and
            child.get("kind") == "native_model_archive_transfer_observation" and
            type(source.get("schema_version")) is int and source["schema_version"] == 1 and
            type(child.get("schema_version")) is int and child["schema_version"] == 1,
            "archive_transfer_unknown_fixture_schema")
    require(source.get("complete") is True and child.get("complete") is True and
            number(source.get("window_begin_s")) == 0 and number(source.get("window_end_s")) == .1,
            "archive_transfer_incomplete_window")
    require(type(source.get("frequency_hz")) is int and source["frequency_hz"] == frequency and
            ((source.get("stimulus_port") == "training_burst") if boundary else "stimulus_port" not in source),
            "archive_transfer_wrong_condition")
    archive = source["archive"];version = 2 if boundary else 1
    require(archive.get("kind") == "timelearner_model_archive" and
            type(archive.get("schema_version")) is int and archive["schema_version"] == version and
            archive.get("encoding") == f"native-xml-and-model-identity-v{version}" and
            archive.get("dynamic_checkpoint") is False, "archive_transfer_unknown_archive_schema")
    require(canonical_model_sha256({k: v for k, v in archive.items() if k != "sha256"}) == archive["sha256"],
            "archive_transfer_archive_digest")
    model = graph(archive["graph"])
    require(archive["graph"]["identity"]["schema_version"] == version,
            "archive_transfer_wrong_identity_schema")
    definitions = archive["class_definitions"]
    require(type(definitions) is list and definitions and
            len({d["name"] for d in definitions}) == len(definitions), "archive_transfer_invalid_images")
    for definition in definitions:graph(definition["snapshot"])
    identity(child["identity"])
    require(child["identity"] == archive["graph"]["identity"], "archive_transfer_import_identity_changed")
    nodes = {n["path"]: n for n in model["nodes"]}
    require("$.Soma2" in nodes and nodes["$"]["parameters"]["NumSomaMembraneParts"]["data"]["value"] == "2",
            "archive_transfer_wrong_output_soma")
    def bits(path, parameter, expected):
        data = nodes[path]["parameters"][parameter]["data"]
        require(data["type"] == "binary64" and data["value"] == struct.pack(">d", expected).hex(),
                "archive_transfer_effective_physics_changed")
    bits("$.Dendrite1_1.ExcChannel", "Capacity", 1.2345678901234567e-9 if precise else 1e-9)
    bits("$.Dendrite2_3.ExcChannel", "Capacity", 1.4142135623730951e-9 if precise else 1.41e-9)
    bits("$.Dendrite2_3.ExcSynapse2", "Resistance", 333333333.12345678 if precise else 333e6)
    if matrix:
        expected = [[.0012345678901234567, .0056789012345678901, .0098765432109876543],
                    [.0023456789012345678, .0067890123456789012, .012345678901234567]]
        data = nodes["$"]["parameters"]["TrainingPattern"]["data"]
        require(data == {"type": "binary64_matrix", "rows": "2", "columns": "3",
                         "value": [[struct.pack(">d", v).hex() for v in row] for row in expected]},
                "archive_transfer_reference_matrix_changed")
    else:
        require(nodes["$"]["parameters"]["TrainingPattern"]["data"] == {
            "type": "binary64_matrix", "rows": "0", "columns": "0", "value": []},
            "archive_transfer_unexpected_reference_matrix")
    keys = ("time_s", "actual_input", "soma", "waveform")
    for obj in (source, child):
        require(all(type(obj.get(key)) is list and len(obj[key]) == frequency//10 for key in keys),
                "archive_transfer_incomplete_grid")
        for key in keys:
            for value in obj[key]:number(value)
    require(child.get("samples") == frequency//10, "archive_transfer_sample_count")
    rows = []
    for i in range(frequency//10):
        t = source["time_s"][i]
        require(abs(t-i/frequency) < 1e-12 and child["time_s"][i] == t, "archive_transfer_native_clock")
        pulse = 1. if .005 <= i/frequency < .006 else 0.
        require(source["actual_input"][i] == child["actual_input"][i] == pulse,
                "archive_transfer_actual_input")
        rows.append([t, pulse, pulse, source["soma"][i], child["soma"][i]])
    errors = {key: max(abs(a-b) for a, b in zip(source[key], child[key])) for key in ("soma", "waveform")}
    require(all(v <= 1e-12 for v in errors.values()), "archive_transfer_response_changed")
    require(number(child["max_pairwise_error"]) == errors["waveform"] and
            number(child["max_soma_pairwise_error"]) == errors["soma"], "archive_transfer_error_summary")
    span = max(source["soma"])-min(source["soma"])
    require(span > 1e-8, "archive_transfer_flat_soma")
    return {"rows": rows, "summary": {"topology": "Asymmetric archive neuron", "inputs": 1,
            "frequency_hz": frequency, "somas": 1, "samples": len(rows), "saved_state": True,
            "external_stimulus": boundary, "precise_scalar_physics": precise, "precise_matrix": matrix,
            "observed_soma_paths": ["$.Soma2"], "physical_soma_ids": [2],
            "sample_grid_complete": True, "stimulus_times": [.005], "soma_spans": [span],
            "maximum_waveform_difference": [errors["soma"]], "exc_channel_difference": errors["waveform"],
            "model_sha256": archive["graph"]["identity"]["sha256"], "storage_images": len(definitions),
            "primary": records, "lt_spike_timestamps": None, "scientific_verdict": None,
            "training_certificate": None}}


def checked(call, *args):
    try:return call(*args)
    except EvidenceError:raise
    except OSError as error:raise EvidenceError("archive_transfer_missing_or_unreadable_artifact") from error
    except (KeyError, TypeError, ValueError, OverflowError, ET.ParseError) as error:
        raise EvidenceError("archive_transfer_malformed_data") from error


def read_case(folder, stem, boundary, frequency, precise, matrix):
    return checked(_read_case, folder, stem, boundary, frequency, precise, matrix)


def _audit_run(root):
    def passed(name, count):
        value = parse_json_bytes(snapshot(root, name)[0]);g = value["gtest"]
        require(value["execution"]["execution"] == "completed" and value["execution"]["returncode"] == 0 and
                g["tests"] == str(count) and g["failures"] == g["errors"] == g["disabled"] == "0",
                "archive_transfer_native_tests_failed")
        return value
    native = passed("validation.json", 16);unit = passed("unit-validation.json", 10)
    require(unit["skipped"] == 0, "archive_transfer_skipped_tests")
    tree = ET.fromstring(snapshot(root, "gtest.xml")[0]);cases = tree.findall(".//testcase")
    require(len(cases) == 16 and not tree.findall(".//skipped") and not tree.findall(".//failure"),
            "archive_transfer_gtest_detail")
    transfers = {"TransfersImagesAndAsymmetricModelIntoFreshNativeProcess",
                 "TransfersDeclaredExternalStimulusIntoFreshNativeProcess",
                 "TransfersHighPrecisionStorageAndLearnedStateIntoFreshNativeProcess",
                 "TransfersHighPrecisionStateAndExternalStimulusIntoFreshNativeProcess",
                 "TransfersHighPrecisionMatrixIntoFreshNativeProcess",
                 "TransfersHighPrecisionMatrixAndExternalStimulusIntoFreshNativeProcess"}
    guards = {"BoundaryMustBeDeclaredUsedAndReboundByStableId", "RejectsMalformedArchiveBeforeRegistration",
              "RejectsLostGraphInformationEvenWithUpdatedFileHashes",
              "CalibrationMustMatchActualZoneWithoutInventingAThresholdSignRule"}
    expected = {("SingleRate/NativeArchive", f"{name}/{i}", str(f)) for name in transfers
                for i, f in enumerate((2000, 20000))} | {("TimeLearnerModelArchive", name, "") for name in guards}
    actual = [(c.get("classname"), c.get("name"), c.get("value_param", "")) for c in cases]
    require(len(set(actual)) == 16 and set(actual) == expected, "archive_transfer_test_condition_set")
    files = {f"{stem}-{phase}-{freq}.json" for _, stem, _, freq, *_ in conditions()
             for phase in ("fixture", "import-verification")}
    require({p.name for p in (root/"artifacts").iterdir()} == files, "archive_transfer_artifact_set")
    data = {name: read_case(root/"artifacts", *spec) for name, *spec in conditions()}
    return data, {"kind": "native_archive_transfer_report", "schema_version": 1,
                  "native_validation": native, "unit_validation": unit,
                  "cases": {k: v["summary"] for k, v in data.items()}, "case_soma_pairs": len(data),
                  "scientific_verdict": None, "training_certificate": None}


def audit_run(root):return checked(_audit_run, root)


def _audit_gate_pair(root):
    """Two explicit telemetry controls; never evidence for the legacy16 corpus."""
    records = []
    def read(name):
        raw, record = snapshot(root, name);records.append(record);return parse_json_bytes(raw)
    result = read("result.json")
    process = read("process/result.json")
    expected = ["NativeArchiveTelemetry/At2000", "NativeArchiveTelemetry/At20000"]
    require(result.get("kind") == "timelearner_native_test_gate_result" and
            type(result.get("schema_version")) is int and result["schema_version"] == 1 and
            result.get("execution") == "completed" and result.get("validity") == "valid" and
            result.get("assertion_status") == "passed" and
            result.get("reason") == "complete_declared_test_inventory" and
            result.get("scientific_verdict", "missing") is None,
            "archive_transfer_native_gate_not_passed")
    require(process.get("kind") == "timelearner_process_result" and
            type(process.get("schema_version")) is int and process["schema_version"] == 2 and
            process.get("execution") == "completed" and type(process.get("returncode")) is int and
            process["returncode"] == 0 and process.get("ownership_scope") == "bound_cgroup" and
            process.get("all_processes_closed") is True and
            process.get("runtime_provenance") == "loaded_files_captured" and
            process.get("mapping_error", "missing") is None and
            process.get("scientific_verdict", "missing") is None,
            "archive_transfer_native_process_not_closed_or_unproven")
    # Recompute from the actual XML. A copied green result.json is insufficient.
    _, junit_record = snapshot(root, "native.xml");records.append(junit_record)
    inventory = audit_junit(root/"native.xml", expected)
    require(inventory["assertion_status"] == "passed" and result.get("inventory") == inventory,
            "archive_transfer_native_gate_inventory_changed")
    data = {f"telemetry-matrix-precise-boundary-f{frequency}":
            read_case(root/"native", "telemetry-matrix-precise-boundary", True, frequency, True, True)
            for frequency in (2000, 20000)}
    return data, {"kind": "native_archive_transfer_report", "schema_version": 2,
                  "input_format": "native-gate-pair", "native_validation": result,
                  "execution_validation": process,
                  "gate_primary": records, "expected_test_ids": expected,
                  "cases": {k: v["summary"] for k, v in data.items()},
                  "case_soma_pairs": len(data), "legacy16_admitted": False,
                  "whole_parent_cohort_admitted": False,
                  "scientific_verdict": None, "training_certificate": None}


def audit_gate_pair(root):return checked(_audit_gate_pair, root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True);parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--input-format", choices=("legacy16", "native-gate-pair"), default="legacy16")
    parser.add_argument("--plots", action="store_true");args = parser.parse_args()
    data, report = (audit_run if args.input_format == "legacy16" else audit_gate_pair)(args.input)
    runtime = plotting_runtime() if args.plots else None
    args.output.mkdir(parents=True, exist_ok=False)
    if args.plots:
        for name, value in data.items():
            report["cases"][name]["figures"] = render(value, args.output/name,
                source_label="Source physical soma", loaded_label="Fresh-process imported soma",
                context="Versioned model transfer characterization; not selectivity",
                state_description="Native import and Reset; one pulse", physical_soma_ids=[2])
    report["plotting_runtime"] = runtime
    (args.output/"validation.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":main()
