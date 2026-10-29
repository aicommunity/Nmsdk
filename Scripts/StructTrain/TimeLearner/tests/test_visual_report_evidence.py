"""Read back actual production reports; no copied renderer implementation."""
import hashlib
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.native_evidence import load
from Scripts.StructTrain.TimeLearner.recognition_metrics import load_evaluation, score_recognition_evaluation


class VisualReportEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_VISUAL_REPORT_DIR")
        if not root:
            raise unittest.SkipTest("requires production reports rendered from actual native observations")
        cls.cases = sorted(p for p in Path(root).iterdir() if p.is_dir() and (p/"manifest.json").exists())
        if len(cls.cases) != 4:
            raise RuntimeError("requires Classic/Branch high/low threshold reports")

    def test_portable_primary_data_reproduce_metrics(self):
        for case in self.cases:
            spec, observations = load_evaluation(case/"primary/evaluation.json")
            actual = score_recognition_evaluation(spec, observations, load(case/"primary/model.json"))
            self.assertEqual(actual, load(case/"analysis.json"))
            self.assertEqual(actual["validity"], "valid")
            self.assertIsNone(actual["evaluation_verdict"])

    def test_complete_trial_soma_coverage_and_all_files_hashes(self):
        for case in self.cases:
            manifest = load(case/"manifest.json")
            figures = manifest["figures"]
            count = 1 if case.name.startswith("Branch") else 2
            self.assertEqual({(f["presentation_index"], f["descriptor"]["index"]) for f in figures},
                             {(trial, soma) for trial in range(4) for soma in range(count)})
            self.assertEqual(len(figures), manifest["expected_trial_soma_pairs"])
            for name, sha in load(case/"SHA256SUMS.json").items():
                self.assertEqual(hashlib.sha256((case/name).read_bytes()).hexdigest(), sha)

    def test_actual_png_dimensions_vector_export_and_time_resolution(self):
        from PIL import Image
        for case in self.cases:
            for figure in load(case/"manifest.json")["figures"]:
                for view in figure["views"]:
                    png, svg, pdf = (case/p for p in view["files"])
                    with Image.open(png) as image:
                        self.assertEqual(image.size, (1920, 960))
                    self.assertIn("<svg", svg.read_text())
                    self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
                    if view["view"] != "overview":
                        self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        self.assertLessEqual(view["end"]-view["begin"], .050000001)

    def test_unverified_units_and_visual_acceptance_are_not_promoted(self):
        for case in self.cases:
            manifest = load(case/"manifest.json")
            self.assertEqual(manifest["status"], "diagnostic")
            self.assertFalse(manifest["visual_acceptance_complete"])
            self.assertTrue(manifest["limitations"])
            for figure in manifest["figures"]:
                self.assertEqual(figure["descriptor"]["units"], "model_units_SI_unverified")
