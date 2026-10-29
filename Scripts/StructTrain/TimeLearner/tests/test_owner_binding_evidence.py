"""Actual native editor-boundary controls and corruption rejection."""
import copy
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.owner_binding_evidence import audit_editor_binding, audit_editor_directory


class OwnerBindingEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_OWNER_BINDING_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual native owner editor boundary records")
        cls.directory = Path(directory)

    def test_all_native_controls_and_primary_boundary_probes(self):
        report = audit_editor_directory(self.directory)
        self.assertEqual((report["cases"], report["matching"]), (12, 6))
        self.assertGreater(report["boundary_samples"], 0)
        self.assertIsNone(report["evaluation_verdict"])

    def test_corrupted_actual_owner_records_cannot_pass(self):
        paths = sorted(self.directory.glob("*_editor_binding.json"))
        self.assertEqual(len(paths), 12)
        for path in paths:
            original = load(path)
            audit_editor_binding(original)
            corruptions = [
                ("schema_version", True), ("schema_version", 99),
                ("evaluation_verdict", "PASS"), ("model_after", "missing"),
                ("matching", not original["matching"]),
                ("owner_resistances", [float("nan"), 1]),
                ("owner_counts", [True, 1]), ("source_resistances", [1, 1]),
            ]
            if not original["matching"]:
                corruptions += [("status", "applied"), ("model_may_have_changed", True)]
            for key, value in corruptions:
                with self.subTest(case=path.name, corruption=key):
                    record = copy.deepcopy(original)
                    record[key] = value
                    with self.assertRaises(EvidenceError):
                        audit_editor_binding(record)
