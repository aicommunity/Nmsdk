"""Selection checks against a complete, actual inherited-property report cache."""
import copy
import json
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError
from ..probe_reports import _read_probe_data
from ..review_views import select_review_views


class ReviewViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ["TIMELEARNER_INHERITED_REPORT_CACHE"])
        manifest = json.loads((root/"manifest.json").read_text())
        cls.cases = []
        for i, group in enumerate(manifest["groups"]):
            name = group["trials"][0]["source_packet"]
            if not name.endswith("_inherited_activity_probe_2_evidence.json"):
                continue
            folder = root/f"group-{i:03d}"/"probe-0000"
            data = _read_probe_data(folder/"primary/probe.json", folder/"primary/trace.csv", True)
            probe = json.loads((folder/"manifest.json").read_text())
            cls.cases.append((name, probe["figures"][0]["views"], data[5]))
        if len(cls.cases) != 8:
            raise AssertionError("requires all8 actual topology/frequency/normalization cases")

    def test_all_actual_cases_select_pulse_and_first_response(self):
        for name, views, samples in self.cases:
            with self.subTest(case=name):
                selected = select_review_views(views, samples, 0)
                self.assertEqual([r["purpose"] for r in selected],
                                 ["overview", "first_actual_pulse", "first_response_excursion"])
                for row in selected[1:]:
                    self.assertLessEqual(row["view"]["begin"], row["anchor_time"])
                    self.assertGreaterEqual(row["view"]["end"], row["anchor_time"])
                pulse = selected[1]["view"]
                self.assertTrue(any(s["stimulus"] != 0 and pulse["begin"] <= s["time"] <= pulse["end"]
                                    for s in samples))
                if "_20000_" in name:
                    self.assertEqual(selected[2]["view"]["y_scale"], "local_detail")

    def test_old_first_zoom_is_blank_in_all_four_20000_hz_cases(self):
        bad = 0
        for name, views, samples in self.cases:
            if "_20000_" not in name:
                continue
            old = next(v for v in views if v["view"] == "zoom-001")
            self.assertFalse(any(s["stimulus"] != 0 and old["begin"] <= s["time"] <= old["end"]
                                 for s in samples))
            selected = select_review_views(views, samples, 0)
            self.assertNotEqual(selected[1]["view"]["view"], "zoom-001")
            bad += 1
        self.assertEqual(bad, 4)

    def test_missing_stimulus_does_not_invent_anchor(self):
        _, views, original = self.cases[0]
        samples = copy.deepcopy(original)
        for row in samples:
            row["stimulus"] = 0
        with self.assertRaisesRegex(EvidenceError, "review_actual_stimulus_missing"):
            select_review_views(views, samples, 0)

    def test_missing_or_duplicate_overview_is_rejected(self):
        _, views, samples = self.cases[0]
        for changed in ([v for v in views if v["view"] != "overview"], views+[views[0]]):
            with self.assertRaisesRegex(EvidenceError, "review_views_missing"):
                select_review_views(changed, samples, 0)

    def test_uncovered_anchor_is_rejected(self):
        _, views, samples = self.cases[0]
        bad = copy.deepcopy(views)
        for v in bad:
            if v["view"] != "overview":
                v["begin"] += 100; v["end"] += 100
        with self.assertRaisesRegex(EvidenceError, "review_anchor_not_covered"):
            select_review_views(bad, samples, 0)

    def test_nonfinite_soma_is_rejected(self):
        _, views, original = self.cases[0]
        samples = copy.deepcopy(original); samples[0]["soma"][0] = float("nan")
        with self.assertRaisesRegex(EvidenceError, "invalid_review_samples"):
            select_review_views(views, samples, 0)

    def test_unordered_samples_are_rejected(self):
        _, views, original = self.cases[0]
        samples = copy.deepcopy(original); samples[1]["time"] = samples[0]["time"]
        with self.assertRaisesRegex(EvidenceError, "unordered_review_samples"):
            select_review_views(views, samples, 0)
