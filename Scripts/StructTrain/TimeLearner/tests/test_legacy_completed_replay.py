"""Actual saved-state replay receipts plus preflight corruption; no substitute model."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..legacy_completed_replay import run_legacy_completed_replay
from ..native_evidence import EvidenceError, audit_probe, load
from ..native_gate import audit_junit


class LegacyCompletedReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_LEGACY_REPLAY_DIR")
        if not directory:
            raise unittest.SkipTest("requires a real completed four-case replay")
        cls.root = Path(directory)
        cls.spec = load(cls.root/"specification.json")

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="tl-legacy-replay-")
        self.addCleanup(directory.cleanup)
        self.temporary = Path(directory.name)

    def rejected(self, specification, reason):
        source, output = self.temporary/"specification.json", self.temporary/"output"
        source.write_text(json.dumps(specification, allow_nan=False)+"\n", encoding="utf-8")
        with self.assertRaisesRegex(EvidenceError, reason):
            run_legacy_completed_replay(source, output)
        self.assertFalse(output.exists(), "rejected declaration must not create output or launch native cases")

    def test_actual_complete_inventory_and_independent_raw_waveforms(self):
        result = load(self.root/"result.json")
        self.assertEqual(result["assertion_status"], "passed")
        expected = {row["id"] for row in self.spec["cases"]}
        self.assertEqual(len(result["cases"]), len(expected))
        self.assertEqual({row["case_id"] for row in result["cases"]}, expected)
        for row in self.spec["cases"]:
            case = self.root/row["id"]
            package, actual = load(case/"input-state.json"), load(case/"actual.json")
            self.assertEqual(hashlib.sha256((case/"input-state.json").read_bytes()).hexdigest(), row["package"]["raw_sha256"])
            self.assertEqual(package["kind"], "timelearner_completed_state")
            self.assertEqual(package["training_outcome"], "search_unresolved")
            self.assertFalse(package["certificate"]["exact"])
            self.assertEqual(actual["model"]["sha256"], package["model_revision"])
            self.assertEqual(actual["certificate"], package["certificate"])
            self.assertIs(actual["need"], False)
            self.assertEqual((case/"actual.json.csv").read_bytes(), (case/"expected.csv").read_bytes())
            self.assertIs(audit_probe(actual["probe"], case/"actual.json.csv")["valid_observation"], True)
            self.assertEqual(audit_junit(case/"gate/native.xml", ["NativeLearnedState/FreshProcessImport"])["assertion_status"], "passed")
            process = load(case/"gate/process/result.json")
            self.assertEqual((process["execution"], process["returncode"], process["runtime_provenance"]),
                             ("completed", 0, "loaded_files_captured"))

    def test_unknown_or_boolean_schema_is_rejected_before_output(self):
        for version in (True, 2):
            spec = deepcopy(self.spec)
            spec["schema_version"] = version
            self.rejected(spec, "unknown_legacy_completed_replay")

    def test_stored_or_raw_hash_mismatch_is_rejected_before_output(self):
        for field in ("stored_sha256", "raw_sha256"):
            spec = deepcopy(self.spec)
            spec["cases"][0]["package"][field] = "0"*64
            self.rejected(spec, "legacy_replay_.*hash_mismatch")

    def test_duplicate_case_id_cannot_run_a_partial_prefix(self):
        spec = deepcopy(self.spec)
        spec["cases"].append(deepcopy(spec["cases"][0]))
        self.rejected(spec, "invalid_legacy_replay_case")

    def test_existing_actual_result_is_not_overwritten(self):
        before = (self.root/"result.json").read_bytes()
        with self.assertRaisesRegex(EvidenceError, "legacy_replay_output_overlaps_inputs"):
            run_legacy_completed_replay(self.root/"specification.json", self.root)
        self.assertEqual((self.root/"result.json").read_bytes(), before)
