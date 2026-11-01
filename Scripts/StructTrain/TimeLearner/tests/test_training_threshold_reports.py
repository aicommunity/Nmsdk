"""Readable positive LTZ crossing, preserving actual full-recovery primary data."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load


class TrainingThresholdReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native = os.environ.get("TIMELEARNER_TRAINING_THRESHOLD_NATIVE")
        reports = os.environ.get("TIMELEARNER_TRAINING_THRESHOLD_REPORTS")
        if not native or not reports:
            raise unittest.SkipTest("requires actual selected-threshold Solo records and reports")
        cls.native, cls.reports = Path(native), Path(reports)
        cls.sources = sorted((cls.native/"threshold-references").glob("*-confirmation.json"))
        if len(cls.sources) != 2:
            raise RuntimeError("requires both actual topology confirmations")

    def test_every_channel_preserves_all_primary_samples(self):
        pairs = 0
        for path in self.sources:
            folder = self.reports/path.name.removesuffix("-confirmation.json")
            raw, m = load(path), load(folder/"manifest.json")
            self.assertEqual(load(folder/"source.json.gz"), raw)
            channels = len(raw["samples"][0]["soma"])
            self.assertEqual([(f["source"], f["channel"]) for f in m["figures"]],
                             [("soma", i) for i in range(channels)]+[("lt_potential", None)])
            self.assertEqual(m["samples"], len(raw["samples"]))
            self.assertFalse(m["calibrated"])
            self.assertIsNone(m["evaluation_verdict"])
            pairs += len(m["figures"])
        self.assertEqual(pairs, 5)

    def test_threshold_detail_has_actual_level_and_readable_native_ticks(self):
        from PIL import Image
        for path in self.sources:
            folder = self.reports/path.name.removesuffix("-confirmation.json")
            raw, m = load(path), load(folder/"manifest.json")
            views = next(f["views"] for f in m["figures"] if f["source"] == "lt_potential")
            potential = [s["lt_potential"] for s in raw["samples"]]
            self.assertLess(min(potential), 0)
            self.assertGreater(max(potential), 0)
            full = next(v for v in views if v["view"] == "overview")
            self.assertLessEqual(full["y_limits"][0], min(potential))
            details = [v for v in views if v["y_scale"] == "positive_threshold_detail"]
            self.assertTrue(details)
            self.assertTrue(any(v["time_view"] != "overview" for v in details))
            for view in details:
                self.assertEqual(view["reference_level"], raw["source"]["threshold"])
                self.assertLessEqual(view["y_limits"][0], 0)
                self.assertGreater(view["y_limits"][0], min(potential)/10)
                self.assertGreaterEqual(view["y_limits"][1], max(max(potential), raw["source"]["threshold"]))
                self.assertFalse(view["downsampling"])
                if view["time_view"] != "overview":
                    self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                png, svg, pdf = [folder/"ltzone"/p for p in view["files"]]
                with Image.open(png) as image:
                    self.assertEqual(image.size, (1920, 960))
                text = svg.read_text()
                for label in ("Actual scalar spike threshold", "Actual shared input", "positive threshold detail"):
                    self.assertIn(label, text)
                self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
