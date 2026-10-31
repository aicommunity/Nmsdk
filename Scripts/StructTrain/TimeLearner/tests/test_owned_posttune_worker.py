"""Owned Console phase: actual run closure and re-signed corrupted clock receipts."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_calibration_worker import audit_execution, audit_run_manifest
from ..native_evidence import EvidenceError, load


class OwnedPostTuneWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_OWNED_POSTTUNE_WORKER_DIR")
        if not value:
            raise unittest.SkipTest("requires actual production Console owned-phase corpus")
        cls.root = Path(value)
        cls.controls = load(cls.root/"controls.json")["records"]
        if len(cls.controls) != 18:
            raise RuntimeError("requires all eighteen mode/metric/budget controls")

    def test_all_actual_production_jobs_use_owned_phase(self):
        for control in self.controls:
            folder = self.root/control["name"]
            with self.subTest(case=control["name"]):
                audit = audit_run_manifest(folder/"run-manifest.json", post_tune=True)
                self.assertTrue(audit["run_evidence_consistent"])
                execution = load(folder/"native/execution.json")
                self.assertEqual(execution["schema_version"], 2)
                self.assertEqual(execution["post_tune_status"], control["expected_status"])
                phase = load(folder/"native/phase-execution.json")
                self.assertEqual(len(phase["advance_times"]), execution["model_ticks"])
                self.assertEqual(phase["advance_phase"], "owner_before_children")
                self.assertTrue(phase["done"])
                self.assertFalse(phase["dynamic_checkpoint"])
                self.assertIsNone(phase["evaluation_verdict"])

    def test_fixed_explicit_probe_jobs_keep_model_threshold_and_record_fresh_responses(self):
        root = self.root.parent/"fixed-runs"
        for topology in ("Classic", "Branch"):
            folder = root/(topology+"-fixed")
            with self.subTest(topology=topology):
                audit = audit_run_manifest(folder/"run-manifest.json",post_tune=True)
                self.assertTrue(audit["run_evidence_consistent"])
                job, execution = load(folder/"input/job.json"), load(folder/"native/execution.json")
                report = load(folder/"native/transaction.json")
                self.assertEqual(job["schema_version"],3)
                self.assertEqual(execution["schema_version"],2)
                self.assertEqual(report["status"],"weights_selected")
                self.assertEqual(report["finalization"],"keep_fixed_threshold")
                self.assertTrue(report["final_threshold_responses_observed"])
                self.assertFalse(report["recognition_success_confirmed"])
                self.assertEqual(len(load(folder/"native/phase-execution.json")["advance_times"]),execution["model_ticks"])

    def test_resigned_corrupt_phase_receipts_reject(self):
        # Production source, report, model and responses remain byte-identical.
        # Re-sign the changed file inventory so semantic checks must reject it.
        folder = self.root/self.controls[0]["name"]
        manifest = load(folder/"run-manifest.json")
        source = load_case(folder/manifest["source_package_path"])
        job = load(folder/"input/job.json")
        original = load(folder/"native/phase-execution.json")
        for name, mutate in (
            ("phase", lambda p: p.update(advance_phase="after_children")),
            ("missing_tick", lambda p: p["advance_times"].pop()),
            ("duplicate", lambda p: p["advance_times"].__setitem__(1,p["advance_times"][0])),
            ("origin", lambda p: p["advance_times"].__setitem__(0,p["advance_times"][0]+.0001)),
            ("frequency", lambda p: p.update(frequency_hz=1000)),
            ("done", lambda p: p.update(done=False)),
            ("checkpoint", lambda p: p.update(dynamic_checkpoint=True)),
            ("verdict", lambda p: p.update(evaluation_verdict=True)),
        ):
            with self.subTest(corruption=name), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                for path in (folder/"native").iterdir():
                    if path.is_file(): (target/path.name).write_bytes(path.read_bytes())
                phase = deepcopy(original);mutate(phase)
                data = (json.dumps(phase,allow_nan=False)+"\n").encode()
                (target/"phase-execution.json").write_bytes(data)
                execution = load(target/"execution.json")
                for record in execution["artifacts"]:
                    if record["path"] == "phase-execution.json":
                        record["bytes"] = len(data);record["sha256"] = hashlib.sha256(data).hexdigest()
                execution["sha256"] = sha({k:v for k,v in execution.items() if k!="sha256"})
                (target/"execution.json").write_text(json.dumps(execution),encoding="utf-8")
                with self.assertRaises(EvidenceError):
                    audit_execution(target,job,source,post_tune=True)
