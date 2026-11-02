"""Owned execution of an already-built, explicitly declared native test set."""
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import re
from xml.etree import ElementTree as ET

from .native_calibration_worker import _write
from .native_evidence import EvidenceError, load, number, require
from .process_runner import execute, verify_runtime
from .runtime import source_closure


FIELDS = {"kind", "schema_version", "runtime_manifest", "source_root", "expected_test_ids",
          "maximum_wall_seconds", "asan_options"}


@contextmanager
def _environment(values):
    previous = {key: os.environ.get(key) for key in values}
    try:
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def audit_junit(path, expected):
    """An assertion failure is recorded data; missing/skipped cases are not PASS."""
    root = ET.parse(path).getroot()
    cases = list(root.iter("testcase"))
    identities = [c.get("classname", "")+"/"+c.get("name", "") for c in cases]
    require(len(identities) == len(set(identities)) and set(identities) == set(expected),
            "native_gate_junit_expected_set_mismatch")
    require(all(c.get("status") == "run" and c.get("result") == "completed"
                and c.find("skipped") is None for c in cases), "native_gate_skipped_or_unfinished_case")
    failed = [identity for identity, case in zip(identities, cases)
              if case.find("failure") is not None or case.find("error") is not None]
    require(root.get("tests") == str(len(expected)) and root.get("disabled", "0") == "0"
            and root.get("failures") == str(sum(c.find("failure") is not None for c in cases))
            and root.get("errors") == str(sum(c.find("error") is not None for c in cases)),
            "native_gate_junit_totals_mismatch")
    return {"expected": len(expected), "observed": len(cases), "failed_test_ids": failed,
            "assertion_status": "failed" if failed else "passed",
            "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def run_native_gate(specification, output):
    specification = Path(specification).resolve(strict=True)
    spec = load(specification)
    require(type(spec) is dict and set(spec) == FIELDS and spec["kind"] == "timelearner_native_test_gate"
            and type(spec["schema_version"]) is int and spec["schema_version"] == 1,
            "unknown_native_gate_specification")
    expected = spec["expected_test_ids"]
    require(type(expected) is list and bool(expected)
            and all(type(x) is str and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*/[A-Za-z_][A-Za-z0-9_]*", x)
                    for x in expected) and len(expected) == len(set(expected)), "invalid_native_gate_test_ids")
    require(type(spec["asan_options"]) is str and "\x00" not in spec["asan_options"], "invalid_native_gate_asan_options")
    wall = number(spec["maximum_wall_seconds"])
    require(wall > 0, "invalid_native_gate_wall_budget")

    def resolve(key):
        value = spec[key]
        require(type(value) is str and bool(value), "invalid_native_gate_path:"+key)
        path = Path(value)
        return (path if path.is_absolute() else specification.parent/path).resolve(strict=True)

    runtime_path, source = resolve("runtime_manifest"), resolve("source_root")
    runtime = load(runtime_path)
    executable = verify_runtime(runtime)
    output = Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(source) and not source.is_relative_to(output)
            and not output.is_relative_to(executable.parent) and not executable.parent.is_relative_to(output),
            "native_gate_output_overlaps_sources_or_runtime")
    require(source_closure(source) == runtime["source_closure"], "native_gate_source_context_changed")
    output.mkdir(parents=True, exist_ok=False)
    _write(output/"specification.json", spec)
    _write(output/"runtime.json", runtime)
    environment = {key: runtime["loader_environment"].get(key)
                   for key in ("LD_LIBRARY_PATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM")}
    environment.update(ASAN_OPTIONS=spec["asan_options"], TIMELEARNER_EXECUTION_OUTPUT=str(output/"native"))
    with _environment(environment):
        result = execute(runtime, ["--gtest_filter="+":".join(x.replace("/", ".") for x in expected),
                                  "--gtest_output=xml:"+str(output/"native.xml")],
                         executable.parent, output/"process", wall)
        verify_runtime(runtime)
    record = {"kind": "timelearner_native_test_gate_result", "schema_version": 1,
              "execution": result["execution"], "validity": "incomplete_test_observation",
              "assertion_status": "not_assessed", "reason": "native_result_not_available",
              "inventory": None, "scientific_verdict": None}
    try:
        require(result["runtime_provenance"] == "loaded_files_captured", "native_gate_loaded_runtime_missing")
        inventory = audit_junit(output/"native.xml", expected)
        require((inventory["assertion_status"] == "passed" and result["execution"] == "completed"
                 and result["returncode"] == 0) or
                (inventory["assertion_status"] == "failed" and result["execution"] == "process_error"
                 and result["returncode"] == 1), "native_gate_execution_junit_disagree")
        require(source_closure(source) == runtime["source_closure"], "native_gate_source_context_changed")
        record.update(validity="valid", assertion_status=inventory["assertion_status"],
                      reason="complete_declared_test_inventory", inventory=inventory)
    except (EvidenceError, OSError, ET.ParseError, ValueError, TypeError, KeyError) as error:
        record["reason"] = str(error)
    _write(output/"result.json", record)
    return record
