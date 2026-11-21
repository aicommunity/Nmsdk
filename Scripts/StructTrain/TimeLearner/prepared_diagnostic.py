"""Execute an immutable, already prepared eight-pattern diagnostic job.

The complete source and history remain in the checked file-source input. This
worker does not reload their Python object trees. Native decoding/import still
checks the complete resolved job. Preparation and execution outcomes are separate.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time


def inventory(root, file_record):
    root = root.resolve(strict=True)
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise ValueError('prepared_input_alias')
        if path.is_dir():
            continue
        if not path.is_file() or not path.resolve(strict=True).is_relative_to(root):
            raise ValueError('prepared_input_not_regular')
        record = file_record(path)
        result[path.relative_to(root).as_posix()] = dict(bytes=record['size'], sha256=record['sha256'])
    if not result:
        raise ValueError('prepared_input_empty')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', required=True)
    args = parser.parse_args()
    controls = Path(args.controls).resolve(strict=True)
    spec = json.loads((controls/'specification.json').read_bytes())
    if spec.get('kind') != 'timelearner_prepared_diagnostic' or spec.get('schema_version') != 1:
        raise ValueError('prepared_diagnostic_schema')
    sys.path.insert(0, spec['python_source'])
    sys.dont_write_bytecode = True
    from Scripts.StructTrain.TimeLearner.runtime import file_record, source_closure
    from Scripts.StructTrain.TimeLearner.native_evidence import load, require
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
    from Scripts.StructTrain.TimeLearner.native_cli import inspect_native_cli

    output = Path(spec['output']).resolve()
    require(not output.exists(), 'prepared_diagnostic_fresh_output_required')
    output.mkdir()

    def write(name, value):
        with (output/name).open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')

    registry = lease = None
    try:
        inputs = Path(spec['inputs']).resolve(strict=True)
        require(inventory(inputs, file_record) == spec['input_inventory'], 'prepared_input_changed')
        require(file_record(Path(__file__))['sha256'] == spec['worker_sha256'], 'prepared_worker_changed')
        runtime = load(controls/'runtime.json')
        sdk = Path(spec['sdk_source'])
        require(source_closure(sdk) == runtime['source_closure'], 'prepared_sdk_changed')
        envelope = load(inputs/'native-job-source.json')
        require(envelope['kind'] == 'timelearner_checked_file_source_job' and envelope['schema_version'] == 1 and
                envelope['sha256'] == canonical_model_sha256({k:v for k,v in envelope.items() if k != 'sha256'}),
                'prepared_job_envelope')
        body = envelope['job']
        require(body['kind'] == 'timelearner_native_diagnostic_evaluation_job' and body['schema_version'] in (1,2) and
                body['sha256'] == spec['resolved_job_sha256'] and len(body['trials']) == 8 and
                len({r['trial_id'] for r in body['trials']}) == 8 and
                sum(r['label'] == 'target' for r in body['trials']) == 1 and
                sum(r['label'] == 'foil' for r in body['trials']) == 7 and
                all(r['reset_policy'] == 'reset_per_trial' and r['duration'] == 2 for r in body['trials']),
                'prepared_diagnostic_eight_pattern_scope')
        source = envelope['source']
        require(source['field'] == 'source_stopped' and source['package_sha256'] == spec['source_package_sha256'] and
                source['path'] in spec['input_inventory'] and spec['input_inventory'][source['path']] ==
                dict(bytes=source['bytes'], sha256=source['sha256']), 'prepared_source_binding')
        prior = Path(spec['source_audit']['path'])
        require(file_record(prior)['sha256'] == spec['source_audit']['sha256'], 'prepared_prior_audit_changed')
        audit = load(prior)
        require(audit['package_digest_verified'] is True and audit['model_revision'] == spec['source_model_revision'] and
                audit['training_outcome'] == 'budget_exhausted', 'prepared_source_audit_scope')
        write('cli.json', inspect_native_cli(runtime, ['diagnostic-evaluate'],
              require_file_source=True, evidence_output=output))
        arguments = ['--app-ini', runtime['app_ini']['path'], '--timelearner-diagnostic-evaluate',
            str(inputs/'native-job-source.json'), '--timelearner-output', str(output/'native')]
        if os.name == 'nt':
            from Scripts.StructTrain.TimeLearner.windows_process import execute
            result = execute(runtime, arguments, Path(runtime['executable']['path']).parent, output/'process',
                memory_bytes=spec['memory_bytes'], maximum_processes=64,
                maximum_wall_seconds=spec['maximum_wall_seconds'], lock_file=spec['lock_file'], cooperative_capture=True)
        else:
            from Scripts.StructTrain.TimeLearner.contained_runner import execute
            from Scripts.StructTrain.TimeLearner.contained_process import inspect
            from Scripts.StructTrain.TimeLearner.owned_python_job import _allocated_output_bytes
            from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
            from Scripts.StructTrain.TimeLearner.runtime import applied_loader_environment
            base = Path(spec['execution_root']).resolve(strict=True)
            require(base in (Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor')) and
                    output.is_relative_to(base/'readbacks') and inputs.is_relative_to(base/'readbacks'),
                    'prepared_worker_resource_scope')
            disk = spec['disk']
            require(shutil.disk_usage(base).free >= sum(disk.values()), 'prepared_worker_disk_admission')
            registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
            lease = registry.reserve(spec['job_id'], [dict(path=str(p), access=access) for p,access in
                ((inputs,'read'), (sdk,'read'), (Path(runtime['executable']['path']).parent,'read'),
                 (controls,'read'), (output,'write'))], ttl_seconds=spec['maximum_wall_seconds']+600,
                demands=dict(slots=1, memory_bytes=spec['memory_bytes']+1024**3,
                             disk_bytes=disk['maximum_output_bytes']))
            last = [0.]
            def monitor(state):
                if time.monotonic()-last[0] < 1:
                    return
                last[0] = time.monotonic()
                registry.heartbeat(lease['token'], ttl_seconds=spec['maximum_wall_seconds']+600)
                allocated = _allocated_output_bytes(output)
                free = shutil.disk_usage(base).free
                with (output/'monitor.jsonl').open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(dict(time=time.time(), free_bytes=free,
                        output_allocated_bytes=allocated))+'\n')
                require(allocated <= disk['maximum_output_bytes'], 'prepared_worker_output_budget')
                require(free >= disk['minimum_free_bytes'], 'prepared_worker_disk_floor')
            with applied_loader_environment(runtime):
                result = execute(runtime, arguments, Path(runtime['executable']['path']).parent,
                    output/'process', spec['maximum_wall_seconds'], memory_bytes=spec['memory_bytes'],
                    tasks=128, cooperative_capture=True, monitor=monitor)
        write('process-result.json', result)
        require(inventory(inputs, file_record) == spec['input_inventory'], 'prepared_input_changed_after_execution')
        require(source_closure(sdk) == runtime['source_closure'], 'prepared_sdk_changed_after_execution')
        require(result['execution'] == 'completed' and result['all_processes_closed'] and
                result['runtime_provenance'] == 'loaded_files_captured', 'prepared_native_execution_incomplete')
        write('terminal.json', dict(native_process_completed=True, original_preparation_failure_preserved=True,
            source_bytes_unchanged=True, observations_independently_audited=False,
            training_completed=False, scientific_verdict=None))
    except BaseException as error:
        import traceback
        write('exception.json', dict(reason=str(error), traceback=traceback.format_exc(), scientific_verdict=None))
        raise
    finally:
        if lease is not None:
            child = output/'process/contained'
            if not (child/'request.json').exists() or inspect(child)['all_processes_closed']:
                registry.release(lease['token'], note='Prepared diagnostic native group closed; original outcomes retained')


if __name__ == '__main__':
    main()
