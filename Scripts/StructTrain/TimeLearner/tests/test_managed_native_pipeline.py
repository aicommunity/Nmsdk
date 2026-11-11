"""Real public cold Train/export/frozen Test under one managed-unit lease.

Historical jobs supply declarations only. Every exported state and evaluated
model comes from the new Train; a terminal boundary is not convergence.
"""
import contextlib
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import unittest

from ..__main__ import main
from ..contained_process import inspect as inspect_contained
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import load
from ..native_pipeline_worker import audit_run_manifest
from ..native_process_policy import policy_for_reservation
from ..resource_reservations import Reservations


def signed(value):
    value = deepcopy(value)
    value.pop("sha256", None)
    value["sha256"] = sha(value)
    return value


class ManagedNativePipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        declaration = os.environ.get("TIMELEARNER_MANAGED_NATIVE_PIPELINE")
        if not declaration:
            raise unittest.SkipTest("requires real Console runtime, controller and cold job declarations")
        cls.spec = load(Path(declaration))
        if set(cls.spec) != {"runtime", "templates", "positive_templates", "controller", "output"}:
            raise RuntimeError("incomplete managed pipeline declaration")
        cls.output = Path(cls.spec["output"])
        cls.output.mkdir(parents=True, exist_ok=False)
        cls.templates = Path(cls.spec["templates"])
        cls.positive_templates = Path(cls.spec["positive_templates"])

    def case(self, name, *, positive=False, preflight=False):
        root = self.output/name
        root.mkdir()
        capacity = {"slots": 1, "memory_bytes": 6*1024**3, "disk_bytes": 1024**3, "tasks": 512}
        demands = {"slots": 1, "memory_bytes": 4*1024**3+
                   getattr(self, 'controller_reserve_bytes', 256*1024**2),
                   "disk_bytes": 512*1024**2, "tasks": 256}
        registry = Reservations(root/"leases.sqlite3", capacity=capacity, managed_units=True)
        lease = registry.reserve("managed-cold-pipeline-"+name,
            [{"path": str(root/"runs"), "access": "write"}], demands=demands,
            controller_directory=self.spec["controller"], ttl_seconds=1800)
        policy = policy_for_reservation(registry, lease["token"], memory_bytes=4*1024**3, tasks=64)
        policy_path = root/"policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        records = []

        def invoke(mode, job, source=None):
            job = signed(job)
            path = root/(mode+"-job.json")
            path.write_text(json.dumps(job, allow_nan=False), encoding="utf-8")
            output = root/"runs"/mode
            arguments = [mode, str(path), "--runtime-manifest", self.spec["runtime"],
                "--wall-seconds", "600", "--process-policy", str(policy_path), "--output", str(output)]
            if source is not None:
                arguments += ["--source-solo", str(source)]
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
                code = main(arguments)
            (root/(mode+"-cli.log")).write_text(stdout.getvalue(), encoding="utf-8")
            self.assertEqual(code, 0, stdout.getvalue())
            manifest = load(output/"run-manifest.json")
            self.assertEqual(manifest["schema_version"], 4)
            self.assertEqual((manifest["execution"], manifest["validity"]), ("completed", "valid"))
            self.assertTrue(audit_run_manifest(output/"run-manifest.json")["run_evidence_consistent"])
            self.assertTrue(inspect_contained(output/"process/contained")["all_processes_closed"])
            context = load(output/"process/reservation-context.json")
            binding = load(output/"process/contained/owned-unit.json")
            self.assertEqual(context["lease"]["token"], lease["token"])
            self.assertEqual(context["intent"]["intent"]["unit"], binding["unit"])
            self.assertEqual(registry.inspect()["leases"][0]["state"], "held")
            self.assertIsNone(manifest["evaluation_verdict"])
            records.append({"operation": mode, "unit": binding["unit"],
                            "job_sha256": job["sha256"], "manifest_sha256": manifest["sha256"]})
            return output

        templates = self.positive_templates if positive else self.templates
        job = load(templates/(name+"-train/input/job.json"))
        self.assertEqual(job["schema_version"], 1)
        job["configuration"]["run_id"] += "/managed-cold-pipeline"
        if preflight:
            invoke("preflight", job)
        trained = invoke("train", job)
        execution = load(trained/"native/execution.json")
        if not positive:
            # These older declarations have a real, retained negative outcome
            # under this runtime. They are never reused as positive seeds.
            self.assertFalse(execution["completed_boundary"])
            self.assertEqual(execution["training_outcome"], "budget_exhausted")
            self.assertFalse((trained/"native/train_learned_state.json").exists())
            stopped = trained/"native/train_stopped_state.json"
            self.assertTrue(stopped.is_file())
            forbidden = root/"runs/forbidden-export"
            export = load(templates/(name+"-export/input/job.json"))
            export["source_solo"] = load(stopped)
            path = root/"forbidden-export.json"
            path.write_text(json.dumps(signed(export)), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
                code = main(["export", str(path), "--source-solo", str(stopped),
                    "--runtime-manifest", self.spec["runtime"], "--wall-seconds", "600",
                    "--process-policy", str(policy_path), "--output", str(forbidden)])
            (root/"forbidden-export-cli.log").write_text(stdout.getvalue(), encoding="utf-8")
            self.assertEqual(code, 2)
            self.assertFalse(forbidden.exists())
            registry.release(lease["token"], note="Actual stopped Train closed; completed export refused before output or model process.")
            self.assertEqual(registry.inspect()["leases"][0]["state"], "released")
            (root/"result.json").write_text(json.dumps({"phases": records,
                "training_outcome": execution["training_outcome"], "completed_export_refused": True,
                "scientific_verdict": None}), encoding="utf-8")
            return
        self.assertTrue(execution["completed_boundary"])
        self.assertEqual(execution["training_outcome"], "exact")
        solo_path = trained/"native/train_learned_state.json"
        solo = load(solo_path)
        if job["configuration"]["schema_version"] in (6, 7, 8):
            # Composite cold6/cold7/cold8 preserve the complete initial declaration.
            # Scalar service configurations use a separate session identity.
            self.assertEqual(solo["configuration"], job["configuration"])
        else:
            self.assertEqual(solo["configuration"]["run_id"], job["configuration"]["run_id"]+"/session/1")
        export = load(templates/(name+"-export/input/job.json"))
        export["source_solo"] = solo
        exported = invoke("export", export, solo_path)
        recognition = load(exported/"native/model.json")
        self.assertEqual(recognition["source_solo"], solo)
        evaluation = load(templates/(name+"-frozen/input/job.json"))
        evaluation["source_recognition"] = recognition
        evaluation["run_id"] += "/managed-frozen"
        for i, trial in enumerate(evaluation["trials"]):
            trial["run_id"] = evaluation["run_id"]
            trial["trial_id"] = evaluation["run_id"]+"/"+str(i)
        evaluated = invoke("evaluate", evaluation, solo_path)
        self.assertEqual(load(evaluated/"native/model.json"), recognition)
        self.assertEqual(load(evaluated/"native/model-after.json"), recognition)
        actual = load(evaluated/"native/execution.json")
        self.assertEqual(actual["observed_trials"], actual["expected_trials"])
        self.assertEqual(actual["observed_trials"], len(evaluation["trials"]))
        self.assertEqual(len({r["unit"] for r in records}), 4 if preflight else 3)
        registry.release(lease["token"], note="Three real public native phases closed; full-model frozen identity audited.")
        self.assertEqual(registry.inspect()["leases"][0]["state"], "released")
        (root/"result.json").write_text(json.dumps({"phases": records,
            "training_outcome": execution["training_outcome"], "solo_sha256": solo["sha256"],
            "recognition_sha256": recognition["sha256"], "scientific_verdict": None,
            "independent_partition_verified": False}, indent=2), encoding="utf-8")

    def test_previous_classic_n0_stopped_train_cannot_export(self):
        self.case("Classic-N0")

    def test_previous_classic_n1_stopped_train_cannot_export(self):
        self.case("Classic-N1")

    def test_previous_branch_n0_stopped_train_cannot_export(self):
        self.case("Branch-N0")

    def test_previous_branch_n1_stopped_train_cannot_export(self):
        self.case("Branch-N1")

    def test_classic_n1_modelspec1_exact_train_export_frozen_evaluation(self):
        self.case("Classic-v1", positive=True)

    def test_classic_n1_modelspec2_exact_train_export_frozen_evaluation(self):
        self.case("Classic-v2", positive=True)

    def test_branch_n1_modelspec1_exact_train_export_frozen_evaluation(self):
        self.case("Branch-v1", positive=True)

    def test_branch_n1_modelspec2_exact_train_export_frozen_evaluation(self):
        self.case("Branch-v2", positive=True)
