"""Read back a real production candidate report; every plotted sample is primary."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recognition_metrics import load_evaluation, score_threshold_candidate


class ThresholdCandidateReportEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_THRESHOLD_CANDIDATE_REPORT_DIR")
        if not value:
            raise unittest.SkipTest("requires an actual rendered native threshold candidate report")
        cls.root = Path(value)

    def test_primary_data_reproduce_candidate_metrics_without_calibration_claim(self):
        spec, observations = load_evaluation(self.root/"primary/evaluation.json")
        package = load(self.root/"primary/model.json")
        self.assertEqual(score_threshold_candidate(spec, observations, package), load(self.root/"analysis.json"))
        manifest = load(self.root/"manifest.json")
        self.assertEqual(manifest["purpose"], "threshold_candidate_diagnostic")
        self.assertFalse(manifest["calibration_claim"])
        self.assertFalse(manifest["visual_acceptance_complete"])
        self.assertIsNone(manifest["evaluation_verdict"])

    def test_all_expected_soma_trials_have_readable_native_tick_views(self):
        from PIL import Image
        spec, _ = load_evaluation(self.root/"primary/evaluation.json")
        package = load(self.root/"primary/model.json")
        context = package["source_recognition"]
        count = 1 if context["source_solo"]["configuration"]["model"]["branch"] else len(context["recognition_inputs"])
        manifest = load(self.root/"manifest.json")
        figures = manifest["figures"]
        self.assertEqual({(f["presentation_index"], f["descriptor"]["index"]) for f in figures},
                         {(i, j) for i in range(len(spec["trials"])) for j in range(count)})
        self.assertEqual(len(figures), manifest["expected_trial_soma_pairs"])
        for figure in figures:
            self.assertTrue(any(v["view"] != "overview" for v in figure["views"]))
            for view in figure["views"]:
                png, svg, pdf = (self.root/name for name in view["files"])
                with Image.open(png) as image: self.assertEqual(image.size, (1920, 960))
                self.assertIn("<svg", svg.read_text())
                self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
                if view.get("time_view", view["view"]) != "overview":
                    self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)

    def test_all_report_files_match_saved_hashes(self):
        sums = load(self.root/"SHA256SUMS.json")
        actual = {p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(actual, set(sums)|{"SHA256SUMS.json"})
        for name, digest in sums.items():
            self.assertEqual(hashlib.sha256((self.root/name).read_bytes()).hexdigest(), digest)
