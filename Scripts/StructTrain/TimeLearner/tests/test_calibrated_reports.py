"""Read actual frozen calibrated-model reports, raw data and every plotted view."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recognition_metrics import load_evaluation, score_recognition_evaluation


class CalibratedReportEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_CALIBRATED_REPORT_DIR")
        if not value: raise unittest.SkipTest("requires actual Classic/Branch calibrated frozen reports")
        cls.cases = sorted(p for p in Path(value).iterdir() if p.is_dir() and (p/"manifest.json").exists())
        if {p.name for p in cls.cases} != {"Classic", "Branch"}:
            raise RuntimeError("requires both complete reports")

    def test_metrics_reproduce_from_portable_primary_data(self):
        for path in self.cases:
            spec, observations = load_evaluation(path/"primary/evaluation.json")
            result = score_recognition_evaluation(spec, observations, load(path/"primary/model.json"))
            self.assertEqual(result, load(path/"analysis.json"))
            self.assertTrue(result["calibration_evidence_checked"])
            self.assertIsNone(result["evaluation_verdict"])
            manifest = load(path/"manifest.json")
            self.assertFalse(manifest["calibration_claim"])
            self.assertTrue(manifest["source_calibration_evidence_checked"])
            self.assertFalse(manifest["visual_acceptance_complete"])

    def test_all_trial_soma_pairs_have_readable_full_native_tick_views(self):
        from PIL import Image
        for path in self.cases:
            manifest = load(path/"manifest.json");figures = manifest["figures"]
            count = 1 if path.name == "Branch" else 2
            self.assertEqual(len(figures), 4*count)
            self.assertEqual({(f["presentation_index"], f["descriptor"]["index"]) for f in figures},
                             {(i, j) for i in range(4) for j in range(count)})
            for figure in figures:
                self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                for view in figure["views"]:
                    self.assertFalse(view["downsampling"])
                    if view["time_view"] != "overview":
                        self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                    png, svg, pdf = (path/name for name in view["files"])
                    with Image.open(png) as image: self.assertEqual(image.size, (1920, 960))
                    self.assertIn("<svg", svg.read_text())
                    self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))

    def test_every_saved_file_matches_report_checksum_manifest(self):
        for path in self.cases:
            sums = load(path/"SHA256SUMS.json")
            self.assertEqual({p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()},
                             set(sums)|{"SHA256SUMS.json"})
            for name, digest in sums.items():
                self.assertEqual(hashlib.sha256((path/name).read_bytes()).hexdigest(), digest)
