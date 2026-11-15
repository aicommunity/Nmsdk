"""Prefix evidence from real first-invalid Classic/Branch native traces."""
from copy import deepcopy
from pathlib import Path
import os
import unittest

from ..native_evidence import EvidenceError
from ..stock_first_pulse import audit_prefix
from ..stock_wave_replay import select_packet
from ..stopped_evidence import load_case


class StockFirstPulseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_STOCK_WAVE_SOURCE')
        if not root:
            raise unittest.SkipTest('requires actual stock native primary')
        cls.cases = [load_case(Path(root)/'runs'/name/'native/train_stopped_state.json')
                     for name in ('Classic-threshold-low-retry32', 'Branch-threshold-low-retry32')]

    def test_actual_classic_has_three_interior_maxima_before_second_stimulus(self):
        case = self.cases[0];packet = select_packet(case[0])
        result = audit_prefix(packet, case[3][packet['requested_specification']['trial_id']], case[0]['protocol'])
        self.assertEqual(result['interior_positive_maxima_count'], 3)
        self.assertTrue(all(p['time'] < result['second_actual_stimulus']
                            for p in result['interior_positive_maxima']))
        self.assertFalse(result['valid_training_measurement'])
        self.assertFalse(result['later_waves_decomposed'])

    def test_actual_branch_prefix_is_distinct_from_its_seven_wave_full_burst(self):
        case = self.cases[1];packet = select_packet(case[0])
        result = audit_prefix(packet, case[3][packet['requested_specification']['trial_id']], case[0]['protocol'])
        self.assertEqual(result['interior_positive_maxima_count'], 1)
        self.assertEqual(len(packet['observation']['burst_assignments'][0]['waves']), 7)
        self.assertFalse(result['new_single_pulse_trial_executed'])
        self.assertIsNone(result['scientific_verdict'])

    def test_modified_actual_stimulus_time_is_rejected(self):
        case = self.cases[0];packet = deepcopy(select_packet(case[0]))
        trace = case[3][packet['requested_specification']['trial_id']]
        packet['observation']['stimuli'][1]['time'] += .001
        with self.assertRaises(EvidenceError):
            audit_prefix(packet, trace, case[0]['protocol'])

    def test_unrecorded_extra_wave_is_rejected_before_prefix_analysis(self):
        case = self.cases[0];packet = deepcopy(select_packet(case[0]))
        trace = case[3][packet['requested_specification']['trial_id']]
        packet['observation']['burst_assignments'][0]['waves'].pop()
        with self.assertRaisesRegex(EvidenceError, 'diagnostic_trace_wave_count_mismatch'):
            audit_prefix(packet, trace, case[0]['protocol'])
