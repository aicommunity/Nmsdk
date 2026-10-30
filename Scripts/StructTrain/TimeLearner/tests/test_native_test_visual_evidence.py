"""Read back all rendered native-suite trials against original producer files."""
import hashlib
import json
import os
import struct
import unittest
from pathlib import Path

from ..native_evidence import load


class NativeTestVisualEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("TIMELEARNER_NATIVE_TEST_REPORT_DIR")
        report = os.environ.get("TIMELEARNER_NATIVE_TEST_VISUAL_DIR")
        if not source or not report:
            raise unittest.SkipTest("requires original native suite and completed full visual report")
        cls.native = Path(source)/"native"
        cls.report = Path(report)
        cls.manifest = load(cls.report/"manifest.json")

    def test_every_direct_and_embedded_original_probe_has_a_source_bound_figure_set(self):
        expected = {}
        for path in self.native.glob("*.json"):
            value = load(path)
            if value.get("kind") == "timelearner_native_probe_evidence":
                expected[(path.name, "")] = value
            if isinstance(value.get("probe"), dict) and value["probe"].get("kind") == "timelearner_native_probe_evidence":
                expected[(path.name, "/probe")] = value["probe"]
        self.assertEqual(len(expected), 338)
        seen = set()
        for group in self.manifest["groups"]:
            folder = self.report/Path(group["report"]).parent
            actual = load(folder/"manifest.json")["reports"]
            self.assertEqual(len(actual), len(group["trials"]))
            for entry, item in zip(group["trials"], actual):
                key = (entry["source_packet"], entry["json_pointer"])
                self.assertNotIn(key, seen);seen.add(key)
                self.assertEqual(item["trial_id"], entry["trial_id"])
                rendered = folder/item["folder"]
                self.assertEqual(load(rendered/"primary/probe.json"), expected[key])
                original_csv = (self.native/entry["source_trace"]).read_bytes()
                self.assertEqual((rendered/"primary/trace.csv").read_bytes(), original_csv)
                self.assertEqual(entry["trace_sha256"], hashlib.sha256(original_csv).hexdigest())
                self.assertEqual(entry["packet_sha256"], hashlib.sha256((self.native/key[0]).read_bytes()).hexdigest())
        self.assertEqual(seen, set(expected))

    def test_all_507_soma_pairs_have_large_overview_and_timestep_resolving_views(self):
        pairs = 0
        for group in self.manifest["groups"]:
            folder = self.report/Path(group["report"]).parent
            for item in load(folder/"manifest.json")["reports"]:
                probe = folder/item["folder"]; record = load(probe/"manifest.json")
                self.assertFalse(record["visual_acceptance_complete"])
                self.assertIsNone(record["scientific_verdict"])
                for figure in record["figures"]:
                    views = figure["views"]
                    self.assertTrue(views)
                    self.assertTrue(any(v["view"] == "overview" for v in views))
                    self.assertTrue(any(v["view"].startswith("zoom-") for v in views))
                    for view in views:
                        self.assertFalse(view["downsampling"])
                        if view["time_view"] != "overview":
                            self.assertGreaterEqual(view["minimum_native_tick_pixels_on_zoom"], 8)
                        self.assertEqual({Path(p).suffix for p in view["files"]}, {".png", ".svg", ".pdf"})
                        png = next(probe/p for p in view["files"] if p.endswith(".png"))
                        with png.open("rb") as stream: header = stream.read(24)
                        self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
                        self.assertEqual(struct.unpack(">II", header[16:24]), (1920, 960))
                    pairs += 1
        self.assertEqual(pairs, 507)
        self.assertEqual(self.manifest["rendered_trial_soma_pairs"], pairs)

    def test_every_published_file_hash_matches_and_original_wrappers_are_retained(self):
        hashes = load(self.report/"SHA256SUMS.json")
        files = {p.relative_to(self.report).as_posix() for p in self.report.rglob("*")
                 if p.is_file() and p != self.report/"SHA256SUMS.json"}
        self.assertEqual(set(hashes), files)
        for relative, expected in hashes.items():
            self.assertEqual(hashlib.sha256((self.report/relative).read_bytes()).hexdigest(), expected, relative)
        for path in self.native.iterdir():
            self.assertEqual((self.report/"primary/native"/path.name).read_bytes(), path.read_bytes())
        self.assertFalse(self.manifest["data_complete"])
        self.assertFalse(self.manifest["visual_acceptance_complete"])
        self.assertIsNone(self.manifest["scientific_verdict"])
