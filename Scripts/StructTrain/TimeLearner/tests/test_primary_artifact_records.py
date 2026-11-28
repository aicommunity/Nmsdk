"""Primary digest records retain their wire contract and reject changed bytes."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from Scripts.StructTrain.TimeLearner.native_calibration_worker import _record
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.native_pipeline_worker import _artifact_records


class PrimaryArtifactRecordsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.primary = self.root/'model.json'

    def test_empty_primary_has_the_standard_empty_digest(self):
        self.primary.write_bytes(b'')
        self.assertEqual(_record(self.primary, self.root), dict(path='model.json', bytes=0,
            sha256='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'))

    def test_full_content_and_last_short_block_are_included(self):
        data = bytes(range(256))*8193 + b'last bytes\x00\xff'
        self.primary.write_bytes(data)
        self.assertEqual(_record(self.primary, self.root), dict(path='model.json',
            bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))

    def test_current_schema_one_inventory_accepts_the_exact_primary(self):
        self.primary.write_bytes(b'{"model":"retained bytes"}\n')
        execution = dict(schema_version=1, artifacts=[_record(self.primary, self.root)])
        self.assertEqual(_artifact_records(self.root, execution), {'model.json'})

    def test_same_size_changed_primary_is_rejected(self):
        self.primary.write_bytes(b'{"value":1}\n')
        execution = dict(schema_version=1, artifacts=[_record(self.primary, self.root)])
        self.primary.write_bytes(b'{"value":2}\n')
        with self.assertRaisesRegex(EvidenceError, 'pipeline_artifact_changed'):
            _artifact_records(self.root, execution)

    def test_truncated_primary_is_rejected(self):
        self.primary.write_bytes(b'{"value":12}\n')
        execution = dict(schema_version=1, artifacts=[_record(self.primary, self.root)])
        self.primary.write_bytes(b'{"value":1}\n')
        with self.assertRaisesRegex(EvidenceError, 'pipeline_artifact_changed'):
            _artifact_records(self.root, execution)

    def test_extra_unlisted_primary_is_rejected(self):
        self.primary.write_bytes(b'{}')
        execution = dict(schema_version=1, artifacts=[_record(self.primary, self.root)])
        (self.root/'unlisted.json').write_bytes(b'{}')
        with self.assertRaisesRegex(EvidenceError, 'pipeline_native_artifact_closure_changed'):
            _artifact_records(self.root, execution)

    def test_directory_is_rejected_as_a_primary_file(self):
        self.primary.mkdir()
        with self.assertRaisesRegex(EvidenceError, 'worker_artifact_missing_or_symlink'):
            _record(self.primary, self.root)

    def test_missing_primary_is_rejected(self):
        with self.assertRaisesRegex(EvidenceError, 'worker_artifact_missing_or_symlink'):
            _record(self.primary, self.root)


if __name__ == '__main__':
    unittest.main()
