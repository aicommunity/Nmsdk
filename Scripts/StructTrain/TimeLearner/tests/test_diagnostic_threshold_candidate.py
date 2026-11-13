"""Actual native threshold-only diagnostic imports and complete trial scoring."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..diagnostic_recognition_evidence import audit_diagnostic_recognition, audit_diagnostic_recognition_trial
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import score_diagnostic_recognition_evaluation
from ..recognition_trial_evidence import audit_recognition_trial
from ..threshold_candidate_evidence import audit_threshold_candidate
from ..native_pipeline_worker import validate_job


def signed(value):
    value.pop('sha256', None)
    value['sha256'] = sha(value)
    return value


class DiagnosticThresholdCandidateNativeTest(unittest.TestCase):
    def cases(self):
        root = Path(os.environ['TIMELEARNER_DIAGNOSTIC_THRESHOLD_NATIVE'])
        for topology in ('Classic', 'Branch'):
            prefix = topology+'_2000_N1_diagnostic_threshold'
            source = load(root/(prefix+'_stopped_package.json'))
            summary = load(root/(prefix+'_training_outcome.json'))
            packets, traces = {}, {}
            for index in range(1, len(source['observed_packets'])+1):
                path = root/(prefix+f'_training_proof_{index}.json')
                packet = load(path);trial = packet['requested_specification']['trial_id']
                self.assertNotIn(trial, packets)
                packets[trial], traces[trial] = packet, path.with_suffix('.csv')
            candidate = load(root/(prefix+'_diagnostic_threshold.json'))
            observations = [load(root/(prefix+f'_frozen_trial_{i}.json')) for i in range(4)]
            yield candidate, (source, summary, packets, traces), observations

    def test_native_sole_threshold_edit_preserves_stopped_source_and_all_trials(self):
        for candidate, case, observations in self.cases():
            proof = audit_diagnostic_recognition(candidate, case)
            self.assertTrue(proof['threshold_derivation_verified'])
            self.assertTrue(proof['diagnostic_only'])
            self.assertFalse(proof['certificate_present'])
            self.assertFalse(proof['calibrated'])
            self.assertEqual(candidate['threshold'], .01)
            self.assertEqual(candidate['source_recognition']['source_solo'], case[0])
            for observation in observations:
                self.assertTrue(audit_diagnostic_recognition_trial(observation, candidate, case)['valid_observation'])

    def test_same_full_window_counts_keep_unfinished_role_and_null_verdict(self):
        for candidate, case, observations in self.cases():
            trials = [dict(trial_id=o['trial_id'], sample_id=o['sample_id'], label=o['label'],
                pattern_hash=o['pattern_hash'], reset_policy=o['reset_policy'], presentation_index=i,
                duration=o['end']-o['begin'], observation=f'trial-{i}.json') for i, o in enumerate(observations)]
            specification = dict(kind='timelearner_diagnostic_recognition_evaluation_spec', schema_version=1,
                run_id=observations[0]['run_id'], model_revision=candidate['model_revision'],
                coverage_policy='per_trial_windows', criterion=dict(id='post_anchor_target_whole_window_foil_v1',
                    anchor='onset', begin_offset=0., end_offset=None, reject_target_outside_window=True),
                trials=trials, diagnostic_only=True, source_stopped_sha256=case[0]['sha256'],
                training_outcome=case[0]['training_outcome'])
            result = score_diagnostic_recognition_evaluation(specification, observations, candidate, case)
            self.assertEqual(result['validity'], 'valid')
            self.assertEqual(result['pooled_counts']['targets'], 2)
            self.assertEqual(result['pooled_counts']['foils'], 2)
            self.assertTrue(result['diagnostic_threshold_experiment'])
            self.assertFalse(result['training_completed'])
            self.assertFalse(result['calibration_performed'])
            self.assertIsNone(result['evaluation_verdict'])
            with self.assertRaisesRegex(EvidenceError, 'missing_evaluation_trial'):
                score_diagnostic_recognition_evaluation(specification, observations[:-1], candidate, case)

    def test_ordinary_candidate_and_trial_readers_reject_diagnostic_kind(self):
        for candidate, case, observations in self.cases():
            with self.assertRaises(EvidenceError):
                audit_threshold_candidate(candidate, case)
            with self.assertRaises(EvidenceError):
                audit_recognition_trial(observations[0], candidate)
            forged = deepcopy(candidate)
            forged.update(kind='timelearner_recognition_threshold_candidate', state_kind='recognition')
            signed(forged)
            with self.assertRaises(EvidenceError):
                audit_threshold_candidate(forged, case)

    def test_explicit_job_schema_is_required_for_the_threshold_factor(self):
        for candidate, case, observations in self.cases():
            run_id = observations[0]['run_id']
            trials = [dict(run_id=run_id, trial_id=o['trial_id'], sample_id=o['sample_id'],
                label=o['label'], pattern_isi=o['pattern_isi'], pattern_hash=o['pattern_hash'],
                duration=o['end']-o['begin'], maximum_samples=o['maximum_samples'],
                reset_policy=o['reset_policy'], record_threshold_potential=True) for o in observations]
            job = signed(dict(kind='timelearner_native_diagnostic_evaluation_job', schema_version=2,
                owner_class='NNeuronTimeLearner'+('Branch' if case[0]['configuration']['model']['branch'] else ''),
                implementation_id=case[0]['implementation_id'], source_stopped=case[0],
                conversion_spec=candidate['source_recognition']['conversion_spec'], maximum_model_ticks=100000,
                run_id=run_id, coverage_policy='per_trial_windows',
                criterion=dict(id='post_anchor_target_whole_window_foil_v1', anchor='onset',
                    begin_offset=0., end_offset=None, reject_target_outside_window=True),
                trials=trials, diagnostic_threshold=.01))
            self.assertTrue(validate_job('diagnostic-evaluate', job, case)['primary_source_checked'])
            job['schema_version'] = 1;signed(job)
            with self.assertRaisesRegex(EvidenceError, 'unknown_native_pipeline_job'):
                validate_job('diagnostic-evaluate', job, case)

    def test_resigned_other_physics_edit_cannot_hide_in_threshold_candidate(self):
        for candidate, case, _ in self.cases():
            changed = deepcopy(candidate)
            identity = changed['neuron']['graph']['identity']
            identity['model']['nodes'][0]['class'] = 'UnrequestedReplacement'
            identity['sha256'] = changed['model_revision'] = sha(identity['model'])
            signed(changed['neuron']);signed(changed)
            with self.assertRaises(EvidenceError):
                audit_diagnostic_recognition(changed, case)
