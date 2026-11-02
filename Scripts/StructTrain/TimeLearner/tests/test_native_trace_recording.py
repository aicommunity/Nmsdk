"""Fresh traces preserve the original native fault callbacks and outcomes."""
import os
import unittest
from pathlib import Path

from ..native_evidence import load
from ..native_test_reports import inventory_native_test_run


class NativeTraceRecordingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_NATIVE_TRACE_RECORDING_DIR")
        if not value:
            raise unittest.SkipTest("requires actual 18-case native recording output")
        cls.root = Path(value)
        cls.native = cls.root/"native"
        cls.spec = Path(__file__).parents[1]/"specs/native-trace-recording-report-v2.json"

    def packet(self, prefix):
        return load(self.native/(prefix+"_training_proof_1.json"))

    def test_all_declared_sources_have_traces_without_double_counting_aliases(self):
        result = inventory_native_test_run(self.spec, self.root)
        self.assertEqual(result["tests"], 18)
        self.assertEqual(result["trials"], 88)
        self.assertEqual(result["primary_packet_count"], 88)
        self.assertEqual(len(result["packet_aliases"]), 6)
        self.assertEqual(result["untraced"], [])
        self.assertEqual(result["observability_gaps"], [])
        # Intended invalid and censored observations remain invalid/censored.
        self.assertFalse(result["data_complete"])
        self.assertFalse(result["visual_acceptance_complete"])
        self.assertIsNone(result["scientific_verdict"])

    def test_physics_mutation_callback_still_invalidates_tenth_actual_sample(self):
        for topology in ("Classic", "Branch"):
            packet = self.packet(topology+"_2000_N0_observer_external_physics")
            self.assertEqual(packet["observation"]["sample_count"], 10)
            self.assertFalse(packet["observation"]["valid"])
            self.assertIn("model_revision_changed", packet["reasons"])
            self.assertTrue(packet["requires_fresh_verification"])

    def test_external_stop_and_deadline_remain_censored(self):
        for prefix, samples in [(t+"_2000_N0_service_external_stop", 10) for t in ("Classic", "Branch")]+[("Branch_2000_N1_service_deadline", 4)]:
            packet = self.packet(prefix)
            self.assertEqual(packet["native_status"], "cancelled")
            self.assertEqual(packet["observation"]["sample_count"], samples)
            self.assertFalse(packet["observation"]["complete"])

    def test_spoofed_hash_is_rejected_before_any_raw_sample(self):
        prefix = "Classic_2000_N0_service_spoofed_hash"
        packet = self.packet(prefix)
        self.assertIsNone(packet["observation"])
        self.assertEqual(packet["native_status"], "rejected")
        self.assertIn("native_pattern_hash_mismatch", packet["reasons"])
        self.assertEqual((self.native/(prefix+"_training_proof_1.csv")).read_text().splitlines(),
                         ["time,stimulus,soma0,soma1"])

    def test_cold_warm_outcomes_and_retarget_remain_distinct(self):
        prefix = "Classic_2000_N1_service_exact_warm_"
        cold = load(self.native/(prefix+"cold_outcome.json"))
        warm = load(self.native/(prefix+"warm_outcome.json"))
        self.assertEqual((cold["reference_probes"], cold["search_probes"]), (2, 4))
        self.assertEqual((warm["reference_probes"], warm["search_probes"]), (0, 4))
        self.assertTrue(cold["certificate"]["exact"])
        self.assertTrue(warm["certificate"]["exact"])
        retarget = load(self.native/(prefix+"retarget_control.json"))
        self.assertEqual(retarget["kind"], "native_retarget_invalidation")
        self.assertFalse(retarget["references"])
        self.assertFalse(retarget["certificate"])
        self.assertNotEqual(retarget["outcome"], "exact")
