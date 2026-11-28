"""Check Linux recognition jobs against the actual stopped-model DATA graph.

This suite exercises the production validator, including the original rejected
payload. It does not claim native evaluation or training convergence.
"""
from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest
from tempfile import TemporaryDirectory

from Scripts.StructTrain.TimeLearner.linux_physical_recognition_sequence import (
    bind_condition, evaluation_limits, job_for)
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.native_pipeline_worker import _load_source_case, validate_job


class ActualLinuxDATARecognitionJob(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = os.environ.get('TIMELEARNER_LINUX_DATA_SEQUENCE_FIXTURE')
        if sys.platform != 'linux' or not fixture:
            raise unittest.SkipTest('requires the actual closed Linux Train/DATA/rejected-job fixture')
        root = Path(fixture).resolve(strict=True)
        cls.request = load(root/'request.json')
        cls.source_case = _load_source_case('physical-model-evaluate', root/'model.json')
        cls.rejected_job = load(root/'rejected-job.json')
        cls.runtime = root/'runtime.json'
        cls.actual_legacy_condition = load(root/'legacy-condition.json')

    def generated(self, phase):
        return job_for({'q': self.request}, phase, self.source_case[0])

    def test_baseline_passes_production_validator_on_actual_DATA(self):
        job = self.generated('baseline')
        result = validate_job('physical-model-evaluate', job, self.source_case)
        self.assertTrue(result['data_only'])
        self.assertEqual(len(job['trials']), 8)
        self.assertEqual(sum(t['label'] == 'target' for t in job['trials']), 1)
        self.assertEqual([t['pattern_hash'] for t in job['trials']],
                         [t['pattern_hash'] for t in self.request['patterns']])
        self.assertTrue(all(t['run_id'] == job['run_id'] for t in job['trials']))

    def test_confirmation_uses_complete_schema_and_its_own_run_scope(self):
        # The actual DATA fixture checks preparation only; a threshold candidate
        # and a real confirmation are separate native operations.
        baseline = self.generated('baseline')
        confirmation = self.generated('confirmation')
        validate_job('physical-model-evaluate', confirmation, self.source_case)
        self.assertNotEqual(baseline['run_id'], confirmation['run_id'])
        self.assertTrue(all(t['run_id'] == confirmation['run_id'] for t in confirmation['trials']))
        physical = lambda job: [{k: v for k, v in t.items() if k not in ('run_id', 'trial_id')}
                                for t in job['trials']]
        self.assertEqual(physical(baseline), physical(confirmation))

    def test_original_rejected_payload_still_fails_before_native_execution(self):
        self.assertTrue(all('run_id' not in t for t in self.rejected_job['trials']))
        with self.assertRaisesRegex(EvidenceError, 'invalid_evaluation_trial_scope'):
            validate_job('physical-model-evaluate', self.rejected_job, self.source_case)

    def test_foreign_run_scope_is_rejected_even_with_a_valid_digest(self):
        job = deepcopy(self.generated('baseline'))
        job['trials'][0]['run_id'] += '-foreign'
        job['sha256'] = sha({k: v for k, v in job.items() if k != 'sha256'})
        with self.assertRaisesRegex(EvidenceError, 'invalid_evaluation_trial_scope'):
            validate_job('physical-model-evaluate', job, self.source_case)

    def conditions(self, request):
        with TemporaryDirectory() as temporary:
            destination = Path(temporary)
            model = self.source_case[0]
            job = job_for({'q': request}, 'baseline', model)
            bind_condition({'q': request, 'runtime': self.runtime}, 'baseline', job, model, destination)
            return job, load(destination/'condition.json')

    def test_legacy_condition_matches_the_actual_before_timeout_declaration(self):
        _, condition = self.conditions(self.request)
        self.assertEqual(condition, self.actual_legacy_condition)
        limits = evaluation_limits(self.request)
        self.assertEqual(limits['native_wall_seconds'], 3600)
        self.assertGreater(limits['python_phase_wall_seconds'], limits['native_wall_seconds'])
        self.assertGreater(limits['reservation_ttl_seconds'], limits['python_phase_wall_seconds'])

    def test_declared_budget_changes_only_the_actual_execution_condition_axis(self):
        request = dict(self.request, schema_version=2, native_evaluation_wall_seconds=5400)
        before_job, before = self.conditions(self.request)
        after_job, after = self.conditions(request)
        self.assertEqual(before_job, after_job)
        self.assertNotEqual(before['fingerprint'], after['fingerprint'])
        changed = [role for role in before['artifacts']
                   if before['artifacts'][role] != after['artifacts'][role]]
        self.assertEqual(changed, ['execution_policy'])
        limits = evaluation_limits(request)
        self.assertEqual(limits['native_wall_seconds'], 5400)
        self.assertGreater(limits['python_phase_wall_seconds'], 5400)
        self.assertGreater(limits['reservation_ttl_seconds'], limits['python_phase_wall_seconds'])

    def test_invalid_declared_budgets_are_rejected(self):
        for value in (True, 0, -1, 36001, 1.5, '5400', None, float('inf')):
            with self.subTest(value=value):
                request = dict(self.request, schema_version=2, native_evaluation_wall_seconds=value)
                with self.assertRaisesRegex(EvidenceError, 'evaluation_wall_budget'):
                    evaluation_limits(request)

    def test_schema_version_cannot_silently_add_or_drop_the_execution_budget(self):
        for request in (dict(self.request, native_evaluation_wall_seconds=5400),
                        dict(self.request, schema_version=2), dict(self.request, schema_version=True),
                        dict(self.request, schema_version=3, native_evaluation_wall_seconds=5400)):
            with self.subTest(version=request['schema_version']):
                with self.assertRaisesRegex(EvidenceError, 'request_schema'):
                    evaluation_limits(request)


if __name__ == '__main__':
    unittest.main()
