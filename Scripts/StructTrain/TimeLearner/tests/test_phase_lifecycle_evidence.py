"""Re-audit real native lifecycle detach controls, without inferring owner restoration."""
import copy
import os
from pathlib import Path
import unittest

from ..calibration_transaction_evidence import audit_native_calibration_transaction
from ..posttune_transaction_evidence import audit_posttune_transaction
from ..native_evidence import EvidenceError, load
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha


class NativePhaseLifecycleEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_PHASE_LIFECYCLE_ARTIFACTS")
        source = os.environ.get("TIMELEARNER_POSTTUNE_FIXED_SOURCE")
        if not directory or not source:
            raise unittest.SkipTest("requires actual native interruption controls and source primaries")
        cls.records = [load(p) for p in sorted(Path(directory).glob("*.json"))]
        if len(cls.records) != 16:
            raise RuntimeError("requires all 16 Classic/Branch native lifecycle controls")
        cls.sources = {}
        for name in ("Classic-auto_metric", "Branch-synthetic"):
            folder = Path(source)/name
            manifest = load(folder/"run-manifest.json")
            state = folder/manifest["source_package_path"]
            cls.sources[load(state)["sha256"]] = load_case(state)

    def audit(self, row, report):
        source = self.sources[report["source_recognition"]["source_solo"]["sha256"]]
        return (audit_native_calibration_transaction if row["controller"] == "threshold" else
                audit_posttune_transaction)(report, source)

    def test_all_sixteen_recovery_reports_preserve_partial_diagnostic_scope(self):
        seen = set()
        for row in self.records:
            self.assertEqual(row["kind"], "native_phase_lifecycle_interruption_control")
            report = row["transaction"]
            key = (row["topology"], row["controller"], row["operation"])
            self.assertNotIn(key, seen);seen.add(key)
            result = self.audit(row, report)
            self.assertEqual(report["status"], "recovery_required")
            self.assertFalse(report["source_restored"])
            self.assertIsNone(result["evaluation_verdict"])
            self.assertFalse(result["native_execution_verified"])
            if row["controller"] == "weights":
                self.assertEqual(result["calibration_status"], "unverified")
            if row["controller"] == "nested":
                self.assertEqual(report["calibration"]["status"], "recovery_required")
                self.assertFalse(report["calibration"]["source_restored"])
                self.assertGreater(row["model_ticks"], 0)
        expected = {(top, controller, operation) for top in ("classic", "branch")
                    for controller in ("weights", "threshold") for operation in ("reset", "default", "destroy")}
        expected |= {(top, "nested", operation) for top in ("classic", "branch") for operation in ("default", "destroy")}
        self.assertEqual(seen, expected)

    def test_recovery_cannot_claim_source_restored(self):
        for row in self.records:
            report = copy.deepcopy(row["transaction"]);report["source_restored"] = True
            report["sha256"] = sha({k: v for k, v in report.items() if k != "sha256"})
            with self.subTest(controller=row["controller"]), self.assertRaises(EvidenceError):
                self.audit(row, report)

    def test_interrupted_probe_cannot_be_upgraded_to_success(self):
        for row in self.records:
            report = copy.deepcopy(row["transaction"])
            report["status"] = "weights_selected" if row["controller"] == "weights" else "calibrated"
            report["sha256"] = sha({k: v for k, v in report.items() if k != "sha256"})
            with self.subTest(controller=row["controller"]), self.assertRaises(EvidenceError):
                self.audit(row, report)
