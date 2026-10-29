import copy
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.connected_stop_evidence import audit_connected_stop
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.stopped_evidence import load_case, audit_stopped_state


class ConnectedStopEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        baseline = os.environ.get("TIMELEARNER_CONNECTED_STOP_BASELINE")
        fixed = os.environ.get("TIMELEARNER_CONNECTED_STOP_FIXED")
        if not baseline or not fixed:
            raise unittest.SkipTest("requires actual baseline and fixed connected stop readbacks")
        cls.baseline, cls.fixed = Path(baseline), Path(fixed)
        expected = {f"{topology}_2000_N1_connected_stop_{point}_mode{mode}_connected_stop.json"
                    for topology in ("Classic", "Branch") for mode in (0, 1) for point in range(5)}
        for root in (cls.baseline, cls.fixed):
            if {p.name for p in root.glob("*_connected_stop.json")} != expected:
                raise RuntimeError("requires complete 20-case native matrix")
        cls.names = sorted(expected)

    def case(self, root, name):
        packet = load(root / name)
        state = root / name.replace("_connected_stop.json", "_stopped_state.json")
        return packet, load_case(state) if state.is_file() else None

    def test_baseline_proves_ignored_stops_and_positive_controls(self):
        results = [audit_connected_stop(*self.case(self.baseline, name)) for name in self.names]
        self.assertEqual(sum(r["stop_requested"] and not r["stop_honored"] for r in results), 16)
        self.assertEqual(sum(r["keep_true_control_active"] for r in results), 4)

    def test_fixed_honors_all_stops_without_false_convergence(self):
        results = [audit_connected_stop(*self.case(self.fixed, name)) for name in self.names]
        self.assertEqual(sum(r["stop_honored"] for r in results), 16)
        self.assertEqual(sum(r["keep_true_control_active"] for r in results), 4)
        for result in results:
            self.assertIsNone(result["evaluation_verdict"])
            if result["stop_honored"]:
                self.assertFalse(result["stopped_proof"]["certificate_present"])

    def test_corrupt_flags_certificate_schema_and_counts_rejected(self):
        name = next(name for name in self.names if "_stop_0_" in name)
        original, case = self.case(self.fixed, name)
        for key, value in (("schema_version", 2), ("calculate_mode", 99), ("source_value", True),
                           ("learner_need", True), ("stop_requested", False), ("connected", False),
                           ("certificate_present", True), ("observed_packets", 999)):
            packet = copy.deepcopy(original);packet[key] = value
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                audit_connected_stop(packet, case)

    def test_model_evidence_cannot_be_omitted_or_substituted(self):
        name = next(name for name in self.names if "_stop_1_" in name)
        packet, case = self.case(self.fixed, name)
        with self.assertRaises(EvidenceError):
            audit_connected_stop(packet)
        changed = list(copy.deepcopy(case));changed[0]["training_outcome"] = "exact"
        with self.assertRaises(EvidenceError):
            audit_connected_stop(packet, tuple(changed))

    def test_existing_twenty_stopped_regressions_retain_primary_proof(self):
        paths = sorted(p for p in self.fixed.glob("*_stopped_state.json") if "_connected_stop_" not in p.name)
        self.assertEqual(len(paths), 20)
        for path in paths:
            result = audit_stopped_state(*load_case(path))
            self.assertFalse(result["certificate_present"])
