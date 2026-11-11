"""Compile whole production C++ units before/after; no copied function bodies.

These controlled-observation decision tests do not admit a physical SDK or
claim native cable convergence. Physical Console A/B remains separate.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import unittest

from ..collector_provenance import frozen_digest
from ..native_evidence import load, require
from ..native_gate import audit_junit, _environment
from ..process_runner import execute
from ..runtime import build_flags, digest_json, file_record, resolved_libraries, runtime_content_identity


def _git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args],
        env={**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_OPTIONAL_LOCKS': '0'}).decode().strip()


def _source(root, root_commit, pulse_commit):
    root = Path(root).resolve(strict=True)
    pulse = root/'Libraries/Nmsdk-PulseLib'
    result = {}
    for name, path, commit in [('root', root, root_commit), ('Libraries/Nmsdk-PulseLib', pulse, pulse_commit)]:
        require(_git(path, 'rev-parse', 'HEAD') == commit and
            not _git(path, 'status', '--porcelain', '--untracked-files=all', '--ignore-submodules=all'),
            'decision_cpp_source_commit_or_status')
        inventory = {}
        for line in _git(path, 'ls-files', '--stage').splitlines():
            meta, relative = line.split('\t', 1)
            if meta.split()[0] == '160000':
                continue
            file = path/relative
            if file.is_file():
                inventory[relative] = frozen_digest(file, 32*1024**2)
        result[name] = dict(commit=commit, files=inventory)
    require(_git(root, 'rev-parse', 'HEAD:Libraries/Nmsdk-PulseLib') == pulse_commit,
        'decision_cpp_gitlink_changed')
    return result


def _command(arguments, output, maximum_seconds):
    with output.open('xb') as stream:
        done = subprocess.run(arguments, stdout=stream, stderr=subprocess.STDOUT,
            timeout=maximum_seconds)
    require(done.returncode == 0, 'decision_cpp_command_failed:'+str(output))


def _discover(executable, output):
    with _environment({key: None for key in os.environ if key.startswith('GTEST_')}):
        _command([str(executable), '--gtest_list_tests', '--gtest_filter=*', '--gtest_repeat=1'], output, 60)
    group, identities = None, []
    for line in output.read_text().splitlines():
        text = line.split('#', 1)[0].strip()
        if not text:
            continue
        if not line.startswith(' '):
            require(text.endswith('.'), 'decision_cpp_discovery_group')
            group = text[:-1]
        else:
            require(group is not None and re.fullmatch(r'[A-Za-z0-9_/]+', text),
                'decision_cpp_discovery_case')
            identities.append(group+'/'+text)
    require(identities and len(set(identities)) == len(identities) and
        not any('DISABLED_' in identity for identity in identities), 'decision_cpp_discovery_incomplete')
    return identities


class N1GeometryCppABTest(unittest.TestCase):
    def test_before_exposes_starvation_and_after_passes_complete_decision_cohort(self):
        binding = os.environ.get('TIMELEARNER_N1_GEOMETRY_CPP_CONTROLS')
        require(binding is not None, 'decision_cpp_controls_required')
        spec = load(Path(binding)/'declaration.json')
        require(set(spec) == {'before', 'after', 'output', 'toolchain', 'expected_case_ids',
            'expected_before_failures'} and all(set(spec[n]) ==
            {'directory', 'root_commit', 'pulse_commit'} for n in ('before', 'after')),
            'decision_cpp_controls_schema')
        toolchain = spec['toolchain']
        require(set(toolchain) == {'qt_major', 'qt_dir', 'generator', 'compiler', 'make_program',
            'gtest_dir', 'gtest_source'} and toolchain['qt_major'] in (5, 6) and
            toolchain['generator'] == 'Unix Makefiles' and
            bool(toolchain['gtest_dir']) != bool(toolchain['gtest_source']), 'decision_cpp_toolchain_schema')
        dependencies = []
        qt = Path(toolchain['qt_dir'])/('Qt'+str(toolchain['qt_major'])+'Config.cmake')
        dependencies.append(qt)
        if toolchain['gtest_dir']:
            dependencies.append(Path(toolchain['gtest_dir'])/'GTestConfig.cmake')
        else:
            dependency = Path(toolchain['gtest_source']).resolve(strict=True)
            dependencies += [f for f in dependency.rglob('*') if '.git' not in f.relative_to(dependency).parts
                and f.is_file()]
        require(len(dependencies) <= 10000 and sum(f.stat().st_size for f in dependencies) <= 64*1024**2,
            'decision_cpp_dependency_inventory_budget')
        dependency_before = {str(f): frozen_digest(f, 32*1024**2) for f in dependencies}
        output = Path(spec['output']);output.mkdir(parents=True, exist_ok=False)
        snapshots = {n: _source(Path(spec[n]['directory']), spec[n]['root_commit'], spec[n]['pulse_commit'])
                     for n in ('before', 'after')}
        harness = Path(spec['after']['directory'])/'Tests/Integration/Algorithms'
        compiler = Path(toolchain['compiler']).resolve(strict=True)
        results, expected = {}, spec['expected_case_ids']
        require(type(expected) is list and expected and len(set(expected)) == len(expected) and
            type(spec['expected_before_failures']) is list and
            len(set(spec['expected_before_failures'])) == len(spec['expected_before_failures']) and
            set(spec['expected_before_failures']) <= set(expected), 'decision_cpp_expected_inventory')
        regression = ('BoundedTrainingN1GeometryFairness/'
            'ValidDenseResistanceMeshDoesNotStarveOtherLengthsInEitherRecoveryMode')
        for name in ('before', 'after'):
            root = Path(spec[name]['directory']);folder = output/name;folder.mkdir()
            build = folder/'build'
            configure = ['cmake', '-S', str(harness), '-B', str(build), '-G', toolchain['generator'],
                '-DCMAKE_BUILD_TYPE=Release', '-DQT_MAJOR='+str(toolchain['qt_major']),
                '-DQt'+str(toolchain['qt_major'])+'_DIR='+toolchain['qt_dir'],
                '-DCMAKE_CXX_COMPILER='+str(compiler), '-DCMAKE_MAKE_PROGRAM='+toolchain['make_program'],
                '-DNMSDK_TRAINING_ALGORITHM_SOURCE_ROOT='+str(root)]
            configure += (['-DGTest_DIR='+toolchain['gtest_dir']] if toolchain['gtest_dir'] else
                ['-DNMSDK_GTEST_SOURCE_ROOT='+toolchain['gtest_source']])
            _command(configure, folder/'configure.log', 180)
            _command(['cmake', '--build', str(build), '--parallel', '2'], folder/'build.log', 600)
            executable = build/'runtime/Test_PulseLib_TrainingAlgorithms'
            ids = _discover(executable, folder/'discovery.log')
            require(regression in ids, 'decision_cpp_regression_missing')
            self.assertEqual(set(ids), set(expected))
            self.assertEqual(len(ids), len(expected))
            flags = build_flags(build/'CMakeCache.txt')
            flags['role'] = 'production_decision_unit_projection; not native SDK admission'
            closure = {'root': {'head': spec[name]['root_commit'], 'status': ''},
                'Libraries/Nmsdk-PulseLib': {'head': spec[name]['pulse_commit'],
                    'recorded_gitlink': spec[name]['pulse_commit'], 'status': ''}}
            runtime = dict(schema_version=2, source_closure=closure,
                executable=file_record(executable), app_ini=file_record(Path(binding)/'declaration.json'),
                compiler=file_record(compiler), build_flags=flags, resolved_libraries=resolved_libraries(executable),
                loaded_process_files=None, loader_environment={k: os.environ.get(k)
                    for k in ('LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM')})
            runtime['runtime_identity'] = runtime_content_identity(runtime)
            runtime['runtime_fingerprint'] = digest_json(runtime['runtime_identity'])
            junit = folder/'native.xml'
            with _environment({key: None for key in os.environ if key.startswith('GTEST_')}):
                process = execute(runtime, ['--gtest_output=xml:'+str(junit),
                    '--gtest_filter=*', '--gtest_repeat=1'], folder,
                    folder/'process', 120., cooperative_capture=True)
            self.assertEqual(process['returncode'], 1 if name == 'before' else 0)
            self.assertEqual(process['runtime_provenance'], 'loaded_files_captured')
            inventory = audit_junit(junit, expected)
            wanted = spec['expected_before_failures'] if name == 'before' else []
            self.assertEqual(set(inventory['failed_test_ids']), set(wanted))
            self.assertEqual(len(inventory['failed_test_ids']), len(wanted))
            results[name] = dict(configure=configure, inventory=inventory, process=process,
                runtime=runtime, scientific_verdict=None)
        self.assertEqual(snapshots, {n: _source(Path(spec[n]['directory']),
            spec[n]['root_commit'], spec[n]['pulse_commit']) for n in ('before', 'after')})
        self.assertEqual(dependency_before, {str(f): frozen_digest(f, 32*1024**2) for f in dependencies})
        (output/'source-inventories.json').write_text(json.dumps(snapshots, indent=2)+'\n')
        (output/'dependency-inventory.json').write_text(json.dumps(dependency_before, indent=2)+'\n')
        (output/'result.json').write_text(json.dumps(dict(kind='timelearner_n1_geometry_cpp_ab',
            schema_version=1, results=results, before_expected_failure=True, physical_models_executed=False,
            scientific_verdict=None), indent=2, allow_nan=False)+'\n')
