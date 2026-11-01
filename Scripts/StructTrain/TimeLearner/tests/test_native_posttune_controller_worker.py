"""Production-process gates; genuine compact Console run corpus required."""
import contextlib
import copy
import io
import os
from pathlib import Path
import unittest

from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_calibration_worker import audit_run_manifest, validate_job
from ..native_evidence import EvidenceError, load


class NativePostTuneControllerWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_POSTTUNE_CONTROLLER_WORKER_DIR")
        if not value:
            raise unittest.SkipTest("requires actual owned Console PostTune runs")
        cls.root = Path(value)
        cls.controls = load(cls.root/"controls.json")["records"]
        if len(cls.controls) != 18 or len({r["name"] for r in cls.controls}) != 18:
            raise RuntimeError("requires 18 real Classic/Branch mode/metric/silent/budget controls")

    def example(self):
        folder = self.root/self.controls[0]["name"]
        manifest = load(folder/"run-manifest.json")
        return load(folder/"input/job.json"), load_case(folder/manifest["source_package_path"])

    def test_all_eighteen_portable_runs_and_actual_outcomes(self):
        modes, metrics, owners = set(), set(), set()
        for control in self.controls:
            folder = self.root/control["name"]
            proof = audit_run_manifest(folder/"run-manifest.json", post_tune=True)
            self.assertTrue(proof["run_evidence_consistent"])
            self.assertFalse(proof["native_execution_verified"])
            self.assertIsNone(proof["evaluation_verdict"])
            job, report = load(folder/"input/job.json"), load(folder/"native/transaction.json")
            modes.add(job["post_tune"]["mode"]);metrics.add(job["post_tune"]["metric"]);owners.add(job["owner_class"])
            self.assertEqual(report["status"], control["expected_status"])
            self.assertEqual(load(folder/"process/result.json")["returncode"], 0)
        self.assertEqual(modes, {"off", "keep_done", "canon_rmin", "flat_last_r", "search_synthetic"})
        self.assertEqual(metrics, {"auto", "ltzone", "soma_sum"})
        self.assertEqual(owners, {"NNeuronTimeLearner", "NNeuronTimeLearnerBranch"})

    def test_real_cli_analysis_and_protocol_separation(self):
        from ..__main__ import main
        path = self.root/self.controls[0]["name"]/"run-manifest.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["analyze", str(path), "--format", "posttune-run"]), 0)
        with self.assertRaises(EvidenceError):
            audit_run_manifest(path)

    def test_preflight_rejects_unused_physics_bad_modes_and_unknown_fields(self):
        original, source = self.example()
        for edit in ({"mode": "search_synthetic_candidate"}, {"metric": "unknown"}, {"canonical_floor": 1.},
                     {"maximum_recorded_samples": True}, {"unexpected": 1}, {"search_passes": 0}):
            with self.subTest(edit=edit):
                job = copy.deepcopy(original);job["post_tune"].update(edit)
                job["sha256"] = sha({k: v for k, v in job.items() if k != "sha256"})
                with self.assertRaises(EvidenceError):
                    validate_job(job, source, post_tune=True)

    def test_condition_identity_includes_weight_search_and_model_tick_budgets(self):
        original, source = self.example()
        before = validate_job(original, source, post_tune=True)["conditions_digest"]
        for field in ("maximum_model_ticks", "maximum_recorded_samples"):
            job = copy.deepcopy(original)
            obj = job if field == "maximum_model_ticks" else job["post_tune"]
            obj[field] += 1
            job["sha256"] = sha({k: v for k, v in job.items() if k != "sha256"})
            self.assertNotEqual(before, validate_job(job, source, post_tune=True)["conditions_digest"])
