"""Actual explicit-threshold preflight and strict nested model-spec versions."""
from copy import deepcopy
import os
from pathlib import Path
import struct
import unittest

from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..native_model_spec import audit_initial_threshold, validate_model_spec
from ..native_pipeline_worker import audit_run_manifest


class NativeModelSpecTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_INITIAL_THRESHOLD_PREFLIGHT')
        if not value:
            raise unittest.SkipTest('requires both actual model-spec2 stock preflights at threshold100')
        cls.root = Path(value)
        cls.rows = load(cls.root/'index.json')['rows']

    def test_both_actual_native_construction_values_and_full_physics_are_bound(self):
        self.assertEqual({r['name'] for r in self.rows},
                         {t+'-stock-nspneurongen-inputs4' for t in ('Classic', 'Branch')})
        for row in self.rows:
            folder = self.root/'runs'/row['name']
            self.assertTrue(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'])
            spec = load(folder/'input/job.json')['configuration']['model']
            self.assertEqual(validate_model_spec(spec), 2)
            self.assertEqual(spec['initial_threshold'], 100)
            self.assertEqual(row['profile']['initial_threshold'], 100)
            self.assertFalse(row['profile']['lt_membrane'])
            self.assertFalse(row['profile']['training_started'])
            audit_initial_threshold(spec, load(folder/'native/initial-state.json')['identity'])

    def test_schema_downgrade_unknown_factor_and_invalid_scalar_cannot_be_ignored(self):
        row = self.rows[0]
        spec = load(self.root/'runs'/row['name']/'input/job.json')['configuration']['model']
        for change in ['downgrade', 'unknown', 'missing', 'extra', 'boolean', 'nonfinite']:
            bad = deepcopy(spec)
            if change == 'downgrade':bad['schema_version'] = 1
            elif change == 'unknown':bad['schema_version'] = 3
            elif change == 'missing':bad.pop('initial_threshold')
            elif change == 'extra':bad['TrainingLTZThreshold'] = 100
            elif change == 'boolean':bad['initial_threshold'] = True
            else:bad['initial_threshold'] = float('nan')
            with self.subTest(change=change), self.assertRaises(EvidenceError):
                validate_model_spec(bad)

    def test_rehashed_effective_threshold_mismatch_is_rejected(self):
        for row in self.rows:
            folder = self.root/'runs'/row['name']
            spec = load(folder/'input/job.json')['configuration']['model']
            changed = deepcopy(load(folder/'native/initial-state.json')['identity'])
            zone = next(n for n in changed['model']['nodes'] if n['path'] == '$.LTZone')
            zone['parameters']['Threshold']['data']['value'] = struct.pack('>d', .0117).hex()
            changed['sha256'] = canonical_model_sha256(changed['model'])
            with self.assertRaisesRegex(EvidenceError, 'native_initial_threshold_readback_mismatch'):
                audit_initial_threshold(spec, changed)
