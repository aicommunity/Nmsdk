"""Replay a real closed C++ source export; its enclosing test failed.

This is diagnostic DATA acceptance, never a successful model roundtrip or a
classification result. The required original archive must not be synthesized.
"""
from copy import deepcopy
import hashlib
import json
import os
import shutil
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..composite_primary import filesystem_primary_resolver
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError, load, require
from ..portable_primary import restore_native_bundle
from ..native_pipeline_worker import _snapshot_source


def resign(document):
    document['sha256']=digest({k:v for k,v in document.items() if k!='sha256'})
    return document


class ClosedNativePackage7SourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value=os.environ.get('TIMELEARNER_CLOSED_PACKAGE7_SOURCE')
        require(value is not None,'closed_native_package7_fixture_required')
        cls.root=Path(value)
        require(cls.root.is_dir() and not cls.root.is_symlink(),'closed_native_package7_fixture_missing')
        cls.origin=load(cls.root/'ORIGIN.json');cls.bundle=load(cls.root/'bundle.json')
        require(cls.origin['source_commit']=='3edb22a4cf80b76fbae4deb379ec510ebfac0fcf' and
                cls.origin['original_selected_test']=='NativeRecoveryPackage7/ClassicN0StoppedRoundtripKeepsResponse'
                and cls.origin['original_test_outcome']=='failed' and
                cls.origin['imported_response_verified'] is False and cls.origin['scientific_verdict'] is None,
                'closed_native_package7_original_failure_scope')
        cls.scratch=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.scratch.cleanup)
        cls.restored=Path(cls.scratch.name)/'original'
        cls.restoration=restore_native_bundle(cls.root/'bundle.json',cls.restored)
        cls.directory=cls.restored/'case/native-composite/package7'
        cls.package=load(cls.directory/'source-package.json')
        cls.summary=load(cls.directory/'source-summary.json')
        # Functions stored on a class otherwise bind a spurious `self` when
        # used by individual tests; keep the production resolver unchanged.
        cls.resolver=staticmethod(filesystem_primary_resolver(cls.directory))
        before=deepcopy((cls.package,cls.summary))
        cls.audit=audit_candidate_window_recovery_package(cls.package,cls.summary,external_resolver=cls.resolver)
        require((cls.package,cls.summary)==before,'closed_native_package7_auditor_mutated_input')
        # Captured by the owned validation process, alongside its test log.
        print(json.dumps({'kind':'closed_native_package7_source_audit','schema_version':1,
            'original_test_outcome':'failed','restoration':cls.restoration,'audit':cls.audit,
            'scientific_verdict':None},sort_keys=True))

    def test_entire_original_bundle_is_restored_and_hash_checked(self):
        self.assertEqual(self.restoration['archive_members_verified'],len(self.bundle['members']))
        self.assertFalse(self.restoration['source_archive_modified'])
        self.assertFalse(self.restoration['native_execution_attested'])

    def test_actual_stopped_package_and_summary8_bind_the_same_model(self):
        self.assertEqual(self.package['schema_version'],7)
        self.assertEqual(self.package['kind'],'timelearner_stopped_state')
        self.assertEqual(self.audit['model_revision'],self.package['model_revision'])
        self.assertTrue(self.audit['summary_checked'])
        self.assertEqual(self.audit['summary']['summary_schema_version'],8)
        self.assertIsNone(self.audit['exact']);self.assertFalse(self.audit['certificate_consistent'])

    def test_nonempty_actual_recovery_deliveries_replay_their_original_runtime3(self):
        ledger=self.audit['recovery_ledger']
        self.assertGreater(ledger['deliveries_checked'],0)
        self.assertGreater(ledger['primary_files_checked'],0)
        self.assertTrue(ledger['event_bindings_verified'])
        self.assertFalse(ledger['service_ledger_completeness_verified'])
        for row in self.package['recovery_ledger']['deliveries']:
            self.assertEqual(row['runtime_plan']['schema_version'],3)
            self.assertEqual(row['event']['transition']['run_id'],row['runtime_plan']['run_id'])

    def test_data_acceptance_does_not_promote_original_failed_execution(self):
        self.assertEqual(self.origin['original_test_outcome'],'failed')
        for field in ('terminal_provenance_verified','native_import_verified','native_execution_verified',
                      'live_authority_restored'):
            self.assertFalse(self.audit[field])
        self.assertIsNone(self.audit['evaluation_verdict'])
        self.assertFalse(self.summary['contains_controller_checkpoint'])

    def test_actual_summary_cannot_claim_checkpoint_or_drop_ledger(self):
        for field,value,reason in [('contains_controller_checkpoint',True,'recovery_summary_is_not_checkpoint'),
                                   ('recovery_ledger',None,'domain_recomputed')]:
            changed=deepcopy(self.summary);changed[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(EvidenceError,reason):
                audit_candidate_window_recovery_package(self.package,changed,external_resolver=self.resolver)

    def test_modified_external_primary_cannot_fall_back_to_embedded_bytes(self):
        with self.assertRaisesRegex(EvidenceError,'composite_external_primary_mismatch'):
            audit_candidate_window_recovery_package(self.package,self.summary,
                external_resolver=lambda name:self.resolver(name)+b'changed')

    def test_rehashed_duplicate_delivery_is_rejected(self):
        changed=deepcopy(self.package);ledger=changed['recovery_ledger']
        ledger['deliveries'].append(deepcopy(ledger['deliveries'][0]));resign(ledger)
        changed['neuron']['metadata']['recovery_ledger_sha256']=ledger['sha256']
        resign(changed['neuron']);resign(changed)
        summary=deepcopy(self.summary);summary['recovery_ledger']=deepcopy(ledger)
        with self.assertRaisesRegex(EvidenceError,'candidate_window_recovery_ledger_replay_or_order'):
            audit_candidate_window_recovery_package(changed,summary,external_resolver=self.resolver)

    def test_coherently_dropped_events_still_cannot_prove_history_completeness(self):
        changed=deepcopy(self.package);ledger=changed['recovery_ledger']
        ledger['deliveries']=[];resign(ledger)
        changed['neuron']['metadata']['recovery_ledger_sha256']=ledger['sha256']
        resign(changed['neuron']);resign(changed)
        summary=deepcopy(self.summary);summary['recovery_ledger']=deepcopy(ledger)
        result=audit_candidate_window_recovery_package(changed,summary,external_resolver=self.resolver)
        self.assertNotEqual(changed['sha256'],self.package['sha256'])
        self.assertEqual(result['recovery_ledger']['deliveries_checked'],0)
        self.assertFalse(result['recovery_ledger']['service_ledger_completeness_verified'])
        self.assertFalse(result['terminal_provenance_verified']);self.assertIsNone(result['evaluation_verdict'])

    def test_original_archive_and_model_files_remain_unchanged(self):
        archive=(self.root/'primary.tar.xz').read_bytes()
        self.assertEqual(hashlib.sha256(archive).hexdigest(),self.bundle['archive_sha256'])
        source='case/native-composite/package7/source-package.json'
        self.assertEqual(hashlib.sha256((self.restored/source).read_bytes()).hexdigest(),
                         self.bundle['members'][source]['sha256'])

    def _transfer_source(self, root):
        source=root/'source'
        shutil.copytree(self.directory,source)
        package=source/'model_stopped_state.json'
        package.write_bytes((source/'source-package.json').read_bytes())
        (source/'model_stopped_summary.json').write_bytes((source/'source-summary.json').read_bytes())
        return package

    def test_pipeline_snapshot_preserves_actual_package7_summary_and_all_primary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=self._transfer_source(root);destination=root/'snapshot'
            copied=_snapshot_source(source,destination,diagnostic=True)
            self.assertEqual(copied.read_bytes(),source.read_bytes())
            summary=destination/'model_stopped_summary.json'
            self.assertEqual(summary.read_bytes(),source.with_name(summary.name).read_bytes())
            resolver=filesystem_primary_resolver(destination)
            result=audit_candidate_window_recovery_package(load(copied),load(summary),external_resolver=resolver)
            self.assertEqual(result,self.audit)
            expected={trial['primary_ref']['relative_path']
                      for group in self.package['measurement_archive']['records'] for trial in group['raw_trials']}
            expected.update((copied.name,summary.name))
            self.assertEqual({p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()},expected)

    def test_pipeline_snapshot_rejects_changed_external_primary_before_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=self._transfer_source(root);destination=root/'snapshot'
            name=self.package['measurement_archive']['records'][0]['raw_trials'][0]['primary_ref']['relative_path']
            primary=source.parent/name
            primary.write_bytes(primary.read_bytes()+b'changed')
            with self.assertRaisesRegex(EvidenceError,'composite_external_primary_mismatch'):
                _snapshot_source(source,destination,diagnostic=True)
            self.assertFalse(destination.exists())

    def test_pipeline_snapshot_cannot_hide_missing_primary_with_embedded_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=self._transfer_source(root);destination=root/'snapshot'
            name=self.package['measurement_archive']['records'][0]['raw_trials'][0]['primary_ref']['relative_path']
            (source.parent/name).unlink()
            with self.assertRaisesRegex(EvidenceError,'composite_primary_missing_or_escape'):
                _snapshot_source(source,destination,diagnostic=True)
            self.assertFalse(destination.exists())
