"""Real same-matrix grid provenance, observations and transactional result."""
import copy
import os
from pathlib import Path
import unittest

from ..calibration_transaction_evidence import audit_native_calibration_transaction
from ..learned_evidence import audit_learned_state, load_case
from ..native_calibration_worker import audit_run_manifest
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_evaluation
from .live_pipeline_corpus import signed


class NativeN1CalibrationWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        values = [os.environ.get(k) for k in ("TIMELEARNER_POSITIVE_N1_CALIBRATION", "TIMELEARNER_POSITIVE_N1_HANDOFF")]
        if not all(values):
            raise unittest.SkipTest("requires actual positive N1 grid and original frozen traces")
        cls.root, cls.handoff = map(Path, values)
        index = load(cls.root/"index.json")
        cls.rows = index["records"]
        if index["kind"] != "positive_n1_measured_calibration_controls" or len(cls.rows) != 2:
            raise RuntimeError("incomplete positive N1 native grid")

    def test_both_owned_calibration_operations_import_the_genuine_exact_solo(self):
        for row in self.rows:
            folder = self.root/"runs"/row["name"]
            audit = audit_run_manifest(folder/"run-manifest.json")
            self.assertTrue(audit["run_evidence_consistent"])
            manifest = load(folder/"run-manifest.json")
            self.assertEqual(manifest["execution"], "completed")
            case = load_case(folder/manifest["source_package_path"])
            self.assertTrue(audit_learned_state(*case)["exact"])
            self.assertEqual(case[0]["sha256"], row["source_solo_sha256"])

    def test_proposed_grid_spans_real_subthreshold_peaks_without_using_them_as_a_verdict(self):
        for row in self.rows:
            top = row["name"].split("-")[0]
            proposal = load(self.root/"jobs"/(row["name"]+"-proposal.json"))
            folder = self.handoff/"runs"/(top+"-frozen")
            manifest = load(folder/"run-manifest.json")
            self.assertEqual(proposal["source_frozen_run"], manifest["sha256"])
            _, observations = load_evaluation(folder/"native/evaluation.json")
            by_id = {o["trial_id"]: o for o in observations}
            self.assertEqual(len(proposal["peaks"]), 8)
            peaks = []
            for record in proposal["peaks"]:
                o = by_id[record["trial_id"]]
                self.assertEqual(o["spike_count"], 0)
                actual = max(s["lt_potential"] for s in o["samples"] if s["time"] >= o["stimulus_onset"])
                self.assertEqual(actual, record["ltz_raw_max"])
                self.assertEqual(record["pattern_hash"], o["pattern_hash"])
                peaks.append(actual)
            grid = row["declared_thresholds"]
            self.assertEqual(grid, proposal["thresholds"])
            self.assertLess(min(grid), min(peaks));self.assertGreater(max(grid), max(peaks))
            unique = sorted(set(peaks))
            for left, right in zip(unique, unique[1:]):
                self.assertTrue(any(left < t < right for t in grid))

    def test_every_declared_candidate_has_a_real_complete_matrix_and_honest_commit_or_rollback(self):
        for row in self.rows:
            folder = self.root/"runs"/row["name"]
            job = load(folder/"input/job.json")
            report = load(folder/"native/transaction.json")
            audit = audit_native_calibration_transaction(report)
            self.assertTrue(audit["transaction_evidence_consistent"])
            self.assertIn(report["status"], ("calibrated", "nonseparable"))
            self.assertEqual(len(report["candidates"]), len(job["thresholds"]))
            self.assertEqual([r["candidate"]["threshold"] for r in report["candidates"]], job["thresholds"])
            for candidate in report["candidates"]:
                self.assertEqual(len(candidate["matrix"]["observations"]), 8)
                self.assertTrue(all(o["complete"] and o["valid"] for o in candidate["matrix"]["observations"]))
            self.assertFalse(report["statistical_independence_verified"])
            model = load(folder/"native/model.json")
            if report["status"] == "nonseparable":
                self.assertFalse(any(r["assessment"]["criterion_met"] for r in report["candidates"]))
                self.assertTrue(report["source_restored"])
                self.assertEqual(model, job["source_recognition"])
                self.assertIsNone(report["calibrated_package"])
            else:
                self.assertEqual(model, report["calibrated_package"])
                self.assertEqual(len(report["confirmation"]["observations"]), 8)

    def test_rehashed_missing_measured_candidate_cannot_keep_a_terminal_grid_claim(self):
        for row in self.rows:
            report = load(self.root/"runs"/row["name"]/"native/transaction.json")
            damaged = copy.deepcopy(report)
            damaged["candidates"].pop()
            signed(damaged)
            with self.assertRaises(EvidenceError):
                audit_native_calibration_transaction(damaged)


if __name__ == "__main__":
    unittest.main()
