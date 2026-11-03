"""Schema3 C-aware N1 domains from actual Classic/Branch native previews."""
import copy
import os
from pathlib import Path
import struct
import unittest

from ..domain_evidence import audit_resistance_domain
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load


class CapacitanceDomainEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_TRAINING_CAPACITANCE_BRIDGE_DIR')
        if not root: raise unittest.SkipTest('requires real C-aware native N1 domain artifacts')
        cls.records = [(p, load(p)) for p in sorted(Path(root).glob('*_training_capacitance_bridge_domain.json'))]
        if len(cls.records) != 2 or {r['branch'] for _, r in cls.records} != {False, True}:
            raise RuntimeError('requires both real Classic/Branch N1 domain records')

    def test_actual_physics_and_capacitance_context(self):
        for path, record in self.records:
            with self.subTest(path=path.name):
                self.assertEqual(record['schema_version'], 3)
                result = audit_resistance_domain(record)
                self.assertTrue(result['capacitance_verified'])
                self.assertEqual(result['physics_verified'], record['status'] == 'available')
                self.assertIsNone(result['evaluation_verdict'])

    def test_preview_is_bound_to_actual_base_and_committed_graph(self):
        for path, record in self.records:
            with self.subTest(path=path.name):
                bridge = load(path.with_name(path.name.removesuffix('_domain.json')+'_bridge.json'))
                phases = {f['phase']: f for f in bridge['phases']}
                self.assertEqual(record['base_model_revision'], phases['joint_shrink']['model']['sha256'])
                self.assertEqual(record['preview_model_revision'], phases['joint_growth']['model']['sha256'])
                self.assertEqual(record['effective_capacitance'], phases['joint_growth']['controller_parameters'])
                self.assertEqual(record['capacitance_state'], phases['joint_growth']['native_state'])

    def test_rejected_request_does_not_claim_effective_physics(self):
        for path, _ in self.records:
            with self.subTest(path=path.name):
                record = load(path.with_name(path.name.removesuffix('.json')+'_rejected.json'))
                self.assertEqual(record['status'], 'unsupported')
                result = audit_resistance_domain(record)
                self.assertFalse(result['physics_verified'])
                self.assertFalse(result['capacitance_verified'])

    def test_old_schema_cannot_hide_new_context(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); record['schema_version'] = 2
                with self.assertRaisesRegex(EvidenceError, '^unversioned_domain_capacitance$'):
                    audit_resistance_domain(record)

    def test_actual_legacy_domain_keeps_its_physics_and_schema(self):
        for path, typed in self.records:
            with self.subTest(path=path.name):
                legacy = load(path.with_name(path.name.removesuffix('.json')+'_legacy.json'))
                self.assertEqual(legacy['schema_version'], 2)
                result = audit_resistance_domain(legacy)
                self.assertEqual(result['physics_verified'], legacy['status'] == 'available')
                self.assertNotIn('capacitance_verified', result)
                for key in ('status', 'preview_model_revision', 'preview_model', 'minimum_resistance', 'maximum_resistance'):
                    self.assertEqual(legacy[key], typed[key])

    def test_requested_and_effective_scales_cannot_disagree(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original)
                record['requested_capacitance']['membrane_scales']['Dendrite1_4'] = .96
                with self.assertRaisesRegex(EvidenceError, '^domain_requested_capacitance_mismatch$'):
                    audit_resistance_domain(record)

    def test_registry_readback_cannot_be_omitted(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); record['capacitance_storage_images'] = []
                with self.assertRaisesRegex(EvidenceError, '^invalid_capacitance_images$'):
                    audit_resistance_domain(record)

    def test_resigned_physical_C_corruption_is_rejected(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original)
                node = next(n for n in record['preview_model']['nodes'] if n['path'] == '$.Dendrite1_4.ExcChannel')
                data = node['parameters']['Capacity']['data']
                data['value'] = struct.pack('>d', struct.unpack('>d', bytes.fromhex(data['value']))[0]*1.01).hex()
                record['preview_model_revision'] = canonical_model_sha256(record['preview_model'])
                state = record['capacitance_state']; state['applied_model_revision'] = record['preview_model_revision']
                state['sha256'] = canonical_model_sha256({k: v for k, v in state.items() if k != 'sha256'})
                with self.assertRaisesRegex(EvidenceError, '^incomplete_or_changed_capacitance_scales$'):
                    audit_resistance_domain(record)


if __name__ == '__main__': unittest.main()
