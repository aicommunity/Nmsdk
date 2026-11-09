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


def supported_specification(spec):
    """V2 explicitly requests the executable's cooperative exit handshake.

    V1 retains its original launch contract; a missed mapping remains invalid.
    Never infer support from a binary name or silently retry a failed attempt.
    """
    if type(spec) is not dict or spec.get("kind") != "timelearner_native_test_gate" or type(spec.get("schema_version")) is not int:
        return False
    if spec["schema_version"] == 1:
        return set(spec) == FIELDS
    if spec['schema_version'] == 4:
        limits = spec.get('process_limits')
        return (set(spec) == FIELDS | {'cooperative_runtime_capture', 'process_limits', 'worker_lock'} and
                spec['cooperative_runtime_capture'] is True and type(limits) is dict and
                set(limits) == {'memory_bytes', 'maximum_processes'} and
                type(limits['memory_bytes']) is int and 32*1024**2 <= limits['memory_bytes'] <= 64*1024**3 and
                type(limits['maximum_processes']) is int and 1 <= limits['maximum_processes'] <= 64 and
                type(spec['worker_lock']) is str and bool(spec['worker_lock']))
    if spec['schema_version'] == 3:
        limits = spec.get('process_limits')
        return (set(spec) == FIELDS | {'cooperative_runtime_capture', 'process_limits'} and
                type(spec['cooperative_runtime_capture']) is bool and type(limits) is dict and
                set(limits) == {'memory_bytes', 'tasks'} and
                type(limits['memory_bytes']) is int and 0 < limits['memory_bytes'] <= 2**63-1 and
                type(limits['tasks']) is int and 0 < limits['tasks'] <= 2**31-1)
    return (spec["schema_version"] == 2 and set(spec) == FIELDS | {"cooperative_runtime_capture"}
            and spec["cooperative_runtime_capture"] is True)


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
    require(supported_specification(spec), "unknown_native_gate_specification")
    require(spec['schema_version'] != 4 or (os.name == 'nt' and spec['asan_options'] == ''),
            'windows_native_gate_platform_or_asan_mismatch')
    expected = spec["expected_test_ids"]
    require(type(expected) is list and bool(expected)
            and all(type(x) is str and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*/[A-Za-z_][A-Za-z0-9_]*", x)
                    for x in expected) and len(expected) == len(set(expected)), "invalid_native_gate_test_ids")
    require(type(spec["asan_options"]) is str and "\x00" not in spec["asan_options"], "invalid_native_gate_asan_options")
    wall = number(spec["maximum_wall_seconds"])
    require(wall > 0, "invalid_native_gate_wall_budget")
    if spec['schema_version'] == 3:
        require(1 <= wall <= 86400, 'invalid_contained_wall_budget')

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
    # The runner owns the supplied destination. An isolated fixture must not
    # depend on an earlier test having created its result directory.
    (output/"native").mkdir(exist_ok=False)
    _write(output/"specification.json", spec)
    _write(output/"runtime.json", runtime)
    environment = {key: runtime["loader_environment"].get(key)
                   for key in (("PATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM") if spec['schema_version'] == 4
                               else ("LD_LIBRARY_PATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM"))}
    environment.update(ASAN_OPTIONS=spec["asan_options"],
                       TIMELEARNER_EXECUTION_OUTPUT=str(output/"native"),
                       TIMELEARNER_COMPOSITE_OUTPUT=str(output/"native-composite"))
    with _environment(environment):
        runner, limits = execute, {}
        if spec['schema_version'] == 3:
            from .contained_runner import execute as contained_execute
            runner, limits = contained_execute, spec['process_limits']
        if spec['schema_version'] == 4:
            from .windows_process import execute as windows_execute
            lock = Path(spec['worker_lock'])
            lock = (lock if lock.is_absolute() else specification.parent/lock).resolve()
            require(source == Path(runtime['windows_source_root']).resolve(strict=True),
                    'windows_native_gate_source_binding_mismatch')
            def runner(manifest, arguments, cwd, destination, wall, **options):
                return windows_execute(manifest, arguments, cwd, destination, maximum_wall_seconds=wall,
                                       lock_file=lock, **options)
            limits = spec['process_limits']
        result = runner(runtime, ["--gtest_filter="+":".join(x.replace("/", ".") for x in expected),
                                  "--gtest_output=xml:"+str(output/"native.xml")],
                         executable.parent, output/"process", wall,
                         cooperative_capture=spec.get("cooperative_runtime_capture", False), **limits)
        verify_runtime(runtime)
    record = {"kind": "timelearner_native_test_gate_result", "schema_version": 1,
              "execution": result["execution"], "validity": "incomplete_test_observation",
              "assertion_status": "not_assessed", "reason": "native_result_not_available",
              "inventory": None, "scientific_verdict": None}
    try:
        if spec['schema_version'] == 3:
            require(result.get('schema_version') == 2 and result.get('ownership_scope') == 'bound_cgroup' and
                    result.get('all_processes_closed') is True, 'native_gate_whole_group_closure_missing')
        if spec['schema_version'] == 4:
            require(result.get('kind') == 'timelearner_windows_process_result' and
                    result.get('all_processes_closed') is True and result.get('validity') == 'valid' and
                    result.get('cooperative_capture') == 'completed', 'windows_native_gate_closure_or_capture_missing')
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
