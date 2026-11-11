"""Actual strict N4 Train; engineering validity is distinct from convergence.

Workers only. Each case starts cold through the production CLI. No evaluation,
threshold tuning or template fallback occurs in this cohort.
"""
import contextlib
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from ..__main__ import main
from ..native_evidence import load, require


class StockCandidateRecoveryTrainTest(unittest.TestCase):
    expected_plan_version = 2

    def train_case(self, case):
        controls = Path(os.environ['TIMELEARNER_STOCK_COLD8_TRAIN_CONTROLS']).resolve(strict=True)
        spec = load(controls/'declaration.json')
        require(set(spec) == {'source', 'runtime', 'controller', 'output', 'finalization_seconds'},
            'stock_cold8_train_control_fields')
        source = Path(spec['source']).resolve(strict=True)
        require(source == Path(os.environ['TIMELEARNER_STOCK_COLD8_TRAIN_SOURCE']).resolve(strict=True),
            'stock_cold8_train_plan_binding')
        require(load(source/'index.json')['schema_version'] == self.expected_plan_version,
            'stock_cold8_train_declared_plan_mismatch')
        runtime_path = Path(spec['runtime'])
        require(runtime_path.parent.resolve(strict=True) == controls, 'stock_cold8_train_runtime_binding')
        runtime = load(runtime_path)
        require(Path(runtime['executable']['path']).parent.resolve(strict=True) ==
            Path(os.environ['TIMELEARNER_STOCK_COLD8_TRAIN_RUNTIME']).resolve(strict=True),
            'stock_cold8_train_runtime_fixture_binding')
        job = load(source/'jobs'/(case+'.json'));configuration = job['configuration']
        self.assertEqual(configuration['schema_version'], 8)
        self.assertEqual(configuration['invalid_measurement_recovery'], 'advance_rejected_candidate_window')
        self.assertEqual(configuration['search']['tolerances'],
            dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
        self.assertEqual(configuration['model']['normalization'], 'N1')
        self.assertEqual(len(configuration['model']['inputs']), 4)
        output = Path(spec['output']);output.mkdir(parents=True, exist_ok=True)
        transcript = io.StringIO()
        try:
            with patch.dict(os.environ, runtime['loader_environment']), \
                 contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
                code = main(['stock-candidate-window-study', 'train', str(source),
                    '--runtime-manifest', str(runtime_path), '--controller', spec['controller'],
                    '--case', case, '--output', str(output/case),
                    '--finalization-seconds', str(spec['finalization_seconds'])])
            self.assertEqual(code, 0, transcript.getvalue())
            result = load(output/case/'index.json')
            self.assertEqual(result['execution'], 'completed')
            self.assertEqual(result['validity'], 'valid')
            self.assertIsNotNone(result['package_audit'])
            self.assertIsNotNone(result['physical_audit'])
            self.assertFalse(result['classification_assessed'])
            self.assertIsNone(result['scientific_verdict'])
            limits = load(output/case/'execution-limits.json')
            self.assertEqual(limits['native_search_wall_seconds'], configuration['maximum_wall_seconds'])
            self.assertEqual(limits['process_maximum_wall_seconds'],
                configuration['maximum_wall_seconds']+spec['finalization_seconds'])
        finally:
            (output/(case+'-public-cli.log')).write_text(transcript.getvalue(), encoding='utf-8')

    def test_classic_actual_strict_N4_cold8_train_retains_honest_outcome(self):
        self.train_case('Classic-stock-cold8-N1')

    def test_branch_actual_strict_N4_cold8_train_retains_honest_outcome(self):
        self.train_case('Branch-stock-cold8-N1')
