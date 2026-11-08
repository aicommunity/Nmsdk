"""Lossless self-contained composite primary transport, not a training proof.

Blob integrity cannot attest native execution, selection, causal lineage or a
certificate. Semantic group/measurement audits are deliberately separate.
"""
import base64
import binascii
import hashlib
from pathlib import Path, PurePosixPath
import re

from .native_evidence import EvidenceError, count, require


def primary_path(value):
    require(type(value) is str and bool(value), 'composite_primary_path_missing')
    try: value.encode('utf-8')
    except UnicodeError as error: raise EvidenceError('composite_primary_path_invalid_unicode') from error
    path = PurePosixPath(value)
    require(str(path) == value and not path.is_absolute() and ':' not in value and '\\' not in value
            and all(part not in ('', '.', '..') for part in value.split('/')),
            'composite_primary_path_unsafe')
    return value


def _digest(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None,
            'composite_primary_digest_invalid')
    return value


def _paths(values):
    names = [primary_path(value) for value in values]
    folded = [value.casefold() for value in names]
    require(len(set(folded)) == len(folded), 'composite_primary_duplicate_or_case_colliding_path')
    files = set(folded)
    require(all('/'.join(name.split('/')[:i]) not in files for name in folded
                for i in range(1, len(name.split('/')))), 'composite_primary_file_directory_collision')
    return names


def capture_primary_blobs(primary_blobs, references, maximum_total_primary_bytes, *, external_resolver=None):
    """Resolve every declared raw CSV from the embedded bytes and optional mirror.

    An external resolver is an additional consistency requirement. It is never
    a fallback for missing embedded data. Repeated content may use different
    relative paths; both stored and materialized byte budgets remain bounded.
    """
    limit = count(maximum_total_primary_bytes)
    require(limit > 0 and type(primary_blobs) is dict and type(references) is list,
            'composite_primary_invalid_inventory')
    requested = []
    for reference in references:
        require(type(reference) is dict and set(reference) == {'relative_path', 'bytes', 'sha256'},
                'composite_primary_reference_fields')
        requested.append((primary_path(reference['relative_path']), count(reference['bytes']), _digest(reference['sha256'])))
    _paths([name for name, _, _ in requested])
    require(sum(size for _, size, _ in requested) <= limit, 'composite_primary_materialized_budget_exhausted')
    require(set(primary_blobs) == {digest for _, _, digest in requested},
            'composite_primary_missing_or_unreferenced_blob')
    declared = {}
    for digest, value in primary_blobs.items():
        _digest(digest)
        require(type(value) is dict and set(value) == {'bytes', 'base64'}, 'composite_primary_blob_fields')
        size = count(value['bytes']); encoded = value['base64']
        require(type(encoded) is str and len(encoded) == 4*((size+2)//3), 'composite_primary_base64_size_mismatch')
        declared[digest] = size
    require(sum(declared.values()) <= limit, 'composite_primary_stored_budget_exhausted')
    blobs = {}
    for digest, value in primary_blobs.items():
        try: raw = base64.b64decode(value['base64'], validate=True)
        except (binascii.Error, ValueError, UnicodeError) as error:
            raise EvidenceError('composite_primary_base64_invalid') from error
        require(len(raw) == declared[digest] and base64.b64encode(raw).decode('ascii') == value['base64']
                and hashlib.sha256(raw).hexdigest() == digest, 'composite_primary_blob_content_mismatch')
        blobs[digest] = raw
    result = {}
    for name, size, digest in requested:
        raw = blobs[digest]
        require(len(raw) == size, 'composite_primary_reference_size_mismatch')
        if external_resolver is not None:
            try: mirrored = external_resolver(name) if callable(external_resolver) else external_resolver[name]
            except EvidenceError: raise
            except (OSError, KeyError, TypeError, ValueError) as error:
                raise EvidenceError('composite_external_primary_missing') from error
            require(type(mirrored) is bytes and mirrored == raw, 'composite_external_primary_mismatch')
        result[name] = raw
    return result


def filesystem_primary_resolver(directory):
    """Require regular files inside the source root, including every ancestor."""
    directory = Path(directory)
    require(not directory.is_symlink() and directory.is_dir(), 'composite_primary_root_invalid')
    root = directory.resolve(strict=True)
    def resolve(name):
        name = primary_path(name); path = root
        for part in name.split('/'):
            path = path/part
            require(not path.is_symlink(), 'composite_primary_symlink')
        require(path.is_file() and path.resolve(strict=True).is_relative_to(root), 'composite_primary_missing_or_escape')
        return path.read_bytes()
    return resolve


def write_primary_snapshot(primary, destination):
    """Write already captured immutable bytes to a fresh owned source snapshot."""
    require(type(primary) is dict and all(type(raw) is bytes for raw in primary.values()),
            'composite_primary_snapshot_invalid')
    names = _paths(list(primary))
    destination = Path(destination)
    require(not destination.exists() and not destination.is_symlink(), 'composite_primary_snapshot_exists')
    destination = destination.parent.resolve(strict=True)/destination.name
    destination.mkdir()
    for name in names:
        path = destination/name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream: stream.write(primary[name])
    return destination
