"""Actual August primary CSV, label-based metrics and no invented completeness."""
import contextlib
import csv
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..__main__ import main
from ..historical_selectivity import analyze_historical_csv
from ..native_evidence import EvidenceError


class HistoricalSelectivityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["TIMELEARNER_AUGUST_PHASEA"])
        cls.paths = [cls.root/p/"SelectivityLog/results.csv" for p in (
            "EXP00_baseline/Test", "EXP01_ltz_threshold_sweep/Test_thr00130",
            "EXP01_ltz_threshold_sweep/Test_thr00135")]
        if not all(p.is_file() for p in cls.paths):
            raise RuntimeError("requires all original August4/8,5/8,6/8 primary CSVs")
        cls.ids = [str(i) for i in range(8)]
        with cls.paths[0].open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream);cls.fields = reader.fieldnames;cls.rows = list(reader)

    def write(self, path, rows=None, fields=None):
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=self.fields if fields is None else fields)
            writer.writeheader();writer.writerows(self.rows if rows is None else rows)

    def test_actual_august4_5_6_observations_are_retained_without_new_scientific_pass(self):
        for path, correct in zip(self.paths, (4, 5, 6)):
            result = analyze_historical_csv(path, self.ids)
            self.assertEqual(result["native_match_count"], correct)
            self.assertEqual(result["reported_counts"], {"TP": 1, "FP": 8-correct, "FN": 0, "TN": correct-1})
            self.assertEqual(result["validity"], "unknown")
            self.assertFalse(result["complete_observation_windows_verified"])
            self.assertIsNone(result["evaluation_verdict"])
            self.assertIsNone(result["late_responses"])
            self.assertTrue(all(row["complete"] is None and row["spike_count"] is None for row in result["rows"]))

    def test_reversing_rows_moves_target_and_preserves_label_based_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"reversed.csv";self.write(path, list(reversed(self.rows)))
            result = analyze_historical_csv(path, self.ids)
            self.assertEqual(result["reported_counts"], analyze_historical_csv(self.paths[0], self.ids)["reported_counts"])
            self.assertEqual(result["rows"][-1]["label"], "target")

    def test_numeric_corruption_and_inconsistent_native_match_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"bad.csv"
            mutations = [("ltz_potential_max", "nan"), ("soma_amp_0", "inf"), ("soma_amp_sum", "broken"),
                         ("isi1", "0"), ("isi3", "nan"), ("stim_count", "4.0"),
                         ("neuron_t_rel", "-1"), ("match", "0"), ("neuron_fired", "2")]
            for key, value in mutations:
                with self.subTest(key=key, value=value):
                    rows = [dict(row) for row in self.rows];rows[0][key] = value;self.write(path, rows)
                    with self.assertRaises((EvidenceError, ValueError)):
                        analyze_historical_csv(path, self.ids)

    def test_duplicate_missing_and_unexpected_trials_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"bad.csv"
            for rows in (self.rows[:-1], self.rows+[self.rows[0]], self.rows[:-1]+[{**self.rows[-1], "trial": "extra"}]):
                self.write(path, rows)
                with self.assertRaises(EvidenceError):analyze_historical_csv(path, self.ids)

    def test_trial_set_must_be_explicit_and_cannot_be_derived_from_incomplete_csv(self):
        for expected in (None, [], ["0", "0"], [0, 1]):
            with self.assertRaises(EvidenceError):analyze_historical_csv(self.paths[0], expected)

    def test_new_schema_and_duplicate_header_cannot_be_downcast_to_august_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"schema.csv"
            rows = [{**r, "complete": "1"} for r in self.rows]
            self.write(path, rows, self.fields+["complete"])
            with self.assertRaisesRegex(EvidenceError, "unknown_historical_selectivity_schema"):
                analyze_historical_csv(path, self.ids)
            self.write(path, fields=self.fields+[self.fields[-1]])
            with self.assertRaisesRegex(EvidenceError, "missing_or_duplicate_historical_header"):
                analyze_historical_csv(path, self.ids)

    def test_soma_columns_support_more_than_four_without_silent_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"five.csv"
            self.write(path, [{**r, "soma_amp_4": "0.001"} for r in self.rows], self.fields+["soma_amp_4"])
            result = analyze_historical_csv(path, self.ids)
            self.assertTrue(all(len(r["soma_amplitudes"]) == 5 for r in result["rows"]))
            fields = [name for name in self.fields if name != "soma_amp_2"]
            self.write(path, [{k: v for k, v in r.items() if k in fields} for r in self.rows], fields)
            with self.assertRaisesRegex(EvidenceError, "noncontiguous_historical_columns"):
                analyze_historical_csv(path, self.ids)

    def invoke(self, path, *options):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = main(["analyze", str(path), "--format", "historical-selectivity", *options])
        return status, out.getvalue(), err.getvalue()

    def test_production_cli_preserves_history_and_existing_output(self):
        status, text, error = self.invoke(self.paths[2], "--expected-trial-ids", *self.ids)
        self.assertEqual(status, 0, error)
        self.assertEqual(json.loads(text)["analysis"]["native_match_count"], 6)
        self.assertIsNone(json.loads(text)["evaluation_verdict"])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/"prior.json";output.write_text("prior")
            status, text, error = self.invoke(self.paths[0], "--expected-trial-ids", *self.ids, "--output", str(output))
            self.assertEqual(status, 2)
            self.assertFalse(text)
            self.assertEqual(json.loads(error)["execution"], "process_error")
            self.assertEqual(output.read_text(), "prior")

    def test_malformed_quoted_csv_has_structured_cli_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"broken.csv"
            path.write_text(",".join(self.fields)+'\n"unterminated')
            status, text, error = self.invoke(path, "--expected-trial-ids", *self.ids)
            self.assertEqual(status, 2)
            self.assertFalse(text)
            self.assertEqual(json.loads(error)["validity"], "invalid")
