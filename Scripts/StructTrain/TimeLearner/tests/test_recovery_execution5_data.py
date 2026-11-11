"""Execution5 payload checks against a genuine closed, failed C++ export.

Wrapper arguments below are test inputs, never actual Console process records.
The entire original primary corpus is required; no synthetic model fallback.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..candidate_window_recovery_execution_evidence import audit_candidate_window_recovery_execution
from ..composite_configuration import METHOD
from ..composite_primary import filesystem_primary_resolver
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError, load, require
from ..portable_primary import restore_native_bundle


def signed(document):
    document['sha256'] = digest({k: v for k, v in document.items() if k != 'sha256'})
    return document


class RecoveryExecution5DataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_CLOSED_PACKAGE7_SOURCE')
        require(value is not None, 'recovery_execution5_actual_primary_required')
        root = Path(value)
        require(root.is_dir() and not root.is_symlink(), 'recovery_execution5_actual_primary_missing')
        origin = load(root/'ORIGIN.json')
        require(origin['original_test_outcome'] == 'failed' and origin['scientific_verdict'] is None,
                'recovery_execution5_original_failed_scope')
        cls.scratch = tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.scratch.cleanup)
        restored = Path(cls.scratch.name)/'original'
        restore_native_bundle(root/'bundle.json', restored)
        cls.directory = restored/'case/native-composite/package7'
        cls.package = load(cls.directory/'source-package.json'); cls.summary = load(cls.directory/'source-summary.json')
        require(cls.package['schema_version'] == 7 and cls.package['kind'] == 'timelearner_stopped_state' and
                len(cls.package['recovery_ledger']['deliveries']) > 0, 'recovery_execution5_nonempty_source_required')
        audit_candidate_window_recovery_package(cls.package, cls.summary,
            external_resolver=filesystem_primary_resolver(cls.directory))
        # Exact original service summary, not a summary reconstructed from a package.
        (cls.directory/'train_stopped_summary.json').write_bytes((cls.directory/'source-summary.json').read_bytes())
        (cls.directory/'train_stopped_state.json').write_bytes((cls.directory/'source-package.json').read_bytes())

    def execution(self, base=1):
        package = self.package; archive = package['measurement_archive']
        index = (self.directory/'composite-measurements/index.json').read_bytes()
        return signed({'kind': 'timelearner_native_training_execution', 'schema_version': 5,
            'base_schema_version': base, 'execution': 'completed', 'model_revision': package['model_revision'],
            'model_semantic_hash': package['model_revision'], 'source_origin': archive['source_origin'],
            'measurement_method': METHOD,
            'measurement_archive': {'path': 'composite-measurements/index.json', 'bytes': len(index),
                                    'sha256': hashlib.sha256(index).hexdigest()},
            'composite_counters': {'attempt': deepcopy(archive['counters']['attempt']),
                'archive': deepcopy(archive['counters']['archive']), 'execution': {
                    'native_trials': archive['counters']['attempt']['native_probes'],
                    'sampled_frames': archive['counters']['attempt']['sampled_frames']}},
            'recovery_ledger_sha256': package['recovery_ledger']['sha256'],
            'recovery_delivery_count': len(package['recovery_ledger']['deliveries'])})

    def audit(self, execution, *, directory=None, package=None):
        directory = self.directory if directory is None else directory
        names = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
        return audit_candidate_window_recovery_execution(execution, directory, names, mode='train',
            base_version=execution['base_schema_version'], package=self.package if package is None else package)

    def test_actual_source7_and_both_base_wrappers_bind_nonempty_ledger(self):
        for base in (1, 2):
            with self.subTest(base=base):
                result = self.audit(self.execution(base))
                self.assertTrue(result['recovery_ledger_present'])
                self.assertEqual(result['supplied_recovery_deliveries'], len(self.package['recovery_ledger']['deliveries']))
                self.assertTrue(result['package_audit']['recovery_ledger']['event_bindings_verified'])
                self.assertFalse(result['service_ledger_completeness_verified'])
                self.assertFalse(result['native_execution_verified']); self.assertIsNone(result['evaluation_verdict'])

    def test_digest_protects_ledger_fields(self):
        changed = self.execution(); changed['recovery_delivery_count'] += 1
        with self.assertRaisesRegex(EvidenceError, 'recovery_execution_digest'):
            self.audit(changed)

    def test_rehashed_wrong_hash_and_count_are_rejected(self):
        for field, value in [('recovery_ledger_sha256', '0'*64),
                             ('recovery_delivery_count', len(self.package['recovery_ledger']['deliveries'])+1)]:
            with self.subTest(field=field):
                changed = self.execution(); changed[field] = value; signed(changed)
                with self.assertRaisesRegex(EvidenceError, 'recovery_execution_ledger_binding'):
                    self.audit(changed)

    def test_missing_recovery_binding_cannot_be_legacy_execution4(self):
        changed = self.execution(); del changed['recovery_delivery_count']; signed(changed)
        with self.assertRaisesRegex(EvidenceError, 'recovery_execution_ledger_fields_missing'):
            self.audit(changed)
        changed = self.execution(); changed['schema_version'] = 4; signed(changed)
        with self.assertRaisesRegex(EvidenceError, 'composite_execution_version_or_method'):
            self.audit(changed)

    def test_package6_cannot_be_accepted_in_execution5(self):
        changed = deepcopy(self.package); changed['schema_version'] = 6; signed(changed)
        with self.assertRaisesRegex(EvidenceError, 'recovery_execution_version_tuple'):
            self.audit(self.execution(), package=changed)

    def test_external_primary_corruption_is_not_hidden_by_embedded_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'copy'; shutil.copytree(self.directory, output)
            name = self.package['measurement_archive']['records'][0]['raw_trials'][0]['primary_ref']['relative_path']
            path = output/name; path.write_bytes(path.read_bytes()+b'changed')
            with self.assertRaisesRegex(EvidenceError, 'composite_external_primary_mismatch'):
                self.audit(self.execution(), directory=output)

    def test_pre_source_payload_has_null_ledger_and_distinct_known_counters(self):
        for preflight in (False, True):
            with self.subTest(preflight=preflight):
                changed = self.execution()
                changed.update(measurement_archive=None, source_origin=None,
                               recovery_ledger_sha256=None, recovery_delivery_count=None)
                changed['composite_counters'] = {'attempt': None, 'archive': None,
                                                'execution': {'native_trials': 0, 'sampled_frames': 0}}
                if preflight:
                    changed['composite_counters'].update(attempt={'logical_groups': 0, 'native_probes': 0, 'sampled_frames': 0},
                        archive={'groups': 0, 'native_probes': 0, 'sampled_frames': 0, 'primary_bytes': 0})
                signed(changed)
                result = audit_candidate_window_recovery_execution(changed, self.directory, set(),
                    mode='preflight' if preflight else 'train', base_version=1)
                self.assertFalse(result['owned_archive_present']); self.assertFalse(result['recovery_ledger_present'])
                changed['recovery_delivery_count'] = 0; signed(changed)
                with self.assertRaisesRegex(EvidenceError, 'recovery_execution_invented_ledger_before_source'):
                    audit_candidate_window_recovery_execution(changed, self.directory, set(),
                        mode='preflight' if preflight else 'train', base_version=1)
