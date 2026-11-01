"""Full actual paired-native waveforms; no toy replacements of primary data."""
import csv
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.recognition_transport_reports import render_transport


class RecognitionTransportReportsTest(unittest.TestCase):
    def test_all_declared_native_posttune_transport_patterns(self):
        value = os.environ.get("TIMELEARNER_POSTTUNE_CANDIDATES_DIR")
        if not value:
            self.skipTest("requires actual native PostTune primary exports")
        paths = sorted(Path(value).glob("*_recognition_state.json"))
        self.assertEqual(len(paths), 4)
        cache = os.environ.get("TIMELEARNER_POSTTUNE_TRANSPORT_REPORT_CACHE")
        temporary = None if cache else tempfile.TemporaryDirectory(prefix="tl-native-posttune-report-")
        root = Path(cache if cache else temporary.name)
        root.mkdir(parents=True, exist_ok=True)
        try:
            total_channels = 0
            for i, source in enumerate(paths):
                output = root/f"transport-{i:03d}"
                result = render_transport(source, output)
                manifest = json.loads((output/"manifest.json").read_text())
                self.assertEqual(result["patterns"], 1)
                self.assertIsNone(result["scientific_verdict"])
                self.assertFalse(manifest["visual_acceptance_complete"])
                self.assertTrue(manifest["paired_model_waveform_values_exact"])
                total_channels += manifest["soma_channels"]
                stem = source.name.removesuffix("_recognition_state.json")
                with source.with_name(stem+"_recognition_roundtrip.csv").open(newline="") as stream:
                    rows = list(csv.reader(stream))
                self.assertEqual(manifest["recorded_native_ticks"], len(rows)-1)
                self.assertEqual(len(manifest["figures"]), manifest["soma_channels"])
                for figure in manifest["figures"]:
                    self.assertTrue(any(v["view"] == "overview" for v in figure["views"]))
                    for view in figure["views"]:
                        self.assertFalse(view["downsampling"])
                        if view["minimum_native_tick_pixels_on_zoom"] is not None:
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                for name, expected in json.loads((output/"SHA256SUMS.json").read_text()).items():
                    self.assertEqual(hashlib.sha256((output/name).read_bytes()).hexdigest(), expected)
            self.assertEqual(total_channels, 6)
        finally:
            if temporary:
                temporary.cleanup()
