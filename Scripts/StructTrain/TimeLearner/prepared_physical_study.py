"""Declared Windows frozen DATA studies after the actual eight-trial replay.

Uses the shared foil/cadence declarations, native process backend, full audit
and response comparator. No training or threshold selection occurs here.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

from .native_evidence import require
from .runtime import file_record


def _write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def _actor(actor, commit):
    require(type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit) is not None and
        Path(__file__).resolve(strict=True) == actor/'Scripts/StructTrain/TimeLearner/prepared_physical_study.py',
        'physical_study_actor_identity')
    def git(*args):
        return subprocess.check_output(['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0',
            '-C', str(actor), *args], stderr=subprocess.PIPE, timeout=60,
            creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    require(git('rev-parse', 'HEAD') == commit and not git('status', '--porcelain',
        '--untracked-files=all', '--ignore-submodules=all'), 'physical_study_python_source_changed')


def declare(original, run_id, study, runtime, *, threshold, memory_bytes, wall_seconds):
    """Reuse the production mathematical protocols; never infer an expected score."""
    require(type(study) is dict, 'physical_study_protocol_schema')
    if study == {'protocol': 'new_foils'}:
        from .frozen_physical_foil_study import declare_job, condition
        job, design = declare_job(original, run_id)
        identity = condition(job, design, runtime, dict(threshold=threshold,
            native_memory_bytes=memory_bytes, maximum_native_wall_seconds=wall_seconds))
    elif set(study) == {'protocol', 'protocol_document'} and study['protocol'] == 'heldout_matched_duration':
        require(type(study['protocol_document']) is dict, 'physical_study_holdout_protocol_required')
        from .frozen_physical_foil_study import declare_job, condition
        job, design = declare_job(original, run_id, holdout_protocol=study['protocol_document'])
        identity = condition(job, design, runtime, dict(threshold=threshold,
            native_memory_bytes=memory_bytes, maximum_native_wall_seconds=wall_seconds))
    elif set(study) == {'protocol', 'rotation', 'cadence', 'reset_policy'} and study['protocol'] == 'cadence':
        from .frozen_physical_iti_study import declare_job, condition
        job, design = declare_job(original, run_id, rotation=study['rotation'],
            cadence=study['cadence'], reset_policy=study['reset_policy'])
        identity = condition(job, design, runtime, threshold=threshold)
    elif set(study) == {'protocol', 'predecessor', 'cadence', 'reset_policy'} and study['protocol'] == 'predecessor':
        from .frozen_physical_predecessor_study import declare_job, condition
        job, design = declare_job(original, run_id, predecessor=study['predecessor'],
            cadence=study['cadence'], reset_policy=study['reset_policy'])
        identity = condition(job, design, runtime, threshold=threshold)
    else:
        raise ValueError('physical_study_protocol_schema')
    return job, design, identity


def _source(controls):
    from .native_pipeline_worker import audit_execution, validate_job
    controls = Path(controls).resolve(strict=True)
    spec = json.loads((controls/'specification.json').read_bytes())
    inputs = Path(spec['inputs']).resolve(strict=True)
    output = Path(spec['output']).resolve(strict=True)
    terminal = json.loads((output/'terminal.json').read_bytes())
    process = json.loads((output/'process-result.json').read_bytes())
    require(terminal['kind'] == 'timelearner_actual_windows_physical_replay' and
        terminal['execution'] == 'completed' and terminal['validity'] == 'valid' and
        terminal['transfer_valid'] and terminal['all_eight_waveforms_and_events_preserved'] and
        len(terminal['rows']) == 8 and all(r['waveform_preserved'] and
            r['stimulus_and_spike_events_preserved'] for r in terminal['rows']) and
        process['execution'] == 'completed' and process['all_processes_closed'] and
        process['runtime_provenance'] == 'loaded_files_captured', 'physical_study_source_replay_not_verified')
    model_path = inputs/'model.json'; job_path = inputs/'job.json'
    model = json.loads(model_path.read_bytes()); job = json.loads(job_path.read_bytes())
    require(model == job['source_model_data'] and model['sha256'] == terminal['source_model_data_sha256'] and
        model['model_revision'] == terminal['model_revision'], 'physical_study_source_model_changed')
    validate_job('physical-model-evaluate', job, (model,))
    audited = audit_execution('physical-model-evaluate', output/'native', job, (model,))
    metrics = audited['metrics']
    require(audited['frozen_model_verified'] and metrics['validity'] == 'valid' and metrics['data_only'] and
        len(job['trials']) == len(metrics['trials']) == 8 and len({t['sample_id'] for t in job['trials']}) == 8 and
        sum(t['label'] == 'target' for t in job['trials']) == 1 and
        sum(t['label'] == 'foil' for t in job['trials']) == 7 and
        metrics['model_revision'] == model['model_revision'] and
        metrics['pooled_counts'] == terminal['counts'] and
        metrics['effective_threshold'] == terminal['threshold'], 'physical_study_source_audit_changed')
    paths = [controls/'specification.json', controls/'runtime.json', output/'terminal.json',
        output/'process-result.json', output/'native/execution.json', model_path, job_path,
        *[output/'native'/f'trial-{i}.json' for i in range(8)]]
    records = {str(p): file_record(p) for p in paths}
    return dict(spec=spec, model=model, model_path=model_path, job=job, metrics=metrics,
        output=output, runtime=json.loads((controls/'runtime.json').read_bytes()), records=records)


def prepare(declaration):
    fields = {'kind', 'schema_version', 'source_controls', 'destination', 'inputs', 'output',
        'run_id', 'study', 'python_source', 'python_root'}
    require(type(declaration) is dict and set(declaration) == fields and
        declaration['kind'] == 'timelearner_physical_study_preparation' and
        type(declaration['schema_version']) is int and declaration['schema_version'] == 1,
        'physical_study_preparation_schema')
    base = Path('C:/Projects/TimeLearnerWorker').resolve(strict=True)
    actor = Path(declaration['python_source']).resolve(strict=True)
    destination = Path(declaration['destination']).resolve(strict=True)
    inputs, output = [Path(declaration[n]).absolute() for n in ('inputs', 'output')]
    require(os.name == 'nt' and actor.is_relative_to(base) and destination.is_relative_to(base/'controls') and
        inputs.is_relative_to(base/'jobs') and output.is_relative_to(base/'jobs') and inputs != output and
        not inputs.exists() and not output.exists(), 'physical_study_fresh_worker_paths')
    _actor(actor, declaration['python_root'])
    source = _source(declaration['source_controls'])
    memory_bytes, wall_seconds = 4*1024**3, 7200
    job, design, identity = declare(source['job'], declaration['run_id'], declaration['study'], source['runtime'],
        threshold=source['metrics']['effective_threshold'], memory_bytes=memory_bytes, wall_seconds=wall_seconds)
    require(job['source_model_data'] == source['model'], 'physical_study_declaration_changed_model')
    inputs.mkdir(parents=True); os.link(source['model_path'], inputs/'model.json'); _write(inputs/'job.json', job)
    _write(destination/'design.json', design); _write(destination/'condition.json', identity)
    runtime = source['runtime']
    from .runtime import runtime_content_identity, digest_json
    backend = file_record(actor/'Scripts/StructTrain/TimeLearner/windows_process.py')
    require(backend['sha256'] == runtime['windows_backend']['sha256'], 'physical_study_backend_changed')
    runtime['windows_backend'] = backend; runtime['runtime_identity'] = runtime_content_identity(runtime)
    runtime['runtime_fingerprint'] = digest_json(runtime['runtime_identity']); _write(destination/'runtime.json', runtime)
    worker = actor/'Scripts/StructTrain/TimeLearner/prepared_physical_study.py'
    spec = dict(kind='timelearner_prepared_physical_study', schema_version=1, python_source=str(actor),
        python_root=declaration['python_root'], sdk_source=source['spec']['sdk_source'], inputs=str(inputs),
        output=str(output), worker_sha256=file_record(worker)['sha256'], source_controls=declaration['source_controls'],
        source_records=source['records'], study=declaration['study'], run_id=declaration['run_id'],
        expected_trials=len(job['trials']), job_sha256=job['sha256'], model_revision=source['model']['model_revision'],
        threshold=source['metrics']['effective_threshold'], condition_fingerprint=identity['condition_fingerprint'],
        input_inventory={p.name: file_record(p) for p in inputs.iterdir()},
        design_record=file_record(destination/'design.json'), condition_record=file_record(destination/'condition.json'),
        memory_bytes=memory_bytes, maximum_wall_seconds=wall_seconds, minimum_free_bytes=2*1024**3,
        maximum_output_bytes=512*1024**2, lock_file=str(base/'locks/worker.lock'),
        training_completed=False, scientific_verdict=None)
    _write(destination/'specification.json', spec)
    require(all(file_record(Path(p)) == row for p, row in source['records'].items()),
        'physical_study_source_changed_during_preparation')
    return dict(prepared=True, expected_trials=len(job['trials']), study=spec['study'],
        model_revision=spec['model_revision'], threshold=spec['threshold'],
        condition_fingerprint=spec['condition_fingerprint'], native_execution_started=False, scientific_verdict=None)


def run(controls):
    from .native_pipeline_worker import audit_execution, validate_job
    from .native_cli import inspect_native_cli
    from .native_gate import _environment
    from .runtime import source_closure
    from .windows_process import execute
    from .trial_response_comparison import trial_response_comparison
    controls = Path(controls).resolve(strict=True); spec = json.loads((controls/'specification.json').read_bytes())
    require(os.name == 'nt' and spec['kind'] == 'timelearner_prepared_physical_study' and
        spec['schema_version'] == 1 and file_record(Path(__file__))['sha256'] == spec['worker_sha256'],
        'physical_study_worker_changed')
    _actor(Path(spec['python_source']).resolve(strict=True), spec['python_root'])
    base = Path('C:/Projects/TimeLearnerWorker').resolve(strict=True)
    inputs = Path(spec['inputs']).resolve(strict=True); output = Path(spec['output']).absolute()
    require(controls.is_relative_to(base/'controls') and inputs.is_relative_to(base/'jobs') and
        output.is_relative_to(base/'jobs') and not output.exists() and
        Path(spec['lock_file']) == base/'locks/worker.lock', 'physical_study_worker_paths')
    def unchanged():
        require({p.name: file_record(p) for p in inputs.iterdir()} == spec['input_inventory'] and
            file_record(controls/'design.json') == spec['design_record'] and
            file_record(controls/'condition.json') == spec['condition_record'] and
            all(file_record(Path(p)) == row for p, row in spec['source_records'].items()),
            'physical_study_bound_source_changed')
    unchanged(); source = _source(spec['source_controls'])
    require(source['records'] == spec['source_records'], 'physical_study_source_record_set_changed')
    runtime = json.loads((controls/'runtime.json').read_bytes()); runtime_before = file_record(controls/'runtime.json')
    sdk = Path(spec['sdk_source']).resolve(strict=True)
    require(source_closure(sdk) == runtime['source_closure'], 'physical_study_native_sdk_changed')
    job = json.loads((inputs/'job.json').read_bytes()); model = source['model']
    expected, design, identity = declare(source['job'], spec['run_id'], spec['study'], runtime,
        threshold=spec['threshold'], memory_bytes=spec['memory_bytes'], wall_seconds=spec['maximum_wall_seconds'])
    require(job == expected and job['sha256'] == spec['job_sha256'] and
        json.loads((controls/'design.json').read_bytes()) == design and
        identity == json.loads((controls/'condition.json').read_bytes()) and
        identity['condition_fingerprint'] == spec['condition_fingerprint'], 'physical_study_predeclared_job_changed')
    validate_job('physical-model-evaluate', job, (model,)); output.mkdir(parents=True)
    try:
        _write(output/'preflight.json', inspect_native_cli(runtime, ['physical-model-evaluate'],
            require_file_source=True, evidence_output=output))
        last = [0.]
        def monitor(state):
            if time.monotonic()-last[0] < 1: return
            last[0] = time.monotonic()
            import shutil
            require(shutil.disk_usage(output).free >= spec['minimum_free_bytes'], 'physical_study_disk_floor')
            total = 0
            for p in output.rglob('*'):
                try:
                    if p.is_file(): total += p.stat().st_size
                except FileNotFoundError: pass
            require(total <= spec['maximum_output_bytes'], 'physical_study_output_budget')
        args = ['--app-ini', runtime['app_ini']['path'], '--timelearner-physical-model-evaluate',
            str(inputs/'job.json'), '--timelearner-output', str(output/'native')]
        with _environment({k: runtime['loader_environment'].get(k) for k in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}):
            process = execute(runtime, args, Path(runtime['executable']['path']).parent, output/'process',
                memory_bytes=spec['memory_bytes'], maximum_processes=64,
                maximum_wall_seconds=spec['maximum_wall_seconds'], lock_file=base/'locks/worker.lock',
                cooperative_capture=True, monitor=monitor)
        _write(output/'process-result.json', process)
        require(process['execution'] == 'completed' and process['all_processes_closed'] and
            process['runtime_provenance'] == 'loaded_files_captured', 'physical_study_native_incomplete')
        audited = audit_execution('physical-model-evaluate', output/'native', job, (model,))
        _write(output/'audit.json', audited); metrics = audited['metrics']
        require(audited['frozen_model_verified'] and metrics['validity'] == 'valid' and metrics['data_only'] and
            len(metrics['trials']) == spec['expected_trials'] and metrics['model_revision'] == spec['model_revision'] and
            metrics['effective_threshold'] == spec['threshold'], 'physical_study_audit_invalid')
        source_trials = {r['sample_id']: r for r in source['job']['trials']}
        source_observations = {r['sample_id']: json.loads((source['output']/'native'/f'trial-{i}.json').read_bytes())
            for i, r in enumerate(source['job']['trials'])}
        comparisons = []
        # Only a new-foil grid repeats the source observation protocol. Cadence
        # changes the coverage/window length, even for its first reset trial;
        # comparing it with the original full two-second source would conflate
        # different conditions. Paired reset/preserve runs need their own
        # SAME-cadence first-trial comparison at the matrix level.
        controls_to_compare = [i for i,t in enumerate(job['trials']) if
            t['sample_id'] in source_trials and spec['study']['protocol'] in ('new_foils','heldout_matched_duration')]
        require(spec['study']['protocol'] not in ('new_foils','heldout_matched_duration') or len(controls_to_compare) == 1,
            'physical_study_missing_repeated_control')
        with trial_response_comparison(model, physical_data=True) as compare:
            for i in controls_to_compare:
                observed = json.loads((output/'native'/f'trial-{i}.json').read_bytes())
                comparison = compare(source_observations[observed['sample_id']], observed)
                require(comparison['response_preserved'], 'physical_study_reset_control_changed')
                comparisons.append(comparison)
        cadence_evidence = None
        if spec['study']['protocol'] in ('cadence', 'predecessor'):
            from .native_evidence import number, equal, after
            observed = [json.loads((output/'native'/f'trial-{i}.json').read_bytes())
                        for i in range(spec['expected_trials'])]
            quiet = number(observed[-1]['end'])-number(observed[-1]['stimulus_times'][-1])
            require(quiet > 2 or equal(quiet, 2), 'physical_study_final_quiet_tail_incomplete')
            cadence_evidence = dict(final_quiet_tail_seconds=quiet,
                complete_contiguous_observations_verified=True,
                paired_same_cadence_first_trial_comparison_pending=True,
                carryover_events_not_causally_assigned_to_a_single_pattern=True,
                actual_timing_and_events=[dict(trial_id=o['trial_id'], sample_id=o['sample_id'],
                    reset_policy=o['reset_policy'], stimulus_times=o['stimulus_times'], spike_times=o['spike_times'],
                    events_before_current_first_input=[t for t in o['spike_times'] if after(o['stimulus_times'][0], t)],
                    events_before_current_last_input=[t for t in o['spike_times'] if after(o['stimulus_times'][-1], t)],
                    first_input_interval_from_previous=None if i == 0 else
                        o['stimulus_times'][0]-observed[i-1]['stimulus_times'][0]) for i,o in enumerate(observed)])
        unchanged(); require(file_record(controls/'runtime.json') == runtime_before and
            source_closure(sdk) == runtime['source_closure'], 'physical_study_runtime_changed')
        _actor(Path(spec['python_source']).resolve(strict=True), spec['python_root'])
        terminal = dict(kind='timelearner_actual_windows_frozen_physical_study', schema_version=1,
            execution='completed', validity='valid', study=spec['study'], model_revision=spec['model_revision'],
            threshold=spec['threshold'], trials=spec['expected_trials'], counts=metrics['pooled_counts'],
            condition_fingerprint=spec['condition_fingerprint'], repeated_control_comparisons=comparisons,
            source_protocol_repeated_control_checked=spec['study']['protocol'] in ('new_foils','heldout_matched_duration'),
            cadence_evidence=cadence_evidence,
            frozen_model_verified=True, complete_native_observations=True, threshold_selected=False,
            training_performed=False, source_training_completed=False,
            new_foils_excluded_from_calibration=spec['study']['protocol'] in ('new_foils','heldout_matched_duration'),
            independently_heldout_positive_class=False, scientific_verdict=None)
        if spec['study']['protocol'] == 'heldout_matched_duration':
            terminal.update(source_training_completed=None,
                protocol_sha256=design['protocol_sha256'], independence_scope=design['independence_scope'])
        _write(output/'terminal.json', terminal)
    except BaseException as error:
        _write(output/'exception.json', dict(reason=str(error), traceback=traceback.format_exc(), scientific_verdict=None))
        raise


def main():
    parser = argparse.ArgumentParser(); mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare'); mode.add_argument('--controls'); args = parser.parse_args()
    if args.prepare: print(json.dumps(prepare(json.loads(Path(args.prepare).read_bytes())), allow_nan=False))
    else: run(args.controls)


if __name__ == '__main__': main()
