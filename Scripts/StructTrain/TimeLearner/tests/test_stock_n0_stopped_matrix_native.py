"""Worker-only frozen Phase A diagnostic of an actual stopped N0 model."""
import contextlib
import io
import os
from pathlib import Path
import unittest

from ..__main__ import main
from ..contained_process import inspect
from ..native_calibration_worker import _write
from ..native_evidence import load, require
from ..native_pipeline_worker import audit_run_manifest
from ..native_process_policy import policy_for_reservation
from ..phasea_matrix import extract
from ..process_runner import verify_runtime
from ..resource_reservations import Reservations
from ..runtime import file_record
from ..stock_stopped_evaluation import job_for


class StockN0StoppedMatrixNativeTest(unittest.TestCase):
    def test_actual_N0_source_and_all_eight_complete_frozen_responses(self):
        controls = Path(os.environ['TIMELEARNER_STOCK_N0_MATRIX_CONTROLS']).resolve(strict=True)
        spec = load(controls/'declaration.json')
        require(set(spec) == {'controller', 'matrix_revision', 'topology', 'source_package_sha256',
            'source_model_revision'} and spec['topology'] in ('Classic', 'Branch'), 'stock_n0_matrix_controls')
        run = Path(os.environ['TIMELEARNER_STOCK_N0_MATRIX_TRAIN']).resolve(strict=True)
        self.assertTrue(audit_run_manifest(run/'run-manifest.json')['run_evidence_consistent'])
        execution = load(run/'native/execution.json')
        source = run/'native'/execution['package_path']
        source_before = file_record(source);package = load(source)
        self.assertEqual(source_before['sha256'], spec['source_package_sha256'])
        self.assertEqual(package['model_revision'], spec['source_model_revision'])
        self.assertEqual(package['kind'], 'timelearner_stopped_state')
        self.assertIsNone(package['certificate'])
        self.assertEqual(package['configuration']['model']['normalization'], 'N0')
        self.assertEqual(package['configuration']['model']['branch'], spec['topology'] == 'Branch')
        runtime_path = controls/'runtime.json';runtime = load(runtime_path);verify_runtime(runtime)
        self.assertEqual(runtime, load(run/'process/runtime.json'))
        matrix = extract((controls/'Parameters_00.xml').read_bytes(),
            (controls/'results.csv').read_bytes(), spec['matrix_revision'])
        row = dict(name=spec['topology']+'-stock-N0-terminal', topology=spec['topology'],
            model_revision=package['model_revision'], initial_threshold=100.)
        job = job_for(row, package, matrix)
        self.assertEqual(len(job['trials']), 8)
        self.assertEqual([t['label'] for t in job['trials']].count('target'), 1)
        self.assertEqual([t['label'] for t in job['trials']].count('foil'), 7)
        output = Path(os.environ['TMPDIR'])/'stock-n0-stopped-matrix';output.mkdir()
        _write(output/'matrix.json', matrix);_write(output/'job.json', job)
        live = inspect(spec['controller'])
        self.assertEqual(live['binding']['initial_main_pid'], os.getpid())
        self.assertEqual(live['execution'], 'running')
        memory = 8*1024**3;tasks = 128
        registry = Reservations(output/'leases.sqlite3', managed_units=True,
            capacity=dict(slots=1, memory_bytes=live['memory_max']+2*memory,
                disk_bytes=12*1024**3, tasks=live['tasks_max']+2*tasks))
        lease = registry.reserve('stock-N0-stopped-eight-pattern-diagnostic',
            [dict(path=str(output/'run'), access='write')], ttl_seconds=7200,
            demands=dict(slots=1, memory_bytes=live['memory_max']+memory,
                disk_bytes=8*1024**3, tasks=live['tasks_max']+tasks), controller_directory=spec['controller'])
        transcript = io.StringIO()
        try:
            policy = policy_for_reservation(registry, lease['token'], memory_bytes=memory, tasks=tasks)
            _write(output/'process-policy.json', policy)
            with contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
                code = main(['diagnostic-evaluate', str(output/'job.json'), '--source-stopped', str(source),
                    '--runtime-manifest', str(runtime_path), '--wall-seconds', '1800',
                    '--process-policy', str(output/'process-policy.json'), '--output', str(output/'run')])
            self.assertEqual(code, 0, transcript.getvalue())
            self.assertTrue(inspect(output/'run/process/contained')['all_processes_closed'])
            self.assertTrue(audit_run_manifest(output/'run/run-manifest.json')['run_evidence_consistent'])
            manifest = load(output/'run/run-manifest.json')
            self.assertEqual((manifest['execution'], manifest['validity']), ('completed', 'valid'))
            metrics = manifest['analysis']['metrics']
            self.assertTrue(metrics['diagnostic_only'])
            self.assertFalse(metrics['training_completed'])
            self.assertIsNone(metrics['evaluation_verdict'])
            self.assertEqual(len(metrics['trials']), 8)
            self.assertEqual((metrics['pooled_counts']['targets'], metrics['pooled_counts']['foils']), (1, 7))
            self.assertEqual(metrics['effective_threshold'], 100.)
            model = load(output/'run/native/model.json')
            self.assertEqual(model, load(output/'run/native/model-after.json'))
            self.assertEqual(model['source_solo'], package)
            self.assertEqual(model['neuron']['graph']['identity'], package['neuron']['graph']['identity'])
            self.assertEqual(source_before, file_record(source))
            _write(output/'result.json', dict(kind='actual_stock_N0_stopped_matrix_result', schema_version=1,
                source=source_before, topology=spec['topology'], metrics=metrics, model_frozen=True,
                source_graph_preserved=True, training_completed=False, threshold_selected=False,
                independent_evaluation=False, scientific_verdict=None))
        finally:
            (output/'public-cli.log').write_text(transcript.getvalue(), encoding='utf-8')
            registry.release(lease['token'], note='N0 diagnostic child closed; no training convergence claim.')
