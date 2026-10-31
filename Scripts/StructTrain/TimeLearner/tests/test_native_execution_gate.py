"""Gate corruption tests use actual native execution and loader receipts."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError, load
from ..native_execution_gate import audit_native_gate, read_native_gate


class NativeExecutionGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names = ("TIMELEARNER_NATIVE_GATE_SPEC", "TIMELEARNER_NATIVE_GATE_ROOT", "TIMELEARNER_NATIVE_GATE_AFTER")
        if not all(os.environ.get(name) for name in names):
            raise unittest.SkipTest("requires real native XML, owned process and before/after runtime receipts")
        cls.spec = load(Path(os.environ[names[0]]))
        cls.receipts = read_native_gate(cls.spec, Path(os.environ[names[1]]), Path(os.environ[names[2]]))

    def test_actual_native_receipts_and_explicit_control_contract(self):
        result = audit_native_gate(self.spec, self.receipts)
        self.assertTrue(result["native_receipts_consistent"])
        self.assertFalse(result["payloads_audited"])
        self.assertFalse(result["process_lifetime_and_file_origin_attested"])

    def test_corrupt_actual_execution_scope_and_auxiliary_json_reject(self):
        for label, mutate in (
            ("xml_case", lambda r: r["junit"].find(".//testcase").set("name", "unexpected")),
            ("control_missing", lambda r: r["controls"].pop(next(iter(r["controls"])))),
            ("auxiliary_json", lambda r: r["controls"].update({"unexpected_state_trial_1.json": {"kind": "native_live_finalization_control", "schema_version": 1}})),
            ("returncode", lambda r: r["process"].update(returncode=1)),
            ("owned_executable", lambda r: r["owned"].update(executable="/other/test")),
            ("start_identity", lambda r: r["owned"].update(start_ticks="not-ticks")),
            ("loaded_empty", lambda r: r.update(loaded=[])),
            ("runtime_after", lambda r: r["runtime_after"].update(runtime_fingerprint="0"*64)),
            ("extra_args", lambda r: r["request"]["arguments"].append("--gtest_repeat=2")),
        ):
            receipts = deepcopy(self.receipts);mutate(receipts)
            with self.subTest(corruption=label):
                with self.assertRaises(EvidenceError):audit_native_gate(self.spec, receipts)
        spec = deepcopy(self.spec);spec["supervisor_policy"] = "require_zero"
        receipts = deepcopy(self.receipts);receipts["supervisor_status"] = 1
        with self.assertRaises(EvidenceError):audit_native_gate(spec, receipts)
