"""Explicit native-test isolation; every case still uses the production gate.

Partitioning is a declared execution protocol, never a retry of an invalid run.
The derived JUnit references the original per-process JUnits. No aggregate
process/result.json is manufactured for processes that did not run together.
"""
import argparse
import copy
import hashlib
import os
from pathlib import Path
import re
import time
from xml.etree import ElementTree as ET

from .native_evidence import load, number, require
from .native_gate import audit_junit, run_native_gate, supported_specification
from .process_runner import _write, verify_runtime


FIELDS = {"kind", "schema_version", "native_gate", "maximum_total_wall_seconds",
          "maximum_case_wall_seconds"}


def validate(spec):
    require(type(spec) is dict and set(spec) == FIELDS and
            spec['kind'] == 'timelearner_partitioned_native_gate' and
            type(spec['schema_version']) is int and spec['schema_version'] == 1,
            'unknown_partitioned_native_specification')
    gate = spec['native_gate']
    require(supported_specification(gate) and gate['schema_version'] == 2 and
            gate['cooperative_runtime_capture'] is True, 'partition_requires_captured_native_gate')
    ids = gate['expected_test_ids']
    require(type(ids) is list and ids and all(type(x) is str and
            re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*/[A-Za-z_][A-Za-z0-9_]*', x)
            for x in ids) and len(ids) == len(set(ids)), 'invalid_partition_test_ids')
    total, case = number(spec['maximum_total_wall_seconds']), number(spec['maximum_case_wall_seconds'])
    require(1 <= case <= total <= 86400, 'invalid_partition_wall_budgets')
    require(number(gate['maximum_wall_seconds']) >= total, 'partition_exceeds_declared_gate_budget')
    return gate, total, case


def aggregate_junit(output, expected):
    """Only complete, individually valid original case observations may aggregate."""
    output = Path(output)
    combined = ET.Element('testsuites', tests=str(len(expected)), failures='0', errors='0', disabled='0')
    sources, owners, failures, errors = [], set(), 0, 0
    for index, identity in enumerate(expected):
        folder = output/'cases'/f'{index:04d}'
        result = load(folder/'result.json')
        require(result['validity'] == 'valid' and result['assertion_status'] in ('passed', 'failed'),
                'partition_case_not_valid:'+identity)
        inventory = audit_junit(folder/'native.xml', [identity])
        require(inventory == result['inventory'], 'partition_case_inventory_changed:'+identity)
        process = load(folder/'process/result.json')
        require(process['runtime_provenance'] == 'loaded_files_captured' and
                ((inventory['assertion_status'] == 'passed' and process['execution'] == 'completed' and process['returncode'] == 0) or
                 (inventory['assertion_status'] == 'failed' and process['execution'] == 'process_error' and process['returncode'] == 1)),
                'partition_case_execution_disagrees:'+identity)
        owner = load(folder/'process/owned-process.json')
        key = (owner['boot_id'], owner['pid'], owner['start_ticks'])
        require(key not in owners, 'partition_reused_native_process')
        owners.add(key)
        tree = ET.parse(folder/'native.xml').getroot()
        require(tree.tag == 'testsuites', 'partition_unexpected_junit_root')
        for suite in tree:
            require(suite.tag == 'testsuite', 'partition_unexpected_junit_child')
            combined.append(copy.deepcopy(suite))
        failures += int(tree.get('failures', '0'))
        errors += int(tree.get('errors', '0'))
        sources.append({'test_id': identity, 'junit': str((folder/'native.xml').relative_to(output)),
                        'sha256': inventory['sha256'], 'native_process': owner})
    combined.set('failures', str(failures))
    combined.set('errors', str(errors))
    combined.set('timelearner_origin', 'derived_from_independent_original_junits')
    ET.ElementTree(combined).write(output/'native.xml', encoding='utf-8', xml_declaration=True)
    _write(output/'junit-sources.json', {'kind': 'partition_junit_sources', 'schema_version': 1, 'cases': sources})
    return audit_junit(output/'native.xml', expected)


def project_native_outputs(output, count):
    """A lossless reader view; differing same-name files are never overwritten."""
    output = Path(output)
    records = {}
    for index in range(count):
        source = output/'cases'/f'{index:04d}'/'native'
        for path in sorted(source.rglob('*')):
            require(not path.is_symlink(), 'partition_native_symlink')
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            record = {'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            name = relative.as_posix()
            if name in records:
                require(records[name]['content'] == record, 'partition_native_filename_collision:'+name)
                records[name]['sources'].append(str(path.relative_to(output)))
                continue
            target = output/'native'/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.link(path, target)
            records[name] = {'content': record, 'sources': [str(path.relative_to(output))]}
    _write(output/'native-projection.json', records)


def run(specification, output):
    specification = Path(specification).resolve(strict=True)
    spec = load(specification)
    gate, total, per_case = validate(spec)
    gate = copy.deepcopy(gate)
    for key in ['source_root', 'runtime_manifest']:
        require(type(gate[key]) is str and bool(gate[key]), 'invalid_partition_path:'+key)
        path = Path(gate[key])
        gate[key] = str((path if path.is_absolute() else specification.parent/path).resolve(strict=True))
    runtime = load(gate['runtime_manifest'])
    executable = verify_runtime(runtime)
    output = Path(output).resolve()
    for protected in (Path(gate['source_root']), executable.parent):
        require(not output.is_relative_to(protected) and not protected.is_relative_to(output),
                'partition_output_overlaps_source_or_runtime')
    output.mkdir(parents=True, exist_ok=False)
    _write(output/'partitioned-specification.json', spec)
    _write(output/'specification.json', gate)
    _write(output/'runtime.json', runtime)
    expected, results, started = gate['expected_test_ids'], [], time.monotonic()
    record = {'kind': 'timelearner_partitioned_native_gate_result', 'schema_version': 1,
              'execution': 'interrupted', 'validity': 'incomplete_test_observation',
              'assertion_status': 'not_assessed', 'reason': 'not_all_partitions_observed',
              'inventory': None, 'scientific_verdict': None}
    try:
        for index, identity in enumerate(expected):
            remaining = total - (time.monotonic() - started)
            require(remaining >= 1, 'partition_total_wall_budget_exhausted')
            child = dict(gate, expected_test_ids=[identity], maximum_wall_seconds=min(per_case, remaining))
            declaration = output/'declarations'/f'{index:04d}.json'
            declaration.parent.mkdir(exist_ok=True)
            _write(declaration, child)
            result = run_native_gate(declaration, output/'cases'/f'{index:04d}')
            results.append({'test_id': identity, 'result': result})
            _write(output/'progress.json', {'expected': len(expected), 'executed': len(results), 'cases': results})
        verify_runtime(runtime)
        inventory = aggregate_junit(output, expected)
        project_native_outputs(output, len(expected))
        record.update(execution='completed', validity='valid', assertion_status=inventory['assertion_status'],
                      reason='complete_independently_observed_inventory', inventory=inventory)
    except Exception as error:
        record.update(execution='process_error', reason=str(error))
    record.update(executed_partitions=len(results), wall_seconds=time.monotonic()-started)
    _write(output/'result.json', record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('specification', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = run(args.specification, args.output)
    return 0 if result['validity'] == 'valid' and result['assertion_status'] == 'passed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
