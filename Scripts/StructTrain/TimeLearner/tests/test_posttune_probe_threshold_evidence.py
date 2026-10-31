"""Replay distinct measurement/final physics from actual native transactions."""
import copy
import os
from pathlib import Path
import unittest

from ..calibration_transaction_reports import _spec
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..posttune_transaction_evidence import audit_posttune_transaction
from ..recognition_metrics import score_recognition_evaluation


class PostTuneProbeThresholdEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        artifacts = os.environ.get("TIMELEARNER_PROBE_THRESHOLD_ARTIFACTS")
        source = os.environ.get("TIMELEARNER_PROBE_THRESHOLD_SOURCE")
        if not artifacts or not source:
            raise unittest.SkipTest("requires real two-topology native probes and complete source primaries")
        cls.records = [load(p) for p in sorted(Path(artifacts).glob("*_probe_threshold_*.json"))]
        if len(cls.records) != 8:
            raise RuntimeError("requires eight actual final-boundary controls")
        cls.sources = {}
        for name in ("Classic-auto_metric", "Branch-synthetic"):
            folder = Path(source)/(name+"-legacy")
            manifest = load(folder/"run-manifest.json")
            path = folder/manifest["source_package_path"]
            cls.sources[load(path)["sha256"]] = load_case(path)

    def audit(self, report):
        return audit_posttune_transaction(report, self.sources[report["source_recognition"]["source_solo"]["sha256"]])

    def reject(self, report):
        report["sha256"] = sha({k: v for k, v in report.items() if k != "sha256"})
        with self.assertRaises(EvidenceError):
            self.audit(report)

    def test_all_eight_actual_controls_and_final_observation_scope(self):
        self.assertEqual({status: sum(r["status"] == status for r in self.records) for status in
                         ("weights_selected", "budget_exhausted", "cancelled", "recovery_required")},
                         {"weights_selected": 2, "budget_exhausted": 2, "cancelled": 2, "recovery_required": 2})
        for report in self.records:
            proof = self.audit(report)
            self.assertTrue(proof["recorded_search_consistent"])
            self.assertEqual(proof["weight_probe_threshold"], 2.)
            self.assertEqual(proof["final_threshold_responses_observed"], report["status"] == "weights_selected")
            self.assertFalse(proof["recognition_success_confirmed"])
            self.assertFalse(proof["owner_restoration_verified"])
            self.assertIsNone(proof["evaluation_verdict"])

    def test_fresh_final_silence_remains_target_miss(self):
        for report in self.records:
            if report["status"] != "weights_selected":
                continue
            self.audit(report)
            model, matrix = report["selected_package"], report["final_model_matrix"]
            design = _spec(matrix, model, report["confirmation_specification"]["criterion"])
            result = score_recognition_evaluation(design, matrix["observations"], model)
            self.assertEqual(result["validity"], "valid")
            self.assertEqual({k: result["pooled_counts"][k] for k in ("TP", "FP", "FN", "TN")},
                             {"TP": 0, "FP": 0, "FN": 1, "TN": 1})
            self.assertNotEqual(model["model_revision"], report["weight_measurement_candidates"][0]["model_revision"])

    def test_measurement_threshold_and_model_rebinding_are_rejected(self):
        for original in self.records:
            report = copy.deepcopy(original)
            report["weight_probe_threshold"] = 1.
            self.reject(report)
            report = copy.deepcopy(original)
            report["weight_measurement_candidates"][0] = report["candidates"][0]["candidate"]
            self.reject(report)

    def test_missing_final_matrix_cannot_be_claimed_as_completed(self):
        for original in self.records:
            report = copy.deepcopy(original)
            report.update(status="weights_selected", reason="", source_restored=False,
                          selected_package=report["candidates"][0]["candidate"],
                          final_threshold_responses_observed=True,
                          final_model_matrix={"requests": [], "observations": []})
            self.reject(report)
