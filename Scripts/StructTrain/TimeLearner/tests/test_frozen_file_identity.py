"""Real regular files and native handles; no fabricated OS identity records."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import collector_provenance as subject
from ..native_evidence import EvidenceError


class FrozenFileIdentityTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.path=self.root/'source.bin'
        self.raw=b'complete original bytes\x00\xff\n';self.path.write_bytes(self.raw)

    def test_whole_read_and_stream_digest_bind_the_same_native_file(self):
        raw,record=subject._frozen(self.path,1024)
        self.assertEqual(raw,self.raw)
        self.assertEqual(record,subject.frozen_digest(self.path,1024))
        self.assertEqual(record['sha256'],hashlib.sha256(self.raw).hexdigest())

    def test_another_real_handle_with_identical_bytes_is_not_the_source(self):
        other=self.root/'other.bin';other.write_bytes(self.raw)
        os.utime(other,ns=(self.path.stat().st_atime_ns,self.path.stat().st_mtime_ns))
        with self.path.open('rb') as actual,other.open('rb') as wrong:
            before=self.path.lstat()
            self.assertTrue(subject._path_matches_opened(self.path,before,os.fstat(actual.fileno())))
            self.assertFalse(subject._path_matches_opened(self.path,before,os.fstat(wrong.fileno())))

    def test_actual_write_during_the_read_boundary_cannot_produce_frozen_success(self):
        for reader in (subject._frozen,subject.frozen_digest):
            self.path.write_bytes(self.raw);original=subject._path_matches_opened;changed=False
            def intervene(path,path_stat,opened):
                nonlocal changed
                result=original(path,path_stat,opened)
                if not changed:
                    changed=True
                    with path.open('ab') as writer:writer.write(b'changed');writer.flush();os.fsync(writer.fileno())
                return result
            # Only schedule a real filesystem write; the production identity
            # function and all native stat/read operations still execute.
            with patch.object(subject,'_path_matches_opened',side_effect=intervene):
                with self.assertRaises((EvidenceError,PermissionError)):reader(self.path,1024)

    def test_size_and_noncanonical_paths_are_rejected_before_payload_use(self):
        (self.root/'child').mkdir()
        for reader in (subject._frozen,subject.frozen_digest):
            with self.assertRaises(EvidenceError):reader(self.path,len(self.raw)-1)
            with self.assertRaises(EvidenceError):reader(self.root/'child/../source.bin',1024)
