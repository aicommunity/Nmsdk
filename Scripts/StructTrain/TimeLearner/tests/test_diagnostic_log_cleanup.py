"""Deletion gates and exact retention of meaningful diagnostic transitions."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from ..diagnostic_log_cleanup import compact_tick_log


class DiagnosticLogCleanupTest(unittest.TestCase):
    def fixture(self, root):
        folder = root/"EventsLog";folder.mkdir()
        source = folder/"NeuroModeler.fixture.log.INFO.20261023-000000.1"
        lines = [b"Log file created at: fixture\n",
                 b"I1023 00:00:00.000001 1 x:1] EolGateAudit phase=0\n",
                 b"I1023 00:00:00.000002 1 x:1] EolGateAudit phase=0\n",
                 b"I1023 00:00:00.000003 1 x:1] EolGateAudit phase=1\n",
                 b"W1023 00:00:00.000004 1 x:1] keep this diagnostic\n",
                 b"I1023 00:00:00.000005 1 x:1] EolGateAudit phase=1\n"]
        source.write_bytes(b"".join(lines));return source, lines

    def test_transitions_raw_lines_and_endpoints_retained_without_default_deletion(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source,lines=self.fixture(root);dest=root/"summary.jsonl.gz"
            result=compact_tick_log(source,dest)
            self.assertTrue(source.exists());self.assertFalse(result["original_removed"])
            self.assertEqual(result["source_sha256"],hashlib.sha256(b"".join(lines)).hexdigest())
            self.assertEqual(result["collapsed_tick_lines"],1)
            with gzip.open(dest,"rt") as f:records=[json.loads(s) for s in f]
            groups=[r for r in records if r["kind"]=="repeat"]
            self.assertEqual([r["count"] for r in groups],[2,1,1])
            self.assertEqual(base64.b64decode(groups[0]["first"]),lines[1])
            self.assertEqual(base64.b64decode(groups[0]["last"]),lines[2])
            self.assertEqual([base64.b64decode(r["line"]) for r in records if r["kind"]=="raw"],[lines[0],lines[4]])

    def test_explicit_deletion_requires_completed_verified_summary_and_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source,_=self.fixture(root);dest=root/"summary.jsonl.gz"
            result=compact_tick_log(source,dest,delete_original=True)
            self.assertFalse(source.exists());self.assertTrue(result["original_removed"])
            self.assertEqual(json.loads(Path(str(dest)+".json").read_text()),result)
            self.assertEqual(hashlib.sha256(dest.read_bytes()).hexdigest(),result["summary_sha256"])

    def test_open_log_and_wrong_file_class_cannot_be_removed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source,_=self.fixture(root)
            with source.open("rb"):
                with self.assertRaises(RuntimeError):compact_tick_log(source,root/"open.gz",delete_original=True)
            self.assertTrue(source.exists());self.assertFalse((root/"open.gz").exists())
            other=root/"observation.csv";other.write_text("primary\n")
            with self.assertRaises(ValueError):compact_tick_log(other,root/"bad.gz",delete_original=True)
            self.assertTrue(other.exists())

    def test_nonredundant_log_remains_without_leaving_a_completed_scratch_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source,_=self.fixture(root);dest=root/"summary.jsonl.gz"
            original=b"Log file created at: fixture\nI1023 00:00:00.000001 1 x:1] EolGateAudit phase=0\n"
            source.write_bytes(original)
            with self.assertRaisesRegex(RuntimeError,"no redundant tick messages"):
                compact_tick_log(source,dest,delete_original=True)
            self.assertEqual(source.read_bytes(),original)
            self.assertFalse(dest.exists())
            self.assertFalse(Path(str(dest)+".partial").exists())
