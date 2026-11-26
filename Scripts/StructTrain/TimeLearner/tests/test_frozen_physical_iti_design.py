"""Cadence/reset declarations checked against an actual frozen native DATA job."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..frozen_physical_iti_study import condition, declare_job
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job


class FrozenPhysicalItiDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(os.environ['TIMELEARNER_ITI_SOURCE'])
        cls.original = load(source/'job.json')
        cls.runtime = load(source/'runtime.json')
        cls.threshold = cls.original['source_model_data']['neuron']['metadata']['calibration']['threshold']

    def job(self, *, run_id='iti-declaration/a1', rotation=0, cadence='short',
            reset_policy='preserve_neuron_dynamics'):
        return declare_job(self.original,run_id,rotation=rotation,cadence=cadence,reset_policy=reset_policy)

    def test_all_target_positions_have_complete_patterns_and_explicit_first_reset(self):
        positions=set()
        for rotation in range(8):
            job,design=self.job(rotation=rotation)
            positions.add(design['target_position'])
            self.assertEqual(job['source_model_data'],self.original['source_model_data'])
            self.assertEqual(job['criterion'],self.original['criterion'])
            self.assertEqual(job['trials'][0]['reset_policy'],'reset_per_trial')
            self.assertTrue(all(t['reset_policy']=='preserve_neuron_dynamics' for t in job['trials'][1:]))
            self.assertEqual({t['pattern_hash'] for t in job['trials']},
                             {t['pattern_hash'] for t in self.original['trials']})
            self.assertGreaterEqual(job['trials'][-1]['duration']-sum(job['trials'][-1]['pattern_isi']),2.)
            self.assertTrue(all(t['duration']>sum(t['pattern_isi']) for t in job['trials']))
            self.assertLess(job['trials'][0]['duration'],2.)
            self.assertIsNone(design['expected_response_counts'])
        self.assertEqual(positions,set(range(8)))

    def test_reset_and_preserve_controls_share_the_same_timing_and_last_tail(self):
        for cadence in ('short','long'):
            reset,rd=self.job(cadence=cadence,reset_policy='reset_per_trial')
            preserve,pd=self.job(cadence=cadence)
            for a,b in zip(reset['trials'],preserve['trials']):
                self.assertEqual({k:v for k,v in a.items() if k!='reset_policy'},
                                 {k:v for k,v in b.items() if k!='reset_policy'})
            self.assertEqual(rd['final_observation_duration'],pd['final_observation_duration'])
            if cadence=='long':self.assertTrue(all(t['duration']==2 for t in reset['trials'][:-1]))

    def test_real_matrix_float_sum_cannot_add_a_native_tick(self):
        frequency=int(self.original['source_model_data']['configuration']['model']['frequency_hz'])
        self.assertIn([.01,.4,.04,.04],[t['pattern_isi'] for t in self.original['trials']])
        expected_ticks=max(sum(round(v*frequency) for v in t['pattern_isi'])
                           for t in self.original['trials'])+round(.2*frequency)
        self.assertEqual(expected_ticks/frequency,.69)
        for rotation in (0,7):
            job,_=self.job(rotation=rotation)
            self.assertEqual(job['trials'][0]['duration'],.69)
            self.assertTrue(all(t['maximum_samples']==expected_ticks+5 for t in job['trials'][:-1]))
            self.assertEqual(job['maximum_model_ticks'],sum(t['maximum_samples']-1 for t in job['trials']))

    def test_coverage_and_reset_are_separate_axes_with_explicit_new_preflight(self):
        ordinary=validate_job('physical-model-evaluate',self.original,(self.original['source_model_data'],))
        self.assertNotIn('evaluation_presentation',ordinary)
        for reset_policy in ('reset_per_trial','preserve_neuron_dynamics'):
            job,_=self.job(reset_policy=reset_policy)
            for coverage in ('per_trial_windows','continuous_native_stream'):
                changed=deepcopy(job);changed['coverage_policy']=coverage
                changed.pop('sha256');changed['sha256']=sha(changed)
                result=validate_job('physical-model-evaluate',changed,(changed['source_model_data'],))
                extended=coverage=='continuous_native_stream' or reset_policy=='preserve_neuron_dynamics'
                self.assertEqual('evaluation_presentation' in result,extended)
                self.assertFalse(result['effective_model_checked'])
                self.assertTrue(result['native_configuration_validation_required'])
                if extended:
                    self.assertTrue(result['evaluation_presentation']['complete_primary_observations_required'])
        for field,value in (('coverage_policy','unobserved'),('reset_policy','unknown')):
            job,_=self.job()
            if field=='reset_policy':job['trials'][1][field]=value
            else:job[field]=value
            job.pop('sha256');job['sha256']=sha(job)
            with self.assertRaises(EvidenceError):
                validate_job('physical-model-evaluate',job,(job['source_model_data'],))

    def test_attempt_and_binary_path_do_not_change_condition_but_real_factors_do(self):
        job,design=self.job();a=condition(job,design,self.runtime,threshold=self.threshold)
        other,other_design=self.job(run_id='different-attempt/b2')
        runtime=deepcopy(self.runtime);runtime['executable']['path']='different-location/unchanged-binary'
        self.assertEqual(a['condition_fingerprint'],
            condition(other,other_design,runtime,threshold=self.threshold)['condition_fingerprint'])
        for kwargs in (dict(cadence='long'),dict(reset_policy='reset_per_trial'),dict(rotation=3)):
            other,other_design=self.job(**kwargs)
            self.assertNotEqual(a['condition_fingerprint'],
                condition(other,other_design,self.runtime,threshold=self.threshold)['condition_fingerprint'])

    def test_invalid_rotation_labels_and_tick_grid_are_rejected(self):
        for rotation in (True,-1,8,1.5):
            with self.subTest(rotation=rotation),self.assertRaises(EvidenceError):self.job(rotation=rotation)
        for mutation in ('label','tick'):
            broken=deepcopy(self.original)
            if mutation=='label':next(t for t in broken['trials'] if t['label']=='target')['label']='foil'
            else:
                row=broken['trials'][-1];row['pattern_isi'][1]+=.000013
                row['pattern_hash']=sha(row['pattern_isi'])
            broken.pop('sha256');broken['sha256']=sha(broken)
            with self.subTest(mutation=mutation),self.assertRaises(EvidenceError):
                declare_job(broken,'bad-condition',rotation=0,cadence='short',reset_policy='preserve_neuron_dynamics')

    def test_completed_long_reset_source_keeps_its_tail_and_declares_the_same_jobs(self):
        source, _ = self.job(run_id='source-with-native-tail', cadence='long',
                             reset_policy='reset_per_trial')
        before = deepcopy(source)
        self.assertGreater(source['trials'][-1]['duration'], 2.)
        for rotation in range(8):
            for cadence in ('long', 'short'):
                for policy in ('reset_per_trial', 'preserve_neuron_dynamics'):
                    expected = self.job(rotation=rotation, cadence=cadence, reset_policy=policy)
                    observed = declare_job(source, 'iti-declaration/a1', rotation=rotation,
                                           cadence=cadence, reset_policy=policy)
                    self.assertEqual(observed, expected)
        self.assertEqual(source, before)

    def test_arbitrary_tail_early_extension_and_unobserved_coverage_are_rejected(self):
        source, _ = self.job(cadence='long', reset_policy='reset_per_trial')
        for mutation in ('short_tail', 'extra_tail', 'early_extension', 'sample_budget', 'coverage'):
            broken = deepcopy(source)
            frequency = int(broken['source_model_data']['configuration']['model']['frequency_hz'])
            if mutation in ('short_tail', 'extra_tail'):
                change = -1 if mutation == 'short_tail' else 1
                broken['trials'][-1]['duration'] += change/frequency
                broken['trials'][-1]['maximum_samples'] += change
            elif mutation == 'early_extension':
                broken['trials'][0]['duration'] += 1/frequency
                broken['trials'][0]['maximum_samples'] += 1
            elif mutation == 'sample_budget':
                broken['trials'][-1]['maximum_samples'] += 1
            else:
                broken['coverage_policy'] = 'per_trial_windows'
            broken['maximum_model_ticks'] = sum(t['maximum_samples']-1 for t in broken['trials'])
            broken.pop('sha256'); broken['sha256'] = sha(broken)
            with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                declare_job(broken, 'invalid-tail', rotation=3, cadence='short',
                            reset_policy='preserve_neuron_dynamics')
