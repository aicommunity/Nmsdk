"""Recover long logical member names from a short destination without model runs."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..external_archive import _native_path
from ..native_evidence import EvidenceError
from ..portable_primary import create_native_bundle, restore_native_bundle
from ..source_envelope_bundle import create as create_enveloped


class LongDescendantRestorationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='primary-long-members-')
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        # The production operation is given an ordinary short path. Only
        # independent readback/cleanup qualify paths explicitly in this fixture.
        self.addCleanup(self.remove_scoped_tree)
        self.source = self.root/'source'
        self.source.write_bytes(b'original primary bytes\x00\xff\n')
        self.name = '/'.join(['original-Train', 'native', 'events-'+100*'a',
                              'retained-'+100*'b', 'NeuroModeler.INFO.20261123'])

    def remove_scoped_tree(self):
        target = self.root.absolute()
        self.assertEqual(target, Path(self.temporary.name).absolute())
        self.assertTrue(target.name.startswith('primary-long-members-'))
        shutil.rmtree(_native_path(target, long_descendants=True))

    def assert_recovered(self, output, name, expected=None):
        member = output/name
        self.assertGreater(len(str(member.absolute())), 260)
        actual = _native_path(member)
        self.assertTrue(actual.is_file())
        self.assertFalse(actual.is_symlink())
        self.assertEqual(actual.read_bytes(), self.source.read_bytes() if expected is None else expected)

    def test_short_destination_recovers_long_members_in_both_wire_versions(self):
        for version2 in (False, True):
            with self.subTest(content_references=version2):
                package = self.root/('bundle-'+str(version2))
                output = self.root/('restored-'+str(version2))
                self.assertLess(len(str(output.absolute())), 240)
                names = [self.name, 'second-copy/'+self.name]
                create_native_bundle({n:self.source for n in names}, package,
                    dictionary_bytes=8*1024**2, deduplicate_content=version2)
                original_archive = (package/'primary.tar.xz').read_bytes()
                receipt = restore_native_bundle(package/'bundle.json', output)
                self.assertEqual(receipt['archive_members_verified'], 2)
                self.assertEqual(receipt['retained_regular_files'], 2)
                self.assertFalse(receipt['native_execution_attested'])
                for name in names:self.assert_recovered(output, name)
                self.assertFalse(os.path.samefile(*[_native_path(output/n) for n in names]))
                self.assertEqual((package/'primary.tar.xz').read_bytes(), original_archive)

    def test_envelope_recipes_and_literal_fallback_keep_long_names_and_reject_overlap(self):
        package = self.root/'enveloped'
        self.source.write_bytes(b'{"retained_source":true}\n')
        literal = 'literal-job/'+self.name
        target = 'reconstructed-job/'+self.name
        job = self.root/'job'
        raw_job = (json.dumps(dict(source_stopped=dict(retained_source=True), role='job'),
                              indent=2)+'\n').encode('utf-8')
        job.write_bytes(raw_job)
        packed = create_enveloped({self.name:self.source, literal:self.source, target:job},
            [dict(target=name, source=self.name) for name in (literal, target)], package,
            maximum_total_bytes=1024**2, dictionary_bytes=8*1024**2)
        self.assertEqual(packed['factored_files'], 1)
        self.assertEqual(packed['literal_fallbacks'], {literal:'unsupported_encoding'})
        for invalid in (package/'nested', _native_path(package/'nested', long_descendants=True)):
            with self.assertRaisesRegex(EvidenceError, 'new_separate_restore_required'):
                restore_native_bundle(package/'bundle.json', invalid)
        self.assertFalse((package/'nested').exists())
        output = self.root/'envelope-restored'
        receipt = restore_native_bundle(package/'bundle.json', output)
        self.assertTrue(receipt['all_primary_bytes_verified'])
        self.assertEqual(receipt['restored_files'], 3)
        self.assertEqual(receipt['reconstructed_job_files'], 1)
        self.assertFalse(receipt['native_execution_attested'])
        for name in (self.name, literal):self.assert_recovered(output, name)
        self.assert_recovered(output, target, raw_job)
