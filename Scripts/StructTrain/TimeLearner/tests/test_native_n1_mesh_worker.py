"""Actual finite-mesh baseline before measured-resistance refinement."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..native_pipeline_worker import audit_execution, audit_run_manifest


class NativeN1MeshWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_N1_MESH_CORPUS")
        if not directory:
            raise unittest.SkipTest("requires actual unrefined N1 physical baseline")
        cls.root = Path(directory)
        cls.index = load(cls.root/"index.json")

    def test_original_native_training_and_declared_individual_domains(self):
        rows = self.index["records"]
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["name"] for r in rows},
                         {"native-n1-mesh-"+t+"-isi030" for t in ("Classic", "Branch")})
        for row in rows:
            with self.subTest(run=row["name"]):
                folder = self.root/row["name"]
                job = load(folder/"input/job.json")
                self.assertEqual(job, load(self.root/(row["name"]+".json")))
                self.assertTrue(audit_run_manifest(folder/"run-manifest.json")["run_evidence_consistent"])
                self.assertEqual(audit_execution("train", folder/"native", job), row["execution_audit"])
                self.assertTrue(row["execution_audit"]["completed_boundary"])
                self.assertEqual(job["configuration"]["model"]["normalization"], "N1")
                self.assertEqual(job["configuration"]["search"]["resistance_subdivision_depth"], 4)
                self.assertTrue(row["resistance_domains"])
                for candidate in row["candidates"]:
                    self.assertTrue(all(p["synapses"] == 1 for p in candidate["full_parameters"]))
                    self.assertEqual(candidate["full_parameters"][-1],
                                     {"length": 1, "synapses": 1, "resistance": 86000000})
                    self.assertGreaterEqual(candidate["parameters"]["resistance"], 43000000)
                    self.assertLessEqual(candidate["parameters"]["resistance"], 86000000)

    def test_timing_ready_measured_bracket_is_missed_by_the_declared_seed_mesh(self):
        for row in self.index["records"]:
            with self.subTest(run=row["name"]):
                summary = load(self.root/row["name"]/"native/train_learned_summary.json")
                self.assertEqual(row["candidates"], summary["candidates"])
                self.assertEqual(row["certificate"], summary["certificate"])
                self.assertEqual(row["execution_audit"]["training_outcome"], "search_unresolved")
                self.assertFalse(row["certificate"]["exact"])
                timing_ready = [c for c in row["candidates"] if c["within_timing"]]
                self.assertTrue(timing_ready)
                self.assertGreater(min(abs(c["amplitude_residual"]) for c in timing_ready), 1e-5)
                points = {c["parameters"]["resistance"]: c["amplitude_residual"]
                          for c in timing_ready if c["parameters"]["length"] == 2}
                ordered = sorted(points.items())
                self.assertGreaterEqual(len(ordered), 3)
                self.assertTrue(all(a[1] >= b[1] for a, b in zip(ordered, ordered[1:])))
                self.assertTrue(any(a[1] > 1e-5 and b[1] < -1e-5
                                    for a, b in zip(ordered, ordered[1:])))
                self.assertIsNone(row["scientific_verdict"])


if __name__ == "__main__":
    unittest.main()
