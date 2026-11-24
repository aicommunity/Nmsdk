"""Initial frozen DATA evaluation on the owned Windows native backend.

This is a new observation, not a replay claim. Replay adapters still require
their original complete observations and primary audit. A physical DATA file
does not transfer a Train certificate or establish threshold calibration.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import time

from .native_evidence import require
from .runtime import file_record, source_closure


BASE = Path('C:/Projects/TimeLearnerWorker')


def _write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def _inventory(directory):
    result = {}
    for path in directory.iterdir():
        require(path.is_file() and not path.is_symlink() and
                not getattr(path, 'is_junction', lambda: False)(), 'physical_evaluation_input_alias')
        record = file_record(path)
        result[path.name] = dict(bytes=record['size'], sha256=record['sha256'])
    return result


def prepare(plan_path):
    from .job_source_transport import make_envelope
    from .model_identity import canonical_model_sha256 as sha
    from .native_pipeline_worker import validate_job
    from .physical_model_data_evidence import audit_physical_model_data
    from .process_runner import verify_runtime

    plan_path = Path(plan_path).resolve(strict=True)
    before = file_record(plan_path)
    plan = json.loads(plan_path.read_bytes())
    require(os.name == 'nt' and set(plan) == {'kind', 'schema_version', 'job_id', 'source_data',
            'runtime_manifest', 'sdk_source', 'worker_origin', 'job'} and
            plan['kind'] == 'timelearner_prepared_physical_evaluation_plan' and
            type(plan['schema_version']) is int and plan['schema_version'] == 1,
            'physical_evaluation_preparation_scope')
    name = plan['job_id']
    require(type(name) is str and 1 <= len(name) <= 100 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name), 'physical_evaluation_job_id')
    require(BASE.resolve(strict=True) == BASE, 'physical_evaluation_base_alias')
    controls, inputs, output = BASE/'controls'/name, BASE/'jobs'/(name+'-inputs'), BASE/'jobs'/name
    require(all(p.parent.resolve(strict=True) == p.parent and not p.exists() and not p.is_symlink()
                for p in (controls, inputs, output)), 'physical_evaluation_fresh_paths_required')
    source_path = Path(plan['source_data']['path']).resolve(strict=True)
    runtime_path = Path(plan['runtime_manifest']['path']).resolve(strict=True)
    require(source_path.is_relative_to(BASE/'jobs') and
            file_record(source_path) == plan['source_data'] and
            file_record(runtime_path) == plan['runtime_manifest'], 'physical_evaluation_source_changed')
    model = json.loads(source_path.read_bytes())
    audited = audit_physical_model_data(model, frozen=True)
    job = dict(plan['job'])
    require('source_model_data' not in job and 'sha256' not in job,
            'physical_evaluation_job_must_reference_retained_DATA')
    job.update(source_model_data=model)
    job['sha256'] = sha(job)
    validate_job('physical-model-evaluate', job, (model,))
    require(len(job['trials']) == 8 and len({t['sample_id'] for t in job['trials']}) == 8 and
            sum(t['label'] == 'target' for t in job['trials']) == 1,
            'physical_evaluation_eight_pattern_scope')
    runtime = json.loads(runtime_path.read_bytes())
    sdk = Path(plan['sdk_source']).resolve(strict=True)
    require(source_closure(sdk) == runtime['source_closure'], 'physical_evaluation_sdk_changed')
    verify_runtime(runtime)
    controls.mkdir(); inputs.mkdir()
    carrier = inputs/'model.json'
    shutil.copyfile(source_path, carrier)
    require(file_record(carrier)['sha256'] == plan['source_data']['sha256'], 'physical_evaluation_copy_changed')
    _write(inputs/'native-job-source.json', make_envelope(job, carrier, inputs))
    (controls/'worker.py').write_bytes(Path(__file__).read_bytes())
    _write(controls/'runtime.json', runtime)
    _write(controls/'specification.json', dict(kind='timelearner_prepared_physical_evaluation',
        schema_version=1, job_id=name, sdk_source=str(sdk), worker_origin=plan['worker_origin'],
        worker_sha256=file_record(controls/'worker.py')['sha256'], source_data=plan['source_data'],
        source_runtime=plan['runtime_manifest'], preparation_plan=before, inputs=str(inputs), output=str(output),
        input_inventory=_inventory(inputs), resolved_job_sha256=job['sha256'],
        model_revision=model['model_revision'], document_sha256=model['sha256'],
        effective_threshold=audited['effective_threshold'], memory_bytes=8*1024**3,
        maximum_wall_seconds=3600, minimum_free_bytes=2*1024**3, maximum_output_bytes=512*1024**2))
    require(file_record(source_path) == plan['source_data'] and file_record(runtime_path) == plan['runtime_manifest']
            and file_record(plan_path) == before, 'physical_evaluation_preparation_inputs_changed')
    _write(controls/'proposal.json', dict(kind='initial_frozen_physical_evaluation_preparation',
        replay_equality_claimed=False, source_model_revision=model['model_revision'],
        training_certificate_transferred=False, calibration_confirmed=False,
        source_training_outcome_unchanged=True, native_execution_started=False, scientific_verdict=None))
    return controls


def run(controls):
    from .job_source_transport import verify_envelope
    from .model_identity import canonical_model_sha256 as sha
    from .native_cli import inspect_native_cli
    from .native_gate import _environment
    from .native_pipeline_worker import validate_job, audit_execution
    from .process_runner import verify_runtime
    from .windows_process import execute

    controls = Path(controls).resolve(strict=True)
    spec = json.loads((controls/'specification.json').read_bytes())
    require(os.name == 'nt' and spec['kind'] == 'timelearner_prepared_physical_evaluation' and
            spec['schema_version'] == 1 and controls == BASE/'controls'/spec['job_id'],
            'physical_evaluation_worker_scope')
    inputs, output = Path(spec['inputs']), Path(spec['output'])
    require(inputs == BASE/'jobs'/(spec['job_id']+'-inputs') and
            output == BASE/'jobs'/spec['job_id'] and inputs.resolve(strict=True) == inputs and
            not output.exists() and not output.is_symlink(), 'physical_evaluation_paths')
    output.mkdir()
    try:
        require(_inventory(inputs) == spec['input_inventory'] and
                file_record(Path(__file__))['sha256'] == spec['worker_sha256'], 'physical_evaluation_input_changed')
        runtime = json.loads((controls/'runtime.json').read_bytes())
        sdk = Path(spec['sdk_source'])
        require(source_closure(sdk) == runtime['source_closure'], 'physical_evaluation_sdk_changed')
        source = Path(spec['source_data']['path'])
        require(file_record(source) == spec['source_data'] and
                file_record(Path(spec['source_runtime']['path'])) == spec['source_runtime'],
                'physical_evaluation_original_source_changed')
        model = json.loads((inputs/'model.json').read_bytes())
        envelope = json.loads((inputs/'native-job-source.json').read_bytes())
        job = dict(envelope['job'], source_model_data=model)
        require(job['sha256'] == spec['resolved_job_sha256'] == sha({k:v for k,v in job.items() if k != 'sha256'}),
                'physical_evaluation_resolved_job_changed')
        verify_envelope(envelope, job, inputs/'model.json', inputs)
        _write(output/'admission.json', validate_job('physical-model-evaluate', job, (model,)))
        require(shutil.disk_usage(BASE).free >= spec['minimum_free_bytes']+spec['maximum_output_bytes'],
                'physical_evaluation_disk_admission')
        _write(output/'cli.json', inspect_native_cli(runtime, ['physical-model-evaluate'],
            require_file_source=True, evidence_output=output))
        last = [0.]
        def monitor(state):
            if time.monotonic()-last[0] < 1:
                return
            last[0] = time.monotonic()
            require(shutil.disk_usage(BASE).free >= spec['minimum_free_bytes'], 'physical_evaluation_disk_floor')
            total = 0
            for path in output.rglob('*'):
                try:
                    require(not path.is_symlink() and not path.is_junction(), 'physical_evaluation_output_alias')
                    if path.is_file():
                        total += path.stat().st_size
                except FileNotFoundError:
                    pass  # The native writer atomically renames temporary files.
            require(total <= spec['maximum_output_bytes'], 'physical_evaluation_output_budget')
        args = ['--app-ini', runtime['app_ini']['path'], '--timelearner-physical-model-evaluate',
                str(inputs/'native-job-source.json'), '--timelearner-output', str(output/'native')]
        with _environment({k:runtime['loader_environment'].get(k)
                           for k in ('PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM')}):
            process = execute(runtime, args, Path(runtime['executable']['path']).parent, output/'process',
                memory_bytes=spec['memory_bytes'], maximum_processes=64,
                maximum_wall_seconds=spec['maximum_wall_seconds'], lock_file=BASE/'locks/worker.lock',
                cooperative_capture=True, monitor=monitor)
        _write(output/'process-result.json', process)
        require(process['execution'] == 'completed' and process['returncode'] == 0 and
                process['all_processes_closed'] and process['runtime_provenance'] == 'loaded_files_captured',
                'physical_evaluation_native_incomplete')
        audited = audit_execution('physical-model-evaluate', output/'native', job, (model,))
        _write(output/'audit.json', audited)
        metrics = audited['metrics']
        require(audited['frozen_model_verified'] and metrics['validity'] == 'valid' and metrics['data_only'] and
                len(metrics['trials']) == 8 and metrics['model_revision'] == spec['model_revision'] and
                metrics['effective_threshold'] == spec['effective_threshold'], 'physical_evaluation_native_audit_invalid')
        require(_inventory(inputs) == spec['input_inventory'] and file_record(source) == spec['source_data'] and
                source_closure(sdk) == runtime['source_closure'], 'physical_evaluation_inputs_changed_after')
        verify_runtime(runtime)
        _write(output/'terminal.json', dict(kind='timelearner_initial_windows_physical_evaluation', schema_version=1,
            execution='completed', validity='valid', native_execution_verified=True, frozen_model_verified=True,
            replay_equality_claimed=False, model_revision=spec['model_revision'],
            source_model_data_sha256=model['sha256'], threshold=metrics['effective_threshold'],
            counts=metrics['pooled_counts'], complete_observations=len(metrics['trials']),
            native_execution=file_record(output/'native/execution.json'),
            source_training_outcome_unchanged=True, training_certificate_transferred=False,
            calibration_confirmed=False, scientific_verdict=None))
    except BaseException as error:
        import traceback
        _write(output/'exception.json', dict(reason=str(error), traceback=traceback.format_exc(), scientific_verdict=None))
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', type=Path)
    group.add_argument('--run', type=Path)
    args = parser.parse_args(argv)
    prepare(args.prepare) if args.prepare else run(args.run)


if __name__ == '__main__':
    main()
