"""Actual model snapshots before binding, after unit binding and after trim."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from ..capacitance_binding_evidence import audit_capacitance_binding
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, audit_probe, load


class CapacitanceBindingEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_TRAINING_CAPACITANCE_BRIDGE_DIR')
        if not root: raise unittest.SkipTest('requires real explicit C0 binding records')
        cls.records = [(p, load(p)) for p in sorted(Path(root).glob('*_training_capacitance_binding_binding.json'))]
        if len(cls.records) != 4 or {(r['branch'], r['normalization']) for _, r in cls.records} != {
                (False, 0), (False, 1), (True, 0), (True, 1)}:
            raise RuntimeError('requires all four actual explicit C0 bindings')

    def test_actual_unit_binding_and_retained_original_C0_after_trim(self):
        for path, record in self.records:
            with self.subTest(path=path.name):
                result = audit_capacitance_binding(record)
                self.assertTrue(result['consistent'])
                self.assertFalse(result['cold_training_history_verified'])
                self.assertFalse(result['native_lifecycle_verified'])
                self.assertIsNone(result['scientific_verdict'])
                process = subprocess.run([sys.executable, '-m', 'Scripts.StructTrain.TimeLearner',
                    'analyze', str(path), '--format', 'capacitance-binding'],
                    capture_output=True, text=True, timeout=120, check=False)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(json.loads(process.stdout)['analysis'], result)

    def test_unknown_schema_and_missing_phase(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); record['schema_version'] = True
                with self.assertRaisesRegex(EvidenceError, '^unknown_capacitance_binding_schema$'):
                    audit_capacitance_binding(record)
                record = copy.deepcopy(original); record['phases'].pop(0)
                with self.assertRaisesRegex(EvidenceError, '^incomplete_capacitance_binding_phases$'):
                    audit_capacitance_binding(record)

    def test_unit_binding_cannot_change_a_valid_actual_model(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original)
                # Both identities are genuine valid snapshots; no stale digest
                # can be mistaken for the metadata-only contract violation.
                record['phases'][0]['model'] = copy.deepcopy(record['phases'][2]['model'])
                with self.assertRaisesRegex(EvidenceError, '^capacitance_binding_changed_model$'):
                    audit_capacitance_binding(record)

    def test_controller_unit_scale_cannot_disagree_with_native_state(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original)
                record['phases'][1]['controller_parameters']['membrane_scales']['Dendrite1_1'] = 1.05
                with self.assertRaisesRegex(EvidenceError, '^capacitance_binding_controller_mismatch$'):
                    audit_capacitance_binding(record)

    def test_missing_actual_registry_snapshot(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); record['phases'][1]['storage_images'] = []
                with self.assertRaisesRegex(EvidenceError, '^invalid_capacitance_images$'):
                    audit_capacitance_binding(record)

    def test_unused_dataset_image_is_required_for_initial_binding(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); frame = record['phases'][1]
                self.assertIn('NDatasetMatrix', [d['name'] for d in frame['storage_images']])
                frame['storage_images'] = [d for d in frame['storage_images'] if d['name'] != 'NDatasetMatrix']
                with self.assertRaisesRegex(EvidenceError, '^capacitance_storage_profile_mismatch$'):
                    audit_capacitance_binding(record)

    def test_fabricated_unbound_owner(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original)
                record['phases'][0]['native_state'] = copy.deepcopy(record['phases'][1]['native_state'])
                with self.assertRaisesRegex(EvidenceError, '^fabricated_unbound_capacitance_binding$'):
                    audit_capacitance_binding(record)

    def test_actual_retained_references_block_first_binding(self):
        root = Path(os.environ['TIMELEARNER_TRAINING_CAPACITANCE_BRIDGE_DIR'])
        guards = [load(p) for p in sorted(root.glob('*_binding_reference_guard_reference_guard.json'))]
        self.assertEqual(len(guards), 2)
        self.assertEqual({g['branch'] for g in guards}, {False, True})
        for guard in guards:
            with self.subTest(branch=guard['branch']):
                self.assertEqual(guard['kind'], 'native_capacitance_binding_reference_guard')
                self.assertEqual(guard['reason'], 'training_capacitance_binding_requires_initial_model_boundary')
                self.assertEqual(guard['owner_state'], {})
                self.assertEqual(guard['before_model'], guard['after_model'])
                identity = guard['before_model']
                self.assertEqual(identity['sha256'], canonical_model_sha256(identity['model']))
                packets = guard['reference_packets']; self.assertEqual(len(packets), 2)
                audits = [audit_probe(packet) for packet in packets]
                self.assertTrue(all(a['valid_observation'] for a in audits))
                self.assertEqual(len({a['trial_id'] for a in audits}), 2)
                self.assertTrue(all(p['current_base_revision'] == identity['sha256'] for p in packets))
                self.assertIsNone(guard['scientific_verdict'])


if __name__ == '__main__': unittest.main()
