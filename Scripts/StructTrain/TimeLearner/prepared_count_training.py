"""Matched cold count-normalization Train on the owned Windows backend.

The native SDK, initial physics, target, tolerances and search budgets stay
fixed. The permitted normalization variable changes from Rs to integer Ns.
Preflight is audited before Train. A closed Train still requires the separate
full primary-history audit; this worker never equates process exit with Exact.
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import threading

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import load, number, require


def matched_count_job(original, run_id, *, maximum_synapses=128):
    require(type(run_id) is str and bool(run_id) and type(maximum_synapses) is int and
            2 <= maximum_synapses <= 128, 'count_train_case_declaration')
    require(original['sha256'] == sha({k:v for k,v in original.items() if k != 'sha256'}),
            'count_train_original_job_digest')
    job = deepcopy(original)
    c = job['configuration']; model = c['model']; inputs = model['inputs']
    bounds = c['search']['bounds']
    require(model['normalization'] == 'N1' and len(inputs) >= 2 and len(bounds) == len(inputs) and
            all(i['synapses'] == 1 and number(i['resistance']) > 0 for i in inputs) and
            all(b['minimum_synapses'] == b['maximum_synapses'] == 1 for b in bounds),
            'count_train_requires_fixed_single_synapse_resistance_source')
    anchor = bounds[-1]
    require(anchor['minimum_length'] == anchor['maximum_length'] == inputs[-1]['attachment'] and
            anchor['minimum_resistance'] == anchor['maximum_resistance'] == inputs[-1]['resistance'],
            'count_train_source_anchor_is_not_fixed')
    c['run_id'] = run_id; model['normalization'] = 'N0'
    for i,bound in enumerate(bounds[:-1]):
        require(bound['minimum_resistance'] <= inputs[i]['resistance'] <= bound['maximum_resistance'],
                'count_train_initial_resistance_outside_source_bounds')
        bound.update(minimum_synapses=1, maximum_synapses=maximum_synapses,
                     minimum_resistance=inputs[i]['resistance'], maximum_resistance=inputs[i]['resistance'])
    job['sha256'] = sha({k:v for k,v in job.items() if k != 'sha256'})
    return job


def _write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False);f.write('\n')


def factor_control_job(job):
    """An explicitly separate graph-construction control, never a cold Train."""
    control = deepcopy(job)
    control['configuration']['run_id'] += '/positive-control-ns2'
    control['configuration']['model']['inputs'][0]['synapses'] = 2
    control['sha256'] = sha({k:v for k,v in control.items() if k != 'sha256'})
    return control


def run(controls):
    from .native_cli import inspect_native_cli
    from .native_pipeline_worker import audit_execution, validate_job
    from .native_gate import _environment
    from .runtime import file_record, source_closure
    from .windows_process import execute
    controls = Path(controls).resolve(strict=True)
    spec = load(controls/'specification.json')
    require(type(spec) is dict and set(spec) == {'kind','schema_version','python_source','python_root',
            'sdk_source','original_job','job_file','factor_job_file','run_id','maximum_synapses','output',
            'worker_sha256','native_memory_bytes','native_wall_seconds','preflight_wall_seconds',
            'minimum_free_bytes','maximum_output_bytes'} and
            os.name == 'nt' and spec['kind'] == 'timelearner_matched_count_training' and
            spec['schema_version'] == 1, 'count_train_worker_scope')
    base = Path('C:/Projects/TimeLearnerWorker').resolve(strict=True)
    output = Path(spec['output']).absolute()
    require(controls.is_relative_to(base/'controls') and output.is_relative_to(base/'jobs') and
            not output.exists(), 'count_train_fresh_owned_paths')
    output.mkdir()
    stop = threading.Event(); failures = []
    try:
        require(file_record(Path(__file__))['sha256'] == spec['worker_sha256'], 'count_train_worker_changed')
        original_path = Path(spec['original_job']['path'])
        require(file_record(original_path) == spec['original_job'], 'count_train_original_job_changed')
        original = load(original_path); job_path = controls/'job.json'
        require(file_record(job_path) == spec['job_file'], 'count_train_job_file_changed')
        job = load(job_path)
        require(job == matched_count_job(original, spec['run_id'], maximum_synapses=spec['maximum_synapses']),
                'count_train_matched_case_changed')
        validate_job('train', job)
        factor_path = controls/'factor-job.json'
        require(file_record(factor_path) == spec['factor_job_file'] and
                load(factor_path) == factor_control_job(job), 'count_train_factor_control_changed')
        factor = load(factor_path);validate_job('preflight', factor)
        runtime_path = controls/'runtime.json'; runtime = load(runtime_path)
        runtime_before = file_record(runtime_path); sdk = Path(spec['sdk_source'])
        require(source_closure(sdk) == runtime['source_closure'], 'count_train_sdk_changed')
        require(spec['native_memory_bytes'] == 16*1024**3 and spec['native_wall_seconds'] == 39600 and
                spec['preflight_wall_seconds'] == 900 and
                job['configuration']['maximum_wall_seconds'] == original['configuration']['maximum_wall_seconds'] == 32400,
                'count_train_declared_finite_budgets')
        require(type(spec['minimum_free_bytes']) is int and spec['minimum_free_bytes'] >= 10*1024**3 and
                type(spec['maximum_output_bytes']) is int and 0 < spec['maximum_output_bytes'] <= 8*1024**3,
                'count_train_disk_limits')
        require(shutil.disk_usage(output).free >= spec['minimum_free_bytes']+spec['maximum_output_bytes'],
                'count_train_capacity_preflight')
        def check_disk():
            while not stop.is_set():
                try:
                    require(shutil.disk_usage(output).free >= spec['minimum_free_bytes'], 'count_train_disk_floor')
                    total = 0
                    def walk_error(error):
                        if not isinstance(error, FileNotFoundError):raise error
                    for directory, _, files in os.walk(output, onerror=walk_error):
                        for name in files:
                            try:total += (Path(directory)/name).stat().st_size
                            except FileNotFoundError:pass
                    require(total <= spec['maximum_output_bytes'], 'count_train_output_budget')
                except BaseException as error:
                    failures.append(str(error));return
                stop.wait(5)
        thread = threading.Thread(target=check_disk, daemon=True);thread.start()
        def monitor(state):
            # Never walk large output trees on the native capture/ack path.
            require(not failures, failures[0] if failures else 'count_train_disk_guard')
        with _environment({k:runtime['loader_environment'].get(k)
                           for k in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}):
            _write(output/'cli.json', inspect_native_cli(runtime, ['preflight','train'], evidence_output=output))
            for phase,mode,path,case,wall,memory in [
                    ('preflight','preflight',job_path,job,spec['preflight_wall_seconds'],8*1024**3),
                    ('factor-preflight','preflight',factor_path,factor,spec['preflight_wall_seconds'],8*1024**3),
                    ('train','train',job_path,job,spec['native_wall_seconds'],spec['native_memory_bytes'])]:
                require(not failures and file_record(job_path) == spec['job_file'], 'count_train_input_or_guard_changed')
                destination = output/phase;destination.mkdir()
                result = execute(runtime, ['--app-ini',runtime['app_ini']['path'],'--timelearner-'+mode,
                    str(path),'--timelearner-output',str(destination/'native')],
                    Path(runtime['executable']['path']).parent,destination/'process',memory_bytes=memory,
                    maximum_processes=64,maximum_wall_seconds=wall,lock_file=base/'locks/worker.lock',
                    cooperative_capture=True,monitor=monitor)
                _write(destination/'process-result.json',result)
                require(result['execution'] == 'completed' and result['all_processes_closed'] and
                        result['runtime_provenance'] == 'loaded_files_captured', 'count_train_'+mode+'_native_incomplete')
                execution = load(destination/'native/execution.json')
                if mode == 'preflight':
                    audited = audit_execution(mode,destination/'native',case)
                    _write(destination/'audit.json',audited)
                    initial = load(destination/'native/initial-state.json')
                    if phase == 'preflight':
                        baseline_initial = initial
                    else:
                        require(initial['parameters'][0]['synapses'] == 2 and
                                len(initial['identity']['model']['nodes']) >
                                len(baseline_initial['identity']['model']['nodes']),
                                'count_train_factor_did_not_create_additional_physical_nodes')
                        _write(output/'preflight-accepted.json',dict(job_sha256=job['sha256'],
                            normalization='N0',initial_model_revision=baseline_initial['identity']['sha256'],
                            effective_initial_model_checked=True,factor_control_synapses=2,
                            initial_nodes=len(baseline_initial['identity']['model']['nodes']),
                            factor_control_nodes=len(initial['identity']['model']['nodes']),
                            factor_control_is_a_separate_initial_state=True,
                            full_training_audit_pending=True,scientific_verdict=None))
                else:
                    require(execution['sha256'] == sha({k:v for k,v in execution.items() if k != 'sha256'}) and
                            execution['job_sha256'] == job['sha256'], 'count_train_native_execution_binding')
                    # Full model/history parsing belongs to a separate finite
                    # audited process after native closure, not this launcher.
                    terminal = dict(execution='completed',validity='pending_full_primary_audit',
                        job_sha256=job['sha256'],native_execution_sha256=execution['sha256'],
                        training_outcome=execution.get('training_outcome'),
                        completed_boundary=execution.get('completed_boundary'),package_path=execution.get('package_path'),
                        full_primary_audit_complete=False,training_certificate_verified=False,scientific_verdict=None)
        require(file_record(original_path) == spec['original_job'] and file_record(job_path) == spec['job_file'] and
                file_record(factor_path) == spec['factor_job_file'] and not failures and
                file_record(runtime_path) == runtime_before and source_closure(sdk) == runtime['source_closure'],
                'count_train_source_changed_after_execution')
        _write(output/'terminal.json',terminal)
    except BaseException as error:
        import traceback
        _write(output/'exception.json',dict(reason=str(error),traceback=traceback.format_exc(),scientific_verdict=None))
        raise
    finally:
        stop.set()
        if 'thread' in locals():thread.join(10)


def main():
    p=argparse.ArgumentParser();p.add_argument('--controls',required=True)
    run(p.parse_args().controls)


if __name__ == '__main__':main()
