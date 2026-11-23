"""Production declarations exercised on the real, exported eight-trial model."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..frozen_physical_predecessor_study import condition, declare_job
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job
from ..prepared_physical_study import declare


class FrozenPhysicalPredecessorDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(os.environ['TIMELEARNER_PREDECESSOR_SOURCE'])
        cls.original = load(source/'job.json')
        cls.runtime = load(source/'runtime.json')
        cls.threshold = cls.original['source_model_data']['neuron']['metadata']['calibration']['threshold']
        cls.foils = [t['sample_id'] for t in cls.original['trials'] if t['label'] == 'foil']
        cls.target = next(t for t in cls.original['trials'] if t['label'] == 'target')

    def pair(self, *, predecessor=None, reset_policy='preserve_neuron_dynamics',
             cadence='short', run_id='predecessor-design/a1'):
        return declare_job(self.original, run_id, predecessor=predecessor or self.foils[0],
                           cadence=cadence, reset_policy=reset_policy)

    def test_all_seven_predecessors_and_both_reset_policies_keep_the_model_frozen(self):
        before = deepcopy(self.original)
        conditions = set()
        for predecessor in self.foils:
            for policy in ('reset_per_trial', 'preserve_neuron_dynamics'):
                job, design = self.pair(predecessor=predecessor, reset_policy=policy)
                self.assertEqual(len(job['trials']), 2)
                self.assertEqual([t['label'] for t in job['trials']], ['foil', 'target'])
                self.assertEqual(job['trials'][0]['sample_id'], predecessor)
                self.assertEqual(job['trials'][0]['reset_policy'], 'reset_per_trial')
                self.assertEqual(job['trials'][1]['reset_policy'], policy)
                self.assertEqual(job['trials'][1]['pattern_isi'], self.target['pattern_isi'])
                self.assertEqual(job['source_model_data'], self.original['source_model_data'])
                self.assertEqual(job['criterion'], self.original['criterion'])
                self.assertEqual(design['target_position'], 1)
                self.assertEqual(design['pulses_per_pattern'], len(self.target['pattern_isi']))
                self.assertFalse(design['independently_heldout_patterns'])
                self.assertIsNone(design['expected_response_counts'])
                conditions.add(condition(job, design, self.runtime,
                                         threshold=self.threshold)['condition_fingerprint'])
        self.assertEqual(len(self.foils), 7)
        self.assertEqual(len(conditions), 14)
        self.assertEqual(self.original, before)

    def test_target_timing_is_identical_for_different_predecessors(self):
        jobs = [self.pair(predecessor=p)[0] for p in self.foils]
        self.assertTrue(all(j['trials'][1] == jobs[0]['trials'][1] for j in jobs))
        self.assertEqual({j['trials'][0]['duration'] for j in jobs}, {.69})
        self.assertEqual({j['maximum_model_ticks'] for j in jobs}, {jobs[0]['maximum_model_ticks']})

    def test_only_the_second_reset_policy_changes_in_each_paired_control(self):
        reset, _ = self.pair(reset_policy='reset_per_trial')
        preserve, _ = self.pair()
        self.assertEqual(reset['trials'][0], preserve['trials'][0])
        self.assertEqual({k:v for k,v in reset['trials'][1].items() if k != 'reset_policy'},
                         {k:v for k,v in preserve['trials'][1].items() if k != 'reset_policy'})
        self.assertEqual(reset['source_model_data'], preserve['source_model_data'])

    def test_native_grid_full_coverage_and_final_quiet_tail_are_declared(self):
        for cadence in ('short', 'long'):
            job, design = self.pair(cadence=cadence)
            self.assertEqual(job['coverage_policy'], 'continuous_native_stream')
            self.assertGreaterEqual(job['trials'][1]['duration']-sum(self.target['pattern_isi']), 2.)
            self.assertEqual(job['maximum_model_ticks'], sum(t['maximum_samples']-1 for t in job['trials']))
            preflight = validate_job('physical-model-evaluate', job, (job['source_model_data'],))
            self.assertTrue(preflight['evaluation_presentation']['complete_primary_observations_required'])
            self.assertFalse(preflight['effective_model_checked'])
            self.assertEqual(design['final_observation_duration'], job['trials'][1]['duration'])

    def test_attempt_and_binary_location_do_not_change_the_scientific_condition(self):
        job, design = self.pair()
        other, od = self.pair(run_id='another-attempt/b2')
        runtime = deepcopy(self.runtime)
        runtime['executable']['path'] = 'relocated/unchanged-binary.exe'
        self.assertEqual(condition(job, design, self.runtime, threshold=self.threshold)['condition_fingerprint'],
                         condition(other, od, runtime, threshold=self.threshold)['condition_fingerprint'])

    def test_unused_foil_change_does_not_change_this_case_when_the_cadence_is_unchanged(self):
        predecessor = self.foils[0]
        job, design = self.pair(predecessor=predecessor)
        changed = deepcopy(self.original)
        unused = next(t for t in changed['trials'] if t['label'] == 'foil' and
                      t['sample_id'] != predecessor and t['pattern_isi'][1] > .04)
        unused['pattern_isi'][1] -= .02
        unused['pattern_isi'][2] += .02
        unused['pattern_hash'] = sha(unused['pattern_isi'])
        changed.pop('sha256'); changed['sha256'] = sha(changed)
        other, od = declare_job(changed, 'predecessor-design/b2', predecessor=predecessor,
                               cadence='short', reset_policy='preserve_neuron_dynamics')
        self.assertEqual(job['trials'][0]['duration'], other['trials'][0]['duration'])
        self.assertEqual(condition(job, design, self.runtime, threshold=self.threshold)['condition_fingerprint'],
                         condition(other, od, self.runtime, threshold=self.threshold)['condition_fingerprint'])

    def test_unknown_predecessor_target_alias_and_invalid_cadence_are_rejected(self):
        for predecessor in ('missing', self.target['sample_id'], True):
            with self.subTest(predecessor=predecessor), self.assertRaises(EvidenceError):
                declare_job(self.original, 'bad', predecessor=predecessor,
                            cadence='short', reset_policy='preserve_neuron_dynamics')
        for cadence in ('unobserved', 1):
            with self.subTest(cadence=cadence), self.assertRaises(EvidenceError):
                self.pair(cadence=cadence)

    def test_windows_production_dispatch_reuses_the_same_declaration_and_identity(self):
        job, design = self.pair()
        dispatched, dd, identity = declare(self.original, 'predecessor-design/a1',
            dict(protocol='predecessor', predecessor=self.foils[0], cadence='short',
                 reset_policy='preserve_neuron_dynamics'), self.runtime,
            threshold=self.threshold, memory_bytes=4*1024**3, wall_seconds=7200)
        self.assertEqual(dispatched, job)
        self.assertEqual(dd, design)
        self.assertEqual(identity, condition(job, design, self.runtime, threshold=self.threshold))
