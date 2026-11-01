"""Actual production live Train/finalization and separate frozen evaluations."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest, validate_job
from .live_pipeline_corpus import signed


def save(path, value):
    path.write_text(json.dumps(value, allow_nan=False)+"\n", encoding="utf-8")


def refresh(folder, execution):
    for row in execution["artifacts"]:
        raw = (folder/"native"/row["path"]).read_bytes()
        row.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    save(folder/"native/execution.json", signed(execution))
    manifest = load(folder/"run-manifest.json")
    for row in manifest["artifacts"]:
        raw = (folder/row["path"]).read_bytes()
        row.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    save(folder/"run-manifest.json", signed(manifest))


class LivePipelineWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_LIVE_PIPELINE_CORPUS")
        if not directory:
            raise unittest.SkipTest("requires real production live Train corpus")
        cls.root = Path(directory);cls.index = load(cls.root/"index.json")
        if cls.index["operations"] != 14 or len(cls.index["records"]) != 14:
            raise RuntimeError("requires all fourteen actual production operations")
        cls.completed = tuple(top+"-"+mode for top in ("Classic", "Branch") for mode in ("fixed", "grid"))

    def test_actual_full_pipeline_and_partial_legacy_controls(self):
        for row in self.index["records"]:
            with self.subTest(run=row["name"]):
                folder = self.root/"runs"/row["name"]
                self.assertTrue(audit_run_manifest(folder/"run-manifest.json")["run_evidence_consistent"])
                e = load(folder/"native/execution.json")
                if row["name"] in self.completed:
                    self.assertTrue(e["completed_boundary"]);self.assertTrue(e["recognition_available"])
                    self.assertEqual(e["schema_version"], 2)
                elif row["operation"] == "train":
                    self.assertFalse(e["completed_boundary"])
                    self.assertFalse((folder/"native/recognition-model.json").exists())
                    if e["schema_version"] == 2:
                        m = load(folder/"run-manifest.json")
                        self.assertEqual(m["validity"], "valid")
                        self.assertFalse(e["recognition_available"])
                else:
                    self.assertEqual(load(folder/"native/model.json"), load(folder/"native/model-after.json"))
                self.assertIsNone(e["evaluation_verdict"])

    def test_resigned_source_phase_clock_and_recognition_corruption_rejected(self):
        for name in self.completed:
            for mutation in ("source_outcome", "availability", "missing_boundary", "missing_last_phase_tick"):
                with self.subTest(run=name, corruption=mutation), tempfile.TemporaryDirectory() as temporary:
                    folder = Path(temporary)/"run";shutil.copytree(self.root/"runs"/name, folder)
                    e = load(folder/"native/execution.json");live = load(folder/"native/finalization.json")
                    if mutation == "source_outcome":
                        e["training_outcome"] = "manufactured_exact"
                    elif mutation == "availability":
                        e["recognition_available"] = not e["recognition_available"]
                    else:
                        if mutation == "missing_boundary":
                            live["boundary"] = None
                        else:
                            live["post_tune_execution"]["advance_times"].pop()
                        signed(live);save(folder/"native/finalization.json", live)
                        e["finalization_sha256"] = live["sha256"]
                    refresh(folder, e)
                    with self.assertRaises(EvidenceError):audit_run_manifest(folder/"run-manifest.json")

    def test_preflight_unknown_and_invalid_persisted_plan_rejected(self):
        for name in self.completed:
            original = load(self.root/"runs"/name/"input/job.json")
            for mutation in ("unknown", "version", "trials", "thresholds", "implementation", "budget"):
                j = deepcopy(original);p = j["finalization_plan"]
                if mutation == "unknown":p["unknown_factor"] = True
                elif mutation == "version":p["schema_version"] = 999
                elif mutation == "trials":p["trials"] = []
                elif mutation == "thresholds":p["thresholds"] = ["damaged"]
                elif mutation == "implementation":p["implementation_id"] = "wrong"
                else:p["maximum_calibration_candidates"] = 1.5
                signed(p);signed(j)
                with self.subTest(run=name, corruption=mutation):
                    with self.assertRaises(EvidenceError):validate_job("train", j)

    def test_packaged_all_run_closures_and_cold_source_contract(self):
        from ..artifact_bundle import verify_packaged_run_closure
        files = {p.relative_to(self.root).as_posix(): p.read_bytes()
                 for p in (self.root/"runs").rglob("*") if p.is_file()}
        result = verify_packaged_run_closure(files)
        self.assertEqual(result["run_snapshots_verified"], 14)
        train = "runs/Classic-fixed/run-manifest.json";evaluation = "runs/Classic-fixed-evaluate/run-manifest.json"
        for mutation in ("missing_artifact", "changed_artifact", "cold_source", "evaluation_source", "operation"):
            changed = dict(files)
            if mutation in ("missing_artifact", "changed_artifact"):
                row = load(self.root/train)["artifacts"][0];key = "runs/Classic-fixed/"+row["path"]
                if mutation == "missing_artifact":changed.pop(key)
                else:changed[key] += b" "
            else:
                key = evaluation if mutation == "evaluation_source" else train
                m = json.loads(files[key])
                if mutation == "cold_source":m["source_package_path"] = "input/job.json"
                elif mutation == "evaluation_source":m["source_package_path"] = None
                else:m["operation"] = "invented"
                changed[key] = json.dumps(signed(m)).encode("utf-8")
            with self.subTest(corruption=mutation):
                with self.assertRaises(EvidenceError):verify_packaged_run_closure(changed)
