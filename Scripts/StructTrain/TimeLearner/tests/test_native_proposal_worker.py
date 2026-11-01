"""Physical positive control of the N0 proposal path, not classification."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..native_pipeline_worker import audit_execution, audit_run_manifest


class NativeProposalWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_PROPOSAL_CORPUS")
        if not directory:
            raise unittest.SkipTest("requires original physical N0 proposal controls")
        cls.root = Path(directory)
        cls.index = load(cls.root/"index.json")

    def test_both_topologies_use_actual_complete_native_training_evidence(self):
        rows = self.index["records"]
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["name"] for r in rows},
                         {"native-priority-"+t+"-isi030" for t in ("Classic", "Branch")})
        for row in rows:
            folder = self.root/row["name"]
            job = load(folder/"input/job.json")
            self.assertEqual(job, load(self.root/(row["name"]+".json")))
            self.assertTrue(audit_run_manifest(folder/"run-manifest.json")["run_evidence_consistent"])
            self.assertEqual(audit_execution("train", folder/"native", job), row["execution_audit"])
            self.assertTrue(row["execution_audit"]["completed_boundary"])

    def test_measured_timing_ready_length_gets_neighbor_ns_before_next_length(self):
        for row in self.index["records"]:
            with self.subTest(run=row["name"]):
                folder = self.root/row["name"]/"native"
                summary = load(folder/"train_learned_summary.json")
                self.assertEqual(row["candidates"], summary["candidates"])
                candidates = summary["candidates"]
                self.assertGreaterEqual(len(candidates), 4)
                self.assertEqual([(c["parameters"]["length"], c["parameters"]["synapses"])
                                  for c in candidates[:4]], [(1, 1), (2, 1), (2, 2), (3, 1)])
                self.assertFalse(candidates[0]["within_timing"])
                self.assertTrue(candidates[1]["within_timing"])
                self.assertFalse(candidates[1]["within_amplitude"])
                self.assertNotEqual(candidates[1]["trial_id"], candidates[2]["trial_id"])
                self.assertTrue(row["physical_priority_path_exercised"])
                self.assertTrue(all(c["parameters"]["resistance"] == 86000000 for c in candidates))
                self.assertEqual(row["certificate"], summary["certificate"])
                self.assertFalse(row["certificate"]["exact"])
                self.assertEqual(row["execution_audit"]["training_outcome"], "search_unresolved")
                self.assertIsNone(row["scientific_verdict"])


if __name__ == "__main__":
    unittest.main()
