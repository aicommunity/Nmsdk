"""Worker-only declared N0 preflight/Train through production CLI and DATA audits."""
import contextlib
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from ..__main__ import main
from ..native_evidence import load, require


class StockNormalizationStudyTest(unittest.TestCase):
    def test_declared_operation_preserves_cold_physics_and_honest_outcome(self):
        controls = Path(os.environ['TIMELEARNER_STOCK_N0_CONTROLS']).resolve(strict=True)
        spec = load(controls/'declaration.json')
        require(set(spec) == {'source', 'runtime', 'controller', 'output', 'operation', 'cases', 'finalization_seconds'}
            and spec['operation'] in ('preflight', 'train') and spec['cases'] in (
                ['Classic-stock-cold8-N0'], ['Branch-stock-cold8-N0'],
                ['Classic-stock-cold8-N0', 'Branch-stock-cold8-N0']), 'stock_n0_controls_schema')
        source = Path(spec['source']).resolve(strict=True)
        require(source == Path(os.environ['TIMELEARNER_STOCK_N0_SOURCE']).resolve(strict=True), 'stock_n0_source_binding')
        runtime_path = Path(spec['runtime']).resolve(strict=True)
        require(runtime_path.parent == controls, 'stock_n0_runtime_binding')
        runtime = load(runtime_path)
        require(Path(runtime['executable']['path']).parent.resolve(strict=True) ==
            Path(os.environ['TIMELEARNER_STOCK_N0_RUNTIME']).resolve(strict=True), 'stock_n0_runtime_fixture')
        output = Path(spec['output']);output.mkdir(parents=True, exist_ok=False)
        prepared = output/'prepared';transcript = io.StringIO()
        try:
            with patch.dict(os.environ, runtime['loader_environment']), \
                 contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
                self.assertEqual(main(['stock-candidate-window-study', 'prepare-N0', str(source),
                    '--runtime-manifest', str(runtime_path), '--output', str(prepared)]), 0, transcript.getvalue())
                self.assertEqual(load(prepared/'index.json')['schema_version'], 4)
                for case in spec['cases']:
                    original = load(source/'jobs'/(case.removesuffix('-N0')+'-N1.json'))
                    job = load(prepared/'jobs'/(case+'.json'));c = job['configuration']
                    self.assertEqual(c['model']['normalization'], 'N0')
                    self.assertEqual(c['search']['tolerances'], dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
                    for key in ('maximum_probes', 'maximum_edits', 'maximum_candidates_per_input',
                                'maximum_sweeps', 'maximum_invalid_observations'):
                        self.assertEqual(c['search'][key], original['configuration']['search'][key])
                    self.assertEqual(c['maximum_wall_seconds'], original['configuration']['maximum_wall_seconds'])
                    self.assertEqual(c['model']['inputs'], original['configuration']['model']['inputs'])
                    self.assertEqual([b['maximum_synapses'] for b in c['search']['bounds']], [128,128,128,1])
                    self.assertEqual(load(prepared/'initial'/(case+'.json')),
                        load(source/'initial'/(case.removesuffix('-N0')+'-N1.json')))
                    arguments = ['stock-candidate-window-study', spec['operation'], str(prepared),
                        '--runtime-manifest', str(runtime_path), '--controller', spec['controller'],
                        '--case', case, '--output', str(output/case)]
                    if spec['operation'] == 'train':
                        arguments += ['--finalization-seconds', str(spec['finalization_seconds'])]
                    else:
                        self.assertEqual(spec['finalization_seconds'], 0.)
                    self.assertEqual(main(arguments), 0, transcript.getvalue())
                    result = load(output/case/'index.json')
                    self.assertEqual(result['execution'], 'completed')
                    self.assertEqual(result['validity'], 'valid')
                    self.assertIsNone(result['scientific_verdict'])
                    if spec['operation'] == 'preflight':
                        self.assertFalse(result['training_started'])
                    else:
                        self.assertFalse(result['classification_assessed'])
                        self.assertIsNotNone(result['package_audit'])
                        self.assertIsNotNone(result['physical_audit'])
                        package = load(output/case/result['package_path'])
                        self.assertEqual(package['configuration'], c)
                        self.assertEqual(package['runtime_plan']['maximum_wall_seconds'], c['maximum_wall_seconds'])
                        limits = load(output/case/'execution-limits.json')
                        self.assertEqual(limits['native_search_wall_seconds'], c['maximum_wall_seconds'])
                        self.assertEqual(limits['process_finalization_seconds'], spec['finalization_seconds'])
        finally:
            (output/'public-cli.log').write_text(transcript.getvalue(), encoding='utf-8')
