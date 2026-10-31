"""Complete native boundary replay plots and failure-before-output controls."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..finalization_boundary_reports import render_boundary_replay
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_evaluation


class FinalizationBoundaryReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_FINALIZATION_BOUNDARY_REPORTS")
        native = os.environ.get("TIMELEARNER_FINALIZATION_BOUNDARY_NATIVE")
        jobs = os.environ.get("TIMELEARNER_POSTTUNE_FIXED_SOURCE")
        if not all((directory, native, jobs)):
            raise unittest.SkipTest("requires actual native replay plots and immutable source fixtures")
        cls.root, cls.native, cls.jobs = Path(directory), Path(native), Path(jobs)
        cls.cases = sorted(p.parent for p in cls.root.glob("*/manifest.json")
                           if load(p)["kind"] == "native_finalization_boundary_visual_report")
        if len(cls.cases) != 4:
            raise RuntimeError("requires Classic/Branch plain and connected replay reports")

    def test_all_patterns_channels_samples_and_readable_overlays(self):
        from PIL import Image
        pairs = 0
        for folder in self.cases:
            outer = load(folder/"manifest.json")
            self.assertFalse(outer["visual_acceptance_complete"])
            self.assertFalse(outer["configured_phase_dispatch_implemented"])
            self.assertIsNone(outer["scientific_verdict"])
            raw = load(self.native/(folder.name+"_replay.json"))
            spec, observations = load_evaluation(folder/"evaluation/primary/evaluation.json")
            self.assertEqual(observations, raw["observations"])
            self.assertEqual({o["label"] for o in observations}, {"target", "foil"})
            channels = 1 if folder.name.startswith("Branch") else 2
            figures = load(folder/"evaluation/manifest.json")["figures"]
            self.assertEqual({(f["trial_id"], f["descriptor"]["index"]) for f in figures},
                             {(q["trial_id"], i) for q in spec["trials"] for i in range(channels)})
            for figure in figures:
                self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                for view in figure["views"]:
                    self.assertFalse(view["downsampling"])
                    if view["time_view"] != "overview":
                        self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                    png, svg, pdf = (folder/"evaluation"/name for name in view["files"])
                    with Image.open(png) as image:
                        self.assertEqual(image.size, (1920, 960))
                    self.assertIn("Actual shared input", svg.read_text())
                    self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            pairs += len(figures)
        self.assertEqual(pairs, 12)

    def test_incomplete_record_rejects_before_output(self):
        name = "Classic_finalization_boundary_0"
        with tempfile.TemporaryDirectory(prefix="tl-boundary-report-") as temporary:
            root = Path(temporary)
            raw = load(self.native/(name+"_replay.json"))
            raw["observations"][0]["complete"] = False
            source = root/(name+"_replay.json")
            source.write_text(json.dumps(raw))
            # Output must be outside the derivative primary directory as well.
            output = root.parent/(root.name+"-must-not-exist")
            with self.assertRaises(EvidenceError):
                render_boundary_replay(source, self.native/(name+"_capture-comparison.json"),
                                       self.jobs/"Classic-auto_metric/input/job.json", output)
            self.assertFalse(output.exists())

    def test_backend_failure_rejects_before_output(self):
        name = "Classic_finalization_boundary_0"
        with tempfile.TemporaryDirectory(prefix="tl-boundary-backend-") as temporary:
            output = Path(temporary)/"must-not-exist"
            with patch("Scripts.StructTrain.TimeLearner.finalization_boundary_reports.plotting_runtime",
                       side_effect=EvidenceError("unavailable_backend")):
                with self.assertRaisesRegex(EvidenceError, "unavailable_backend"):
                    render_boundary_replay(self.native/(name+"_replay.json"),
                        self.native/(name+"_capture-comparison.json"),
                        self.jobs/"Classic-auto_metric/input/job.json", output)
            self.assertFalse(output.exists())
