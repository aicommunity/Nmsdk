"""Actual four stopped stock models; no successful-training surrogate fixture."""
from copy import deepcopy
import os
import tempfile
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job
from ..phasea_matrix import from_git
from ..stock_stopped_evaluation import audit, job_for, prepare
from ..stock_threshold_study import audit as audit_source
from ..stopped_evidence import load_case


class StockStoppedJobTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source, repository = (os.environ.get(k) for k in
            ('TIMELEARNER_STOCK_THRESHOLD_STUDY', 'TIMELEARNER_BIN_REPOSITORY'))
        if not source or not repository:
            raise unittest.SkipTest('requires published four stopped stock models and historical Bin Git objects')
        cls.source = Path(source)
        cls.repository = Path(repository)
        cls.matrix = from_git(repository)
        cls.rows = audit_source(cls.source)['rows']

    def sources(self):
        for row in self.rows:
            native = self.source/'runs'/row['name']/'native'
            package_path = native/load(native/'execution.json')['package_path']
            yield row, load_case(package_path)

    def test_actual_complete_packages_and_all_eight_historical_patterns(self):
        for row, case in self.sources():
            package = case[0]
            job = job_for(row, package, self.matrix)
            validate_job('diagnostic-evaluate', job, case)
            self.assertEqual(job['source_stopped'], package)
            self.assertIsNot(job['source_stopped'], package)
            self.assertEqual(len(job['trials']), 8)
            self.assertEqual({t['sample_id'] for t in job['trials']},
                             {p['sample_id'] for p in self.matrix['patterns']})
            self.assertEqual(sum(t['label'] == 'target' for t in job['trials']), 1)
            self.assertTrue(all(t['duration'] == 2 and t['reset_policy'] == 'reset_per_trial' and
                                t['record_threshold_potential'] for t in job['trials']))
            self.assertEqual(job['conversion_spec']['mode'], 'identity')

    def test_training_threshold_and_no_lt_physics_are_not_replaced(self):
        for row, case in self.sources():
            package = case[0];job = job_for(row, package, self.matrix)
            model = job['source_stopped']['configuration']['model']
            self.assertEqual(model['initial_threshold'], row['initial_threshold'])
            nodes = package['neuron']['graph']['identity']['model']['nodes']
            self.assertFalse(any(n['path'].startswith('$.LTMembrane') for n in nodes))
            job['source_stopped']['configuration']['model']['initial_threshold'] = -99
            self.assertEqual(package['configuration']['model']['initial_threshold'], row['initial_threshold'])

    def test_mismatched_actual_source_and_false_certificate_rejected(self):
        for row, case in self.sources():
            for key, value in (('model_revision', 'different-model'), ('certificate', {})):
                changed = deepcopy(case[0]);changed[key] = value
                with self.assertRaisesRegex(EvidenceError, 'stock_diagnostic_source_not_actual_stopped_model'):
                    job_for(row, changed, self.matrix)

    def test_retargeting_is_not_a_transient_evaluation_pattern(self):
        for row, case in self.sources():
            changed = deepcopy(case[0]);changed['configuration']['model']['initial_isi'][-1] += .01
            with self.assertRaisesRegex(EvidenceError, 'phasea_matrix_learned_target_mismatch'):
                job_for(row, changed, self.matrix)

    def test_prepare_creates_all_jobs_and_bound_sources_before_native_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'new-diagnostic'
            design = prepare(self.source, self.repository, output)
            self.assertEqual(len(design['rows']), 4)
            for row in design['rows']:
                job = load(output/'jobs'/(row['name']+'.json'))
                self.assertEqual(job['sha256'], row['job_sha256'])
                source = output/'source/runs'/row['name']/'native'/row['source_package']
                validate_job('diagnostic-evaluate', job, load_case(source))
            self.assertFalse((output/'runs').exists())


class StockStoppedExecutionTest(unittest.TestCase):
    def test_actual_public_diagnostic_execution_keeps_unfinished_role(self):
        value = os.environ.get('TIMELEARNER_STOCK_STOPPED_EVALUATION')
        if not value:
            self.skipTest('requires actual32-trial native diagnostic output')
        result = audit(Path(value))
        self.assertEqual(result['trials'], 32)
        self.assertEqual(len(result['models']), 4)
        self.assertTrue(result['diagnostic_only'])
        self.assertFalse(result['training_completed'])
        self.assertIsNone(result['scientific_verdict'])
