"""Real Console preflight receipts and rehashed corruptions of those receipts."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_execution, audit_run_manifest, validate_job
from ..native_calibration_worker import _signed


def save(path, value):
    path.write_text(json.dumps(value, allow_nan=False)+"\n", encoding="utf-8")


class NativePreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_PREFLIGHT_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual owned Console preflight runs")
        cls.root = Path(directory)
        cls.corpus = load(cls.root/"corpus.json")
        expected = {"pipeline-"+t+"-N"+n for t in ("Classic", "Branch") for n in ("0", "1")}
        expected |= {"live-"+t+"-"+m for t in ("Classic", "Branch")
                     for m in ("budget", "fixed", "grid", "legacy-budget", "stopped")}
        if set(cls.corpus["positive"]) != expected or len(cls.corpus["negative"]) != 6:
            raise AssertionError("incomplete preflight corpus")

    def test_all_fourteen_actual_preflight_runs(self):
        for name in self.corpus["positive"]:
            result = audit_run_manifest(self.root/"runs"/name/"run-manifest.json")
            self.assertTrue(result["run_evidence_consistent"])
            self.assertEqual(result["operation"], "preflight")
            self.assertFalse(result["native_execution_verified"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_real_preflight_has_no_training_artifacts_or_time_advance(self):
        for name in self.corpus["positive"]:
            run = self.root/"runs"/name
            execution = load(run/"native/execution.json")
            self.assertEqual(execution["model_ticks"], 0)
            self.assertEqual(execution["model_time_begin"], execution["model_time_end"])
            self.assertFalse(execution["training_started"])
            self.assertEqual(execution["controller_state"], "idle")
            self.assertEqual(set(p.name for p in (run/"native").iterdir()),
                             {"job.json", "initial-state.json", "execution.json"})

    def test_invalid_declarations_have_no_positive_native_preflight(self):
        for name, record in self.corpus["negative"].items():
            run = self.root/"runs"/name
            self.assertFalse((run/"native/execution.json").exists())
            if record["stage"] == "descriptor":
                self.assertFalse(run.exists())
                self.assertTrue(record["reason"])
            else:
                result = audit_run_manifest(run/"run-manifest.json")
                self.assertTrue(result["run_evidence_consistent"])
                manifest = load(run/"run-manifest.json")
                self.assertEqual(manifest["validity"], "unverified_execution")
                self.assertIsNone(manifest["analysis"])
                self.assertEqual(load(run/"process/result.json")["returncode"], 2)

    def corrupt_native(self, change, pattern):
        original = self.root/"runs"/"pipeline-Classic-N1"
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)/"native";shutil.copytree(original/"native", folder)
            execution = load(folder/"execution.json")
            change(folder, execution)
            save(folder/"execution.json", _signed({k: v for k, v in execution.items() if k != "sha256"}))
            with self.assertRaisesRegex(EvidenceError, pattern):
                audit_execution("preflight", folder, load(original/"input/job.json"))

    def test_rehashed_tick_is_rejected(self):
        self.corrupt_native(lambda _, e: e.update(model_ticks=1), "pipeline_clock_changed|preflight_started")

    def test_rehashed_training_or_observation_claim_is_rejected(self):
        for values in ({"training_started": True}, {"reference_probes": 1},
                       {"observed_probes": 1}, {"controller_state": "capturing_references"}):
            self.corrupt_native(lambda _, e: e.update(values), "preflight_started")

    def test_rehashed_unsafe_or_nonfinite_integration_is_rejected(self):
        for field, value in (("maximum_step_gain", 2.), ("maximum_step_gain", -1.),
                             ("maximum_conductance", -1.), ("maximum_step_gain", "NaN")):
            self.corrupt_native(lambda _, e: e["integration"]["channels"][0].update({field: value}),
                                "preflight_integration|not_a_number")

    def test_rehashed_extra_model_or_certificate_is_rejected(self):
        def change(folder, execution):
            import hashlib
            raw=b'{}\n';(folder/"certificate.json").write_bytes(raw)
            execution["artifacts"].append({"path": "certificate.json", "bytes": len(raw),
                                           "sha256": hashlib.sha256(raw).hexdigest()})
        self.corrupt_native(change, "preflight_started")

    def test_rehashed_changed_initial_parameter_is_rejected(self):
        def change(folder, execution):
            import hashlib
            initial = load(folder/"initial-state.json");initial["parameters"][0]["length"] += 1
            save(folder/"initial-state.json", _signed({k: v for k, v in initial.items() if k != "sha256"}))
            record = next(r for r in execution["artifacts"] if r["path"] == "initial-state.json")
            raw = (folder/record["path"]).read_bytes();record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        self.corrupt_native(change, "preflight_effective_parameters_changed")

    def test_preflight_reuses_the_train_descriptor_contract(self):
        for name in self.corpus["positive"]:
            job = load(self.root/"runs"/name/"input/job.json")
            self.assertEqual(validate_job("preflight", job), validate_job("train", job))
            bad = copy.deepcopy(job);bad["optional_modes"]["sync_capacitance_trim"] = 1
            bad = _signed({k: v for k, v in bad.items() if k != "sha256"})
            with self.assertRaisesRegex(EvidenceError, "training_optional_modes_not_yet_supported"):
                validate_job("preflight", bad)
