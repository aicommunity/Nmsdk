"""Protocol controls on an actual exported, frozen eight-pattern source."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..frozen_fourth_pulse_history import FOURTH_TICKS, condition, declare_job
from ..frozen_physical_iti_study import declare_job as cadence_job
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job
from ..prepared_physical_study import declare


class FrozenFourthPulseHistoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(os.environ['TIMELEARNER_FOURTH_HISTORY_SOURCE'])
        cls.original = load(source/'job.json')
        cls.runtime = load(source/'runtime.json')
        cls.threshold = cls.original['source_model_data']['neuron']['metadata']['calibration']['threshold']
        cls.target = next(t for t in cls.original['trials'] if t['label'] == 'target')

    def job(self, tick=960, policy='preserve_neuron_dynamics', run_id='fourth-history/check'):
        return declare_job(self.original, run_id, fourth_from_first_ticks=tick, reset_policy=policy)

    def test_reference_is_the_unchanged_native_r3_cadence_job_for_both_policies(self):
        for policy in ('reset_per_trial', 'preserve_neuron_dynamics'):
            expected, _ = cadence_job(self.original, 'fourth-history/check', rotation=3,
                                      cadence='short', reset_policy=policy)
            actual, design = self.job(policy=policy)
            self.assertEqual(actual, expected)
            self.assertTrue(design['reference_case'])
            self.assertEqual(design['target_position'], 5)

    def test_all16_conditions_preserve_the_source_model_target_and_original_request(self):
        before = deepcopy(self.original)
        fingerprints = set()
        for policy in ('reset_per_trial', 'preserve_neuron_dynamics'):
            for tick in FOURTH_TICKS:
                job, design = self.job(tick, policy)
                self.assertEqual(job['source_model_data'], before['source_model_data'])
                self.assertEqual(job['criterion'], before['criterion'])
                self.assertEqual(len(job['trials']), 8)
                self.assertEqual(len({t['sample_id'] for t in job['trials']}), 8)
                self.assertEqual(len({t['pattern_hash'] for t in job['trials']}), 8)
                self.assertEqual(sum(t['label'] == 'target' for t in job['trials']), 1)
                self.assertTrue(validate_job('physical-model-evaluate', job,
                    (job['source_model_data'],))['evaluation_presentation']['complete_primary_observations_required'])
                fingerprints.add(condition(job, design, self.runtime,
                                           threshold=self.threshold)['condition_fingerprint'])
        self.assertEqual(len(fingerprints), 16)
        self.assertEqual(self.original, before)

    def test_full_five_pattern_history_and_immediately_following_foil_are_unchanged(self):
        for policy in ('reset_per_trial', 'preserve_neuron_dynamics'):
            baseline, _ = self.job(policy=policy)
            for tick in FOURTH_TICKS:
                job, _ = self.job(tick, policy)
                self.assertEqual(job['trials'][:5], baseline['trials'][:5])
                self.assertEqual(job['trials'][6], baseline['trials'][6])
                self.assertEqual([t['duration'] for t in job['trials']],
                                 [t['duration'] for t in baseline['trials']])
                self.assertEqual(job['maximum_model_ticks'], baseline['maximum_model_ticks'])

    def test_only_the_fourth_probe_time_varies_and_every_probe_fits_its_original_window(self):
        for tick in FOURTH_TICKS:
            job, _ = self.job(tick)
            probe = job['trials'][5]
            self.assertEqual(probe['pattern_isi'][:3], self.target['pattern_isi'][:3])
            intervals = [round(x*2000) for x in probe['pattern_isi']]
            self.assertEqual([0, intervals[1], sum(intervals[1:3])], [0, 160, 480])
            self.assertEqual(sum(intervals[1:]), tick)
            self.assertGreater(tick, 480)
            self.assertLess((sum(intervals)+1)/2000, probe['duration'])

    def test_changed_probe_is_a_foil_and_the_future_control_is_the_original_target(self):
        for tick in set(FOURTH_TICKS)-{960}:
            job, design = self.job(tick)
            self.assertEqual(job['trials'][5]['label'], 'foil')
            self.assertNotEqual(job['trials'][5]['pattern_hash'], self.target['pattern_hash'])
            self.assertEqual(job['trials'][7]['label'], 'target')
            self.assertEqual(job['trials'][7]['pattern_isi'], self.target['pattern_isi'])
            self.assertEqual(job['trials'][7]['pattern_hash'], self.target['pattern_hash'])
            self.assertEqual(design['target_position'], 7)
            self.assertGreaterEqual(job['trials'][7]['duration']-sum(self.target['pattern_isi']), 2.)
            self.assertIsNone(design['expected_response_counts'])

    def test_history_is_part_of_scientific_identity_while_attempt_and_binary_path_are_not(self):
        job, design = self.job(560)
        original = condition(job, design, self.runtime, threshold=self.threshold)['condition_fingerprint']
        other, od = self.job(560, run_id='fourth-history/different-attempt')
        moved = deepcopy(self.runtime); moved['executable']['path'] = 'relocated/unchanged.exe'
        self.assertEqual(original, condition(other, od, moved,
                                            threshold=self.threshold)['condition_fingerprint'])
        changed = deepcopy(self.original)
        earlier = changed['trials'][3]
        earlier['pattern_isi'][1] += .01
        earlier['pattern_isi'][2] -= .01
        earlier['pattern_hash'] = sha(earlier['pattern_isi'])
        changed.pop('sha256'); changed['sha256'] = sha(changed)
        altered, ad = declare_job(changed, 'fourth-history/history-changed',
                                  fourth_from_first_ticks=560, reset_policy='preserve_neuron_dynamics')
        self.assertNotEqual(original, condition(altered, ad, self.runtime,
                                               threshold=self.threshold)['condition_fingerprint'])

    def test_unsupported_timing_reset_and_incomplete_original_design_are_rejected(self):
        for tick in (True, 480, 0, 1200, 560.0, None):
            with self.subTest(tick=tick), self.assertRaises(EvidenceError):
                self.job(tick)
        with self.assertRaises(EvidenceError):
            self.job(policy='unobserved_gap')
        missing = deepcopy(self.original)
        missing['trials'].pop()
        missing.pop('sha256'); missing['sha256'] = sha(missing)
        with self.assertRaises(EvidenceError):
            declare_job(missing, 'fourth-history/missing', fourth_from_first_ticks=560,
                        reset_policy='preserve_neuron_dynamics')

    def test_prepared_worker_dispatches_the_same_production_protocol(self):
        job, design = self.job(1120)
        other, od, identity = declare(self.original, 'fourth-history/check',
            dict(protocol='fourth_pulse_history', fourth_from_first_ticks=1120,
                 reset_policy='preserve_neuron_dynamics'), self.runtime,
            threshold=self.threshold, memory_bytes=4*1024**3, wall_seconds=7200)
        self.assertEqual(other, job)
        self.assertEqual(od, design)
        self.assertEqual(identity, condition(job, design, self.runtime, threshold=self.threshold))
