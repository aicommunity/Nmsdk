"""Actual native archived streams and corruptions, not synthetic function copies."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..historical_phasea_temporal import read_case
from ..native_evidence import EvidenceError


class HistoricalTemporal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path(os.environ["TL_HISTORICAL_TEMPORAL"])

    def test_three_actual_native_cases(self):
        for case, correct in (("baseline", 4), ("threshold0130", 5), ("threshold0135", 6)):
            with self.subTest(case=case):
                data = read_case(self.source/case)
                self.assertEqual(data["validation"]["native_correct"], correct)
                self.assertEqual(data["validation"]["stimulus_edges"], 32)
                self.assertEqual(len(data["trials"]), 8)
                self.assertIsNone(data["validation"]["strict_evaluation_verdict"])

    def corrupted(self, mutation, expected, update_hash=True):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/"case"
            shutil.copytree(self.source/"baseline", folder,
                            ignore=shutil.ignore_patterns("EventsLog", "*.user.ini"))
            records = json.loads((folder/"trace-files.json").read_text())
            record = next(r for r in records if r["role"] == "soma1_exc")
            path = folder/record["path"]
            lines = path.read_text().splitlines()
            lines = mutation(lines)
            path.write_text("\n".join(lines)+"\n")
            if update_hash:
                record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                (folder/"trace-files.json").write_text(json.dumps(records))
            with self.assertRaisesRegex(EvidenceError, expected):read_case(folder)

    def test_hash_mismatch(self):
        self.corrupted(lambda rows: rows[:-1], "historical_trace_hash_mismatch", False)

    def test_truncated_stream(self):
        self.corrupted(lambda rows: rows[:-1], "historical_trace_incomplete_40s")

    def test_nonfinite_stream(self):
        self.corrupted(lambda rows: [rows[0].rsplit(None, 1)[0]+" nan"]+rows[1:],
                       "historical_trace_nonfinite")

    def test_index_duplicate(self):
        self.corrupted(lambda rows: [rows[0], rows[0]]+rows[2:], "historical_trace_index")

    def test_clock_corruption(self):
        self.corrupted(lambda rows: ["00000000 0.0001 -1"]+rows[1:], "historical_trace_clock")

    def test_derived_soma_corruption(self):
        self.corrupted(lambda rows: [rows[0].rsplit(None, 1)[0]+" -2"]+rows[1:],
                       "historical_soma_cached_disagreement")


if __name__ == "__main__":
    unittest.main()
