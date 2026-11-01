"""Actual CLI source binding and no-data rejection report, without new physics."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ..native_evidence import load


class LiveFinalizationCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names = ("TIMELEARNER_LIVE_FINALIZATION_NATIVE", "TIMELEARNER_LIVE_PRIMARY_INVENTORY")
        if not all(os.environ.get(name) for name in names):
            raise unittest.SkipTest("requires actual native preflight control and primary inventory")
        cls.native, cls.inventory = (Path(os.environ[name]) for name in names)
        cls.source = cls.native/"Classic_live_finalization_0_local_6.json"
        if not cls.source.is_file():
            raise RuntimeError("requires actual Classic invalid-design receipt")
        cls.root = Path(__file__).resolve().parents[4]

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "Scripts.StructTrain.TimeLearner", *map(str, args)],
                              cwd=self.root, text=True, capture_output=True, timeout=120)

    def test_real_analysis_and_report_share_the_inventory_bound_native_source(self):
        result = self.run_cli("analyze", self.source, "--format", "native-live-finalization",
                              "--primary-inventory", self.inventory)
        self.assertEqual(result.returncode, 0, result.stderr)
        analyzed = json.loads(result.stdout)
        self.assertEqual(analyzed["validity"], "valid")
        self.assertTrue(analyzed["analysis"]["no_recognition_evidence"])
        self.assertIsNone(analyzed["evaluation_verdict"])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/"report"
            result = self.run_cli("report", self.source, "--format", "native-live-finalization",
                                  "--primary-inventory", self.inventory, "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(load(output/"primary/live-record.json.gz"), load(self.source))
            self.assertFalse(load(output/"manifest.json")["recognition_presented"])
            self.assertFalse(list(output.rglob("*.png")))

    def test_missing_inventory_and_irrelevant_overlays_reject_without_output(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, options in (("missing_inventory", []), ("model_overlay", ["--primary-inventory", self.inventory, "--model", self.source])):
                output = Path(directory)/name
                result = self.run_cli("report", self.source, "--format", "native-live-finalization", "--output", output, *options)
                with self.subTest(case=name):
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(json.loads(result.stderr)["status"], "incomplete")
                    self.assertFalse(output.exists())
