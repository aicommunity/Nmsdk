"""Wire/hash and nonpromotion controls; no synthetic native training PASS."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from ..composite_measurement_contract import (integral_number_view,
    expected_semantic_measurement_id, expected_artifact_document_id)
from ..composite_package_evidence import audit_composite_package
from ..composite_execution_evidence import audit_composite_execution
from ..learned_evidence import load_case, audit_learned_state
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from .test_composite_configuration import configuration, protocol


def hash_payload():
    """Hash-format fixture, deliberately not an admissible native record."""
    return dict(purpose='search', source_origin='source', candidate_witness_id='candidate', live_attempt_binding='lease',
        logical_request=dict(trial_id='run/trial'), group_id='group',
        budgets=dict(attempt_limits=dict(maximum_groups=8, maximum_native_probes=32, maximum_total_samples=1000,
            maximum_model_seconds=3., maximum_wall_seconds=10.), maximum_group_model_seconds=.5, maximum_group_wall_seconds=2.),
        native_group=dict(traces=[dict(native_evidence=dict(trial_id='raw'), sha256='0'*64, relative_path='old/a.csv')]),
        measurement=dict(actual_peak=dict(raw_potential=.1, time=.02, plateau_end=.02)))


class CompositePortableContractTest(unittest.TestCase):
    def test_private_numeric_view_preserves_semantics_and_does_not_mutate_input(self):
        original = dict(schema_version=1., indices=[0., 2.], bool_value=True, amplitude=.125)
        before = deepcopy(original); view = integral_number_view(original)
        self.assertEqual(original, before); self.assertEqual(digest(view), digest(original))
        self.assertIs(type(view['schema_version']), int); self.assertIs(view['bool_value'], True)

    def test_nonfinite_private_view_is_rejected_before_hashing(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=value), self.assertRaises((EvidenceError, ValueError)):
                integral_number_view(dict(value=value))

    def test_csv_path_rename_changes_document_identity_but_not_measurement_proof(self):
        spec = protocol(configuration()); record = hash_payload(); renamed = deepcopy(record)
        renamed['native_group']['traces'][0]['relative_path'] = 'new/а.csv'
        self.assertEqual(expected_semantic_measurement_id(record, spec), expected_semantic_measurement_id(renamed, spec))
        self.assertNotEqual(expected_artifact_document_id(record), expected_artifact_document_id(renamed))

    def test_measurement_identity_retains_attempt_and_actual_bytes(self):
        spec = protocol(configuration()); record = hash_payload(); original = expected_semantic_measurement_id(record, spec)
        for field in ('group_id', 'live_attempt_binding', 'source_origin', 'candidate_witness_id'):
            changed = deepcopy(record); changed[field] += '-changed'
            self.assertNotEqual(original, expected_semantic_measurement_id(changed, spec))
        changed = deepcopy(record); changed['native_group']['traces'][0]['sha256'] = '1'*64
        self.assertNotEqual(original, expected_semantic_measurement_id(changed, spec))

    def test_hash_payload_is_not_promoted_to_a_training_package(self):
        with self.assertRaises(EvidenceError): audit_composite_package(hash_payload())

    def test_schema_five_loader_never_uses_old_flat_trial_globs_or_invents_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root/'train_learned_state.json'
            path.write_text(json.dumps(dict(schema_version=5, kind='timelearner_completed_state')), encoding='utf-8')
            (root/'train_state_trial_1.json').write_text('corrupt legacy flat file', encoding='utf-8')
            case = load_case(path)
            self.assertIsNone(case[1]); self.assertEqual(case[2:], ({}, {}))
            with self.assertRaises(EvidenceError): audit_learned_state(*case)

    def test_schema_five_does_not_ignore_supplied_legacy_primary_overlay(self):
        with self.assertRaisesRegex(EvidenceError, 'legacy_primary_overlay'):
            audit_learned_state(dict(schema_version=5, kind='timelearner_completed_state'), None, {'x':{}}, {})

    def test_preflight_envelope_accepts_known_zero_callbacks_but_rejects_invented_archive(self):
        execution = dict(schema_version=3, base_schema_version=1, measurement_method='declared-window-basin-necessity-v1',
            measurement_archive=None, source_origin=None, model_semantic_hash='actual', model_revision='actual',
            composite_counters=dict(attempt=dict(logical_groups=0, native_probes=0, sampled_frames=0),
                archive=dict(groups=0, native_probes=0, sampled_frames=0, primary_bytes=0),
                execution=dict(native_trials=0, sampled_frames=0)))
        result = audit_composite_execution(execution, '.', set(), mode='preflight', base_version=1)
        self.assertFalse(result['owned_archive_present']); self.assertIsNone(result['evaluation_verdict'])
        execution['composite_counters']['execution']['native_trials'] = 1
        with self.assertRaises(EvidenceError): audit_composite_execution(execution, '.', set(), mode='preflight', base_version=1)

