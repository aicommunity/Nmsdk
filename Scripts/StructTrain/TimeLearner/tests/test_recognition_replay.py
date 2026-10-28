"""Use real native child-process output, never synthesized positive replay traces."""
import copy
import csv
import json
import os
from pathlib import Path
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.recognition_evidence import audit_fresh_recognition_transport, load_case


class RecognitionReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_RECOGNITION_REPLAY_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual fresh-process recognition imports")
        root = Path(directory)
        cls.cases = []
        for package in sorted((root / "input").glob("*_recognition_state.json")):
            prefix = package.name.removesuffix("_recognition_state.json")
            record = root / "replay" / (prefix + ".json")
            cls.cases.append((load_case(package), json.loads(record.read_text()), Path(str(record) + ".csv")))
        if len(cls.cases) != 8:
            raise RuntimeError("requires eight completed native fresh-process replay cases")

    def test_actual_fresh_process_waveforms(self):
        for case in self.cases:
            with self.subTest(model=case[0][0]["model_revision"]):
                result = audit_fresh_recognition_transport(*case)
                self.assertTrue(result["waveform_values_exact"])
                self.assertTrue(result["waveform_bytes_exact"])
                self.assertFalse(result["process_provenance_verified"])
                self.assertFalse(result["native_import_verified"])
                self.assertIsNone(result["evaluation_verdict"])

    def reject_record(self, edit):
        case, record, trace = copy.deepcopy(self.cases[0])
        edit(record)
        with self.assertRaises(EvidenceError):
            audit_fresh_recognition_transport(case, record, trace)

    def test_incomplete_or_unknown_schema(self):
        self.reject_record(lambda r: r.__setitem__("complete", False))
        self.reject_record(lambda r: r.__setitem__("schema_version", True))
        self.reject_record(lambda r: r.__setitem__("schema_version", 999))

    def test_changed_model_or_trial(self):
        self.reject_record(lambda r: r.__setitem__("frozen_after", "changed"))
        self.reject_record(lambda r: r.__setitem__("trial_id", "another-trial"))

    def test_false_scientific_verdict_or_count(self):
        self.reject_record(lambda r: r.__setitem__("scientific_verdict", "PASS"))
        self.reject_record(lambda r: r.__setitem__("sample_count", True))
        self.reject_record(lambda r: r.__setitem__("sample_count", r["sample_count"] - 1))

    def test_missing_sample_even_with_updated_summary(self):
        case, record, trace = copy.deepcopy(self.cases[0])
        with trace.open(newline="") as stream:
            rows = list(csv.reader(stream))
        rows.pop(len(rows) // 2)
        record["sample_count"] -= 1
        self.reject_trace(case, record, rows)

    def test_corrupted_or_nonfinite_soma(self):
        case, record, trace = copy.deepcopy(self.cases[0])
        with trace.open(newline="") as stream:
            original = list(csv.reader(stream))
        for value in ("nan", "inf", str(float(original[20][2]) + .001)):
            rows = copy.deepcopy(original)
            rows[20][2] = value
            self.reject_trace(case, record, rows)

    def reject_trace(self, case, record, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replay.csv"
            with path.open("w", newline="") as stream:
                csv.writer(stream).writerows(rows)
            with self.assertRaises(EvidenceError):
                audit_fresh_recognition_transport(case, record, path)
