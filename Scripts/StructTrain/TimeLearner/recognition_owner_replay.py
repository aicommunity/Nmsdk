"""Fresh-process recognition transport over actual, pinned native owner cases.

This is an integration replay, not Train, calibration or classification. Input
primary data stays immutable. The original corpus is needed for portable audit.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from .fresh_recognition_owner_evidence import audit_fresh_owner_process
from .native_calibration_worker import _write
from .native_evidence import EvidenceError, load, number, require
from .native_gate import _environment, audit_junit, run_native_gate
from .process_runner import verify_runtime
from .recognition_owner_evidence import audit_owner_recognition, load_case


FIELDS = {"kind", "schema_version", "source_directory", "source_bundle", "source_archive",
          "source_prefix", "origin_evidence_commit", "native_source_root", "runtime_manifest",
          "maximum_wall_seconds", "asan_options", "cases"}
TEST_ID = "NativeRecognitionOwner/FreshProcessImport"


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def _relative(value):
    require(type(value) is str and value and "\\" not in value and
            not PurePosixPath(value).is_absolute() and
            all(p not in ("", ".", "..") for p in value.split("/")), "invalid_owner_replay_relative_path")
    return value


def run_replay(specification, output):
    specification = Path(specification).resolve(strict=True)
    spec = load(specification)
    require(type(spec) is dict and set(spec) == FIELDS and
            spec["kind"] == "timelearner_recognition_owner_replay" and
            type(spec["schema_version"]) is int and spec["schema_version"] == 1,
            "unknown_recognition_owner_replay")
    require(type(spec["origin_evidence_commit"]) is str and
            re.fullmatch("[0-9a-f]{40}", spec["origin_evidence_commit"]), "owner_replay_origin_sha_required")
    wall = number(spec["maximum_wall_seconds"])
    require(0 < wall <= 86400 and type(spec["asan_options"]) is str and
            "\x00" not in spec["asan_options"], "invalid_owner_replay_execution_policy")

    def resolve(key):
        value = spec[key]
        require(type(value) is str and value, "invalid_owner_replay_path:"+key)
        p = Path(value)
        return (p if p.is_absolute() else specification.parent/p).resolve(strict=True)

    source, bundle_path, archive_path, native_source, runtime_path = (resolve(k) for k in
        ("source_directory", "source_bundle", "source_archive", "native_source_root", "runtime_manifest"))
    runtime = load(runtime_path)
    executable = verify_runtime(runtime)
    output = Path(output).resolve()
    require(not output.exists() and all(not output.is_relative_to(p) and not p.is_relative_to(output)
            for p in (source, native_source, executable.parent)), "owner_replay_output_overlaps_inputs")
    bundle = load(bundle_path)
    require(archive_path.stat().st_size == bundle["archive_bytes"] and
            file_hash(archive_path) == bundle["archive_sha256"], "owner_replay_source_archive_changed")
    prefix = _relative(spec["source_prefix"]).rstrip("/")+"/"
    cases = spec["cases"]
    require(type(cases) is list and bool(cases), "owner_replay_cases_missing")
    prepared, ids, filenames = [], set(), set()
    for row in cases:
        require(type(row) is dict and set(row) == {"id", "package", "file_sha256"} and
                type(row["id"]) is str and re.fullmatch("[A-Za-z][A-Za-z0-9_]*", row["id"]) and
                row["id"] not in ids, "invalid_owner_replay_case")
        name = _relative(row["package"])
        require("/" not in name and name.endswith("_owner_recognition_state.json") and name not in filenames,
                "owner_replay_package_filename_invalid")
        ids.add(row["id"]); filenames.add(name)
        path = source/name
        require(path.is_file() and not path.is_symlink() and file_hash(path) == row["file_sha256"],
                "owner_replay_source_package_changed")
        stem = name.removesuffix("_owner_recognition_state.json")
        dependencies = {}
        for p in sorted(source.glob(stem+"_*")):
            require(p.is_file() and not p.is_symlink(), "owner_replay_source_not_regular")
            record = {"bytes": p.stat().st_size, "sha256": file_hash(p)}
            require(bundle["members"].get(prefix+p.name) == record, "owner_replay_primary_member_changed:"+p.name)
            dependencies[p.name] = record
        case = load_case(path)
        audit_owner_recognition(*case)
        prepared.append((row, path, case, dependencies))

    # Every case, complete primary audit and immutable input binding is checked
    # before creating output or starting any native importer.
    output.mkdir(parents=True, exist_ok=False)
    _write(output/"specification.json", spec)
    _write(output/"runtime.json", runtime)
    rows = []
    for declared, path, case, dependencies in prepared:
        folder = output/declared["id"]
        folder.mkdir()
        model_input, probe_input, actual = folder/"input-model.json", folder/"input-probe.json", folder/"actual.json"
        model_input.write_bytes(path.read_bytes())
        probe_path = path.with_name(path.name.removesuffix("_state.json")+"_probe_spec.json")
        probe_input.write_bytes(probe_path.read_bytes())
        require(file_hash(model_input) == declared["file_sha256"] and
                file_hash(probe_input) == dependencies[probe_path.name]["sha256"],
                "owner_replay_input_changed_before_launch")
        _write(folder/"source-dependencies.json", dependencies)
        gate_spec = {"kind": "timelearner_native_test_gate", "schema_version": 2,
            "cooperative_runtime_capture": True, "runtime_manifest": str(runtime_path),
            "source_root": str(native_source), "expected_test_ids": [TEST_ID],
            "maximum_wall_seconds": wall, "asan_options": spec["asan_options"]}
        _write(folder/"gate-specification.json", gate_spec)
        environment = {"TIMELEARNER_RECOGNITION_OWNER_IMPORT": str(model_input),
            "TIMELEARNER_RECOGNITION_OWNER_SPEC": str(probe_input),
            "TIMELEARNER_RECOGNITION_OWNER_OUTPUT": str(actual)}
        _write(folder/"fixture-environment.json", environment)
        row = {"id": declared["id"], "source_filename": path.name,
            "source_file_sha256": declared["file_sha256"], "source_package_sha256": case[0]["sha256"],
            "source_solo_sha256": case[0]["source_solo"]["sha256"], "passed": False, "reason": "not_assessed"}
        try:
            with _environment(environment):
                gate = run_native_gate(folder/"gate-specification.json", folder/"gate")
            require(gate["execution"] == "completed" and gate["validity"] == "valid" and
                    gate["assertion_status"] == "passed", "owner_replay_native_gate_not_passed")
            audit = audit_fresh_owner_process(case, load(actual), Path(str(actual)+".csv"))
            _write(folder/"transport-audit.json", audit)
            require(model_input.read_bytes() == path.read_bytes() and
                    probe_input.read_bytes() == probe_path.read_bytes(), "owner_replay_input_changed")
            require(all(p.is_file() and not p.is_symlink() and p.stat().st_size == value["bytes"] and
                        file_hash(p) == value["sha256"]
                        for name, value in dependencies.items() for p in [source/name]),
                    "owner_replay_source_changed_during_run")
            row.update(passed=True, reason="native_import_and_exact_waveform")
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            row["reason"] = str(error)
        _write(folder/"result.json", row)
        rows.append(row)
    index = {"kind": "timelearner_recognition_owner_replay_result", "schema_version": 1,
        "execution": "completed", "passed": all(r["passed"] for r in rows),
        "source_archive_sha256": bundle["archive_sha256"], "origin_evidence_commit": spec["origin_evidence_commit"],
        "cases": rows, "scientific_verdict": None}
    _write(output/"index.json", index)
    return index


def audit_case_replay(package_path, replay):
    """Portable consistency with supplied original primaries; no local binary lookup."""
    package_path, replay = Path(package_path), Path(replay)
    case = load_case(package_path)
    index = load(replay/"index.json")
    require(index["kind"] == "timelearner_recognition_owner_replay_result" and
            type(index["schema_version"]) is int and index["schema_version"] == 1 and
            index["execution"] == "completed" and index["passed"] is True and index["scientific_verdict"] is None,
            "owner_replay_not_completed")
    ids = [r["id"] for r in index["cases"]]
    require(len(ids) == len(set(ids)), "duplicate_owner_replay_id")
    selected = [r for r in index["cases"] if r["source_filename"] == package_path.name]
    require(len(selected) == 1, "owner_replay_case_missing_or_duplicate")
    row = selected[0]
    require(row["passed"] is True and row["source_file_sha256"] == file_hash(package_path) and
            row["source_package_sha256"] == case[0]["sha256"] and
            row["source_solo_sha256"] == case[0]["source_solo"]["sha256"], "owner_replay_source_changed")
    require(re.fullmatch("[A-Za-z][A-Za-z0-9_]*", row["id"]), "owner_replay_case_id_invalid")
    folder = replay/row["id"]
    gate = load(folder/"gate/result.json")
    inventory = audit_junit(folder/"gate/native.xml", [TEST_ID])
    require(gate["execution"] == "completed" and gate["validity"] == "valid" and
            gate["assertion_status"] == "passed" and inventory["assertion_status"] == "passed" and
            gate["inventory"] == inventory, "owner_replay_native_inventory_changed")
    actual = folder/"actual.json"
    audit = audit_fresh_owner_process(case, load(actual), Path(str(actual)+".csv"))
    require(audit == load(folder/"transport-audit.json"), "owner_replay_transport_audit_changed")
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("specification", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run_replay(args.specification, args.output)
        print(json.dumps(result, allow_nan=False))
        return 0 if result["passed"] else 1
    except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"execution": "not_accepted", "reason": str(error), "scientific_verdict": None}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
