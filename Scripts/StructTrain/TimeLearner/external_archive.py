"""Immutable experiment objects on M40; Git contains small checked references.

This module never deletes sources, rewrites Git, starts SSH or uploads results.
Run the store operation on the mounted archive, then publish its JSON reference.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from .native_evidence import load, require

ARCHIVE_KIND = 'nmsdk_structtrain_external_experiment_archive'
REFERENCE_KIND = 'nmsdk_structtrain_external_object'
DEFAULT_ROOT = '/media/user/Data/Nmsdk-StructTrainExpArchive'
ROOT_ENV = 'NMSDK_STRUCTTRAIN_ARCHIVE_ROOT'
SMB_WINDOWS_ROOT = '//10.245.1.17/Nmsdk-StructTrainExpArchive'
SMB_LINUX_ROOT = '/mnt/nmsdk-structtrain-archive'


def _configured_root(root):
    if root is not None:
        return root
    if os.environ.get(ROOT_ENV):
        return os.environ[ROOT_ENV]
    if os.name == 'nt':
        return SMB_WINDOWS_ROOT
    return DEFAULT_ROOT if Path(DEFAULT_ROOT).is_dir() else SMB_LINUX_ROOT


def _sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024**2), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _root(root):
    root = Path(root).absolute()
    require(not any(p.is_symlink() for p in (root, *root.parents)), 'archive_root_symlink')
    root = root.resolve(strict=True)
    marker = load(root/'archive.root.json')
    require(marker.get('kind') == ARCHIVE_KIND and marker.get('schema_version') == 1,
            'archive_root_identity_mismatch')
    require(marker.get('authoritative_root') == DEFAULT_ROOT, 'archive_root_identity_mismatch')
    return root


def validate_reference(record):
    require(type(record) is dict and record.get('kind') == REFERENCE_KIND
            and type(record.get('schema_version')) is int and record['schema_version'] == 1,
            'archive_reference_schema')
    require(type(record.get('sha256')) is str and
            re.fullmatch('[0-9a-f]{64}', record['sha256']) is not None,
            'archive_reference_digest')
    require(type(record.get('bytes')) is int and record['bytes'] >= 0,
            'archive_reference_bytes')
    require(record.get('archive_root') == DEFAULT_ROOT, 'archive_reference_root')
    require(record.get('object') == 'objects/sha256/'+record['sha256'][:2]+'/'+record['sha256'],
            'archive_reference_object')
    return record


def resolve(record, root=None):
    """Return a verified, read-only source path; never trust a server path alone."""
    record = validate_reference(record)
    root = _root(_configured_root(root))
    path = root/record['object']
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'archive_object_symlink')
    require(path.is_file() and path.stat().st_size == record['bytes'], 'archive_object_missing_or_size')
    require(_sha(path) == record['sha256'], 'archive_object_digest')
    return path


def store(source, root=None):
    """Copy exact bytes, verify the destination, and return a Git-sized reference."""
    source = Path(source).resolve(strict=True)
    require(source.is_file(), 'archive_source_not_file')
    root = _root(_configured_root(root))
    directory = root/'objects'/'sha256'
    directory.mkdir(parents=True, exist_ok=True)
    require(not any(p.is_symlink() for p in (directory, *directory.parents)), 'archive_object_symlink')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix='.incoming-', delete=False) as target:
            temporary = Path(target.name)
            digest = hashlib.sha256(); count = 0
            with source.open('rb') as stream:
                while chunk := stream.read(1024**2):
                    target.write(chunk); digest.update(chunk); count += len(chunk)
            target.flush(); os.fsync(target.fileno())
        digest = digest.hexdigest()
        require(source.stat().st_size == count and _sha(source) == digest,
                'archive_source_changed_during_copy')
        record = {'kind': REFERENCE_KIND, 'schema_version': 1,
                  'archive_root': DEFAULT_ROOT, 'object': 'objects/sha256/'+digest[:2]+'/'+digest,
                  'sha256': digest, 'bytes': count}
        target = root/record['object']; target.parent.mkdir(exist_ok=True)
        require(not target.parent.is_symlink(), 'archive_object_symlink')
        # Hard-link creation is exclusive and atomic. Existing objects are never
        # replaced, including when a concurrent store chose the same digest.
        try:
            os.link(temporary, target)
        except FileExistsError:
            pass
        resolve(record, root)
        return record
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def locate(path, root=None):
    """Compatibility for materialized bundles: original bytes or a checked sidecar."""
    path = Path(path)
    if path.is_file():
        return path
    sidecar = path.with_name(path.name+'.archive.json')
    require(sidecar.is_file(), 'archive_reference_missing:'+str(path))
    return resolve(load(sidecar), root)


def logical_file_names(directory):
    """Original package namespace, with explicit references instead of payloads."""
    result = set()
    directory = Path(directory)
    for path in directory.rglob('*'):
        require(not path.is_symlink(), 'archive_package_symlink')
        if not path.is_file():
            continue
        name = path.relative_to(directory).as_posix()
        if name.endswith('.archive.json'):
            validate_reference(load(path))
            name = name[:-len('.archive.json')]
        result.add(name)
    return result


def materialize(reference, output, root=None):
    """Create an explicit local cache file for native tools requiring a filename."""
    source = resolve(reference, root)
    output = Path(output).absolute()
    require('.git' not in output.parts, 'archive_materialization_inside_git_metadata')
    require(not any(p.is_symlink() for p in (output, *output.parents)), 'archive_cache_symlink')
    if output.exists():
        require(output.is_file() and output.stat().st_size == reference['bytes']
                and _sha(output) == reference['sha256'], 'archive_cache_collision')
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix='.archive-cache-', delete=False) as target:
            temporary = Path(target.name)
            with source.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024**2), b''):
                    target.write(chunk)
            target.flush(); os.fsync(target.fileno())
        require(temporary.stat().st_size == reference['bytes'] and _sha(temporary) == reference['sha256'],
                'archive_cache_copy_digest')
        os.link(temporary, output)
        return output
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def prepare_publication(source, output, root=None):
    """Archive a closed package and create a small Git publication directory.

    The original package namespace lives under output/package. Its historical
    checksums remain unchanged; the separate outer manifest lists physical Git
    files, including references. No Git index or remote is modified here.
    """
    from .history_guard import artifact_policy
    from .publisher import _new_report_artifact_policy
    source = Path(source).resolve(strict=True); requested = Path(output).absolute()
    require(not any(p.is_symlink() for p in (requested, *requested.parents)), 'archive_publication_output_symlink')
    output = requested.resolve()
    require(source.is_dir() and not output.exists() and not output.is_symlink(), 'archive_publication_new_directory_required')
    require(not output.is_relative_to(source) and not source.is_relative_to(output), 'archive_publication_overlapping_directories')
    paths = []
    for path in source.rglob('*'):
        require(not path.is_symlink(), 'archive_publication_source_symlink')
        if path.is_file():
            paths.append(path)
    require(paths, 'archive_publication_empty_package')
    output.mkdir(parents=True, exist_ok=False)
    physical = {}; originals = {}; external = 0
    for path in sorted(paths):
        name = path.relative_to(source).as_posix()
        if name.endswith('.archive.json'):
            resolve(load(path), root)
        reference = store(path, root); originals[name] = reference
        with path.open('rb') as stream:
            header = stream.read(512)
        externalize = False
        try:
            artifact_policy('Reports/StructTrain/TimeLearner/prepared/package/'+name,
                            reference['bytes'], header)
            _new_report_artifact_policy('Reports/StructTrain/TimeLearner/prepared/package/'+name,
                '100755' if os.name != 'nt' and path.stat().st_mode & 0o111 else '100644', header)
        except ValueError:
            externalize = True
        relative = 'package/'+name+('.archive.json' if externalize else '')
        require(relative not in physical, 'archive_publication_reference_path_collision')
        target = output/relative; target.parent.mkdir(parents=True, exist_ok=True)
        require(not target.exists(), 'archive_publication_reference_path_collision')
        raw = ((json.dumps(reference, sort_keys=True, indent=2)+'\n').encode() if externalize else path.read_bytes())
        if not externalize:
            require(hashlib.sha256(raw).hexdigest() == reference['sha256'], 'archive_publication_source_changed')
        target.write_bytes(raw); physical[relative] = hashlib.sha256(raw).hexdigest()
        external += externalize
    for name, record in originals.items():
        require((source/name).stat().st_size == record['bytes'] and _sha(source/name) == record['sha256'],
                'archive_publication_source_changed')
    require({p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()} == set(originals),
            'archive_publication_source_namespace_changed')
    inventory = (json.dumps(physical, sort_keys=True, indent=2)+'\n').encode()
    (output/'SHA256SUMS.json').write_bytes(inventory)
    return {'kind': 'nmsdk_external_archive_publication_view', 'schema_version': 1,
            'files_archived': len(originals), 'payloads_externalized': external,
            'manifest': str(output/'SHA256SUMS.json'), 'manifest_sha256': hashlib.sha256(inventory).hexdigest(),
            'scientific_verdict': None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=None)
    actions = parser.add_subparsers(dest='action', required=True)
    actions.add_parser('store').add_argument('source', type=Path)
    actions.add_parser('verify').add_argument('reference', type=Path)
    cache = actions.add_parser('materialize')
    cache.add_argument('reference', type=Path); cache.add_argument('output', type=Path)
    publication = actions.add_parser('prepare-publication')
    publication.add_argument('source', type=Path); publication.add_argument('output', type=Path)
    arguments = parser.parse_args(argv)
    if arguments.action == 'store':
        result = store(arguments.source, arguments.root)
    elif arguments.action == 'verify':
        result = {'verified_path': str(resolve(load(arguments.reference), arguments.root))}
    elif arguments.action == 'materialize':
        result = {'cache_path': str(materialize(load(arguments.reference), arguments.output, arguments.root))}
    else:
        result = prepare_publication(arguments.source, arguments.output, arguments.root)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
