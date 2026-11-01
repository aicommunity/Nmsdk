"""Actual physical N1 A/B: unchanged declarations and fresh exact certificates."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..native_pipeline_worker import audit_execution, audit_run_manifest


class NativeN1RefinedWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        required = ("TIMELEARNER_NATIVE_N1_BASELINE", "TIMELEARNER_NATIVE_N1_REFINED")
        if not all(os.environ.get(k) for k in required):
            raise unittest.SkipTest("requires both original and refined real physical runs")
        cls.baseline = Path(os.environ[required[0]])
        cls.root = Path(os.environ[required[1]])
        cls.index = load(cls.root/"index.json")

    def test_identical_jobs_profiles_and_cold_models_with_distinct_verified_runtimes(self):
        rows = self.index["records"]
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["name"] for r in rows},
                         {"native-n1-mesh-"+t+"-isi030" for t in ("Classic", "Branch")})
        for row in rows:
            name = row["name"]
            with self.subTest(run=name):
                folder, previous = self.root/name, self.baseline/name
                job = load(folder/"input/job.json")
                self.assertEqual(job, load(previous/"input/job.json"))
                self.assertEqual(job, load(self.root/(name+".json")))
                self.assertEqual(job["configuration"]["search"]["tolerances"],
                                 {"amplitude_absolute": 1e-5, "amplitude_relative": 0, "sync": .02})
                before = load(previous/"native/initial-state.json")
                current = load(folder/"native/initial-state.json")
                self.assertEqual(current["identity"], before["identity"])
                self.assertEqual(current["parameters"], before["parameters"])
                self.assertTrue(audit_run_manifest(folder/"run-manifest.json")["run_evidence_consistent"])
                runtime = load(folder/"run-manifest.json")
                original_runtime = load(previous/"run-manifest.json")
                self.assertNotEqual(runtime["runtime_fingerprint"], original_runtime["runtime_fingerprint"])
                pulse = "Libraries/Nmsdk-PulseLib"
                self.assertNotEqual(runtime["source_closure"][pulse]["head"],
                                    original_runtime["source_closure"][pulse]["head"])
                for dependency in set(runtime["source_closure"])-{"root", pulse}:
                    self.assertEqual(runtime["source_closure"][dependency]["head"],
                                     original_runtime["source_closure"][dependency]["head"])
                self.assertEqual(audit_execution("train", folder/"native", job), row["execution_audit"])

    def test_actual_nonseed_resistance_change_passes_the_original_fresh_all_input_gate(self):
        for row in self.index["records"]:
            name = row["name"]
            with self.subTest(run=name):
                previous = load(self.baseline/name/"native/train_learned_summary.json")
                current = load(self.root/name/"native/train_learned_summary.json")
                package = load(self.root/name/"native/train_learned_state.json")
                self.assertEqual(row["candidates"], current["candidates"])
                self.assertEqual(row["certificate"], current["certificate"])
                self.assertFalse(previous["certificate"]["exact"])
                self.assertTrue(current["certificate"]["exact"])
                self.assertEqual(row["execution_audit"]["training_outcome"], "exact")
                self.assertEqual(package["training_outcome"], "exact")
                residuals = {r["input_id"]: r for r in current["certificate"]["residuals"]}
                original = {r["input_id"]: r for r in previous["certificate"]["residuals"]}
                self.assertEqual(set(residuals), {"input0", "input1"})
                self.assertEqual(len({r["trial_id"] for r in residuals.values()}), 2)
                for key, value in residuals.items():
                    self.assertEqual(value["target_raw_potential"], original[key]["target_raw_potential"])
                    self.assertTrue(value["within_amplitude"] and value["within_timing"])
                    self.assertLessEqual(abs(value["amplitude_residual"]), 1e-5)
                    self.assertLessEqual(max(abs(value["timing_low"]), abs(value["timing_high"])), .02)
                    self.assertIn("/verify/", value["trial_id"])
                initial = load(self.root/name/"native/initial-state.json")
                self.assertNotEqual(current["actual_model_revision"], initial["identity"]["sha256"])
                self.assertEqual(current["actual_parameters"][-1], initial["parameters"][-1])
                final = current["actual_parameters"][0]
                seed = {(c["parameters"]["length"], c["parameters"]["resistance"])
                        for c in previous["candidates"]}
                self.assertNotIn((final["length"], final["resistance"]), seed)
                self.assertTrue(all(p["synapses"] == 1 for p in current["actual_parameters"]))
                self.assertIsNone(row["scientific_verdict"])
                self.assertIsNone(self.index["scientific_verdict"])


if __name__ == "__main__":
    unittest.main()
