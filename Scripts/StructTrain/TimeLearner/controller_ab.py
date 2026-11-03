"""Compile original pure controller sources at two Git closures on a worker.

This is a decision-kernel gate, not a native Rdk integration or scientific gate.
No checkout, source-tree write, function extraction or shared build is used.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import time

from .native_calibration_worker import _write
from .native_evidence import load, require
from .native_gate import audit_junit
from .runtime import file_record, parse_ldd


def _git(repository, *arguments):
    return subprocess.check_output(['git', '-C', str(repository), *arguments], timeout=120)


def _blob(repository, revision, name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and '..' not in path.parts and str(path) == name,
            'invalid_controller_ab_source_path')
    entry = _git(repository, 'ls-tree', revision, '--', name).decode().split()
    require(len(entry) == 4 and entry[0] == '100644' and entry[1] == 'blob' and entry[3] == name,
            'controller_ab_requires_regular_git_source')
    return _git(repository, 'cat-file', 'blob', entry[2])


def _run(arguments, directory, output, wall_seconds, environment):
    """Own the complete compiler/test process group and retain failure output."""
    output.mkdir()
    begin = time.monotonic()
    with (output/'stdout.log').open('xb') as stdout, (output/'stderr.log').open('xb') as stderr:
        child = subprocess.Popen(arguments, cwd=directory, env=environment, stdin=subprocess.DEVNULL,
                                 stdout=stdout, stderr=stderr, start_new_session=True)
        # Keep the process handle open until its group has been terminated and
        # reaped. Never signal a name match, another job or a reused PID.
        identity = Path('/proc', str(child.pid), 'stat').read_text().rsplit(') ', 1)[1].split()[19]
        _write(output/'owned-process.json', {'pid': child.pid, 'start_ticks': identity,
               'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
               'arguments': arguments})
        try:
            child.wait(timeout=wall_seconds)
            execution = 'completed' if child.returncode == 0 else 'process_error'
        except subprocess.TimeoutExpired:
            require(child.poll() is None and os.getpgid(child.pid) == child.pid and
                    Path('/proc', str(child.pid), 'stat').read_text().rsplit(') ', 1)[1].split()[19] == identity,
                    'controller_ab_timeout_owner_changed')
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            execution = 'timeout'
    result = {'execution': execution, 'returncode': child.returncode,
              'wall_seconds': time.monotonic()-begin}
    _write(output/'result.json', result)
    return result


def run_controller_ab(specification, root_repository, pulse_repository, compiler, output):
    require(os.name == 'posix' and Path('/proc/self/stat').exists(), 'controller_ab_requires_linux_worker')
    spec = load(Path(specification).resolve(strict=True))
    require(type(spec) is dict and set(spec) == {'kind', 'schema_version', 'baseline_root', 'candidate_root',
            'production_paths', 'test_paths', 'expected_test_ids', 'compile_wall_seconds', 'test_wall_seconds'} and
            spec['kind'] == 'timelearner_controller_ab' and type(spec['schema_version']) is int and
            spec['schema_version'] == 1, 'unsupported_controller_ab_specification')
    for field in ('baseline_root', 'candidate_root'):
        require(type(spec[field]) is str and re.fullmatch('[0-9a-f]{40}', spec[field]), 'controller_ab_requires_full_sha')
    for field in ('compile_wall_seconds', 'test_wall_seconds'):
        require(type(spec[field]) is int and 0 < spec[field] <= 7200, 'invalid_controller_ab_wall_budget')
    for field in ('production_paths', 'test_paths', 'expected_test_ids'):
        values = spec[field]
        require(type(values) is list and values and all(type(v) is str for v in values) and
                len(values) == len(set(values)), 'invalid_controller_ab_inventory')
    require(all(n.startswith('Core/TimeLearner/') and n.endswith(('.h', '.cpp')) for n in spec['production_paths']) and
            all(n.startswith('Tests/Integration/Libraries/Test_PulseLib_') and n.endswith('.cpp') for n in spec['test_paths']),
            'unsupported_controller_ab_source_scope')
    root_repository, pulse_repository = (Path(p).resolve(strict=True) for p in (root_repository, pulse_repository))
    compiler = Path(compiler).resolve(strict=True)
    output = Path(output).resolve()
    require(not any(output == p or p in output.parents for p in (root_repository, pulse_repository)),
            'controller_ab_output_must_be_outside_sources')
    output.mkdir(parents=True, exist_ok=False)
    _write(output/'specification.json', spec)
    environment = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
    toolchain = {'compiler': file_record(compiler), 'environment': environment,
                 'version': subprocess.check_output([str(compiler), '--version'], env=environment, text=True, timeout=30)}
    libraries = []
    for name in ('libgtest_main.a', 'libgtest.a'):
        value = subprocess.check_output([str(compiler), '-print-file-name='+name], env=environment, text=True, timeout=30).strip()
        path = Path(value).resolve(strict=True)
        libraries.append(path)
    toolchain['gtest_libraries'] = [file_record(p) for p in libraries]
    headers = Path('/usr/include/gtest')
    require(headers.is_dir(), 'controller_ab_system_gtest_headers_missing')
    toolchain['gtest_headers'] = [file_record(p) for p in sorted(headers.rglob('*.h'))]
    _write(output/'toolchain.json', toolchain)
    results, source_maps = {}, {}
    for label in ('baseline', 'candidate'):
        revision = spec[label+'_root']
        require(_git(root_repository, 'rev-parse', revision+'^{commit}').decode().strip() == revision,
                'controller_ab_root_commit_unavailable')
        pulse = _git(root_repository, 'rev-parse', revision+':Libraries/Nmsdk-PulseLib').decode().strip()
        require(_git(pulse_repository, 'rev-parse', pulse+'^{commit}').decode().strip() == pulse,
                'controller_ab_pulselib_commit_unavailable')
        directory = output/label
        directory.mkdir()
        sources = {}
        for name in spec['production_paths']+spec['test_paths']:
            production = name in spec['production_paths']
            data = _blob(pulse_repository if production else root_repository, pulse if production else revision, name)
            destination = directory/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            sources[name] = {'repository': 'PulseLib' if production else 'root',
                             'commit': pulse if production else revision, 'sha256': hashlib.sha256(data).hexdigest()}
        declared = []
        for name in spec['test_paths']:
            declared.extend(a+'/'+b for a, b in re.findall(r'^TEST\(\s*(\w+)\s*,\s*(\w+)\s*\)',
                            (directory/name).read_text(), re.M))
        require(len(declared) == len(set(declared)) and set(declared) == set(spec['expected_test_ids']),
                'controller_ab_test_declaration_mismatch')
        _write(directory/'sources.json', sources)
        source_maps[label] = sources
        binary = directory/'controller-tests'
        args = [str(compiler), '-std=c++20', '-O2', '-g0', '-I'+str(directory/'Core'),
                *[str(directory/n) for n in sources if n.endswith('.cpp')],
                *map(str, libraries), '-pthread', '-o', str(binary)]
        compile_result = _run(args, directory, directory/'compile', spec['compile_wall_seconds'], environment)
        record = {'root': revision, 'pulselib': pulse, 'compile': compile_result,
                  'execution': 'not_started', 'validity': 'not_assessed', 'assertion_status': 'not_assessed'}
        if compile_result['execution'] == 'completed':
            record['executable'] = file_record(binary)
            ldd = subprocess.check_output(['ldd', str(binary)], env=environment, text=True, timeout=30)
            record['resolved_libraries'] = [file_record(p) for p in parse_ldd(ldd)]
            record['actual_loaded_files_captured'] = False
            execution = _run([str(binary), '--gtest_filter='+':'.join(n.replace('/', '.') for n in declared),
                              '--gtest_output=xml:'+str(directory/'junit.xml')], directory,
                             directory/'test', spec['test_wall_seconds'], environment)
            record['test'] = execution
            record['execution'] = execution['execution']
            if execution['execution'] in ('completed', 'process_error') and (directory/'junit.xml').is_file():
                inventory = audit_junit(directory/'junit.xml', declared)
                require((execution['returncode'] == 0) == (inventory['assertion_status'] == 'passed'),
                        'controller_ab_process_junit_disagreement')
                record.update(validity='valid', assertion_status=inventory['assertion_status'], inventory=inventory)
            require(record['executable'] == file_record(binary), 'controller_ab_binary_changed')
        for name, source in sources.items():
            require(hashlib.sha256((directory/name).read_bytes()).hexdigest() == source['sha256'],
                    'controller_ab_materialized_source_changed')
        results[label] = record
        _write(directory/'result.json', record)
    # The corpus itself must be identical: a different test body is not an A/B
    # refactor comparison even when its test ID stayed unchanged.
    require(all(source_maps['baseline'][p]['sha256'] == source_maps['candidate'][p]['sha256']
                for p in spec['test_paths']), 'controller_ab_test_sources_changed')
    for record in [toolchain['compiler'], *toolchain['gtest_libraries'], *toolchain['gtest_headers']]:
        require(record == file_record(Path(record['path'])), 'controller_ab_toolchain_changed')
    passed = all(r['execution'] == 'completed' and r['validity'] == 'valid' and r['assertion_status'] == 'passed'
                 for r in results.values())
    result = {'kind': 'timelearner_controller_ab_result', 'schema_version': 1, 'cases': results,
              'assertion_status': 'passed' if passed else 'failed', 'same_test_sources': True,
              'native_rdk_integration_verified': False, 'operation_trace_equivalence_verified': False,
              'capacitance_search_enabled': False, 'scientific_verdict': None}
    _write(output/'result.json', result)
    return result
