"""Production numeric-trace reader and CLI, including a real Git-preserved Rdk trace."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..__main__ import main
from ..native_evidence import EvidenceError
from ..statistic_traces import analyze_inputs, read_trace


class StatisticTracesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def trace(self, text="0 0 -2\n1 .5 -1\n2 1 -3\n", layout="index-time-values", width=1):
        path = self.folder/"trace.txt"; path.write_bytes(text.encode())
        return {"id": "trace", "path": path.name, "layout": layout, "width": width,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def inputs(self, records):
        path = self.folder/"inputs.json"
        path.write_text(json.dumps({"kind": "timelearner_legacy_statistic_inputs",
                                  "schema_version": 1, "traces": records}), encoding="utf-8")
        return path

    def test_real_original_scalar_trace_and_source_binding(self):
        folder = Path(__file__).parent/"fixtures/statistic_traces"
        source = json.loads((folder/"source.json").read_text())
        path = folder/"native-time-values.txt"
        self.assertEqual(path.stat().st_size, source["bytes"])
        times, rows = read_trace(path, layout="time-values", width=1, expected_sha256=source["sha256"])
        self.assertGreater(len(times), 10)
        self.assertEqual(times[0], 0)
        self.assertEqual({v for row in rows for v in row}, {0., 1.})

    def test_both_declared_layouts_and_dimensions_above_four(self):
        for width in (1, 2, 4, 5):
            for indexed in (False, True):
                with self.subTest(width=width, indexed=indexed):
                    text = "".join((str(i)+" " if indexed else "")+str(i/2)+" "+
                                   " ".join(str(-j-i-1) for j in range(width))+"\n" for i in range(3))
                    record = self.trace(text, "index-time-values" if indexed else "time-values", width)
                    result = analyze_inputs(self.inputs([record]))
                    self.assertEqual(len(result["traces"][0]["channels"]), width)
                    self.assertEqual(result["traces"][0]["channels"][-1]["maximum"], -width)

    def test_corrupt_nonfinite_and_partial_rows_are_never_skipped(self):
        for text in ("0 0 1\n1 .5 bad\n", "0 0 nan\n", "0 0 inf\n", "0 0 -inf\n",
                     "0 0 1\n1 .5\n", "0 0 1\n\n", "header time value\n", "0 0 1e309\n"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError): analyze_inputs(self.inputs([self.trace(text)]))

    def test_replayed_missing_and_noninteger_indices_are_rejected(self):
        for text in ("0 0 1\n0 1 2\n", "1 0 1\n", "0.0 0 1\n", "00 0 1\n", "0 0 1\n2 1 2\n"):
            with self.assertRaises(EvidenceError): analyze_inputs(self.inputs([self.trace(text)]))

    def test_clock_must_be_finite_nonnegative_and_strictly_increasing(self):
        for text in ("0 -1 1\n", "0 1 1\n1 1 2\n", "0 1 1\n1 0 2\n", "0 nan 1\n"):
            with self.assertRaises(EvidenceError): analyze_inputs(self.inputs([self.trace(text)]))

    def test_file_hash_is_required_and_checked(self):
        record = self.trace(); record["sha256"] = "0"*64
        with self.assertRaisesRegex(EvidenceError, "hash_mismatch"): analyze_inputs(self.inputs([record]))
        for digest in (None, "bad", "A"*64):
            record["sha256"] = digest
            with self.assertRaises(EvidenceError): analyze_inputs(self.inputs([record]))

    def test_empty_files_and_unknown_layout_or_width_are_rejected(self):
        with self.assertRaises(EvidenceError): analyze_inputs(self.inputs([self.trace("")]))
        for layout, width in (("auto", 1), ("time-values", 0), ("time-values", True), ("time-values", 1.0)):
            with self.assertRaises(EvidenceError): analyze_inputs(self.inputs([self.trace(layout=layout, width=width)]))

    def test_duplicate_ids_and_path_aliases_are_rejected(self):
        record = self.trace()
        for rows in ([record, record], [record, {**record, "id": "alias"}]):
            with self.assertRaises(EvidenceError): analyze_inputs(self.inputs(rows))

    def test_unknown_schema_keys_and_missing_fields_are_rejected(self):
        record = self.trace()
        for rows in ([{**record, "complete": True}], [{k:v for k,v in record.items() if k != "width"}], []):
            with self.assertRaises(EvidenceError): analyze_inputs(self.inputs(rows))
        path = self.inputs([record]);data = json.loads(path.read_text());data["schema_version"] = True
        path.write_text(json.dumps(data))
        with self.assertRaises(EvidenceError): analyze_inputs(path)

    def test_parent_absolute_and_symlink_escape_paths_are_rejected(self):
        record = self.trace()
        for path in ("../trace.txt", "/tmp/trace.txt", "C:/trace.txt", "a\\trace.txt", "./trace.txt"):
            with self.assertRaises(EvidenceError): analyze_inputs(self.inputs([{**record, "path": path}]))
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/"outside.txt";target.write_text("0 0 1\n")
            (self.folder/"alias.txt").symlink_to(target)
            with self.assertRaisesRegex(EvidenceError, "alias_or_escape"):
                analyze_inputs(self.inputs([{**record, "path": "alias.txt"}]))

    def test_descriptive_summary_never_proves_training_or_complete_trials(self):
        result = analyze_inputs(self.inputs([self.trace()]))
        self.assertEqual(result["validity"], "unknown")
        self.assertTrue(result["numeric_files_verified"])
        self.assertFalse(result["classification_verified"])
        self.assertFalse(result["complete_observation_windows_verified"])
        self.assertIsNone(result["training_certificate"])
        self.assertIsNone(result["evaluation_verdict"])
        self.assertEqual(result["traces"][0]["channels"][0], {"minimum": -3., "maximum": -1., "last": -3.})

    def test_cli_from_another_directory_preserves_source_and_refuses_output_collision(self):
        source = self.inputs([self.trace()]);before = source.read_bytes();out = self.folder/"result.json"
        previous = Path.cwd()
        try:
            os.chdir(self.folder)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["analyze", str(source), "--format", "legacy-statistic-traces", "--output", str(out)]), 0)
            original = out.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertNotEqual(main(["analyze", str(source), "--format", "legacy-statistic-traces", "--output", str(out)]), 0)
            self.assertEqual(out.read_bytes(), original)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(json.loads(original)["validity"], "unknown")
        finally: os.chdir(previous)
