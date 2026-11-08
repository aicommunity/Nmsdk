"""Explicit job admission using actual archived stopped models."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from Scripts.StructTrain.TimeLearner.native_characterization import prepare_single_pulse_job, prepare_stopped_job, validate_job
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.n1_protocol_robustness import _signed
from Scripts.StructTrain.TimeLearner.stock_wave_replay import select_packet
from Scripts.StructTrain.TimeLearner.stopped_evidence import load_case


@unittest.skipUnless(os.environ.get('TIMELEARNER_STOCK_WAVE_SOURCE'), 'requires archived native stopped models')
class SinglePulseJobTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = []
        study = Path(os.environ['TIMELEARNER_STOCK_WAVE_SOURCE'])
        for path in sorted((study/'runs').glob('*threshold-low-retry32/native/train_stopped_state.json')):
            case = load_case(path);packet = select_packet(case[0]);identity = packet['prepared']['input_id']
            index = next(i for i,v in enumerate(case[0]['protocol']['inputs']) if v['id'] == identity)
            cls.rows.append((case,index,prepare_single_pulse_job(case,index,'explicit-single-pulse-test')))
        if len(cls.rows) != 2:raise AssertionError('both exact archived stock candidates are required')

    def test_explicit_presentation_preserves_full_model_and_target(self):
        self.assertEqual({row[2]['model']['branch'] for row in self.rows},{False,True})
        for case,index,job in self.rows:
            validate_job(job);self.assertEqual(job['schema_version'],4)
            self.assertEqual(job['source_stopped'],case[0]);self.assertEqual(job['model'],case[0]['configuration']['model'])
            self.assertEqual(job['stimulus_profile'],case[0]['configuration']['stimulus_profile'])
            self.assertEqual(job['probe']['input_index'],index);self.assertEqual(job['resistance_intervention'],[])
            self.assertEqual(job['presentation'],{'kind':'single_pulse_characterization'})

    def test_old_preparation_defaults_are_unchanged(self):
        for case,index,_ in self.rows:
            old = prepare_stopped_job(case,index,'legacy-default')
            explicit = prepare_stopped_job(case,index,'legacy-default',channel_diagnostics=None)
            self.assertEqual(old,explicit);self.assertEqual(old['schema_version'],2)
            self.assertNotIn('presentation',old);self.assertNotIn('channel_diagnostics',old)

    def test_rehashed_unknown_presentation_is_rejected(self):
        for _,_,job in self.rows:
            bad = deepcopy(job);bad['presentation']['kind']='training_burst'
            with self.assertRaises(EvidenceError):validate_job(_signed(bad))

    def test_mixed_resistance_intervention_is_rejected(self):
        for _,index,job in self.rows:
            bad = deepcopy(job);bad['resistance_intervention']=[{'input_index':index,'resistance':3e8}]
            with self.assertRaises(EvidenceError):validate_job(_signed(bad))

    def test_assignment_and_source_physics_cannot_silently_change(self):
        for _,_,job in self.rows:
            for factor in ('selection','source'):
                bad = deepcopy(job)
                if factor=='selection':bad['probe']['peak_selection']='assigned_burst_wave'
                else:bad['stimulus_profile']['amplitude']*=2
                with self.assertRaises(EvidenceError):validate_job(_signed(bad))

    def test_diagnostic_enable_requires_boolean(self):
        for _,_,job in self.rows:
            bad = deepcopy(job);bad['channel_diagnostics']=1
            with self.assertRaises(EvidenceError):validate_job(_signed(bad))

    def test_explicit_channel_enable_and_disable_are_canonically_signed(self):
        for case,index,_ in self.rows:
            for enabled in (False,True):
                job = prepare_stopped_job(case,index,'explicit-channel-toggle',channel_diagnostics=enabled)
                validate_job(job);self.assertEqual(job['schema_version'],3)
                self.assertIs(job['channel_diagnostics'],enabled)

    def test_largest_peak_requires_explicit_single_pulse_presentation(self):
        for case,index,_ in self.rows:
            maximum=prepare_single_pulse_job(case,index,'explicit-maximum',peak_selection='single_impulse_maximum')
            validate_job(maximum)
            self.assertEqual(maximum['probe']['peak_selection'],'single_impulse_maximum')
            self.assertEqual(maximum['source_stopped'],case[0])
            self.assertTrue(maximum['probe']['protocol_revision'].endswith('/single-impulse-maximum-v1'))
            bad=prepare_stopped_job(case,index,'maximum-on-burst')
            bad['probe']['peak_selection']='single_impulse_maximum'
            with self.assertRaises(EvidenceError):validate_job(_signed(bad))

    def test_unknown_single_pulse_selection_is_rejected(self):
        for case,index,_ in self.rows:
            with self.assertRaises(EvidenceError):
                prepare_single_pulse_job(case,index,'unknown-maximum',peak_selection='largest_anywhere')
