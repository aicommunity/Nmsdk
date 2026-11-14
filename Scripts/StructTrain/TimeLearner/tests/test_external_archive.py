"""Exercise production archive I/O, collision handling and tamper rejection."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import external_archive as archive
from ..native_evidence import EvidenceError


class ExternalArchiveTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'archive'; self.root.mkdir()
        (self.root/'archive.root.json').write_text(json.dumps({
            'kind': archive.ARCHIVE_KIND, 'schema_version': 1,
            'authoritative_root': archive.DEFAULT_ROOT}))
        self.source = Path(self.temp.name)/'primary.tar.xz'
        self.source.write_bytes(b'\x00actual archived bytes\xff'*100)

    def test_roundtrip_and_duplicate_store_preserve_exact_original(self):
        original = self.source.read_bytes()
        record = archive.store(self.source, self.root)
        self.assertEqual(archive.store(self.source, self.root), record)
        self.assertEqual(archive.resolve(record, self.root).read_bytes(), original)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(list((self.root/'objects/sha256').glob('.incoming-*')), [])

    def test_tampered_existing_object_is_rejected_and_never_overwritten(self):
        record = archive.store(self.source, self.root)
        target = archive.resolve(record, self.root)
        target.write_bytes(b'X'*record['bytes'])
        with self.assertRaisesRegex(EvidenceError, 'archive_object_digest'):
            archive.store(self.source, self.root)
        self.assertEqual(target.read_bytes(), b'X'*record['bytes'])

    def test_missing_wrong_root_traversal_and_unknown_schema_fail_closed(self):
        record = archive.store(self.source, self.root)
        for change, reason in (({'object': '../outside'}, 'archive_reference_object'),
                               ({'schema_version': 2}, 'archive_reference_schema'),
                               ({'bytes': True}, 'archive_reference_bytes'),
                               ({'archive_root': '/another/archive'}, 'archive_reference_root')):
            with self.subTest(change=change), self.assertRaisesRegex(EvidenceError, reason):
                archive.resolve({**record, **change}, self.root)
        (self.root/'archive.root.json').write_text('{"kind":"another_archive"}')
        with self.assertRaisesRegex(EvidenceError, 'archive_root_identity_mismatch'):
            archive.resolve(record, self.root)

    def test_sidecar_resolves_without_recreating_large_file_in_source_tree(self):
        record = archive.store(self.source, self.root)
        sidecar = self.source.with_name(self.source.name+'.archive.json')
        sidecar.write_text(json.dumps(record)); self.source.unlink()
        self.assertEqual(archive.locate(self.source, self.root).read_bytes(), b'\x00actual archived bytes\xff'*100)
        self.assertFalse(self.source.exists())

    def test_source_change_during_store_does_not_publish_object(self):
        with patch.object(archive, '_sha', return_value='0'*64):
            with self.assertRaisesRegex(EvidenceError, 'archive_source_changed_during_copy'):
                archive.store(self.source, self.root)
        self.assertEqual(list((self.root/'objects/sha256').rglob('*')), [])

    def test_native_primary_roundtrip_uses_external_sidecar(self):
        from ..portable_primary import create_native_bundle, restore_native_bundle
        folder = Path(self.temp.name)/'bundle'
        create_native_bundle({'signals.csv': self.source}, folder, dictionary_bytes=8*1024**2)
        payload = folder/'primary.tar.xz'
        record = archive.store(payload, self.root)
        payload.with_name(payload.name+'.archive.json').write_text(json.dumps(record))
        payload.unlink()
        output = Path(self.temp.name)/'restored'
        with patch.dict('os.environ', {archive.ROOT_ENV: str(self.root)}):
            restore_native_bundle(folder/'bundle.json', output)
        self.assertEqual((output/'signals.csv').read_bytes(), self.source.read_bytes())
        self.assertFalse(payload.exists())


if __name__ == '__main__':
    unittest.main()
