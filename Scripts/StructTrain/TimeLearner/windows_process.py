"""Owned Windows child jobs with limits established before native execution.

This backend records observed DLLs, not a lifetime loader closure. It does not
provide Linux cgroups, thread limits, or scientific-worker admission.
"""
import ctypes as C
import math
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid

from .native_evidence import load, require
from .native_calibration_worker import _write
from .process_runner import verify_runtime
from .runtime import file_record, source_closure


class ModuleInventoryError(OSError):
    """A failed actual PSAPI snapshot, including its partial paths for diagnosis."""
    def __init__(self, operation, winerror, *, module=None, paths=(), returned=None):
        self.record = {'operation': operation, 'winerror': winerror,
                       'module_base': hex(module) if module is not None else None,
                       'partial_paths': [str(p) for p in paths], 'returned_characters': returned}
        super().__init__(winerror, 'windows_module_inventory_failed:'+operation)


def _module_error(error, phase):
    return {'phase': phase, 'detail': getattr(error, 'record', None),
            'reason': str(error), 'exception': type(error).__name__}


class _Windows:
    def __init__(self):
        require(os.name == 'nt', 'windows_worker_required')
        from ctypes import wintypes as W
        self.W = W
        S = C.c_size_t

        class Basic(C.Structure):
            _fields_ = [('process_time', C.c_longlong), ('job_time', C.c_longlong),
                        ('flags', W.DWORD), ('minimum_working_set', S), ('maximum_working_set', S),
                        ('processes', W.DWORD), ('affinity', S), ('priority', W.DWORD), ('scheduling', W.DWORD)]

        class IO(C.Structure):
            _fields_ = [(name, C.c_ulonglong) for name in ('read_operations', 'write_operations',
                        'other_operations', 'read_bytes', 'write_bytes', 'other_bytes')]

        class Limits(C.Structure):
            _fields_ = [('basic', Basic), ('io', IO), ('process_memory', S), ('job_memory', S),
                        ('peak_process_memory', S), ('peak_job_memory', S)]

        class Startup(C.Structure):
            _fields_ = [('cb', W.DWORD), ('reserved', W.LPWSTR), ('desktop', W.LPWSTR), ('title', W.LPWSTR),
                        *[(name, W.DWORD) for name in ('x', 'y', 'width', 'height', 'columns', 'rows', 'fill', 'flags')],
                        ('show', W.WORD), ('reserved_bytes', W.WORD), ('reserved_pointer', C.POINTER(W.BYTE)),
                        ('stdin', W.HANDLE), ('stdout', W.HANDLE), ('stderr', W.HANDLE)]

        class Process(C.Structure):
            _fields_ = [('process', W.HANDLE), ('thread', W.HANDLE), ('pid', W.DWORD), ('tid', W.DWORD)]

        class Memory(C.Structure):
            _fields_ = [('length', W.DWORD), ('load', W.DWORD), *[(name, C.c_ulonglong) for name in
                        ('total_physical', 'available_physical', 'total_page', 'available_page',
                         'total_virtual', 'available_virtual', 'available_extended')]]

        self.Limits, self.Startup, self.Process, self.Memory = Limits, Startup, Process, Memory
        require(C.sizeof(C.c_void_p) == 8 and C.sizeof(Limits) == 144 and
                C.sizeof(Startup) == 104 and C.sizeof(Process) == 24 and C.sizeof(Memory) == 64,
                'unsupported_windows_process_abi')
        k = C.WinDLL('kernel32', use_last_error=True);p = C.WinDLL('psapi', use_last_error=True)

        def bind(dll, name, result, *arguments):
            f = getattr(dll, name);f.restype = result;f.argtypes = arguments;return f

        self.create_job = bind(k, 'CreateJobObjectW', W.HANDLE, W.LPVOID, W.LPCWSTR)
        self.set_job = bind(k, 'SetInformationJobObject', W.BOOL, W.HANDLE, C.c_int, W.LPVOID, W.DWORD)
        self.query_job = bind(k, 'QueryInformationJobObject', W.BOOL, W.HANDLE, C.c_int, W.LPVOID, W.DWORD, C.POINTER(W.DWORD))
        self.assign = bind(k, 'AssignProcessToJobObject', W.BOOL, W.HANDLE, W.HANDLE)
        self.in_job = bind(k, 'IsProcessInJob', W.BOOL, W.HANDLE, W.HANDLE, C.POINTER(W.BOOL))
        self.create_process = bind(k, 'CreateProcessW', W.BOOL, W.LPCWSTR, W.LPWSTR, W.LPVOID, W.LPVOID,
                                   W.BOOL, W.DWORD, W.LPVOID, W.LPCWSTR, C.POINTER(Startup), C.POINTER(Process))
        self.resume = bind(k, 'ResumeThread', W.DWORD, W.HANDLE)
        self.exit_code = bind(k, 'GetExitCodeProcess', W.BOOL, W.HANDLE, C.POINTER(W.DWORD))
        self.terminate_job = bind(k, 'TerminateJobObject', W.BOOL, W.HANDLE, W.UINT)
        self.terminate_process = bind(k, 'TerminateProcess', W.BOOL, W.HANDLE, W.UINT)
        self.wait = bind(k, 'WaitForSingleObject', W.DWORD, W.HANDLE, W.DWORD)
        self.close = bind(k, 'CloseHandle', W.BOOL, W.HANDLE)
        self.memory_status = bind(k, 'GlobalMemoryStatusEx', W.BOOL, C.POINTER(Memory))
        self.image_name = bind(k, 'QueryFullProcessImageNameW', W.BOOL, W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD))
        self.process_times = bind(k, 'GetProcessTimes', W.BOOL, W.HANDLE, *([C.POINTER(W.FILETIME)]*4))
        self.enum_modules = bind(p, 'EnumProcessModulesEx', W.BOOL, W.HANDLE, C.POINTER(W.HMODULE), W.DWORD, C.POINTER(W.DWORD), W.DWORD)
        self.module_name = bind(p, 'GetModuleFileNameExW', W.DWORD, W.HANDLE, W.HMODULE, W.LPWSTR, W.DWORD)

    @staticmethod
    def check(value):
        if not value:raise C.WinError(C.get_last_error())

    def limits(self, job):
        value = self.Limits();self.check(self.query_job(job, 9, C.byref(value), C.sizeof(value), None))
        return {'flags': int(value.basic.flags), 'memory_bytes': int(value.job_memory),
                'maximum_processes': int(value.basic.processes), 'peak_job_memory_bytes': int(value.peak_job_memory)}

    def running(self, process):
        state = self.wait(process, 0)
        if state == 0:return False
        if state == 258:return True
        self.check(False)

    def pids(self, job):
        for capacity in (16, 64, 256):
            data = C.create_string_buffer(8+capacity*C.sizeof(C.c_size_t));needed = self.W.DWORD()
            if not self.query_job(job, 3, data, C.sizeof(data), C.byref(needed)):
                if C.get_last_error() == 234:continue
                self.check(False)
            assigned, present = (self.W.DWORD*2).from_buffer(data)
            require(present <= capacity and present == assigned, 'incomplete_windows_job_membership')
            return list((C.c_size_t*present).from_buffer(data, 8))
        raise RuntimeError('windows_job_membership_too_large')

    def identity(self, process):
        path = C.create_unicode_buffer(32768);size = self.W.DWORD(len(path))
        self.check(self.image_name(process, 0, path, C.byref(size)))
        times = [self.W.FILETIME() for _ in range(4)]
        self.check(self.process_times(process, *[C.byref(t) for t in times]))
        created = (int(times[0].dwHighDateTime)<<32)|int(times[0].dwLowDateTime)
        return {'executable': str(Path(path.value).resolve(strict=True)), 'creation_filetime': str(created)}

    def modules(self, process):
        modules = (self.W.HMODULE*2048)();needed = self.W.DWORD()
        C.set_last_error(0)
        if not self.enum_modules(process, modules, C.sizeof(modules), C.byref(needed), 3):
            raise ModuleInventoryError('EnumProcessModulesEx', C.get_last_error())
        require(needed.value <= C.sizeof(modules) and needed.value % C.sizeof(self.W.HMODULE) == 0,
                'windows_module_inventory_truncated')
        result = []
        for module in modules[:needed.value//C.sizeof(self.W.HMODULE)]:
            path = C.create_unicode_buffer(32768)
            C.set_last_error(0)
            returned = self.module_name(process, module, path, len(path))
            error = C.get_last_error()
            if not 0 < returned < len(path):
                raise ModuleInventoryError('GetModuleFileNameExW', error,
                                           module=module, paths=result, returned=int(returned))
            result.append(Path(path.value).resolve(strict=True))
        return result


def execute(manifest, arguments, working_directory, output, *, memory_bytes, maximum_processes,
            maximum_wall_seconds, lock_file, cancel_file=None, cooperative_capture=False):
    """Run one immutable native runtime in an owned, memory-limited Windows job.

    A host lock serializes this backend's workers. It does not reserve resources
    against unrelated applications. Process count is not a thread-count limit.
    """
    require(type(memory_bytes) is int and 32*1024**2 <= memory_bytes <= 64*1024**3, 'invalid_windows_memory_budget')
    require(type(maximum_processes) is int and 1 <= maximum_processes <= 64, 'invalid_windows_process_budget')
    require(type(maximum_wall_seconds) in (int, float) and math.isfinite(maximum_wall_seconds) and
            .1 <= maximum_wall_seconds <= 86400, 'invalid_windows_wall_budget')
    require(type(arguments) is list and all(type(s) is str and '\x00' not in s for s in arguments), 'invalid_windows_arguments')
    require(type(cooperative_capture) is bool and all(a.split('=', 1)[0] != '--timelearner-capture-directory'
            for a in arguments), 'capture_directory_is_supervisor_owned')
    api = _Windows();exe = verify_runtime(manifest);cwd = Path(working_directory).resolve(strict=True)
    backend = file_record(Path(__file__))
    require(manifest.get('windows_backend') == backend and
            manifest['build_flags'].get('windows_backend_sha256') == backend['sha256'],
            'windows_backend_changed')
    for key in ('PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM'):
        require(os.environ.get(key) == manifest['loader_environment'].get(key), 'windows_loader_environment_changed:'+key)
    require(cwd.is_dir(), 'invalid_windows_working_directory')
    source = Path(manifest['windows_source_root']).resolve(strict=True)
    output = Path(output).resolve();require(not output.exists() and not output.is_relative_to(source) and
            not output.is_relative_to(exe.parent), 'windows_output_overlaps_runtime_or_source')
    output.mkdir(parents=True, exist_ok=False)
    arguments = list(arguments)
    if cooperative_capture:arguments.extend(['--timelearner-capture-directory', str(output)])
    lock_file = Path(lock_file).resolve();lock_file.parent.mkdir(parents=True, exist_ok=True)
    require(lock_file.suffix == '.lock' and not lock_file.is_relative_to(source) and
            not lock_file.is_relative_to(exe.parent) and not lock_file.is_relative_to(output),
            'windows_worker_lock_overlaps_inputs')
    import msvcrt
    lock = lock_file.open('a+b');lock.seek(0)
    if lock_file.stat().st_size == 0:lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:lock.close();raise RuntimeError('windows_worker_already_reserved')
    job = None;process = api.Process();assigned = False;resumed = False;observed = {};module_errors = [];captured = False
    result = {'kind': 'timelearner_windows_process_result', 'schema_version': 1,
              'execution': 'process_error', 'validity': 'incomplete', 'reason': 'not_started',
              'returncode': None, 'scientific_verdict': None, 'thread_limit_enforced': False,
              'memory_limit_semantics': 'job_committed_virtual_memory',
              'wall_budget_scope': 'whole_attempt_including_preparation'}
    start = time.monotonic();name = 'Local\\TimeLearner-'+str(uuid.uuid4())
    try:
        require(source_closure(source) == manifest['source_closure'], 'windows_source_context_changed')
        status = api.Memory();status.length = C.sizeof(status);api.check(api.memory_status(C.byref(status)))
        require(status.available_physical >= memory_bytes+256*1024**2, 'insufficient_windows_available_memory')
        require(shutil.disk_usage(output).free >= 1024**3, 'insufficient_windows_disk_space')
        _write(output/'resource-preflight.json', {'available_physical_bytes': int(status.available_physical),
               'total_physical_bytes': int(status.total_physical), 'memory_budget_bytes': memory_bytes})
        _write(output/'request.json', {'runtime': manifest, 'arguments': arguments, 'working_directory': str(cwd),
               'memory_bytes': memory_bytes, 'maximum_processes': maximum_processes, 'maximum_wall_seconds': maximum_wall_seconds,
               'job_name': name, 'cancel_file': str(cancel_file) if cancel_file else None})
        job = api.create_job(None, name);api.check(job)
        limits = api.Limits();limits.basic.flags = 0x2000|0x200|0x8
        limits.basic.processes = maximum_processes;limits.job_memory = memory_bytes
        api.check(api.set_job(job, 9, C.byref(limits), C.sizeof(limits)))
        actual = api.limits(job)
        require(actual['flags'] == limits.basic.flags and actual['memory_bytes'] == memory_bytes and
                actual['maximum_processes'] == maximum_processes, 'windows_job_limits_not_applied')
        _write(output/'limits-before-exec.json', actual)
        if cancel_file and Path(cancel_file).exists():
            result.update(execution='cancelled', validity='not_executed', reason='cancelled_before_start',
                          all_processes_closed=True, runtime_provenance='not_started')
            return result
        if time.monotonic()-start >= maximum_wall_seconds:
            result.update(execution='timeout', validity='not_executed', reason='timeout_before_start',
                          all_processes_closed=True, runtime_provenance='not_started')
            return result
        with open(os.devnull, 'rb') as stdin, (output/'stdout.log').open('xb') as stdout, (output/'stderr.log').open('xb') as stderr:
            startup = api.Startup();startup.cb = C.sizeof(startup);startup.flags = 0x100
            for field, stream in [('stdin', stdin), ('stdout', stdout), ('stderr', stderr)]:
                handle = msvcrt.get_osfhandle(stream.fileno());os.set_handle_inheritable(handle, True);setattr(startup, field, handle)
            command = C.create_unicode_buffer(subprocess.list2cmdline([str(exe), *arguments]))
            api.check(api.create_process(str(exe), command, None, None, True, 0x4|0x08000000,
                                        None, str(cwd), C.byref(startup), C.byref(process)))
            api.check(api.assign(job, process.process));assigned = True
            belongs = api.W.BOOL();api.check(api.in_job(process.process, job, C.byref(belongs)));require(bool(belongs.value), 'windows_child_not_in_owned_job')
            identity = api.identity(process.process)
            require(os.path.samefile(identity['executable'], exe), 'windows_child_image_mismatch')
            _write(output/'owned-process.json', {**identity, 'pid': int(process.pid), 'job_name': name,
                    'runtime_fingerprint': manifest['runtime_fingerprint'], 'suspended_until_limits_applied': True})
            require(api.resume(process.thread) != 0xffffffff, 'windows_child_resume_failed');resumed = True
            api.close(process.thread);process.thread = None
            stop_reason = None;code = api.W.DWORD()
            while True:
                if not api.running(process.process):break
                if cancel_file and Path(cancel_file).exists():stop_reason = 'cancelled'
                elif time.monotonic()-start >= maximum_wall_seconds:stop_reason = 'timeout'
                if stop_reason:
                    api.check(api.terminate_job(job, 1460));break
                try:
                    for path in api.modules(process.process):
                        key = os.path.normcase(str(path))
                        if key not in observed:observed[key] = file_record(path)
                except (OSError, RuntimeError) as error:
                    if len(module_errors) < 8:module_errors.append(_module_error(error, 'poll'))
                if cooperative_capture and not captured and (output/'capture-ready.json').exists():
                    expected = {'kind': 'native_runtime_capture_ready', 'schema_version': 2,
                                'pid': int(process.pid), 'creation_filetime': identity['creation_filetime']}
                    ready = load(output/'capture-ready.json')
                    require(type(ready.get('pid')) is int and type(ready.get('schema_version')) is int and
                            ready == expected and api.identity(process.process) == identity,
                            'windows_cooperative_capture_identity_changed')
                    try:
                        boundary = [file_record(p) for p in api.modules(process.process)]
                    except (OSError, RuntimeError) as error:
                        module_errors.append(_module_error(error, 'cooperative_boundary'))
                        raise
                    require(any(os.path.samefile(p['path'], exe) for p in boundary),
                            'windows_capture_boundary_executable_missing')
                    require(api.running(process.process) and api.identity(process.process) == identity,
                            'windows_capture_boundary_process_changed')
                    _write(output/'boundary-loaded-files.json', boundary)
                    for record in boundary:observed[os.path.normcase(record['path'])] = record
                    ack = {**expected, 'kind': 'native_runtime_capture_ack'}
                    temporary = output/'capture-ack.pending.json';_write(temporary, ack)
                    temporary.rename(output/'capture-ack.json');captured = True
                time.sleep(.05)
            if api.wait(process.process, 10000) != 0:raise RuntimeError('windows_owned_process_not_closed')
            api.check(api.exit_code(process.process, C.byref(code)))
            remaining = api.pids(job)
            result['descendants_at_main_exit'] = remaining
            if remaining:
                api.check(api.terminate_job(job, 1460));stop_reason = stop_reason or 'descendants_remaining'
                deadline = time.monotonic()+10
                while api.pids(job) and time.monotonic() < deadline:time.sleep(.05)
            closed = not api.pids(job);require(closed, 'windows_owned_job_not_closed')
            result.update(execution=stop_reason or ('completed' if code.value == 0 else 'process_error'),
                          reason=stop_reason or ('exit_zero' if code.value == 0 else 'nonzero_exit'),
                          returncode=int(code.value), all_processes_closed=True)
            _write(output/'limits-after.json', api.limits(job));_write(output/'loaded-files.json', list(observed.values()))
            _write(output/'module-observation-errors.json', module_errors)
            for record in observed.values():
                require(file_record(Path(record['path'])) == record, 'windows_loaded_file_changed')
            verify_runtime(manifest)
            require(file_record(Path(__file__)) == backend, 'windows_backend_changed')
            require(source_closure(source) == manifest['source_closure'], 'windows_source_context_changed')
            result['cooperative_capture'] = 'completed' if captured else ('not_ready' if cooperative_capture else 'not_requested')
            if cooperative_capture and not captured:
                result.update(validity='provenance_missing', reason='windows_cooperative_capture_not_ready',
                              runtime_provenance='not_captured')
                return result
            if os.path.normcase(str(exe)) not in observed:
                result.update(validity='provenance_missing', reason='windows_executable_mapping_not_observed',
                              runtime_provenance='not_captured')
                return result
            result.update(execution=stop_reason or ('completed' if code.value == 0 else 'process_error'),
                          validity='valid', reason=stop_reason or ('exit_zero' if code.value == 0 else 'nonzero_exit'),
                          returncode=int(code.value), runtime_provenance='loaded_files_captured',
                          all_processes_closed=True, observed_module_files=len(observed))
    except BaseException as error:
        result.update(reason=str(error), validity='invalid_or_incomplete')
    finally:
        if process.process:
            if api.running(process.process):
                if assigned:api.terminate_job(job, 1460)
                else:api.terminate_process(process.process, 1460)
                api.wait(process.process, 10000)
            if process.thread:api.close(process.thread)
            api.close(process.process)
        if job:
            if assigned and api.pids(job):api.terminate_job(job, 1460)
            deadline = time.monotonic()+10
            while api.pids(job) and time.monotonic() < deadline:time.sleep(.05)
            result['all_processes_closed'] = not api.pids(job)
            api.close(job)
        # Diagnostics must not delay owned-process cleanup if storage fails.
        # Partial observations never replace a successful boundary capture.
        _write(output/'partial-loaded-files.json', list(observed.values()))
        _write(output/'module-observation-errors.json', module_errors)
        result.update(wall_seconds=time.monotonic()-start, child_resumed=resumed, job_name=name)
        _write(output/'result.json', result)
        lock.seek(0);msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1);lock.close()
    return result
