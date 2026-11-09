"""Owned Python validation or reviewed duplicate-AR maintenance from typed JSON.

This adapter reuses contained_runner, validation and apply_plan. It generates
no program and provides no native-build/model action. Selected validation code
and its scope still require independent source review. Existing outputs fail.
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
import threading
import time
import traceback

from .collector_provenance import _canonical, _frozen, _git_blob, _json
from .contained_process import inspect
from .contained_runner import execute
from .native_evidence import EvidenceError, require
from .process_limits import validate_limits
from .resource_reservations import Reservations
from .runtime import file_record, resolved_libraries, runtime_content_identity, digest_json

SOURCE = Path(__file__).resolve().parents[3]
_BASES = {Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor')}


def _write(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())


def _pinned(record):
    _file_binding(record)
    raw, observed = _frozen(Path(record['path']), 64*1024**2)
    require(observed['sha256'] == record['sha256'], 'owned_job_bound_file_changed')
    return _json(raw)


def _commit(value):
    return type(value) is str and len(value) == 40 and all(c in '0123456789abcdef' for c in value)


def _file_binding(record):
    require(type(record) is dict and set(record) == {'path', 'sha256'} and
            type(record['path']) is str and '\0' not in record['path'] and Path(record['path']).is_absolute() and
            type(record['sha256']) is str and len(record['sha256']) == 64 and
            all(c in '0123456789abcdef' for c in record['sha256']), 'owned_job_file_binding')


def validate_request(value):
    require(type(value) is dict and set(value) == {'kind', 'schema_version', 'job_id', 'worker_host',
        'execution_root', 'tool_commit', 'limits', 'disk', 'operation'} and
        value['kind'] == 'timelearner_owned_python_job' and type(value['schema_version']) is int and
        value['schema_version'] == 1, 'owned_job_request_schema')
    job = value['job_id']
    require(type(job) is str and job and all(c.isalnum() or c in '-_' for c in job), 'owned_job_id')
    require(type(value['execution_root']) is str and Path(value['execution_root']) in _BASES and
            type(value['worker_host']) is str,
            'owned_job_explicit_worker_root')
    require(_commit(value['tool_commit']), 'owned_job_tool_commit')
    require(type(value['limits']) is dict and set(value['limits']) ==
            {'memory_bytes', 'tasks', 'maximum_wall_seconds'}, 'owned_job_limits_schema')
    validate_limits(**value['limits'])
    require(type(value['disk']) is dict and set(value['disk']) == {'minimum_free_bytes', 'maximum_output_bytes'}
            and all(type(n) is int and n > 0 for n in value['disk'].values()), 'owned_job_disk_schema')
    operation = value['operation']
    require(type(operation) is dict and operation.get('kind') in
            ('python-validation', 'duplicate-static-archives', 'native-canonical-preparation'), 'owned_job_operation')
    if operation['kind'] == 'python-validation':
        require(set(operation) == {'kind', 'source', 'suite', 'fixtures'} and
                type(operation['source']) is dict and set(operation['source']) == {'path', 'commit'} and
                type(operation['fixtures']) is dict and all(type(k) is str and
                k.startswith(('TIMELEARNER_', 'TL_')) and type(v) is str for k, v in operation['fixtures'].items()),
                'owned_job_validation_schema')
        require(type(operation['source']['path']) is str and Path(operation['source']['path']).is_absolute() and
                _commit(operation['source']['commit']), 'owned_job_validation_source_binding')
        _file_binding(operation['suite'])
    elif operation['kind']=='native-canonical-preparation':
        require(set(operation)=={'kind','plan'},'owned_job_canonical_schema')
        _file_binding(operation['plan'])
    else:
        require(set(operation) == {'kind', 'plan', 'review'}, 'owned_job_archive_schema')
        _file_binding(operation['plan']);_file_binding(operation['review'])
    return value


def _paths(request):
    base = _canonical(Path(request['execution_root']))
    require(socket.gethostname() == request['worker_host'] and SOURCE.is_relative_to(base), 'owned_job_worker_changed')
    operation = request['operation']
    files = ([operation['suite']] if operation['kind']=='python-validation' else
             [operation['plan']] if operation['kind']=='native-canonical-preparation' else [operation['plan'],operation['review']])
    for row in files:
        require(Path(row['path']).is_relative_to(base), 'owned_job_input_outside_execution_root')
    if operation['kind'] == 'python-validation':
        for path in [operation['source']['path'], *operation['fixtures'].values()]:
            require(Path(path).is_absolute() and Path(path).is_relative_to(base), 'owned_job_source_or_fixture_outside_root')
    _canonical(base/'readbacks')
    return base, _canonical(base/'readbacks'/request['job_id'], exists=False)


def _display(value):
    try:
        print(value, flush=True)
    except BrokenPipeError:
        # Files remain authoritative if the observing transport disconnects.
        sys.stdout = open(os.devnull, 'w')


def _source_snapshot(root, commit):
    root = _canonical(Path(root))
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args],
            env={**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_OPTIONAL_LOCKS': '0'})
    require(git('rev-parse', 'HEAD').decode().strip() == commit and
            not git('status', '--porcelain', '--untracked-files=all', '--ignore-submodules=all').strip(),
            'owned_job_source_epoch_or_status')
    result = {}
    for path in sorted((root/'Scripts').rglob('*')):
        if path.is_dir() and not path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        raw, record = _frozen(path, 64*1024**2)
        git_raw, git_record = _git_blob(root, commit, relative, 64*1024**2)
        require(raw == git_raw, 'owned_job_source_bytes_changed')
        result[relative] = {**record, 'git_blob': git_record['git_blob']}
    require(result, 'owned_job_source_projection_empty')
    return {'root_commit': commit, 'files': result, 'SDK_gitlinks_materialized_or_verified': False,
            'scope': 'all materialized Scripts files only; not full SDK/build provenance'}


def _ancestry():
    result = {};pid = os.getpid()
    while pid > 1:
        fields = Path('/proc', str(pid), 'stat').read_text().rsplit(') ', 1)[1].split()
        result[str(pid)] = fields[19];pid = int(fields[1])
    return result


def _fixture_snapshot(suite, bindings):
    from .validation import _digest
    require(type(suite.get('fixtures')) is dict and set(suite['fixtures']) == set(bindings),
            'owned_job_fixture_bindings')
    result = {}
    for name, declaration in suite['fixtures'].items():
        root = _canonical(Path(bindings[name]));pattern = declaration['pattern']
        require(type(pattern) is str and pattern and not Path(pattern).is_absolute() and
                '..' not in Path(pattern).parts and '\\' not in pattern, 'owned_job_fixture_pattern')
        records = {p.relative_to(root).as_posix(): _frozen(p, 64*1024**2)[1]
                   for p in sorted(root.glob(pattern))}
        fingerprint = _digest({p: r['sha256'] for p, r in records.items()})
        require(records and len(records) == declaration['files'] and
                fingerprint == declaration['fingerprint'], 'owned_job_fixture_content_changed')
        result[name] = {'files': records, 'fingerprint': fingerprint}
    return result


def _validation_resources(operation, job):
    # Reservations owns directory trees, never individual configuration files.
    resources = [{'path': str(SOURCE), 'access': 'read'}, {'path': operation['source']['path'], 'access': 'read'},
                 {'path': str(Path(operation['suite']['path']).parent), 'access': 'read'},
                 *({'path': p, 'access': 'read'} for p in operation['fixtures'].values()),
                 {'path': str(job), 'access': 'write'}]
    resources = [{'path': str(_canonical(Path(r['path']))), 'access': r['access']} for r in resources]
    return list({(r['path'], r['access']): r for r in resources}.values())


def _worker(request_path):
    raw, _ = _frozen(Path(request_path), 1024*1024)
    request = validate_request(_json(raw));base, job = _paths(request)
    context_raw, _ = _frozen(job/'launch-context.json', 1024*1024)
    context = _json(context_raw);runtime = _json(_frozen(job/'process/contained/runtime.json', 1024*1024)[0])
    require(runtime['app_ini']['path'] == str(Path(request_path)) and
            runtime['app_ini']['sha256'] == hashlib.sha256(raw).hexdigest() and
            runtime['source_closure']['tool_root'] == request['tool_commit'] and
            runtime['source_closure']['launch_context_sha256'] == hashlib.sha256(context_raw).hexdigest(),
            'owned_job_launch_context_changed')
    unit_request = _json(_frozen(job/'process/contained/request.json', 1024*1024)[0])
    require(context['client'] == unit_request['controller'] and context['boot_id'] == unit_request['boot_id'] ==
            Path('/proc/sys/kernel/random/boot_id').read_text().strip() and unit_request['uid'] == os.getuid(),
            'owned_job_launch_ancestry_binding')
    binding = inspect(job/'process/contained')['binding']
    own_ticks = Path('/proc/self/stat').read_text().rsplit(') ', 1)[1].split()[19]
    require(binding['initial_main_pid'] == os.getpid() and binding['initial_start_ticks'] == own_ticks and
            Path('/proc/self/cgroup').read_text().strip() == '0::'+binding['control_group'],
            'owned_job_worker_not_bound_main')
    output = job/'worker';output.mkdir(exist_ok=False)
    temporary = output/'tmp';temporary.mkdir();os.environ['TMPDIR'] = str(temporary)
    for name, directory in (('MPLCONFIGDIR', 'matplotlib'), ('XDG_CACHE_HOME', 'xdg-cache')):
        cache = temporary/directory;cache.mkdir();os.environ[name] = str(cache)
    _write(output/'temporary-environment.json',
           {name: os.environ[name] for name in ('TMPDIR', 'MPLCONFIGDIR', 'XDG_CACHE_HOME')})
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1';sys.dont_write_bytecode = True
    registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
    operation = request['operation'];resources = [{'path': str(base), 'access': 'write'}]
    if operation['kind'] == 'python-validation':
        resources = _validation_resources(operation, job)
    elif operation['kind']=='native-canonical-preparation':
        from .native_canonical_preparation import resources as canonical_resources
        resources=canonical_resources(_pinned(operation['plan']),job,operation['plan']['path'])
    token = None;stop = threading.Event();errors = [];thread = None;passed = False;before = None
    def emit(name, value):
        _write(output/name, value)
    try:
        lease = registry.reserve(request['job_id'], resources, ttl_seconds=120,
            demands={'slots': 1, 'memory_bytes': request['limits']['memory_bytes'],
                     'disk_bytes': request['disk']['maximum_output_bytes']} if registry.capacity is not None else None)
        token = lease['token'];emit('reservation.json', lease)
        def heartbeat():
            while not stop.wait(10):
                try:
                    registry.heartbeat(token, ttl_seconds=120);registry.validate_paths(token)
                except BaseException as error:
                    errors.append(str(error));return
        thread = threading.Thread(target=heartbeat, daemon=True);thread.start()
        before = _source_snapshot(SOURCE, request['tool_commit']);emit('tool-source-before.json', before)
        if operation['kind'] == 'python-validation':
            source = operation['source'];snapshot = _source_snapshot(source['path'], source['commit'])
            emit('validation-source-before.json', snapshot)
            suite = _pinned(operation['suite'])
            require(type(suite.get('expected_test_ids')) is list and suite['expected_test_ids'], 'owned_job_suite_inventory')
            fixtures = _fixture_snapshot(suite, operation['fixtures']);emit('fixtures-before.json', fixtures)
            arguments = [sys.executable, '-B', '-m', 'Scripts.StructTrain.TimeLearner.validation',
                         operation['suite']['path'], '--output', str(output/'validation')]
            for name, path in operation['fixtures'].items():
                _canonical(Path(path));arguments += ['--fixture', name+'='+path]
            environment = dict(os.environ)
            for name in ('PYTHONPATH', 'PYTHONHOME'):
                environment.pop(name, None)
            result = subprocess.run(arguments, cwd=source['path'], env=environment)
            emit('validation-process.json', {'returncode': result.returncode, 'arguments': arguments})
            require(_source_snapshot(source['path'], source['commit']) == snapshot, 'owned_job_validation_source_changed')
            emit('validation-source-after.json', snapshot)
            require(_fixture_snapshot(suite, operation['fixtures']) == fixtures, 'owned_job_fixture_epoch_changed')
            emit('fixtures-after.json', fixtures)
            require(_pinned(operation['suite']) == suite, 'owned_job_suite_changed_during_run')
            record = _json(_frozen(output/'validation/result.json', 16*1024**2)[0])
            require(result.returncode == 0 and record['assertion_status'] == 'passed' and
                    record['kind'] == 'timelearner_python_validation_result' and record['schema_version'] == 1 and
                    record['suite_id'] == suite['suite_id'] and record['package_fingerprint'] == suite['package_fingerprint'] and
                    record['expected_test_ids'] == suite['expected_test_ids'] and
                    _json(_frozen(output/'validation/suite.json', 16*1024**2)[0]) == suite and
                    record['executed_tests'] == len(suite['expected_test_ids']) and not record['skipped'] and
                    not record['failures'] and not record['errors'], 'owned_job_validation_failed')
        elif operation['kind']=='native-canonical-preparation':
            from .native_canonical_preparation import produce
            plan=_pinned(operation['plan']);emit('canonical-plan.json',plan)
            def canonical_guard():
                require(not errors,'owned_job_heartbeat_failed')
                require(shutil.disk_usage(base).free>=request['disk']['minimum_free_bytes'],'owned_job_disk_floor')
            produce(plan,operation['plan']['path'],operation['plan']['sha256'],output,registry,token,canonical_guard,emit)
        else:
            from .archive_retirement import retire
            plan, review = _pinned(operation['plan']), _pinned(operation['review'])
            require(Path(plan['root']) == base and review['plan_sha256'] == operation['plan']['sha256'],
                    'owned_job_archive_root_or_plan_binding')
            emit('plan.json', plan);emit('review.json', review)
            free_before = shutil.disk_usage(base).free;emit('space-before.json', {'free_bytes': free_before})
            def extra_guard():
                require(not errors, 'owned_job_heartbeat_failed')
                require(shutil.disk_usage(base).free >= request['disk']['minimum_free_bytes'], 'owned_job_disk_floor')
            retire(plan, review, registry, token, output, context['ancestors'], emit, extra_guard)
            emit('space-after.json', {'free_bytes': shutil.disk_usage(base).free,
                'actual_df_delta_bytes': shutil.disk_usage(base).free-free_before,
                'logical_removed_bytes': plan['bytes_planned'],
                'allocated_removed_bytes': review['candidate_allocated_bytes']})
        require(not errors, 'owned_job_heartbeat_failed')
        after = _source_snapshot(SOURCE, request['tool_commit']);emit('tool-source-after.json', after)
        require(after == before, 'owned_job_tool_source_changed');passed = True
    except BaseException as error:
        emit('exception.json', {'reason': str(error), 'traceback': traceback.format_exc()})
    finally:
        stop.set()
        if thread is not None:
            thread.join(timeout=15)
        if before is not None and not (output/'tool-source-after.json').exists():
            try:
                after = _source_snapshot(SOURCE, request['tool_commit']);emit('tool-source-after.json', after)
                passed = passed and after == before
            except BaseException as error:
                emit('tool-source-after-error.json', {'reason': str(error)});passed = False
        passed = passed and not errors
        emit('terminal.json', {'operation_passed': passed, 'operation': operation['kind'],
            'heartbeat_errors': errors, 'lease_release': 'controller only after whole cgroup closure',
            'selected_validation_scope_requires_source_review': True, 'scientific_verdict': None})
    return 0 if passed else 1


def run(request_path):
    raw, _ = _frozen(Path(request_path), 1024*1024)
    request = validate_request(_json(raw));base, job = _paths(request)
    require(sys.platform == 'linux' and not job.exists(), 'owned_job_fresh_linux_attempt_required')
    _source_snapshot(SOURCE, request['tool_commit'])
    job.mkdir(exist_ok=False);copied = job/'request.json';copied.write_bytes(raw)
    context = {'client': {'pid': os.getpid(), 'start_ticks': Path('/proc/self/stat').read_text().rsplit(') ', 1)[1].split()[19]},
               'ancestors': _ancestry(), 'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    _write(job/'launch-context.json', context)
    context_sha = hashlib.sha256((job/'launch-context.json').read_bytes()).hexdigest()
    mem = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))*1024
    require(mem >= request['limits']['memory_bytes']+256*1024**2 and shutil.disk_usage(base).free >=
            request['disk']['minimum_free_bytes']+request['disk']['maximum_output_bytes'], 'owned_job_capacity_preflight')
    _write(job/'preflight.json', {'MemAvailable_bytes': mem, 'disk_free_bytes': shutil.disk_usage(base).free})
    runtime = {'schema_version': 2, 'source_closure': {'kind': 'owned_python_metadata_projection',
        'tool_root': request['tool_commit'], 'launch_context_sha256': context_sha, 'SDK_source_verified': False},
        'executable': file_record(Path(sys.executable)), 'app_ini': file_record(copied),
        'compiler': file_record(Path(sys.executable)), 'resolved_libraries': resolved_libraries(Path(sys.executable)),
        'loaded_process_files': None, 'loader_environment': {}, 'build_flags':
        {'role': 'Python validation or duplicate-AR maintenance only; legacy compiler field is Python interpreter'}}
    runtime['runtime_identity'] = runtime_content_identity(runtime)
    runtime['runtime_fingerprint'] = digest_json(runtime['runtime_identity'])
    def started(binding):
        line = 'STARTED '+json.dumps(binding, allow_nan=False)+'\n'
        with (job/'supervisor.log').open('x', encoding='utf-8') as stream:
            stream.write(line);stream.flush();os.fsync(stream.fileno())
        _display(line.rstrip('\n'))
    last_check = [0.];guard_failure = [None];peak_allocated = [0];minimum_free = [shutil.disk_usage(base).free]
    def monitor(state):
        if time.monotonic()-last_check[0] < 1:
            return
        last_check[0] = time.monotonic()
        allocated = 0
        for path in job.rglob('*'):
            try:
                allocated += path.lstat().st_blocks*512
            except FileNotFoundError:
                continue  # Concurrent TemporaryDirectory cleanup is expected.
        free = shutil.disk_usage(base).free;peak_allocated[0] = max(peak_allocated[0], allocated)
        minimum_free[0] = min(minimum_free[0], free)
        with (job/'monitor.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'time': time.time(), 'free_bytes': free, 'output_allocated_bytes': allocated,
                                     'whole_group_closed': state['all_processes_closed']})+'\n')
            stream.flush();os.fsync(stream.fileno())
        if free < request['disk']['minimum_free_bytes']:
            guard_failure[0] = {'kind': 'owned_job_disk_floor', 'free_bytes': free}
        elif allocated > request['disk']['maximum_output_bytes']:
            guard_failure[0] = {'kind': 'owned_job_output_budget', 'bytes': allocated}
        require(guard_failure[0] is None, guard_failure[0]['kind'] if guard_failure[0] else 'owned_job_guard')
    result = execute(runtime, ['-B', '-m', 'Scripts.StructTrain.TimeLearner.owned_python_job',
        '_worker', str(copied)], SOURCE, job/'process', **request['limits'], on_started=started, monitor=monitor)
    _write(job/'controller-result.json', result)
    _write(job/'monitor-final.json', {'guard_triggered': guard_failure[0] is not None,
        'original_reason': guard_failure[0], 'peak_allocated_bytes': peak_allocated[0],
        'minimum_free_bytes': minimum_free[0]})
    closure = inspect(job/'process/contained');require(closure['all_processes_closed'], 'owned_job_closure_unproven')
    registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
    rows = [r for r in registry.inspect()['leases'] if r['job_id'] == request['job_id']]
    if rows and rows[0]['state'] == 'held':
        recovered = registry.recover_closed_worker(rows[0]['token'], job/'process/contained',
            note='Typed Python job whole cgroup closed; execution/test/maintenance outcome remains separate.')
        _write(job/'lease-recovery.json', recovered)
    _write(job/'closure-and-reservation.json', {'closure': closure,
        'leases': [r for r in registry.inspect()['leases'] if r['job_id'] == request['job_id']]})
    terminal = _json(_frozen(job/'worker/terminal.json', 1024*1024)[0]) if (job/'worker/terminal.json').exists() else None
    _display(json.dumps({'controller': result, 'worker_terminal': terminal, 'scientific_verdict': None}, allow_nan=False))
    return 0 if result['execution'] == 'completed' and terminal and terminal['operation_passed'] else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', '_worker'));parser.add_argument('request', type=Path)
    args = parser.parse_args(argv)
    try:
        return (run if args.action == 'run' else _worker)(args.request)
    except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'kind': 'owned_python_job_error', 'reason': str(error), 'scientific_verdict': None}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
