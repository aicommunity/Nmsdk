"""Render all real replay models/somas at native-tick resolution."""
import csv
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recognition_owner_replay_reports import render_replays


class RecognitionOwnerReplayReportsTest(unittest.TestCase):
    def test_all_declared_models_and_somas_have_full_sample_input_overlays(self):
        names = ("TIMELEARNER_MODELSPEC2_OWNER_SOURCE", "TIMELEARNER_MODELSPEC2_FRESH_OWNER_REPLAY",
                 "TIMELEARNER_MODELSPEC2_REPLAY_REPORT_CACHE")
        if not all(os.environ.get(n) for n in names):
            self.skipTest("requires real replay/source corpora and a new report cache")
        source, replay, output = (Path(os.environ[n]) for n in names)
        manifest = render_replays(source, replay, output)
        index = load(replay/"index.json")
        self.assertEqual({r["id"] for r in manifest["cases"]}, {r["id"] for r in index["cases"]})
        self.assertEqual(len(manifest["cases"]), 8)
        self.assertEqual(sum(r["soma_channels"] for r in manifest["cases"]), 12)
        self.assertFalse(manifest["visual_acceptance_complete"])
        self.assertFalse(manifest["primary_data_copied_into_report"])
        self.assertIsNone(manifest["scientific_verdict"])
        for row in manifest["cases"]:
            with (replay/row["id"]/"actual.json.csv").open(newline="") as stream:
                samples = list(csv.reader(stream))
            self.assertEqual(row["native_ticks"], len(samples)-1)
            self.assertEqual(len(row["figures"]), row["soma_channels"])
            for figure in row["figures"]:
                self.assertTrue(any(v["view"] == "overview" for v in figure["views"]))
                self.assertTrue(any(v["minimum_native_tick_pixels_on_zoom"] is not None for v in figure["views"]))
                for view in figure["views"]:
                    self.assertFalse(view["downsampling"])
                    self.assertGreaterEqual(view["png_width"], 1600)
                    if view["minimum_native_tick_pixels_on_zoom"] is not None:
                        self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
        for name, digest in load(output/"SHA256SUMS.json").items():
            self.assertEqual(hashlib.sha256((output/name).read_bytes()).hexdigest(), digest)
