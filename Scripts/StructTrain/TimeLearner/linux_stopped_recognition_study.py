"""Evaluate an actually audited stopped M=4 model through existing workers.

Preparation and full evidence audits get separate 16 GiB processes. Native
evaluation uses a small owned controller and its separately bounded 16 GiB
child. Their maxima never have to be reserved concurrently with preparation.
The original Train, its primary audit and their outcomes remain unchanged.
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

from .native_evidence import load, require
from .runtime import file_record


SOURCE = Path(__file__).resolve().parents[3]
MODULE = 'Scripts.StructTrain.TimeLearner.linux_stopped_recognition_study'
BASES = (Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor'))
GIB = 1024**3


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False);stream.write('\n')


def context(request_path):
    request_path = Path(request_path).resolve(strict=True);spec = load(request_path)
    require(type(spec) is dict and set(spec) == {'kind','schema_version','job_id','worker_host',
        'execution_root','tool_commit','source_request','source_train','source_audit_job','template_envelope'}
        and spec['kind'] == 'timelearner_linux_stopped_recognition_study' and
        type(spec['schema_version']) is int and spec['schema_version'] == 1 and sys.platform == 'linux',
        'stopped_study_request_schema')
    base = Path(spec['execution_root']);name = spec['job_id']
    require(base in BASES and base.resolve(strict=True) == base and SOURCE.is_relative_to(base) and
        socket.gethostname() == spec['worker_host'] and type(name) is str and name and len(name) <= 90 and
        all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name), 'stopped_study_worker_scope')
    controls = base/'requests'/name;output = base/'readbacks'/name
    require(request_path == controls/'request.json' and controls.resolve(strict=True) == controls,
        'stopped_study_controls_path')
    paths = {}
    for key in ('source_request','template_envelope'):
        record = spec[key];p = Path(record['path'])
        require(p.is_relative_to(base) and p.resolve(strict=True) == p and not p.is_symlink() and
            file_record(p) == record, 'stopped_study_bound_input_changed:'+key)
        paths[key] = p
    for key in ('source_train','source_audit_job'):
        p = Path(spec[key]);require(p.is_relative_to(base/'readbacks') and
            p.resolve(strict=False) == p and not p.is_symlink(), 'stopped_study_source_path')
        paths[key] = p
    original = load(paths['source_request']);runtime_path = Path(original['runtime']['path'])
    require(original['operation'] == 'train' and original['execution_root'] == str(base) and
        runtime_path.is_relative_to(base) and file_record(runtime_path) == original['runtime'],
        'stopped_study_original_count_training_binding')
    sdk = Path(original['sdk_source']);runtime = load(runtime_path)
    from .runtime import source_closure
    require(sdk.is_relative_to(base) and source_closure(sdk) == runtime['source_closure'],
        'stopped_study_original_runtime_changed')
    baseline = controls/'baseline';threshold = controls/'threshold'
    return dict(spec=spec,request=request_path,request_record=file_record(request_path),base=base,
        controls=controls,output=output,paths=paths,runtime=runtime,runtime_path=runtime_path,
        runtime_record=original['runtime'],sdk=sdk,baseline=baseline,threshold=threshold)


def guard(plan):
    require(file_record(plan['request']) == plan['request_record'], 'stopped_study_request_changed')
    for key in ('source_request','template_envelope'):
        require(file_record(plan['paths'][key]) == plan['spec'][key], 'stopped_study_input_changed:'+key)
    require(file_record(plan['runtime_path']) == plan['runtime_record'], 'stopped_study_runtime_changed')


def phase_paths(plan, phase):
    is_threshold = phase.startswith('threshold')
    control = plan['threshold'] if is_threshold else plan['baseline']
    name = plan['spec']['job_id']+('-threshold' if is_threshold else '-baseline')
    return control, plan['base']/'readbacks'/name, plan['base']/'readbacks'/(name+'-inputs')


def reservation_resources(plan, output, inputs):
    from .resource_reservations import coalesce_resource_requests
    return coalesce_resource_requests([dict(path=str(p),access=access) for p,access in (
        (SOURCE,'read'),(plan['paths']['source_train'],'read'),(plan['paths']['source_audit_job'],'read'),
        (plan['paths']['source_request'].parent,'read'),(plan['sdk'],'read'),
        (plan['paths']['template_envelope'].parent,'read'),(plan['controls'],'write'),
        (plan['output'],'write'),(output,'write'),(inputs,'write'))])


def worker(request_path, phase):
    plan = context(request_path);spec = plan['spec'];directory = plan['output']/phase
    from .contained_process import inspect
    from .resource_reservations import Reservations
    from .owned_python_job import _source_snapshot
    owner = inspect(directory/'process/contained');binding = owner['binding']
    ticks = Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19]
    require(not owner['all_processes_closed'] and binding['initial_main_pid'] == os.getpid() and
        binding['initial_start_ticks'] == ticks and
        Path('/proc/self/cgroup').read_text().strip() == '0::'+binding['control_group'],
        'stopped_study_worker_not_owned_main')
    _source_snapshot(SOURCE, spec['tool_commit']);guard(plan)
    control, output, inputs = phase_paths(plan, phase)
    if phase.endswith('native'):
        # This maintained executor owns the slot/17 GiB reservation itself.
        # Its native child is declared to the outer supervisor below.
        sys.argv = [str(control/'worker.py'),'--controls',str(control)]
        # Keep the checked copied producer as __file__, as its own code expects.
        import runpy
        runpy.run_path(str(control/'worker.py'),run_name='__main__')
    else:
        registry = Reservations.open_existing(plan['base']/'resource-reservations.sqlite3')
        lease = registry.reserve(spec['job_id']+'-'+phase,
            reservation_resources(plan,output,inputs),
            ttl_seconds=7800,demands=dict(slots=1,memory_bytes=16*GIB,disk_bytes=8*GIB))
        write(directory/'reservation.json',lease)
        # No early lease release: the shared supervisor closes the exact owner
        # and every declared native child, then performs normal recovery.
        if phase == 'baseline-prepare':
            from .prepare_stopped_baseline import prepare
            control.mkdir()
            proof = plan['paths']['source_audit_job']/'worker/tmp/matched-count-training-audit.json'
            audit_path = control/'source-audit.json'
            write(audit_path,load(proof)['full_primary_audit']['training_audit'])
            declaration = dict(kind='timelearner_stopped_baseline_preparation',schema_version=1,
                source_native=str(plan['paths']['source_train']/'train/native'),source_proof=str(proof),
                source_audit=str(audit_path),template_envelope=str(plan['paths']['template_envelope']),
                native_runtime=str(plan['runtime_path']),sdk_source=str(plan['sdk']),destination=str(control),
                inputs=str(inputs),output=str(output),run_id=spec['job_id']+'/baseline',python_source=str(SOURCE))
            write(control/'declaration.json',declaration);prepare(declaration)
        elif phase == 'threshold-prepare':
            from .prepared_threshold import prepare
            control.mkdir();prepare(plan['baseline'],control,inputs,output,spec['job_id']+'/threshold')
        elif phase.endswith('audit'):
            from .audit_prepared_diagnostic import audit
            write(control/'independent-audit.json',audit(control))
        else:
            raise ValueError('unknown_stopped_study_phase')
        if phase.endswith('prepare'):
            prepared = load(control/'specification.json')
            write(control/'original-prepared-specification.json',prepared)
            # Operational storage ceiling only; source/job/model/math unchanged.
            # The older 24 GiB default exceeds Elder's 14 GiB quantity pool.
            prepared['disk'] = dict(minimum_free_bytes=8*GIB,maximum_output_bytes=8*GIB)
            (control/'specification.json').write_text(json.dumps(prepared,indent=2,allow_nan=False)+'\n',
                encoding='utf-8',newline='\n')
    guard(plan);_source_snapshot(SOURCE,spec['tool_commit'])
    write(directory/'worker-terminal.json',dict(phase=phase,completed=True,original_Train_unchanged=True,
        training_convergence_inferred=False,scientific_verdict=None))
    return 0


def supervise(request_path):
    from .owned_native_job import _identity, _run_owned
    from .owned_python_job import _source_snapshot
    from .resource_reservations import Reservations
    from .runtime import resolved_libraries, runtime_content_identity, digest_json
    plan = context(request_path);spec = plan['spec'];root = plan['output']
    _source_snapshot(SOURCE,spec['tool_commit']);write(root/'supervisor-identity.json',_identity(os.getpid()))
    registry = Reservations.open_existing(plan['base']/'resource-reservations.sqlite3')
    try:
        started = time.monotonic();audit_job = plan['paths']['source_audit_job']
        while True:
            guard(plan);require(time.monotonic()-started < 21600, 'stopped_study_audit_wait_budget')
            require(not (root/'cancel.request').exists(), 'stopped_study_wait_cancelled')
            done = audit_job/'controller-result.json';closure = audit_job/'closure-and-reservation.json'
            if done.exists() and closure.exists():
                result,closed = load(done),load(closure)
                require(result['execution'] == 'completed' and result['all_processes_closed'] and
                    closed['closure']['all_processes_closed'] and
                    load(audit_job/'worker/terminal.json')['operation_passed'] is True,
                    'stopped_study_original_primary_audit_failed')
                validation = load(audit_job/'worker/validation/result.json')
                require(validation['assertion_status'] == 'passed' and validation['executed_tests'] == 1 and
                    not validation['failures'] and not validation['errors'] and not validation['skipped'],
                    'stopped_study_original_primary_audit_not_complete')
                if registry.inspect()['reserved']['slots'] == 0:break
            time.sleep(15)
        proof = load(audit_job/'worker/tmp/matched-count-training-audit.json')
        require(proof['full_primary_audit']['training_outcome'] == 'budget_exhausted' and
            proof['full_primary_audit']['completed_boundary'] is False,
            'stopped_study_requires_other_protocol_for_completed_or_different_Train')
        write(root/'original-primary-audit.json',dict(proof=file_record(audit_job/'worker/tmp/matched-count-training-audit.json'),
            validation=file_record(audit_job/'worker/validation/result.json'),original_outcome_unchanged=True))
        for phase in ('baseline-prepare','baseline-native','baseline-audit',
                      'threshold-prepare','threshold-native','threshold-audit'):
            control, output, inputs = phase_paths(plan, phase)
            require(registry.inspect()['reserved']['slots'] == 0 and shutil.disk_usage(root).free >= 16*GIB,
                'stopped_study_phase_resources_unavailable')
            available = int(next(row.split()[1] for row in Path('/proc/meminfo').read_text().splitlines()
                if row.startswith('MemAvailable:')))*1024
            require(available >= (17 if phase.endswith('native') else 16)*GIB+256*1024**2,
                'stopped_study_actual_memory_unavailable')
            directory = root/phase;directory.mkdir()
            native = phase.endswith('native')
            runtime = dict(schema_version=2,source_closure=dict(kind='stopped_recognition_controller',
                tool_root=spec['tool_commit'],request_sha256=plan['request_record']['sha256']),
                executable=file_record(Path(sys.executable)),app_ini=plan['request_record'],
                compiler=file_record(Path(sys.executable)),resolved_libraries=resolved_libraries(Path(sys.executable)),
                loaded_process_files=None,loader_environment={},build_flags=dict(role=phase))
            runtime['runtime_identity']=runtime_content_identity(runtime)
            runtime['runtime_fingerprint']=digest_json(runtime['runtime_identity']);write(directory/'runtime.json',runtime)
            result = _run_owned(runtime,['-B','-m',MODULE,'_worker',str(plan['request']),phase],SOURCE,
                directory,output,[output/'process/contained'] if native else [],registry,
                output.name if native else spec['job_id']+'-'+phase,
                dict(memory_bytes=(1 if native else 16)*GIB,tasks=128,maximum_wall_seconds=9000 if native else 7200),
                dict(minimum_free_bytes=8*GIB,maximum_increment_bytes=8*GIB),
                [directory,output,inputs,control],control_guard=lambda:guard(plan))
            require(result == 0 and load(directory/'worker-terminal.json')['completed'], 'stopped_study_phase_failed:'+phase)
        baseline = load(plan['baseline']/'independent-audit.json');threshold = load(plan['threshold']/'independent-audit.json')
        write(root/'terminal.json',dict(execution='completed',validity='valid',
            baseline_counts=baseline['native_evidence']['metrics']['pooled_counts'],
            actual_threshold_counts=threshold['native_evidence']['metrics']['pooled_counts'],
            threshold=load(plan['threshold']/'proposal.json')['threshold'],
            report_family_response_requirement_met=threshold['report_family_response_requirement_met'],
            complete_source_history_audited=True,original_Train_outcome='budget_exhausted',
            training_completed=False,independently_heldout_evaluation=False,scientific_verdict=None))
        return 0
    except BaseException as error:
        write(root/'exception.json',dict(reason=str(error),traceback=traceback.format_exc(),
            original_Train_not_restarted=True,scientific_verdict=None));raise


def launch(request_path):
    from .owned_python_job import _source_snapshot
    from .owned_native_job import _identity
    plan=context(request_path);_source_snapshot(SOURCE,plan['spec']['tool_commit'])
    require(not plan['output'].exists(), 'stopped_study_fresh_attempt_required');plan['output'].mkdir()
    environment=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_NO_LAZY_FETCH='1')
    for key in ('PYTHONPATH','PYTHONHOME','LD_LIBRARY_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM'):environment.pop(key,None)
    with (plan['output']/'supervisor.log').open('xb') as log:
        process=subprocess.Popen([sys.executable,'-B','-m',MODULE,'_supervise',str(plan['request'])],cwd=SOURCE,
            env=environment,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    identity=_identity(process.pid);write(plan['output']/'dispatched.json',identity)
    return dict(queued=True,job=plan['spec']['job_id'],supervisor=identity,output=str(plan['output']),
        source_primary_audit_must_complete=True,scientific_verdict=None)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('launch','_supervise','_worker'));parser.add_argument('request',type=Path)
    parser.add_argument('phase',nargs='?',choices=('baseline-prepare','baseline-native','baseline-audit',
        'threshold-prepare','threshold-native','threshold-audit'))
    args=parser.parse_args(argv)
    if args.action=='launch':print(json.dumps(launch(args.request)));return 0
    return supervise(args.request) if args.action=='_supervise' else worker(args.request,args.phase)


if __name__=='__main__':raise SystemExit(main())
