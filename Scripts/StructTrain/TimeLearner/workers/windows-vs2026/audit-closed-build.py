"""Verify existing closed Windows build outputs without changing its outcome.

This metadata operation runs no compiled model or test and admits no worker.
The original build and its terminal/result files remain read-only.
"""
import argparse
import ctypes as C
from ctypes import wintypes as W
import gzip
import hashlib
import importlib.util
import json
import msvcrt
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
BASE = Path('C:/Projects/TimeLearnerWorker')


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def private_path(value):
    path = Path(value).absolute()
    require(path != BASE and path.is_relative_to(BASE), 'outside_private_workspace')
    require(not any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)), 'reparse_path')
    return path.resolve(strict=False)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(source, *arguments):
    return subprocess.check_output(['git', '-C', str(source), *arguments], timeout=60,
        env=dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_NO_LAZY_FETCH='1'),
        creationflags=0x08000000).decode('utf-8').strip()


def emit(output, name, value):
    raw = (json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':'))+'\n').encode()
    if name.endswith('.gz'):
        with (output/name).open('xb') as target:
            with gzip.GzipFile(filename='', mode='wb', fileobj=target, mtime=0) as stream:
                stream.write(raw)
    else:
        with (output/name).open('xb') as target:
            target.write(raw)


def verify_original_kernel(owned):
    kernel = C.WinDLL('kernel32', use_last_error=True)
    open_job = kernel.OpenJobObjectW
    open_job.argtypes = [W.DWORD, W.BOOL, W.LPCWSTR];open_job.restype = W.HANDLE
    close = kernel.CloseHandle;close.argtypes = [W.HANDLE];close.restype = W.BOOL
    handle = open_job(4, False, owned['job_name'])
    error = C.get_last_error()
    if handle:
        close(handle)
        raise RuntimeError('original_named_job_still_exists')
    require(error == 2, 'original_job_absence_unproven:'+str(error))
    open_process = kernel.OpenProcess
    open_process.argtypes = [W.DWORD, W.BOOL, W.DWORD];open_process.restype = W.HANDLE
    handle = open_process(0x1000, False, owned['pid'])
    error = C.get_last_error();reused = False
    if handle:
        try:
            times = [W.FILETIME() for _ in range(4)]
            get_times = kernel.GetProcessTimes
            get_times.argtypes = [W.HANDLE, *([C.POINTER(W.FILETIME)]*4)];get_times.restype = W.BOOL
            require(get_times(handle, *[C.byref(t) for t in times]), 'original_process_time_unavailable')
            creation = str((int(times[0].dwHighDateTime)<<32)|int(times[0].dwLowDateTime))
            require(creation != owned['creation_filetime'], 'original_owned_process_still_exists')
            reused = True
        finally:
            close(handle)
    else:
        require(error == 87, 'original_process_absence_unproven:'+str(error))
    return {'original_named_job_absent': True, 'original_main_absent': True, 'pid_reused': reused}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--specification', required=True, type=Path)
    args = parser.parse_args()
    require(os.name == 'nt' and __debug__, 'normal_windows_python_required')
    specification = private_path(args.specification)
    spec = json.loads(specification.read_bytes())
    require(spec['kind'] == 'timelearner_closed_windows_build_audit' and
            type(spec['schema_version']) is int and spec['schema_version'] == 1, 'unknown_audit_specification')
    require(digest(Path(__file__)) == spec['worker_sha256'], 'audit_worker_bytes_differ')
    source, original, runtime, dependencies, output = [private_path(spec[key]) for key in
        ('source_root', 'original_build_output', 'runtime_root', 'installed_dependencies', 'output_root')]
    paths = [source, original, runtime, dependencies, output]
    require(len(set(paths)) == 5 and all(a == b or not a.is_relative_to(b) for a in paths for b in paths), 'overlapping_audit_paths')
    require(not output.exists(), 'fresh_audit_output_required')
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic();passed = False;lock = None
    try:
        emit(output, 'specification.json', spec)
        (output/'producer.py').write_bytes(Path(__file__).read_bytes())
        lock_path = private_path(BASE/'locks/worker.lock')
        lock = lock_path.open('a+b');lock.seek(0)
        if lock_path.stat().st_size == 0:
            lock.write(b'0');lock.flush();lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        def guard():
            require(time.monotonic()-started < 1800, 'audit_wall_budget')
        originals = {}
        for name, expected in spec['original_records'].items():
            path = original/name
            require(path.resolve(strict=True).is_relative_to(original) and
                    not any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)), 'invalid_original_record')
            require(digest(path) == expected, 'original_record_changed:'+name)
            originals[name] = expected
        terminal = json.loads((original/'terminal.json').read_bytes())
        result = json.loads((original/'build-result.json').read_bytes())
        require(terminal['build_accepted'] is False and result['returncode'] == 0 and
                result['validity'] == 'valid' and result['all_processes_closed'] is True and
                result['execution'] == 'descendants_remaining', 'unexpected_original_build_outcome')
        emit(output, 'kernel-before.json', verify_original_kernel(json.loads((original/'build-process/owned-process.json').read_bytes())))
        require(git(source, 'rev-parse', 'HEAD') == spec['source_commit'], 'source_head_changed')
        namespace = json.loads(git(source, 'cat-file', 'blob', spec['namespace_git_blob']))
        require(len(namespace) == spec['expected_source_files'], 'namespace_count_changed')
        for name, record in namespace.items():
            path = private_path(source/name)
            require(path.is_relative_to(source) and path.is_file() and path.stat().st_size == record['bytes'] and
                    digest(path) == record['sha256'], 'source_file_changed:'+name)
            guard()
        # Reuse the exact original production inventory/checking paths, after
        # verifying all source bytes; do not copy their implementation here.
        sys.path.insert(0, str(source))
        from Scripts.StructTrain.TimeLearner.runtime import source_closure, file_record
        module_spec = importlib.util.spec_from_file_location('original_sdk_build', source/'Scripts/StructTrain/TimeLearner/workers/windows-vs2026/sdk-build.py')
        helper = importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(helper)
        closure_before = source_closure(source)
        require(closure_before == json.loads((original/'source-before.json').read_bytes()), 'original_source_closure_changed')
        with gzip.open(original/'dependencies-before.json.gz', 'rb') as stream:
            dependency_before = json.load(stream)
        dependency_after = helper.inventory(dependencies);guard()
        emit(output, 'dependencies-after.json.gz', dependency_after)
        require(dependency_after == dependency_before, 'shared_dependencies_changed')
        tools = json.loads((original/'tools-before.json').read_bytes())
        require({name:file_record(Path(name)) for name in tools} == tools, 'compiler_tools_changed')
        runtime_before = helper.inventory(runtime);guard()
        for name, expected in spec['expected_targets'].items():
            target = private_path(runtime/name)
            require(target.parent == runtime and digest(target) == expected, 'target_changed:'+name)
            with target.open('rb') as stream:
                require(stream.read(2) == b'MZ', 'target_not_PE:'+name)
        emit(output, 'runtime-files.json.gz', runtime_before)
        require(helper.inventory(runtime) == runtime_before, 'runtime_changed_during_audit')
        require(source_closure(source) == closure_before, 'source_changed_during_audit')
        require(all(digest(original/name) == expected for name, expected in originals.items()), 'original_records_changed_during_audit')
        emit(output, 'kernel-after.json', verify_original_kernel(json.loads((original/'build-process/owned-process.json').read_bytes())))
        emit(output, 'audit.json', {'source_commit': spec['source_commit'], 'source_closure': closure_before,
            'verified_source_files': len(namespace), 'dependency_files': len(dependency_after), 'runtime_files': len(runtime_before),
            'targets': {name:file_record(runtime/name) for name in spec['expected_targets']},
            'original_execution': result['execution'], 'original_build_accepted': False,
            'compiled_tests_executed': False, 'scientific_worker_admitted': False, 'scientific_verdict': None})
        guard();passed = True
    except BaseException as error:
        emit(output, 'exception.json', {'reason': str(error), 'traceback': traceback.format_exc()})
    finally:
        if lock is not None:
            lock.close()
        emit(output, 'terminal.json', {'audit_passed': passed, 'wall_seconds': time.monotonic()-started,
            'original_build_outcome_unchanged': True, 'compiled_tests_executed': False,
            'scientific_worker_admitted': False, 'scientific_verdict': None})
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
