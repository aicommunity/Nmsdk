"""Complete production C++ units for the opt-in input traversal candidate.

Decision observations are controlled by the shared production-recorder fixture;
this test does not execute native neuron physics or admit an SDK. Default-mode
compatibility is a separate before/after cohort, with its own pinned sources.
"""
import json
import os
from pathlib import Path
import unittest

from . import test_input_search_state_cpp_parity as parity
from .test_n1_geometry_cpp_ab import _command, _discover, _source
from ..native_evidence import load, require
from ..native_gate import _environment, audit_junit
from ..process_runner import execute
from ..runtime import build_flags, digest_json, file_record, resolved_libraries, runtime_content_identity


class ClassicRoundRobinDefaultCppParityTest(parity.InputSearchStateCppParityTest):
    controls_environment = 'TIMELEARNER_RR_DEFAULT_CPP_CONTROLS'
    result_kind = 'timelearner_round_robin_sequential_default_cpp_parity'


class ClassicInputRoundRobinCppTest(unittest.TestCase):
    def test_complete_candidate_traversal_and_fresh_context_contract(self):
        controls = os.environ.get('TIMELEARNER_RR_DECISION_CPP_CONTROLS')
        require(controls is not None, 'round_robin_cpp_controls_required')
        spec = load(Path(controls)/'declaration.json')
        require(set(spec) == {'source', 'output', 'toolchain', 'expected_case_ids'} and
            set(spec['source']) == {'directory', 'root_commit', 'pulse_commit'}, 'round_robin_cpp_schema')
        declared = spec['source'];root = Path(declared['directory']).resolve(strict=True)
        before = _source(root, declared['root_commit'], declared['pulse_commit'])
        tool = spec['toolchain']
        require(tool['qt_major'] in (5, 6) and tool['generator'] == 'Unix Makefiles' and
            tool['gtest_dir'] and not tool['gtest_source'], 'round_robin_cpp_toolchain')
        dependencies = [Path(tool['qt_dir'])/('Qt'+str(tool['qt_major'])+'Config.cmake'),
            Path(tool['gtest_dir'])/'GTestConfig.cmake']
        dependency_before = [file_record(p) for p in dependencies]
        output = Path(spec['output']);output.mkdir(parents=True, exist_ok=False)
        build = output/'build';compiler = Path(tool['compiler']).resolve(strict=True)
        arguments = ['cmake', '-S', str(root/'Tests/Integration/Algorithms'), '-B', str(build),
            '-G', tool['generator'], '-DCMAKE_BUILD_TYPE=Release', '-DQT_MAJOR='+str(tool['qt_major']),
            '-DQt'+str(tool['qt_major'])+'_DIR='+tool['qt_dir'], '-DGTest_DIR='+tool['gtest_dir'],
            '-DCMAKE_CXX_COMPILER='+str(compiler), '-DCMAKE_MAKE_PROGRAM='+tool['make_program'],
            '-DNMSDK_TRAINING_ALGORITHM_SOURCE_ROOT='+str(root), '-DNMSDK_TEST_CLASSIC_INPUT_ROUND_ROBIN=ON']
        _command(arguments, output/'configure.log', 180)
        _command(['cmake', '--build', str(build), '--target', 'Test_PulseLib_ClassicInputRoundRobin',
            '--parallel', '2'], output/'build.log', 600)
        executable = build/'runtime/Test_PulseLib_ClassicInputRoundRobin'
        expected = spec['expected_case_ids'];ids = _discover(executable, output/'discovery.log')
        require(type(expected) is list and len(expected) == len(set(expected)) == 14 and
            set(ids) == set(expected) and len(ids) == len(expected), 'round_robin_cpp_case_inventory')
        runtime = dict(schema_version=2,
            source_closure={'root': {'head': declared['root_commit'], 'status': ''},
                'Libraries/Nmsdk-PulseLib': {'head': declared['pulse_commit'],
                    'recorded_gitlink': declared['pulse_commit'], 'status': ''}},
            executable=file_record(executable), app_ini=file_record(Path(controls)/'declaration.json'),
            compiler=file_record(compiler), build_flags=build_flags(build/'CMakeCache.txt'),
            resolved_libraries=resolved_libraries(executable), loaded_process_files=None,
            loader_environment={k: os.environ.get(k) for k in
                ('LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM')})
        runtime['runtime_identity'] = runtime_content_identity(runtime)
        runtime['runtime_fingerprint'] = digest_json(runtime['runtime_identity'])
        with _environment({k: None for k in os.environ if k.startswith('GTEST_')}):
            process = execute(runtime, ['--gtest_output=xml:'+str(output/'native.xml'),
                '--gtest_filter=*', '--gtest_repeat=1'], output, output/'process',
                120., cooperative_capture=True)
        self.assertEqual(process['runtime_provenance'], 'loaded_files_captured')
        inventory = audit_junit(output/'native.xml', expected)
        self.assertEqual(process['returncode'], 0)
        self.assertEqual(inventory['failed_test_ids'], [])
        self.assertEqual(before, _source(root, declared['root_commit'], declared['pulse_commit']))
        self.assertEqual(dependency_before, [file_record(p) for p in dependencies])
        result = dict(kind='timelearner_classic_input_round_robin_cpp', schema_version=1,
            inventory=inventory, process=process, runtime=runtime, source_inventory=before,
            dependency_inventory=dependency_before, native_physics_executed=False,
            native_configuration_enabled=False, scientific_verdict=None)
        (output/'result.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
