"""Declared native-test receipts; payload/scientific auditing stays separate.

Use exact test IDs and a full filename match. Auxiliary Train JSON files are
not counted as top-level controls. Loader receipts describe a point in time,
not process-lifetime library closure or arbitrary-file origin.
"""
import argparse
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET

from .native_evidence import EvidenceError, count, load, load_json, require
from .runtime import digest_json, runtime_content_identity


def _read_native_gate(specification, root, after):
    root = Path(root)
    pattern = re.compile(specification["control_filename_pattern"])
    controls = {p.name: {k: value.get(k) for k in ("kind", "schema_version")}
                for p in (root/"native").iterdir() if p.is_file() and pattern.fullmatch(p.name)
                for value in (load(p),)}
    return {"junit": ET.parse(root/"native.xml").getroot(), "controls": controls,
            "runtime_before": load(root/"runtime-before.json"), "runtime_after": load(after),
            "process_runtime": load(root/"process/runtime.json"), "process": load(root/"process/result.json"),
            "request": load(root/"process/request.json"), "owned": load(root/"process/owned-process.json"),
            "loaded": load_json(root/"process/loaded-files.json"),
            "supervisor_status": int((root/"process-exit-status.txt").read_text().strip())}


def _audit_native_gate(specification, receipts):
    require(type(specification) is dict and set(specification) ==
            {"kind", "schema_version", "expected_test_ids", "control_filename_pattern", "expected_controls",
             "supervisor_policy"} and specification["kind"] == "timelearner_native_execution_gate_spec" and
            type(specification["schema_version"]) is int and specification["schema_version"] == 1,
            "unknown_native_execution_gate_spec")
    expected = specification["expected_test_ids"]
    require(type(expected) is list and bool(expected) and all(type(s) is str and s for s in expected) and
            len(expected) == len(set(expected)), "invalid_native_gate_expected_tests")
    xml = receipts["junit"]
    cases = list(xml.iter("testcase"))
    names = [case.get("classname", "")+"/"+case.get("name", "") for case in cases]
    require(len(names) == len(set(names)) and set(names) == set(expected) and
            int(xml.attrib["tests"]) == len(expected) and
            all(int(xml.attrib.get(k, 0)) == 0 for k in ("failures", "errors", "disabled")) and
            all(case.get("status", "run") == "run" and case.get("result", "completed") == "completed" and
                all(case.find(tag) is None for tag in ("failure", "error", "skipped")) for case in cases),
            "native_gate_expected_tests_not_completed")
    pattern = re.compile(specification["control_filename_pattern"])
    controls = specification["expected_controls"]
    require(type(controls) is dict and bool(controls) and all(type(name) is str and pattern.fullmatch(name) and
            "/" not in name and "\\" not in name and type(kind) is str and kind for name, kind in controls.items()),
            "invalid_native_gate_control_contract")
    require(set(receipts["controls"]) == set(controls) and all(
            type(receipts["controls"][name]["schema_version"]) is int and
            receipts["controls"][name] == {"kind": kind, "schema_version": 1} for name, kind in controls.items()),
            "native_gate_control_coverage_mismatch")
    runtime = receipts["runtime_before"]
    require(type(runtime["schema_version"]) is int and runtime["schema_version"] == 2 and
            runtime == receipts["runtime_after"] == receipts["process_runtime"] and
            runtime["runtime_fingerprint"] == digest_json(runtime_content_identity(runtime)),
            "native_gate_runtime_snapshot_changed")
    process, owned, loaded = receipts["process"], receipts["owned"], receipts["loaded"]
    require(process["kind"] == "timelearner_process_result" and type(process["schema_version"]) is int and
            process["schema_version"] == 1 and process["execution"] == "completed" and
            type(process["returncode"]) is int and process["returncode"] == 0 and
            process["runtime_provenance"] == "loaded_files_captured" and
            process["ownership_scope"] == "launched_executable_only" and
            process["runtime_fingerprint"] == owned["runtime_fingerprint"] == runtime["runtime_fingerprint"] and
            process["scientific_verdict"] is None, "native_gate_process_not_completed")
    require(type(loaded) is list and all(type(row) is dict and set(row) == {"path", "size", "sha256"} and
            type(row["path"]) is str and PurePosixPath(row["path"]).is_absolute() and
            type(row["size"]) is int and row["size"] >= 0 and type(row["sha256"]) is str and
            re.fullmatch("[0-9a-f]{64}", row["sha256"]) for row in loaded) and
            len({row["path"] for row in loaded}) == len(loaded), "native_gate_loaded_files_changed")
    executable = {k: runtime["executable"][k] for k in ("path", "size", "sha256")}
    require(executable in loaded and owned["executable"] == executable["path"] and
            owned["executable_sha256"] == executable["sha256"] and count(owned["pid"]) > 0 and
            count(owned["start_ticks"]) >= 0 and type(owned["boot_id"]) is str and bool(owned["boot_id"]),
            "native_gate_owned_process_changed")
    arguments = receipts["request"]["arguments"]
    require(type(arguments) is list and len(arguments) == 2 and
            arguments[0].startswith("--gtest_filter=") and arguments[1].startswith("--gtest_output=xml:") and
            PurePosixPath(arguments[1].removeprefix("--gtest_output=xml:")).name == "native.xml" and
            receipts["request"]["working_directory"] == str(PurePosixPath(executable["path"]).parent),
            "native_gate_process_request_changed")
    policy = specification["supervisor_policy"]
    require(policy in {"require_zero", "retain_failure"} and type(receipts["supervisor_status"]) is int and
            0 <= receipts["supervisor_status"] <= 255 and
            (policy != "require_zero" or receipts["supervisor_status"] == 0), "native_gate_supervisor_failed")
    return {"kind": "native_execution_gate_receipt_audit", "schema_version": 1,
            "tests": len(expected), "controls": len(controls), "native_receipts_consistent": True,
            "supervisor_passed": receipts["supervisor_status"] == 0,
            "supervisor_failure_retained": receipts["supervisor_status"] != 0,
            "runtime_before_after_equal": True, "payloads_audited": False,
            "process_lifetime_and_file_origin_attested": False, "scientific_verdict": None}


def _checked(function, *args):
    try:
        return function(*args)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, AttributeError, ET.ParseError, re.error) as error:
        raise EvidenceError("malformed_native_execution_gate:" + str(error)) from error


def read_native_gate(specification, root, after):
    return _checked(_read_native_gate, specification, root, after)


def audit_native_gate(specification, receipts):
    return _checked(_audit_native_gate, specification, receipts)


def main():
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--runtime-after", type=Path, required=True)
    args = parser.parse_args()
    spec = load(args.spec)
    print(json.dumps(audit_native_gate(spec, read_native_gate(spec, args.root, args.runtime_after)), sort_keys=True))


if __name__ == "__main__":
    main()
