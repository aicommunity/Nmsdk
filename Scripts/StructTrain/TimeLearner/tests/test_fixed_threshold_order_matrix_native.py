"""Worker-only counterbalanced order control of an actual frozen threshold run.

All neural execution and scoring use the ordinary production CLI. Counts are
measurements: the test does not require order invariance or a successful target.
"""
import contextlib
import io
import math
import os
from pathlib import Path
import unittest

from ..__main__ import main
from ..collector_provenance import _frozen
from ..contained_process import inspect
from ..native_calibration_worker import _signed, _write
from ..native_evidence import load, parse_json_bytes, require
from ..native_pipeline_worker import audit_run_manifest
from ..native_process_policy import policy_for_reservation
from ..phasea_matrix import extract, trial_design
from ..process_runner import verify_runtime
from ..recognition_metrics import load_diagnostic_evaluation
from ..resource_reservations import Reservations
from ..runtime import file_record


class FixedThresholdOrderMatrixNativeTest(unittest.TestCase):
    def test_same_frozen_model_and_threshold_with_target_in_every_position(self):
        controls = Path(os.environ['TIMELEARNER_FIXED_ORDER_CONTROLS']).resolve(strict=True)
        source = Path(os.environ['TIMELEARNER_FIXED_ORDER_SOURCE_RUN']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration) == {'controller', 'source_manifest_sha256', 'source_job_sha256',
            'source_package_sha256', 'source_model_revision', 'threshold', 'matrix_revision',
            'maximum_wall_seconds', 'leaf_memory_bytes'}, 'fixed_order_control_fields')
        manifest_before = file_record(source/'run-manifest.json')
        self.assertEqual(manifest_before['sha256'], declaration['source_manifest_sha256'])
        self.assertTrue(audit_run_manifest(source/'run-manifest.json')['run_evidence_consistent'])
        manifest = load(source/'run-manifest.json')
        self.assertEqual((manifest['operation'], manifest['execution'], manifest['validity']),
                         ('diagnostic-evaluate', 'completed', 'valid'))
        records = {r['path']: r for r in manifest['artifacts']}

        def original(relative, maximum):
            raw, record = _frozen(source/relative, maximum)
            require(relative in records and all(record[k] == records[relative][k]
                    for k in ('bytes', 'sha256')), 'fixed_order_original_artifact_changed')
            return raw

        original_job = parse_json_bytes(original('input/job.json', 384*1024**2))
        self.assertEqual(original_job['sha256'], declaration['source_job_sha256'])
        self.assertEqual(original_job['schema_version'], 2)
        self.assertEqual(original_job['diagnostic_threshold'], declaration['threshold'])
        self.assertEqual(original_job['conversion_spec'],
                         dict(schema_version=1, mode='identity', resistance_bounds=[]))
        package_path = source/'input/source/train_stopped_state.json'
        package_before = file_record(package_path)
        self.assertEqual(package_before['sha256'], declaration['source_package_sha256'])
        package = original_job['source_stopped']
        self.assertEqual(package['model_revision'], declaration['source_model_revision'])
        self.assertIsNone(package['certificate'])
        self.assertFalse(manifest['analysis']['metrics']['training_completed'])
        self.assertTrue(manifest['analysis']['metrics']['diagnostic_threshold_experiment'])
        self.assertEqual(manifest['analysis']['metrics']['effective_threshold'], declaration['threshold'])
        model_spec = package['configuration']['model']
        self.assertFalse(model_spec['branch'])
        self.assertEqual(model_spec['normalization'], 'N0')
        self.assertEqual(model_spec['frequency_hz'], 2000)
        matrix = extract((controls/'Parameters_00.xml').read_bytes(),
                         (controls/'results.csv').read_bytes(), declaration['matrix_revision'])
        run_id = 'Classic-stock-N0-fixed-threshold/order-eight-positions'
        trials = trial_design(matrix, model_spec['initial_isi'], run_id, duration=2., rotations=8)
        source_trials = original_job['trials']
        self.assertEqual(len(source_trials), 8)
        comparable_fields = ('sample_id', 'label', 'pattern_hash', 'pattern_isi', 'duration',
                             'maximum_samples', 'reset_policy', 'record_threshold_potential')
        self.assertTrue(all(all(a[k] == b[k] for k in comparable_fields)
                            for a, b in zip(source_trials, trials[:8])))
        job = {k: v for k, v in original_job.items() if k != 'sha256'}
        job.update(run_id=run_id, trials=trials,
                   maximum_model_ticks=sum(math.ceil(t['duration']*2000)+4 for t in trials))
        job = _signed(job)
        unchanged = set(original_job)-{'sha256', 'run_id', 'trials', 'maximum_model_ticks'}
        self.assertTrue(all(job[k] == original_job[k] for k in unchanged))
        runtime_path = controls/'runtime.json'
        runtime = load(runtime_path)
        self.assertTrue(runtime == load(source/'process/runtime.json'), 'source runtime changed')
        verify_runtime(runtime)
        live = inspect(declaration['controller'])
        self.assertEqual((live['execution'], live['binding']['initial_main_pid']), ('running', os.getpid()))
        wall, memory = declaration['maximum_wall_seconds'], declaration['leaf_memory_bytes']
        require(type(wall) is int and 1 <= wall <= 7200 and type(memory) is int and
                1024**3 <= memory <= 8*1024**3, 'fixed_order_native_limits')
        output = Path(os.environ['TMPDIR'])/'fixed-threshold-order-matrix'
        output.mkdir(); (output/'baseline').mkdir()
        _write(output/'matrix.json', matrix); _write(output/'job.json', job)
        # Do not retain a second hundred-megabyte embedded training archive
        # while the production CLI independently reads and audits its inputs.
        del original_job, job, package
        (output/'baseline/source-run-manifest.json').write_bytes((source/'run-manifest.json').read_bytes())
        (output/'baseline/evaluation.json').write_bytes(original('native/evaluation.json', 16*1024**2))
        baseline_spec = load(output/'baseline/evaluation.json')
        for row in baseline_spec['trials']:
            (output/'baseline'/row['observation']).write_bytes(
                original('native/'+row['observation'], 16*1024**2))
        registry = Reservations(output/'leases.sqlite3', managed_units=True,
            capacity=dict(slots=1, memory_bytes=live['memory_max']+2*memory,
                          disk_bytes=16*1024**3, tasks=live['tasks_max']+256))
        lease = registry.reserve('actual-fixed-threshold-counterbalanced-order',
            [dict(path=str(output/'run'), access='write')], ttl_seconds=14400,
            demands=dict(slots=1, memory_bytes=live['memory_max']+memory,
                         disk_bytes=12*1024**3, tasks=live['tasks_max']+128),
            controller_directory=declaration['controller'])
        transcript = io.StringIO()
        try:
            policy = policy_for_reservation(registry, lease['token'], memory_bytes=memory, tasks=128)
            _write(output/'process-policy.json', policy)
            with contextlib.redirect_stdout(transcript), contextlib.redirect_stderr(transcript):
                code = main(['diagnostic-evaluate', str(output/'job.json'), '--source-stopped',
                    str(package_path), '--runtime-manifest', str(runtime_path), '--wall-seconds', str(wall),
                    '--process-policy', str(output/'process-policy.json'), '--output', str(output/'run')])
            self.assertEqual(code, 0, transcript.getvalue())
            self.assertTrue(inspect(output/'run/process/contained')['all_processes_closed'])
            self.assertTrue(audit_run_manifest(output/'run/run-manifest.json')['run_evidence_consistent'])
            result = load(output/'run/run-manifest.json')
            self.assertEqual((result['execution'], result['validity']), ('completed', 'valid'))
            metrics = result['analysis']['metrics']
            self.assertEqual((metrics['pooled_counts']['targets'], metrics['pooled_counts']['foils']), (8, 56))
            self.assertEqual(metrics['effective_threshold'], declaration['threshold'])
            self.assertTrue(metrics['diagnostic_only'])
            self.assertFalse(metrics['training_completed'])
            self.assertIsNone(metrics['evaluation_verdict'])
            _, actual = load_diagnostic_evaluation(output/'run/native/evaluation.json')
            _, baseline = load_diagnostic_evaluation(output/'baseline/evaluation.json')
            self.assertEqual(len(actual), 64)
            self.assertTrue(all(o['complete'] and o['valid'] for o in actual))
            # This is replay of the same first eight conditions, not an
            # optimistic prediction about the seven subsequent rotations.
            self.assertTrue(all(a['samples'] == b['samples'] and a['model_before'] == b['model_before']
                                for a, b in zip(actual[:8], baseline)), 'first rotation baseline differs')
            self.assertEqual(file_record(output/'run/native/model.json')['sha256'],
                             records['native/model.json']['sha256'])
            self.assertEqual(file_record(output/'run/native/model-after.json')['sha256'],
                             records['native/model.json']['sha256'])
            rows = []
            for index, (observation, trial) in enumerate(zip(actual, trials)):
                self.assertEqual(observation['sample_id'], trial['sample_id'])
                expected = []; total = 0.
                for interval in trial['pattern_isi']:
                    total += interval; expected.append(total)
                self.assertEqual(len(observation['stimulus_times']), len(expected))
                self.assertTrue(all(abs(t-observation['begin']-e) <= 1/2000+1e-10
                                    for t, e in zip(observation['stimulus_times'], expected)))
                scored = next(r for r in metrics['trials'] if r['trial_id'] == trial['trial_id'])
                rows.append(dict(rotation=index//8, position=index%8, sample_id=trial['sample_id'],
                    trial_id=trial['trial_id'], label=trial['label'], classification=scored['classification'],
                    spike_count=observation['spike_count'],
                    stimulus_times_after_begin=[t-observation['begin'] for t in observation['stimulus_times']],
                    spike_times_after_begin=[t-observation['begin'] for t in observation['spike_times']],
                    spikes_after_last_input=[t-observation['stimulus_times'][-1]
                                            for t in observation['spike_times']]))
            self.assertEqual(sorted(r['position'] for r in rows if r['sample_id'] ==
                next(p['sample_id'] for p in matrix['patterns'] if p['label'] == 'target')), list(range(8)))
            self.assertEqual(manifest_before, file_record(source/'run-manifest.json'))
            self.assertEqual(package_before, file_record(package_path))
            _write(output/'result.json', dict(kind='actual_fixed_threshold_order_matrix_result',
                schema_version=1, source_manifest=manifest_before, source_package=package_before,
                source_model_revision=declaration['source_model_revision'], threshold=declaration['threshold'],
                first_rotation_waveforms_equal=True, frozen_model_bytes_equal=True, rows=rows, metrics=metrics,
                training_completed=False, threshold_selected=False, independent_evaluation=False,
                random_independent_repetitions=False, iti_changed=False, reset_policy='reset_per_trial',
                scientific_verdict=None))
        finally:
            (output/'public-cli.log').write_text(transcript.getvalue(), encoding='utf-8')
            registry.release(lease['token'], note='Fixed-threshold order child closed; no convergence claim.')
