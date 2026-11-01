"""Acceptance of real Console dimension controls and original final-gate data."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..native_pipeline_worker import audit_execution, audit_run_manifest
from .native_dimension_corpus import make_dimension_job


class NativeDimensionWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_DIMENSION_CORPUS")
        if not directory:
            raise unittest.SkipTest("requires actual native dimension runs")
        cls.root = Path(directory)
        cls.index = load(cls.root/"index.json")

    def test_complete_declared_case_set_and_native_artifact_closure(self):
        expected = {(n, top, norm) for n in self.index["dimensions"]
                    for top in ("Classic", "Branch") for norm in ("N0", "N1")}
        rows = self.index["records"]
        self.assertEqual(len(rows), len(expected))
        self.assertEqual({(r["inputs"], r["topology"], r["normalization"]) for r in rows}, expected)
        for row in rows:
            with self.subTest(run=row["name"]):
                folder = self.root/"runs"/row["name"]
                job = load(folder/"input/job.json")
                self.assertEqual(job, load(self.root/"jobs"/(row["name"]+".json")))
                self.assertTrue(audit_run_manifest(folder/"run-manifest.json")["run_evidence_consistent"])
                self.assertEqual(audit_execution("train", folder/"native", job), row["execution_audit"])

    def test_fresh_final_probes_cover_every_input_without_reusing_references(self):
        for row in self.index["records"]:
            with self.subTest(run=row["name"]):
                folder = self.root/"runs"/row["name"]/"native"
                summary = load(folder/"train_learned_summary.json")
                certificate = summary["certificate"]
                residuals = certificate["residuals"]
                n = row["inputs"]
                self.assertEqual({r["input_id"] for r in residuals}, {"input"+str(i) for i in range(n)})
                self.assertEqual(len(residuals), n)
                trials = {r["trial_id"] for r in residuals}
                self.assertEqual(len(trials), n)
                self.assertTrue(all("/verify/" in t for t in trials))
                self.assertEqual(row["certificate"], certificate)
                self.assertEqual(row["actual_parameters"], summary["actual_parameters"])
                self.assertTrue(all(p["length"] == p["synapses"] == 1 for p in row["actual_parameters"]))
                if n == 1:
                    self.assertTrue(certificate["exact"])
                    self.assertEqual(row["outcome"], "exact")
                else:
                    self.assertFalse(certificate["exact"])
                    self.assertEqual(row["outcome"], "search_unresolved")
                    self.assertTrue(any(not r["within_timing"] for r in residuals[:-1]))

    def test_dimension_preparation_preserves_profiles_and_original_tolerances(self):
        for row in self.index["records"]:
            template = load(self.root/"runs"/row["name"]/"input/job.json")
            before = deepcopy(template)
            job = make_dimension_job(template, row["topology"], row["normalization"], row["inputs"])
            self.assertEqual(job, template)
            self.assertEqual(before, template)
            self.assertEqual(job["configuration"]["search"]["tolerances"],
                             {"amplitude_absolute": 1e-5, "amplitude_relative": 0, "sync": .02})
            self.assertIsNone(self.index["scientific_classification_verdict"])


if __name__ == "__main__":
    unittest.main()
