"""Full physical baseline/correction temporal caches, not selected-image coverage."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..finite_ranking_evidence import load_case, audit_finite_timing_ranking


class FiniteRankingReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        keys = ("TIMELEARNER_FINITE_RANK_REPORT_INPUTS", "TIMELEARNER_FINITE_RANK_REPORT_DIR")
        if not all(os.environ.get(k) for k in keys):
            raise unittest.SkipTest("requires actual complete baseline/correction temporal cache")
        cls.inputs, cls.root = (Path(os.environ[k]) for k in keys)
        cls.manifest = load(cls.root/"manifest.json")
        if len(cls.manifest["cases"]) != 8:
            raise AssertionError("requires four physical cases in each phase")

    def test_every_declared_probe_and_every_soma_preserved(self):
        total = pairs = 0
        for case in self.manifest["cases"]:
            native = self.inputs/case["source_native"]
            source = load_case(native, case["prefix"])
            audited = audit_finite_timing_ranking(*source)
            self.assertEqual(audited, case["primary_audit"])
            folder = self.root/case["report"];manifest = load(folder/"manifest.json")
            expected = source[0]["observed_packets"]
            self.assertEqual([r["trial_id"] for r in manifest["reports"]],
                             [p["requested_specification"]["trial_id"] for p in expected])
            for entry, packet in zip(manifest["reports"], expected):
                directory = folder/entry["folder"];trial = entry["trial_id"]
                self.assertEqual(load(directory/"primary/probe.json"), packet)
                self.assertEqual((directory/"primary/trace.csv").read_bytes(), source[3][trial].read_bytes())
                item = load(directory/"manifest.json")
                count = len(packet["observation"]["specification"]["baseline"])
                self.assertEqual({f["channel"] for f in item["figures"]}, set(range(count)))
                self.assertIsNone(item["scientific_verdict"])
                for figure in item["figures"]:
                    for view in figure["views"]:
                        if view["y_scale"] == "shared":
                            self.assertEqual(view["y_limits"], manifest["common_y_limits"][figure["channel"]])
                pairs += count;total += 1
        self.assertEqual(total, self.manifest["trials"])
        self.assertEqual(pairs, self.manifest["trial_soma_pairs"])

    def test_all_files_and_readable_input_overlays_without_downsampling(self):
        from PIL import Image
        for case in self.manifest["cases"]:
            folder = self.root/case["report"]
            for name, digest in load(folder/"SHA256SUMS.json").items():
                self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(), digest)
            for entry in load(folder/"manifest.json")["reports"]:
                directory = folder/entry["folder"]
                for figure in load(directory/"manifest.json")["figures"]:
                    self.assertTrue(any(v["time_view"] != "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        png, svg, pdf = (directory/p for p in view["files"])
                        with Image.open(png) as image:self.assertEqual(image.size, (1920, 960))
                        self.assertIn("Actual shared input", svg.read_text())
                        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))

    def test_negative_training_is_not_promoted_by_a_better_rank(self):
        for case in self.manifest["cases"]:
            audit = case["primary_audit"]
            self.assertIs(audit["selected_is_measured_minimum"], case["phase"] == "correction")
            self.assertFalse(audit["training_completed"])
            self.assertFalse(audit["certificate_present"])
            self.assertIsNone(audit["evaluation_verdict"])
        self.assertFalse(self.manifest["visual_acceptance_complete"])
        self.assertIsNone(self.manifest["scientific_verdict"])
