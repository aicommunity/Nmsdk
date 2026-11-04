"""Policy validation and audits of real archived native cgroup executions.

The portable fixture suite must receive previously produced native process
records. It never manufactures a passing process/kernel record or runs a copy
of the supervisor implementation.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..native_process_policy import validate_policy, execute_native, audit_contained_attempt
from ..runtime import digest_json


POLICY = {"kind": "timelearner_native_process_policy", "schema_version": 1,
          "backend": "bound_cgroup", "memory_bytes": 1024**3, "tasks": 64, "cooperative_capture": True}


class NativeProcessPolicyTest(unittest.TestCase):
    def test_legacy_is_explicitly_separate(self):
        self.assertIsNone(validate_policy(None))

    def test_valid_policy_is_not_a_mutable_alias(self):
        value = copy.deepcopy(POLICY)
        result = validate_policy(value, 86400)
        result["tasks"] = 32
        self.assertEqual(value, POLICY)

    def test_unknown_schema_backend_and_fields_are_rejected(self):
        for change in ({"schema_version": True}, {"schema_version": 2}, {"backend": "fallback"},
                       {"extra": 1}, {"cooperative_capture": False}, {"cooperative_capture": 1}):
            with self.subTest(change=change), self.assertRaises(EvidenceError):
                validate_policy(POLICY | change)
        with self.assertRaises(EvidenceError):
            validate_policy({k: v for k, v in POLICY.items() if k != "tasks"})

    def test_unsafe_limits_and_budgets_are_rejected_before_launch(self):
        for key, values in (("tasks", [True, 0, -1, 1.0, 2**31]),
                            ("memory_bytes", [True, 0, -1, 1.0, 2**63])):
            for value in values:
                with self.subTest(key=key, value=value), tempfile.TemporaryDirectory() as tmp:
                    output = Path(tmp)/"process"
                    with self.assertRaises(EvidenceError):
                        execute_native({}, [], Path(tmp), output, 10, POLICY | {key: value})
                    self.assertFalse(output.exists())
        for value in (True, 0, .5, 86401, float("nan"), float("inf")):
            with self.subTest(wall=value), self.assertRaises(EvidenceError):
                validate_policy(POLICY, value)


class NativeContainedPortableEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.environ.get("TIMELEARNER_CONTAINED_POLICY_FIXTURES")
        if not path:
            raise unittest.SkipTest("requires actual archived native cgroup process fixtures")
        values = json.loads(Path(path).read_text())
        if type(values) is not list or len(values) != 2:
            raise RuntimeError("requires two declared real native codec/storage process fixtures")
        cls.fixtures = [Path(p).resolve(strict=True) for p in values]
        for p in cls.fixtures:
            if load(p/"result.json")["execution"] != "completed":
                raise RuntimeError("archived contained fixture did not complete")

    def cases(self):
        for original in self.fixtures:
            with tempfile.TemporaryDirectory() as tmp:
                destination = Path(tmp)/"relocated-process"
                shutil.copytree(original, destination)
                runtime, request = load(destination/"runtime.json"), load(destination/"request.json")
                policy = POLICY | {k: request[k] for k in ("memory_bytes", "tasks")}
                yield destination, runtime, policy

    def mutate(self, path, function, *, signed=False):
        value = load(path)
        function(value)
        if signed:
            value["sha256"] = digest_json({k: v for k, v in value.items() if k != "sha256"})
        path.write_text(json.dumps(value))

    def rejected(self, path, runtime, policy):
        with self.assertRaises((EvidenceError, FileNotFoundError)):
            audit_contained_attempt(path, runtime, policy, auditable=True)

    def test_actual_native_records_are_portable(self):
        for path, runtime, policy in self.cases():
            normalized = audit_contained_attempt(path, runtime, policy, auditable=True)
            self.assertEqual(normalized["model_time"], None)
            self.assertEqual(normalized["arguments"][-2], "--timelearner-capture-directory")
            self.assertEqual(normalized["arguments"][-1], str(Path(load(path/"request.json")["cancel_file"]).parent))

    def test_policy_cannot_change_actual_limits(self):
        for path, runtime, policy in self.cases():
            self.rejected(path, runtime, policy | {"memory_bytes": policy["memory_bytes"]+1})

    def test_missing_whole_group_closure_is_rejected(self):
        for path, runtime, policy in self.cases():
            (path/"whole-group-closure.json").unlink()
            self.rejected(path, runtime, policy)

    def test_live_descendants_cannot_be_promoted(self):
        for path, runtime, policy in self.cases():
            self.mutate(path/"whole-group-closure.json", lambda x: x.update(all_processes_closed=False))
            self.rejected(path, runtime, policy)

    def test_kernel_readback_cannot_be_replaced_by_declared_limits(self):
        for path, runtime, policy in self.cases():
            self.mutate(path/"contained/limits-readback.json", lambda x: x.update({"memory.max": "max"}))
            self.rejected(path, runtime, policy)

    def test_resigned_request_does_not_change_unit_binding(self):
        for path, runtime, policy in self.cases():
            self.mutate(path/"contained/request.json", lambda x: x.update(memory_bytes=x["memory_bytes"]+1), signed=True)
            self.rejected(path, runtime, policy)

    def test_main_pid_must_match_owned_binding(self):
        for path, runtime, policy in self.cases():
            self.mutate(path/"owned-process.json", lambda x: x.update(pid=x["pid"]+1))
            self.rejected(path, runtime, policy)

    def test_ready_and_ack_are_not_optional(self):
        for path, runtime, policy in self.cases():
            (path/"capture-ack.json").unlink()
            self.rejected(path, runtime, policy)

    def test_exit_status_is_bound_to_terminal_unit(self):
        for path, runtime, policy in self.cases():
            self.mutate(path/"terminal-unit-state.json", lambda x: x["state"].update(ExecMainStatus="2"))
            self.rejected(path, runtime, policy)

    def test_owned_executable_only_is_not_whole_group_ownership(self):
        for path, runtime, policy in self.cases():
            self.mutate(path/"result.json", lambda x: x.update(ownership_scope="launched_executable_only"))
            self.rejected(path, runtime, policy)

    def test_duplicate_loaded_paths_are_rejected(self):
        for path, runtime, policy in self.cases():
            p = path/"loaded-files.json"
            value = json.loads(p.read_text())
            value.append(copy.deepcopy(value[0]))
            p.write_text(json.dumps(value))
            self.rejected(path, runtime, policy)
