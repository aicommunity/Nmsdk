"""Real cold9 Console preflight/Train and frozen transfer on native declarations.

Sixteen N2 engineering cases cover unchanged completed boundaries and genuine
changed-graph terminal restoration. They do not establish N4 selectivity.
Train calls the public Console primitive while run_job's cold9 launch gate is
still closed; all results pass the production execution/package readers.
"""
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import unittest

from ..contained_process import inspect
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import load, require
from ..native_pipeline_worker import audit_execution, audit_run_manifest, run_job, validate_job
from ..native_process_policy import execute_native, policy_for_reservation
from ..process_runner import verify_runtime
from ..resource_reservations import Reservations
from ..runtime import applied_loader_environment


def signed(value):
    value = deepcopy(value); value.pop('sha256', None)
    return {**value, 'sha256': digest(value)}


class TerminalConsolePipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        controls = Path(os.environ['TIMELEARNER_TERMINAL_CONSOLE']).resolve(strict=True)
        cls.spec = load(controls/'declaration.json')
        fields = {'runtime', 'corpus', 'controller', 'output'}
        require(set(cls.spec) in (fields, fields | {'selected_cases'}), 'terminal_console_declaration')
        all_cases = {f'configured9-{topology}-terminal-{method}-{normalization}-completed'
                     for topology in ('classic','branch') for method in ('fixed4','window5') for normalization in ('N0','N1')}
        all_cases |= {f'{topology}-terminal-actual-{method}-{normalization}'
                      for topology in ('classic','branch') for method in ('fixed4','window5') for normalization in ('N0','N1')}
        selected = cls.spec.get('selected_cases', sorted(all_cases))
        require(type(selected) is list and len(selected) == len(set(selected)) and set(selected) <= all_cases,
                'terminal_console_selected_case_inventory')
        cls.selected_cases = set(selected)
        for completed in (False, True):
            for topology in ('classic','branch'):
                prefix = 'configured9-'+topology if completed else topology+'-terminal-actual-'
                require(any(name.startswith(prefix) for name in selected), 'terminal_console_selected_pair_incomplete')
        cls.runtime_path = Path(cls.spec['runtime']).resolve(strict=True)
        require(cls.runtime_path.parent == controls, 'terminal_console_runtime_not_in_controls')
        cls.runtime = load(cls.runtime_path); verify_runtime(cls.runtime)
        cls.executable = Path(cls.runtime['executable']['path'])
        require(cls.executable.parent.resolve(strict=True) == Path(os.environ['TIMELEARNER_CONSOLE_RUNTIME_FILES']).resolve(strict=True),
                'terminal_console_runtime_binding_changed')
        cls.corpus = Path(cls.spec['corpus']).resolve(strict=True)
        require(cls.corpus == Path(os.environ['TIMELEARNER_NATIVE_TERMINAL_CONFIGURATION9']).resolve(strict=True),
                'terminal_console_corpus_binding_changed')
        cls.output = Path(cls.spec['output']).resolve()
        require(cls.output.is_relative_to(Path(os.environ['TMPDIR']).resolve(strict=True)) and not cls.output.exists(),
                'terminal_console_output_requires_owned_fresh_TMPDIR')
        cls.output.mkdir(parents=True)
        live = inspect(Path(cls.spec['controller']))
        require(live['execution'] == 'running' and live['binding']['initial_main_pid'] == os.getpid(),
                'terminal_console_requires_actual_contained_controller')
        cls.memory = live['memory_max']

    def cases(self, completed):
        for topology in ('classic', 'branch'):
            for method in ('fixed4', 'window5'):
                for normalization in ('N0', 'N1'):
                    folder = (f'configured9-{topology}-terminal-{method}-{normalization}-completed' if completed else
                              f'{topology}-terminal-actual-{method}-{normalization}')
                    if folder not in self.selected_cases:
                        continue
                    with self.subTest(case=folder):
                        self.case(folder, completed=completed)

    def case(self, folder, *, completed):
        source = self.corpus/folder; job = load(source/'cold9-job.json')
        require(job['configuration']['schema_version'] == 9 and len(job['configuration']['model']['inputs']) == 2,
                'terminal_console_requires_native_N2_cold9_declaration')
        validate_job('train', job)
        root = self.output/folder; root.mkdir()
        registry = Reservations(root/'leases.sqlite3', managed_units=True,
            capacity=dict(slots=1, memory_bytes=self.memory+2*1024**3, disk_bytes=2*1024**3, tasks=512))
        lease = registry.reserve('terminal-console-'+folder, [dict(path=str(root/'runs'), access='write')], ttl_seconds=3600,
            demands=dict(slots=1, memory_bytes=self.memory+1024**3, disk_bytes=1024**3, tasks=256),
            controller_directory=self.spec['controller'])
        policy = policy_for_reservation(registry, lease['token'], memory_bytes=1024**3, tasks=64)
        records = []
        def invoke(mode, document, source_path=None):
            registry.heartbeat(lease['token'], ttl_seconds=3600)
            document = signed(document); path = root/(mode+'-job.json')
            path.write_text(json.dumps(document, indent=2, allow_nan=False)+'\n', encoding='utf-8')
            destination = root/'runs'/mode; destination.parent.mkdir(exist_ok=True)
            if mode == 'train':
                destination.mkdir()
                with applied_loader_environment(self.runtime):
                    process = execute_native(self.runtime, ['--app-ini', self.runtime['app_ini']['path'],
                        '--timelearner-train', str(path), '--timelearner-output', str(destination/'native')],
                        self.executable.parent, destination/'process', 600, policy)
                self.assertEqual(process['execution'], 'completed', process)
                self.assertEqual(process['runtime_provenance'], 'loaded_files_captured')
                result = audit_execution('train', destination/'native', document)
                self.assertIsNone(result['evaluation_verdict'])
                (destination/'integration-audit.json').write_text(json.dumps(dict(
                    source_job_sha256=document['sha256'], runtime_fingerprint=self.runtime['runtime_fingerprint'],
                    analysis=result, native_process=process, scope='Actual public Console primitive, cold9 production launch gate retained',
                    scientific_verdict=None), indent=2, allow_nan=False)+'\n', encoding='utf-8')
            else:
                result = run_job(mode, path, source_path, self.runtime_path, destination, 600, process_policy=policy)
                self.assertEqual((result['execution'], result['validity']), ('completed', 'valid'))
                self.assertTrue(audit_run_manifest(destination/'run-manifest.json')['run_evidence_consistent'])
            self.assertTrue(inspect(destination/'process/contained')['all_processes_closed'])
            records.append(dict(operation=mode, output=str(destination), job_sha256=document['sha256']))
            return destination/'native'
        try:
            preflight = invoke('preflight', job)
            self.assertEqual(load(preflight/'execution.json')['schema_version'], 6)
            self.assertIsNone(load(preflight/'execution.json')['terminal_boundary'])
            native = invoke('train', job)
            package_path = native/('train_learned_state.json' if completed else 'train_stopped_state.json')
            package = load(package_path); execution = load(native/'execution.json')
            self.assertEqual(execution['schema_version'], 6); self.assertEqual(package['schema_version'], 8)
            self.assertEqual(execution['completed_boundary'], completed)
            self.assertEqual(package['certificate'] is not None, completed)
            self.assertEqual(package['terminal_policy'], job['configuration']['terminal_selection'])
            if completed:
                self.assertIsNone(package['terminal_event'])
            else:
                self.assertEqual(package['training_outcome'], 'budget_exhausted')
                self.assertEqual(package['terminal_event']['status'], 'restored')
                self.assertNotEqual(package['model_revision'], package['historical_state']['model_revision'])
                self.assertEqual(package['model_epoch'], package['historical_state']['model_epoch']+1)
            from ..composite_primary import filesystem_primary_resolver
            source_archive = package['historical_state']['measurement_archive']
            # Corruption must be rejected despite a newly signed execution.
            from ..terminal_execution_evidence import audit_terminal_execution
            from ..native_evidence import EvidenceError
            names = {r['path'] for r in execution['artifacts']}
            changed = deepcopy(execution); changed['terminal_boundary']['actual_model_epoch'] += 1
            changed = signed(changed)
            with self.assertRaises(EvidenceError):
                audit_terminal_execution(changed, native, names, mode='train', job=job, package=package)
            changed = deepcopy(execution); changed['terminal_selection']['maximum_wall_seconds'] += .125
            changed = signed(changed)
            with self.assertRaises(EvidenceError):
                audit_terminal_execution(changed, native, names, mode='train', job=job, package=package)
            # A missing real CSV cannot be concealed by its embedded copy.
            relative = source_archive['records'][0]['raw_trials'][0]['primary_ref']['relative_path']
            primary = native/relative; saved = primary.read_bytes(); primary.unlink()
            try:
                with self.assertRaises(EvidenceError):
                    audit_execution('train', native, job)
            finally:
                primary.write_bytes(saved)
            self.assertEqual(filesystem_primary_resolver(native)(relative), saved)

            owner = job['owner_class']; implementation = job['implementation_id']
            conversion = dict(schema_version=1, mode='identity', resistance_bounds=[])
            if completed:
                converted = invoke('export', dict(kind='timelearner_native_recognition_export_job', schema_version=1,
                    implementation_id=implementation, source_solo=package, conversion_spec=conversion), package_path)
                model = load(converted/'model.json')
            else:
                model = None
            target = job['configuration']['model']['initial_isi']; foil = deepcopy(target); foil[-1] *= 1.5
            frequency = job['configuration']['model']['frequency_hz']; duration = max(2., sum(foil)+.5)
            run = folder+'/frozen-transport'; trials = []
            for index, (label, pattern) in enumerate((('target', target), ('foil', foil), ('foil', foil), ('target', target))):
                trials.append(dict(run_id=run, trial_id=run+'/'+str(index), sample_id=label+'-pattern', label=label,
                    pattern_hash=digest(pattern), pattern_isi=pattern, duration=duration,
                    maximum_samples=math.ceil(duration*frequency)+1, reset_policy='reset_per_trial', record_threshold_potential=True))
            evaluation = dict(kind='timelearner_native_evaluation_job' if completed else 'timelearner_native_diagnostic_evaluation_job',
                schema_version=1, owner_class=owner, implementation_id=implementation, maximum_model_ticks=200000,
                run_id=run, coverage_policy='per_trial_windows', criterion=dict(id='post_anchor_target_whole_window_foil_v1',
                anchor='onset', begin_offset=0., end_offset=None, reject_target_outside_window=True), trials=trials)
            if completed:
                evaluation['source_recognition'] = model
            else:
                evaluation.update(source_stopped=package, conversion_spec=conversion)
            invoke('evaluate' if completed else 'diagnostic-evaluate', evaluation, package_path)
            self.assertEqual(load(package_path), package)
            self.assertEqual(load(native/'execution.json'), execution)
            verify_runtime(self.runtime)
            (root/'result.json').write_text(json.dumps(dict(operations=records, actual_cold_training=True,
                original_learned_state_used_as_seed=False, original_profile_images_used=True, source_unchanged=True,
                engineering_only=True, scientific_verdict=None), indent=2)+'\n', encoding='utf-8')
        finally:
            registry.release(lease['token'], note='All declared Console primitive/pipeline native groups closed')

    def test_completed_native_cold9_preflight_train_export_frozen8_variants(self):
        self.cases(completed=True)

    def test_changed_graph_cold9_preflight_train_stopped_frozen8_variants(self):
        self.cases(completed=False)
