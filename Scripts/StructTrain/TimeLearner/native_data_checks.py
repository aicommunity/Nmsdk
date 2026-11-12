"""Finite DATA-dependent checks of an immutable, already-built native runtime.

Use the existing native ownership loop, child-intent recovery and schema5 gate.
This command never builds, changes sources or grants a scientific verdict.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import sys
import threading
import time
import traceback

from .collector_provenance import _canonical, _frozen, _json
from .contained_process import inspect
from .native_evidence import require
from .native_gate import run_native_gate
from .native_gate_inputs import valid_declarations, capture_inputs
from .owned_native_job import (_identity, _same_process, _backend, _write, _run_owned,
                               _finish, _control_identity)
from .owned_python_job import _source_snapshot
from .process_limits import validate_limits
from .process_runner import verify_runtime
from .resource_reservations import Reservations
from .runtime import (file_record, resolved_libraries, runtime_content_identity,
                      digest_json, source_closure)

ROOT = Path(__file__).resolve().parents[3]
BASES = {Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor')}
MODULE = 'Scripts.StructTrain.TimeLearner.native_data_checks'
SHA = re.compile('[0-9a-f]{64}')
COMMIT = re.compile('[0-9a-f]{40}')
NAME = re.compile('[A-Za-z][A-Za-z0-9_-]{0,79}')
TEST = re.compile('[A-Za-z_][A-Za-z0-9_]*/[A-Za-z_][A-Za-z0-9_]*')


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_request(value):
    require(type(value) is dict and set(value) == {'kind', 'schema_version', 'job_id',
        'worker_host', 'execution_root', 'tool_commit', 'source', 'runtime_manifest',
        'inputs', 'cases', 'limits', 'disk'} and value['kind'] == 'timelearner_native_data_checks'
        and type(value['schema_version']) is int and value['schema_version'] == 1,
        'native_data_request_schema')
    require(type(value['job_id']) is str and NAME.fullmatch(value['job_id']) and
        type(value['worker_host']) is str and value['worker_host'] and
        type(value['execution_root']) is str and Path(value['execution_root']) in BASES and
        type(value['tool_commit']) is str and COMMIT.fullmatch(value['tool_commit']),
        'native_data_job_identity')
    for key, field, pattern in [('source', 'commit', COMMIT), ('runtime_manifest', 'sha256', SHA)]:
        row = value[key]
        require(type(row) is dict and set(row) == {'path', field} and
            type(row['path']) is str and Path(row['path']).is_absolute() and
            type(row[field]) is str and pattern.fullmatch(row[field]), 'native_data_binding')
    require(valid_declarations(value['inputs']), 'native_data_inputs')
    cases = value['cases']
    require(type(cases) is list and 1 <= len(cases) <= 32 and all(type(r) is dict and
        set(r) == {'name', 'test_id'} and type(r['name']) is str and NAME.fullmatch(r['name']) and
        type(r['test_id']) is str and TEST.fullmatch(r['test_id']) for r in cases), 'native_data_cases')
    require(len({r['name'].casefold() for r in cases}) == len(cases) and
        len({r['test_id'] for r in cases}) == len(cases), 'native_data_duplicate_case')
    limits = value['limits']
    require(type(limits) is dict and set(limits) == {'memory_bytes', 'tasks', 'maximum_wall_seconds',
        'leaf_memory_bytes', 'leaf_tasks', 'leaf_wall_seconds', 'reservation_memory_bytes'} and
        all(type(n) is int and n > 0 for n in limits.values()), 'native_data_limits')
    validate_limits(limits['memory_bytes'], limits['tasks'], limits['maximum_wall_seconds'])
    validate_limits(limits['leaf_memory_bytes'], limits['leaf_tasks'], limits['leaf_wall_seconds'])
    require(limits['maximum_wall_seconds'] >= len(cases)*limits['leaf_wall_seconds']+60 and
        limits['reservation_memory_bytes'] >= limits['memory_bytes']+limits['leaf_memory_bytes'],
        'native_data_aggregate_budget')
    require(type(value['disk']) is dict and set(value['disk']) == {'minimum_free_bytes', 'maximum_output_bytes'}
        and all(type(n) is int and n > 0 for n in value['disk'].values()), 'native_data_disk')
    return value


def layout(request):
    base = Path(request['execution_root'])
    output = base/'readbacks'/request['job_id']
    return base, output, output.with_name(output.name+'-controller')


def resources(request, runtime, request_path):
    base, output, controller = layout(request)
    rows = [(ROOT, 'read'), (Path(request['source']['path']), 'read'),
            (Path(request_path), 'read'), (Path(request['runtime_manifest']['path']), 'read'),
            (Path(runtime['executable']['path']).parent, 'read'),
            *[(Path(r['path']), 'read') for r in request['inputs']],
            (output, 'write')]
    result = {}
    for path, access in rows:
        path = _canonical(path, exists=access == 'read')
        require(path.is_relative_to(base), 'native_data_resource_outside_workspace')
        if access == 'read':
            require(not any(path.is_relative_to(p) or p.is_relative_to(path)
                for p in (output, controller)), 'native_data_input_output_overlap')
        result[str(path), access] = {'path': str(path), 'access': access}
    return list(result.values())


def _bound_runtime(request):
    raw, _ = _frozen(Path(request['runtime_manifest']['path']), 16*1024**2)
    require(_hash(raw) == request['runtime_manifest']['sha256'], 'native_data_runtime_manifest_changed')
    runtime = _json(raw)
    verify_runtime(runtime)
    source = _canonical(Path(request['source']['path']))
    closure = source_closure(source)
    require(closure['root']['head'] == request['source']['commit'] and
        closure == runtime['source_closure'], 'native_data_runtime_source_changed')
    return runtime


def _controls(request_path, copied, external_identity, raw):
    require(_control_identity(request_path) == external_identity and
        _frozen(request_path, 1024**2)[0] == raw and _frozen(copied, 1024**2)[0] == raw,
        'native_data_control_changed')


def run(request_path):
    request_path = _canonical(Path(request_path));raw, _ = _frozen(request_path, 1024**2)
    request = validate_request(_json(raw));base, output, controller = layout(request)
    require(socket.gethostname() == request['worker_host'] and ROOT.is_relative_to(base), 'native_data_host')
    require(not output.exists() and not controller.exists(), 'native_data_fresh_attempt_required')
    _canonical(base/'readbacks');_backend()
    snapshot = _source_snapshot(ROOT, request['tool_commit'])
    runtime = _bound_runtime(request)
    declared = resources(request, runtime, request_path)
    capture_inputs(request['inputs'], output)  # Validate all bounded bytes before any launch.
    registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
    require(not registry.managed_units, 'native_data_uses_finite_native_controller')
    leases = registry.inspect()['leases']
    require(not any(r['job_id'] == request['job_id'] for r in leases), 'native_data_attempt_already_used')
    for old in [s for r in leases if r['state'] == 'held' for s in r['resources']]:
        for new in declared:
            a, b = Path(old['canonical_path']), Path(new['path'])
            require(not ('write' in (old['access'], new['access']) and
                (a.is_relative_to(b) or b.is_relative_to(a))), 'native_data_resource_busy')
    memory = int(next(r.split()[1] for r in Path('/proc/meminfo').read_text().splitlines()
                      if r.startswith('MemAvailable:')))*1024
    require(memory >= request['limits']['reservation_memory_bytes']+256*1024**2 and
        shutil.disk_usage(base).free >= sum(request['disk'].values()), 'native_data_capacity')
    controller.mkdir();copied = controller/'request.json';copied.write_bytes(raw)
    identity = _identity();external_identity = _control_identity(request_path)
    _write(controller/'launch-intent.json', {'supervisor': identity, 'request_sha256': _hash(raw),
        'request_path': str(request_path), 'external_identity': external_identity})
    _write(controller/'tool-source.json', snapshot)
    _write(controller/'declared-resources.json', declared)
    outer = {'schema_version': 2, 'source_closure': runtime['source_closure'],
        'executable': file_record(Path(sys.executable)), 'app_ini': file_record(copied),
        'compiler': file_record(Path('/usr/bin/c++')), 'resolved_libraries': resolved_libraries(Path(sys.executable)),
        'loaded_process_files': None, 'loader_environment': {k: os.environ[k] for k in
            ('LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM') if k in os.environ},
        'build_flags': {'role': 'Python DATA check controller; no build or scientific claim',
                        'tool_commit': request['tool_commit'], 'request_sha256': _hash(raw)}}
    outer['runtime_identity'] = runtime_content_identity(outer)
    outer['runtime_fingerprint'] = digest_json(outer['runtime_identity'])
    _write(controller/'runtime.json', outer)
    expected = [output/r['name']/'process/contained' for r in request['cases']]
    return _run_owned(outer, ['-B', '-m', MODULE, '_worker', str(copied)], ROOT, controller,
        output, expected, registry, request['job_id'],
        {k: request['limits'][k] for k in ('memory_bytes', 'tasks', 'maximum_wall_seconds')},
        {'minimum_free_bytes': request['disk']['minimum_free_bytes'],
         'maximum_increment_bytes': request['disk']['maximum_output_bytes']},
        [controller, output], control_guard=lambda: _controls(request_path, copied, external_identity, raw))


def _context(controller):
    controller = _canonical(Path(controller));raw, _ = _frozen(controller/'request.json', 1024**2)
    request = validate_request(_json(raw));base, output, expected = layout(request)
    require(controller == expected and socket.gethostname() == request['worker_host'], 'native_data_context')
    intent = _json(_frozen(controller/'launch-intent.json', 1024**2)[0])
    require(type(intent) is dict and set(intent) == {'supervisor', 'request_sha256', 'request_path', 'external_identity'}
            and intent['request_sha256'] == _hash(raw), 'native_data_request_copy_changed')
    outer_request = controller/'process/contained/request.json'
    if outer_request.exists():
        observed = _json(_frozen(outer_request, 1024**2)[0])
        identity = intent['supervisor']
        require(observed['controller'] == {'pid': identity['pid'], 'start_ticks': identity['start_ticks']}
                and observed['boot_id'] == identity['boot_id'] and observed['uid'] == identity['uid'],
                'native_data_supervisor_binding_changed')
    return request, base, output, controller, intent


def worker(request_path):
    request, base, output, controller, intent = _context(Path(request_path).parent)
    require(Path(request_path) == controller/'request.json', 'native_data_worker_request')
    outer = inspect(controller/'process/contained')
    identity = _identity()
    require(outer['binding']['initial_main_pid'] == identity['pid'] and
        outer['binding']['initial_start_ticks'] == identity['start_ticks'] and
        Path('/proc/self/cgroup').read_text().strip() == '0::'+outer['binding']['control_group'],
        'native_data_worker_not_bound_main')
    require(not output.exists(), 'native_data_output_already_exists');output.mkdir()
    registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
    token = None;stop = threading.Event();errors = [];thread = None;passed = False
    try:
        runtime = _bound_runtime(request)
        declared = resources(request, runtime, Path(intent['request_path']))
        require(declared == _json(_frozen(controller/'declared-resources.json', 1024**2)[0]),
                'native_data_resources_changed')
        lease = registry.reserve(request['job_id'], declared, ttl_seconds=120,
            demands={'slots': 1, 'memory_bytes': request['limits']['reservation_memory_bytes'],
                     'disk_bytes': request['disk']['maximum_output_bytes']} if registry.capacity is not None else None)
        token = lease['token'];_write(output/'reservation.json', lease)
        def heartbeat():
            while not stop.wait(10):
                try:
                    registry.heartbeat(token, ttl_seconds=120);registry.validate_paths(token)
                except BaseException as error:
                    errors.append(str(error));return
        thread = threading.Thread(target=heartbeat, daemon=True);thread.start()
        before = _source_snapshot(ROOT, request['tool_commit']);_write(output/'tool-before.json', before)
        source_before = source_closure(Path(request['source']['path']));_write(output/'source-before.json', source_before)
        results = []
        for row in request['cases']:
            require(not errors, 'native_data_heartbeat_failed');registry.validate_paths(token)
            _bound_runtime(request)
            spec = {'kind': 'timelearner_native_test_gate', 'schema_version': 5,
                'runtime_manifest': request['runtime_manifest']['path'], 'source_root': request['source']['path'],
                'expected_test_ids': [row['test_id']], 'maximum_wall_seconds': request['limits']['leaf_wall_seconds'],
                'asan_options': '', 'cooperative_runtime_capture': True,
                'process_limits': {'memory_bytes': request['limits']['leaf_memory_bytes'], 'tasks': request['limits']['leaf_tasks']},
                'data_inputs': request['inputs']}
            spec_path = output/(row['name']+'-spec.json');_write(spec_path, spec)
            result = run_native_gate(spec_path, output/row['name']);results.append(result)
            _write(output/(row['name']+'-result.json'), result)
            require(result['execution'] == 'completed' and result['validity'] == 'valid' and
                    result['assertion_status'] == 'passed', 'native_data_case_not_passed:'+row['name'])
        require(not errors, 'native_data_heartbeat_failed');registry.validate_paths(token)
        _bound_runtime(request)
        after = _source_snapshot(ROOT, request['tool_commit']);_write(output/'tool-after.json', after)
        source_after = source_closure(Path(request['source']['path']));_write(output/'source-after.json', source_after)
        require(before == after and source_before == source_after, 'native_data_source_changed')
        _write(output/'results.json', {'cases': results, 'scientific_verdict': None})
        passed = True
    except BaseException as error:
        _write(output/'exception.json', {'reason': str(error), 'traceback': traceback.format_exc()})
        raise
    finally:
        stop.set()
        if thread is not None:
            thread.join(5)
            if thread.is_alive(): errors.append('heartbeat_thread_not_closed')
        _write(output/'terminal.json', {'operation_passed': passed and not errors, 'heartbeat_errors': errors,
            'lease_release': 'external controller only after exact outer and finite children close', 'scientific_verdict': None})
    return 0 if passed and not errors else 2


def status(controller):
    request, base, output, controller, intent = _context(controller)
    outer_path = controller/'process/contained'
    return {'supervisor_live': _same_process(intent['supervisor']),
        'outer': inspect(outer_path) if (outer_path/'owned-unit.json').exists() else None,
        'result': _json(_frozen(controller/'supervisor-result.json', 16*1024**2)[0])
                  if (controller/'supervisor-result.json').exists() else None, 'scientific_verdict': None}


def recover(controller):
    request, base, output, controller, intent = _context(controller)
    require(not _same_process(intent['supervisor']), 'native_data_supervisor_still_live')
    _source_snapshot(ROOT, request['tool_commit'])
    receipt = controller/('recovery-'+str(time.time_ns()));receipt.mkdir()
    errors = []
    known = _json(_frozen(controller/'recorded-child-bindings.json', 16*1024**2)[0]) if (controller/'recorded-child-bindings.json').exists() else {}
    seen = _json(_frozen(controller/'seen-child-intents.json', 16*1024**2)[0]) if (controller/'seen-child-intents.json').exists() else []
    expected = [output/r['name']/'process/contained' for r in request['cases']]
    require(set(known) <= set(map(str, expected)) and set(seen) <= set(map(str, expected)), 'native_data_recovery_graph')
    _, closed, children = _finish(controller, output, expected,
        Reservations.open_existing(base/'resource-reservations.sqlite3'), request['job_id'], errors=errors,
        known=known, seen=set(seen), receipt=receipt)
    _write(receipt/'result.json', {'outer_closed': bool(closed and closed['all_processes_closed']),
        'children': children, 'errors': errors, 'restart_performed': False, 'scientific_verdict': None})
    return 0 if closed and closed['all_processes_closed'] and not errors else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', '_worker', 'status', 'recover'));parser.add_argument('path', type=Path)
    args = parser.parse_args(argv)
    if args.action == 'status':
        print(json.dumps(status(args.path), allow_nan=False));return 0
    return {'run': run, '_worker': worker, 'recover': recover}[args.action](args.path)


if __name__ == '__main__':
    raise SystemExit(main())
