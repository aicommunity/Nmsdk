"""Read back every declared joint44 frozen report through production readers."""
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import load
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
from Scripts.StructTrain.TimeLearner.recognition_metrics import load_evaluation
from Scripts.StructTrain.TimeLearner.tests import test_visual_report_evidence as _base


class JointFrozenReportEvidenceTest(_base.VisualReportEvidenceTest):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_JOINT44_VISUAL_DIR")
        recipe = os.environ.get("TIMELEARNER_JOINT44_VISUAL_RECIPE")
        if not root or not recipe:
            raise unittest.SkipTest("requires declared joint44 production reports")
        cls.root = Path(root)
        cls.recipe = load(Path(recipe))
        if cls.recipe["kind"] != "timelearner_joint44_frozen_report_recipe":
            raise RuntimeError("unknown joint frozen report recipe")
        cls.cases = [cls.root / (m["stem"].split("_", 1)[0]+f"-case-{i:02d}")
                     for i, m in enumerate(cls.recipe["models"])]
        actual = {p for p in cls.root.iterdir() if p.is_dir() and (p/"manifest.json").is_file()}
        if len(cls.cases) != cls.recipe["expected_models"] or actual != set(cls.cases):
            raise RuntimeError("declared joint report case coverage mismatch")

    def test_declared_trial_labels_patterns_thresholds_and_frozen_state(self):
        total_trials, total_pairs = 0, 0
        for model, case in zip(self.recipe["models"], self.cases):
            spec, observations = load_evaluation(case/"primary/evaluation.json")
            self.assertEqual(spec["run_id"], model["stem"]+"_frozen")
            self.assertEqual(spec["criterion"], self.recipe["criterion"])
            self.assertEqual(spec["coverage_policy"], self.recipe["coverage_policy"])
            package = load(case/"primary/model.json")
            self.assertEqual(package["neuron"]["metadata"]["calibration"]["threshold"], model["effective_threshold"])
            by_id = {o["trial_id"]: o for o in observations}
            self.assertEqual(set(by_id), {t["trial_id"] for t in self.recipe["trials"]})
            for trial in self.recipe["trials"]:
                o = by_id[trial["trial_id"]]
                for key in ("label", "sample_id", "reset_policy"):
                    self.assertEqual(o[key], trial[key])
                self.assertEqual(o["pattern_isi"], trial["pattern_isi"])
                self.assertEqual(o["pattern_hash"], canonical_model_sha256(trial["pattern_isi"]))
                self.assertTrue(o["complete"] and o["valid"] and o["armed"])
                self.assertFalse(o["censored"])
                self.assertEqual(o["model_before"], o["model_after"])
                self.assertAlmostEqual(o["end"]-o["begin"], trial["duration"], places=10)
            spikes = sum(o["spike_count"] for o in observations)
            self.assertEqual(spikes > 0, model["expected_spikes"])
            manifest = load(case/"manifest.json")
            self.assertEqual(manifest["expected_trial_soma_pairs"], len(observations)*model["soma_channels"])
            total_trials += len(observations)
            total_pairs += len(manifest["figures"])
        self.assertEqual(total_trials, self.recipe["expected_trials"])
        self.assertEqual(total_pairs, self.recipe["expected_trial_soma_pairs"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
