"""Server-only native DATA staging and post-execution mutation guards."""
import hashlib
import tempfile
from pathlib import Path
import unittest

from .. import native_gate_inputs as subject
from ..native_evidence import EvidenceError
from ..native_gate import supported_specification


class NativeGateInputsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='native-gate-inputs-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.source = self.root/'source.qz'
        self.raw = b'opaque recorded model bytes\n'
        self.source.write_bytes(self.raw)
        self.output = self.root/'owned'
        self.rows = [dict(name='recorded-model.qz', path=str(self.source), bytes=len(self.raw),
                          sha256=hashlib.sha256(self.raw).hexdigest())]

    def staged(self):
        captured = subject.capture_inputs(self.rows, self.output)
        self.output.mkdir()
        subject.stage_inputs(captured, self.output)
        return captured

    def test_exact_captured_bytes_and_descriptor_are_retained(self):
        captured = self.staged()
        self.assertEqual((self.output/'native-inputs/recorded-model.qz').read_bytes(), self.raw)
        audit = subject.verify_inputs(captured, self.output)
        self.assertTrue(audit['source_bytes_unchanged'])
        self.assertTrue(audit['staged_bytes_unchanged'])
        self.assertFalse(audit['native_execution_attested'])
        self.assertIsNone(audit['scientific_verdict'])

    def test_source_changed_after_capture_is_not_a_successful_gate(self):
        captured = self.staged()
        self.source.write_bytes(b'x'*len(self.raw))
        with self.assertRaisesRegex(EvidenceError, 'data_input_changed'):
            subject.verify_inputs(captured, self.output)

    def test_staged_bytes_changed_by_native_process_are_rejected(self):
        captured = self.staged()
        (self.output/'native-inputs/recorded-model.qz').write_bytes(b'x'*len(self.raw))
        with self.assertRaisesRegex(EvidenceError, 'data_input_changed'):
            subject.verify_inputs(captured, self.output)

    def test_extra_staged_file_and_changed_descriptor_are_rejected(self):
        captured = self.staged()
        extra = self.output/'native-inputs/extra'
        extra.write_bytes(b'extra')
        with self.assertRaisesRegex(EvidenceError, 'namespace_changed'):
            subject.verify_inputs(captured, self.output)
        extra.unlink()
        (self.output/'native-inputs/descriptor.json').write_bytes(b'{}')
        with self.assertRaisesRegex(EvidenceError, 'descriptor_changed'):
            subject.verify_inputs(captured, self.output)

    def test_wrong_source_digest_is_rejected_before_output_is_created(self):
        self.rows[0]['sha256'] = '0'*64
        with self.assertRaises(EvidenceError):
            subject.capture_inputs(self.rows, self.output)
        self.assertFalse(self.output.exists())

    def test_alias_and_traversal_names_and_boolean_size_are_rejected(self):
        for change in [dict(name='../escape'), dict(name='descriptor.json'), dict(bytes=True),
                       dict(sha256='not-a-hash'), dict(unknown=True)]:
            self.assertFalse(subject.valid_declarations([{**self.rows[0], **change}]))
        self.assertFalse(subject.valid_declarations([self.rows[0], self.rows[0]]))
        self.assertFalse(subject.valid_declarations([self.rows[0], {**self.rows[0], 'name':'RECORDED-MODEL.QZ'}]))

    def test_symlink_source_and_staged_alias_are_rejected(self):
        alias = self.root/'alias.qz'
        alias.symlink_to(self.source)
        with self.assertRaises(EvidenceError):
            subject.capture_inputs([{**self.rows[0], 'path':str(alias)}], self.output)
        captured = self.staged()
        staged = self.output/'native-inputs/recorded-model.qz'
        staged.unlink();staged.symlink_to(self.source)
        with self.assertRaises(EvidenceError):
            subject.verify_inputs(captured, self.output)

    def test_explicit_schema5_does_not_change_legacy_or_windows_contract(self):
        old = dict(kind='timelearner_native_test_gate', schema_version=3, runtime_manifest='runtime.json',
                   source_root='source', expected_test_ids=['Suite/Case'], maximum_wall_seconds=60,
                   asan_options='', cooperative_runtime_capture=True,
                   process_limits=dict(memory_bytes=128*1024**2, tasks=16))
        self.assertTrue(supported_specification(old))
        self.assertTrue(supported_specification(dict(old, schema_version=5, data_inputs=self.rows)))
        self.assertFalse(supported_specification(dict(old, data_inputs=self.rows)))
        self.assertFalse(supported_specification(dict(old, schema_version=5)))
        self.assertFalse(supported_specification(dict(old, schema_version=5, data_inputs=self.rows,
                                                    cooperative_runtime_capture=False)))
        self.assertFalse(supported_specification(dict(old, schema_version=4, data_inputs=self.rows)))
