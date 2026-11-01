"""Corruptions of real native model/trace exports, not reimplemented fixtures."""
import csv
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..loaded_readout_reports import audit_run, read_case
from ..native_evidence import EvidenceError


class LoadedReadoutReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["TL_LOADED_READOUT_SOURCE"])
        cls.case = cls.root/"artifacts/Classic-N4-f2000-state0"

    def test_actual_native_corpus_and_all_somas(self):
        data, report = audit_run(self.root)
        self.assertEqual(len(data), 32)
        self.assertEqual(report["case_soma_pairs"], 68)
        self.assertIsNone(report["scientific_verdict"])
        self.assertTrue(all(v["summary"]["sample_grid_complete"] for v in data.values()))

    def corrupted(self, mutate, reason):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/"case";shutil.copytree(self.case, folder)
            mutate(folder)
            with self.assertRaisesRegex(EvidenceError, reason):read_case(folder, False, 4, 2000, False)

    @staticmethod
    def csv_change(folder, mutate):
        path = folder/"roundtrip.csv"
        with path.open(newline="") as stream:rows = list(csv.reader(stream))
        mutate(rows)
        with path.open("w", newline="") as stream:csv.writer(stream).writerows(rows)

    def csv_corrupted(self, mutate, reason):
        self.corrupted(lambda folder: self.csv_change(folder, mutate), reason)

    def test_truncated_grid(self):
        self.csv_corrupted(lambda rows: rows.pop(), "readout_incomplete_grid")

    def test_duplicate_clock(self):
        self.csv_corrupted(lambda rows: rows.__setitem__(3, rows[2]), "readout_sample_clock")

    def test_nonfinite_sample(self):
        self.csv_corrupted(lambda rows: rows[1].__setitem__(4, "nan"), "readout_nonfinite_sample")

    def test_invalid_numeric_token(self):
        self.csv_corrupted(lambda rows: rows[1].__setitem__(4, "broken"), "readout_invalid_number")

    def test_stimulus_disagreement(self):
        self.csv_corrupted(lambda rows: rows[1].__setitem__(2, "1"), "readout_stimulus_disagreement")

    def test_missing_all_pulses(self):
        def remove(rows):
            for row in rows[1:]:row[1:3] = ["0", "0"]
        self.csv_corrupted(remove, "readout_pulse_count")

    def test_changed_waveform(self):
        self.csv_corrupted(lambda rows: rows[1].__setitem__(4, "0.1"), "readout_roundtrip_waveform_changed")

    def test_flat_source_and_loaded_soma(self):
        def flatten(rows):
            for row in rows[1:]:row[3:5] = ["0", "0"]
        self.csv_corrupted(flatten, "readout_flat_soma_control")

    def json_corrupted(self, name, mutate, reason):
        def change(folder):
            path = folder/name;data = json.loads(path.read_text());mutate(data)
            path.write_text(json.dumps(data))
        self.corrupted(change, reason)

    def test_individual_physics_change(self):
        def capacity(data):
            node = next(n for n in data["nodes"] if n["path"].endswith("Soma1.ExcChannel"))
            node["physics"]["capacity_f"] *= 2
        self.json_corrupted("loaded-model.json", capacity, "readout_graph_changed_on_load")

    def test_missing_link(self):
        self.json_corrupted("loaded-model.json", lambda data: data["links"].pop(), "readout_graph_changed_on_load")

    def test_unknown_graph_schema(self):
        self.json_corrupted("loaded-model.json", lambda data: data.__setitem__("schema_version", 999),
                            "readout_unknown_graph_schema")

    def test_duplicate_json_key(self):
        self.corrupted(lambda folder: (folder/"loaded-model.json").write_text(
            '{"schema_version":1,"schema_version":1}'), "duplicate_json_key")

    def test_wrong_dimension(self):
        self.json_corrupted("loaded-dimensions.json", lambda data: data.__setitem__("soma_rows", 2),
                            "readout_wrong_loaded_dimensions")

    def test_state_protocol_is_explicit(self):
        with self.assertRaisesRegex(EvidenceError, "readout_wrong_state_protocol"):
            read_case(self.case, False, 4, 2000, True)

    def test_missing_condition_prevents_whole_run_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("validation.json", "regression-validation.json", "gtest.xml"):
                shutil.copyfile(self.root/name, root/name)
            # The expected matrix cannot be replaced by a successful subset.
            (root/"artifacts").mkdir()
            with self.assertRaisesRegex(EvidenceError, "readout_artifact_condition_set"):audit_run(root)


if __name__ == "__main__":
    unittest.main()
