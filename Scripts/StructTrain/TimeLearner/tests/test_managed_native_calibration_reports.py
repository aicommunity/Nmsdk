"""Public reports for every measured candidate, confirmation and frozen trial."""
import contextlib
import hashlib
import io
import os
from pathlib import Path
import unittest

from ..__main__ import main
from ..native_evidence import load
from ..recognition_metrics import load_evaluation


class ManagedNativeCalibrationReportsTest(unittest.TestCase):
    def test_every_declared_matrix_and_soma_has_full_sample_input_overlays(self):
        source = os.environ.get("TIMELEARNER_MANAGED_CALIBRATION_PRIMARY")
        output = os.environ.get("TIMELEARNER_MANAGED_CALIBRATION_REPORTS")
        if not source or not output:
            self.skipTest("requires actual completed managed calibration runs and a new report cache")
        from PIL import Image
        source, output = Path(source), Path(output)
        output.mkdir(parents=True, exist_ok=False)
        matrix_pairs = frozen_pairs = declared_matrix_pairs = declared_frozen_pairs = 0

        def check_matrix(folder, expected):
            manifest = load(folder/"manifest.json")
            spec, observations = load_evaluation(folder/"primary/evaluation.json")
            self.assertEqual(len(spec["trials"]), 4)
            self.assertEqual(observations, expected)
            pairs = {(o["trial_id"], i) for o in expected
                     for i in range(len(o["samples"][0]["soma"]))}
            self.assertEqual({(f["trial_id"], f["descriptor"]["index"])
                              for f in manifest["figures"]}, pairs)
            for figure in manifest["figures"]:
                self.assertTrue(any(v["time_view"] == "overview" for v in figure["views"]))
                self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                for view in figure["views"]:
                    self.assertFalse(view["downsampling"])
                    if view["time_view"] != "overview":
                        self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                    png, svg, pdf = (folder/p for p in view["files"])
                    with Image.open(png) as image:
                        self.assertEqual(image.size, (1920, 960))
                    self.assertIn("Actual shared input", svg.read_text())
                    self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            return len(pairs)

        for name in ("Classic-v1", "Classic-v2", "Branch-v1", "Branch-v2"):
            result = load(source/name/"result.json")
            phases = ("measured-grid", "silent-nonseparable", "fresh-frozen")
            if "changed_threshold_rollback" in result:
                phases += ("rollback-frozen",)
            self.assertEqual({p["operation"] for p in result["phases"]}, set(phases))
            self.assertEqual({p.name for p in (source/name/"runs").iterdir() if p.is_dir()}, set(phases))
            for phase in phases:
                run = source/name/"runs"/phase
                report = output/name/phase
                run_manifest = load(run/"run-manifest.json")
                source_model = load(run/run_manifest["source_package_path"])["configuration"]["model"]
                channels = 1 if source_model["branch"] else len(source_model["inputs"])
                job = load(run/"input/job.json")
                frozen = phase in ("fresh-frozen", "rollback-frozen")
                fmt = "pipeline-run" if frozen else "calibration-run"
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
                    code = main(["report", str(run/"run-manifest.json"), "--format", fmt,
                                 "--output", str(report)])
                self.assertEqual(code, 0, stdout.getvalue())
                if frozen:
                    _, actual = load_evaluation(run/"native/evaluation.json")
                    frozen_pairs += check_matrix(report/"evaluation", actual)
                    declared_frozen_pairs += len(job["trials"])*channels
                else:
                    transaction = load(run/"native/transaction.json")
                    self.assertEqual(len(transaction["candidates"]), len(job["thresholds"]))
                    manifest = load(report/"manifest.json")
                    expected = {f"candidate-{i:04d}": r["matrix"]["observations"]
                                for i, r in enumerate(transaction["candidates"])}
                    if transaction["status"] in ("calibrated", "confirmation_failed"):
                        expected["fresh-confirmation"] = transaction["confirmation"]["observations"]
                    declared_matrix_pairs += len(expected)*len(job["trials"])*channels
                    self.assertEqual({r["name"] for r in manifest["matrices"]}, set(expected))
                    for item in manifest["matrices"]:
                        matrix_pairs += check_matrix(report/item["name"], expected[item["name"]])
                    binding = load(report/"run-binding.json")
                    self.assertTrue(binding["source_primary_checked"])
                    self.assertTrue(binding["run_audit"]["run_evidence_consistent"])
                for path, digest in load(report/"SHA256SUMS.json").items():
                    self.assertEqual(hashlib.sha256((report/path).read_bytes()).hexdigest(), digest)
        self.assertEqual(frozen_pairs, declared_frozen_pairs)
        self.assertGreater(declared_frozen_pairs, 0)
        self.assertEqual(matrix_pairs, declared_matrix_pairs)
