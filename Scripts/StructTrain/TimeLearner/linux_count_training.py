"""Matched count-normalization cold Train using the owned Linux native backend.

The request pins the original resistance-normalization declaration and its
measured cold graph. Both native preflights must pass before Train starts.
Native closure is followed by a separate full primary-history audit; neither
the controller nor an exit-zero result certifies convergence or recognition.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import traceback

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import load, number, require
from .prepared_count_training import matched_count_job, factor_control_job
from .runtime import file_record


SOURCE = Path(__file__).resolve().parents[3]
BASES = (Path('/media/user/Data/TimeLearnerRefactor'), Path('/home/user/timelearner-refactor'))
MODULE = 'Scripts.StructTrain.TimeLearner.linux_count_training'


def _write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def _file(record, root):
    require(type(record) is dict and set(record) == {'path','size','sha256'}, 'count_linux_file_record')
    path = Path(record['path'])
    require(path.is_absolute() and path.is_relative_to(root) and not path.is_symlink() and
            path.resolve(strict=True) == path and file_record(path) == record, 'count_linux_input_changed')
    return path


def context(request_path):
    from .owned_python_job import _source_snapshot
    from .runtime import source_closure
    from .process_runner import verify_runtime
    request_path = Path(request_path).resolve(strict=True);spec = load(request_path)
    require(type(spec) is dict and set(spec) == {'kind','schema_version','job_id','worker_host',
            'execution_root','tool_commit','sdk_source','original_job','original_initial_state',
            'runtime','run_id','maximum_synapses','operation','limits','disk'} and
            spec['kind'] == 'timelearner_linux_matched_count_training' and
            type(spec['schema_version']) is int and spec['schema_version'] == 1 and
            sys.platform == 'linux', 'count_linux_request_schema')
    base = Path(spec['execution_root'])
    require(base in BASES and base.resolve(strict=True) == base and SOURCE.is_relative_to(base) and
            socket.gethostname() == spec['worker_host'], 'count_linux_worker_scope')
    name = spec['job_id']
    require(type(name) is str and 1 <= len(name) <= 100 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name), 'count_linux_job_id')
    controls = base/'requests'/name
    require(request_path == controls/'request.json' and controls.resolve(strict=True) == controls and
            spec['operation'] in ('preflight','train'), 'count_linux_request_path_or_operation')
    _source_snapshot(SOURCE, spec['tool_commit'])
    original_path = _file(spec['original_job'], controls)
    initial_path = _file(spec['original_initial_state'], controls)
    runtime_path = _file(spec['runtime'], controls)
    original, initial, runtime = load(original_path), load(initial_path), load(runtime_path)
    require(original['sha256'] == sha({k:v for k,v in original.items() if k != 'sha256'}) and
            initial['sha256'] == sha({k:v for k,v in initial.items() if k != 'sha256'}) and
            initial['configuration_sha256'] == sha(original['configuration']) and
            initial['training_started'] is False and initial['dynamics_checkpoint'] is False and
            initial['identity']['valid'] is True and
            initial['identity']['sha256'] == sha(initial['identity']['model']), 'count_linux_original_cold_binding')
    job = matched_count_job(original, spec['run_id'], maximum_synapses=spec['maximum_synapses'])
    factor = factor_control_job(job)
    from .native_pipeline_worker import validate_job
    validate_job('train', job);validate_job('preflight', factor)
    sdk = Path(spec['sdk_source'])
    require(sdk.is_absolute() and sdk.is_relative_to(base) and sdk.resolve(strict=True) == sdk and
            source_closure(sdk) == runtime['source_closure'], 'count_linux_sdk_changed')
    verify_runtime(runtime)
    limits = spec['limits']
    require(type(limits) is dict and set(limits) == {'controller_memory_bytes','native_memory_bytes',
            'preflight_memory_bytes','controller_tasks','native_tasks','native_wall_seconds',
            'preflight_wall_seconds','whole_wall_seconds'} and
            all(type(v) is int and v > 0 for v in limits.values()), 'count_linux_limits')
    from .contained_process import validate_limits
    validate_limits(limits['controller_memory_bytes'], limits['controller_tasks'], limits['whole_wall_seconds'])
    validate_limits(limits['native_memory_bytes'], limits['native_tasks'], limits['native_wall_seconds'])
    validate_limits(limits['preflight_memory_bytes'], limits['native_tasks'], limits['preflight_wall_seconds'])
    declared_wall = number(original['configuration']['maximum_wall_seconds'])
    required_native_wall=limits['native_wall_seconds'] if spec['operation']=='train' else 0
    require(limits['native_wall_seconds'] >= declared_wall+600 and
            limits['whole_wall_seconds'] >= required_native_wall+2*limits['preflight_wall_seconds']+60 and
            limits['preflight_memory_bytes'] <= limits['native_memory_bytes'], 'count_linux_budget_envelope')
    disk = spec['disk']
    require(type(disk) is dict and set(disk) == {'minimum_free_bytes','maximum_output_bytes'} and
            all(type(v) is int and v > 0 for v in disk.values()) and
            shutil.disk_usage(base).free >= disk['minimum_free_bytes']+disk['maximum_output_bytes'],
            'count_linux_capacity_preflight')
    return dict(spec=spec, request_path=request_path, request_sha256=file_record(request_path)['sha256'],
        base=base, controls=controls, directory=base/'readbacks'/(name+'-controller'),
        output=base/'readbacks'/name, runtime_path=runtime_path, runtime=runtime, sdk=sdk,
        original=original, initial=initial, job=job, factor=factor)


def _guard(plan):
    # This monitor runs during native execution. Rehash only the small frozen
    # inputs here; do not walk Git trees or hash the SDK on every heartbeat.
    require(file_record(plan['request_path'])['sha256'] == plan['request_sha256'],
            'count_linux_consumed_controls_changed')
    for name in ('original_job','original_initial_state','runtime'):
        _file(plan['spec'][name],plan['controls'])


def _verify_sources_after(plan):
    from .owned_python_job import _source_snapshot
    from .runtime import source_closure
    _guard(plan);_source_snapshot(SOURCE,plan['spec']['tool_commit'])
    require(source_closure(plan['sdk']) == plan['runtime']['source_closure'], 'count_linux_sdk_changed_after_execution')


def _reservation_resources(plan):
    # The tool source may be the very SDK tree being used. Reserve that read
    # once; the registry deliberately rejects repeated canonical paths.
    from .resource_reservations import coalesce_resource_requests, ReservationError
    resources = [dict(path=str(path),access=access) for path,access in (
        (SOURCE, 'read'), (plan['sdk'], 'read'),
        (Path(plan['runtime']['executable']['path']).parent, 'read'),
        (plan['controls'], 'read'), (plan['output'], 'write'),
        (plan['directory'], 'write'))]
    try:
        return coalesce_resource_requests(resources)
    except ReservationError as error:
        if str(error)=='reservation_resource_access_collision':
            require(False,'count_linux_resource_access_collision')
        raise


def launch(request_path):
    plan = context(request_path);directory=plan['directory'];spec=plan['spec']
    require(not directory.exists() and not plan['output'].exists(), 'count_linux_fresh_attempt_required')
    from .resource_reservations import Reservations
    registry=Reservations.open_existing(plan['base']/'resource-reservations.sqlite3')
    require(registry.inspect()['reserved']['slots'] == 0, 'count_linux_worker_busy')
    directory.mkdir()
    _write(directory/'launch-context.json',dict(request_sha256=plan['request_sha256'],tool_commit=spec['tool_commit'],
        original_model_revision=plan['initial']['identity']['sha256'],job_sha256=plan['job']['sha256'],
        factor_job_sha256=plan['factor']['sha256'],operation=spec['operation'],scientific_verdict=None))
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for key in ('PYTHONPATH','PYTHONHOME','LD_LIBRARY_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM'):
        env.pop(key,None)
    with (directory/'supervisor.log').open('xb') as log:
        process=subprocess.Popen([sys.executable,'-B','-m',MODULE,'_supervise',str(request_path)],cwd=SOURCE,
            env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    from .owned_native_job import _identity
    _write(directory/'supervisor-identity.json',_identity(process.pid))
    return dict(dispatched=True,job=spec['job_id'],supervisor_pid=process.pid,
        controller=str(directory),output=str(plan['output']),original_model_revision=plan['initial']['identity']['sha256'],
        job_sha256=plan['job']['sha256'],scientific_verdict=None)


def _supervise(request_path):
    from .owned_native_job import _run_owned
    from .resource_reservations import Reservations
    from .runtime import resolved_libraries,runtime_content_identity,digest_json
    plan=context(request_path);spec=plan['spec'];directory=plan['directory'];limits=spec['limits']
    launch_record=load(directory/'launch-context.json')
    require(launch_record['request_sha256']==plan['request_sha256'], 'count_linux_launch_context_changed')
    runtime=dict(schema_version=2,source_closure=dict(kind='matched_count_linux_controller',
        tool_root=spec['tool_commit'],request_sha256=plan['request_sha256']),
        executable=file_record(Path(sys.executable)),app_ini=file_record(plan['request_path']),
        compiler=file_record(Path(sys.executable)),resolved_libraries=resolved_libraries(Path(sys.executable)),
        loaded_process_files=None,loader_environment={},build_flags=dict(role='Matched cold count Train controller'))
    runtime['runtime_identity']=runtime_content_identity(runtime);runtime['runtime_fingerprint']=digest_json(runtime['runtime_identity'])
    _write(directory/'controller-runtime.json',runtime)
    phases=['preflight','factor-preflight']+(['train'] if spec['operation']=='train' else [])
    expected=[plan['output']/name/'process/contained' for name in phases]
    # Reuse the maintained exact-owner supervisor. Its finite child set also
    # permits cleanup/recovery after the Python controller is killed.
    return _run_owned(runtime,['-B','-m',MODULE,'_worker',str(plan['request_path'])],SOURCE,directory,
        plan['output'],expected,Reservations.open_existing(plan['base']/'resource-reservations.sqlite3'),
        spec['job_id'],dict(memory_bytes=limits['controller_memory_bytes'],tasks=limits['controller_tasks'],
                           maximum_wall_seconds=limits['whole_wall_seconds']),
        dict(minimum_free_bytes=spec['disk']['minimum_free_bytes'],maximum_increment_bytes=spec['disk']['maximum_output_bytes']),
        [directory,plan['output']],control_guard=lambda:_guard(plan))


def _worker(request_path):
    from .resource_reservations import Reservations
    from .native_cli import inspect_native_cli
    from .native_pipeline_worker import run_job
    from .contained_runner import execute
    from .runtime import applied_loader_environment
    plan=context(request_path);spec=plan['spec'];output=plan['output'];limits=spec['limits']
    from .contained_process import inspect
    owner=inspect(plan['directory']/'process/contained');binding=owner['binding']
    ticks=Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19]
    require(not owner['all_processes_closed'] and binding['initial_main_pid']==os.getpid() and
            binding['initial_start_ticks']==ticks and
            Path('/proc/self/cgroup').read_text().strip()=='0::'+binding['control_group'],
            'count_linux_worker_not_bound_main')
    output.mkdir();registry=Reservations.open_existing(plan['base']/'resource-reservations.sqlite3')
    maximum_memory=limits['controller_memory_bytes']+(limits['native_memory_bytes']
        if spec['operation']=='train' else limits['preflight_memory_bytes'])
    resources = _reservation_resources(plan)
    demands=dict(slots=1,memory_bytes=maximum_memory,disk_bytes=spec['disk']['maximum_output_bytes'])
    require(not registry.managed_units, 'count_linux_quantity_registry_required')
    lease=registry.reserve(spec['job_id'],resources,ttl_seconds=120,demands=demands)
    _write(output/'reservation.json',lease);last=[0.];derived={}
    def monitor(state=None):
        if time.monotonic()-last[0] >= 10:
            for name,record in derived.items():
                require(file_record(output/name)==record,'count_linux_derived_job_changed')
            registry.heartbeat(lease['token'],ttl_seconds=120);registry.validate_paths(lease['token']);last[0]=time.monotonic()
    try:
        _write(output/'job.json',plan['job']);_write(output/'factor-job.json',plan['factor'])
        derived={name:file_record(output/name) for name in ('job.json','factor-job.json')}
        with applied_loader_environment(plan['runtime']):
            _write(output/'cli.json',inspect_native_cli(plan['runtime'],['preflight','train']))
            for phase,job_path in [('preflight',output/'job.json'),('factor-preflight',output/'factor-job.json')]:
                require(all(file_record(output/name)==record for name,record in derived.items()),'count_linux_derived_job_changed')
                monitor();policy=dict(kind='timelearner_native_process_policy',schema_version=1,
                    backend='bound_cgroup',memory_bytes=limits['preflight_memory_bytes'],tasks=limits['native_tasks'],cooperative_capture=True)
                run=run_job('preflight',job_path,None,plan['runtime_path'],output/phase,
                            limits['preflight_wall_seconds'],process_policy=policy)
                require(run['execution']=='completed' and run['validity']=='valid', 'count_linux_preflight_incomplete')
                current=load(output/phase/'native/initial-state.json')
                if phase=='preflight':
                    require(current['identity']==plan['initial']['identity'] and
                            current['parameters']==plan['initial']['parameters'], 'count_linux_initial_graph_differs_from_resistance_control')
                    baseline=current
                else:
                    require(current['parameters'][0]['synapses']==2 and
                            len(current['identity']['model']['nodes'])>len(baseline['identity']['model']['nodes']),
                            'count_linux_factor_did_not_change_effective_graph')
                    _write(output/'preflight-accepted.json',dict(initial_model_revision=baseline['identity']['sha256'],
                        same_actual_cold_graph_as_resistance_control=True,job_sha256=plan['job']['sha256'],
                        factor_model_revision=current['identity']['sha256'],factor_synapses=2,
                        initial_nodes=len(baseline['identity']['model']['nodes']),
                        factor_nodes=len(current['identity']['model']['nodes']),training_started=False,scientific_verdict=None))
            if spec['operation']=='preflight':
                _verify_sources_after(plan)
                _write(output/'terminal.json',dict(execution='completed',validity='valid',preflight_only=True,
                    training_started=False,training_certificate_verified=False,scientific_verdict=None));return 0
            monitor();destination=output/'train';destination.mkdir()
            require(all(file_record(output/name)==record for name,record in derived.items()),'count_linux_derived_job_changed')
            result=execute(plan['runtime'],['--app-ini',plan['runtime']['app_ini']['path'],'--timelearner-train',
                str(output/'job.json'),'--timelearner-output',str(destination/'native')],
                Path(plan['runtime']['executable']['path']).parent,destination/'process',limits['native_wall_seconds'],
                memory_bytes=limits['native_memory_bytes'],tasks=limits['native_tasks'],cooperative_capture=True,monitor=monitor)
            require(result['all_processes_closed'] and result['runtime_provenance']=='loaded_files_captured',
                    'count_linux_native_train_closure_or_runtime_unverified')
            execution=load(destination/'native/execution.json')
            require(execution['sha256']==sha({k:v for k,v in execution.items() if k!='sha256'}) and
                    execution['job_sha256']==plan['job']['sha256'], 'count_linux_native_execution_binding')
            _verify_sources_after(plan)
            _write(output/'terminal.json',dict(execution=result['execution'],validity='pending_full_primary_audit',
                job_sha256=plan['job']['sha256'],native_execution_sha256=execution['sha256'],
                training_outcome=execution.get('training_outcome'),completed_boundary=execution.get('completed_boundary'),
                package_path=execution.get('package_path'),full_primary_audit_complete=False,
                training_certificate_verified=False,evaluation_verdict=None,scientific_verdict=None))
            return 0 if result['execution']=='completed' else 2
    except BaseException as error:
        _write(output/'exception.json',dict(reason=str(error),traceback=traceback.format_exc(),scientific_verdict=None));raise
    # Lease recovery belongs to the exact-owner supervisor, after closure of
    # this controller AND every declared native child. No early release here.


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','launch','_supervise','_worker'))
    parser.add_argument('request',type=Path);args=parser.parse_args(argv)
    if args.action=='prepare':
        plan=context(args.request);print(json.dumps(dict(job_sha256=plan['job']['sha256'],
            original_model_revision=plan['initial']['identity']['sha256'],native_preflight_verified=False,scientific_verdict=None)));return 0
    if args.action=='launch':print(json.dumps(launch(args.request)));return 0
    return _supervise(args.request) if args.action=='_supervise' else _worker(args.request)


if __name__=='__main__':
    raise SystemExit(main())
