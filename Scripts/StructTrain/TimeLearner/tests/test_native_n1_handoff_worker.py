"""Independent checks of actual positive N1 export/frozen Console artifacts."""
import copy
import os
from pathlib import Path
import unittest

from ..learned_evidence import audit_learned_state, load_case
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest
from ..recognition_metrics import load_evaluation, score_recognition_evaluation


class NativeN1HandoffWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_N1_HANDOFF_CORPUS")
        if not directory:
            raise unittest.SkipTest("requires actual positive N1 frozen worker controls")
        cls.root = Path(directory)
        cls.index = load(cls.root/"index.json")
        cls.rows = cls.index["records"]
        if cls.index["kind"] != "native_n1_exact_handoff_controls" or len(cls.rows) != 2:
            raise RuntimeError("incomplete positive N1 handoff corpus")

    def test_all_four_owned_operations_bind_genuine_exact_solo_sources(self):
        self.assertEqual(self.index["operations"], 4)
        for row in self.rows:
            for name in (row["export_name"], row["name"]):
                folder = self.root/"runs"/name
                audit = audit_run_manifest(folder/"run-manifest.json")
                self.assertTrue(audit["run_evidence_consistent"])
                manifest = load(folder/"run-manifest.json")
                self.assertEqual(manifest["execution"], "completed")
                source = load_case(folder/manifest["source_package_path"])
                self.assertTrue(audit_learned_state(*source)["exact"])
                self.assertEqual(source[0]["sha256"], row["source_solo_sha256"])

    def test_all_eight_patterns_and_target_positions_have_full_real_observations(self):
        design = load(self.root/"design.json")
        for row in self.rows:
            target_positions = set()
            folder = self.root/"runs"/row["name"]
            job = load(folder/"input/job.json")
            declared = next(d for d in design["rows"] if d["topology"] == row["name"].split("-")[0])
            self.assertEqual(job["trials"], declared["trials"])
            spec, observations = load_evaluation(folder/"native/evaluation.json")
            self.assertEqual(len(observations), 64)
            self.assertEqual(len({o["trial_id"] for o in observations}), 64)
            for start in range(0, 64, 8):
                block = job["trials"][start:start+8]
                self.assertEqual(len({t["pattern_hash"] for t in block}), 8)
                self.assertEqual(sum(t["label"] == "target" for t in block), 1)
                target_positions.add(next(i for i, t in enumerate(block) if t["label"] == "target"))
            for observation in observations:
                self.assertTrue(observation["complete"])
                self.assertEqual(observation["reset_policy"], "reset_per_trial")
            score = score_recognition_evaluation(spec, observations, load(folder/"native/model.json"))
            self.assertEqual(score["validity"], "valid")
            self.assertEqual(score["pooled_counts"]["targets"], 8)
            self.assertEqual(score["pooled_counts"]["foils"], 56)
            self.assertEqual(target_positions, set(range(8)))

    def test_frozen_model_and_threshold_remain_exactly_the_exported_values(self):
        for row in self.rows:
            export = load(self.root/"runs"/row["export_name"]/"native/model.json")
            folder = self.root/"runs"/row["name"]
            self.assertEqual(load(folder/"input/job.json")["source_recognition"], export)
            self.assertEqual(load(folder/"native/model.json"), export)
            self.assertEqual(load(folder/"native/model-after.json"), export)
            self.assertEqual(export["source_solo"]["sha256"], row["source_solo_sha256"])
            self.assertEqual(export["conversion_spec"], {"schema_version": 1, "mode": "identity", "resistance_bounds": []})
            calibration = export["neuron"]["metadata"]["calibration"]
            self.assertEqual(calibration["threshold"],
                             export["source_solo"]["neuron"]["metadata"]["calibration"]["threshold"])
            self.assertEqual(calibration["protocol"], "fixed-inherited-from-solo")
            self.assertEqual(calibration["source_solo_sha256"], row["source_solo_sha256"])

    def test_metrics_are_id_based_and_damaged_coverage_cannot_be_positive(self):
        for row in self.rows:
            folder = self.root/"runs"/row["name"]
            spec, observations = load_evaluation(folder/"native/evaluation.json")
            model = load(folder/"native/model.json")
            score = score_recognition_evaluation(spec, observations, model)
            self.assertEqual(score_recognition_evaluation(spec, list(reversed(observations)), model), score)
            for damaged in (observations[:-1], observations+[observations[0]]):
                with self.assertRaises(EvidenceError):
                    score_recognition_evaluation(spec, damaged, model)
            censored = copy.deepcopy(observations)
            censored[-1]["complete"] = False
            try:
                invalid = score_recognition_evaluation(spec, censored, model)
            except EvidenceError:
                pass
            else:
                self.assertEqual(invalid["validity"], "invalid")


if __name__ == "__main__":
    unittest.main()
