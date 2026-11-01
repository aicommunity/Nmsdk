"""Selection over actual native threshold measurements and original source CSV.

The two-threshold fixture is nonseparable under the declared criterion. It is
not fabricated into a positive confirmation or an exhaustive physical result.
"""
import copy
import os
import unittest

from . import test_threshold_candidate_evidence as fixtures
from ..calibration import RULE, calibration_dataset_digest, confirm_threshold, select_threshold
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError


class CalibrationStudyEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get("TIMELEARNER_THRESHOLD_CANDIDATE_DIR"):
            raise unittest.SkipTest("requires the complete native calibration candidate matrix")
        fixtures.ThresholdCandidateEvidenceTest.setUpClass()
        groups = {}
        for path, package, source, observations, invalid in fixtures.ThresholdCandidateEvidenceTest.cases:
            base = package["source_recognition"]
            evaluation = fixtures.ThresholdCandidateEvidenceTest.specification(path, package)
            group = groups.setdefault(base["sha256"], {"base": base, "source": source, "measurements": [], "invalid": []})
            group["measurements"].append({"candidate": package, "evaluation_spec": evaluation, "observations": observations,
                "execution": {"attempt_id": "native-"+base["sha256"], "clock_id": "clock-"+base["sha256"],
                              "stage": "search", "selection_sha256": None}})
            group["invalid"].extend(invalid)
        cls.groups = list(groups.values())
        if len(cls.groups) != 8 or any(len(group["measurements"]) != 2 for group in cls.groups):
            raise RuntimeError("requires eight immutable source models and two thresholds per source")
        for group in cls.groups:
            group["measurements"].sort(key=lambda measurement: measurement["candidate"]["threshold"])
            base = group["base"]
            evaluation = group["measurements"][0]["evaluation_spec"]
            target = base["source_solo"]["configuration"]["model"]["initial_isi"]
            trials = []
            for trial in evaluation["trials"]:
                item = {key: value for key, value in trial.items() if key not in ("observation", "pattern_hash")}
                item["pattern_isi"] = target if trial["label"] == "target" else list(reversed(target))
                trials.append(item)
            spec = {"kind": "timelearner_threshold_calibration_spec", "schema_version": 1,
                    "calibration_id": "fixture-"+base["sha256"], "protocol": "historical_same_matrix",
                    "data_partition_id": "native-threshold-control-v1", "source_recognition_sha256": base["sha256"],
                    "source_model_revision": base["model_revision"], "coverage_policy": evaluation["coverage_policy"],
                    "criterion": evaluation["criterion"], "trials": trials, "thresholds": [.0001, 1.],
                    "maximum_candidates": 2, "selection_rule": RULE}
            spec["dataset_digest"] = calibration_dataset_digest(spec["coverage_policy"], spec["criterion"], trials)
            group["spec"] = spec

    def test_complete_real_grid_remains_nonseparable_without_a_selected_model(self):
        for group in self.groups:
            result = select_threshold(group["spec"], group["measurements"], group["source"])
            self.assertEqual(result["status"], "nonseparable")
            self.assertTrue(result["grid_complete"])
            self.assertFalse(result["calibrated"])
            self.assertFalse(result["native_execution_verified"])
            self.assertIsNone(result["selected_candidate"])
            self.assertIsNone(result["selected_threshold"])
            self.assertTrue(all(row["target_violations"] or row["foil_responses"] for row in result["candidates"]))
            self.assertIsNone(result["evaluation_verdict"])

    def test_order_independent_measurements_and_rows(self):
        group = self.groups[0]
        expected = select_threshold(group["spec"], group["measurements"], group["source"])
        reversed_measurements = copy.deepcopy(list(reversed(group["measurements"])))
        for measurement in reversed_measurements:measurement["observations"].reverse()
        self.assertEqual(expected, select_threshold(group["spec"], reversed_measurements, group["source"]))

    def test_silent_budget_prefix_does_not_become_success(self):
        for group in self.groups:
            spec = copy.deepcopy(group["spec"]);spec["thresholds"] = [1., .0001];spec["maximum_candidates"] = 1
            high = group["measurements"][1]
            result = select_threshold(spec, [high], group["source"])
            self.assertEqual(result["status"], "budget_exhausted")
            self.assertFalse(result["grid_complete"])
            self.assertFalse(result["calibrated"])
            self.assertEqual(result["candidates"][0]["target_violations"], 2)
            self.assertIsNone(result["selected_candidate"])

    def test_missing_and_duplicate_candidates_are_rejected(self):
        group = self.groups[0]
        for measurements in (group["measurements"][:1], [group["measurements"][0]]*2):
            with self.assertRaises(EvidenceError):select_threshold(group["spec"], measurements, group["source"])

    def test_different_source_and_incomplete_trials_are_rejected(self):
        group = self.groups[0]
        for change in ("source", "missing", "cancelled"):
            measurements = copy.deepcopy(group["measurements"])
            if change == "source":measurements[1] = self.groups[1]["measurements"][1]
            elif change == "missing":measurements[0]["observations"].pop()
            else:measurements[0]["observations"][0] = group["invalid"][0]
            with self.assertRaises(EvidenceError):select_threshold(group["spec"], measurements, group["source"])

    def test_dataset_change_and_unbalanced_policy_are_rejected(self):
        group = self.groups[0]
        for change in ("hash", "policy", "schema", "threshold"):
            spec = copy.deepcopy(group["spec"])
            if change == "hash":spec["trials"][0]["duration"] *= 2
            elif change == "policy":spec["trials"][0]["reset_policy"] = "preserve_neuron_dynamics"
            elif change == "schema":spec["schema_version"] = True
            else:spec["thresholds"][0] = float("nan")
            with self.assertRaises(EvidenceError):select_threshold(spec, group["measurements"], group["source"])

    def test_attempt_identity_is_separate_from_scientific_conditions(self):
        group = self.groups[0]
        first = select_threshold(group["spec"], group["measurements"], group["source"])
        spec = copy.deepcopy(group["spec"]);spec["calibration_id"] += "-another-attempt"
        other = select_threshold(spec, group["measurements"], group["source"])
        self.assertEqual(first["conditions_digest"], other["conditions_digest"])
        self.assertNotEqual(first["spec_digest"], other["spec_digest"])

    def test_declared_trial_array_order_does_not_change_conditions(self):
        group = self.groups[0]
        first = select_threshold(group["spec"], group["measurements"], group["source"])
        spec = copy.deepcopy(group["spec"]);spec["trials"].reverse()
        other = select_threshold(spec, group["measurements"], group["source"])
        self.assertEqual(first["conditions_digest"], other["conditions_digest"])
        self.assertEqual(first["candidates"], other["candidates"])
        self.assertEqual(first["status"], other["status"])

    def test_nonseparable_selection_cannot_be_confirmed(self):
        group = self.groups[0]
        result = select_threshold(group["spec"], group["measurements"], group["source"])
        confirmation = copy.deepcopy(group["measurements"][0])
        confirmation["execution"].update(stage="confirmation", selection_sha256=result["sha256"])
        with self.assertRaisesRegex(EvidenceError, "no_separable_selection"):
            confirm_threshold(group["spec"], group["measurements"], group["source"], result, confirmation)

    def test_resigned_forged_positive_selection_is_rejected(self):
        group = self.groups[0]
        result = select_threshold(group["spec"], group["measurements"], group["source"])
        result["status"] = "pending_confirmation";result.pop("sha256")
        result["sha256"] = canonical_model_sha256(result)
        with self.assertRaisesRegex(EvidenceError, "selection_mismatch"):
            confirm_threshold(group["spec"], group["measurements"], group["source"], result, group["measurements"][0])
