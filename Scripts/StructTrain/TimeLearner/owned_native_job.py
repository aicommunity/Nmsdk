"""Pinned, durable native-acceptance controller; never generates executable code.

The native worker remains the sole reservation owner. A controller only recovers
that exact dead whole-worker lease after every finite canonical child intent is
closed. An incomplete ownership graph stays held, independently of test outcome.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import traceback
import uuid

from .collector_provenance import _canonical, _frozen, _git_blob, _json
from .contained_process import start, inspect, stop, adopt
from .native_evidence import require
from .native_acceptance_worker import validate_job, validate_job_paths
from .owned_python_job import _source_snapshot
from .process_limits import validate_limits
from .resource_reservations import Reservations
from .runtime import source_closure, file_record, resolved_libraries, runtime_content_identity, digest_json

SOURCE = Path(__file__).resolve().parents[3]
_BASES = {Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor')}
_MODULE = 'Scripts.StructTrain.TimeLearner.owned_native_job'
_NATIVE_MODULE = 'Scripts.StructTrain.TimeLearner.native_acceptance_worker'


def _write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n');stream.flush();os.fsync(stream.fileno())


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _identity(pid=None):
    pid = os.getpid() if pid is None else pid
    directory = Path('/proc')/str(pid)
    return {'pid':pid, 'start_ticks':directory.joinpath('stat').read_text().rsplit(') ',1)[1].split()[19],
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(), 'uid':directory.stat().st_uid}


def _validate_identity(identity):
    require(type(identity) is dict and set(identity)=={'pid','start_ticks','boot_id','uid'} and
            type(identity['pid']) is int and identity['pid']>0 and
            type(identity['uid']) is int and identity['uid']>=0 and
            type(identity['start_ticks']) is str and identity['start_ticks'].isdigit() and
            str(int(identity['start_ticks']))==identity['start_ticks'] and
            type(identity['boot_id']) is str and len(identity['boot_id'])==36,
            'owned_native_process_identity_invalid')
    try:
        require(str(uuid.UUID(identity['boot_id']))==identity['boot_id'],'owned_native_process_identity_invalid')
    except (ValueError,AttributeError):
        require(False,'owned_native_process_identity_invalid')
    return identity


def _same_process(identity):
    _validate_identity(identity)
    try:
        return _identity(identity['pid']) == identity
    except (FileNotFoundError, ProcessLookupError):
        return False


def _display(value):
    try:
        print(json.dumps(value, allow_nan=False), flush=True)
    except (BrokenPipeError, OSError):
        pass  # Durable files, not the observing transport, are authoritative.


def _file_record(record):
    require(type(record) is dict and set(record)=={'path','sha256'} and
            type(record['path']) is str and '\0' not in record['path'] and
            type(record['sha256']) is str and len(record['sha256'])==64 and
            all(c in '0123456789abcdef' for c in record['sha256']), 'owned_native_file_binding')
    path = _canonical(Path(record['path']))
    raw, metadata = _frozen(path, 16*1024**2)
    require(_sha(raw)==record['sha256'], 'owned_native_input_changed')
    return _json(raw), raw, metadata


def validate_request(value):
    require(type(value) is dict and set(value)=={'kind','schema_version','job_id','worker_host',
            'execution_root','tool_commit','job','preparation'} and
            value['kind']=='timelearner_owned_native_job' and type(value['schema_version']) is int and
            value['schema_version']==1, 'owned_native_request_schema')
    require(type(value['job_id']) is str and value['job_id'] and
            all(c.isalnum() or c in '-_' for c in value['job_id']), 'owned_native_job_id')
    require(type(value['worker_host']) is str and value['worker_host'] and
            type(value['execution_root']) is str and Path(value['execution_root']) in _BASES,
            'owned_native_explicit_worker')
    require(type(value['tool_commit']) is str and len(value['tool_commit'])==40 and
            all(c in '0123456789abcdef' for c in value['tool_commit']), 'owned_native_tool_commit')
    # Bindings are fully read later, once the base is known; syntax still fails early.
    for key in ('job','preparation'):
        record = value[key]
        require(type(record) is dict and set(record)=={'path','sha256'} and
                type(record['path']) is str and Path(record['path']).is_absolute() and
                type(record['sha256']) is str and len(record['sha256'])==64 and
                all(c in '0123456789abcdef' for c in record['sha256']), 'owned_native_file_binding')
    return value


def _resources(paths, protected):
    return ([{'path':str(paths[k]),'access':'write'} for k in ('build','runtime','output')] +
            [{'path':str(paths[k]),'access':'read'} for k in ('source','resources','framework')] +
            [{'path':str(p),'access':'read'} for p in protected])


def _overlap(a, b):
    return a==b or a.is_relative_to(b) or b.is_relative_to(a)


def _backend():
    require(sys.platform=='linux' and Path('/sys/fs/cgroup/cgroup.controllers').is_file(),
            'owned_native_linux_cgroup_required')
    require(shutil.which('systemd-run') and shutil.which('systemctl'), 'owned_native_systemd_required')
    result = subprocess.run(['systemctl','--user','show','--property=Version','--value'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    require(result.returncode==0 and result.stdout.strip(), 'owned_native_user_manager_unavailable')
    return {'manager_version':result.stdout.decode().strip(), 'cgroup_v2':True}


def preflight(request_path, *, existing_controller=False):
    """Read and validate everything before reserving a fresh controller directory."""
    raw, _ = _frozen(_canonical(Path(request_path)), 1024**2)
    request = validate_request(_json(raw))
    base = _canonical(Path(request['execution_root']))
    require(socket.gethostname()==request['worker_host'] and SOURCE.is_relative_to(base),
            'owned_native_worker_or_tool_location_changed')
    for key in ('job','preparation'):
        require(Path(request[key]['path']).is_relative_to(base), 'owned_native_input_outside_workspace')
    job, jobraw, _ = _file_record(request['job'])
    preparation, prepraw, _ = _file_record(request['preparation'])
    controller = base/'readbacks'/(request['job_id']+'-controller')
    _canonical(controller, exists=existing_controller)
    inputs = controller/'inputs'
    args = ['--job',str(inputs/'job.json')]
    validate_job(job, preparation, args)
    workspace, paths, protected, configure = validate_job_paths(job)
    require(workspace==base and paths['output']==base/'readbacks'/request['job_id'] and
            job['preparation']==str(inputs/'preparation.json'), 'owned_native_control_copy_declaration')
    require(not _overlap(controller, paths['output']) and
            all(not _overlap(controller,p) for p in [*paths.values(),*protected]),
            'owned_native_controller_path_overlap')
    require(all(not Path(request[k]['path']).is_relative_to(controller) for k in ('job','preparation')),
            'owned_native_external_control_input_required')
    require(not controller.exists() or existing_controller, 'owned_native_controller_already_exists')
    require(source_closure(paths['source'])==preparation['source_inventory']['source_closure'],
            'owned_native_fresh_SDK_closure_changed')
    worker = preparation['execution']['source']
    require(preparation['execution']['module']==_NATIVE_MODULE and
            worker['path']=='Scripts/StructTrain/TimeLearner/native_acceptance_worker.py',
            'owned_native_worker_capability')
    sdkraw, sdkrecord = _git_blob(paths['source'],worker['commit'],worker['path'],2*1024**2)
    physical, _ = _frozen(paths['source']/worker['path'],2*1024**2)
    require(physical==sdkraw and _sha(physical)==worker['sha256'] and
            sdkrecord['git_blob']==worker['git_blob'], 'owned_native_SDK_worker_bytes_changed')
    tool_worker, _ = _git_blob(SOURCE,request['tool_commit'],worker['path'],2*1024**2)
    require(sdkraw==tool_worker,'owned_native_SDK_worker_helper_version_not_tested')
    snapshot = _source_snapshot(SOURCE, request['tool_commit'])
    module_path = Path(__file__).resolve()
    require(module_path.is_relative_to(SOURCE), 'owned_native_tool_module_outside_root')
    relative = module_path.relative_to(SOURCE).as_posix()
    module_raw, module_record = _git_blob(SOURCE, request['tool_commit'],relative,2*1024**2)
    require(_frozen(module_path,2*1024**2)[0]==module_raw, 'owned_native_tool_module_changed')
    backend = _backend()
    validate_limits(job['limits']['reservation_memory_bytes'],job['limits']['leaf_tasks'],
                    job['limits']['whole_wall_seconds'])
    require(job['limits']['leaf_memory_bytes']<=job['limits']['reservation_memory_bytes'],
            'owned_native_leaf_exceeds_outer_memory')
    registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
    require(not registry.managed_units,'owned_native_managed_registry_requires_SDK_child_registration')
    resources = _resources(paths,protected)
    for lease in registry.inspect()['leases']:
        require(lease['job_id']!=request['job_id'], 'owned_native_attempt_identity_already_used')
        if lease['state']!='held':
            continue
        for old in lease['resources']:
            for new in resources:
                require(not (_overlap(Path(old['canonical_path']),Path(new['path'])) and
                             'write' in (old['access'],new['access'])), 'owned_native_resource_overlap')
    memory = int(next(r.split()[1] for r in Path('/proc/meminfo').read_text().splitlines()
                      if r.startswith('MemAvailable:')))*1024
    free = shutil.disk_usage(base).free
    require(memory>=job['limits']['reservation_memory_bytes']+256*1024**2 and
            free>=job['limits']['reservation_disk_bytes']+job['limits']['physical_free_floor_bytes'],
            'owned_native_capacity_preflight')
    for prior in preparation['prior_bindings']:
        state = inspect(Path(prior['binding_path']).parent)
        require(state['all_processes_closed'] and state['binding']==prior['binding'],
                'owned_native_prior_group_not_closed')
    return {'request':request,'request_raw':raw,'job':job,'job_raw':jobraw,
            'preparation':preparation,'preparation_raw':prepraw,'base':base,'controller':controller,
            'paths':paths,'protected':protected,'configure':configure,'resources':resources,
            'tool_snapshot':snapshot,'module_raw':module_raw,'module_record':module_record,
            'backend':backend,'memory_available':memory,'disk_free':free,
            'external_controls':{k:{'path':request[k]['path'],'identity':_control_identity(Path(request[k]['path'])),
                'sha256':request[k]['sha256']} for k in ('job','preparation')}}


def launch(request_path):
    plan = preflight(request_path)
    directory = plan['controller']
    directory.mkdir()  # Atomic fresh context capability; not another registry lease.
    try:
        _write(directory/'launch-intent.json', {'kind':'owned_native_launch_intent','schema_version':1,
               'launcher':_identity(),'request_sha256':_sha(plan['request_raw']),
               'tool_commit':plan['request']['tool_commit'],'module_git_blob':plan['module_record']['git_blob']})
        (directory/'request.json').write_bytes(plan['request_raw'])
        (directory/'inputs').mkdir()
        (directory/'inputs/job.json').write_bytes(plan['job_raw'])
        (directory/'inputs/preparation.json').write_bytes(plan['preparation_raw'])
        _write(directory/'external-control-identities.json',plan['external_controls'])
        _write(directory/'tool-source.json', plan['tool_snapshot'])
        _write(directory/'module-source.json', {'relative_path':Path(__file__).relative_to(SOURCE).as_posix(),
               'commit':plan['request']['tool_commit'],**plan['module_record'],
               'source_utf8':plan['module_raw'].decode('utf-8'),'executed_copy':False})
        _write(directory/'preflight.json', {'backend':plan['backend'],'memory_available':plan['memory_available'],
               'disk_free':plan['disk_free'],'job_sha256':_sha(plan['job_raw']),
               'preparation_sha256':_sha(plan['preparation_raw']),'configure_arguments':plan['configure']})
        with (directory/'supervisor.log').open('xb') as log:
            process = subprocess.Popen([sys.executable,'-B','-m',_MODULE,'_supervise',str(directory/'request.json')],
                    cwd=SOURCE,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        identity = _identity(process.pid)
        _write(directory/'launched.json', {'supervisor':identity,'module':_MODULE,
               'tool_commit':plan['request']['tool_commit'],'module_sha256':_sha(plan['module_raw'])})
        _display({'controller':str(directory),'supervisor':identity,'scientific_verdict':None})
        return 0
    except BaseException as error:
        original = {'reason':str(error),'traceback':traceback.format_exc(),
                    'restart_allowed':False,'scientific_verdict':None}
        try:
            _write(directory/'launch-failure.json',original)
        except BaseException as write_error:
            _display({'launch_failure':original,'preservation_failure':str(write_error)})
        raise


def _allocated(paths):
    seen, size = set(), 0
    for path in paths:
        if not path.exists():
            continue
        for root, dirs, files in os.walk(path,followlinks=False):
            for p in [Path(root)]+[Path(root)/x for x in files]+[Path(root)/x for x in dirs if (Path(root)/x).is_symlink()]:
                try:
                    row = p.lstat()
                except FileNotFoundError:
                    continue
                key = row.st_dev,row.st_ino
                if key not in seen:
                    seen.add(key);size += row.st_blocks*512
    return size


def _child_request(path, outer_request, outer_binding):
    path = _canonical(path)
    request = _json(_frozen(path/'request.json',1024**2)[0])
    require(type(request) is dict and request.get('kind')=='timelearner_contained_request' and
            request.get('controller')=={'pid':outer_binding['initial_main_pid'],
                'start_ticks':outer_binding['initial_start_ticks']} and
            request.get('boot_id')==outer_request['boot_id'] and request.get('uid')==outer_request['uid'],
            'owned_native_child_controller_changed')
    return request


def _finish(directory, output, expected, registry, job_id, *, errors, known=None, seen=None, receipt=None):
    """Close exact known intents; record original outcome before any stop.

    Recovery writes a NEW receipt directory; immutable earlier outcomes stay put.
    """
    receipt = directory if receipt is None else receipt
    known,seen = ({} if known is None else known),(set() if seen is None else seen)
    def record(name,value):
        try:
            _write(receipt/name,value)
        except BaseException as error:
            errors.append({'file':name,'reason':str(error)})
    outer = directory/'process/contained'
    before, closed, children, outer_request = None, None, [], None
    if (outer/'request.json').exists():
        try:
            outer_request = _json(_frozen(outer/'request.json',1024**2)[0])
            if not (outer/'owned-unit.json').exists():
                adopt(outer)
            before = inspect(outer)
            terminal = _json(_frozen(output/'terminal.json',1024**2)[0]) if (output/'terminal.json').exists() else None
            record('original-outcome.json', {'kernel_before_stop':before,'worker_terminal':terminal,
                   'cleanup_does_not_attest_execution_success':True})
        except BaseException as error:
            errors.append({'phase':'original_outcome','reason':str(error)})
        try:
            closed = stop(outer)
            require(closed['all_processes_closed'], 'owned_native_outer_closure_unproven')
            record('outer-closure.json',closed)
        except BaseException as error:
            errors.append({'phase':'outer_close','reason':str(error)})
    if closed and closed['all_processes_closed'] and outer_request is not None:
        for path in expected:
            if not (path/'request.json').exists():
                if str(path) in seen or str(path) in known:
                    errors.append({'phase':'child_close','directory':str(path),'reason':'previously_seen_request_missing'})
                continue
            try:
                request = _child_request(path,outer_request,closed['binding'])
                if not (path/'owned-unit.json').exists():
                    adopt(path)  # Exact original worker/controller is physically closed.
                current = inspect(path)
                require(current['binding']['request_sha256']==request['sha256'] and
                        (str(path) not in known or known[str(path)]==current['binding']),
                        'owned_native_child_binding_changed')
                state = stop(path)
                require(state['all_processes_closed'] and state['binding']==current['binding'],
                        'owned_native_child_closure_unproven')
                children.append({'directory':str(path),'binding':current['binding'],'closure':state})
            except BaseException as error:
                errors.append({'phase':'child_close','directory':str(path),'reason':str(error)})
        for child in children:
            try:
                request = _child_request(Path(child['directory']),outer_request,closed['binding'])
                state = inspect(child['directory'])
                require(state['all_processes_closed'] and state['binding']==child['binding'] and
                        state['binding']['request_sha256']==request['sha256'],
                        'owned_native_final_child_binding_changed')
            except BaseException as error:
                errors.append({'phase':'child_recheck','reason':str(error)})
    record('child-closures.json',children)
    try:
        leases = [r for r in registry.inspect()['leases'] if r['job_id']==job_id]
        require(len(leases)<=1,'owned_native_ambiguous_worker_lease')
        if leases and leases[0]['state']=='held':
            if closed and closed['all_processes_closed'] and not errors:
                # Existing API verifies exact owner PID/start/boot/UID against binding.
                event = registry.recover_closed_worker(leases[0]['token'],outer,
                    note='Maintained native controller: exact outer owner and all finite canonical child intents closed; original outcome preserved; no science implied.')
                record('lease-recovery.json',event)
            else:
                record('lease-held.json',{'token':leases[0]['token'],'reason':'Incomplete exact graph or preservation; no forced release'})
        record('reservation-final.json',[r for r in registry.inspect()['leases'] if r['job_id']==job_id])
    except BaseException as error:
        errors.append({'phase':'lease_recovery','reason':str(error)})
    return before,closed,children


def _run_owned(runtime, arguments, cwd, directory, output, expected, registry, job_id, limits, disk, scopes, *, control_guard=None):
    """Shared real ownership loop. Tests may supply a pinned tiny process, never a public request override."""
    process = directory/'process'
    errors, binding, reason, last = [], None, None, None
    begun, baseline, minimum, peak = time.monotonic(), _allocated(scopes), shutil.disk_usage(scopes[0]).free, 0
    def record(name,value):
        try:
            _write(directory/name,value)
        except BaseException as error:
            errors.append({'file':name,'reason':str(error)})
    known,seen = {},set()
    try:
        if control_guard is not None:
            control_guard()
        process.mkdir()
        binding = start(runtime,arguments,cwd,process/'contained',memory_bytes=limits['memory_bytes'],
                        tasks=limits['tasks'],maximum_wall_seconds=limits['maximum_wall_seconds'])
        record('started-binding.json',binding)
        _display({'kind':'STARTED','binding':binding})
        outer_request = _json(_frozen(process/'contained/request.json',1024**2)[0])
        while True:
            require(not errors,'owned_native_metadata_preservation_failed')
            if control_guard is not None:
                control_guard()
            last = inspect(process/'contained')
            for path in expected:
                if not (path/'request.json').exists():
                    continue
                if str(path) not in seen:
                    seen.add(str(path))
                    record('child-intent-'+path.parent.parent.name+'.json',{'directory':str(path)})
                _canonical(path)
                try:
                    request = _child_request(path,outer_request,binding)
                except (ValueError,UnicodeDecodeError,FileNotFoundError) as error:
                    if str(error) not in ('collector_json_invalid','collector_file_changed_during_read') and not isinstance(error,(UnicodeDecodeError,FileNotFoundError)):
                        raise
                    continue  # In-flight partial write; final closure is strict.
                if (path/'owned-unit.json').exists():
                    state = inspect(path);binding_now=state['binding']
                    require(binding_now['request_sha256']==request['sha256'] and
                            (str(path) not in known or known[str(path)]==binding_now), 'owned_native_live_child_binding_changed')
                    if str(path) not in known:
                        known[str(path)] = binding_now
                        record('child-binding-'+path.parent.parent.name+'.json',{'directory':str(path),'binding':binding_now})
            free = shutil.disk_usage(scopes[0]).free;growth = _allocated(scopes)-baseline
            minimum,peak = min(minimum,free),max(peak,growth)
            require(free>=disk['minimum_free_bytes'],'owned_native_disk_floor')
            require(growth<=disk['maximum_increment_bytes'],'owned_native_disk_budget')
            require(time.monotonic()-begun<limits['maximum_wall_seconds'],'owned_native_whole_wall_budget')
            require(not (directory/'cancel.request').exists() and not (output/'stop-request.json').exists(),
                    'owned_native_cancel_requested')
            if last['all_processes_closed']:
                break
            time.sleep(1.)
    except BaseException as error:
        reason={'reason':str(error),'traceback':traceback.format_exc()}
    finally:
        if control_guard is not None:
            try:
                control_guard()
            except BaseException as error:
                errors.append({'phase':'controlled_inputs','reason':str(error)})
        record('recorded-child-bindings.json',known)
        record('seen-child-intents.json',sorted(seen))
        before,closed,children = _finish(directory,output,expected,registry,job_id,errors=errors,known=known,seen=seen)
        record('supervisor-result.json',{'reason':reason,'record_errors':errors,'last_before_cleanup':last,
               'outer_binding':binding,'outer_closed':bool(closed and closed['all_processes_closed']),
               'children_closed':children,'disk_peak_increment':peak,'minimum_free':minimum,
               'execution_success_not_inferred_from_cleanup':True,'scientific_verdict':None})
    return 0 if reason is None and not errors and before and before['state'].get('ExecMainStatus')=='0' and before['state'].get('Result')=='success' else 2


def _supervise(request_path):
    directory,request,intent = _context(Path(request_path).parent,require_tool=True)
    require(Path(request_path)==directory/'request.json','owned_native_context_request_changed')
    _write(directory/'supervisor-identity.json',_identity())
    try:
        return _supervise_validated(request_path)
    except BaseException as error:
        _write(directory/'supervisor-bootstrap-failure.json',{'reason':str(error),
               'traceback':traceback.format_exc(),'restart_performed':False,'scientific_verdict':None})
        raise


def _control_identity(path):
    path = _canonical(path)
    row = path.stat()
    return [row.st_dev,row.st_ino,row.st_size,row.st_mtime_ns,row.st_ctime_ns]


def _control_guard(directory, expected, external=None):
    for name, record in expected.items():
        path = directory/'inputs'/name
        require(_control_identity(path)==record['identity'] and
                _sha(_frozen(path,16*1024**2)[0])==record['sha256'],
                'owned_native_consumed_control_identity_changed')
    if external is not None:
        require(type(external) is dict and set(external)=={'job','preparation'},
                'owned_native_external_control_identity_schema')
        for record in external.values():
            require(type(record) is dict and set(record)=={'path','identity','sha256'},
                    'owned_native_external_control_identity_schema')
            path=Path(record['path'])
            require(_control_identity(path)==record['identity'] and
                    _sha(_frozen(path,16*1024**2)[0])==record['sha256'],
                    'owned_native_external_control_identity_changed')


def _supervise_validated(request_path):
    plan = preflight(request_path,existing_controller=True)
    directory=plan['controller']
    external=_json(_frozen(directory/'external-control-identities.json',1024**2)[0])
    require(external==plan['external_controls'],'owned_native_external_controls_changed_since_launch')
    require(_frozen(directory/'inputs/job.json',16*1024**2)[0]==plan['job_raw'] and
            _frozen(directory/'inputs/preparation.json',16*1024**2)[0]==plan['preparation_raw'],
            'owned_native_control_copy_changed')
    runtime={'schema_version':2,'source_closure':plan['preparation']['source_inventory']['source_closure'],
             'executable':file_record(Path(sys.executable)),'app_ini':file_record(directory/'inputs/job.json'),
             'compiler':file_record(Path('/usr/bin/c++')),'resolved_libraries':resolved_libraries(Path(sys.executable)),
             'loaded_process_files':None,'loader_environment':{k:os.environ[k] for k in ('LD_LIBRARY_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM') if k in os.environ},
             'build_flags':{'role':'Python owned-native controller, not a compiled C++ runtime',
                 'tool_commit':plan['request']['tool_commit'],'module_sha256':_sha(plan['module_raw']),
                 'job_sha256':_sha(plan['job_raw']),'preparation_sha256':_sha(plan['preparation_raw'])}}
    runtime['runtime_identity']=runtime_content_identity(runtime);runtime['runtime_fingerprint']=digest_json(runtime['runtime_identity'])
    _write(directory/'runtime.json',runtime)
    controls={name:{'identity':_control_identity(directory/'inputs'/name),'sha256':_sha(raw)}
              for name,raw in [('job.json',plan['job_raw']),('preparation.json',plan['preparation_raw'])]}
    _write(directory/'consumed-control-identities.json',controls)
    job=plan['job'];expected=[plan['paths']['output']/r['name']/'process/contained' for r in plan['preparation']['current']['runplan']]
    result = _run_owned(runtime,['-B','-m',_NATIVE_MODULE]+plan['preparation']['execution']['arguments'],plan['paths']['source'],
            directory,plan['paths']['output'],expected,Reservations.open_existing(plan['base']/'resource-reservations.sqlite3'),
            plan['request']['job_id'],{'memory_bytes':job['limits']['reservation_memory_bytes'],'tasks':job['limits']['leaf_tasks'],
            'maximum_wall_seconds':job['limits']['whole_wall_seconds']},
            {'minimum_free_bytes':job['limits']['physical_free_floor_bytes'],'maximum_increment_bytes':job['limits']['reservation_disk_bytes']},
            [plan['paths']['source'],plan['paths']['build'],plan['paths']['runtime'],plan['paths']['output'],directory],
            control_guard=lambda:_control_guard(directory,controls,external))
    require(_frozen(directory/'inputs/job.json',16*1024**2)[0]==plan['job_raw'] and
            _frozen(directory/'inputs/preparation.json',16*1024**2)[0]==plan['preparation_raw'],
            'owned_native_consumed_control_changed')
    if result==0:
        terminal=_json(_frozen(plan['paths']['output']/'terminal.json',1024**2)[0])
        count=plan['preparation']['current']['counts']['selected_cases']
        require(terminal['job_validation_passed'] is True and terminal['cohort_assertions_passed'] is True and
                terminal['built'] is True and type(terminal['audited_completed_cpp_cases']) is int and
                type(terminal['actual_audited_assertion_passed_cpp_cases']) is int and
                terminal['audited_completed_cpp_cases']==count and
                terminal['actual_audited_assertion_passed_cpp_cases']==count and
                not terminal['actual_audited_failed_cpp_ids'] and not terminal['heartbeat_errors'] and
                not terminal['final_capture_errors'] and terminal['scientific_verdict'] is None,
                'owned_native_completed_worker_outcome_missing')
    return result


def _context(controller, *, require_tool=False):
    controller=_canonical(Path(controller))
    request_raw=_frozen(controller/'request.json',1024**2)[0]
    request=validate_request(_json(request_raw))
    base=_canonical(Path(request['execution_root']))
    require(controller==base/'readbacks'/(request['job_id']+'-controller') and
            socket.gethostname()==request['worker_host'],'owned_native_controller_path_or_worker_changed')
    intent=_json(_frozen(controller/'launch-intent.json',1024**2)[0])
    require(intent['kind']=='owned_native_launch_intent' and
            intent['request_sha256']==_sha(request_raw) and intent['tool_commit']==request['tool_commit'],
            'owned_native_launch_context_changed')
    if require_tool:
        _source_snapshot(SOURCE,request['tool_commit'])
        relative=Path(__file__).resolve().relative_to(SOURCE).as_posix()
        module,_=_git_blob(SOURCE,request['tool_commit'],relative,2*1024**2)
        require(_frozen(Path(__file__).resolve(),2*1024**2)[0]==module,'owned_native_recovery_tool_changed')
    return controller,request,intent


def status(controller):
    controller,request,intent=_context(controller)
    process=controller/'process/contained'
    state=inspect(process) if (process/'request.json').exists() and (process/'owned-unit.json').exists() else None
    owned=_json(_frozen(controller/'supervisor-identity.json',1024**2)[0]) if (controller/'supervisor-identity.json').exists() else None
    launched=_json(_frozen(controller/'launched.json',1024**2)[0]) if (controller/'launched.json').exists() else None
    if owned and launched:
        require(owned==launched['supervisor'],'owned_native_supervisor_identity_changed')
    identity=owned if owned else launched['supervisor'] if launched else None
    if identity is not None:
        _validate_identity(identity)
    if (process/'request.json').exists():
        outer_request=_json(_frozen(process/'request.json',1024**2)[0])
        require(identity is not None and outer_request['controller']=={
                'pid':identity['pid'],'start_ticks':identity['start_ticks']} and
                outer_request['boot_id']==identity['boot_id'] and outer_request['uid']==identity['uid'],
                'owned_native_supervisor_request_link_changed')
    return {'controller':str(controller),'supervisor_identity':identity,
            'supervisor_identity_known':identity is not None,
            'supervisor_live':bool(identity and _same_process(identity)),
            'outer':state,'unbound_outer_intent':(process/'request.json').exists() and not (process/'owned-unit.json').exists(),
            'result':_json(_frozen(controller/'supervisor-result.json',16*1024**2)[0]) if (controller/'supervisor-result.json').exists() else None,
            'scientific_verdict':None}


def recover(controller):
    directory,request,intent=_context(controller,require_tool=True)
    current=status(directory)
    require(current['supervisor_identity_known'] and not current['supervisor_live'],
            'owned_native_supervisor_not_proven_closed')
    jobraw=_frozen(directory/'inputs/job.json',16*1024**2)[0]
    prepraw=_frozen(directory/'inputs/preparation.json',16*1024**2)[0]
    require(_sha(jobraw)==request['job']['sha256'] and _sha(prepraw)==request['preparation']['sha256'],
            'owned_native_recovery_control_changed')
    job,preparation=_json(jobraw),_json(prepraw)
    validate_job(job,preparation,['--job',str(directory/'inputs/job.json')])
    expected=[Path(job['paths']['output'])/r['name']/'process/contained' for r in preparation['current']['runplan']]
    known=_json(_frozen(directory/'recorded-child-bindings.json',16*1024**2)[0]) if (directory/'recorded-child-bindings.json').exists() else {}
    seen=_json(_frozen(directory/'seen-child-intents.json',16*1024**2)[0]) if (directory/'seen-child-intents.json').exists() else []
    for path in expected:
        intent_path=directory/('child-intent-'+path.parent.parent.name+'.json')
        binding_path=directory/('child-binding-'+path.parent.parent.name+'.json')
        if intent_path.exists():
            observed=_json(_frozen(intent_path,1024**2)[0])
            require(observed=={'directory':str(path)},'owned_native_durable_intent_changed')
            seen.append(str(path))
        if binding_path.exists():
            observed=_json(_frozen(binding_path,1024**2)[0])
            require(set(observed)=={'directory','binding'} and observed['directory']==str(path) and
                    (str(path) not in known or known[str(path)]==observed['binding']),
                    'owned_native_durable_binding_changed')
            known[str(path)]=observed['binding']
    require(set(known)<=set(map(str,expected)) and set(seen)<=set(map(str,expected)),
            'owned_native_recovery_graph_outside_canonical')
    attempt=directory/('recovery-'+str(time.time_ns()));attempt.mkdir()
    errors=[]
    try:
        controls=_json(_frozen(directory/'consumed-control-identities.json',1024**2)[0])
        require(set(controls)=={'job.json','preparation.json'},'owned_native_control_identity_schema')
        external=_json(_frozen(directory/'external-control-identities.json',1024**2)[0])
        require(all(external[k]['path']==request[k]['path'] and external[k]['sha256']==request[k]['sha256']
                    for k in ('job','preparation')),'owned_native_external_binding_changed')
        _control_guard(directory,controls,external)
    except BaseException as error:
        errors.append({'phase':'controlled_inputs','reason':str(error)})
    before,closed,children=_finish(directory,Path(job['paths']['output']),expected,
        Reservations.open_existing(Path(request['execution_root'])/'resource-reservations.sqlite3'),
        request['job_id'],errors=errors,known=known,seen=set(seen),receipt=attempt)
    _write(attempt/'result.json',{'outer_closed':bool(closed and closed['all_processes_closed']),
           'errors':errors,'children':children,'restart_performed':False,'scientific_verdict':None})
    return 0 if closed and closed['all_processes_closed'] and not errors else 2


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='action',required=True)
    for name in ('launch','_supervise'):
        commands.add_parser(name).add_argument('request',type=Path)
    for name in ('status','recover'):
        commands.add_parser(name).add_argument('controller',type=Path)
    args=parser.parse_args(argv)
    if args.action=='launch':return launch(args.request)
    if args.action=='_supervise':return _supervise(args.request)
    if args.action=='recover':return recover(args.controller)
    _display(status(args.controller));return 0


if __name__=='__main__':
    raise SystemExit(main())
