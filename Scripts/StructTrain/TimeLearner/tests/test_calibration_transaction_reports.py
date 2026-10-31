"""Read actual all-grid soma/input reports; no simulator or synthetic traces."""
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import load
from ..recognition_metrics import load_evaluation, score_threshold_candidate


class NativeCalibrationTransactionReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_CALIBRATION_TRANSACTION_REPORT_DIR")
        if not root: raise unittest.SkipTest("requires actual all-grid native transaction reports")
        cls.cases = sorted(p for p in Path(root).iterdir() if p.is_dir() and (p/"manifest.json").exists())
        counts = {}
        for path in cls.cases:
            status = load(path/"manifest.json")["transaction_status"]
            counts[status] = counts.get(status, 0)+1
        if counts != {"calibrated": 2, "nonseparable": 2, "budget_exhausted": 2, "cancelled": 4, "recovery_required": 6}:
            raise RuntimeError("requires all sixteen Classic/Branch transaction/context reports")

    def test_complete_matrices_reproduce_metrics_and_lossless_primary(self):
        total = 0
        for path in self.cases:
            report = load(path/"primary/transaction.json.gz");manifest = load(path/"manifest.json")
            self.assertEqual(report["sha256"], manifest["source_transaction_sha256"])
            self.assertFalse(manifest["calibration_claim"])
            self.assertFalse(manifest["source_primary_checked"])
            self.assertFalse(manifest["visual_acceptance_complete"])
            self.assertIsNone(manifest["evaluation_verdict"])
            expected = len(report["candidates"])+(report["status"] == "calibrated")
            self.assertEqual(manifest["completed_matrices"], expected)
            for item in manifest["matrices"]:
                folder = path/item["name"]
                spec, observations = load_evaluation(folder/"primary/evaluation.json")
                package = load(folder/"primary/model.json")
                self.assertEqual(score_threshold_candidate(spec, observations, package), load(folder/"analysis.json"))
                matrix = report["confirmation"] if item["name"] == "fresh-confirmation" else report["candidates"][int(item["name"].split("-")[1])]["matrix"]
                self.assertEqual(observations, matrix["observations"])
                total += 1
        self.assertEqual(total, 10)

    def test_every_pattern_and_soma_has_readable_full_native_input_overlay(self):
        from PIL import Image
        total = 0
        for path in self.cases:
            outer = load(path/"manifest.json")
            for item in outer["matrices"]:
                folder = path/item["name"];manifest = load(folder/"manifest.json")
                count = 1 if path.name.startswith("Branch") else 2
                figures = manifest["figures"]
                self.assertEqual({(f["presentation_index"], f["descriptor"]["index"]) for f in figures},
                                 {(i, j) for i in range(2) for j in range(count)})
                total += len(figures)
                for figure in figures:
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, pdf = (folder/p for p in view["files"])
                        with Image.open(png) as im: self.assertEqual(im.size, (1920, 960))
                        self.assertIn("Actual shared input", svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
        self.assertEqual(total, 30)

    def test_every_file_matches_complete_cache_checksum_manifest(self):
        for path in self.cases:
            sums = load(path/"SHA256SUMS.json")
            self.assertEqual({p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()},
                             set(sums)|{"SHA256SUMS.json"})
            for name, digest in sums.items():
                self.assertEqual(hashlib.sha256((path/name).read_bytes()).hexdigest(), digest)

    def test_incomplete_probes_do_not_invent_complete_response_plots(self):
        for path in self.cases:
            manifest = load(path/"manifest.json")
            if manifest["transaction_status"] not in {"cancelled", "recovery_required"}: continue
            self.assertEqual(manifest["completed_matrices"], 0)
            self.assertEqual(manifest["trial_soma_pairs"], 0)
            self.assertFalse(manifest["incomplete_matrix_plotted_as_complete"])
            self.assertIn("No completed matrix", (path/"index.html").read_text())

    def test_cli_rejects_corrupt_selection_before_creating_output(self):
        from ..__main__ import main
        path = next(p for p in self.cases if load(p/"manifest.json")["transaction_status"] == "calibrated")
        value = copy.deepcopy(load(path/"primary/transaction.json.gz"));value["selected_index"] = 0
        value.pop("sha256");value["sha256"] = sha(value)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);source = root/"bad.json";output = root/"report"
            source.write_text(json.dumps(value))
            with contextlib.redirect_stderr(io.StringIO()):
                status = main(["report", str(source), "--format", "calibration-transaction", "--output", str(output)])
            self.assertEqual(status, 2)
            self.assertFalse(output.exists())
