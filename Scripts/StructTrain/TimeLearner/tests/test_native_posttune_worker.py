"""Real Console export/evaluation for every typed native PostTune candidate."""
import json
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
from Scripts.StructTrain.TimeLearner.native_evidence import load
from Scripts.StructTrain.TimeLearner.native_pipeline_worker import audit_run_manifest, run_job


def _write(path, value):
    path.write_text(json.dumps(value, allow_nan=False)+"\n", encoding="utf-8")


def _signed(value):
    value["sha256"] = sha(value)
    return value


def create_actual_worker_controls(primary, runtime, output):
    """Explicit fixture operation; never executes on import."""
    primary, runtime, output = Path(primary), Path(runtime), Path(output)
    candidates = sorted(primary.glob("*_post_tune_candidate_*.json"))
    if len(candidates) != 20:
        raise ValueError("requires all twenty native PostTune candidates")
    output.mkdir(parents=True, exist_ok=False)
    records = []
    for i, path in enumerate(candidates):
        package = load(path)
        stem = path.name.split("_post_tune_candidate_")[0]
        source = primary/(stem+"_learned_state.json")
        solo = load(source)
        name = f"candidate-{i:03d}"
        job = _signed({"kind": "timelearner_native_recognition_export_job", "schema_version": 1,
                       "implementation_id": package["implementation_id"], "source_solo": solo,
                       "conversion_spec": package["conversion_spec"]})
        job_path = output/(name+"-export-job.json"); _write(job_path, job)
        run_job("export", job_path, source, runtime, output/(name+"-export"), 180)
        actual = load(output/(name+"-export/native/model.json"))
        if actual != package:
            raise ValueError("fresh_console_export_does_not_match_native_candidate")
        # The fixture producer fixes this two-pattern matrix; obtain target from
        # the immutable model metadata and check it against the protocol hash.
        target = solo["neuron"]["metadata"]["training"]["target_pattern"]
        if len(target) != 2 or sha(target) != solo["protocol"]["pattern_hash"]:
            raise ValueError("worker_control_target_does_not_match_native_protocol")
        foil = list(target); foil[-1] += .12
        run_id = name+"/frozen-diagnostic"
        trials = [{"run_id": run_id, "trial_id": run_id+"/"+label,
                   "sample_id": label, "label": label, "pattern_hash": sha(pattern), "pattern_isi": pattern,
                   "duration": .4, "maximum_samples": 802, "reset_policy": "reset_per_trial",
                   "record_threshold_potential": True} for label, pattern in (("target", target), ("foil", foil))]
        job = _signed({"kind": "timelearner_native_evaluation_job", "schema_version": 1,
                       "owner_class": "NNeuronTimeLearner"+("Branch" if solo["configuration"]["model"]["branch"] else ""),
                       "implementation_id": package["implementation_id"], "source_recognition": actual,
                       "maximum_model_ticks": 4000, "run_id": run_id, "coverage_policy": "per_trial_windows",
                       "criterion": {"id": "post_anchor_target_whole_window_foil_v1", "anchor": "onset",
                                     "begin_offset": 0., "end_offset": None, "reject_target_outside_window": True},
                       "trials": trials})
        job_path = output/(name+"-evaluate-job.json"); _write(job_path, job)
        run_job("evaluate", job_path, source, runtime, output/(name+"-evaluate"), 180)
        records.append({"name": name, "model_revision": actual["model_revision"],
                        "mode": package["conversion_spec"]["post_tune"]["mode"],
                        "source_training_outcome": solo["training_outcome"]})
    _write(output/"controls.json", {"kind": "native_posttune_worker_controls", "schema_version": 1,
                                   "records": records, "diagnostic_evaluation_only": True, "scientific_verdict": None})


class NativePostTuneWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_NATIVE_POSTTUNE_WORKER_DIR")
        if not value:
            raise unittest.SkipTest("requires twenty actual export/evaluation worker pairs")
        cls.root = Path(value)
        cls.records = load(cls.root/"controls.json")["records"]
        if len(cls.records) != 20:
            raise ValueError("incomplete native PostTune worker controls")

    def test_all_forty_actual_owned_operations(self):
        for record in self.records:
            for mode in ("export", "evaluate"):
                audit = audit_run_manifest(self.root/(record["name"]+"-"+mode)/"run-manifest.json")
                self.assertTrue(audit["run_evidence_consistent"])
                self.assertIsNone(audit["evaluation_verdict"])

    def test_conversion_does_not_advance_physical_time(self):
        for r in self.records:
            execution = load(self.root/(r["name"]+"-export/native/execution.json"))
            self.assertEqual(execution["model_ticks"], 0)

    def test_all_frozen_patterns_complete_and_model_unchanged(self):
        for r in self.records:
            folder = self.root/(r["name"]+"-evaluate")
            execution = load(folder/"native/execution.json")
            self.assertEqual(execution["execution"], "completed")
            self.assertEqual(execution["observed_trials"], 2)
            self.assertEqual(execution["model_revision"], r["model_revision"])
            analysis = load(folder/"run-manifest.json")["analysis"]
            self.assertTrue(analysis["frozen_model_verified"])
            self.assertEqual(analysis["metrics"]["validity"], "valid")

    def test_all_five_modes_have_equal_declared_coverage(self):
        from collections import Counter
        self.assertEqual(Counter(r["mode"] for r in self.records),
                         {"off": 4, "keep_done": 4, "canon_rmin": 4, "flat_last_r": 4, "search_synthetic_candidate": 4})
