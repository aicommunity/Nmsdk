"""Corrupt actual native Reset exports; no synthetic learner implementation."""
import csv
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..hot_readout_reports import audit_run, read_case
from ..native_evidence import EvidenceError


class HotReadoutReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["TL_HOT_READOUT_SOURCE"])
        cls.case = cls.root/"artifacts/Classic-N2-f2000"

    def test_actual_native_corpus(self):
        data, summary = audit_run(self.root)
        self.assertEqual(len(data), 8);self.assertEqual(summary["case_soma_pairs"], 16)
        self.assertEqual(summary["stale_cases"], int(os.environ["TL_HOT_EXPECT_STALE"]))
        self.assertIsNone(summary["scientific_verdict"]);self.assertIsNone(summary["training_certificate"])

    def corrupt(self, change, reason):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/"case";shutil.copytree(self.case, folder);change(folder)
            with self.assertRaisesRegex(EvidenceError, reason):read_case(folder, False, 2, 2000)

    def json_corrupt(self, change, reason):
        def mutate(folder):
            p = folder/"observation.json";o = json.loads(p.read_text());change(o);p.write_text(json.dumps(o))
        self.corrupt(mutate, reason)

    def csv_corrupt(self, change, reason):
        def mutate(folder):
            p = folder/"warm.csv"
            with p.open(newline="") as f:rows = list(csv.reader(f))
            change(rows)
            with p.open("w", newline="") as f:csv.writer(f).writerows(rows)
        self.corrupt(mutate, reason)

    def test_unknown_schema(self):self.json_corrupt(lambda o:o.update(schema_version=2), "hot_unknown_observation_schema")
    def test_wrong_condition(self):self.json_corrupt(lambda o:o.update(inputs=4), "hot_condition_mismatch")
    def test_wrong_dimension(self):self.json_corrupt(lambda o:o["after_reset"]["cached_somas"].pop(), "hot_wrong_soma_dimension")
    def test_boolean_number(self):self.json_corrupt(lambda o:o["warm"]["physical_somas"].__setitem__(0, True), "hot_invalid_number")
    def test_changed_physics(self):self.json_corrupt(lambda o:o.update(effective_capacity=1e-9), "hot_individual_physics_changed")
    def test_inconsistent_total(self):self.json_corrupt(lambda o:o["after_reset"].update(physical_total=1.), "hot_inconsistent_physical_total")
    def test_changed_rest(self):
        def change(o):o["after_reset"]["physical_somas"][0] += 1.;o["after_reset"]["physical_total"] += 1.
        self.json_corrupt(change, "hot_physical_rest_changed")
    def test_invalid_number(self):self.csv_corrupt(lambda r:r[2].__setitem__(2,"broken"), "hot_invalid_number")
    def test_nonfinite_number(self):self.csv_corrupt(lambda r:r[2].__setitem__(2,"nan"), "hot_invalid_number")
    def test_wrong_clock(self):self.csv_corrupt(lambda r:r[2].__setitem__(0,r[1][0]), "hot_sample_clock")
    def test_truncated_grid(self):self.csv_corrupt(lambda r:r.pop(), "hot_incomplete_grid")
    def test_missing_stimulus(self):self.csv_corrupt(lambda r:[row.__setitem__(1,"0") for row in r[1:]], "hot_pulse_count")
    def test_live_readout_mismatch(self):self.csv_corrupt(lambda r:r[40].__setitem__(3,"1"), "hot_live_readout_mismatch")
    def test_flat_soma(self):
        self.csv_corrupt(lambda r:[row.__setitem__(i,"0") for row in r[1:] for i in range(2,len(row))], "hot_flat_soma_control")
    def test_promoted_native_status(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/"run";shutil.copytree(self.root, folder)
            p = folder/"validation.json";v = json.loads(p.read_text());v["execution"]["returncode"] = 99
            p.write_text(json.dumps(v))
            with self.assertRaisesRegex(EvidenceError, "hot_execution_disagreement"):audit_run(folder)


if __name__ == "__main__":unittest.main()
