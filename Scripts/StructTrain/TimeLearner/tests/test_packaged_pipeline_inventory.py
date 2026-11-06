"""Archive closure over original native schema1/2/3/4 producer snapshots."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest

from ..artifact_bundle import (verify_packaged_run_closure, verify_packaged_run_inventory,
                               verify_pipeline_archive)
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load


class PackagedPipelineInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_PACKAGED_PIPELINE_FIXTURES')
        if not value:
            raise unittest.SkipTest('requires original native schema1..4 snapshots restored from Git archives')
        root = Path(value);descriptor = load(root/'fixtures.json')
        cls.files = {}
        for record in descriptor['files']:
            raw = (root/record['path']).read_bytes()
            if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
                raise AssertionError('original fixture bytes changed: '+record['path'])
            cls.files[record['path']] = raw
        cls.records = {name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                       for name, raw in cls.files.items()}
        cls.manifests = {name: raw for name, raw in cls.files.items() if name.endswith('/run-manifest.json')}
        if len(cls.manifests) != 6 or {json.loads(raw)['schema_version'] for raw in cls.manifests.values()} != {1, 2, 3, 4}:
            raise AssertionError('requires six original native runs spanning schema1..4')

    def archive(self, directory, mutation=None):
        path = Path(directory)/'primary.tar.xz'
        with tarfile.open(path, 'w:xz', preset=1) as tar:
            for index, (name, raw) in enumerate(self.files.items()):
                item = tarfile.TarInfo('../escape' if index == 0 and mutation == 'traversal' else name)
                item.size = len(raw)
                if index == 0 and mutation == 'link':
                    item.type = tarfile.SYMTYPE;item.linkname = '../outside';item.size = 0;tar.addfile(item)
                else:
                    tar.addfile(item, io.BytesIO(raw))
                if index == 0 and mutation == 'duplicate':
                    tar.addfile(item, io.BytesIO(raw))
        return path, {'archive_bytes': path.stat().st_size,
                      'archive_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'members': copy.deepcopy(self.records)}

    def test_actual_versions_and_cold_import_roles_agree_between_byte_and_inventory_apis(self):
        actual = verify_packaged_run_closure(self.files)
        self.assertEqual(actual, verify_packaged_run_inventory(self.records, self.manifests))
        self.assertEqual(actual['run_snapshots_verified'], 6)
        self.assertEqual(actual['artifact_entries_verified'], len(self.files)-6)
        self.assertIsNone(actual['scientific_verdict'])
        self.assertNotIn('validity', actual)
        self.assertNotIn('execution', actual)

    def test_primary_input_source_cannot_be_filtered_as_a_code_cache(self):
        missing = {name: raw for name, raw in self.files.items() if '/input/source/' not in name}
        self.assertLess(len(missing), len(self.files))
        with self.assertRaisesRegex(EvidenceError, 'packaged_run_missing_artifact'):
            verify_packaged_run_closure(missing)

    def test_damaged_csv_and_unregistered_bytes_are_rejected(self):
        name = next(name for name in self.files if name.endswith('.csv'))
        changed = dict(self.files);changed[name] += b'damaged'
        with self.assertRaisesRegex(EvidenceError, 'packaged_run_artifact_bytes_changed'):
            verify_packaged_run_closure(changed)
        changed = dict(self.files)
        name = next(iter(self.manifests)).removesuffix('run-manifest.json')+'unrecorded.txt'
        changed[name] = b'extra'
        with self.assertRaisesRegex(EvidenceError, 'packaged_run_has_unrecorded_artifacts'):
            verify_packaged_run_closure(changed)

    def test_rehashed_unknown_and_mismatched_schema_operation_are_rejected(self):
        for name, raw in self.manifests.items():
            original = json.loads(raw)
            changes = [dict(schema_version=True), dict(schema_version=999), dict(operation='invented')]
            if original['schema_version'] == 3:
                changes.append(dict(schema_version=2))
            if original['operation'] == 'preflight':
                changes.append(dict(schema_version=3))
            changes.append(dict(kind='timelearner_calibration_run_manifest', schema_version=2))
            for mutation in changes:
                changed = {**original, **mutation}
                changed['sha256'] = sha({k: v for k, v in changed.items() if k != 'sha256'})
                files = {**self.files, name: json.dumps(changed).encode()}
                with self.subTest(name=name, mutation=mutation), self.assertRaises(EvidenceError):
                    verify_packaged_run_closure(files)

    def test_inventory_cannot_omit_or_change_the_actual_manifest_bytes(self):
        manifests = dict(self.manifests);manifests.pop(next(iter(manifests)))
        with self.assertRaisesRegex(EvidenceError, 'packaged_run_manifest_set_changed'):
            verify_packaged_run_inventory(self.records, manifests)
        manifests = dict(self.manifests);name = next(iter(manifests));manifests[name] += b' '
        with self.assertRaisesRegex(EvidenceError, 'packaged_run_manifest_bytes_changed'):
            verify_packaged_run_inventory(self.records, manifests)
        records = copy.deepcopy(self.records);records[name]['bytes'] = True
        with self.assertRaisesRegex(EvidenceError, 'invalid_packaged_run_inventory_record'):
            verify_packaged_run_inventory(records, self.manifests)

    def test_streamed_original_bytes_and_declared_inventory_are_both_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            path, bundle = self.archive(directory)
            proof = verify_pipeline_archive(path, bundle)
            self.assertEqual(proof['run_snapshots_verified'], 6)
            self.assertEqual(proof['archive_members_verified'], len(self.files))
            self.assertIsNone(proof['scientific_verdict'])
            with self.assertRaisesRegex(EvidenceError, 'pipeline_archive_exceeds_budget'):
                verify_pipeline_archive(path, bundle, maximum_bytes=sum(x['bytes'] for x in self.records.values())-1)
            changed = copy.deepcopy(bundle);changed['archive_sha256'] = '0'*64
            with self.assertRaisesRegex(EvidenceError, 'pipeline_archive_checksum_mismatch'):
                verify_pipeline_archive(path, changed)
            changed = copy.deepcopy(bundle);changed['members'][next(iter(self.files))]['sha256'] = '0'*64
            with self.assertRaisesRegex(EvidenceError, 'pipeline_archive_member_bytes_changed'):
                verify_pipeline_archive(path, changed)

    def test_links_duplicate_members_and_traversal_reject_even_with_new_archive_checksum(self):
        for mutation in ('link', 'duplicate', 'traversal'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                path, bundle = self.archive(directory, mutation)
                with self.assertRaises(EvidenceError):
                    verify_pipeline_archive(path, bundle)
