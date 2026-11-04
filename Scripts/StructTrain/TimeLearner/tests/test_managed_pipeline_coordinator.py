"""Actual public coordinator: cold Train, boundary continuation and native phases."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import unittest

from . import test_managed_native_pipeline as fixtures
from ..__main__ import main
from ..contained_process import inspect as inspect_contained
from ..managed_pipeline import audit_pipeline
from ..native_evidence import load
from ..native_process_policy import policy_for_reservation
from ..resource_reservations import Reservations


class ManagedPipelineCoordinatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.ManagedNativePipelineTest.setUpClass.__func__(cls)
        calibration = os.environ.get("TIMELEARNER_COORDINATOR_CALIBRATION_TEMPLATES")
        if not calibration:
            raise unittest.SkipTest("requires archived calibration job declarations only")
        cls.calibration_templates = Path(calibration)

    def case(self, name, *, positive):
        root = self.output/name
        root.mkdir()
        templates = self.positive_templates if positive else self.templates
        train = load(templates/(name+"-train/input/job.json"))
        train["configuration"]["run_id"] += "/managed-coordinator"
        train = fixtures.signed(train)
        export = load(templates/(name+"-export/input/job.json"))
        export.pop("sha256")
        export["source_solo"] = None
        evaluation_name = name if positive else ("Branch-v1" if name.startswith("Branch") else "Classic-v1")
        evaluation = load(self.positive_templates/(evaluation_name+"-frozen/input/job.json"))
        evaluation.pop("sha256")
        evaluation["source_recognition"] = None
        evaluation["implementation_id"] = train["implementation_id"]
        evaluation["run_id"] += "/managed-coordinator-frozen"
        for i, trial in enumerate(evaluation["trials"]):
            trial["run_id"] = evaluation["run_id"]
            trial["trial_id"] = evaluation["run_id"]+"/"+str(i)
        phases = [{"operation": "train", "job": train, "wall_seconds": 600},
                  {"operation": "export", "job": export, "wall_seconds": 600}]
        if positive:
            # Parameters from a historical measured grid, never its saved model
            # or verdict. Every candidate and confirmation runs on the new Train.
            calibration = load(self.calibration_templates/name/"measured-grid-job.json")
            calibration.pop("sha256")
            calibration["source_recognition"] = None
            calibration["specification"]["attempt_id"] += "/managed-coordinator"
            phases.append({"operation": "calibrate", "job": calibration, "wall_seconds": 600})
        phases.append({"operation": "evaluate", "job": evaluation, "wall_seconds": 600})
        declaration = root/"pipeline-job.json"
        declaration.write_text(json.dumps({"kind": "timelearner_managed_pipeline_job", "schema_version": 1,
            "attempt_id": name+"/managed-coordinator", "phases": phases}, allow_nan=False))
        registry = Reservations(root/"leases.sqlite3", managed_units=True,
            capacity={"slots": 1, "memory_bytes": 6*1024**3, "disk_bytes": 1024**3, "tasks": 512})
        lease = registry.reserve("managed-coordinator-"+name,
            [{"path": str(root/"runs"), "access": "write"}],
            demands={"slots": 1, "memory_bytes": 4*1024**3+512*1024**2,
                     "disk_bytes": 512*1024**2, "tasks": 256},
            controller_directory=self.spec["controller"], ttl_seconds=1800)
        policy_path = root/"policy.json"
        policy_path.write_text(json.dumps(policy_for_reservation(registry, lease["token"],
                                                               memory_bytes=4*1024**3, tasks=64)))
        output = root/"runs/pipeline"

        def invoke(action, *, stop_after=None, expected=0):
            args = ["pipeline", action, str(output), "--specification", str(declaration),
                    "--runtime-manifest", self.spec["runtime"], "--process-policy", str(policy_path)]
            if stop_after:
                args += ["--stop-after", stop_after]
            text = io.StringIO()
            with contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
                code = main(args)
            (root/(action+("-"+stop_after if stop_after else "")+"-cli.log")).write_text(text.getvalue())
            self.assertEqual(code, expected, text.getvalue())
            return audit_pipeline(output)

        paused = invoke("run", stop_after="train", expected=0 if positive else 2)
        self.assertFalse(paused["pipeline_complete"])
        self.assertIsNone(paused["pending_phase"])
        if not positive:
            self.assertEqual(paused["halted_phase"], "train")
            self.assertFalse((output/"phases/export").exists())
            self.assertFalse((output/"phases/evaluate").exists())
            self.assertIsNone(paused["evaluation"])
        else:
            self.assertEqual(paused["completed_phases"], ["train"])
            package = output/"phases/train/native/train_learned_state.json"
            before = hashlib.sha256(package.read_bytes()).hexdigest()
            complete = invoke("continue")
            self.assertTrue(complete["pipeline_complete"])
            self.assertEqual(complete["completed_phases"], [p["operation"] for p in phases])
            self.assertEqual(hashlib.sha256(package.read_bytes()).hexdigest(), before)
            self.assertEqual({k: complete["evaluation"]["pooled_counts"][k] for k in ("TP", "FP", "FN", "TN")},
                             {"TP": 2, "FP": 0, "FN": 0, "TN": 2})
        units = {}
        for phase in (output/"phases").iterdir():
            contained = phase/"process/contained"
            self.assertTrue(inspect_contained(contained)["all_processes_closed"])
            context = load(phase/"process/reservation-context.json")
            binding = load(contained/"owned-unit.json")
            self.assertEqual(context["lease"]["token"], lease["token"])
            self.assertEqual(context["intent"]["intent"]["unit"], binding["unit"])
            units[phase.name] = binding["unit"]
        self.assertEqual(len(units), 4 if positive else 1)
        self.assertEqual(len(set(units.values())), len(units))
        if positive:
            # A completed continuation is read-only with respect to native work.
            self.assertEqual(invoke("continue"), complete)
            self.assertEqual(units, {p.name: load(p/"process/contained/owned-unit.json")["unit"]
                                     for p in (output/"phases").iterdir()})
        registry.release(lease["token"], note="All actual coordinator native groups freshly closed; no phase rerun on continuation.")
        self.assertEqual(registry.inspect()["leases"][0]["state"], "released")
        (root/"result.json").write_text(json.dumps({"units": units, "positive_source_declaration": positive,
            "final_audit": audit_pipeline(output), "scientific_verdict": None}, indent=2))

    def test_classic_modelspec1_cold_boundary_continue_calibrate_frozen(self):
        self.case("Classic-v1", positive=True)

    def test_classic_modelspec2_cold_boundary_continue_calibrate_frozen(self):
        self.case("Classic-v2", positive=True)

    def test_branch_modelspec1_cold_boundary_continue_calibrate_frozen(self):
        self.case("Branch-v1", positive=True)

    def test_branch_modelspec2_cold_boundary_continue_calibrate_frozen(self):
        self.case("Branch-v2", positive=True)

    def test_classic_n0_stopped_has_no_export_or_test(self):
        self.case("Classic-N0", positive=False)

    def test_classic_n1_stopped_has_no_export_or_test(self):
        self.case("Classic-N1", positive=False)

    def test_branch_n0_stopped_has_no_export_or_test(self):
        self.case("Branch-N0", positive=False)

    def test_branch_n1_stopped_has_no_export_or_test(self):
        self.case("Branch-N1", positive=False)
