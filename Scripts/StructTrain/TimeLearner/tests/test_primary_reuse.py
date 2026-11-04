"""Actual restored native runs and fail-closed primary archive references."""
import hashlib
import io
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest

from ..native_calibration_worker import _signed, _write
from ..native_evidence import EvidenceError, load
from ..primary_reuse import restore, _stream


class PrimaryReuseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder, restored, repo = (os.environ.get(k) for k in ('TIMELEARNER_REUSE_BUNDLE', 'TIMELEARNER_REUSE_RESTORED', 'TIMELEARNER_REUSE_REPOSITORY'))
        if not folder or not restored or not repo:
            raise unittest.SkipTest('requires actual compact native primary and restored file tree')
        cls.bundle, cls.restored, cls.repo = Path(folder), Path(restored), Path(repo)

    def test_all_native_files_are_restored_without_rewriting_their_manifests(self):
        metadata = load(self.bundle/'reuse.json');records = metadata['original_bundle']['members']
        actual = {p.relative_to(self.restored).as_posix(): p for p in self.restored.rglob('*') if p.is_file()}
        self.assertEqual(set(actual), set(records))
        self.assertGreater(len(metadata['reused_members']), 0)
        self.assertLess(metadata['archive_bytes'], metadata['original_bundle']['archive_bytes'])
        for name, p in actual.items():
            self.assertEqual(p.stat().st_size, records[name]['bytes'])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), records[name]['sha256'])

    def test_rehashed_reference_change_cannot_silently_use_a_worker_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'bundle';shutil.copytree(self.bundle, folder)
            p = folder/'reuse.json';record = load(p);record.pop('sha256');record['reference']['commit'] = '0'*40
            p.unlink();_write(p, _signed(record))
            with self.assertRaisesRegex(EvidenceError, 'reuse_git_archive_unavailable'):
                restore(folder, self.repo, Path(tmp)/'restored')

    def test_changed_compressed_primary_is_rejected_before_restoration(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'bundle';shutil.copytree(self.bundle, folder)
            p = folder/'primary.tar.xz';raw = bytearray(p.read_bytes());raw[len(raw)//2] ^= 1;p.write_bytes(raw)
            with self.assertRaisesRegex(EvidenceError, 'reuse_primary_archive_changed'):
                restore(folder, self.repo, Path(tmp)/'restored')
            self.assertFalse((Path(tmp)/'restored').exists())

    def test_nonregular_or_unsafe_archive_members_are_not_extracted(self):
        for mode in ('link', 'path'):
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode='w:xz') as archive:
                member = tarfile.TarInfo('source.json' if mode == 'link' else '../source.json')
                if mode == 'link':member.type = tarfile.SYMTYPE;member.linkname = 'other.json'
                archive.addfile(member, io.BytesIO(b''))
            with self.subTest(mode=mode), self.assertRaises(EvidenceError):list(_stream(stream.getvalue()))
