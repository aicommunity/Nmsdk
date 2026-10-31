"""Actual cold pipeline evidence and rehashed adversarial changes."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_execution, audit_run_manifest
from ..learned_evidence import load_case


def save(path, value):
    path.write_text(json.dumps(value, allow_nan=False)+"\n", encoding="utf-8")


def resign(value):
    value.pop("sha256", None);value["sha256"] = sha(value)
    return value


def refresh_manifest(folder):
    m = load(folder/"run-manifest.json")
    for record in m["artifacts"]:
        data = (folder/record["path"]).read_bytes()
        record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    save(folder/"run-manifest.json", resign(m))


class NativePipelineWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_PIPELINE_CLI_DIR")
        if not directory:
            raise unittest.SkipTest("requires four completed owned cold pipelines")
        cls.root = Path(directory)
        cls.cases = ("Classic-N0", "Classic-N1", "Branch-N0", "Branch-N1")

    def test_all_twelve_actual_owned_phases(self):
        for case in self.cases:
            for phase in ("train", "export", "evaluate"):
                result = audit_run_manifest(self.root/(case+"-"+phase)/"run-manifest.json")
                self.assertTrue(result["run_evidence_consistent"])
                self.assertFalse(result["native_execution_verified"])
                self.assertIsNone(result["evaluation_verdict"])

    def test_rehashed_cold_readback_mismatch_is_rejected(self):
        for case in self.cases:
            with tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)/"run";shutil.copytree(self.root/(case+"-train"), folder)
                initial = load(folder/"native/initial-state.json");initial["parameters"][0]["synapses"] += 1
                save(folder/"native/initial-state.json", resign(initial))
                execution = load(folder/"native/execution.json")
                for record in execution["artifacts"]:
                    raw = (folder/"native"/record["path"]).read_bytes()
                    record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                save(folder/"native/execution.json", resign(execution));refresh_manifest(folder)
                with self.assertRaisesRegex(EvidenceError, "pipeline_cold_parameters_changed"):
                    audit_run_manifest(folder/"run-manifest.json")

    def test_rehashed_target_omission_cannot_shrink_expected_design(self):
        for case in self.cases:
            with tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)/"run";shutil.copytree(self.root/(case+"-evaluate"), folder)
                spec = load(folder/"native/evaluation.json");spec["trials"].pop(0)
                save(folder/"native/evaluation.json", spec)
                execution = load(folder/"native/execution.json")
                for record in execution["artifacts"]:
                    raw = (folder/"native"/record["path"]).read_bytes()
                    record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                save(folder/"native/execution.json", resign(execution));refresh_manifest(folder)
                with self.assertRaisesRegex(EvidenceError, "pipeline_evaluation_design_changed"):
                    audit_run_manifest(folder/"run-manifest.json")

    def test_rehashed_extra_loaded_mapping_requires_real_schema(self):
        for case in self.cases:
            with tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)/"run";shutil.copytree(self.root/(case+"-evaluate"), folder)
                loaded = json.loads((folder/"process/loaded-files.json").read_bytes())
                loaded.append({"path": "/invented/plugin.so", "size": -1, "sha256": "g"*64})
                save(folder/"process/loaded-files.json", loaded);refresh_manifest(folder)
                with self.assertRaisesRegex(EvidenceError, "pipeline_loaded_files_schema_changed"):
                    audit_run_manifest(folder/"run-manifest.json")

    def test_rehashed_wrong_native_operation_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)/"run";shutil.copytree(self.root/"Classic-N0-export", folder)
            request = load(folder/"process/request.json");request["arguments"][2] = "--timelearner-evaluate"
            save(folder/"process/request.json", request);refresh_manifest(folder)
            with self.assertRaisesRegex(EvidenceError, "pipeline_process_arguments_changed"):
                audit_run_manifest(folder/"run-manifest.json")

    def test_actual_evaluation_tick_budget_preserves_full_expected_matrix(self):
        output = os.environ.get("TIMELEARNER_PIPELINE_CONTROL_OUTPUT")
        if not output:
            self.skipTest("requires a new persistent native controls directory")
        out = Path(output);out.mkdir(exist_ok=False)
        for case in ("Classic-N0", "Branch-N1"):
            original = self.root/(case+"-evaluate")
            runtime = load(original/"process/runtime.json")
            job = load(original/"input/job.json");job["maximum_model_ticks"] = 1;resign(job)
            path = out/(case+"-job.json");save(path, job)
            native = out/case
            with (out/(case+".log")).open("wb") as stream:
                result = subprocess.run([runtime["executable"]["path"], "--app-ini", runtime["app_ini"]["path"],
                    "--timelearner-evaluate", str(path), "--timelearner-output", str(native)],
                    cwd=Path(runtime["executable"]["path"]).parent, stdout=stream, stderr=subprocess.STDOUT, timeout=120)
            self.assertEqual(result.returncode, 2)
            manifest = load(original/"run-manifest.json")
            source = load_case(original/manifest["source_package_path"])
            audit = audit_execution("evaluate", native, job, source)
            self.assertTrue(audit["frozen_model_verified"]);self.assertIsNone(audit["metrics"])
            execution = load(native/"execution.json")
            self.assertEqual(execution["execution"], "model_tick_budget_exhausted")
            self.assertEqual(execution["model_ticks"], 1)
            self.assertEqual(len(load(native/"evaluation.json")["trials"]), len(job["trials"]))
