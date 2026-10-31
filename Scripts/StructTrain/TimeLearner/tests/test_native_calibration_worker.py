"""Actual Console calibration jobs, CLI ownership and adversarial artifact changes."""
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_calibration_worker import audit_execution, audit_run_manifest, run_job, validate_job
from ..native_evidence import EvidenceError, load


def save(path, value):
    path.write_text(json.dumps(value, allow_nan=False)+"\n", encoding="utf-8")


def resign(value):
    value.pop("sha256", None);value["sha256"] = sha(value)
    return value


def refresh_execution(directory, **changes):
    record = load(directory/"execution.json")
    record.update(changes)
    for artifact in record["artifacts"]:
        raw = (directory/artifact["path"]).read_bytes()
        artifact["sha256"], artifact["bytes"] = hashlib.sha256(raw).hexdigest(), len(raw)
    save(directory/"execution.json", resign(record))


class NativeCalibrationWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_CALIBRATION_WORKER_DIR")
        source = os.environ.get("TIMELEARNER_CALIBRATION_OWNERSHIP_SOURCE")
        if not directory or not source:
            raise unittest.SkipTest("requires six completed production Console jobs and their primary source")
        cls.root = Path(directory)
        cls.sources = {load(p)["sha256"]: p for p in Path(source).glob("*_learned_state.json")}
        cls.cases = []
        for top in ("Classic", "Branch"):
            for case in ("success", "nonseparable", "budget"):
                job = load(cls.root/(top+"-"+case+"-job.json"))
                source_path = cls.sources[job["source_recognition"]["source_solo"]["sha256"]]
                cls.cases.append((top, case, job, source_path, cls.root/(top+"-"+case)))

    def test_all_six_actual_jobs_bind_full_grid_model_and_primaries(self):
        for _, case, job, source, output in self.cases:
            validate_job(job, load_case(source))
            audit = audit_execution(output, job, load_case(source))
            self.assertTrue(audit["execution_evidence_consistent"])
            self.assertEqual(audit["full_grid_model_binding_verified"], case == "success")
            self.assertFalse(audit["native_execution_verified"])
            self.assertIsNone(audit["evaluation_verdict"])

    def test_rehashed_source_model_cannot_replace_committed_model(self):
        for _, case, job, source, output in self.cases:
            if case != "success":
                continue
            with tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)/"native";shutil.copytree(output, folder)
                replaced = job["source_recognition"]
                save(folder/"model.json", replaced)
                refresh_execution(folder, model_sha256=replaced["sha256"], model_revision=replaced["model_revision"])
                with self.assertRaisesRegex(EvidenceError, "worker_committed_model_changed"):
                    audit_execution(folder, job, load_case(source))

    def test_rehashed_incomplete_grid_cannot_keep_positive_manifest(self):
        for _, case, job, source, output in self.cases:
            if case != "success":
                continue
            with tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)/"native";shutil.copytree(output, folder)
                report = load(folder/"transaction.json");report["candidates"].pop()
                resign(report);save(folder/"transaction.json", report)
                refresh_execution(folder, transaction_sha256=report["sha256"])
                with self.assertRaises(EvidenceError):
                    audit_execution(folder, job, load_case(source))

    def test_original_declared_grid_is_checked_independently_of_result(self):
        for _, case, job, source, output in self.cases:
            if case != "success":
                continue
            with tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)/"native";shutil.copytree(output, folder)
                changed = copy.deepcopy(job);changed["thresholds"][0] = .999
                resign(changed);save(folder/"job.json", changed)
                refresh_execution(folder, job_sha256=changed["sha256"])
                with self.assertRaisesRegex(EvidenceError, "worker_declared_design_changed"):
                    audit_execution(folder, changed, load_case(source))

    def test_invalid_job_is_rejected_before_output_or_runtime_resolution(self):
        _, _, job, source, _ = self.cases[0]
        for key, value in (("frequency_hz", True), ("maximum_model_ticks", 0), ("owner_class", "NNeuronTimeLearnerBranch"),
                           ("source_recognition", []), ("trials", {}), ("specification", [])):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory);bad = copy.deepcopy(job);bad[key] = value;resign(bad)
                save(root/"job.json", bad)
                with self.assertRaises(EvidenceError):
                    run_job(root/"job.json", source, root/"missing-runtime.json", root/"output", 300)
                self.assertFalse((root/"output").exists())

    def test_public_cli_runs_both_topologies_with_owned_runtime_and_primary_snapshot(self):
        from ..__main__ import main
        for top, case, job, source, _ in self.cases:
            if case != "success":
                continue
            with tempfile.TemporaryDirectory() as directory:
                saved = os.environ.get("TIMELEARNER_NATIVE_CALIBRATION_CLI_OUTPUT")
                output = Path(saved)/top if saved else Path(directory)/"attempt"
                if saved:
                    output.parent.mkdir(parents=True, exist_ok=True)
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    status = main(["calibrate", "run", str(self.root/(top+"-"+case+"-job.json")),
                        "--source-solo", str(source), "--runtime-manifest", str(self.root/"runtime-before.json"),
                        "--wall-seconds", "300", "--output", str(output)])
                self.assertEqual(status, 0, stdout.getvalue())
                result = load(output/"run-manifest.json")
                self.assertEqual(result["validity"], "valid")
                self.assertTrue(result["analysis"]["full_grid_model_binding_verified"])
                self.assertFalse(result["independent_partition_verified"])
                self.assertIsNone(result["evaluation_verdict"])
                self.assertTrue(audit_run_manifest(output/"run-manifest.json")["full_grid_model_binding_verified"])
                report_stdout = io.StringIO()
                with contextlib.redirect_stdout(report_stdout):
                    report_status = main(["analyze", str(output/"run-manifest.json"), "--format", "calibration-run"])
                self.assertEqual(report_status, 0, report_stdout.getvalue())
                self.assertTrue(json.loads(report_stdout.getvalue())["analysis"]["run_evidence_consistent"])
                original = (output/"run-manifest.json").read_bytes()
                try:
                    forged = copy.deepcopy(result);forged["runtime_fingerprint"] = "0"*64
                    save(output/"run-manifest.json", resign(forged))
                    with self.assertRaisesRegex(EvidenceError, "worker_run_runtime_scope_changed"):
                        audit_run_manifest(output/"run-manifest.json")
                finally:
                    (output/"run-manifest.json").write_bytes(original)
                self.assertEqual(load(output/"process/owned-process.json")["executable"],
                                 load(self.root/"runtime-before.json")["executable"]["path"])
                snapshot = output/"input/source"/source.name
                self.assertEqual(load(snapshot), job["source_recognition"]["source_solo"])
                self.assertEqual(len(result["artifacts"]), len([p for p in output.rglob("*") if p.is_file()])-1)

    def test_model_tick_budget_is_a_diagnostic_stop_with_source_restored(self):
        for top, case, job, source, _ in self.cases:
            if case != "success":
                continue
            with tempfile.TemporaryDirectory() as directory:
                saved = os.environ.get("TIMELEARNER_NATIVE_CALIBRATION_CLI_OUTPUT")
                root = Path(saved)/(top+"-tick-control") if saved else Path(directory)
                root.mkdir(parents=True, exist_ok=True)
                changed = copy.deepcopy(job);changed["maximum_model_ticks"] = 1;resign(changed)
                save(root/"job.json", changed)
                output = root/"attempt"
                result = run_job(root/"job.json", source, self.root/"runtime-before.json", output, 300)
                self.assertEqual(result["execution"], "process_error")
                self.assertEqual(result["validity"], "unverified_execution")
                native = load(output/"native/execution.json")
                self.assertEqual(native["execution"], "model_tick_budget_exhausted")
                self.assertEqual(native["model_ticks"], 1)
                self.assertEqual(native["calibration_status"], "cancelled")
                self.assertEqual(load(output/"native/model.json"), job["source_recognition"])
                diagnostic = audit_execution(output/"native", changed, load_case(source))
                self.assertFalse(diagnostic["full_grid_model_binding_verified"])
                self.assertFalse(audit_run_manifest(output/"run-manifest.json")["full_grid_model_binding_verified"])

    def test_native_console_strict_parser_and_mode_conflicts_leave_no_output(self):
        _, _, job, _, _ = self.cases[0]
        runtime = load(self.root/"runtime-before.json")
        executable = runtime["executable"]["path"];ini = runtime["app_ini"]["path"]
        with tempfile.TemporaryDirectory() as directory:
            saved = os.environ.get("TIMELEARNER_NATIVE_CALIBRATION_CLI_OUTPUT")
            root = Path(saved)/"native-strict-controls" if saved else Path(directory)
            root.mkdir(parents=True, exist_ok=True)
            unknown = copy.deepcopy(job);unknown["trials"][0]["unused_parameter"] = 1;resign(unknown)
            bad_digest = copy.deepcopy(job);bad_digest["sha256"] = "0"*64
            raw = json.dumps(job)
            cases = [("duplicate", '{"maximum_model_ticks":'+str(job["maximum_model_ticks"])+','+raw[1:], [], "duplicate_native_configuration_key"),
                     ("request-field", json.dumps(unknown), [], "calibration_proof_request_encoding_mismatch"),
                     ("digest", json.dumps(bad_digest), [], "job_digest_mismatch"),
                     ("mode", raw, ["--config", "unused-project.ini"], "excludes project execution/inspection modes")]
            results = []
            for name, raw, extra, reason in cases:
                path = root/(name+".json");path.write_text(raw, encoding="utf-8")
                target = root/(name+"-output")
                done = subprocess.run([executable, "--app-ini", ini, "--timelearner-calibrate", str(path),
                    "--timelearner-output", str(target), *extra], cwd=Path(executable).parent,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
                (root/(name+".log")).write_bytes(done.stdout)
                self.assertEqual(done.returncode, 2, done.stdout.decode(errors="replace"))
                self.assertIn(reason, done.stdout.decode(errors="replace"))
                self.assertFalse(target.exists())
                results.append({"case": name, "returncode": done.returncode, "reason": reason, "output_created": False})
            save(root/"validation.json", {"native_rejection_controls": results, "evaluation_verdict": None})


class NativeCalibrationRunProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_CALIBRATION_RUN_DIR")
        if not directory:
            raise unittest.SkipTest("requires both saved owned production calibration runs")
        cls.paths = [Path(directory)/top/"run-manifest.json" for top in ("Classic", "Branch")]
        for path in cls.paths:
            if not path.is_file():
                raise RuntimeError("missing actual production run manifest")

    def test_actual_runs_bind_process_arguments_executable_and_primary_model(self):
        for path in self.paths:
            self.assertTrue(audit_run_manifest(path)["full_grid_model_binding_verified"])

    def changed(self, path, filename, mutate, reason):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/"attempt";shutil.copytree(path.parent, root)
            target = root/filename;value = json.loads(target.read_bytes());mutate(value);save(target, value)
            manifest = load(root/"run-manifest.json")
            record = next(r for r in manifest["artifacts"] if r["path"] == filename)
            raw = target.read_bytes();record["bytes"] = len(raw);record["sha256"] = hashlib.sha256(raw).hexdigest()
            save(root/"run-manifest.json", resign(manifest))
            with self.assertRaisesRegex(EvidenceError, reason):
                audit_run_manifest(root/"run-manifest.json")

    def test_rehashed_unrelated_process_arguments_are_rejected(self):
        for path in self.paths:
            self.changed(path, "process/request.json", lambda value: value["arguments"].__setitem__(3, "/unrelated/job.json"),
                         "worker_run_process_scope_changed")

    def test_rehashed_owned_executable_replacement_is_rejected(self):
        for path in self.paths:
            self.changed(path, "process/owned-process.json", lambda value: value.update(executable="/unrelated/console"),
                         "worker_run_owned_runtime_changed")

    def test_rehashed_missing_executable_mapping_is_rejected(self):
        for path in self.paths:
            self.changed(path, "process/loaded-files.json", lambda value: value.clear(), "worker_run_owned_runtime_changed")
