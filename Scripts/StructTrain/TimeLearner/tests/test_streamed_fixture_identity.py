"""Bounded real-file identity checks; no native model or numerical fixtures."""
import copy
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from .. import collector_provenance as files
from .. import owned_python_job as jobs
from ..native_evidence import EvidenceError
from ..validation import fixture_fingerprint
from .test_owned_python_job import request


class StreamedFixtureIdentityTest(unittest.TestCase):
    def test_small_and_empty_files_keep_original_frozen_record_format(self):
        with tempfile.TemporaryDirectory() as directory:
            for raw in (b'', b'actual primary bytes\n'):
                p = Path(directory)/'primary';p.write_bytes(raw)
                self.assertEqual(files.frozen_digest(p, 1024), files._frozen(p, 1024)[1])

    def test_large_actual_file_needs_explicit_budget_and_hashes_without_raw_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);p = root/'large.bin';size = 64*1024**2+1
            with p.open('wb') as stream:
                stream.truncate(size)
            count, fingerprint = fixture_fingerprint(root, '*.bin')
            suite = {'fixtures': {'TIMELEARNER_LARGE_PRIMARY':
                {'pattern': '*.bin', 'files': count, 'fingerprint': fingerprint}}}
            bindings = {'TIMELEARNER_LARGE_PRIMARY': str(root)}
            with self.assertRaisesRegex(EvidenceError, 'collector_file_type_or_size'):
                jobs._fixture_snapshot(suite, bindings)
            result = jobs._fixture_snapshot(suite, bindings,
                maximum_file_bytes=size, maximum_total_bytes=size)
            expected = subprocess.check_output(['sha256sum', str(p)], text=True).split()[0]
            self.assertEqual(result['TIMELEARNER_LARGE_PRIMARY']['files']['large.bin'],
                {'source_path': str(p), 'bytes': size, 'sha256': expected})

    def test_total_budget_cannot_be_replaced_by_per_file_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('first.bin', 'second.bin'):
                (root/name).write_bytes(b'1234')
            count, fingerprint = fixture_fingerprint(root, '*.bin')
            suite = {'fixtures': {'TIMELEARNER_PRIMARY':
                {'pattern': '*.bin', 'files': count, 'fingerprint': fingerprint}}}
            bindings = {'TIMELEARNER_PRIMARY': str(root)}
            with self.assertRaisesRegex(EvidenceError, 'fixture_total_bytes_exceeded'):
                jobs._fixture_snapshot(suite, bindings, maximum_file_bytes=4, maximum_total_bytes=7)
            self.assertEqual(jobs._fixture_snapshot(suite, bindings,
                maximum_file_bytes=4, maximum_total_bytes=8)['TIMELEARNER_PRIMARY']['fingerprint'], fingerprint)

    def test_explicit_byte_limits_reject_boolean_fractional_unknown_or_inverted_budgets(self):
        value = request()
        value['operation']['fixture_byte_limits'] = {'maximum_file_bytes': 256*1024**2,
                                                     'maximum_total_bytes': 1024**3}
        self.assertEqual(jobs.validate_request(value), value)
        for bad in ({'maximum_file_bytes': True, 'maximum_total_bytes': 8},
                    {'maximum_file_bytes': 1.5, 'maximum_total_bytes': 8},
                    {'maximum_file_bytes': 9, 'maximum_total_bytes': 8},
                    {'maximum_file_bytes': 4, 'maximum_total_bytes': 8, 'extra': 1}):
            document = copy.deepcopy(value);document['operation']['fixture_byte_limits'] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(EvidenceError, 'fixture_byte_limits'):
                jobs.validate_request(document)

    def test_directory_and_size_overflow_cannot_be_hashed_as_regular_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);p = root/'primary';p.write_bytes(b'1234')
            for path, budget in ((root, 1024), (p, 3)):
                with self.subTest(path=path), self.assertRaisesRegex(EvidenceError, 'collector_file_type_or_size'):
                    files.frozen_digest(path, budget)

    def test_file_and_parent_aliases_are_still_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);actual = root/'actual';actual.mkdir()
            p = actual/'primary';p.write_bytes(b'bytes')
            alias = root/'alias';alias.symlink_to(actual, target_is_directory=True)
            file_alias = root/'file-alias';file_alias.symlink_to(p)
            for path in (alias/'primary', file_alias):
                with self.subTest(path=path), self.assertRaisesRegex(EvidenceError, 'collector_symlink_path'):
                    files.frozen_digest(path, 1024)

    def test_change_during_streaming_cannot_keep_original_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/'primary';p.write_bytes(b'before')
            original = p.stat();digest = hashlib.sha256()
            class ChangingDigest:
                def update(self, block):
                    digest.update(block)
                    p.write_bytes(b'after!')
                    os.utime(p, ns=(original.st_atime_ns, original.st_mtime_ns+10**9))
                def hexdigest(self):
                    return digest.hexdigest()
            with patch.object(files.hashlib, 'sha256', return_value=ChangingDigest()):
                with self.assertRaisesRegex(EvidenceError, 'collector_file_changed_during_read'):
                    files.frozen_digest(p, 1024)
