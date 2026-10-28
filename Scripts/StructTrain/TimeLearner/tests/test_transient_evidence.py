"""Corruption controls consume actual Classic/Branch transient presentations."""
import contextlib
import copy
import csv
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.transient_evidence import audit_transient_presentation, load_case


class TransientEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_TRANSIENT_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual native transient presentation data")
        cls.paths = sorted(Path(directory).glob("*_posttune_transient_presentation_*_spec.json"))
        cls.cases = [load_case(path) for path in cls.paths]
        if len(cls.cases) != 8 or sum(case[0]["presented_isi"][0] == 0 for case in cls.cases) != 4:
            raise RuntimeError("requires both learners, both frequencies and two distinct stimuli including zero onset")

    def test_actual_native_presentations(self):
        for case in self.cases:
            with self.subTest(trial=case[0]["trial_id"]):
                result = audit_transient_presentation(*case)
                self.assertTrue(result["training_goal_preserved"])
                self.assertTrue(result["measurement_uses_presented_pattern"])
                self.assertFalse(result["measured_training_certificate_verified"])
                self.assertFalse(result["native_execution_verified"])
                self.assertIsNone(result["evaluation_verdict"])

    def test_actual_cli(self):
        from Scripts.StructTrain.TimeLearner.__main__ import main
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = main(["analyze", str(self.paths[0]), "--format", "posttune-transient"])
        self.assertEqual(status, 0, error.getvalue())
        self.assertTrue(json.loads(output.getvalue())["analysis"]["training_goal_preserved"])

    def reject(self, edit):
        case = copy.deepcopy(self.cases[0])
        edit(*case)
        with self.assertRaises(EvidenceError):
            audit_transient_presentation(*case)

    def test_target_cannot_be_replaced_by_probe(self):
        self.reject(lambda s, o, p: o.__setitem__("training_goal_after", s["presented_isi"]))
        self.reject(lambda s, o, p: o.__setitem__("material_goal_after", s["presented_isi"]))

    def test_timing_must_use_actual_stimulus(self):
        self.reject(lambda s, o, p: o.__setitem__("expected_relative_times", [0., s["training_goal"][1]]))
        self.reject(lambda s, o, p: o.__setitem__("onsets", [1., 1.5]))

    def test_incomplete_or_changed_model(self):
        self.reject(lambda s, o, p: o.__setitem__("complete", False))
        self.reject(lambda s, o, p: o.__setitem__("frozen_after", "changed"))

    def test_unknown_schema_and_scientific_claim(self):
        self.reject(lambda s, o, p: s.__setitem__("schema_version", True))
        self.reject(lambda s, o, p: o.__setitem__("scientific_verdict", "PASS"))

    def test_missing_or_nonfinite_sample(self):
        for damage in ("missing", "nan"):
            spec, observation, original = copy.deepcopy(self.cases[0])
            with original.open(newline="") as stream:
                rows = list(csv.reader(stream))
            if damage == "missing":
                rows.pop(len(rows) // 2)
                observation["sample_count"] -= 1
            else:
                rows[20][2] = damage
            with tempfile.TemporaryDirectory() as directory:
                trace = Path(directory) / "trial.csv"
                with trace.open("w", newline="") as stream:
                    csv.writer(stream).writerows(rows)
                with self.assertRaises(EvidenceError):
                    audit_transient_presentation(spec, observation, trace)
