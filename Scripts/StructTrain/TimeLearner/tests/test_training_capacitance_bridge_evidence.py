"""Independent controls on complete, real native bridge records."""
import copy
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import unittest

from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..training_capacitance_bridge_evidence import audit_training_capacitance_bridge


class TrainingCapacitanceBridgeEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_TRAINING_CAPACITANCE_BRIDGE_DIR')
        if not root: raise unittest.SkipTest('requires real native training C bridge artifacts')
        cls.records = [(p, load(p)) for p in sorted(Path(root).glob('*_training_capacitance_bridge_bridge.json'))]
        if len(cls.records) != 4 or {(r['branch'], r['normalization']) for _, r in cls.records} != {
                (False, 0), (False, 1), (True, 0), (True, 1)}:
            raise RuntimeError('requires all four actual native training C bridge records')

    def test_actual_complete_maps_physics_and_registry_snapshots(self):
        for path, record in self.records:
            with self.subTest(path=path.name):
                result = audit_training_capacitance_bridge(record)
                self.assertTrue(result['consistent'])
                self.assertEqual(result['bound_phases'], 5)
                self.assertFalse(result['native_import_verified'])
                self.assertFalse(result['probe_observations_verified'])
                self.assertIsNone(result['scientific_verdict'])

    def test_production_cli_on_each_actual_topology_and_normalization(self):
        for path, record in self.records:
            with self.subTest(path=path.name):
                process = subprocess.run([sys.executable, '-m', 'Scripts.StructTrain.TimeLearner',
                    'analyze', str(path), '--format', 'training-capacitance-bridge'],
                    capture_output=True, text=True, check=False, timeout=120)
                self.assertEqual(process.returncode, 0, process.stderr)
                result = json.loads(process.stdout)
                self.assertEqual(result['analysis'], audit_training_capacitance_bridge(record))
                self.assertIsNone(result['evaluation_verdict'])

    def test_unknown_schema_and_incomplete_phase_inventory(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); record['schema_version'] = True
                with self.assertRaisesRegex(EvidenceError, '^unknown_training_capacitance_bridge_schema$'):
                    audit_training_capacitance_bridge(record)
                record = copy.deepcopy(original); record['phases'].pop(2)
                with self.assertRaisesRegex(EvidenceError, '^incomplete_training_capacitance_bridge_phases$'):
                    audit_training_capacitance_bridge(record)

    def test_controller_origin_cannot_be_fabricated(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original)
                record['phases'][1]['controller_parameters']['origin'] = 'a'*64
                with self.assertRaisesRegex(EvidenceError, '^training_capacitance_bridge_origin_mismatch$'):
                    audit_training_capacitance_bridge(record)

    def test_controller_map_cannot_forget_dormant_history(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original)
                del record['phases'][3]['controller_parameters']['membrane_scales']['Dendrite1_2']
                with self.assertRaisesRegex(EvidenceError, '^training_capacitance_bridge_scale_mismatch$'):
                    audit_training_capacitance_bridge(record)

    def test_actual_storage_snapshot_is_required(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); record['phases'][3]['storage_images'] = []
                with self.assertRaisesRegex(EvidenceError, '^invalid_capacitance_images$'):
                    audit_training_capacitance_bridge(record)

    def test_consistently_resigned_policy_change_is_detected(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); frame = record['phases'][3]
                state = frame['native_state']
                state['maximum_relative_change'] = .3
                frame['controller_parameters']['maximum_relative_change'] = .3
                state['sha256'] = canonical_model_sha256({k: v for k, v in state.items() if k != 'sha256'})
                with self.assertRaisesRegex(EvidenceError, '^training_capacitance_bridge_policy_changed$'):
                    audit_training_capacitance_bridge(record)

    def test_resigned_physical_capacity_change_is_detected(self):
        for path, original in self.records:
            with self.subTest(path=path.name):
                record = copy.deepcopy(original); frame = record['phases'][3]
                identity, state = frame['model'], frame['native_state']
                node = next(n for n in identity['model']['nodes'] if n['path'] == '$.Dendrite1_1.ExcChannel')
                data = node['parameters']['Capacity']['data']
                old = struct.unpack('>d', bytes.fromhex(data['value']))[0]
                data['value'] = struct.pack('>d', old*1.01).hex()
                identity['sha256'] = canonical_model_sha256(identity['model'])
                state['applied_model_revision'] = identity['sha256']
                state['sha256'] = canonical_model_sha256({k: v for k, v in state.items() if k != 'sha256'})
                with self.assertRaisesRegex(EvidenceError, '^incomplete_or_changed_capacitance_scales$'):
                    audit_training_capacitance_bridge(record)


if __name__ == '__main__': unittest.main()
