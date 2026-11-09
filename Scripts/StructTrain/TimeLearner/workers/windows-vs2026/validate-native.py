"""Run declared native checks through the existing Windows schema4 gate.

Consumes a verified closed-build audit; never changes its original outcome.
The native gate, JUnit audit and process backend come from the compiled SDK.
"""
import argparse
import gzip
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback

sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--specification', required=True, type=Path)
    args = parser.parse_args()
    module_spec = importlib.util.spec_from_file_location('closed_build_helpers', Path(__file__).with_name('audit-closed-build.py'))
    checks = importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(checks)
    require, private, digest, emit = checks.require, checks.private_path, checks.digest, checks.emit
    require(os.name == 'nt' and __debug__, 'normal_windows_python_required')
    spec = json.loads(private(args.specification).read_bytes())
    require(spec['kind'] == 'timelearner_windows_native_validation' and spec['schema_version'] == 1, 'unknown_native_validation')
    require(digest(Path(__file__)) == spec['worker_sha256'], 'native_worker_changed')
    source, runtime, audit, output = [private(spec[k]) for k in ('source_root','runtime_root','closed_build_audit','output_root')]
    require(not output.exists() and not output.is_relative_to(source) and not output.is_relative_to(runtime) and
            not source.is_relative_to(output) and not runtime.is_relative_to(output), 'fresh_validation_output_required')
    output.mkdir(parents=True, exist_ok=False);passed = False
    try:
        emit(output, 'specification.json', spec);(output/'producer.py').write_bytes(Path(__file__).read_bytes())
        for name, expected in spec['audit_records'].items():
            path = private(audit/name)
            require(path.is_relative_to(audit) and digest(path) == expected, 'closed_audit_changed:'+name)
        proof = json.loads((audit/'audit.json').read_bytes())
        require(json.loads((audit/'terminal.json').read_bytes())['audit_passed'] is True and
                proof['source_commit'] == spec['source_commit'] and proof['compiled_tests_executed'] is False,
                'closed_build_audit_not_valid')
        sys.path.insert(0, str(source))
        from Scripts.StructTrain.TimeLearner.runtime import source_closure, file_record, build_flags, runtime_content_identity, digest_json
        from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
        import Scripts.StructTrain.TimeLearner.windows_process as backend
        require(source_closure(source) == proof['source_closure'], 'audited_source_changed')
        helper_spec = importlib.util.spec_from_file_location('original_build_helpers', source/'Scripts/StructTrain/TimeLearner/workers/windows-vs2026/sdk-build.py')
        helper = importlib.util.module_from_spec(helper_spec);helper_spec.loader.exec_module(helper)
        with gzip.open(audit/'runtime-files.json.gz','rb') as stream:
            runtime_inventory = json.load(stream)
        require(helper.inventory(runtime) == runtime_inventory, 'audited_runtime_changed')
        executable = runtime/'Test_PulseLib_StorageComponents.exe'
        require(file_record(executable) == proof['targets']['Test_PulseLib_StorageComponents.exe'], 'audited_executable_changed')
        cache = private(spec['cmake_cache']);flags = build_flags(cache)
        backend_record = file_record(Path(backend.__file__))
        flags.update({'role':'actual_windows_native_validation','windows_backend_sha256':backend_record['sha256']})
        manifest = {'schema_version':2,'windows_source_root':str(source),'source_closure':proof['source_closure'],
            'executable':file_record(executable),'app_ini':file_record(runtime/'NeuroModelerConsole.ini'),
            'compiler':file_record(Path(flags['CMAKE_CXX_COMPILER'])),'build_flags':flags,
            'resolved_libraries':[file_record(runtime/p) for p in sorted(runtime_inventory) if p.lower().endswith('.dll')],
            'loaded_process_files':None,'windows_backend':backend_record,
            'loader_environment':{key:os.environ.get(key) for key in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}}
        manifest['runtime_identity'] = runtime_content_identity(manifest)
        manifest['runtime_fingerprint'] = digest_json(manifest['runtime_identity'])
        emit(output,'runtime.json',manifest)
        gate = {'kind':'timelearner_native_test_gate','schema_version':4,'runtime_manifest':str(output/'runtime.json'),
            'source_root':str(source),'expected_test_ids':spec['expected_test_ids'],'maximum_wall_seconds':spec['maximum_wall_seconds'],
            'asan_options':'','cooperative_runtime_capture':True,'process_limits':spec['process_limits'],
            'worker_lock':str(private(checks.BASE/'locks/worker.lock'))}
        emit(output,'gate.json',gate)
        result = run_native_gate(output/'gate.json',output/'native-gate');emit(output,'gate-result.json',result)
        require(helper.inventory(runtime) == runtime_inventory and source_closure(source) == proof['source_closure'],
                'validation_changed_runtime_or_source')
        require(result['validity'] == 'valid' and result['assertion_status'] == 'passed', 'actual_native_checks_not_passed')
        passed = True
    except BaseException as error:
        emit(output,'exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
    finally:
        emit(output,'terminal.json',{'native_checks_passed':passed,'scientific_worker_admitted':False,
            'original_build_outcome_unchanged':True,'scientific_verdict':None})
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
