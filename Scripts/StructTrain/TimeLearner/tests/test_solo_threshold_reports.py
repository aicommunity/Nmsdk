"""Validate plots against eight real native complete/interrupted Solo traces."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..native_evidence import EvidenceError, load
from ..solo_threshold_reports import render_solo_threshold_trace


class SoloThresholdReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native = os.environ.get("TIMELEARNER_SOLO_THRESHOLD_NATIVE")
        reports = os.environ.get("TIMELEARNER_SOLO_THRESHOLD_REPORTS")
        if not native or not reports:
            raise unittest.SkipTest("requires actual native Solo traces and rendered reports")
        cls.native, cls.reports = Path(native), Path(reports)
        cls.cases = sorted(cls.native.glob("*_solo_threshold_*.json"))
        if len(cls.cases) != 8:
            raise RuntimeError("requires all eight actual native controls")

    def test_every_recorded_soma_and_ltz_has_readable_input_overlay(self):
        from PIL import Image
        pairs = 0
        for source in self.cases:
            raw = load(source)
            folder = self.reports/source.stem
            m = load(folder/"manifest.json")
            self.assertEqual(load(folder/"source.json.gz"), raw)
            channels = len(raw["samples"][0]["soma"])
            self.assertEqual(m["soma_channels"], channels)
            self.assertEqual(m["samples"], len(raw["samples"]))
            self.assertEqual([(f["source"], f["channel"]) for f in m["figures"]],
                             [("soma", i) for i in range(channels)]+[("lt_potential", None)])
            self.assertEqual(m["clock_scope"], "complete_probe" if raw["complete"] else "recorded_segment_only")
            self.assertFalse(m["visual_acceptance_complete"])
            self.assertFalse(m["calibrated"])
            self.assertIsNone(m["evaluation_verdict"])
            for figure in m["figures"]:
                self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                for view in figure["views"]:
                    self.assertFalse(view["downsampling"])
                    if view["time_view"] != "overview":
                        self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                    png, svg, pdf = [folder/figure["directory"]/n for n in view["files"]]
                    with Image.open(png) as image:
                        self.assertEqual(image.size, (1920, 960))
                    text = svg.read_text()
                    self.assertIn("Actual shared input", text)
                    self.assertIn("LTZone.Potential" if figure["source"] == "lt_potential" else "Soma SumPotential", text)
                    self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
                pairs += 1
        self.assertEqual(pairs, 20)

    def test_backend_unavailable_does_not_create_partial_report(self):
        with tempfile.TemporaryDirectory(prefix="tl-solo-report-") as tmp:
            output = Path(tmp)/"must-not-exist"
            with patch("Scripts.StructTrain.TimeLearner.solo_threshold_reports.plotting_runtime",
                       side_effect=EvidenceError("unavailable_backend")):
                with self.assertRaisesRegex(EvidenceError, "unavailable_backend"):
                    render_solo_threshold_trace(self.cases[0], output)
            self.assertFalse(output.exists())
