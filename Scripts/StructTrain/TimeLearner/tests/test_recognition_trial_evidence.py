import copy
import os
from pathlib import Path
import subprocess
import sys
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.recognition_trial_evidence import audit_recognition_trial, audit_recognition_trial_set


class RecognitionTrialEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_FROZEN_TRIAL_DIR")
        if not root:
            raise unittest.SkipTest("requires real native frozen trials")
        cls.root = Path(root)
        cls.packages = sorted(cls.root.glob("*_owner_recognition_state.json"))
        if len(cls.packages) != 2:
            raise RuntimeError("requires Classic and Branch fresh-owner packages")
        cls.cases = []
        for path in cls.packages:
            prefix = path.name.removesuffix("_owner_recognition_state.json")
            trials = [load(cls.root / f"{prefix}_frozen_trial_{i}.json") for i in range(4)]
            errors = [load(cls.root / f"{prefix}_frozen_trial_{name}.json") for name in ("cancelled", "gap")]
            cls.cases.append((path, load(path), trials, errors))

    def test_real_complete_target_foil_windows(self):
        for _, package, trials, _ in self.cases:
            for trial in trials:
                result = audit_recognition_trial(trial, package)
                self.assertTrue(result["valid_observation"])
                self.assertTrue(result["complete"])
                self.assertIsNone(result["evaluation_verdict"])

    def test_actual_cancel_and_gap_remain_incomplete(self):
        for _, package, _, errors in self.cases:
            self.assertEqual([e["reason"] for e in errors], ["explicit_cancel", "recognition_sample_gap"])
            for trial in errors:
                result = audit_recognition_trial(trial, package)
                self.assertFalse(result["valid_observation"])
                self.assertFalse(result["complete"])

    def test_corrupt_fields_numbers_timestamps_and_model_rejected(self):
        for _, package, trials, _ in self.cases:
            original = trials[0]
            for key, value in (("schema_version", 99), ("label", "unknown"), ("complete", 1),
                               ("spike_count", original["spike_count"] + 1), ("pattern_hash", "0"*64),
                               ("model_after", "0"*64), ("closed_at", original["closed_at"]-.01),
                               ("stimulus_times", [float("nan")])):
                trial = copy.deepcopy(original);trial[key] = value
                with self.subTest(key=key), self.assertRaises(EvidenceError):
                    audit_recognition_trial(trial, package)
            trial = copy.deepcopy(original);trial["samples"][1]["soma"][0] = float("inf")
            with self.assertRaises(EvidenceError):
                audit_recognition_trial(trial, package)
            trial = copy.deepcopy(original);trial["samples"].pop(1)
            with self.assertRaises(EvidenceError):
                audit_recognition_trial(trial, package)

    def expected(self, trials):
        return {(trial["run_id"], f"trial_{i}"): {
            "sample_id": "foil_reverse" if i % 2 else "training_target",
            "label": "foil" if i % 2 else "target", "pattern_hash": trial["pattern_hash"]}
            for i, trial in enumerate(trials)}

    def test_trial_permutation_preserves_audit(self):
        for _, package, trials, _ in self.cases:
            expected = self.expected(trials)
            forward = audit_recognition_trial_set(trials, expected, package)
            reverse = audit_recognition_trial_set(list(reversed(trials)), expected, package)
            self.assertEqual(forward, reverse)
            self.assertTrue(forward["all_observations_valid"])

    def test_missing_duplicate_and_wrong_label_rejected(self):
        for _, package, trials, _ in self.cases:
            expected = self.expected(trials)
            for changed in (trials[:-1], trials + [trials[0]]):
                with self.assertRaises(EvidenceError):
                    audit_recognition_trial_set(changed, expected, package)
            changed = copy.deepcopy(trials);changed[1]["label"] = "target"
            with self.assertRaises(EvidenceError):
                audit_recognition_trial_set(changed, expected, package)

    def test_production_cli_requires_model_and_preserves_null_verdict(self):
        import json
        for path, _, _, _ in self.cases:
            prefix = path.name.removesuffix("_owner_recognition_state.json")
            trial = self.root / f"{prefix}_frozen_trial_0.json"
            command = [sys.executable, "-m", "Scripts.StructTrain.TimeLearner", "analyze", str(trial),
                       "--format", "recognition-trial"]
            missing = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(missing.returncode, 2)
            self.assertIn("recognition_model_package_required", missing.stderr)
            actual = subprocess.run(command + ["--model", str(path)], capture_output=True, text=True)
            self.assertEqual(actual.returncode, 0, actual.stderr)
            result = json.loads(actual.stdout)
            self.assertTrue(result["analysis"]["valid_observation"])
            self.assertIsNone(result["evaluation_verdict"])
