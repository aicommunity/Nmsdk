"""Explicit immutable DATA inputs for contained native tests.

The outer job owns read reservations for the declared source files. This module
captures bounded bytes, stages them inside the owned output and checks both
copies after execution; it grants no execution or scientific authority.
"""
from pathlib import Path
import re

from .collector_provenance import (RequiredFileRole, capture_required_file_roles,
                                   frozen_digest, _frozen, _json)
from .native_evidence import require


MAXIMUM_INPUT_BYTES = 64*1024**2
MAXIMUM_TOTAL_BYTES = 128*1024**2
_NAME = re.compile(r'[A-Za-z][A-Za-z0-9_.-]{0,127}')
_SHA = re.compile(r'[0-9a-f]{64}')


def valid_declarations(rows):
    if type(rows) is not list or not 1 <= len(rows) <= 8:
        return False
    for row in rows:
        if not (type(row) is dict and set(row) == {'name', 'path', 'bytes', 'sha256'} and
                type(row['name']) is str and _NAME.fullmatch(row['name']) and
                row['name'].casefold() != 'descriptor.json' and
                type(row['path']) is str and row['path'] and
                not any(ord(c) < 32 or ord(c) == 127 for c in row['path']) and
                Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts and
                type(row['bytes']) is int and 0 < row['bytes'] <= MAXIMUM_INPUT_BYTES and
                type(row['sha256']) is str and _SHA.fullmatch(row['sha256'])):
            return False
    return (len({r['name'].casefold() for r in rows}) == len(rows) and
            len({r['path'] for r in rows}) == len(rows) and
            sum(r['bytes'] for r in rows) <= MAXIMUM_TOTAL_BYTES)


def capture_inputs(rows, output):
    require(valid_declarations(rows), 'native_gate_data_input_declaration')
    output = Path(output).absolute()
    requirements = []
    for index, row in enumerate(rows):
        path = Path(row['path'])
        require(not path.is_relative_to(output) and not output.is_relative_to(path),
                'native_gate_data_input_overlaps_output')
        requirements.append(RequiredFileRole('input'+str(index), path.parent, path.name,
            row['bytes'], row['sha256'], MAXIMUM_INPUT_BYTES, row['name']))
    return capture_required_file_roles(requirements, maximum_total_bytes=MAXIMUM_TOTAL_BYTES)


def stage_inputs(captured, output):
    return captured.materialize(output, Path(output)/'native-inputs')


def verify_inputs(captured, output):
    """Reject changed sources, changed staged bytes and added/aliased entries."""
    descriptor = captured.descriptor
    directory = Path(output)/'native-inputs'
    roles = descriptor['roles']
    require(not directory.is_symlink() and directory.is_dir() and
            {p.name for p in directory.iterdir()} ==
            {'descriptor.json', *(row['staged_name'] for row in roles.values())},
            'native_gate_data_input_namespace_changed')
    # Materialize's own descriptor is part of the frozen staged namespace.
    raw_descriptor, _ = _frozen(directory/'descriptor.json', 1024**2)
    require(_json(raw_descriptor) == descriptor,
            'native_gate_data_input_descriptor_changed')
    for row in roles.values():
        for path in (Path(row['source_path']), directory/row['staged_name']):
            actual = frozen_digest(path, MAXIMUM_INPUT_BYTES)
            require(actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256'],
                    'native_gate_data_input_changed')
    return dict(descriptor=descriptor, source_bytes_unchanged=True, staged_bytes_unchanged=True,
                native_execution_attested=False, scientific_verdict=None)
