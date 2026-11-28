"""Real Windows staging of the exact archived Classic model fixture.

This checks filesystem transport, not a substitute neuron implementation.
The three compiled DATA tests must still run separately through schema8.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zlib

from .. import native_gate_inputs as subject
from ..native_evidence import EvidenceError


class WindowsNativeData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'nt':
            raise unittest.SkipTest('requires the actual Windows filesystem')
        filename = os.environ.get('TIMELEARNER_NATIVE_GATE_FIXTURE')
        if not filename:
            raise unittest.SkipTest('requires the declared archived Classic fixture')
        cls.original = Path(filename).read_bytes()
        assert len(cls.original) == 323020
        cls.digest = hashlib.sha256(cls.original).hexdigest()
        assert cls.digest == 'd58ce13f3759a9e7c38f65c2cdb3059bb7ddccbd152d7e4144564c1efa36b234'
        assert int.from_bytes(cls.original[:4], 'big') == 4812359
        decoder = zlib.decompressobj()
        raw = decoder.decompress(cls.original[4:], 4812360)
        assert decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
        assert len(raw) == 4812359
        assert hashlib.sha256(raw).hexdigest() == '1c8d50628e7eea87c2bad230428526000802ec73e9627bd5d7d7f414bb69e05c'
        assert json.loads(raw)['schema_version'] == 6

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='tl-win-native-data-')
        self.root = Path(self.tmp.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.tmp.cleanup)
        self.source = self.root/'source.qz'
        self.source.write_bytes(self.original)
        self.output = self.root/'owned'
        self.rows = [dict(name='classic-package6.qz', path=str(self.source),
                          bytes=len(self.original), sha256=self.digest)]

    def staged(self):
        captured = subject.capture_inputs(self.rows, self.output)
        self.output.mkdir()
        subject.stage_inputs(captured, self.output)
        return captured

    def test_real_fixture_and_frozen_descriptor_survive_windows_staging(self):
        captured = self.staged()
        path = self.output/'native-inputs/classic-package6.qz'
        self.assertEqual(path.read_bytes(), self.original)
        self.assertFalse(os.path.samefile(path, self.source))
        proof = subject.verify_inputs(captured, self.output)
        self.assertTrue(proof['source_bytes_unchanged'])
        self.assertTrue(proof['staged_bytes_unchanged'])
        self.assertEqual(proof['descriptor'], captured.descriptor)
        self.assertFalse(proof['native_execution_attested'])

    def test_wrong_source_digest_fails_before_output_creation(self):
        self.rows[0]['sha256'] = '0'*64
        with self.assertRaises(EvidenceError):
            subject.capture_inputs(self.rows, self.output)
        self.assertFalse(self.output.exists())

    def test_source_mutation_after_capture_is_rejected(self):
        captured = self.staged()
        self.source.write_bytes(b'x'+self.original[1:])
        with self.assertRaisesRegex(EvidenceError, 'data_input_changed'):
            subject.verify_inputs(captured, self.output)

    def test_staged_mutation_after_capture_is_rejected(self):
        captured = self.staged()
        (self.output/'native-inputs/classic-package6.qz').write_bytes(b'x'+self.original[1:])
        with self.assertRaisesRegex(EvidenceError, 'data_input_changed'):
            subject.verify_inputs(captured, self.output)

    def test_extra_file_and_changed_descriptor_are_rejected(self):
        captured = self.staged()
        extra = self.output/'native-inputs/extra'
        extra.write_bytes(b'extra')
        with self.assertRaisesRegex(EvidenceError, 'namespace_changed'):
            subject.verify_inputs(captured, self.output)
        extra.unlink()
        (self.output/'native-inputs/descriptor.json').write_bytes(b'{}')
        with self.assertRaisesRegex(EvidenceError, 'descriptor_changed'):
            subject.verify_inputs(captured, self.output)

    def test_equal_bytes_hardlinked_to_source_are_not_an_owned_copy(self):
        captured = self.staged()
        staged = self.output/'native-inputs/classic-package6.qz'
        staged.unlink()
        os.link(self.source, staged)
        with self.assertRaisesRegex(EvidenceError, 'data_input_alias'):
            subject.verify_inputs(captured, self.output)

    def test_existing_staging_is_not_overwritten(self):
        captured = subject.capture_inputs(self.rows, self.output)
        self.output.mkdir()
        directory = self.output/'native-inputs'
        directory.mkdir()
        sentinel = directory/'sentinel'
        sentinel.write_bytes(b'preserve')
        with self.assertRaisesRegex(EvidenceError, 'staging_exists'):
            subject.stage_inputs(captured, self.output)
        self.assertEqual(sentinel.read_bytes(), b'preserve')

    def test_junction_staging_is_rejected_without_symlink_privilege(self):
        captured = self.staged()
        directory = self.output/'native-inputs'
        self.assertEqual({p.name for p in directory.iterdir()}, {'classic-package6.qz', 'descriptor.json'})
        for p in directory.iterdir():
            p.unlink()
        directory.rmdir()
        target = self.root/'other'
        target.mkdir()
        result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(directory), str(target)],
                                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        self.assertTrue(directory.is_junction())
        try:
            with self.assertRaisesRegex(EvidenceError, 'namespace_changed'):
                subject.verify_inputs(captured, self.output)
        finally:
            directory.rmdir()  # the new junction itself, never its target
        self.assertTrue(target.is_dir())


if __name__ == '__main__':
    unittest.main()
