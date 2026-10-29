import copy
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
from Scripts.StructTrain.TimeLearner.recognition_metrics import load_evaluation, score_recognition_evaluation


class RecognitionMetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_FROZEN_TRIAL_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual frozen native observations")
        root = Path(directory)
        paths = sorted(root.glob("*_owner_recognition_state.json"))
        if len(paths) != 4:
            raise RuntimeError("requires four native storage/threshold profiles")
        cls.cases = []
        for path in paths:
            package = load(path);prefix = path.name.removesuffix("_owner_recognition_state.json")
            observations = [load(root/f"{prefix}_frozen_trial_{i}.json") for i in range(4)]
            initial = package["source_solo"]["configuration"]["model"]["initial_isi"]
            hashes = [canonical_model_sha256(initial), canonical_model_sha256(list(reversed(initial)))]
            spec = {"kind": "timelearner_recognition_evaluation_spec", "schema_version": 1,
                    "run_id": prefix+"_frozen", "model_revision": package["model_revision"],
                    "coverage_policy": "per_trial_windows",
                    "criterion": {"id": "post_anchor_target_whole_window_foil_v1", "anchor": "last_stimulus",
                                  "begin_offset": 0., "end_offset": .02, "reject_target_outside_window": True},
                    "trials": [{"trial_id": f"trial_{i}", "sample_id": "foil_reverse" if i % 2 else "training_target",
                                "label": "foil" if i % 2 else "target", "pattern_hash": hashes[i % 2],
                                "reset_policy": "reset_per_trial" if i < 2 else "preserve_neuron_dynamics",
                                "presentation_index": i, "duration": .12, "observation": f"trial-{i}.json.gz"}
                               for i in range(4)]}
            cancelled = load(root/f"{prefix}_frozen_trial_cancelled.json")
            cls.cases.append((path, package, spec, observations, cancelled))

    def test_actual_negative_results_and_separate_reset_policies(self):
        for path, package, spec, observations, _ in self.cases:
            result = score_recognition_evaluation(spec, observations, package)
            self.assertEqual(result["validity"], "valid")
            self.assertEqual(set(result["by_reset_policy"]), {"reset_per_trial", "preserve_neuron_dynamics"})
            self.assertFalse(result["native_execution_verified"])
            self.assertIsNone(result["evaluation_verdict"])
            counts = result["pooled_counts"]
            self.assertEqual(counts["targets"], 2);self.assertEqual(counts["foils"], 2)
            if "_spiking_" not in path.name:
                self.assertEqual([counts[k] for k in ("TP", "FP", "FN", "TN")], [0, 0, 2, 2])
                self.assertEqual(counts["accuracy"], .5)
            else:
                self.assertGreater(counts["FP"], 0)
            for group in result["by_reset_policy"].values():
                self.assertTrue(group["criterion_assessed"])
                self.assertFalse(group["criterion_satisfied"])

    def test_row_permutation_and_relocation_preserve_result(self):
        for _, package, spec, observations, _ in self.cases:
            expected = score_recognition_evaluation(spec, observations, package)
            changed = copy.deepcopy(spec);changed["trials"].reverse()
            for trial in changed["trials"]:
                trial["observation"] = "moved/"+trial["observation"]
            self.assertEqual(score_recognition_evaluation(changed, list(reversed(observations)), package), expected)

    def test_missing_duplicate_and_wrong_label_cannot_score(self):
        _, package, spec, observations, _ = self.cases[0]
        for data in (observations[:-1], observations+[observations[0]]):
            with self.assertRaises(EvidenceError):
                score_recognition_evaluation(spec, data, package)
        changed = copy.deepcopy(observations);changed[1]["label"] = "target"
        with self.assertRaises(EvidenceError):
            score_recognition_evaluation(spec, changed, package)
        changed_spec = copy.deepcopy(spec);changed_spec["trials"][1]["label"] = "target"
        with self.assertRaises(EvidenceError):
            score_recognition_evaluation(changed_spec, observations, package)

    def test_censored_trial_produces_no_counts_or_positive_result(self):
        for _, package, spec, observations, cancelled in self.cases:
            changed = copy.deepcopy(observations);replacement = copy.deepcopy(cancelled)
            replacement["trial_id"] = "trial_0";changed[0] = replacement
            result = score_recognition_evaluation(spec, changed, package)
            self.assertEqual(result["validity"], "invalid")
            self.assertEqual(result["invalid_trial_ids"], ["trial_0"])
            self.assertIsNone(result["pooled_counts"])
            self.assertEqual(result["by_reset_policy"], {})
            self.assertIsNone(result["evaluation_verdict"])

    def synthetic_spike(self, original, index):
        # A rule-test mutation of real primary data, never native execution proof.
        observation = copy.deepcopy(original);time = observation["samples"][index]["time"]
        observation["spike_times"] = [time];observation["spike_count"] = 1
        observation["relative_spike_times"] = [time-observation["stimulus_onset"]]
        for i, sample in enumerate(observation["samples"]):
            sample["spike_history"] = [time] if i >= index else []
            sample["lt_output"] = 1. if index <= i < index+2 else 0.
        return observation

    def silent_case(self):
        return next(case for case in self.cases if "_spiking_" not in case[0].name)

    def test_early_target_response_is_not_a_target_hit(self):
        _, package, spec, observations, _ = self.silent_case()
        changed = copy.deepcopy(observations);changed[0] = self.synthetic_spike(changed[0], 10)
        result = score_recognition_evaluation(spec, changed, package)
        target = result["trials"][0]
        self.assertEqual(target["classification"], "FN")
        self.assertEqual(len(target["early_spikes"]), 1)
        self.assertFalse(result["by_reset_policy"]["reset_per_trial"]["criterion_satisfied"])

    def test_late_foil_response_is_counted_in_the_full_window(self):
        _, package, spec, observations, _ = self.silent_case()
        changed = copy.deepcopy(observations);changed[1] = self.synthetic_spike(changed[1], len(changed[1]["samples"])-1)
        result = score_recognition_evaluation(spec, changed, package)
        foil = result["trials"][1]
        self.assertEqual(foil["classification"], "FP")
        self.assertEqual(len(foil["late_spikes"]), 1)
        self.assertEqual(result["pooled_counts"]["FP"], 1)

    def test_unobserved_stream_gaps_are_not_silently_accepted(self):
        _, package, spec, observations, _ = self.silent_case()
        changed_spec = copy.deepcopy(spec);changed_spec["coverage_policy"] = "continuous_native_stream"
        self.assertEqual(score_recognition_evaluation(changed_spec, observations, package)["validity"], "valid")
        changed = copy.deepcopy(observations)
        for observation in changed[1:]:
            dt = 1/observation["frequency_hz"]
            for key in ("begin", "end", "closed_at", "stimulus_onset"):
                observation[key] += dt
            for key in ("stimulus_times", "spike_times"):
                observation[key] = [t+dt for t in observation[key]]
            for sample in observation["samples"]:
                sample["time"] += dt
                for key in ("stimulus_history", "spike_history"):
                    sample[key] = [t+dt for t in sample[key]]
        with self.assertRaises(EvidenceError):
            score_recognition_evaluation(changed_spec, changed, package)
        self.assertEqual(score_recognition_evaluation(spec, changed, package)["validity"], "valid")

    def test_unknown_criterion_and_false_calibration_claims_rejected(self):
        _, package, spec, observations, _ = self.cases[0]
        changed = copy.deepcopy(spec);changed["criterion"]["id"] = "unknown"
        with self.assertRaises(EvidenceError):
            score_recognition_evaluation(changed, observations, package)
        for key, value in (("threshold", 2.), ("status", "calibrated")):
            altered = copy.deepcopy(package);altered["neuron"]["metadata"]["calibration"][key] = value
            altered["sha256"] = canonical_model_sha256({k: v for k, v in altered.items() if k != "sha256"})
            with self.assertRaises(EvidenceError):
                score_recognition_evaluation(spec, observations, altered)

    def write_case(self, directory, case, invalid=False):
        _, package, spec, observations, cancelled = copy.deepcopy(case)
        if invalid:
            cancelled["trial_id"] = "trial_0";observations[0] = cancelled
        for trial, observation in zip(spec["trials"], observations):
            (directory/trial["observation"]).write_bytes(gzip.compress(json.dumps(observation, allow_nan=False).encode()))
        model = directory/"model.json.gz";model.write_bytes(gzip.compress(json.dumps(package).encode()))
        path = directory/"evaluation.json";path.write_text(json.dumps(spec), encoding="utf-8")
        return path, model

    def test_production_cli_reads_gzip_and_exits_nonzero_for_invalid(self):
        for invalid in (False, True):
            with tempfile.TemporaryDirectory() as temporary:
                path, model = self.write_case(Path(temporary), self.silent_case(), invalid)
                run = subprocess.run([sys.executable, "-m", "Scripts.StructTrain.TimeLearner", "analyze", str(path),
                                      "--format", "recognition-evaluation", "--model", str(model)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 2 if invalid else 0, run.stderr)
                result = json.loads(run.stdout)
                self.assertEqual(result["validity"], "invalid" if invalid else "valid")
                self.assertIsNone(result["evaluation_verdict"])

    def test_artifact_path_escape_and_bad_gzip_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary);path, _ = self.write_case(directory, self.silent_case())
            spec = load(path);spec["trials"][0]["observation"] = "../outside.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            with self.assertRaises(EvidenceError):
                load_evaluation(path)
            bad = directory/"broken.json.gz";bad.write_bytes(b"not gzip")
            with self.assertRaises(EvidenceError):
                load(bad)

    def test_nonfinite_and_duplicate_json_keys_are_rejected_in_gzip(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/"bad.json.gz"
            for text in ('{"value":NaN}', '{"value":1,"value":2}'):
                path.write_bytes(gzip.compress(text.encode()))
                with self.assertRaises(EvidenceError):
                    load(path)

    def test_nonfinite_primary_data_cannot_produce_metrics(self):
        _, package, spec, observations, _ = self.cases[0]
        changed = copy.deepcopy(observations);changed[0]["samples"][0]["soma"][0] = float("nan")
        with self.assertRaises(EvidenceError):
            score_recognition_evaluation(spec, changed, package)
