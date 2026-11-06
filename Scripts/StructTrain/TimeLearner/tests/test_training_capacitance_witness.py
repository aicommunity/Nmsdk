"""Checks against production-encoded witnesses from real native bridge probes."""
import copy
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import unittest

from ..capacitance_evidence import controller_capacitance_parameters
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..training_capacitance_witness import audit_training_capacitance_witness, audit_training_capacitance_registry


class TrainingCapacitanceWitnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_TRAINING_CAPACITANCE_BRIDGE_DIR')
        if not root:
            raise unittest.SkipTest('requires actual production-encoded native capacitance witnesses')
        cls.records = [(p, load(p)) for p in sorted(Path(root).glob('*_training_capacitance_bridge_witness_*.json'))]
        phases = {'captured', 'ordinary_growth', 'joint_shrink', 'rejections_preserve_model', 'joint_growth'}
        by_case = {}
        for path, record in cls.records:
            stem, phase = path.stem.split('_witness_')
            by_case.setdefault(stem, set()).add(phase)
        if len(cls.records) != 20 or len(by_case) != 4 or any(v != phases for v in by_case.values()):
            raise RuntimeError('requires five actual bound witnesses for all four native bridge cases')

    def test_actual_model_state_storage_and_complete_map(self):
        for path, record in self.records:
            with self.subTest(path=path.name):
                result = audit_training_capacitance_witness(record)
                self.assertTrue(result['physical_state_verified'])
                self.assertGreater(result['effective_channels'], 0)
                self.assertFalse(result['probe_observations_verified'])
                self.assertIsNone(result['scientific_verdict'])

    def test_production_cli_for_each_final_graph(self):
        for path, record in self.records:
            if not path.stem.endswith('_joint_growth'):
                continue
            with self.subTest(path=path.name):
                p = subprocess.run([sys.executable, '-m', 'Scripts.StructTrain.TimeLearner', 'analyze',
                    str(path), '--format', 'capacitance-witness'], capture_output=True, text=True, timeout=120)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertEqual(json.loads(p.stdout)['analysis'], audit_training_capacitance_witness(record))

    def test_unknown_schema_and_extra_fields(self):
        for _, original in self.records:
            for field, value in [('schema_version', True), ('unversioned', {})]:
                record = copy.deepcopy(original); record[field] = value
                with self.assertRaisesRegex(EvidenceError, '^unknown_training_capacitance_witness_schema$'):
                    audit_training_capacitance_witness(record)

    def test_registry_binds_every_required_revision(self):
        for stem in {p.stem.split('_witness_')[0] for p, _ in self.records}:
            registry = {canonical_model_sha256(r): r for p, r in self.records if p.stem.startswith(stem+'_witness_')}
            required = {k: r['model_revision'] for k, r in registry.items()}
            self.assertEqual(set(audit_training_capacitance_registry(registry, required)), set(registry))
            with self.assertRaisesRegex(EvidenceError, '^missing_training_capacitance_revision_witness$'):
                audit_training_capacitance_registry(registry, {**required, 'a'*64: 'b'*64})
        original = self.records[0][1]; key = canonical_model_sha256(original)
        with self.assertRaisesRegex(EvidenceError, '^training_capacitance_registry_id_mismatch$'):
            audit_training_capacitance_registry({'a'*64: original}, {})
        with self.assertRaisesRegex(EvidenceError, '^training_capacitance_registry_revision_mismatch$'):
            audit_training_capacitance_registry({key: original}, {key: 'b'*64})

    def test_distinct_dormant_states_can_share_a_physical_revision(self):
        for path, original in self.records:
            if not path.stem.endswith('_joint_shrink'):
                continue
            alternative = copy.deepcopy(original); state = alternative['native_state']
            self.assertEqual(state['dormant_membrane_scales']['Dendrite1_2'], 1.1)
            state['dormant_membrane_scales']['Dendrite1_2'] = 1.15
            state['sha256'] = canonical_model_sha256({k: v for k, v in state.items() if k != 'sha256'})
            alternative['controller_parameters'] = controller_capacitance_parameters(state)
            self.assertTrue(audit_training_capacitance_witness(alternative)['physical_state_verified'])
            registry = {canonical_model_sha256(r): r for r in (original, alternative)}
            self.assertEqual(len(registry), 2)
            required = {k: r['model_revision'] for k, r in registry.items()}
            self.assertEqual(len(set(required.values())), 1)
            self.assertEqual(len(audit_training_capacitance_registry(registry, required)), 2)

    def test_registry_rejects_a_consistently_resigned_policy_change(self):
        for path, original in self.records:
            if not path.stem.endswith('_joint_growth'):
                continue
            initial = next(r for p, r in self.records if p.stem == path.stem.removesuffix('joint_growth')+'captured')
            record = copy.deepcopy(original); state = record['native_state']
            state['maximum_relative_change'] = record['controller_parameters']['maximum_relative_change'] = .3
            state['sha256'] = canonical_model_sha256({k: v for k, v in state.items() if k != 'sha256'})
            self.assertTrue(audit_training_capacitance_witness(record)['physical_state_verified'])
            with self.assertRaisesRegex(EvidenceError, '^training_capacitance_registry_origin_or_policy_changed$'):
                audit_training_capacitance_registry({canonical_model_sha256(initial): initial,
                                                    canonical_model_sha256(record): record}, {})

    def test_applied_revision_cannot_be_replaced(self):
        for _, original in self.records:
            record = copy.deepcopy(original); record['native_state']['applied_model_revision'] = 'a'*64
            with self.assertRaisesRegex(EvidenceError, '^training_capacitance_witness_state_revision_mismatch$'):
                audit_training_capacitance_witness(record)

    def test_full_map_cannot_forget_a_nonunit_scale(self):
        for _, original in self.records:
            record = copy.deepcopy(original)
            del record['controller_parameters']['membrane_scales']['Dendrite1_2']
            with self.assertRaisesRegex(EvidenceError, '^training_capacitance_witness_parameter_mismatch$'):
                audit_training_capacitance_witness(record)

    def test_boolean_scale_is_not_a_numeric_unit(self):
        for _, original in self.records:
            record = copy.deepcopy(original); record['controller_parameters']['membrane_scales']['Dendrite1_2'] = True
            with self.assertRaisesRegex(EvidenceError, '^not_a_number$'):
                audit_training_capacitance_witness(record)

    def test_unused_dataset_definition_is_required(self):
        for _, original in self.records:
            record = copy.deepcopy(original)
            self.assertIn('NDatasetMatrix', [d['name'] for d in record['storage_images']])
            record['storage_images'] = [d for d in record['storage_images'] if d['name'] != 'NDatasetMatrix']
            with self.assertRaisesRegex(EvidenceError, '^capacitance_storage_profile_mismatch$'):
                audit_training_capacitance_witness(record)

    def test_resigned_physical_C_change_does_not_create_proof(self):
        for _, original in self.records:
            record = copy.deepcopy(original); identity, state = record['model'], record['native_state']
            node = next(n for n in identity['model']['nodes'] if n['path'] == '$.Dendrite1_1.ExcChannel')
            data = node['parameters']['Capacity']['data']; old = struct.unpack('>d', bytes.fromhex(data['value']))[0]
            data['value'] = struct.pack('>d', old*1.01).hex()
            identity['sha256'] = canonical_model_sha256(identity['model'])
            record['model_revision'] = state['applied_model_revision'] = identity['sha256']
            state['sha256'] = canonical_model_sha256({k: v for k, v in state.items() if k != 'sha256'})
            with self.assertRaisesRegex(EvidenceError, '^incomplete_or_changed_capacitance_scales$'):
                audit_training_capacitance_witness(record)
