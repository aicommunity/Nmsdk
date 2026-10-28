"""Mutation checks use actual native stopped-state packages and trace files."""
import copy
import os
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.stopped_evidence import audit_stopped_state, load_case
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256


class StoppedEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_STOPPED_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual native stopped-state artifacts")
        cls.cases = [load_case(p) for p in sorted(Path(directory).glob("*_stopped_state.json"))]
        if len(cls.cases) != 16:
            raise RuntimeError("requires eight stopped scenarios in both topologies")

    def test_actual_primary_evidence(self):
        for case in self.cases:
            with self.subTest(outcome=case[0]["training_outcome"], revision=case[0]["model_revision"]):
                audit = audit_stopped_state(*case)
                self.assertFalse(audit["certificate_present"])
                self.assertFalse(audit["native_import_verified"])
                self.assertIsNone(audit["evaluation_verdict"])

    def reject(self, mutate):
        for source in self.cases:
            case = copy.deepcopy(source); mutate(*case)
            case[0]["sha256"] = canonical_model_sha256({k: v for k, v in case[0].items() if k != "sha256"})
            with self.subTest(outcome=case[0]["training_outcome"]):
                with self.assertRaises(EvidenceError):
                    audit_stopped_state(*case)

    def test_false_exact(self):
        self.reject(lambda p, *_: p.__setitem__("training_outcome", "exact"))

    def test_false_certificate(self):
        self.reject(lambda p, *_: p.__setitem__("certificate", {"exact": True}))

    def test_false_reference_completion(self):
        self.reject(lambda p, *_: p.__setitem__("reference_complete", not p["reference_complete"]))

    def test_missing_observation(self):
        self.reject(lambda p, *_: p["observed_packets"].pop())

    def test_duplicate_observation(self):
        self.reject(lambda p, *_: p["observed_packets"].append(copy.deepcopy(p["observed_packets"][0])))

    def test_missing_csv(self):
        self.reject(lambda p, s, packets, traces: traces.pop(next(iter(traces))))

    def test_changed_capture_origin(self):
        self.reject(lambda p, *_: p.__setitem__("capture_revision", "changed"))

    def test_changed_model_identity(self):
        self.reject(lambda p, *_: p["neuron"]["graph"]["identity"].__setitem__("sha256", "changed"))

    def test_dynamic_checkpoint_claim(self):
        self.reject(lambda p, *_: p.__setitem__("dynamic_checkpoint", True))
