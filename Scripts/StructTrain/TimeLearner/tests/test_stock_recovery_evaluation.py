"""Evaluation-role boundaries on real native stock stopped packages."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job
from ..phasea_matrix import from_git
from ..stock_recovery_evaluation import _evaluation_job
from ..stopped_evidence import load_case


class StockRecoveryEvaluationJobTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('TIMELEARNER_RECOVERY_EVALUATION_INPUTS')
        repository = os.environ.get('TIMELEARNER_PHASEA_BIN')
        if not source or not repository:
            raise unittest.SkipTest('requires real stock native packages and historical Bin Git matrix')
        cls.matrix = from_git(repository);source = Path(source)
        cls.cases = []
        for row in load(source/'design.json')['rows']:
            native = source/'runs'/row['name']/'native';execution = load(native/'execution.json')
            if not execution['completed_boundary']:
                case = load_case(native/execution['package_path'])
                cls.cases.append(({**row, 'model_revision': execution['model_revision'],
                                   'completed_boundary': False}, case))
        if not cls.cases:
            raise AssertionError('real stopped stock controls required')

    def test_actual_stopped_sources_pass_native_job_validation_without_becoming_completed(self):
        for row, case in self.cases:
            before = deepcopy(case[0]);job = _evaluation_job(row, case[0], self.matrix)
            validate_job('diagnostic-evaluate', job, case)
            self.assertEqual(case[0], before)
            self.assertEqual(job['source_stopped'], before)
            self.assertNotIn('source_recognition', job)

    def test_all_patterns_and_labels_have_full_windows_actual_input_recording_and_fixed_threshold(self):
        for row, case in self.cases:
            job = _evaluation_job(row, case[0], self.matrix)
            self.assertEqual(len(job['trials']), 8)
            self.assertEqual(len({t['pattern_hash'] for t in job['trials']}), 8)
            self.assertEqual(sum(t['label'] == 'target' for t in job['trials']), 1)
            self.assertTrue(all(t['duration'] == 2. and t['record_threshold_potential'] and
                                t['reset_policy'] == 'reset_per_trial' for t in job['trials']))
            self.assertEqual(job['source_stopped']['configuration']['model']['initial_threshold'], row['initial_threshold'])

    def test_stopped_source_cannot_be_relabelled_as_completed(self):
        for row, case in self.cases:
            changed = {**row, 'completed_boundary': True}
            with self.assertRaisesRegex(EvidenceError, 'recovery_completed_export_required'):
                _evaluation_job(changed, case[0], self.matrix, {'replacement': True})

    def test_diagnostic_source_cannot_be_replaced_with_a_recognition_template(self):
        for row, case in self.cases:
            with self.assertRaisesRegex(EvidenceError, 'recovery_diagnostic_cannot_replace_source'):
                _evaluation_job(row, case[0], self.matrix, {})

    def test_wrong_target_or_source_revision_is_rejected_before_native_evaluation(self):
        for row, case in self.cases:
            with self.assertRaisesRegex(EvidenceError, 'stock_diagnostic_source_not_actual_stopped_model'):
                _evaluation_job({**row, 'model_revision': '0'*64}, case[0], self.matrix)
            changed = deepcopy(self.matrix)
            changed['pattern_matrix_sha256'] = '0'*64
            with self.assertRaisesRegex(EvidenceError, 'phasea_matrix_invalid_artifact'):
                _evaluation_job(row, case[0], changed)
