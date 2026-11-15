"""Fresh native strict N4 preflight. Workers only; no saved learned seed."""
import contextlib
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from ..__main__ import main
from ..native_evidence import load, require


class StockCandidateRecoveryPreflightTest(unittest.TestCase):
    prepare_action = 'prepare-recovery'
    expected_plan_version = 2

    def test_actual_cold8_initial_graphs_match_original_stock_without_training(self):
        controls = Path(os.environ['TIMELEARNER_STOCK_COLD8_CONTROLS']).resolve(strict=True)
        spec = load(controls/'declaration.json')
        require(set(spec) == {'source', 'runtime', 'controller', 'output'}, 'stock_cold8_control_fields')
        require(Path(spec['source']).resolve(strict=True) ==
            Path(os.environ['TIMELEARNER_STOCK_COLD8_SOURCE']).resolve(strict=True),
            'stock_cold8_original_plan_binding')
        runtime_path = Path(spec['runtime'])
        require(runtime_path.parent.resolve(strict=True) == controls, 'stock_cold8_runtime_control_binding')
        runtime = load(runtime_path)
        require(Path(runtime['executable']['path']).parent.resolve(strict=True) ==
            Path(os.environ['TIMELEARNER_STOCK_COLD8_RUNTIME']).resolve(strict=True),
            'stock_cold8_runtime_fixture_binding')
        output = Path(spec['output']);output.mkdir(parents=True, exist_ok=False)
        prepared = output/'prepared';transcript = io.StringIO()
        with patch.dict(os.environ, runtime['loader_environment']), \
             contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
            code = main(['stock-candidate-window-study', self.prepare_action, spec['source'],
                '--runtime-manifest', str(runtime_path), '--output', str(prepared)])
            self.assertEqual(code, 0, transcript.getvalue())
            self.assertEqual(load(prepared/'index.json')['schema_version'], self.expected_plan_version)
            for case in ('Classic-stock-cold8-N1', 'Branch-stock-cold8-N1'):
                job = load(prepared/'jobs'/(case+'.json'))
                self.assertEqual(job['configuration']['schema_version'], 8)
                self.assertEqual(job['configuration']['model']['frequency_hz'], 2000)
                self.assertEqual(job['configuration']['search']['tolerances'],
                    dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
                code = main(['stock-candidate-window-study', 'preflight', str(prepared),
                    '--runtime-manifest', str(runtime_path), '--controller', spec['controller'],
                    '--case', case, '--output', str(output/case)])
                self.assertEqual(code, 0, transcript.getvalue())
                result = load(output/case/'index.json')
                self.assertEqual(result['validity'], 'valid')
                self.assertFalse(result['training_started'])
                self.assertIsNone(result['scientific_verdict'])
        (output/'public-cli.log').write_text(transcript.getvalue(), encoding='utf-8')
