"""Exercise production archive I/O, collision handling and tamper rejection."""
import json
import gzip
from pathlib import Path
import subprocess
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
        index = folder/'bundle.json'; index_record = archive.store(index, self.root)
        index.with_name(index.name+'.archive.json').write_text(json.dumps(index_record)); index.unlink()
        output = Path(self.temp.name)/'restored'
        with patch.dict('os.environ', {archive.ROOT_ENV: str(self.root)}):
            restore_native_bundle(folder/'bundle.json', output)
        self.assertEqual((output/'signals.csv').read_bytes(), self.source.read_bytes())
        self.assertFalse(payload.exists())

    def test_json_reader_keeps_compression_and_integer_precision(self):
        from ..native_evidence import load
        path = Path(self.temp.name)/'metadata.json.gz'
        path.write_bytes(gzip.compress(b'{"timestamp_ns":1794650123456789123}\n'))
        reference = archive.store(path, self.root)
        path.with_name(path.name+'.archive.json').write_text(json.dumps(reference)); path.unlink()
        with patch.dict('os.environ', {archive.ROOT_ENV: str(self.root)}):
            self.assertEqual(load(path), {'timestamp_ns': 1794650123456789123})

    def test_materialization_is_explicit_and_never_overwrites_different_bytes(self):
        record = archive.store(self.source, self.root)
        cache = Path(self.temp.name)/'cache'/'native-state.bin'
        archive.materialize(record, cache, self.root)
        self.assertEqual(archive.materialize(record, cache, self.root).read_bytes(), self.source.read_bytes())
        cache.write_bytes(b'user modification')
        with self.assertRaisesRegex(EvidenceError, 'archive_cache_collision'):
            archive.materialize(record, cache, self.root)
        self.assertEqual(cache.read_bytes(), b'user modification')

    def test_publication_view_keeps_checksums_and_restores_external_primary(self):
        from ..portable_primary import create_native_bundle, restore_native_bundle
        source = Path(self.temp.name)/'native-package'
        create_native_bundle({'signals.csv': self.source}, source, dictionary_bytes=8*1024**2)
        before = {p.name: p.read_bytes() for p in source.iterdir()}
        output = Path(self.temp.name)/'publication'
        receipt = archive.prepare_publication(source, output, self.root)
        self.assertIsNone(receipt['scientific_verdict'])
        self.assertEqual(receipt['payloads_externalized'], 1)
        self.assertFalse((output/'package/primary.tar.xz').exists())
        self.assertEqual((output/'package/bundle.json').read_bytes(), before['bundle.json'])
        self.assertEqual({p.name: p.read_bytes() for p in source.iterdir()}, before)
        with patch.dict('os.environ', {archive.ROOT_ENV: str(self.root)}):
            restore_native_bundle(output/'package/bundle.json', Path(self.temp.name)/'publication-restored')
        self.assertEqual((Path(self.temp.name)/'publication-restored/signals.csv').read_bytes(), self.source.read_bytes())


    def test_private_revision_alias_is_shared_with_linked_worktree(self):
        from ..history import resolve_revision
        repo = Path(self.temp.name)/'private-source'; repo.mkdir()
        def git(*args):
            return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.STDOUT).decode().strip()
        git('init', '-b', 'main'); git('config', 'user.name', 'Archive test')
        git('config', 'user.email', 'archive@example.invalid')
        (repo/'code.txt').write_text('preserved code')
        git('add', '.'); git('commit', '-m', 'preserved source'); final = git('rev-parse', 'HEAD')
        common = Path(git('rev-parse', '--path-format=absolute', '--git-common-dir'))
        aliases = common/'info/structtrain-root-revision-aliases.json'
        aliases.write_text(json.dumps({'kind': 'nmsdk_root_revision_aliases', 'schema_version': 1,
                                      'mapping': {'1'*40: final}}))
        linked = Path(self.temp.name)/'linked-private-source'
        git('worktree', 'add', '--detach', str(linked), final)
        self.assertEqual(resolve_revision(linked, '1'*40)['resolved_revision'], final)
        aliases.write_text(json.dumps({'kind': 'nmsdk_root_revision_aliases', 'schema_version': 1,
                                      'mapping': {'1'*40: '2'*40, '2'*40: '1'*40}}))
        with self.assertRaisesRegex(EvidenceError, 'cyclic_root_revision_map'):
            resolve_revision(linked, '1'*40)

    def test_historical_reader_composes_rewrites_and_preserves_exact_bytes(self):
        from ..history import read_bytes, resolve_revision
        repo = Path(self.temp.name)/'source'; repo.mkdir()
        def git(*args):
            return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.STDOUT).decode().strip()
        git('init', '-b', 'original'); git('config', 'user.name', 'Archive test')
        git('config', 'user.email', 'archive@test.invalid')
        (repo/'note.txt').write_text('original')
        git('add', '.'); git('commit', '-m', 'original'); original = git('rev-parse', 'HEAD')
        (repo/'note.txt').write_text('intermediate')
        git('add', '.'); git('commit', '-m', 'intermediate'); intermediate = git('rev-parse', 'HEAD')
        record = archive.store(self.source, self.root)
        (repo/'primary.tar.xz.archive.json').write_text(json.dumps(record))
        git('add', '.'); git('commit', '-m', 'external reference'); final = git('rev-parse', 'HEAD')
        maps = repo/'Docs/StructTrain/TimeLearner/History'; maps.mkdir(parents=True)
        for name, mapping in (('2026-10-30', {original: intermediate}), ('2026-11-14', {intermediate: final})):
            (maps/('RootRevisionMap-'+name+'.json')).write_text(json.dumps({
                'kind': 'nmsdk_root_revision_aliases', 'schema_version': 1, 'mapping': mapping}))
        self.assertEqual(resolve_revision(repo, original)['resolved_revision'], final)
        with patch.dict('os.environ', {archive.ROOT_ENV: str(self.root)}):
            self.assertEqual(read_bytes(repo, original, 'primary.tar.xz'), self.source.read_bytes())
            with self.assertRaisesRegex(EvidenceError, 'historical_blob_budget_exceeded'):
                read_bytes(repo, original, 'primary.tar.xz', maximum_bytes=1)
            with self.assertRaisesRegex(EvidenceError, 'historical_blob_or_archive_reference_missing'):
                read_bytes(repo, original, 'missing.tar.xz')


if __name__ == '__main__':
    unittest.main()
