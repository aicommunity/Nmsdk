"""Corrupt real learned-state packages and their primary evidence."""
import copy
import os
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.learned_evidence import audit_learned_state, load_case
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError


class LearnedEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_LEARNED_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual C++ learned-state artifacts")
        cls.cases = [load_case(path) for path in sorted(Path(directory).glob("*_learned_state.json"))]
        if len(cls.cases) < 5:
            raise RuntimeError("missing actual Classic/Branch N0/N1 and Exact controls")

    def test_actual_primary_evidence(self):
        for case in self.cases:
            with self.subTest(model=case[0]["model_revision"]):
                result = audit_learned_state(*case)
                self.assertTrue(result["certificate_consistent"])
                self.assertFalse(result["native_import_verified"])
                self.assertIsNone(result["evaluation_verdict"])

    def reject(self, edit):
        case = copy.deepcopy(self.cases[0])
        edit(*case)
        with self.assertRaises(EvidenceError):
            audit_learned_state(*case)

    def test_false_exact(self):
        self.reject(lambda p, *_: p["certificate"].__setitem__("exact", not p["certificate"]["exact"]))

    def test_missing_final(self):
        self.reject(lambda p, *_: p["final_packets"].clear())

    def test_duplicate_reference(self):
        self.reject(lambda p, *_: p["reference_packets"].append(copy.deepcopy(p["reference_packets"][0])))

    def test_changed_embedded_measurement(self):
        def edit(p, *_):
            p["reference_packets"][0]["observation"]["peaks"][0]["raw_potential"] += .001
        self.reject(edit)

    def test_missing_primary_csv(self):
        self.reject(lambda p, s, packets, traces: traces.pop(next(iter(traces))))

    def test_changed_archive_identity(self):
        self.reject(lambda p, *_: p["neuron"]["graph"]["identity"].__setitem__("sha256", "corrupt"))

    def test_changed_tolerance(self):
        self.reject(lambda p, *_: p["configuration"]["search"]["tolerances"].__setitem__("sync", 999.))

    def test_not_a_dynamic_checkpoint(self):
        self.reject(lambda p, *_: p.__setitem__("dynamic_checkpoint", True))
