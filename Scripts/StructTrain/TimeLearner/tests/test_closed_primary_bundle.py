"""Real archive/filesystem contracts; mocked kernel transport is not attestation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import archive_retirement, closed_primary_bundle as subject, portable_primary
from ..native_evidence import EvidenceError
from .test_owned_python_job import request
from ..owned_python_job import validate_request


class ClosedPrimaryBundleTest(unittest.TestCase):
    def fixture(self, root):
        base = root/'base';source = base/'readbacks'/'source';source.mkdir(parents=True)
        unit = source/'process'/'contained';unit.mkdir(parents=True)
        (unit/'owned-unit.json').write_text('{}')
        (source/'model.bin').write_bytes(b'unique model bytes')
        log = source/'NeuroModeler.test.log.INFO.20261111-000000.123';log.write_bytes(b'original log')
        (source/'NeuroModeler.INFO').symlink_to(log.name)
        manifest = dict(kind='timelearner_closed_primary_bundle', schema_version=1,
            base=str(base), roots=[], closed_units=[{'directory': str(unit), 'binding': {'fixture': 'transport'}}],
            bounds={'maximum_file_bytes': 1024, 'maximum_total_bytes': 4096,
                    'maximum_archive_bytes': 1024**2}, scientific_verdict=None)
        self.inventory(manifest, source)
        return manifest, source, base

    def inventory(self, manifest, source):
        snapshot = archive_retirement.snapshot(source.parent, [source.name])
        manifest['roots'] = [{'directory': str(source), 'prefix': 'original-job',
            'files': {n:{'bytes':r['bytes'], 'sha256':r['sha256']}
                      for n,r in snapshot['regular'][source.name].items()},
            'links': snapshot['links'][source.name]}]

    def test_streamed_archive_roundtrip_retains_every_model_and_alias_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);m,s,b = self.fixture(root);events = {}
            state = {'binding': m['closed_units'][0]['binding'], 'all_processes_closed': True}
            with patch.object(subject, 'BASES', {b}), patch.object(subject.contained_process, 'inspect', return_value=state):
                bundle = subject.collect(m, root/'bundle', lambda: None, events.__setitem__)
            self.assertEqual(set(bundle['members']), {'original-job/'+n for n in
                [*m['roots'][0]['files'], *m['roots'][0]['links']]})
            portable_primary.restore_native_bundle(root/'bundle/bundle.json', root/'restored',
                compatibility=portable_primary.ALIAS_ADAPTER)
            self.assertEqual((root/'restored/original-job/model.bin').read_bytes(), b'unique model bytes')
            self.assertIsNone(events['primary-bundle-proof.json']['scientific_verdict'])
            self.assertTrue(events['primary-bundle-proof.json']['original_outcome_unchanged'])

    def test_live_unit_refuses_before_archive_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);m,s,b = self.fixture(root)
            state = {'binding': m['closed_units'][0]['binding'], 'all_processes_closed': False}
            with patch.object(subject, 'BASES', {b}), patch.object(subject.contained_process, 'inspect', return_value=state):
                with self.assertRaisesRegex(EvidenceError, 'unit_not_closed'):
                    subject.collect(m, root/'bundle', lambda: None, lambda *args: None)
            self.assertFalse((root/'bundle').exists())

    def test_changed_and_extra_source_files_cannot_pass_subset_hashes(self):
        for change in ('modified', 'extra'):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory);m,s,b = self.fixture(root)
                if change == 'modified':(s/'model.bin').write_bytes(b'X'*len((s/'model.bin').read_bytes()))
                else:(s/'extra').write_bytes(b'unexpected')
                with patch.object(subject, 'BASES', {b}), self.assertRaisesRegex(EvidenceError, 'namespace_changed'):
                    subject.verify_sources(m)

    def test_undeclared_binding_file_is_not_hidden_as_opaque_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);m,s,b = self.fixture(root)
            other = s/'another';other.mkdir();(other/'owned-unit.json').write_text('{}')
            self.inventory(m,s)
            with patch.object(subject, 'BASES', {b}), self.assertRaisesRegex(EvidenceError, 'unit_inventory_changed'):
                subject.verify_sources(m)

    def test_alias_escape_and_unknown_schema_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);m,s,b = self.fixture(root)
            for field in ('alias', 'schema'):
                changed = copy.deepcopy(m)
                if field == 'alias':changed['roots'][0]['links']['NeuroModeler.INFO']['link_text'] = '../model.bin'
                else:changed['schema_version'] = 2
                with patch.object(subject, 'BASES', {b}), self.assertRaises(EvidenceError):
                    subject.validate_manifest(changed)

    def test_budget_and_output_overlap_are_not_silently_adjusted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);m,s,b = self.fixture(root)
            with patch.object(subject, 'BASES', {b}):
                with self.assertRaisesRegex(EvidenceError, 'output_overlaps_source'):
                    subject.resources(m, s/'output', root/'manifest.json', root)
                changed = copy.deepcopy(m);changed['bounds']['maximum_total_bytes'] = 1024
                changed['roots'][0]['files']['model.bin']['bytes'] = 1024
                with self.assertRaisesRegex(EvidenceError, 'total_bytes_exceeded'):
                    subject.validate_manifest(changed)

    def test_operation_is_explicit_and_manifest_bound(self):
        value = request();value['operation'] = {'kind': 'closed-primary-bundle',
            'manifest': {'path': value['execution_root']+'/requests/manifest.json', 'sha256': 'c'*64}}
        self.assertEqual(validate_request(value), value)
        value['operation']['shell_command'] = 'never accepted'
        with self.assertRaisesRegex(EvidenceError, 'primary_bundle_schema'):
            validate_request(value)

    def test_source_mutation_after_pack_never_emits_completed_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);m,s,b = self.fixture(root);events = {}
            state = {'binding': m['closed_units'][0]['binding'], 'all_processes_closed': True}
            original_pack = portable_primary.create_native_bundle
            def pack_then_change(*args, **kwargs):
                result = original_pack(*args, **kwargs)
                (s/'model.bin').write_bytes(b'changed after packing')
                return result
            with patch.object(subject, 'BASES', {b}), \
                 patch.object(subject.contained_process, 'inspect', return_value=state), \
                 patch.object(subject.portable_primary, 'create_native_bundle', side_effect=pack_then_change):
                with self.assertRaisesRegex(EvidenceError, 'namespace_changed'):
                    subject.collect(m, root/'bundle', lambda: None, events.__setitem__)
            self.assertNotIn('primary-bundle-proof.json', events)
