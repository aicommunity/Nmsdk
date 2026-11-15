"""Worker-only paired frozen observations of the actual stopped N0 states."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from ..contained_process import inspect
from ..native_evidence import load, require
from ..native_pipeline_worker import run_job, audit_run_manifest
from ..native_process_policy import policy_for_reservation
from ..resource_reservations import Reservations
from ..n1_protocol_robustness import _signed, _write
from ..phasea_matrix import from_git
from ..process_runner import verify_runtime
from ..stock_stopped_evaluation import job_for
from ..stopped_evidence import load_case


class N0LengthFrozenPairTest(unittest.TestCase):
    def test_same_matrix_preset_thresholds_keep_both_actual_models_frozen(self):
        controls = Path(os.environ['TIMELEARNER_N0_LENGTH_FROZEN_CONTROLS']).resolve(strict=True)
        spec = load(controls/'declaration.json')
        require(set(spec) == {'sources', 'runtime', 'bin_repository', 'controller', 'output', 'thresholds', 'roles'}
                and set(spec['sources']) == {'baseline', 'candidate'} and spec['thresholds'] == [100., .0117]
                and spec['roles'] in (['baseline'], ['candidate'], ['baseline', 'candidate']),
                'n0_length_frozen_declaration')
        runtime_path = Path(spec['runtime']).resolve(strict=True)
        runtime = load(runtime_path)
        verify_runtime(runtime)
        cases = {role: load_case(Path(path).resolve(strict=True)) for role, path in spec['sources'].items()}
        self.assertEqual(cases['baseline'][0]['configuration'], cases['candidate'][0]['configuration'])
        for case in cases.values():
            self.assertIsNone(case[0]['certificate'])
            self.assertEqual(case[0]['state_kind'], 'diagnostic')
            model = case[0]['configuration']['model']
            self.assertTrue(model['branch'])
            self.assertEqual(model['normalization'], 'N0')
            self.assertEqual(model['neuron_class'], 'NSPNeuronGen')
            self.assertEqual(model['frequency_hz'], 2000)
            self.assertEqual(model['initial_threshold'], 100.)
            self.assertEqual(len(model['inputs']), 4)
        output = Path(spec['output']).resolve()
        output.mkdir(parents=True, exist_ok=False)
        (output/'jobs').mkdir()
        state = inspect(spec['controller'])
        require(state['execution'] == 'running' and not state['all_processes_closed']
                and state['binding']['initial_main_pid'] == os.getpid(), 'n0_length_frozen_not_owner')
        memory = state['memory_max']
        registry = Reservations(output/'leases.sqlite3', managed_units=True,
            capacity=dict(slots=1, memory_bytes=memory+6*1024**3, disk_bytes=4*1024**3, tasks=512))
        lease = registry.reserve('n0-length-paired-frozen', [dict(path=str(output/'runs'), access='write')],
            demands=dict(slots=1, memory_bytes=memory+4*1024**3, disk_bytes=2*1024**3, tasks=256),
            controller_directory=spec['controller'], ttl_seconds=3600)
        policy = policy_for_reservation(registry, lease['token'], memory_bytes=4*1024**3, tasks=64)
        matrix = from_git(spec['bin_repository'])
        _write(output/'matrix.json', matrix)
        rows = []
        with patch.dict(os.environ, runtime['loader_environment']):
            for role in spec['roles']:
                case = cases[role]
                package = case[0]
                for threshold in spec['thresholds']:
                    name = role+('-wave100' if threshold == 100. else '-fixed00117')
                    row = dict(name=name, topology='Branch', model_revision=package['model_revision'],
                               initial_threshold=package['configuration']['model']['initial_threshold'])
                    job = job_for(row, package, matrix)
                    body = {k: v for k, v in job.items() if k != 'sha256'}
                    body['criterion'] = {**body['criterion'], 'anchor': 'last_stimulus',
                                         'reject_target_outside_window': True}
                    if threshold != row['initial_threshold']:
                        body.update(schema_version=2, diagnostic_threshold=threshold)
                    job = _signed(body)
                    self.assertEqual(len(job['trials']), 8)
                    path = output/'jobs'/(name+'.json')
                    _write(path, job)
                    result = run_job('diagnostic-evaluate', path, spec['sources'][role], runtime_path,
                                     output/'runs'/name, 900., process_policy=policy)
                    self.assertEqual((result['execution'], result['validity']), ('completed', 'valid'))
                    self.assertTrue(inspect(output/'runs'/name/'process/contained')['all_processes_closed'])
                    audit_run_manifest(output/'runs'/name/'run-manifest.json')
                    metrics = result['analysis']['metrics']
                    self.assertEqual(metrics['effective_threshold'], threshold)
                    self.assertEqual(len(metrics['trials']), 8)
                    self.assertTrue(metrics['diagnostic_only'])
                    self.assertFalse(metrics['training_completed'])
                    self.assertFalse(metrics['training_certificate_present'])
                    self.assertIsNone(metrics['evaluation_verdict'])
                    model = load(output/'runs'/name/'native/model.json')
                    self.assertEqual(model, load(output/'runs'/name/'native/model-after.json'))
                    recognition = model['source_recognition'] if threshold != 100. else model
                    self.assertEqual(recognition['source_solo'], package)
                    rows.append(dict(role=role, threshold=threshold, run=name, metrics=metrics))
                    _write(output/'progress.json', dict(rows=rows, scientific_verdict=None))
        registry.release(lease['token'], note='All paired frozen native groups closed; no convergence claim.')
        verify_runtime(runtime)
        _write(output/'index.json', dict(kind='n0_length_paired_frozen_diagnostic', schema_version=1,
            rows=rows, trials=8*len(rows), roles=spec['roles'],
            thresholds_selected_from_new_data=False, scientific_verdict=None))
