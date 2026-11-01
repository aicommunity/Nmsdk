"""Independent derivation checks over actual native five-mode candidate exports."""
import copy
import os
import struct
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.learned_evidence import load_case as load_solo
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.recognition_evidence import audit_recognition_derivation, audit_recognition_state, load_case


class NativePostTuneCandidatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_POSTTUNE_CANDIDATES_DIR")
        if not directory:
            raise unittest.SkipTest("requires genuine native candidate exports")
        root = Path(directory)
        cls.cases = []
        cls.frozen = [load_case(p) for p in sorted(root.glob("*_recognition_state.json"))]
        if len(cls.frozen) != 4:
            raise RuntimeError("requires Classic/Branch N0/N1 native controls")
        for path in sorted(root.glob("*_post_tune_candidate_*.json")):
            stem = path.name.split("_post_tune_candidate_")[0]
            cls.cases.append((load(path), load_solo(path.with_name(stem + "_learned_state.json"))))
        if len(cls.cases) != 20:
            raise RuntimeError("requires all five modes for every actual control")

    def test_all_five_modes_derive_from_same_immutable_base(self):
        modes = set()
        for package, source in self.cases:
            with self.subTest(revision=package["model_revision"]):
                result = audit_recognition_derivation(package, source)
                self.assertTrue(result["conversion_math_verified"])
                self.assertTrue(result["other_physics_preserved"])
                self.assertIsNone(result["evaluation_verdict"])
                modes.add(package["conversion_spec"]["post_tune"]["mode"])
        self.assertEqual(modes, {"off", "keep_done", "canon_rmin", "flat_last_r", "search_synthetic_candidate"})

    def test_selected_canon_native_roundtrip_has_complete_actual_waveform(self):
        for case in self.frozen:
            result = audit_recognition_state(*case)
            self.assertTrue(result["frozen_transport"]["complete"])
            self.assertIsNone(result["evaluation_verdict"])

    def reject(self, edit, resign_graph=False):
        for original, source in self.cases:
            package = copy.deepcopy(original)
            edit(package)
            if resign_graph:
                identity = package["neuron"]["graph"]["identity"]
                identity["sha256"] = canonical_model_sha256(identity["model"])
                package["model_revision"] = identity["sha256"]
                package["conversion_record"]["result_identity"] = identity["sha256"]
            for envelope in (package["neuron"], package):
                envelope["sha256"] = canonical_model_sha256({k: v for k, v in envelope.items() if k != "sha256"})
            with self.assertRaises(EvidenceError):
                audit_recognition_derivation(package, source)

    def test_wrong_source_revision(self):
        self.reject(lambda p: p["conversion_spec"]["post_tune"].__setitem__("source_model_revision", "0" * 64))

    def test_candidate_cannot_claim_selection(self):
        self.reject(lambda p: p["conversion_record"]["post_tune"].__setitem__("selection_status", "selected"))

    def test_candidate_cannot_claim_calibration(self):
        self.reject(lambda p: p["conversion_record"]["post_tune"].__setitem__("calibration_status", "calibrated"))

    def test_rewritten_decision(self):
        self.reject(lambda p: p["conversion_record"]["post_tune"]["decisions"][0].__setitem__("applied_resistance", 1.))

    def test_capacity_cannot_change_with_resistances(self):
        def edit(p):
            node = next(n for n in p["neuron"]["graph"]["identity"]["model"]["nodes"] if "Capacity" in n["parameters"])
            field = node["parameters"]["Capacity"]["data"]
            value = struct.unpack(">d", bytes.fromhex(field["value"]))[0]
            field["value"] = struct.pack(">d", value * 1.1).hex()
        self.reject(edit, resign_graph=True)

    def test_solo_certificate_is_not_transferred(self):
        self.reject(lambda p: p.__setitem__("recognition_certificate", p["source_solo"]["certificate"]))
