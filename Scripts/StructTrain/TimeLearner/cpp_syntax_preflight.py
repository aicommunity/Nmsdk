"""Bounded Linux syntax-only checks using a closed production build's flags.

Checks real translation units/headers; never links, overwrites the reference
build, executes a model, or substitutes for native integration acceptance.
"""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import shutil
import time

from . import runtime
from .collector_provenance import _canonical, _frozen, _json
from .contained_process import inspect
from .contained_runner import execute
from .native_evidence import require
from .owned_native_job import status
from .resource_reservations import Reservations

BASES = {Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor')}


def flags_arguments(text, previous_source, source):
    values = {}
    for line in text.splitlines():
        if line.startswith(('CXX_DEFINES =', 'CXX_INCLUDES =', 'CXX_FLAGS =')):
            key, value = line.split('=', 1)
            require(key.strip() not in values and '$' not in value, 'syntax_preflight_make_expansion_or_duplicate')
            values[key.strip()] = shlex.split(value)
    require(set(values) == {'CXX_DEFINES', 'CXX_INCLUDES', 'CXX_FLAGS'}, 'syntax_preflight_flags_inventory')
    result = sum((values[name] for name in ('CXX_DEFINES', 'CXX_INCLUDES', 'CXX_FLAGS')), [])
    forbidden = ('-o', '-MF', '-MT', '-MQ', '-MJ', '-save-temps', '-fplugin', '-fprofile-generate')
    require(not any(value in ('-c', '-S', '-E', '-MD', '-MMD', '-M', '-MM') or
                    value.startswith(('@', *forbidden)) for value in result), 'syntax_preflight_writing_or_response_option')
    return [value.replace(str(previous_source), str(source)) for value in result]


def _keys(value, names):
    require(type(value) is dict and set(value) == set(names.split()), 'syntax_preflight_fields')


def _binding(value):
    _keys(value, 'path sha256')
    path = _canonical(Path(value['path']));raw, record = _frozen(path, 16*1024**2)
    require(record['sha256'] == value['sha256'], 'syntax_preflight_bound_input_changed')
    return path, raw


def _write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False);stream.write('\n')


