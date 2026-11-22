"""Recover the complete closed long-Train archive from the central CAS.

This checks all original bytes, including full histories and negative outcomes.
Restoration does not create an execution, convergence or scientific certificate.
"""
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..external_archive import locate, resolve
from ..native_evidence import load
from ..portable_primary import RETAIN_ALIASES, restore_native_bundle
from ..runtime import file_record


class CompleteLongPrimaryRestoreTest(unittest.TestCase):
    def test_all_original_members_restore_from_the_verified_external_objects(self):
        package = Path(os.environ['TIMELEARNER_COMPLETE_LONG_PRIMARY_PUBLICATION'])
        metadata = locate(package/'bundle.json')
        bundle = load(metadata)
        reference = load(package/'primary.tar.xz.archive.json')
        archive = resolve(reference)
        before = file_record(archive)
        self.assertEqual(bundle['archive_sha256'],
            '0997ee3e6b71c5576c0d65a55c1fdd6f76513c3d7a83c6b42c1af97e07d0a92a')
        self.assertEqual(bundle['archive_sha256'], reference['sha256'])
        self.assertEqual(bundle['expanded_bytes'], 12647050963)
        self.assertEqual(bundle['archive_bytes'], 148792604)
        names = set(bundle['members'])
        self.assertTrue(any(n.endswith('train_stopped_state.json') for n in names))
        # Only the disposable recovery cache is removed after complete hashing.
        with tempfile.TemporaryDirectory(prefix='complete-long-primary-restore-',
                                         dir=os.environ['TMPDIR']) as temporary:
            root = Path(temporary); local = root/'package';local.mkdir()
            (local/'bundle.json').write_bytes(metadata.read_bytes())
            (local/'primary.tar.xz.archive.json').write_text(json.dumps(reference), encoding='utf-8')
            receipt = restore_native_bundle(local/'bundle.json',root/'restored',compatibility=RETAIN_ALIASES)
            self.assertEqual(receipt['archive_members_verified'], len(names))
            self.assertEqual(receipt['retained_regular_files'], len(names))
            self.assertEqual(receipt['omitted_redundant_aliases'], [])
            self.assertFalse(receipt['source_archive_modified'])
            self.assertFalse(receipt['native_execution_attested'])
        self.assertEqual(file_record(archive), before)
        proof = dict(kind='timelearner_complete_long_primary_restoration_proof',schema_version=1,
            archive_reference=reference,source_archive=before,restoration=receipt,
            expanded_bytes=bundle['expanded_bytes'],all_original_member_bytes_verified=True,
            disposable_recovery_cache_removed=True,scientific_verdict=None)
        (Path(os.environ['TMPDIR'])/'complete-long-primary-restoration-proof.json').write_text(
            json.dumps(proof,indent=2,allow_nan=False)+'\n',encoding='utf-8')
