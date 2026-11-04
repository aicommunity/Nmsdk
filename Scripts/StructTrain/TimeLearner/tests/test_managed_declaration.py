"""Early rejection against real coordinator declarations, without native work."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..__main__ import main
from ..managed_pipeline import _validate
from ..native_evidence import EvidenceError, load


class ManagedDeclarationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('TIMELEARNER_MANAGED_COORDINATOR_PRIMARY')
        if not source:
            raise unittest.SkipTest('requires actual completed coordinator corpus')
        cls.source = Path(source)

    def job(self, name='Classic-v1'):
        return load(self.source/name/'runs/pipeline/specification.json')

    def phase(self, job, operation):
        return next(p['job'] for p in job['phases'] if p['operation'] == operation)

    def reject(self, job, reason):
        with self.assertRaisesRegex(EvidenceError, reason):
            _validate(job, preflight=True)

    def test_actual_positive_declarations_remain_valid_without_fake_models(self):
        for name in ('Classic-v1', 'Classic-v2', 'Branch-v1', 'Branch-v2'):
            job = self.job(name)
            self.assertEqual(_validate(job, preflight=True), job)
            self.assertTrue(all(p['job'].get('source_solo', p['job'].get('source_recognition')) is None
                                for p in job['phases'][1:]))

    def test_duplicate_trial_id_is_rejected_before_training(self):
        job = self.job();trials = self.phase(job, 'evaluate')['trials']
        trials[1]['trial_id'] = trials[0]['trial_id']
        self.reject(job, 'duplicate_or_invalid_calibration_trial')

    def test_target_label_cannot_identify_another_pattern(self):
        job = self.job();trials = self.phase(job, 'evaluate')['trials']
        foil = next(t for t in trials if t['label'] == 'foil')
        foil['label'] = 'target'
        self.reject(job, 'worker_trial_identity_or_shape_mismatch')

    def test_sample_identity_cannot_alias_target_and_foil(self):
        job = self.job();trials = self.phase(job, 'evaluate')['trials']
        target = next(t for t in trials if t['label'] == 'target')
        foil = next(t for t in trials if t['label'] == 'foil')
        foil['sample_id'] = target['sample_id']
        self.reject(job, 'worker_sample_collision')

    def test_clipped_sample_budget_is_rejected_before_training(self):
        job = self.job();self.phase(job, 'evaluate')['trials'][0]['maximum_samples'] = 2
        self.reject(job, 'worker_trial_window_or_sample_budget')

    def test_nonfinite_duration_cannot_reach_a_native_process(self):
        for duration in (float('nan'), float('inf'), True):
            job = self.job();self.phase(job, 'evaluate')['trials'][0]['duration'] = duration
            self.reject(job, 'nonfinite|number|numeric')

    def test_response_criterion_uses_the_scorer_contract(self):
        for anchor in ('unknown', None):
            job = self.job();self.phase(job, 'evaluate')['criterion']['anchor'] = anchor
            self.reject(job, 'unknown_response_criterion')
        job = self.job();self.phase(job, 'calibrate')['specification']['criterion']['begin_offset'] = -1
        self.reject(job, 'invalid_response_window')

    def test_calibration_frequency_must_match_declared_model(self):
        job = self.job();self.phase(job, 'calibrate')['frequency_hz'] *= 10
        self.reject(job, 'worker_clock_or_tick_budget_mismatch')

    def test_invalid_grid_is_rejected_before_training(self):
        for thresholds in ([], [0.1, 0.1], [False], [float('nan')]):
            job = self.job();self.phase(job, 'calibrate')['thresholds'] = thresholds
            self.reject(job, 'invalid_calibration|number|numeric|nonfinite')

    def test_historical_conversion_cannot_be_applied_to_classic(self):
        job = self.job();model = job['phases'][0]['job']['configuration']['model']
        conversion = self.phase(job, 'export')['conversion_spec']
        conversion.update(mode='historical_branch_n1_v1',
                          resistance_bounds=[{'minimum': 1., 'maximum': 2.} for _ in model['inputs']])
        self.reject(job, 'unsupported_historical_conversion')

    def test_public_cli_rejects_later_phase_before_output_is_created(self):
        job = self.job();self.phase(job, 'evaluate')['criterion']['anchor'] = 'unknown'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary);declaration = root/'job.json';policy = root/'policy.json'
            declaration.write_text(json.dumps(job));policy.write_text('null')
            # No execution authority is supplied. A regression must not launch
            # a native process merely to prove that early validation is absent.
            output = root/'runs';text = io.StringIO()
            with contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
                result = main(['pipeline', 'run', str(output), '--specification', str(declaration),
                    '--runtime-manifest', str(self.source/'Classic-v1/runs/pipeline/runtime.json'),
                    '--process-policy', str(policy)])
            self.assertEqual(result, 2, text.getvalue())
            self.assertIn('unknown_response_criterion', text.getvalue())
            self.assertFalse(output.exists())
