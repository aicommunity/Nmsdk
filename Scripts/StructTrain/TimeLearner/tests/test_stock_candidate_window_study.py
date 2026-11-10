"""Actual measured-reference N4 preparation/preflight/Train through public CLI."""
import contextlib
import io
import os
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from ..__main__ import main
from ..native_evidence import load, require


class StockCandidateWindowStudyTest(unittest.TestCase):
    def test_declared_public_operation_uses_fresh_stock_model_and_original_tolerances(self):
        binding = os.environ.get('TIMELEARNER_STOCK_COLD7_CONTROLS')
        require(binding is not None, 'stock_cold7_controls_required')
        controls = Path(binding).resolve(strict=True)
        spec = load(controls/'declaration.json')
        require(set(spec) == {'runtime', 'source', 'controller', 'output', 'operation', 'cases'} and
            spec['operation'] in ('preflight', 'train') and spec['cases'] in (
                ['Classic-stock-cold7-N1'], ['Branch-stock-cold7-N1'],
                ['Classic-stock-cold7-N1', 'Branch-stock-cold7-N1']), 'stock_cold7_controls_schema')
        require(Path(spec['runtime']).parent.resolve(strict=True) == controls and
            Path(spec['source']).resolve(strict=True) == Path(os.environ['TIMELEARNER_STOCK_COLD7_CHARACTERIZATION']).resolve(strict=True),
            'stock_cold7_fixture_binding_changed')
        runtime = load(Path(spec['runtime']))
        require(Path(runtime['executable']['path']).parent.resolve(strict=True) ==
            Path(os.environ['TIMELEARNER_STOCK_COLD7_RUNTIME']).resolve(strict=True),
            'stock_cold7_runtime_fixture_binding_changed')
        output = Path(spec['output']);output.mkdir(parents=True, exist_ok=False)
        prepared = output/'prepared';transcript = io.StringIO()
        with patch.dict(os.environ, runtime['loader_environment']), \
             contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
            code = main(['stock-candidate-window-study', 'prepare', spec['source'],
                '--runtime-manifest', spec['runtime'], '--output', str(prepared)])
            self.assertEqual(code, 0, transcript.getvalue())
            for case in load(prepared/'index.json')['jobs']:
                job = load(prepared/'jobs'/(case+'.json'));c = job['configuration']
                self.assertEqual(c['search']['tolerances'],
                    dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
                self.assertEqual(c['minimum_amplitude'], 1e-6)
                self.assertEqual(len(c['model']['inputs']), 4)
                self.assertEqual(job['profile_archives'], [])
                self.assertEqual(c['search']['bounds'][3]['maximum_length'], 1)
                self.assertEqual(c['search']['bounds'][3]['minimum_resistance'], 86e6)
            rejected_case = spec['cases'][0]
            condition_path = prepared/'conditions'/(rejected_case+'.json')
            original_condition = condition_path.read_bytes()
            changed = load(condition_path);changed['condition']['amplitude_goal'] = 'not_the_declared_goal'
            condition_path.write_text(json.dumps(changed), encoding='utf-8')
            try:
                bad = output/'rejected-condition'
                code = main(['stock-candidate-window-study', 'preflight', str(prepared),
                    '--runtime-manifest', spec['runtime'], '--controller', spec['controller'],
                    '--case', rejected_case, '--output', str(bad)])
                self.assertEqual(code, 2, transcript.getvalue())
                self.assertFalse(bad.exists())
            finally:
                condition_path.write_bytes(original_condition)
            for case in spec['cases']:
                code = main(['stock-candidate-window-study', spec['operation'], str(prepared),
                    '--runtime-manifest', spec['runtime'], '--controller', spec['controller'],
                    '--case', case, '--output', str(output/case)])
                (output/(case+'-cli.log')).write_text(transcript.getvalue(), encoding='utf-8')
                self.assertEqual(code, 0, transcript.getvalue())
                result = load(output/case/'index.json')
                self.assertEqual(result['validity'], 'valid')
                self.assertIsNone(result['scientific_verdict'])
                if spec['operation'] == 'preflight':
                    self.assertFalse(result['training_started'])
                else:
                    self.assertFalse(result['classification_assessed'])
                    self.assertIsNotNone(result['package_audit'])
