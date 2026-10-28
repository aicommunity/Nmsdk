"""Audit actual native probes at shifted clocks and corrupt their sampling."""
import copy
import csv
import os
import tempfile
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, audit_probe, load


class SamplingClockEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_CLOCK_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires real shifted-clock C++ probes")
        cls.cases = [(load(p), p.with_name(p.name.removesuffix("_evidence.json") + ".csv"))
                     for p in sorted(Path(directory).glob("*_absolute_clock_*_evidence.json"))]
        if len(cls.cases) != 8:
            raise RuntimeError("requires Classic/Branch, 2/20 kHz, two real absolute origins")

    def test_actual_native_clocks(self):
        for packet, trace in self.cases:
            with self.subTest(trial=packet["requested_specification"]["trial_id"]):
                result = audit_probe(packet, trace)
                self.assertTrue(result["valid_observation"])
                self.assertTrue(result["trace_checked"])
                self.assertIsNone(result["evaluation_verdict"])

    def corrupt_trace(self, edit):
        packet, path = self.cases[0]
        packet = copy.deepcopy(packet)
        with path.open(newline="") as stream:
            rows = list(csv.reader(stream))
        edit(packet, rows)
        with tempfile.TemporaryDirectory() as directory:
            corrupt = Path(directory) / "trace.csv"
            with corrupt.open("w", newline="") as stream:
                csv.writer(stream).writerows(rows)
            with self.assertRaises(EvidenceError):
                audit_probe(packet, corrupt)

    def test_missing_frame_with_consistent_sample_count(self):
        def edit(packet, rows):
            rows.pop(len(rows) // 2)
            packet["observation"]["sample_count"] -= 1
        self.corrupt_trace(edit)

    def test_duplicate_time(self):
        self.corrupt_trace(lambda p, rows: rows[30].__setitem__(0, rows[29][0]))

    def test_unresolvable_sampling_period(self):
        packet, path = self.cases[0]
        packet = copy.deepcopy(packet)
        packet["observation"]["specification"]["maximum_sample_gap"] = 1e-12
        packet["requested_specification"]["maximum_sample_gap"] = 1e-12
        with self.assertRaises(EvidenceError):
            audit_probe(packet, path)

    def test_old_invalid_observation_is_not_recertified(self):
        packet, path = self.cases[0]
        packet = copy.deepcopy(packet)
        packet["observation"]["valid"] = False
        packet["observation"]["reasons"] = ["sample_gap"]
        self.assertFalse(audit_probe(packet, path)["valid_observation"])
