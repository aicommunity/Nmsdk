"""Actual public stock N4 probes, not a replacement for cold training."""
import contextlib
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from ..__main__ import main
from ..native_evidence import load, require
from ..resource_reservations import Reservations


class StockColdCharacterizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_COLD_PROBE_CONTROLS')
        require(value is not None, 'stock_cold_probe_controls_required')
        root = Path(value).resolve(strict=True)
        cls.spec = load(root/'declaration.json')
        require(set(cls.spec) == {'runtime', 'controller', 'output', 'topology'} and
            cls.spec['topology'] in ('both', 'Classic', 'Branch'), 'stock_cold_probe_controls_schema')
        require(Path(cls.spec['runtime']).parent.resolve(strict=True) == root,
            'stock_cold_probe_runtime_not_in_controls')
        runtime = load(Path(cls.spec['runtime']))
        bound = os.environ.get('TIMELEARNER_STOCK_COLD_NATIVE_RUNTIME')
        require(bound is not None and Path(bound).resolve(strict=True) ==
            Path(runtime['executable']['path']).parent.resolve(strict=True),
            'stock_cold_probe_actual_runtime_binding_required')
        cls.runtime = runtime

    def test_public_cold_stock_assigned_probes_preserve_actual_graph_and_primary(self):
        root = Path(self.spec['output']);root.mkdir(parents=True, exist_ok=False)
        prepared = root/'prepared';result = root/'result'
        transcript = io.StringIO()
        with contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
            code = main(['stock-cold-characterization', 'prepare', '--topology', self.spec['topology'],
                '--output', str(prepared)])
        self.assertEqual(code, 0, transcript.getvalue())
        # Project the exact immutable Console loader declaration for this native
        # operation, then restore the Python controller environment afterwards.
        with patch.dict(os.environ, self.runtime['loader_environment']), \
             contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
            code = main(['stock-cold-characterization', 'run', '--source', str(prepared),
                '--runtime-manifest', self.spec['runtime'], '--controller', self.spec['controller'],
                '--output', str(result)])
        (root/'cli-transcript.log').write_text(transcript.getvalue(), encoding='utf-8')
        self.assertEqual(code, 0, transcript.getvalue())
        observed = load(result/'index.json')
        expected = 8 if self.spec['topology'] == 'both' else 4
        self.assertEqual(len(observed['rows']), expected)
        self.assertFalse(observed['training_started'])
        self.assertFalse(observed['training_windows_selected'])
        self.assertTrue(observed['source_unchanged'])
        self.assertIsNone(observed['scientific_verdict'])
        for row in observed['rows']:
            self.assertEqual(row['physical']['input_count'], 4)
            self.assertFalse(row['physical']['lt_membrane'])
            self.assertTrue(row['probe']['model_unchanged'])
            self.assertFalse(row['probe']['training_started'])
            self.assertIs(type(row['probe']['observation_valid']), bool)
        registry = Reservations.open_existing(result/'leases.sqlite3', managed_units=True)
        self.assertEqual([r['state'] for r in registry.inspect()['leases']], ['released'])
