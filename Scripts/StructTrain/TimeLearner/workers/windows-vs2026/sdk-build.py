"""Build a declared private Windows SDK through the existing owned Job backend.

This command does not run scientific models or admit a scientific worker.
All source/configuration inputs are read-only; build, runtime and output are fresh.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

sys.dont_write_bytecode = True
BASE = Path('C:/Projects/TimeLearnerWorker')


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def private_path(value, *, existing=False):
    path = Path(value).absolute()
    require(path.is_relative_to(BASE) and path != BASE, 'path_outside_private_worker')
    require(not any(c in str(path) for c in '%&|<>^!\r\n\x00"'), 'unsafe_batch_path')
    for parent in (path, *path.parents):
        require(not parent.is_symlink() and not parent.is_junction(), 'reparse_path')
    if existing:
        require(path.exists(), 'missing_input:'+str(path))
    return path.resolve(strict=existing)


def git(repository, *arguments):
    return subprocess.check_output(['git', '-C', str(repository), *arguments],
                                   creationflags=0x08000000).decode('utf-8').strip()


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(folder):
    result = {}
    for directory, children, files in os.walk(folder, followlinks=False):
        for name in [*children, *files]:
            path = Path(directory)/name
            require(not path.is_symlink() and not path.is_junction(), 'reparse_inventory_entry')
        for name in files:
            path = Path(directory)/name
            result[path.relative_to(folder).as_posix()] = {
                'bytes': path.stat().st_size, 'sha256': digest(path)}
    return result


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def compressed_inventory(path, value):
    with path.open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as stream:
            stream.write((json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--specification', required=True, type=Path)
    args = parser.parse_args()
    require(os.name == 'nt' and __debug__, 'requires_normal_windows_python')
    spec_path = private_path(args.specification, existing=True)
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    require(spec['kind'] == 'timelearner_private_windows_build' and
            type(spec['schema_version']) is int and spec['schema_version'] == 1, 'unsupported_build_spec')
    source = private_path(spec['source_root'], existing=True)
    dependencies = private_path(spec['installed_dependencies'], existing=True)
    build, runtime, output = [private_path(spec[key]) for key in ('build_root', 'runtime_root', 'output_root')]
    paths = [source, dependencies, build, runtime, output]
    require(all(a == b or not a.is_relative_to(b) for a in paths for b in paths), 'overlapping_build_paths')
    require(len(set(paths)) == len(paths) and all(not p.exists() for p in (build, runtime, output)),
            'fresh_build_runtime_output_required')
    require(digest(Path(__file__)) == spec['worker_sha256'], 'worker_bytes_differ')
    output.mkdir(parents=True, exist_ok=False)
    accepted = False
    try:
        write(output/'specification.json', spec)
        (output/'producer.py').write_bytes(Path(__file__).read_bytes())
        require(git(source, 'rev-parse', 'HEAD') == spec['source_commit'], 'source_head_differs')
        sys.path.insert(0, str(source))
        from Scripts.StructTrain.TimeLearner.runtime import (
            source_closure, file_record, runtime_content_identity, digest_json)
        from Scripts.StructTrain.TimeLearner.windows_process import execute
        import Scripts.StructTrain.TimeLearner.windows_process as backend_module
        closure = source_closure(source)
        write(output/'source-before.json', closure)
        namespace = json.loads(git(source, 'cat-file', 'blob', spec['namespace_git_blob']))
        require(len(namespace) == spec['expected_source_files'], 'source_namespace_count_differs')
        for name, record in namespace.items():
            path = private_path(source/name, existing=True)
            require(path.is_relative_to(source) and path.is_file() and
                    path.stat().st_size == record['bytes'] and digest(path) == record['sha256'],
                    'source_namespace_bytes_differ:'+name)
        physical = set()
        for directory, children, files in os.walk(source, followlinks=False):
            children[:] = [name for name in children if name != '.git']
            for name in [*children, *files]:
                path = Path(directory)/name
                require(not path.is_symlink() and not path.is_junction(), 'source_reparse_entry')
            physical.update((Path(directory)/name).relative_to(source).as_posix()
                            for name in files if name != '.git')
        require(physical == set(namespace), 'source_physical_namespace_differs')
        profile = source/'Scripts/StructTrain/TimeLearner/workers/windows-vs2026'
        for relative, expected in spec['profile_sha256'].items():
            require(digest(profile/relative) == expected, 'profile_bytes_differ:'+relative)
        require(digest(dependencies/'vcpkg/status') == spec['installed_status_sha256'],
                'installed_dependency_status_differs')
        dependency_before = inventory(dependencies)
        compressed_inventory(output/'dependencies-before.json.gz', dependency_before)
        vs = Path(spec['visual_studio_root']).resolve(strict=True)
        vcvars = vs/'VC/Auxiliary/Build/vcvars64.bat'
        devcmd = vs/'Common7/Tools/VsDevCmd.bat'
        cmake = vs/'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
        ninja = vs/'Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe'
        compiler = Path(spec['compiler']).resolve(strict=True)
        for path in (vcvars, devcmd, cmake, ninja, compiler):
            require(path.is_file() and not any(c in str(path) for c in '%&|<>^!\r\n\x00"'), 'invalid_tool_path')
        require(digest(devcmd) == spec['vsdevcmd_sha256'], 'vsdevcmd_bytes_differ')
        require(git(Path('C:/vcpkg'), 'rev-parse', 'HEAD') == spec['vcpkg_commit'], 'vcpkg_head_differs')
        tools_before = {str(path): file_record(path) for path in (vcvars, devcmd, cmake, ninja, compiler)}
        write(output/'tools-before.json', tools_before)
        configure = [str(cmake), '-S', str(source), '-B', str(build), '-G', 'Ninja',
            '-DCMAKE_MAKE_PROGRAM='+str(ninja), '-DCMAKE_CXX_COMPILER='+str(compiler),
            '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake',
            '-DVCPKG_MANIFEST_DIR='+str(profile), '-DVCPKG_OVERLAY_TRIPLETS='+str(profile/'triplets'),
            '-DVCPKG_TARGET_TRIPLET=x64-windows-tl', '-DVCPKG_INSTALLED_DIR='+str(dependencies),
            '-DVCPKG_MANIFEST_INSTALL=OFF', '-DQT_MAJOR=5', '-DRDK_USE_LLM=OFF', '-DRDK_USE_OPENCV=OFF',
            '-DRDK_USE_PYTHON=OFF', '-DRDK_USE_ODESOLVER=OFF', '-DBUILD_TESTING=ON',
            '-DRDK_BUILD_LEGACY_ENGINE_UNIT_TESTS=OFF', '-DNMSDK_BUILD_PARALLEL_JOBS=1',
            '-DNMSDK_DEPLOY_ROOT='+str(runtime), '-DNMSDK_RESOURCE_ROOT='+str(source/'Bin')]
        compile_command = [str(cmake), '--build', str(build), '--target', 'NeuroModelerConsole',
                           'Test_PulseLib_StorageComponents', '--parallel', '1']
        write(output/'commands.json', {'configure': configure, 'build': compile_command,
                                      'dependency_install_disabled': True, 'compiler_jobs': 1})
        batch = output/'build.cmd'
        batch.write_text('\r\n'.join(['@echo off', 'setlocal DisableDelayedExpansion',
            'set VSCMD_SKIP_SENDTELEMETRY=1',
            'call '+subprocess.list2cmdline([str(vcvars)])+' > '+
                subprocess.list2cmdline([str(output/'vcvars.log')])+' 2>&1',
            'if not "%errorlevel%"=="0" exit /b 11', 'set VCPKG_MAX_CONCURRENCY=1',
            'set CMAKE_BUILD_PARALLEL_LEVEL=1', subprocess.list2cmdline(configure),
            'if not "%errorlevel%"=="0" exit /b 12', subprocess.list2cmdline(compile_command),
            'if not "%errorlevel%"=="0" exit /b 13', 'exit /b 0'])+'\r\n', encoding='ascii', newline='')
        backend = file_record(Path(backend_module.__file__))
        manifest = {'schema_version': 2, 'windows_source_root': str(source), 'source_closure': closure,
            'executable': file_record(Path(os.environ['COMSPEC'])), 'app_ini': file_record(batch),
            'compiler': file_record(compiler), 'resolved_libraries': [], 'loaded_process_files': None,
            'windows_backend': backend,
            'build_flags': {'role': 'private_full_sdk_build', 'parallelism': 1, 'ASan': False,
                            'windows_backend_sha256': backend['sha256']},
            'loader_environment': {key: os.environ.get(key) for key in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}}
        manifest['runtime_identity'] = runtime_content_identity(manifest)
        manifest['runtime_fingerprint'] = digest_json(manifest['runtime_identity'])
        write(output/'build-runtime.json', manifest)
        result = execute(manifest, ['/d','/c',str(batch)], BASE, output/'build-process',
            memory_bytes=4*1024**3, maximum_processes=32, maximum_wall_seconds=7200,
            lock_file=BASE/'locks/worker.lock')
        write(output/'build-result.json', result)
        require(result['execution'] == 'completed' and result['validity'] == 'valid' and
                result.get('all_processes_closed') is True, 'owned_build_not_accepted')
        require(source_closure(source) == closure, 'source_changed_after_build')
        dependency_after = inventory(dependencies)
        compressed_inventory(output/'dependencies-after.json.gz', dependency_after)
        require(dependency_after == dependency_before, 'shared_dependencies_changed')
        require({name: file_record(Path(name)) for name in tools_before} == tools_before, 'build_tools_changed')
        cache = (build/'CMakeCache.txt').read_bytes()
        (output/'CMakeCache.txt').write_bytes(cache)
        runtime_files = inventory(runtime)
        compressed_inventory(output/'runtime-files.json.gz', runtime_files)
        for name in ('NeuroModelerConsole.exe','Test_PulseLib_StorageComponents.exe'):
            require(any(Path(relative).name == name for relative in runtime_files), 'built_target_missing:'+name)
        accepted = True
    except BaseException as error:
        write(output/'exception.json', {'reason': str(error), 'traceback': traceback.format_exc()})
    finally:
        write(output/'terminal.json', {'kind': 'timelearner_windows_sdk_build', 'build_accepted': accepted,
            'scientific_models_executed': False, 'scientific_worker_admitted': False, 'scientific_verdict': None})
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
