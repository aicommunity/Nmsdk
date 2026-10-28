"""Exercise the production CLI with actual native preview JSON."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.__main__ import main


class AnalysisCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_DOMAIN_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires original native domain previews")
        cls.source = next(iter(sorted(Path(directory).glob("*_domain_preview.json"))), None)
        if cls.source is None:
            raise RuntimeError("missing actual native preview")

    def invoke(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = main(["analyze", *map(str, args)])
        return code, output.getvalue(), error.getvalue()

    def test_actual_domain(self):
        code, output, error = self.invoke(self.source, "--format", "domain")
        self.assertEqual(code, 0, error)
        result = json.loads(output)
        self.assertTrue(result["analysis"]["physics_verified"])
        self.assertIsNone(result["evaluation_verdict"])

    def test_unknown_schema_fails_without_positive_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corrupt.json"
            record = json.loads(self.source.read_text())
            record["schema_version"] = 999
            path.write_text(json.dumps(record))
            code, output, error = self.invoke(path, "--format", "domain")
        self.assertEqual(code, 2)
        self.assertFalse(output)
        self.assertEqual(json.loads(error)["validity"], "invalid")

    def test_output_collision_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "analysis.json"
            path.write_text("prior-result")
            code, output, error = self.invoke(self.source, "--format", "domain", "--output", path)
            self.assertEqual(path.read_text(), "prior-result")
        self.assertEqual(code, 2)
        self.assertFalse(output)
        self.assertEqual(json.loads(error)["validity"], "invalid")

    def test_probe_cannot_omit_primary_trace(self):
        code, output, error = self.invoke(self.source, "--format", "probe")
        self.assertEqual(code, 2)
        self.assertFalse(output)
        self.assertEqual(json.loads(error)["reason"], "primary_probe_trace_required")

    def test_legacy_adapter_does_not_invent_physical_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.json"
            record = json.loads(self.source.read_text())
            record["schema_version"] = 1
            path.write_text(json.dumps(record))
            code, output, error = self.invoke(path, "--format", "domain", "--allow-legacy")
        self.assertEqual(code, 0, error)
        self.assertFalse(json.loads(output)["analysis"]["physics_verified"])