def run(plan):
    _keys(plan, 'kind schema_version workspace source previous_source reference_job cache output units')
    require(plan['kind'] == 'timelearner_cpp_syntax_preflight' and type(plan['schema_version']) is int and
            plan['schema_version'] == 1 and os.name == 'posix', 'syntax_preflight_linux_schema')
    base = _canonical(Path(plan['workspace']));require(base in BASES, 'syntax_preflight_workspace')
    _keys(plan['source'], 'path commit')
    source = _canonical(Path(plan['source']['path']));previous = _canonical(Path(plan['previous_source']))
    require(source == Path(__file__).resolve().parents[3], 'syntax_preflight_mixed_sdk')
    reference = _canonical(Path(plan['reference_job']));cache, _ = _binding(plan['cache'])
    output = Path(plan['output'])
    require(output.is_absolute() and output.resolve() == output and output.is_relative_to(base/'readbacks') and
            not output.exists() and all(p.is_relative_to(base) for p in (source, previous, reference, cache)),
            'syntax_preflight_paths')
    reference_state = status(Path(str(reference)+'-controller'))
    require(not reference_state['supervisor_live'] and reference_state['outer']['all_processes_closed'] and
            not reference_state['result']['record_errors'], 'syntax_preflight_reference_not_closed')
    reference_job = _json((reference/'job.json').read_bytes())
    require(Path(reference_job['paths']['source']) == previous and
            Path(reference_job['paths']['build']) == cache.parent, 'syntax_preflight_reference_context')
    require(type(plan['units']) is list and 0 < len(plan['units']) <= 16, 'syntax_preflight_units')
    units = [];seen = set()
    for row in plan['units']:
        _keys(row, 'source flags')
        relative = PurePosixPath(row['source'])
        require(type(row['source']) is str and not relative.is_absolute() and '\\' not in row['source'] and
                '..' not in relative.parts and relative.as_posix() == row['source'] and relative.suffix == '.cpp' and row['source'] not in seen,
                'syntax_preflight_translation_unit')
        seen.add(row['source']);unit = _canonical(source/relative)
        require(unit.is_file() and unit.is_relative_to(source), 'syntax_preflight_source_escape')
        flags, raw = _binding(row['flags'])
        require(flags.name == 'flags.make' and flags.is_relative_to(cache.parent), 'syntax_preflight_flags_outside_reference_build')
        units.append((unit, flags, flags_arguments(raw.decode('utf-8'), previous, source)))
    before = runtime.source_closure(source)
    require(before['root']['head'] == plan['source']['commit'], 'syntax_preflight_source_commit')
    compiler = Path(runtime.build_flags(cache)['CMAKE_CXX_COMPILER']).resolve(strict=True)
    require(compiler.name in ('g++', 'c++', 'g++-11', 'g++-12', 'g++-13', 'g++-14', 'g++-15',
                              'x86_64-linux-gnu-g++-11', 'x86_64-linux-gnu-g++-12', 'x86_64-linux-gnu-g++-13',
                              'x86_64-linux-gnu-g++-14', 'x86_64-linux-gnu-g++-15'), 'syntax_preflight_gcc_only')
    registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
    require(not registry.managed_units, 'syntax_preflight_requires_existing_legacy_registry')
    require(shutil.disk_usage(base).free >= 512*1024**2, 'syntax_preflight_disk_floor')
    framework = _canonical(Path(reference_job['paths']['framework']))
    require(framework.is_relative_to(base), 'syntax_preflight_framework_outside_workspace')
    resources = [{'path':str(p), 'access':'read'} for p in (source, previous, cache.parent, reference, framework)]
    resources.append({'path':str(output), 'access':'write'})
    demands = {} if registry.capacity is None else {'demands':{'slots':1, 'memory_bytes':4*1024**3, 'disk_bytes':128*1024**2}}
    lease = registry.reserve(output.name, resources, ttl_seconds=240, **demands);token = lease['token']
    output.mkdir();_write(output/'plan.json', plan);_write(output/'reservation.json', lease)
    results = [];closed = True;passed = False;last_heartbeat = [0.]
    def monitor(_state):
        if time.monotonic()-last_heartbeat[0] >= 15:
            registry.heartbeat(token, ttl_seconds=240);registry.validate_paths(token);last_heartbeat[0] = time.monotonic()
            require(shutil.disk_usage(base).free >= 512*1024**2, 'syntax_preflight_disk_floor')
            allocated = sum(p.lstat().st_blocks*512 for p in output.rglob('*') if p.is_file())
            require(allocated <= 128*1024**2, 'syntax_preflight_output_budget')
    try:
        _write(output/'reference-closure.json', reference_state)
        for number, (unit, flags, arguments) in enumerate(units):
            manifest = runtime.snapshot(source, compiler, flags, cache)
            manifest['build_flags']['validation_scope'] = 'syntax_only_no_link_or_native_execution'
            manifest['build_flags']['translation_unit'] = unit.relative_to(source).as_posix()
            manifest['runtime_identity'] = runtime.runtime_content_identity(manifest)
            manifest['runtime_fingerprint'] = runtime.digest_json(manifest['runtime_identity'])
            closed = False  # No release if launch/observation raises without proven closure.
            result = execute(manifest, [*arguments, '-fsyntax-only', '-fmax-errors=5', str(unit)], source,
                output/('unit-%02d'%number), 180, memory_bytes=4*1024**3, tasks=32, monitor=monitor)
            closure = inspect(output/('unit-%02d'%number)/'contained');closed = closure['all_processes_closed']
            results.append({'source':unit.relative_to(source).as_posix(), 'result':result, 'whole_group_closed':closure['all_processes_closed']})
            _write(output/('unit-%02d-closure.json'%number), closure)
            if not closed or result['execution'] != 'completed':break
        after = runtime.source_closure(source)
        require(before == after, 'syntax_preflight_source_changed')
        _binding(plan['cache'])
        for row in plan['units']:_binding(row['flags'])
        passed = len(results) == len(units) and all(r['result']['execution'] == 'completed' for r in results) and closed
    finally:
        # An unproven child closure deliberately keeps the reservation held.
        if closed:registry.release(token, note='All launched syntax-only compiler groups closed; no native/runtime acceptance claim.')
        _write(output/'terminal.json', {'passed':passed, 'units_completed':len(results), 'expected_units':len(units),
            'whole_groups_closed':closed, 'source_closure':before, 'results':results,
            'native_execution_verified':False, 'scientific_verdict':None})
    return 0 if passed else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('plan', type=Path)
    return run(_json(parser.parse_args().plan.read_bytes()))


if __name__ == '__main__':raise SystemExit(main())
