"""Verify actual separate-threshold visual reports and every native soma trace."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recognition_metrics import load_evaluation


class PostTuneProbeThresholdReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_PROBE_THRESHOLD_REPORTS")
        if not directory:
            raise unittest.SkipTest("requires all eight actual native visual reports")
        cls.cases = sorted(p.parent for p in Path(directory).glob("*/manifest.json")
                           if load(p).get("kind") == "timelearner_posttune_transaction_visual_report")
        if len(cls.cases) != 8:
            raise RuntimeError("requires eight separate-threshold final-boundary reports")

    def test_measurement_and_final_physics_are_separate_and_bound(self):
        for path in self.cases:
            outer = load(path/"manifest.json")
            raw = load(path/"primary/transaction.json.gz")
            self.assertEqual(raw["schema_version"], 3)
            self.assertEqual(outer["source_transaction_sha256"], raw["sha256"])
            self.assertFalse(outer["visual_acceptance_complete"])
            self.assertFalse(outer["recognition_success_confirmed"])
            self.assertIsNone(outer["evaluation_verdict"])
            self.assertEqual(len(outer["weight_matrices"]), 1)
            self.assertEqual(len(outer["final_model_matrices"]), int(raw["status"] == "weights_selected"))
            for item in outer["weight_matrices"]+outer["final_model_matrices"]:
                model = load(path/item["name"]/"primary/model.json")
                final = item["role"] == "final_model_responses"
                self.assertEqual(model, raw["selected_package"] if final else raw["weight_measurement_candidates"][0])
                self.assertEqual(model["neuron"]["metadata"]["calibration"]["threshold"], 1. if final else 2.)
                spec, observations = load_evaluation(path/item["name"]/"primary/evaluation.json")
                source = raw["final_model_matrix"] if final else raw["candidates"][0]["matrix"]
                by_id = {o["trial_id"]: o for o in source["observations"]}
                self.assertEqual(observations, [by_id[q["trial_id"]] for q in spec["trials"]])
                self.assertEqual(item["model_revision"], model["model_revision"])
            self.assertIn("fresh final-model responses", (path/"index.html").read_text())

    def test_every_pattern_soma_and_detail_view_has_native_input_overlay(self):
        from PIL import Image
        total = 0
        for path in self.cases:
            outer = load(path/"manifest.json")
            pairs = 0
            for item in outer["weight_matrices"]+outer["final_model_matrices"]:
                folder = path/item["name"]
                spec, observations = load_evaluation(folder/"primary/evaluation.json")
                manifest = load(folder/"manifest.json")
                count = len(observations[0]["samples"][0]["soma"])
                self.assertEqual({(f["trial_id"], f["descriptor"]["index"]) for f in manifest["figures"]},
                                 {(q["trial_id"], i) for q in spec["trials"] for i in range(count)})
                for figure in manifest["figures"]:
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, pdf = (folder/name for name in view["files"])
                        with Image.open(png) as image:
                            self.assertEqual(image.size, (1920, 960))
                        self.assertIn("Actual shared input", svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
                pairs += len(manifest["figures"])
            self.assertEqual(pairs, outer["trial_soma_pairs"])
            self.assertEqual(pairs, outer["weight_trial_soma_pairs"]+outer["final_model_trial_soma_pairs"])
            total += pairs
        self.assertGreater(total, 0)
