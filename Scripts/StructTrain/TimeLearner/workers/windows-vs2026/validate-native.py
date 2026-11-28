"""Run declared native checks through the Windows native gate.

Consumes a verified closed-build audit; never changes its original outcome.
Legacy validation imports its gate from the compiled SDK. Version3 explicitly
binds a separate immutable Python gate source for declared DATA inputs; the
compiled source, runtime and original closed-build audit remain unchanged.
"""
import argparse
import gzip
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
import traceback

sys.dont_write_bytecode = True


def validation_plan(spec):
    """Preserve the exact declared test set and finite per-process partitioning."""
    def check(condition, reason):
        if not condition:
            raise RuntimeError(reason)
    def ids(value):
        return (type(value) is list and bool(value) and
                all(type(v) is str and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*/[A-Za-z_][A-Za-z0-9_]*', v)
                    for v in value) and len(value) == len(set(value)))
    def wall(value):
        return type(value) in (int, float) and 0 < value <= 86400 and math.isfinite(value)
    version = spec.get('schema_version')
    check(type(version) is int and version in (1, 2, 3), 'unknown_native_validation')
    check(version == 3 or not ({'data_inputs', 'artifact_directories',
          'gate_source_root', 'gate_source_commit'} & set(spec)),
          'native_validation_data_contract_requires_version3')
    if version == 3:
        check(type(spec.get('gate_source_root')) is str and
              Path(spec['gate_source_root']).is_absolute() and
              type(spec.get('gate_source_commit')) is str and
              re.fullmatch(r'[0-9a-f]{40}', spec['gate_source_commit']),
              'native_validation_gate_source_required')
        from Scripts.StructTrain.TimeLearner import native_gate_inputs, gtest_full_names
        from Scripts.StructTrain.TimeLearner.native_gate import artifact_directories_valid
        check(native_gate_inputs.valid_windows_declarations(spec.get('data_inputs')) and
              artifact_directories_valid(spec.get('artifact_directories')),
              'native_validation_data_inputs_or_artifacts_invalid')

        def ids(value):
            try:
                gtest_full_names.validate_names(value)
                return True
            except (ValueError, TypeError):
                return False
    expected, maximum = spec.get('expected_test_ids'), spec.get('maximum_wall_seconds')
    check(ids(expected) and wall(maximum), 'invalid_native_validation_inventory_or_wall')
    if version == 1 or (version == 3 and 'partitions' not in spec):
        check('partitions' not in spec, 'undeclared_native_validation_partitions')
        return [{'name': 'single', 'expected_test_ids': list(expected), 'maximum_wall_seconds': maximum}]
    partitions = spec.get('partitions')
    check(type(partitions) is list and 0 < len(partitions) <= 16, 'native_validation_partitions_required')
    names, flattened, total = [], [], 0
    plan = []
    for row in partitions:
        check(type(row) is dict and set(row) == {'name', 'expected_test_ids', 'maximum_wall_seconds'},
              'native_validation_partition_schema')
        check(type(row['name']) is str and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,99}', row['name']) and
              ids(row['expected_test_ids']) and wall(row['maximum_wall_seconds']),
              'invalid_native_validation_partition')
        names.append(row['name']); flattened.extend(row['expected_test_ids']); total += row['maximum_wall_seconds']
        plan.append({'name': row['name'], 'expected_test_ids': list(row['expected_test_ids']),
                     'maximum_wall_seconds': row['maximum_wall_seconds']})
    check(len(names) == len({name.casefold() for name in names}) and len(flattened) == len(set(flattened)) and
          set(flattened) == set(expected), 'native_validation_partition_inventory_mismatch')
    check(total <= maximum, 'native_validation_partition_wall_exceeded')
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--specification', required=True, type=Path)
    parser.add_argument('--worker-root', type=Path)
    args = parser.parse_args()
    module_spec = importlib.util.spec_from_file_location('closed_build_helpers', Path(__file__).with_name('audit-closed-build.py'))
    checks = importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(checks)
    require, private, digest, emit = checks.require, checks.private_path, checks.digest, checks.emit
    require(os.name == 'nt' and __debug__, 'normal_windows_python_required')
    _, spec = checks.read_specification(args.specification, args.worker_root)
    require(spec['kind'] == 'timelearner_windows_native_validation', 'unknown_native_validation')
    require(digest(Path(__file__)) == spec['worker_sha256'], 'native_worker_changed')
    source, runtime, audit, output = [private(spec[k]) for k in ('source_root','runtime_root','closed_build_audit','output_root')]
    gate_source = source
    if type(spec.get('schema_version')) is int and spec['schema_version'] == 3:
        gate_source = private(spec['gate_source_root'])
        require(Path(__file__).resolve().is_relative_to(gate_source) and
                checks.git(gate_source, 'rev-parse', 'HEAD') == spec['gate_source_commit'],
                'native_validation_gate_source_changed')
        sys.path.insert(0, str(gate_source))
    plan = validation_plan(spec)
    require(not output.exists() and not output.is_relative_to(source) and not output.is_relative_to(runtime) and
            not source.is_relative_to(output) and not runtime.is_relative_to(output), 'fresh_validation_output_required')
    output.mkdir(parents=True, exist_ok=False);passed = False; results = []
    try:
        emit(output, 'specification.json', spec);(output/'producer.py').write_bytes(Path(__file__).read_bytes())
        for name, expected in spec['audit_records'].items():
            path = private(audit/name)
            require(path.is_relative_to(audit) and digest(path) == expected, 'closed_audit_changed:'+name)
        proof = json.loads((audit/'audit.json').read_bytes())
        require(json.loads((audit/'terminal.json').read_bytes())['audit_passed'] is True and
                proof['source_commit'] == spec['source_commit'] and proof['compiled_tests_executed'] is False,
                'closed_build_audit_not_valid')
        sys.path.insert(0, str(gate_source))
        from Scripts.StructTrain.TimeLearner.runtime import source_closure, file_record, build_flags, runtime_content_identity, digest_json
        from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
        import Scripts.StructTrain.TimeLearner.windows_process as backend
        gate_before = None
        if spec['schema_version'] == 3:
            from Scripts.StructTrain.TimeLearner.owned_python_job import _source_snapshot
            gate_before = _source_snapshot(gate_source, spec['gate_source_commit'])
            emit(output, 'gate-source-before.json', gate_before)
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
        for partition in plan:
            single = spec['schema_version'] == 1 or (spec['schema_version'] == 3 and 'partitions' not in spec)
            destination = output if single else output/partition['name']
            if destination != output:
                destination.mkdir(exist_ok=False)
            require(helper.inventory(runtime) == runtime_inventory and source_closure(source) == proof['source_closure'],
                    'validation_changed_runtime_or_source')
            gate = {'kind':'timelearner_native_test_gate','schema_version':4,'runtime_manifest':str(output/'runtime.json'),
                'source_root':str(source),'expected_test_ids':partition['expected_test_ids'],
                'maximum_wall_seconds':partition['maximum_wall_seconds'],
                'asan_options':'','cooperative_runtime_capture':True,'process_limits':spec['process_limits'],
                'worker_lock':str(private(checks.BASE/'locks/worker.lock'))}
            if spec['schema_version'] == 3:
                gate.update(schema_version=8, data_inputs=spec['data_inputs'],
                            artifact_directories=spec['artifact_directories'])
            emit(destination,'gate.json',gate)
            result = run_native_gate(destination/'gate.json',destination/'native-gate')
            emit(destination,'gate-result.json',result)
            results.append({'name': partition['name'], 'result': result})
            require(helper.inventory(runtime) == runtime_inventory and source_closure(source) == proof['source_closure'],
                    'validation_changed_runtime_or_source')
            require(result['validity'] == 'valid' and result['assertion_status'] == 'passed', 'actual_native_checks_not_passed')
        if gate_before is not None:
            require(_source_snapshot(gate_source, spec['gate_source_commit']) == gate_before,
                    'native_validation_gate_source_changed')
            emit(output, 'gate-source-after.json', gate_before)
        passed = True
    except BaseException as error:
        emit(output,'exception.json',{'reason':str(error),'traceback':traceback.format_exc()})
    finally:
        if spec['schema_version'] in (2, 3):
            emit(output, 'suite-results.json', {'partitions': results, 'complete': passed,
                'expected_cpp_cases': len(spec['expected_test_ids']), 'scientific_verdict': None})
        emit(output,'terminal.json',{'native_checks_passed':passed,'scientific_worker_admitted':False,
            'original_build_outcome_unchanged':True,'scientific_verdict':None})
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
