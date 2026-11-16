"""Independent primary replay and readable views of an actual stopped model."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..native_pipeline_worker import audit_run_manifest
from ..reports import render_diagnostic_evaluation


class RestoredFrozenDiagnosticReportTest(unittest.TestCase):
    def test_actual_restored_eight_patterns_keep_metrics_and_native_scale(self):
        from PIL import Image

        run = Path(os.environ["TIMELEARNER_RESTORED_FROZEN_RUN"]).resolve(strict=True)
        controls = Path(os.environ["TIMELEARNER_RESTORED_FROZEN_CONTROLS"]).resolve(strict=True)
        declaration = load(controls/"declaration.json")
        manifest = load(run/"run-manifest.json")
        audit = audit_run_manifest(run/"run-manifest.json")
        self.assertTrue(audit["run_evidence_consistent"])
        self.assertEqual(manifest["analysis"]["metrics"]["model_revision"],
                         declaration["model_revision"])
        output = Path(os.environ["TMPDIR"])/"restored-frozen-eight-pattern-gallery"
        render_diagnostic_evaluation(run/"native/evaluation.json", run/"native/model.json",
                                    run/"input/source/train_stopped_state.json", output)
        metrics, gallery = load(output/"analysis.json"), load(output/"manifest.json")
        self.assertEqual(metrics, manifest["analysis"]["metrics"])
        self.assertTrue(metrics["diagnostic_only"])
        self.assertFalse(metrics["training_completed"])
        self.assertEqual(metrics["effective_threshold"], declaration["threshold"])
        self.assertEqual(len(metrics["trials"]), 8)
        self.assertEqual(gallery["missing_observation_ids"], [])
        self.assertEqual(gallery["expected_trial_soma_pairs"], 8*declaration["somas"])
        self.assertEqual(len(gallery["figures"]), 8*declaration["somas"])
        self.assertTrue(all(t["complete"] for t in gallery["declared_trials"]))
        self.assertFalse(gallery["visual_acceptance_complete"])
        for figure in gallery["figures"]:
            self.assertTrue(any(v["time_view"] == "overview" for v in figure["views"]))
            self.assertTrue(any(v["time_view"] != "overview" and
                v["minimum_native_tick_pixels_on_zoom"] >= 8 for v in figure["views"]))
            for view in figure["views"]:
                self.assertFalse(view["downsampling"])
                with Image.open(output/view["files"][0]) as image:
                    self.assertEqual(image.size, (1920, 960))
