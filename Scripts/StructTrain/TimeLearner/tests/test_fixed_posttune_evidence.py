"""Replay real fixed-threshold selection, negative detection and later calibration."""
import copy
import math
import os
from pathlib import Path
import unittest

from ..calibration_transaction_evidence import audit_native_calibration_transaction
from ..calibration_transaction_reports import _spec
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..posttune_transaction_evidence import audit_posttune_transaction
from ..recognition_metrics import score_recognition_evaluation
from ..recognition_trial_evidence import audit_recognition_trial


class FixedPostTuneEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        artifacts = os.environ.get("TIMELEARNER_FIXED_POSTTUNE_ARTIFACTS")
        source = os.environ.get("TIMELEARNER_FIXED_POSTTUNE_SOURCE")
        if not artifacts or not source:
            raise unittest.SkipTest("requires both real native fixed PostTune controls and original sources")
        cls.root, cls.sources = Path(artifacts), {}
        for name in ("Classic-auto_metric", "Branch-synthetic"):
            folder = Path(source)/name
            run = load(folder/"run-manifest.json")
            package = folder/run["source_package_path"]
            cls.sources[load(package)["sha256"]] = load_case(package)
        cls.records = [load(p) for p in cls.root.glob("*_fixed_*_transaction.json")]
        if len(cls.records) != 8 or len(cls.sources) != 2:
            raise RuntimeError("requires all eight actual two-topology fixed selection/negative controls")

    def audit(self, report):
        return audit_posttune_transaction(report, self.sources[report["source_recognition"]["source_solo"]["sha256"]])

    def selected(self):
        return [r for r in self.records if r["status"] == "weights_selected"]

    def reject(self, report):
        report["sha256"] = sha({k: v for k, v in report.items() if k != "sha256"})
        with self.assertRaises(EvidenceError):
            self.audit(report)

    def test_all_eight_actual_controls_and_distinct_outcomes(self):
        self.assertEqual({s: sum(r["status"] == s for r in self.records) for s in
                          ("weights_selected", "budget_exhausted", "cancelled", "recovery_required")},
                         {"weights_selected": 2, "budget_exhausted": 2, "cancelled": 2, "recovery_required": 2})
        for report in self.records:
            proof = self.audit(report)
            self.assertTrue(proof["recorded_search_consistent"])
            self.assertTrue(proof["weight_selection_only"])
            self.assertEqual(proof["calibration_policy"], "fixed")
            self.assertEqual(proof["calibration_status"], "unverified" if report["status"] == "recovery_required" else "fixed")
            self.assertFalse(proof["recognition_success_confirmed"])
            self.assertFalse(proof["native_execution_verified"])
            self.assertIsNone(proof["evaluation_verdict"])

    def test_silent_target_remains_a_false_negative(self):
        for report in self.selected():
            self.audit(report)
            row = report["candidates"][report["selected_index"]]
            model = report["selected_package"]
            spec = _spec(row["matrix"], model, report["confirmation_specification"]["criterion"])
            metrics = score_recognition_evaluation(spec, row["matrix"]["observations"], model)
            self.assertEqual(metrics["validity"], "valid")
            self.assertEqual({k: metrics["pooled_counts"][k] for k in ("TP", "FP", "FN", "TN")},
                             {"TP": 0, "FP": 0, "FN": 1, "TN": 1})
            self.assertFalse(metrics["by_reset_policy"]["reset_per_trial"]["criterion_satisfied"])
            self.assertEqual(model["neuron"]["metadata"]["calibration"],
                             report["source_recognition"]["neuron"]["metadata"]["calibration"])
            self.assertEqual(report["calibration"], {})
            self.assertEqual(report["calibrated_package"], {})

    def test_roundtrip_samples_and_separate_later_calibration(self):
        wrappers = [load(p) for p in self.root.glob("*_fixed_*_roundtrip.json")]
        self.assertEqual(len(wrappers), 2)
        for wrapper in wrappers:
            model = wrapper["selected_package"]
            report = next(r for r in self.selected() if r["selected_package"] == model)
            row = report["candidates"][report["selected_index"]]
            originals = {o["trial_id"]: o for o in row["matrix"]["observations"]}
            self.assertEqual({o["trial_id"] for o in wrapper["observations"]}, set(originals))
            for observation in wrapper["observations"]:
                self.assertTrue(audit_recognition_trial(observation, model)["valid_observation"])
                self.assertTrue(observation["complete"])
                expected = originals[observation["trial_id"]]
                self.assertEqual(len(observation["samples"]), len(expected["samples"]))
                for actual, reference in zip(observation["samples"], expected["samples"]):
                    self.assertEqual(actual["stimulus"], reference["stimulus"])
                    self.assertEqual(len(actual["soma"]), len(reference["soma"]))
                    for a, b in zip(actual["soma"], reference["soma"]):
                        self.assertLessEqual(abs(a-b), 4*max(math.ulp(a), math.ulp(b)))
            child = wrapper["subsequent_calibration"]
            self.assertEqual(child["source_recognition"], model)
            child_proof = audit_native_calibration_transaction(child, self.sources[model["source_solo"]["sha256"]])
            self.assertIsNone(child_proof["evaluation_verdict"])
            self.assertIn(child["status"], ("calibrated", "nonseparable"))
            self.assertEqual(wrapper["package_after"], child["calibrated_package"] if child["status"] == "calibrated" else model)

    def test_no_forged_calibration_success_grid_or_selected_model(self):
        example = self.selected()[0]
        changes = (("recognition_success_confirmed", True), ("status", "calibrated"),
                   ("calibration_status", "calibrated"), ("finalization", "calibrate"),
                   ("thresholds", [0.1]), ("maximum_calibration_candidates", 1),
                   ("calibrated_package", example["selected_package"]),
                   ("selected_package", example["source_recognition"]),
                   ("selection_proof_embedded_in_model", True), ("source_restored", True),
                   ("active_matrix", {"requests": [example["trials"][0]], "observations": []}))
        for key, value in changes:
            with self.subTest(key=key):
                report = copy.deepcopy(example);report[key] = value;self.reject(report)

    def test_missing_observation_false_gap_and_row_permutation(self):
        example = self.selected()[0]
        missing = copy.deepcopy(example);missing["candidates"][0]["matrix"]["observations"].pop();self.reject(missing)
        wrong = copy.deepcopy(example);wrong["candidates"][0]["measured_gap"] += 1.;self.reject(wrong)
        for report in self.selected():
            shuffled = copy.deepcopy(report)
            for row in shuffled["candidates"]:row["matrix"]["observations"].reverse()
            shuffled["sha256"] = sha({k: v for k, v in shuffled.items() if k != "sha256"})
            self.assertTrue(self.audit(shuffled)["recorded_search_consistent"])
