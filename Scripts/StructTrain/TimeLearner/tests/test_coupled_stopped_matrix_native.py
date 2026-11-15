"""Eight-pattern native diagnostic of the exact coupled-search terminal state."""
import os
from pathlib import Path
import unittest

from ..contained_process import inspect
from ..native_calibration_worker import _write
from ..native_evidence import load
from ..native_pipeline_worker import audit_run_manifest, run_job
from ..native_process_policy import policy_for_reservation
from ..phasea_matrix import extract
from ..resource_reservations import Reservations
from ..runtime import file_record
from ..stock_stopped_evaluation import job_for


class CoupledStoppedMatrixNativeTest(unittest.TestCase):
    def test_actual_stopped_branch_complete_eight_pattern_frozen_diagnostic(self):
        controls = Path(os.environ['TIMELEARNER_COUPLED_FROZEN_CONTROLS'])
        spec = load(controls/'declaration.json')
        run = Path(os.environ['TIMELEARNER_COUPLED_TRAIN_RUN'])
        self.assertTrue(audit_run_manifest(run/'run-manifest.json')['run_evidence_consistent'])
        execution = load(run/'native/execution.json')
        self.assertEqual(execution['training_outcome'], 'invalid_observation')
        source = run/'native'/execution['package_path']
        source_before = file_record(source)
        package = load(source)
        self.assertIsNone(package['certificate'])
        self.assertTrue(package['configuration']['model']['branch'])
        matrix = extract((controls/'Parameters_00.xml').read_bytes(),
                         (controls/'results.csv').read_bytes(), spec['matrix_revision'])
        job = job_for(dict(name='Branch-coupled-terminal-N1',topology='Branch',
                          model_revision=package['model_revision'],initial_threshold=100.),package,matrix)
        self.assertEqual(len(job['trials']), 8)
        output = Path(os.environ['TMPDIR'])/'coupled-stopped-matrix'
        output.mkdir()
        _write(output/'matrix.json', matrix)
        _write(output/'job.json', job)
        live = inspect(spec['controller'])
        self.assertEqual(live['binding']['initial_main_pid'], os.getpid())
        self.assertEqual(live['execution'], 'running')
        memory=8*1024**3; tasks=128
        registry = Reservations(output/'leases.sqlite3', managed_units=True,
            capacity=dict(slots=1,memory_bytes=live['memory_max']+2*memory,
                          disk_bytes=12*1024**3,tasks=live['tasks_max']+2*tasks))
        lease = registry.reserve('coupled-stopped-eight-pattern-diagnostic',
            [dict(path=str(output/'run'),access='write')],ttl_seconds=7200,
            demands=dict(slots=1,memory_bytes=live['memory_max']+memory,
                         disk_bytes=8*1024**3,tasks=live['tasks_max']+tasks),
            controller_directory=spec['controller'])
        try:
            policy=policy_for_reservation(registry,lease['token'],memory_bytes=memory,tasks=tasks)
            result=run_job('diagnostic-evaluate',output/'job.json',source,controls/'runtime.json',
                           output/'run',1800,process_policy=policy)
            self.assertEqual((result['execution'],result['validity']),('completed','valid'))
            metrics=result['analysis']['metrics']
            self.assertTrue(metrics['diagnostic_only'])
            self.assertFalse(metrics['training_completed'])
            self.assertIsNone(metrics['evaluation_verdict'])
            self.assertEqual(len(metrics['trials']),8)
            self.assertEqual(metrics['pooled_counts']['targets'],1)
            self.assertEqual(metrics['pooled_counts']['foils'],7)
            self.assertTrue(audit_run_manifest(output/'run/run-manifest.json')['run_evidence_consistent'])
            model=load(output/'run/native/model.json')
            self.assertEqual(model,load(output/'run/native/model-after.json'))
            self.assertEqual(model['source_solo'],package)
            self.assertEqual(source_before,file_record(source))
            _write(output/'result.json',dict(kind='actual_coupled_stopped_matrix_result',
                schema_version=1,source=source_before,metrics=metrics,model_frozen=True,
                training_completed=False,threshold_selected=False,independent_evaluation=False,
                scientific_verdict=None))
        finally:
            registry.release(lease['token'],note='Exact coupled stopped model diagnostic child closed; no training convergence claim.')
