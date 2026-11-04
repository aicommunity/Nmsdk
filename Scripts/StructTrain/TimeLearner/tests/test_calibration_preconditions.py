"""Positive calibration sources and the unchanged legacy negative experiment."""
from pathlib import Path
import os
import unittest

from ..learned_evidence import audit_learned_state, load_case
from ..native_evidence import EvidenceError, load
from ..stopped_evidence import audit_stopped_state


class CalibrationPreconditionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_CALIBRATED_MODEL_SPEC2_DIR')
        if not value:
            raise unittest.SkipTest('requires the real eight-case native calibration gate')
        cls.root = Path(value)
        cls.cases = [load_case(p) for p in cls.root.glob('*_learned_state.json')]
        if len(cls.cases) != 8:
            raise RuntimeError('requires four completed and four stopped native sources')

    def test_positive_and_legacy_negative_sources_are_complete_and_separate(self):
        dimensions = []
        for case in self.cases:
            package, summary, _, _ = case;positive = package['kind'] == 'timelearner_completed_state'
            model = package['configuration']['model']
            dimensions.append((positive, model['branch'], model['schema_version']))
            if positive:
                self.assertTrue(audit_learned_state(*case)['exact'])
            else:
                audit_stopped_state(*case)
                self.assertEqual(package['reason'], 'maximum_sweeps_exhausted')
                self.assertIsNone(package['certificate'])
                with self.assertRaises(EvidenceError):audit_learned_state(*case)
        self.assertEqual(set(dimensions), {(p, b, v) for p in (False, True) for b in (False, True) for v in (1, 2)})

    def test_declared_domains_and_original_tolerances_are_not_hidden(self):
        for package, summary, _, _ in self.cases:
            c = package['configuration'];positive = package['kind'] == 'timelearner_completed_state'
            self.assertEqual(c['search']['tolerances'], {'sync': .02, 'amplitude_absolute': 1e-5, 'amplitude_relative': 0})
            self.assertEqual(c['model']['initial_isi'], [.01, .03 if positive else .08])
            self.assertEqual(c['search']['maximum_candidates_per_input'], 80 if positive else 4)
            self.assertEqual(c['search']['resistance_subdivision_depth'], 4 if positive else 0)
            self.assertEqual(c['search']['maximum_sweeps'], 1)
            self.assertEqual(c['search']['bounds'][0]['minimum_resistance'], 43e6 if positive else 86e6)
            self.assertEqual(c['search']['bounds'][0]['maximum_resistance'], 86e6 if positive else 172e6)
            self.assertEqual(c['search']['bounds'][0]['minimum_length'], 1 if positive else 2)
            self.assertEqual(c['search']['bounds'][0]['maximum_length'], 3)
            if positive:
                self.assertEqual(c['duration'], .26)
                self.assertEqual(c['model']['allocated_cable_lengths'], [1] if c['model']['branch'] else [1, 1])

    def test_only_positive_sources_reach_calibration_and_schema2_distinct_owner_import(self):
        calibrated = [load(p) for p in self.root.glob('*_calibrated_state.json')]
        self.assertEqual(len(calibrated), 4)
        positive = {case[0]['sha256'] for case in self.cases if case[0]['kind'] == 'timelearner_completed_state'}
        self.assertEqual({p['source_candidate']['source_recognition']['source_solo']['sha256'] for p in calibrated}, positive)
        self.assertEqual(len(list(self.root.glob('*_calibrated_transfer.json'))), 2)
