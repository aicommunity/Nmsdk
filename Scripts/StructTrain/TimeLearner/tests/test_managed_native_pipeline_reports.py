"""Every actual frozen pattern and soma from the managed cold pipelines."""
import hashlib
import os
from pathlib import Path
import unittest

from ..live_pipeline_reports import render_pipeline_run
from ..native_evidence import load
from ..recognition_metrics import load_evaluation


class ManagedNativePipelineReportsTest(unittest.TestCase):
    def test_actual_frozen_patterns_have_readable_full_sample_soma_input_reports(self):
        source = os.environ.get("TIMELEARNER_MANAGED_PIPELINE_PRIMARY")
        output = os.environ.get("TIMELEARNER_MANAGED_PIPELINE_REPORTS")
        if not source or not output:
            self.skipTest("requires real managed pipeline primary data and a new report cache")
        from PIL import Image
        source, output = Path(source), Path(output)
        output.mkdir(parents=True, exist_ok=False)
        pairs = 0
        for name in ("Classic-v1", "Classic-v2", "Branch-v1", "Branch-v2"):
            run = source/name/"runs/evaluate"
            before = hashlib.sha256((run/"run-manifest.json").read_bytes()).hexdigest()
            report = output/name
            render_pipeline_run(run/"run-manifest.json", report)
            self.assertEqual(hashlib.sha256((run/"run-manifest.json").read_bytes()).hexdigest(), before)
            manifest = load(report/"manifest.json")
            self.assertTrue(manifest["audit"]["run_evidence_consistent"])
            self.assertFalse(manifest["independent_partition_verified"])
            self.assertIsNone(manifest["scientific_verdict"])
            evaluation = report/"evaluation"
            plotted = load(evaluation/"manifest.json")
            _, observations = load_evaluation(run/"native/evaluation.json")
            declared = load(run/"input/job.json")["trials"]
            self.assertEqual(len(declared), 4)
            self.assertEqual({o["trial_id"] for o in observations}, {t["trial_id"] for t in declared})
            expected = {(o["trial_id"], i) for o in observations
                        for i in range(len(o["samples"][0]["soma"]))}
            self.assertEqual({(f["trial_id"], f["descriptor"]["index"])
                              for f in plotted["figures"]}, expected)
            pairs += len(expected)
            for figure in plotted["figures"]:
                self.assertTrue(any(v["time_view"] == "overview" for v in figure["views"]))
                self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                for view in figure["views"]:
                    self.assertFalse(view["downsampling"])
                    if view["time_view"] != "overview":
                        self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                    png, svg, pdf = (evaluation/p for p in view["files"])
                    with Image.open(png) as image:
                        self.assertEqual(image.size, (1920, 960))
                    self.assertIn("Actual shared input", svg.read_text())
                    self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            for root in (report, evaluation):
                for name, digest in load(root/"SHA256SUMS.json").items():
                    self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(), digest)
        self.assertEqual(pairs, 24)
