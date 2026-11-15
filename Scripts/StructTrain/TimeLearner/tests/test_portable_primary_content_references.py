"""Production bundle2 roundtrips of retained native primary, without model runs."""
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..portable_primary import (ALIAS_ADAPTER, create_native_bundle,
                                restore_native_bundle, _sha)
from . import test_portable_primary as original


class ContentReferencePrimaryTest(unittest.TestCase):
    def setUp(self):
        original.PortablePrimaryTest.setUp(self)

    def pack(self, names=('a', 'b')):
        source = self.root/'retained-log';source.write_bytes(self.files[self.target])
        directory = self.root/'packed'
        bundle = create_native_bundle({name: source for name in names}, directory,
            dictionary_bytes=8*1024**2, deduplicate_content=True)
        return directory, bundle

    def rewrite_archive(self, directory, bundle, change):
        with tarfile.open(directory/'primary.tar.xz', 'r:xz') as archive:
            entries = [(member, archive.extractfile(member).read() if member.isfile() else None)
                       for member in archive]
        entries = change(entries)
        with tarfile.open(directory/'primary.tar.xz', 'w:xz') as archive:
            for member, raw in entries:
                archive.addfile(member, io.BytesIO(raw) if raw is not None else None)
        bundle['archive_bytes'] = (directory/'primary.tar.xz').stat().st_size
        bundle['archive_sha256'] = _sha(directory/'primary.tar.xz')
        (directory/'bundle.json').write_text(json.dumps(bundle), encoding='utf-8')

    def test_native_alias_and_duplicate_content_restore_as_independent_regular_files(self):
        sources = {}
        for i, (name, raw) in enumerate(self.files.items()):
            source = self.root/str(i);source.write_bytes(raw);sources[name] = source
        sources['copies/retained-log'] = sources[self.target]
        directory = self.root/'packed'
        bundle = create_native_bundle(sources, directory, dictionary_bytes=8*1024**2,
                                      deduplicate_content=True)
        self.assertEqual(bundle['schema_version'], 2)
        with tarfile.open(directory/'primary.tar.xz', 'r:xz') as archive:
            entries = list(archive)
        self.assertTrue(any(member.islnk() for member in entries))
        self.assertFalse(any(member.issym() for member in entries))
        result = restore_native_bundle(directory/'bundle.json', self.root/'out', compatibility=ALIAS_ADAPTER)
        self.assertEqual(result['archive_members_verified'], len(sources))
        first, second = self.root/'out'/self.target, self.root/'out/copies/retained-log'
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertFalse(os.path.samefile(first, second))
        second.write_bytes(b'changed derived copy')
        self.assertEqual(first.read_bytes(), self.files[self.target])
        self.assertFalse(result['source_archive_modified'])
        self.assertFalse(result['native_execution_attested'])

    def test_unknown_bundle_version_is_refused_before_creating_output(self):
        directory, bundle = self.pack();bundle['schema_version'] = 999
        (directory/'bundle.json').write_text(json.dumps(bundle), encoding='utf-8')
        with self.assertRaisesRegex(EvidenceError, 'bundle_schema_invalid'):
            restore_native_bundle(directory/'bundle.json', self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_reference_to_missing_or_forward_target_is_refused(self):
        directory, bundle = self.pack()
        def change(entries):
            reference = next(row for row in entries if row[0].islnk())
            return [reference]+[row for row in entries if row is not reference]
        self.rewrite_archive(directory, bundle, change)
        with self.assertRaisesRegex(EvidenceError, 'bundle_content_reference_invalid'):
            restore_native_bundle(directory/'bundle.json', self.root/'out')

    def test_reference_chain_is_not_treated_as_a_regular_target(self):
        directory, bundle = self.pack(('a', 'b', 'c'))
        def change(entries):
            entries[-1][0].linkname = entries[1][0].name
            return entries
        self.rewrite_archive(directory, bundle, change)
        with self.assertRaisesRegex(EvidenceError, 'bundle_content_reference_invalid'):
            restore_native_bundle(directory/'bundle.json', self.root/'out')

    def test_rehashed_archive_cannot_substitute_a_different_content_target(self):
        first = self.root/'log';first.write_bytes(self.files[self.target])
        second = self.root/'owner';second.write_bytes(self.files[self.owner])
        directory = self.root/'packed'
        bundle = create_native_bundle({'a':first, 'b':first, 'c':second}, directory,
            dictionary_bytes=8*1024**2, deduplicate_content=True)
        def change(entries):
            reference = next(member for member, _ in entries if member.islnk())
            reference.linkname = 'c'
            return [row for row in entries if row[0].isfile()]+[row for row in entries if row[0].islnk()]
        self.rewrite_archive(directory, bundle, change)
        with self.assertRaisesRegex(EvidenceError, 'bundle_content_reference_invalid'):
            restore_native_bundle(directory/'bundle.json', self.root/'out')

    def test_false_logical_byte_total_is_refused_before_output(self):
        directory, bundle = self.pack();bundle['expanded_bytes'] -= 1
        (directory/'bundle.json').write_text(json.dumps(bundle), encoding='utf-8')
        with self.assertRaisesRegex(EvidenceError, 'bundle_content_reference_totals_invalid'):
            restore_native_bundle(directory/'bundle.json', self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_legacy_regular_bundle_cannot_acquire_content_references(self):
        directory, bundle = self.pack();bundle['schema_version'] = 1
        (directory/'bundle.json').write_text(json.dumps(bundle), encoding='utf-8')
        with self.assertRaisesRegex(EvidenceError, 'bundle_member_type_duplicate_or_unknown'):
            restore_native_bundle(directory/'bundle.json', self.root/'out')


class LargeContentReferencePrimaryTest(unittest.TestCase):
    def test_actual_model_larger_than_dictionary_is_stored_once_and_restores_exact_copies(self):
        source = Path(os.environ['TIMELEARNER_LARGE_BUNDLE_SOURCE'])/'classic.qz'
        self.assertGreater(source.stat().st_size, 32*1024**2)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder);before = _sha(source)
            sources = {'first/model.qz':source, 'second/model.qz':source}
            regular = create_native_bundle(sources, root/'regular', dictionary_bytes=32*1024**2)
            compact = create_native_bundle(sources, root/'compact', dictionary_bytes=32*1024**2,
                                           deduplicate_content=True)
            self.assertLess(compact['archive_bytes'], .75*regular['archive_bytes'])
            self.assertEqual(compact['expanded_bytes'], 2*source.stat().st_size)
            self.assertEqual(compact['unique_content_bytes'], source.stat().st_size)
            restored = restore_native_bundle(root/'compact/bundle.json', root/'restored')
            for name in sources:self.assertEqual(_sha(root/'restored'/name), before)
            self.assertFalse(os.path.samefile(root/'restored/first/model.qz', root/'restored/second/model.qz'))
            self.assertEqual(_sha(source), before)
            self.assertFalse(restored['native_execution_attested'])
            print(json.dumps({'kind':'actual_large_primary_content_reference_comparison',
                'source_bytes':source.stat().st_size, 'source_sha256':before,
                'schema1_archive_bytes':regular['archive_bytes'], 'schema2_archive_bytes':compact['archive_bytes'],
                'all_logical_copies_restored':True, 'native_model_executed':False}))
