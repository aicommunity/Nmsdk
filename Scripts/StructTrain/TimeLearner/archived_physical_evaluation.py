"""Read a complete archived eight-trial baseline without relabelling its job.

The catalog, compressed primary, bundle inventory, restoration receipt and every
restored member are bound together. This rechecks data and observations; it
does not reconstruct an original process owner or missing runtime provenance.
"""
from pathlib import Path, PurePosixPath
import re

from .native_evidence import load, require
from .runtime import file_record


def read_source(declaration):
    from .external_archive import validate_reference, _native_path
    from .native_pipeline_worker import audit_execution, validate_job
    from .portable_primary import _bundle_version, _name, _record, RETAIN_ALIASES

    require(type(declaration) is dict and set(declaration) == {
        'kind', 'schema_version', 'catalog', 'bundle', 'primary', 'restoration',
        'restored_root', 'native_prefix'} and
        declaration['kind'] == 'timelearner_archived_physical_evaluation' and
        type(declaration['schema_version']) is int and declaration['schema_version'] == 1,
        'archived_evaluation_source_schema')
    records = {}
    paths = {}
    for key in ('catalog', 'bundle', 'primary', 'restoration'):
        binding = declaration[key]
        require(type(binding) is dict and set(binding) == {'path', 'size', 'sha256'} and
                type(binding['path']) is str and Path(binding['path']).is_absolute() and
                type(binding['size']) is int and binding['size'] > 0 and
                type(binding['sha256']) is str and
                re.fullmatch('[0-9a-f]{64}', binding['sha256']) is not None,
                'archived_evaluation_file_binding')
        path = Path(binding['path'])
        require(path.resolve(strict=True) == path and not path.is_symlink() and
                not getattr(path, 'is_junction', lambda: False)() and
                file_record(path) == binding, 'archived_evaluation_bound_file_changed')
        paths[key] = path
        records[str(path)] = binding
    catalog, bundle = load(paths['catalog']), load(paths['bundle'])
    require(type(catalog) is dict and type(catalog.get('schema_version')) is int and
            catalog['schema_version'] == 1 and type(catalog.get('members')) is int,
            'archived_evaluation_catalog_schema')
    _bundle_version(bundle)
    members = bundle['members']
    require(type(members) is dict and 0 < len(members) <= 4096 and
            len(members) == catalog['members'], 'archived_evaluation_member_count')
    for name, record in members.items():
        _name(name)
        _record(record)
    require(sum(r['bytes'] for r in members.values()) <= 4*1024**3,
            'archived_evaluation_expanded_byte_limit')
    for field, name in (('bundle', 'bundle.json'), ('primary', 'primary.tar.xz')):
        reference = validate_reference(catalog['objects'][name])
        binding = declaration[field]
        require((binding['size'], binding['sha256']) ==
                (reference['bytes'], reference['sha256']), 'archived_evaluation_catalog_binding')
    primary = declaration['primary']
    require(type(bundle.get('archive_bytes')) is int and
            (bundle['archive_bytes'], bundle.get('archive_sha256')) ==
            (primary['size'], primary['sha256']), 'archived_evaluation_primary_binding')
    receipt = load(paths['restoration'])
    require(receipt.get('kind') == 'timelearner_native_bundle_restoration' and
            receipt.get('archive_sha256') == primary['sha256'] and
            receipt.get('archive_members_verified') == len(members) and
            receipt.get('retained_regular_files') == len(members) and
            receipt.get('compatibility') == RETAIN_ALIASES and
            receipt.get('omitted_redundant_aliases') == [] and
            receipt.get('source_archive_modified') is False and
            receipt.get('native_execution_attested') is False,
            'archived_evaluation_restoration_receipt')
    require(type(declaration['restored_root']) is str and
            Path(declaration['restored_root']).is_absolute(), 'archived_evaluation_root')
    root = _native_path(Path(declaration['restored_root']), long_descendants=True)
    require(root.resolve(strict=True) == root and root.is_dir() and not root.is_symlink() and
            not getattr(root, 'is_junction', lambda: False)(), 'archived_evaluation_root_alias')
    found = {}
    for path in root.rglob('*'):
        require(not path.is_symlink() and not getattr(path, 'is_junction', lambda: False)(),
                'archived_evaluation_member_alias')
        if path.is_file():
            name = path.relative_to(root).as_posix()
            require(name in members, 'archived_evaluation_unexpected_member')
            record = file_record(path)
            require(members[name] == dict(bytes=record['size'], sha256=record['sha256']),
                    'archived_evaluation_member_changed')
            found[name] = record
            records[str(path.resolve(strict=True))] = record
    require(set(found) == set(members), 'archived_evaluation_missing_member')
    prefix = declaration['native_prefix']
    _name(prefix)
    native = root.joinpath(*PurePosixPath(prefix).parts)
    require(native.resolve(strict=True) == native and native.is_dir(),
            'archived_evaluation_native_directory')
    job = load(native/'job.json')
    model = job['source_model_data']
    validate_job('physical-model-evaluate', job, (model,))
    audit = audit_execution('physical-model-evaluate', native, job, (model,))
    metrics = audit['metrics']
    require(audit['frozen_model_verified'] and metrics['validity'] == 'valid' and
            metrics['data_only'] and len(job['trials']) == len(metrics['trials']) == 8 and
            len({t['sample_id'] for t in job['trials']}) == 8 and
            sum(t['label'] == 'target' for t in job['trials']) == 1 and
            sum(t['label'] == 'foil' for t in job['trials']) == 7 and
            metrics['model_revision'] == model['model_revision'],
            'archived_evaluation_incomplete_baseline')
    require(all(file_record(Path(p)) == r for p, r in records.items()),
            'archived_evaluation_source_changed_during_audit')
    return dict(model=model, job=job, metrics=metrics, output=native.parent, records=records)
