"""Actual learner frozen-owner controls and corrupted-observation rejection."""
import copy
import os
from pathlib import Path
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.recognition_owner_evidence import audit_owner_recognition, load_case


class RecognitionOwnerEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_RECOGNITION_OWNER_EVIDENCE_DIR")
        if not value:
            raise unittest.SkipTest("requires actual native frozen-owner cases with measured before/after hashes")
        cls.paths = sorted(Path(value).glob("*_owner_recognition_state.json"))
        expected = {
            f"{topology}_2000_N{mode}_learned_boundary_recognition_4_owner_recognition_state.json"
            for topology in ("Classic", "Branch") for mode in (0, 1)
        }
        expected.update({
            "Branch_2000_N1_learned_boundary_recognition_5_owner_recognition_state.json",
            "Branch_2000_N1_learned_boundary_recognition_6_owner_recognition_state.json",
            "Branch_2000_N1_learned_boundary_inputs1_recognition_5_owner_recognition_state.json",
            "Branch_2000_N0_learned_boundary_explicit_tolerance_inputs6_recognition_4_owner_recognition_state.json",
            "Classic_2000_N0_learned_boundary_configured_recognition_4_owner_recognition_state.json",
            "Branch_2000_N1_learned_boundary_configured_recognition_4_owner_recognition_state.json",
            "Classic_2000_N1_learned_boundary_automatic_recognition_4_owner_recognition_state.json",
            "Branch_2000_N0_learned_boundary_automatic_recognition_4_owner_recognition_state.json",
        })
        if {path.name for path in cls.paths} != expected:
            raise RuntimeError("requires all twelve native owner cases including configured V2 and automatic control")
        cls.cases = [load_case(path) for path in cls.paths]

    def test_actual_conversion_source_proofs_and_frozen_native_waveforms(self):
        for path, case in zip(self.paths, self.cases):
            with self.subTest(case=path.name):
                result = audit_owner_recognition(*case)
                self.assertTrue(result["owner_readback_consistent"])
                self.assertTrue(result["conversion"]["conversion_math_verified"])
                self.assertTrue(result["conversion"]["frozen_transport"]["paired_values_exact"])
                self.assertIsNone(result["evaluation_verdict"])
                self.assertEqual(case[0]["source_solo"]["controller_version"], 2 if "_configured_" in path.name else 1)
                self.assertEqual(case[0]["source_solo"]["calculate_mode"], 0 if "_automatic_" in path.name else 1)

    def test_incorrect_scope_hash_window_and_controller_flags_rejected(self):
        for case in self.cases:
            for key, value in (("recognition_certificate", {}), ("training_controller_installed", True),
                               ("need", True), ("frozen_after_owner", "0" * 64),
                               ("source_solo_sha256", "0" * 64), ("begin", case[3]["begin"] + 1),
                               ("sample_count", case[3]["sample_count"] - 1), ("evaluation_verdict", "PASS"),
                               ("unknown_factor", "silently ignored")):
                with self.subTest(case=case[3]["trial_id"], field=key):
                    changed = list(case)
                    changed[3] = copy.deepcopy(case[3])
                    changed[3][key] = value
                    with self.assertRaises(EvidenceError):
                        audit_owner_recognition(*changed)

    def test_lost_final_sample_duplicate_time_and_nonfinite_csv_rejected(self):
        case = self.cases[0]
        rows = case[4].read_text(encoding="utf-8").splitlines()
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "corrupted.csv"
            for mutation in ("truncated", "duplicate", "nan"):
                changed = list(rows)
                if mutation == "truncated":
                    changed = changed[:-2]
                elif mutation == "duplicate":
                    changed[2] = changed[1]
                else:
                    tokens = changed[2].split(",")
                    tokens[3] = "NaN"
                    changed[2] = ",".join(tokens)
                trace.write_text("\n".join(changed) + "\n", encoding="utf-8")
                altered = list(case)
                altered[4] = trace
                with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                    audit_owner_recognition(*altered)
