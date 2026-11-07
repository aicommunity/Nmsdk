"""Actual long-clock replay regression and arithmetic refusal controls."""
from copy import deepcopy
import os
from pathlib import Path
import unittest
from ..clock_alignment import relative_clocks_equal,specification_frequency
from ..native_evidence import EvidenceError,load
from ..stock_wave_replay import compare_traces,read_complete_burst
from ..stock_single_pulse import compare_first_prefix


@unittest.skipUnless(os.environ.get('TIMELEARNER_HIGH_SINGLE_CORPUS'), 'requires actual high-threshold archived replay')
class RelativeClockAlignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['TIMELEARNER_HIGH_SINGLE_CORPUS'])
        cls.row=next(r for r in load(cls.root/'single-pulse-study/single-pulse-design.json')['rows'] if r['name'].startswith('Branch'))
        cls.burst=cls.root/'single-pulse-study/runs'/(cls.row['name']+'-burst')/'native'
        cls.single=cls.root/'single-pulse-study/runs'/(cls.row['name']+'-single')/'native'
        cls.old_packet=load(Path(cls.row['original_packet']));cls.new_packet=load(cls.burst/'probe_trial_1.json')
        cls.a_spec,cls.a=read_complete_burst(cls.old_packet,Path(cls.row['original_trace']))
        cls.b_spec,cls.b=read_complete_burst(cls.new_packet,cls.burst/'probe_trial_1.csv')
        cls.frequency=specification_frequency(cls.a_spec,cls.b_spec)

    def test_original_production_attempt_rejected_the_actual_long_clock(self):
        self.assertFalse(load(self.root/'terminal.json')['high_threshold_diagnostic_complete'])
        self.assertEqual(load(self.root/'exception.json')['reason'],'single_pulse_control_waveform_changed')
        self.assertGreater(self.a_spec['begin'],800.)
        self.assertEqual(self.b_spec['begin'],0.)

    def test_actual_unchanged_soma_and_input_replay_passes_production_comparison(self):
        result=compare_traces(self.old_packet,Path(self.row['original_trace']),self.new_packet,self.burst/'probe_trial_1.csv')
        self.assertTrue(result['exact_waveform_reproduced'])
        prefix=compare_first_prefix(self.new_packet,self.burst/'probe_trial_1.csv',load(self.single/'probe_trial_1.json'),self.single/'probe_trial_1.csv')
        self.assertTrue(prefix['exact_first_prefix_reproduced'])

    def test_tick_phase_and_missing_or_duplicate_samples_are_rejected(self):
        a=[v['time'] for v in self.a];b=[v['time'] for v in self.b]
        for shift in (1/self.frequency,.001/self.frequency):
            self.assertFalse(relative_clocks_equal(a,self.a_spec['begin'],[v+shift for v in b],self.b_spec['begin'],self.frequency))
        self.assertFalse(relative_clocks_equal(a,self.a_spec['begin'],b[:-1],self.b_spec['begin'],self.frequency))
        bad=deepcopy(b);bad[1]=bad[0]
        self.assertFalse(relative_clocks_equal(a,self.a_spec['begin'],bad,self.b_spec['begin'],self.frequency))

    def test_unresolvable_origin_and_nonfinite_input_are_not_accepted(self):
        self.assertFalse(relative_clocks_equal([1e18],1e18,[0.],0.,self.frequency))
        with self.assertRaises(EvidenceError):relative_clocks_equal([float('nan')],0.,[0.],0.,self.frequency)

    def test_existing_low_threshold_replays_keep_the_same_verdicts(self):
        root=Path(os.environ['TIMELEARNER_LOW_SINGLE_CORPUS'])
        design=load(root/'single-pulse-study/single-pulse-design.json')
        for row in design['rows']:
            burst=root/'single-pulse-study/runs'/(row['name']+'-burst')/'native'
            single=root/'single-pulse-study/runs'/(row['name']+'-single')/'native'
            packet=load(burst/'probe_trial_1.json')
            self.assertTrue(compare_traces(load(Path(row['original_packet'])),Path(row['original_trace']),packet,burst/'probe_trial_1.csv')['exact_waveform_reproduced'])
            self.assertTrue(compare_first_prefix(packet,burst/'probe_trial_1.csv',load(single/'probe_trial_1.json'),single/'probe_trial_1.csv')['exact_first_prefix_reproduced'])
