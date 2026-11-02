"""Actual stopped-Train responses: readable plots and explicit missing trials."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recognition_metrics import load_partial_diagnostic_evaluation, score_partial_diagnostic_evaluation
from ..stopped_evidence import load_case


class DiagnosticPipelineReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        keys = ("TIMELEARNER_DIAGNOSTIC_PIPELINE_DIR", "TIMELEARNER_DIAGNOSTIC_PIPELINE_REPORTS")
        if not all(os.environ.get(k) for k in keys):
            raise unittest.SkipTest("requires actual public diagnostic responses and report cache")
        cls.source, cls.reports = (Path(os.environ[k]) for k in keys)

    def cases(self):
        for topology in ("Classic", "Branch"):
            for status in ("completed", "interrupted"):
                name = topology+"-"+status
                yield self.source/"runs"/name, self.reports/name

    def test_every_primary_sample_and_missing_trial_preserved(self):
        for source, report in self.cases():
            native = source/"native";rendered = report/"evaluation"
            spec, observations, missing = load_partial_diagnostic_evaluation(native/"evaluation.json")
            copied, actual, absent = load_partial_diagnostic_evaluation(rendered/"primary/evaluation.json")
            self.assertEqual(actual, observations)
            self.assertEqual(absent, missing)
            self.assertEqual(len(copied["trials"]), len(spec["trials"]))
            self.assertEqual(load(rendered/"primary/model.json"), load(native/"model.json"))
            case = load_case(rendered/"primary/stopped-source/train_stopped_state.json")
            score = score_partial_diagnostic_evaluation(copied, actual, load(native/"model.json"), case)
            self.assertEqual(score, load(rendered/"analysis.json"))
            manifest = load(rendered/"manifest.json")
            self.assertEqual(manifest["missing_observation_ids"], missing)
            self.assertEqual(len(manifest["declared_trials"]), 4)
            if missing:
                self.assertEqual(score["validity"], "invalid")
                self.assertIsNone(score["pooled_counts"])

    def test_actual_soma_input_overlays_readable_scale_and_all_observed_channels(self):
        from PIL import Image
        for source, report in self.cases():
            _, observations, _ = load_partial_diagnostic_evaluation(source/"native/evaluation.json")
            folder = report/"evaluation";manifest = load(folder/"manifest.json")
            expected = {(o["trial_id"], i) for o in observations if o["samples"]
                        for i in range(len(o["samples"][0]["soma"]))}
            self.assertEqual({(f["trial_id"], f["descriptor"]["index"]) for f in manifest["figures"]}, expected)
            for figure in manifest["figures"]:
                for view in figure["views"]:
                    self.assertFalse(view["downsampling"])
                    if view["time_view"] != "overview":
                        self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                    png, svg, pdf = (folder/p for p in view["files"])
                    with Image.open(png) as image:self.assertEqual(image.size, (1920, 960))
                    self.assertIn("Actual shared input", svg.read_text())
                    self.assertIn("Stopped Train: external_stop", svg.read_text())
                    self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))

    def test_all_cache_hashes_and_unfinished_role(self):
        for _, report in self.cases():
            for folder in (report, report/"evaluation"):
                for name, digest in load(folder/"SHA256SUMS.json").items():
                    self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(), digest)
                manifest = load(folder/"manifest.json")
                self.assertTrue(manifest["diagnostic_only"])
                self.assertFalse(manifest["training_completed"])
                self.assertFalse(manifest["visual_acceptance_complete"])
            self.assertIsNone(load(report/"manifest.json")["scientific_verdict"])
