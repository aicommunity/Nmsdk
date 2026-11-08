"""Owned captured streams: explicit operational axis, never scientific PASS."""
from pathlib import Path
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..operational_diagnostics import inspect_streams, permits_positive_audit


class OperationalDiagnosticsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='timelearner-stream-review-')
        self.addCleanup(temporary.cleanup);self.root = Path(temporary.name)
        (self.root/'stdout.log').write_bytes(b'')
        (self.root/'stderr.log').write_bytes(b'')

    def test_actual_classic6_error_record_blocks_positive_audit(self):
        (self.root/'stderr.log').write_text('E20261108 02:41:59.575289 1945244 rdk_logging.h:164] [0] St12system_error Resource temporarily unavailable\n')
        result = inspect_streams(self.root)
        self.assertEqual(result['status'], 'error');self.assertEqual(result['error_records'], 1)
        self.assertFalse(permits_positive_audit(self.root, result))

    def test_empty_stderr_and_unstructured_stdout_are_clear(self):
        (self.root/'stdout.log').write_text('Testing ERROR recovery: expected failures 0\n')
        self.assertTrue(permits_positive_audit(self.root))

    def test_recognized_warnings_are_counted_without_becoming_errors(self):
        (self.root/'stderr.log').write_text('W1108 02:41:59.575289 1945244 rdk_logging.h:164] known warning\n')
        result = inspect_streams(self.root)
        self.assertEqual(result['status'], 'clear');self.assertEqual(result['warning_records'], 1)

    def test_unknown_stderr_requires_review_without_claiming_numerical_failure(self):
        (self.root/'stderr.log').write_text('unclassified runtime message\n')
        result = inspect_streams(self.root)
        self.assertEqual(result['status'], 'needs_review');self.assertEqual(result['error_records'], 0)
        self.assertIsNone(result['scientific_verdict']);self.assertFalse(permits_positive_audit(self.root))

    def test_stdout_error_and_sanitizer_are_not_hidden(self):
        for line in ['F20261108 02:41:59.575289 12 loader.cpp:2] fatal',
                     '==123==ERROR: AddressSanitizer: heap-use-after-free',
                     'Traceback (most recent call last):']:
            with self.subTest(line=line):
                (self.root/'stdout.log').write_text(line+'\n')
                self.assertEqual(inspect_streams(self.root)['status'], 'error')

    def test_missing_and_non_utf8_streams_cannot_be_clear(self):
        (self.root/'stderr.log').write_bytes(b'\xff\n')
        self.assertEqual(inspect_streams(self.root)['status'], 'needs_review')
        (self.root/'stderr.log').unlink()
        self.assertEqual(inspect_streams(self.root)['status'], 'needs_review')

    def test_long_lines_and_examples_are_bounded(self):
        (self.root/'stderr.log').write_bytes(b'x'*200000+b'\n'+b'unknown\n'*100)
        result = inspect_streams(self.root)
        self.assertEqual(result['status'], 'needs_review');self.assertEqual(len(result['examples']), 16)
        self.assertTrue(all(len(v['excerpt']) <= 256 for v in result['examples']))

    def test_recorded_clear_cannot_survive_changed_logs(self):
        recorded = inspect_streams(self.root)
        (self.root/'stderr.log').write_text('changed\n')
        with self.assertRaisesRegex(EvidenceError, 'operational_diagnostics_changed'):
            permits_positive_audit(self.root, recorded)

    def test_legacy_missing_record_is_recomputed_not_assumed_clear(self):
        (self.root/'stderr.log').write_text('E20261108 02:41:59.575289 123 loader.cpp:2] caught error\n')
        self.assertFalse(permits_positive_audit(self.root, None))

    def test_rehashed_portable_copy_cannot_hide_original_contained_error(self):
        original = self.root/'contained';original.mkdir()
        (original/'stdout.log').write_bytes(b'')
        (original/'stderr.log').write_text('E20261108 02:41:59.575289 123 loader.cpp:2] caught error\n')
        result = inspect_streams(self.root)
        self.assertFalse(result['contained_streams_match'])
        self.assertIn('contained_stream_copy_mismatch', result['reasons'])
        self.assertFalse(permits_positive_audit(self.root, result))

    def test_identical_contained_streams_keep_positive_audit(self):
        original = self.root/'contained';original.mkdir()
        for name in ['stdout.log','stderr.log']:(original/name).write_bytes((self.root/name).read_bytes())
        self.assertTrue(inspect_streams(self.root)['contained_streams_match'])
        self.assertTrue(permits_positive_audit(self.root))
