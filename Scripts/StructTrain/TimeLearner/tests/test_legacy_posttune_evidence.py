"""Audit actual legacy free-run primaries; corruption never becomes calibration proof."""
import csv
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..legacy_posttune_evidence import audit_free_run
from ..native_evidence import EvidenceError, load


class LegacyPostTunePhysicalEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_LEGACY_POSTTUNE_FREERUN_DIR")
        if not directory:
            raise unittest.SkipTest("requires four actual legacy inference native free-run cases")
        cls.paths = sorted(Path(directory).glob("*_posttune_inference_physical.json"))
        if len(cls.paths) != 4:
            raise AssertionError("expected exactly Classic/Branch x 2000/20000 physical cases")
        if {(load(p)["topology"],load(p)["frequency_hz"]) for p in cls.paths} != {
                (top,f) for top in ("classic","branch") for f in (2000,20000)}:
            raise AssertionError("incomplete actual topology/frequency matrix")

    def test_four_actual_traces_remain_diagnostics(self):
        for p in self.paths:
            result = audit_free_run(p, p.with_suffix(".csv"))
            self.assertTrue(result["primary_data_consistent"])
            self.assertEqual(result["observed_input_pulses"], 4)
            self.assertFalse(result["calibration_validated"])
            self.assertFalse(result["physical_settling_verified"])
            self.assertIsNone(result["scientific_verdict"])

    def test_missing_native_sample_is_rejected(self):
        for p in self.paths:
            rows = p.with_suffix(".csv").read_text().splitlines();rows.pop(len(rows)//2)
            with tempfile.TemporaryDirectory() as temporary:
                trace = Path(temporary)/"trace.csv";trace.write_text("\n".join(rows)+"\n")
                with self.assertRaises(EvidenceError):audit_free_run(p, trace)

    def test_unknown_foil_state_cannot_reuse_valid_summary(self):
        for p in self.paths:
            packet = load(p);packet["states"][1]["observed"] = False
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary)/"run.json";path.write_text(json.dumps(packet)+"\n")
                with self.assertRaisesRegex(EvidenceError, "incomplete_sample_states"):
                    audit_free_run(path, p.with_suffix(".csv"))

    def test_changed_actual_onset_list_is_rejected(self):
        for p in self.paths:
            packet = load(p);packet["stimulus_times"].pop()
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary)/"run.json";path.write_text(json.dumps(packet)+"\n")
                with self.assertRaisesRegex(EvidenceError, "incomplete_primary_trace"):
                    audit_free_run(path, p.with_suffix(".csv"))

    def test_selected_metric_must_match_actual_somas(self):
        for p in self.paths:
            with p.with_suffix(".csv").open(newline="") as stream:rows = list(csv.reader(stream))
            rows[1][-1] = str(float(rows[1][-1])+.125)
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary)/"trace.csv"
                with path.open("w", newline="") as stream:csv.writer(stream).writerows(rows)
                with self.assertRaisesRegex(EvidenceError, "selected_metric_changed"):audit_free_run(p, path)

    def test_all_physical_patterns_and_somas_are_rendered(self):
        output = os.environ.get("TIMELEARNER_LEGACY_POSTTUNE_REPORT_OUTPUT")
        if not output:
            self.skipTest("requires a new persistent all-pattern visual report directory")
        from ..legacy_posttune_reports import render_free_run
        out = Path(output);out.mkdir(exist_ok=False);channels = 0
        for p in self.paths:
            report = out/p.stem
            result = render_free_run(p, p.with_suffix(".csv"), report);channels += result["soma_channels"]
            m = load(report/"manifest.json")
            self.assertEqual(len(m["figures"]), m["soma_channels"])
            self.assertEqual(m["sample_labels"], ["target", "foil"])
            self.assertFalse(m["visual_acceptance_complete"])
            self.assertFalse(m["physical_settling_verified"])
            for figure in m["figures"]:
                self.assertTrue(any(v["view"] == "overview" for v in figure["views"]))
                zooms = [v for v in figure["views"] if v["time_view"] != "overview"]
                self.assertTrue(zooms)
                self.assertTrue(all(v["downsampling"] is False and v["minimum_native_tick_pixels_on_zoom"] >= 8 for v in zooms))
        self.assertEqual(channels, 6)
