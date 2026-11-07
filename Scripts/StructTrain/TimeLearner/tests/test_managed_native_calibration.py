"""Measured full-grid native calibration of the actual new managed Train states.

Calibration is historical same-matrix; only real confirmation can select a
threshold. Nonseparable remains a valid negative result, never classification.
"""
import contextlib
from copy import deepcopy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import unittest

from ..__main__ import main
from ..contained_process import inspect as inspect_contained
from ..native_calibration_worker import audit_run_manifest as audit_calibration
from ..native_evidence import load
from ..native_pipeline_worker import audit_run_manifest as audit_pipeline
from ..native_process_policy import policy_for_reservation
from ..recognition_metrics import load_evaluation, score_recognition_evaluation
from ..resource_reservations import Reservations
from .test_managed_native_pipeline import signed


class ManagedNativeCalibrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        declaration = os.environ.get("TIMELEARNER_MANAGED_NATIVE_CALIBRATION")
        if not declaration:
            raise unittest.SkipTest("requires actual new managed Train states, runtime and controller")
        cls.spec = load(Path(declaration))
        if set(cls.spec) != {"runtime", "source", "controller", "output"}:
            raise RuntimeError("incomplete managed calibration declaration")
        cls.output = Path(cls.spec["output"])
        cls.output.mkdir(parents=True, exist_ok=False)

    def case(self, name):
        source = Path(self.spec["source"])/name/"runs"
        for phase in ("train", "export", "evaluate"):
            self.assertTrue(audit_pipeline(source/phase/"run-manifest.json")["run_evidence_consistent"])
        solo = source/"train/native/train_learned_state.json"
        model_path = source/"export/native/model.json"
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (solo, model_path)}
        model = load(model_path)
        original = load(source/"evaluate/input/job.json")
        spec, observations = load_evaluation(source/"evaluate/native/evaluation.json")
        self.assertEqual(len(observations), 4)
        self.assertEqual({o["trial_id"] for o in observations}, {t["trial_id"] for t in original["trials"]})
        self.assertTrue(all(o["valid"] and o["complete"] and o["spike_count"] == 0 for o in observations))
        peaks = [max(s["lt_potential"] for s in o["samples"] if s["time"] >= o["stimulus_onset"])
                 for o in observations]
        self.assertTrue(all(math.isfinite(p) and p > 0 for p in peaks))
        inherited = model["neuron"]["metadata"]["calibration"]["threshold"]
        unique = sorted(set(peaks))
        thresholds = sorted(set([.9*unique[0], 1.1*unique[-1], inherited]+
            [a+.5*(b-a) for a, b in zip(unique, unique[1:])]))
        root = self.output/name
        root.mkdir()
        (root/"proposal.json").write_text(json.dumps({"peaks": peaks, "thresholds": thresholds,
            "proposal_rule": "adjacent_measured_nonspiking_LTZ_midpoints_and_outer_controls_v1",
            "source_evaluation_manifest_sha256": load(source/"evaluate/run-manifest.json")["sha256"],
            "source_trial_ids": [o["trial_id"] for o in observations], "selection_verdict": None}, indent=2))
        registry = Reservations(root/"leases.sqlite3", managed_units=True,
            capacity={"slots": 1, "memory_bytes": 6*1024**3, "disk_bytes": 1024**3, "tasks": 512})
        lease = registry.reserve("managed-calibration-"+name,
            [{"path": str(root/"runs"), "access": "write"}],
            demands={"slots": 1, "memory_bytes": 4*1024**3+512*1024**2,
                     "disk_bytes": 512*1024**2, "tasks": 256},
            controller_directory=self.spec["controller"], ttl_seconds=1800)
        policy = policy_for_reservation(registry, lease["token"], memory_bytes=4*1024**3, tasks=64)
        policy_path = root/"policy.json"
        policy_path.write_text(json.dumps(policy))
        phases = []

        def invoke(mode, label, job):
            path = root/(label+"-job.json")
            path.write_text(json.dumps(signed(job), allow_nan=False))
            output = root/"runs"/label
            args = (["calibrate", "run"] if mode == "calibrate" else [mode])+[
                str(path), "--runtime-manifest", self.spec["runtime"], "--source-solo", str(solo),
                "--wall-seconds", "600", "--process-policy", str(policy_path), "--output", str(output)]
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
                code = main(args)
            (root/(label+"-cli.log")).write_text(stdout.getvalue(), encoding="utf-8")
            self.assertEqual(code, 0, stdout.getvalue())
            audit = (audit_calibration if mode == "calibrate" else audit_pipeline)(output/"run-manifest.json")
            self.assertTrue(audit["run_evidence_consistent"])
            self.assertTrue(inspect_contained(output/"process/contained")["all_processes_closed"])
            context = load(output/"process/reservation-context.json")
            self.assertEqual(context["lease"]["token"], lease["token"])
            binding = load(output/"process/contained/owned-unit.json")
            self.assertEqual(binding["unit"], context["intent"]["intent"]["unit"])
            self.assertEqual(registry.inspect()["leases"][0]["state"], "held")
            phases.append({"operation": label, "unit": binding["unit"], "audit": audit})
            return output

        job = {"kind": "timelearner_native_calibration_job", "schema_version": 1,
            "owner_class": original["owner_class"], "implementation_id": original["implementation_id"],
            "frequency_hz": load(solo)["configuration"]["model"]["frequency_hz"],
            "maximum_model_ticks": 200000, "source_recognition": model,
            "thresholds": thresholds, "maximum_candidates": len(thresholds),
            "specification": {"protocol": "historical_same_matrix",
                "data_partition_id": "managed-engineering-four-trial-primary-v1",
                "attempt_id": name+"/managed-grid", "clock_id": "native-2000Hz",
                "criterion": {k: v for k, v in original["criterion"].items() if k != "id"}},
            "trials": deepcopy(original["trials"])}
        grid = invoke("calibrate", "measured-grid", job)
        transaction = load(grid/"native/transaction.json")
        self.assertIn(transaction["status"], ("calibrated", "nonseparable", "confirmation_failed"))
        self.assertEqual(len(transaction["candidates"]), len(thresholds))
        final = load(grid/"native/model.json")
        evaluation = deepcopy(original)
        evaluation["source_recognition"] = final
        evaluation["run_id"] += "/after-managed-calibration"
        for i, trial in enumerate(evaluation["trials"]):
            trial["run_id"] = evaluation["run_id"]
            trial["trial_id"] = evaluation["run_id"]+"/"+str(i)
        frozen = invoke("evaluate", "fresh-frozen", evaluation)
        self.assertEqual(load(frozen/"native/model.json"), final)
        self.assertEqual(load(frozen/"native/model-after.json"), final)
        measured, actual = load_evaluation(frozen/"native/evaluation.json")
        score = score_recognition_evaluation(measured, actual, final)
        self.assertEqual(score["validity"], "valid")
        if transaction["status"] == "calibrated":
            self.assertIsNotNone(transaction["confirmation"])
            self.assertEqual({k: score["pooled_counts"][k] for k in ("TP", "FP", "FN", "TN")},
                             {"TP": 2, "FP": 0, "FN": 0, "TN": 2})
        else:
            self.assertTrue(transaction["source_restored"])
            self.assertEqual(final, model)
        silent = deepcopy(job)
        silent_threshold = 1.1*unique[-1]
        self.assertNotEqual(silent_threshold, inherited)
        silent["thresholds"] = [silent_threshold]
        silent["maximum_candidates"] = 1
        silent["specification"]["attempt_id"] += "/silent-control"
        rejected = invoke("calibrate", "silent-nonseparable", silent)
        rollback = load(rejected/"native/transaction.json")
        self.assertEqual(rollback["status"], "nonseparable")
        self.assertTrue(rollback["source_restored"])
        self.assertEqual(load(rejected/"native/model.json"), model)
        self.assertIsNone(rollback["calibrated_package"])
        self.assertEqual(len(rollback["candidates"]), 1)
        rejected_candidate = rollback["candidates"][0]
        changed = rejected_candidate["candidate"]
        self.assertEqual(changed["threshold"], silent_threshold)
        self.assertNotEqual(changed["model_revision"], model["model_revision"])
        self.assertEqual(changed["candidate_record"]["source_model_revision"], model["model_revision"])
        rejected_observations = rejected_candidate["matrix"]["observations"]
        self.assertEqual(len(rejected_observations), len(original["trials"]))
        self.assertEqual({o["trial_id"] for o in rejected_observations},
                         {t["trial_id"] for t in original["trials"]})
        for observation in rejected_observations:
            self.assertTrue(observation["valid"] and observation["complete"])
            self.assertEqual(observation["model_before"], changed["model_revision"])
            self.assertEqual(observation["model_after"], changed["model_revision"])
            self.assertEqual(observation["spike_count"], 0)
        # Import the actual returned package in another native process. JSON
        # restoration alone cannot establish the response of the restored graph.
        restored_evaluation = deepcopy(original)
        restored_evaluation["source_recognition"] = load(rejected/"native/model.json")
        restored_evaluation["run_id"] += "/after-changed-threshold-rollback"
        for i, trial in enumerate(restored_evaluation["trials"]):
            trial["run_id"] = restored_evaluation["run_id"]
            trial["trial_id"] = restored_evaluation["run_id"]+"/"+str(i)
        restored_run = invoke("evaluate", "rollback-frozen", restored_evaluation)
        self.assertEqual(load(restored_run/"native/model.json"), model)
        self.assertEqual(load(restored_run/"native/model-after.json"), model)
        _, restored_observations = load_evaluation(restored_run/"native/evaluation.json")
        self.assertEqual(len(restored_observations), len(observations))
        for baseline, restored in zip(observations, restored_observations):
            self.assertTrue(restored["valid"] and restored["complete"])
            self.assertEqual(restored["sample_id"], baseline["sample_id"])
            self.assertEqual(restored["samples"], baseline["samples"])
            self.assertEqual(restored["spike_count"], baseline["spike_count"])
        for path, digest in before.items():
            self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), digest)
        registry.release(lease["token"], note="Actual grid, fresh frozen, changed-threshold rejection and restored-model frozen units closed; source model unchanged.")
        self.assertEqual(registry.inspect()["leases"][0]["state"], "released")
        (root/"result.json").write_text(json.dumps({"phases": phases,
            "calibration_status": transaction["status"], "thresholds": thresholds,
            "frozen_counts": score["pooled_counts"], "silent_control_status": rollback["status"],
            "source_unchanged": True, "changed_threshold_rollback": {
                "source_threshold": inherited, "candidate_threshold": silent_threshold,
                "source_model_revision": model["model_revision"],
                "candidate_model_revision": changed["model_revision"],
                "fresh_restored_response_matches_source": True}, "scientific_verdict": None,
            "independent_partition_verified": False}, indent=2))

    def test_classic_modelspec1_measured_grid_and_silent_rollback(self):
        self.case("Classic-v1")

    def test_classic_modelspec2_measured_grid_and_silent_rollback(self):
        self.case("Classic-v2")

    def test_branch_modelspec1_measured_grid_and_silent_rollback(self):
        self.case("Branch-v1")

    def test_branch_modelspec2_measured_grid_and_silent_rollback(self):
        self.case("Branch-v2")
