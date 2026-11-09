"""Synchronous execution with whole-cgroup ownership and actual runtime capture.

This explicit backend leaves legacy pidfd attempts unchanged. A successful main
exit cannot complete an attempt while any descendant remains in its cgroup.
"""
import os
from pathlib import Path
import shutil
import time

from . import contained_process
from .native_evidence import load, require
from .process_runner import verify_runtime, _start_identity, _write
from .process_limits import validate_limits
from .runtime import loaded_process_files
from .operational_diagnostics import inspect_streams


def _returncode(state):
    code, status = state.get('ExecMainCode'), state.get('ExecMainStatus')
    if code == '1' and status is not None:
        return int(status)
    if code in ('2', '3') and status is not None:
        return -int(status)
    return None


def inspect_attempt(output):
    output = Path(output).resolve(strict=True)
    if not (output/'contained/request.json').exists():
        return {'execution': 'unknown', 'reason': 'no_contained_launch_intent', 'scientific_verdict': None}
    state = contained_process.inspect(output/'contained')
    if (output/'result.json').exists() and state['all_processes_closed']:
        return load(output/'result.json')
    return {**state, 'reason': 'whole_group_live' if not state['all_processes_closed'] else 'result_not_committed'}


def execute(manifest, arguments, working_directory, output, maximum_wall_seconds,
            cancel_file=None, *, memory_bytes, tasks, cooperative_capture=False, managed_reservation=None,
            on_started=None, monitor=None):
    require(type(arguments) is list and all(type(a) is str and '\0' not in a for a in arguments),
            'invalid_process_arguments')
    require(type(cooperative_capture) is bool and all(a.split('=', 1)[0] != '--timelearner-capture-directory'
            for a in arguments), 'capture_directory_is_supervisor_owned')
    validate_limits(memory_bytes, tasks, maximum_wall_seconds, wall_reason='invalid_contained_wall_budget')
    require((on_started is None or callable(on_started)) and (monitor is None or callable(monitor)),
            'contained_callback_not_callable')
    executable = verify_runtime(manifest)
    cwd = Path(working_directory).resolve(strict=True)
    require(cwd.is_dir(), 'invalid_process_working_directory')
    output = Path(output).resolve()
    cancel = Path(cancel_file).resolve() if cancel_file is not None else output/'cancel.request'
    require(not cancel.exists(), 'cancellation_request_already_exists')
    # Explicitly reproduce the loader environment declared in the runtime.
    for key in ('LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM'):
        require(os.environ.get(key) == manifest['loader_environment'].get(key), 'loader_environment_changed:'+key)
    output.mkdir(parents=True, exist_ok=False)
    _write(output/'runtime.json', manifest)
    _write(output/'request.json', {'arguments': arguments, 'working_directory': str(cwd),
           'maximum_wall_seconds': maximum_wall_seconds, 'cancel_file': str(cancel),
           'memory_bytes': memory_bytes, 'tasks': tasks, 'cooperative_capture': cooperative_capture})
    args = list(arguments)
    if cooperative_capture:
        args.extend(['--timelearner-capture-directory', str(output)])
    environment = {key: os.environ[key] for key in
                   ('ASAN_OPTIONS', 'TIMELEARNER_EXECUTION_OUTPUT', 'TIMELEARNER_COMPOSITE_OUTPUT')
                   if key in os.environ}
    begin = time.monotonic()
    outcome, reason, mappings, mapping_error = 'process_error', 'launch_not_completed', None, None
    provenance, closure, last, binding = 'invalid_or_incomplete_runtime', None, None, None
    try:
        binding = contained_process.start(manifest, args, cwd, output/'contained', memory_bytes=memory_bytes,
                  tasks=tasks, maximum_wall_seconds=maximum_wall_seconds, environment=environment,
                  managed_reservation=managed_reservation)
        _write(output/'owned-process.json', {'pid': binding['initial_main_pid'],
               'start_ticks': binding['initial_start_ticks'],
               'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
               'executable': str(executable), 'executable_sha256': manifest['executable']['sha256'],
               'runtime_fingerprint': manifest['runtime_fingerprint'], 'unit': binding['unit'],
               'invocation_id': binding['invocation_id'], 'control_group': binding['control_group']})
        if on_started is not None:
            on_started(binding)
        capture_attempted = False
        while True:
            last = contained_process.inspect(output/'contained')
            if monitor is not None:
                monitor(last)
            if last['all_processes_closed']:
                state, returncode = last['state'], _returncode(last['state'])
                if state.get('Result') == 'timeout':
                    outcome, reason = 'timeout', 'contained_runtime_budget_exhausted'
                elif state.get('Result') == 'success' and returncode == 0:
                    outcome, reason = 'completed', 'exit_zero_and_whole_group_closed'
                else:
                    outcome, reason = 'process_error', 'nonzero_exit_or_missing_terminal_status'
                break
            if last['state'].get('MainPID') == '0' and not (output/'main-exited-with-live-descendants.json').exists():
                _write(output/'main-exited-with-live-descendants.json', last)
            if cancel.exists():
                outcome, reason = 'interrupted', 'cancellation_request'
                break
            if time.monotonic()-begin >= maximum_wall_seconds:
                outcome, reason = 'timeout', 'wall_budget_exhausted'
                break
            if not capture_attempted:
                pid = binding['initial_main_pid']
                try:
                    same = (_start_identity(pid) == binding['initial_start_ticks'] and
                            Path('/proc', str(pid), 'exe').resolve(strict=True) == executable)
                except (FileNotFoundError, ProcessLookupError):
                    same = False
                ready_path = output/'capture-ready.json'
                if same and (not cooperative_capture or ready_path.exists()):
                    if cooperative_capture:
                        ready = load(ready_path)
                        require(type(ready) is dict and type(ready.get('schema_version')) is int and
                                type(ready.get('pid')) is int and ready == {
                                    'kind': 'native_runtime_capture_ready', 'schema_version': 1,
                                    'pid': pid, 'start_ticks': binding['initial_start_ticks']},
                                'cooperative_capture_identity_changed')
                    capture_attempted = True
                    try:
                        mappings = loaded_process_files(pid, executable)
                        _write(output/'loaded-files.json', mappings)
                        if cooperative_capture:
                            _write(output/'capture-ack.json', {'kind': 'native_runtime_capture_ack',
                                   'schema_version': 1, 'pid': pid, 'start_ticks': binding['initial_start_ticks']})
                    except (FileNotFoundError, ProcessLookupError) as error:
                        mapping_error = str(error)
                    except RuntimeError as error:
                        # The main process can exit between reading /proc/exe
                        # and /proc/maps while a descendant remains alive.
                        # Missing capture is not permission to finish or to
                        # stop observing that descendant. Other mapping errors
                        # retain the strict invalid-runtime path.
                        if str(error) != 'no executable mappings found':
                            raise
                        mapping_error = str(error)
            time.sleep(.02)
        _write(output/'terminal-unit-state.json', last)
        verify_runtime(manifest)
        provenance = 'loaded_files_captured' if mappings is not None else 'incomplete_loaded_files'
        if cooperative_capture and mappings is None and mapping_error is None:
            mapping_error = 'cooperative_capture_not_ready'
    except Exception as error:
        outcome, reason, provenance = 'process_error', str(error), 'invalid_or_incomplete_runtime'
    finally:
        if (output/'contained/request.json').exists():
            try:
                closure = contained_process.stop(output/'contained')
                _write(output/'whole-group-closure.json', closure)
            except Exception as error:
                outcome, reason, provenance = 'process_error', 'whole_group_closure_unproven:'+str(error), 'invalid_or_incomplete_runtime'
                _write(output/'closure-error.json', {'reason': str(error), 'scientific_verdict': None})
    closed = closure is not None and closure['all_processes_closed'] is True
    if not closed:
        outcome, provenance = 'process_error', 'invalid_or_incomplete_runtime'
    for name in ('stdout.log', 'stderr.log'):
        source = output/'contained'/name
        if closed and source.is_file():
            shutil.copyfile(source, output/name)
    final_state = last['state'] if last else closure['state'] if closure else {}
    result = {'kind': 'timelearner_process_result', 'schema_version': 2, 'execution': outcome, 'reason': reason,
              'returncode': _returncode(final_state), 'wall_seconds': time.monotonic()-begin, 'model_time': None,
              'runtime_provenance': provenance, 'mapping_error': mapping_error,
              'runtime_fingerprint': manifest['runtime_fingerprint'], 'ownership_scope': 'bound_cgroup',
              'all_processes_closed': closed, 'scientific_verdict': None}
    result['operational_diagnostics'] = inspect_streams(output)
    _write(output/'result.json', result)
    return result
