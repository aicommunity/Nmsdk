"""Validate declared followups against the actual closed Classic DATA graph.

These are preparation checks, not new native responses or a convergence proof.
"""
from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest

from Scripts.StructTrain.TimeLearner.linux_physical_recognition_sequence import job_for
from Scripts.StructTrain.TimeLearner.linux_frozen_physical_followups import (
    PHASES, condition, declared_job, validate_request)
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.native_pipeline_worker import _load_source_case, validate_job


class ActualLinuxFrozenFollowupJobs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = os.environ.get('TIMELEARNER_LINUX_DATA_SEQUENCE_FIXTURE')
        if sys.platform != 'linux' or not fixture:
            raise unittest.SkipTest('requires the actual closed Linux Train/DATA fixture')
        cls.fixture = Path(fixture).resolve(strict=True)
        cls.request = load(cls.fixture/'request.json')
        cls.model = _load_source_case('physical-model-evaluate', cls.fixture/'model.json')[0]
        cls.original = job_for({'q':cls.request}, 'confirmation', cls.model)
        cls.runtime = load(cls.fixture/'runtime.json')

    def declared(self, phase, run_id='frozen-preparation-fixture'):
        return declared_job(self.original, run_id, phase)

    def test_repeat_changes_only_attempt_and_trial_identifiers(self):
        job, design = self.declared('repeat')
        normalized = lambda j: {k:([{f:v for f,v in t.items() if f not in ('run_id','trial_id')}
            for t in x] if k == 'trials' else x) for k,x in j.items() if k not in ('sha256','run_id')}
        self.assertEqual(normalized(job), normalized(self.original))
        self.assertNotEqual(job['run_id'], self.original['run_id'])
        self.assertEqual(design['absolute_tolerance'], 1e-12)
        validate_job('physical-model-evaluate', job, (self.model,))

    def test_third_pulse_has_exact_predeclared_native_times_and_single_target(self):
        job, design = self.declared('third-pulse')
        validate_job('physical-model-evaluate', job, (self.model,))
        self.assertEqual(design['third_from_first_ticks'], [240,320,400,480,560,640,720,800])
        self.assertEqual(len(job['trials']), 8)
        self.assertEqual(sum(t['label'] == 'target' for t in job['trials']), 1)
        for trial, tick in zip(job['trials'], design['third_from_first_ticks']):
            intervals = [round(v*2000) for v in trial['pattern_isi']]
            self.assertEqual(intervals[0], 20)
            self.assertEqual(intervals[1], 160)
            self.assertEqual(sum(intervals[1:3]), tick)
            self.assertEqual(sum(intervals[1:]), 960)
            self.assertEqual(trial['pattern_hash'], sha(trial['pattern_isi']))
            self.assertEqual(trial['duration'], 2.)
            self.assertTrue(trial['record_threshold_potential'])
        control = job['trials'][design['target_position']]
        target = next(t for t in self.original['trials'] if t['label'] == 'target')
        self.assertEqual(control['sample_id'], target['sample_id'])
        self.assertEqual(control['pattern_hash'], target['pattern_hash'])

    def test_grid_excludes_actual_calibration_foils_without_mutating_model(self):
        before = sha(self.original)
        job, design = self.declared('new-foils')
        validate_job('physical-model-evaluate', job, (self.model,))
        old = {t['pattern_hash'] for t in self.original['trials']}
        self.assertTrue(all(t['pattern_hash'] not in old for t in job['trials'] if t['label'] == 'foil'))
        self.assertEqual(job['source_model_data'], self.model)
        self.assertEqual(sha(self.original), before)
        self.assertEqual(len(job['trials']), design['new_foil_trials']+1)

    def test_third_pulse_rejects_changed_clock_or_target_or_window(self):
        cases = []
        for label, mutation in [('clock', lambda j:j['source_model_data']['configuration']['model'].__setitem__('frequency_hz',20000)),
            ('window', lambda j:next(t for t in j['trials'] if t['label']=='target').__setitem__('duration',1.)),
            ('target', lambda j:j['source_model_data']['configuration']['model'].__setitem__('initial_isi',[.01,.08,.16,.25]))]:
            changed = deepcopy(self.original); mutation(changed); cases.append((label,changed))
        for label, changed in cases:
            with self.subTest(label=label), self.assertRaisesRegex(EvidenceError, 'third_pulse_requires_declared'):
                declared_job(changed, 'invalid-declaration', 'third-pulse')

    def test_all_phases_keep_physics_and_use_their_own_trial_run_scope(self):
        for phase in PHASES:
            with self.subTest(phase=phase):
                job, _ = self.declared(phase)
                self.assertEqual(job['source_model_data'], self.model)
                self.assertTrue(all(t['run_id'] == job['run_id'] for t in job['trials']))
                self.assertEqual(len({t['trial_id'] for t in job['trials']}), len(job['trials']))

    def test_fingerprint_ignores_attempt_identifiers_and_tracks_declared_wall_budget(self):
        left, design = self.declared('third-pulse','attempt-left')
        right, other = self.declared('third-pulse','attempt-right')
        a = condition(left, design, self.runtime, 5400)
        b = condition(right, other, self.runtime, 5400)
        self.assertEqual(a, b)
        c = condition(left, design, self.runtime, 5401)
        changed = {k for k,v in a['condition'].items() if c['condition'][k] != v}
        self.assertEqual(changed, {'execution_policy'})
        self.assertNotEqual(a['condition_fingerprint'], c['condition_fingerprint'])
        self.assertEqual(len(a['case_conditions']), 8)

    def test_case_identity_is_independent_of_other_matrix_rows(self):
        job, design = self.declared('third-pulse')
        a = condition(job, design, self.runtime, 5400, index=0)
        job['trials'][-1]['sample_id'] += '-unrelated'
        b = condition(job, design, self.runtime, 5400, index=0)
        self.assertEqual(a, b)

    def request(self):
        return dict(kind='timelearner_linux_frozen_physical_followups',schema_version=1,
            job_id='actual-q3-frozen-followups',worker_host='actual-worker',
            execution_root='/home/user/timelearner-refactor',tool_commit='a'*40,
            source_recognition_request=dict(path='/home/user/timelearner-refactor/requests/source/request.json',
                                           sha256='b'*64,size=3147),
            validation_request=dict(path='/home/user/timelearner-refactor/requests/followups/scope-gate/request.json',
                                    sha256='c'*64,size=2048),
            source_recognition_owner=dict(pid=2346026,start_ticks='518700939',
                boot_id='648c6850-88c5-4e0d-8cd4-2129df4100e5',uid=1000),
            native_wall_seconds=dict(repeat=5400,**{'third-pulse':5400,'new-foils':18000}))

    def test_request_requires_exact_predecessor_identity_and_all_integer_phase_budgets(self):
        q = self.request(); self.assertEqual(validate_request(q), q)
        for field, value in [('pid',0),('start_ticks','0518700939'),('boot_id','not-a-boot')]:
            changed = deepcopy(q); changed['source_recognition_owner'][field] = value
            with self.subTest(field=field), self.assertRaises(EvidenceError): validate_request(changed)
        for value in (True, 1.5, 0, -1, 36001):
            changed = deepcopy(q); changed['native_wall_seconds']['repeat'] = value
            with self.subTest(value=value), self.assertRaisesRegex(EvidenceError,'wall_budgets'): validate_request(changed)
        changed = deepcopy(q); changed['native_wall_seconds'].pop('new-foils')
        with self.assertRaisesRegex(EvidenceError,'wall_budgets'): validate_request(changed)

    def test_request_rejects_hidden_threshold_or_training_factors(self):
        for field, value in [('threshold',.01),('new_Train',True),('expected_counts',{'TP':1,'TN':7})]:
            q = self.request(); q[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(EvidenceError,'request_schema'): validate_request(q)


if __name__ == '__main__':
    unittest.main()
