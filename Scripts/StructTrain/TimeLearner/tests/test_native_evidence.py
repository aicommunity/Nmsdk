"""Corrupt actual C++ service artifacts, not a second copy of the recorder."""
import copy
import csv
import os
import re
import tempfile
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.native_evidence import (
    EvidenceError, audit_probe, audit_training_summary, load,
)


class NativeEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual native service output")
        cls.directory = Path(directory)
        paths = [p for p in cls.directory.glob("*_service_*.json")
                 if re.search(r"_service_\d+\.json$", p.name)]
        if not paths:
            raise RuntimeError("missing actual C++ probe evidence")
        cls.paths = sorted(paths)
        cls.path = cls.paths[0]
        cls.packet = load(cls.path)
        cls.packets = {}
        cls.audits = []
        for path in cls.paths:
            packet = load(path)
            cls.audits.append(audit_probe(packet, path.with_suffix(".csv")))
            trial = packet["observation"]["specification"]["trial_id"]
            if trial in cls.packets:
                raise RuntimeError("duplicate native trial ID")
            cls.packets[trial] = packet
        cls.summaries = [load(p) for p in sorted(cls.directory.glob("*_training_summary.json"))]
        if len(cls.summaries) != 4:
            raise RuntimeError("requires Classic/Branch x N0/N1 summary evidence")

    def test_actual_native_traces(self):
        for result in self.audits:
            self.assertTrue(result["valid_observation"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_actual_model_bound_negative_certificates(self):
        for summary in self.summaries:
            result = audit_training_summary(summary, self.packets, "pulse0")
            self.assertTrue(result["certificate_consistent"])
            self.assertFalse(result["exact"])
            self.assertIsNone(result["evaluation_verdict"])

    def test_unknown_schema(self):
        packet = copy.deepcopy(self.packet)
        packet["evidence_schema_version"] = 999
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_duplicate_stimulus_id(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["stimuli"][1]["id"] = packet["observation"]["stimuli"][0]["id"]
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_unknown_spikes_cannot_become_zero(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["spike_count"] = 0
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_incomplete_observation_is_not_valid(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["complete"] = False
        result = audit_probe(packet, self.path.with_suffix(".csv"))
        self.assertFalse(result["valid_observation"])
        self.assertEqual(result["reason"], "incomplete_observation")

    def test_corrupted_peak_is_not_silently_accepted(self):
        packet = copy.deepcopy(self.packet)
        packet["observation"]["peaks"][0]["raw_potential"] += .01
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_isolated_window_cannot_select_one_of_multiple_waves(self):
        packet = copy.deepcopy(self.packet)
        spec = packet["observation"]["specification"]
        spec["windows"][0]["begin"] = spec["begin"]
        spec["windows"][0]["end"] = spec["end"]
        requested = packet["requested_specification"]
        requested["windows"][0]["begin"] = 0
        requested["windows"][0]["end"] = requested["end"]
        with self.assertRaises(EvidenceError):
            audit_probe(packet, self.path.with_suffix(".csv"))

    def test_nonfinite_and_damaged_csv_tokens(self):
        with self.path.with_suffix(".csv").open(newline="") as stream:
            original = list(csv.reader(stream))
        for token in ("nan", "inf", "damaged-number"):
            rows = copy.deepcopy(original)
            rows[2][2] = token
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "trace.csv"
                with path.open("w", newline="") as stream:
                    csv.writer(stream).writerows(rows)
                with self.assertRaises(EvidenceError):
                    audit_probe(self.packet, path)

    def test_duplicate_trace_timestamp(self):
        with self.path.with_suffix(".csv").open(newline="") as stream:
            rows = list(csv.reader(stream))
        rows[2][0] = rows[1][0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.csv"
            with path.open("w", newline="") as stream:
                csv.writer(stream).writerows(rows)
            with self.assertRaises(EvidenceError):
                audit_probe(self.packet, path)

    def test_certificate_exact_is_recomputed_from_actual_trials(self):
        summary = copy.deepcopy(self.summaries[0])
        summary["certificate"]["exact"] = True
        with self.assertRaises(EvidenceError):
            audit_training_summary(summary, self.packets, "pulse0")

    def test_reference_label_is_not_row_position(self):
        summary = copy.deepcopy(self.summaries[0])
        summary["references"].reverse()
        summary["certificate"]["residuals"].reverse()
        self.assertFalse(audit_training_summary(summary, self.packets, "pulse0")["exact"])

    def test_missing_final_trial(self):
        packets = dict(self.packets)
        trial = self.summaries[0]["certificate"]["residuals"][0]["trial_id"]
        del packets[trial]
        with self.assertRaises(EvidenceError):
            audit_training_summary(self.summaries[0], packets, "pulse0")


if __name__ == "__main__":
    unittest.main()
