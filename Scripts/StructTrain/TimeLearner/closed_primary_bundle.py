"""Stream an explicitly inventoried, closed owned job into a lossless bundle.

Collection success attests bytes and closure only, never learning or science.
Original files and outcome records are not rewritten. Glog aliases are retained
as identical regular archive members; no arbitrary symlink is followed.
"""
import os
from pathlib import Path, PurePosixPath

from . import contained_process, portable_primary
from .closed_native_collection import verify_closed_namespace
from .collector_provenance import _canonical, _relative
from .native_evidence import require


BASES = {Path('/home/user/timelearner-refactor'), Path('/media/user/Data/TimeLearnerRefactor')}


def validate_manifest(value):
    fields = {'kind', 'schema_version', 'base', 'roots', 'closed_units', 'bounds', 'scientific_verdict'}
    require(type(value) is dict and
        ((value.get('schema_version') == 1 and set(value) == fields) or
         (value.get('schema_version') == 2 and set(value) == fields | {'controller_join'})) and
        value['kind'] == 'timelearner_closed_primary_bundle' and
        type(value['schema_version']) is int and
        value['scientific_verdict'] is None, 'primary_bundle_manifest_schema')
    base = _canonical(Path(value['base']))
    require(base in BASES and os.name == 'posix', 'primary_bundle_worker_base')
    bounds = value['bounds']
    require(type(bounds) is dict and set(bounds) == {'maximum_file_bytes', 'maximum_total_bytes',
        'maximum_archive_bytes'} and all(type(v) is int and 0 < v < 2**63 for v in bounds.values()) and
        bounds['maximum_file_bytes'] <= bounds['maximum_total_bytes'], 'primary_bundle_byte_limits')
    require(type(value['roots']) is list and 0 < len(value['roots']) <= 4,
            'primary_bundle_roots_required')
    directories, prefixes, total = [], [], 0
    for root in value['roots']:
        require(type(root) is dict and set(root) == {'directory', 'prefix', 'files', 'links'},
                'primary_bundle_root_schema')
        directory = _canonical(Path(root['directory']))
        require(directory.is_dir() and directory != base/'readbacks' and
                directory.is_relative_to(base/'readbacks'), 'primary_bundle_source_outside_readbacks')
        portable_primary._name(root['prefix'])
        require(type(root['files']) is dict and root['files'] and type(root['links']) is dict,
                'primary_bundle_finite_inventory_required')
        for name, record in root['files'].items():
            _relative(name)
            require(type(record) is dict and set(record) == {'bytes', 'sha256'} and
                type(record['bytes']) is int and 0 <= record['bytes'] <= bounds['maximum_file_bytes'] and
                type(record['sha256']) is str and len(record['sha256']) == 64 and
                all(c in '0123456789abcdef' for c in record['sha256']), 'primary_bundle_file_record')
            total += record['bytes']
        for name, record in root['links'].items():
            _relative(name)
            alias = PurePosixPath(name)
            require(alias.name in portable_primary.ALIASES and type(record) is dict and
                record.get('link_not_followed') is True and type(record.get('link_text')) is str,
                'primary_bundle_only_glog_aliases')
            target = PurePosixPath(record['link_text'])
            level = alias.name.removeprefix('NeuroModeler.')
            require(target.name == record['link_text'] and target.name.startswith('NeuroModeler.') and
                '.log.'+level+'.' in target.name and
                (alias.parent/target).as_posix() in root['files'], 'primary_bundle_alias_target')
            total += root['files'][(alias.parent/target).as_posix()]['bytes']
        directories.append(directory);prefixes.append(PurePosixPath(root['prefix']))
    require(total <= bounds['maximum_total_bytes'], 'primary_bundle_total_bytes_exceeded')
    for paths in (directories, prefixes):
        require(len(set(paths)) == len(paths) and all(not a.is_relative_to(b)
            for a in paths for b in paths if a != b), 'primary_bundle_overlapping_roots_or_prefixes')
    units = value['closed_units']
    require(type(units) is list and units and all(type(u) is dict and set(u) ==
        {'directory', 'binding'} and type(u['binding']) is dict for u in units),
        'primary_bundle_closed_units_required')
    declared = [Path(u['directory']) for u in units]
    require(len(set(declared)) == len(declared) and all(p.is_absolute() and
        any(p.is_relative_to(r) for r in directories) for p in declared), 'primary_bundle_unit_outside_source')
    if value['schema_version'] == 2:
        join = value['controller_join']
        require(type(join) is dict and set(join) ==
                {'kind', 'native_prefix', 'controller_prefix', 'original_job_path'} and
                join['kind'] == 'recorded-n4-roundtrip' and
                all(type(join[k]) is str for k in join), 'primary_bundle_controller_join_schema')
        roots = {r['prefix']: r for r in value['roots']}
        require(join['native_prefix'] != join['controller_prefix'] and
                join['native_prefix'] in roots and join['controller_prefix'] in roots and
                join['original_job_path'] == roots[join['native_prefix']]['directory'],
                'primary_bundle_controller_join_roots')
    return directories


def verify_controller_join(manifest):
    """Schema2 prevents a byte-valid archive of unrelated closed jobs."""
    if manifest['schema_version'] == 1:
        return None  # Historical byte/closure-only contract remains explicit.
    from .recorded_roundtrip_evidence import audit_roundtrip_controller
    join = manifest['controller_join']
    roots = {r['prefix']: r['directory'] for r in manifest['roots']}
    return audit_roundtrip_controller(roots[join['native_prefix']], roots[join['controller_prefix']],
                                      original_job_path=join['original_job_path'])


def resources(manifest, job, manifest_path, source):
    directories = validate_manifest(manifest)
    require(all(not job.is_relative_to(p) and not p.is_relative_to(job) for p in directories),
            'primary_bundle_output_overlaps_source')
    rows = [{'path': str(p), 'access': 'read'} for p in
            [*directories, Path(manifest_path).parent, source]]
    rows.append({'path': str(job), 'access': 'write'})
    return list({(r['path'], r['access']): r for r in rows}.values())


def verify_sources(manifest):
    directories = validate_manifest(manifest)
    for root in manifest['roots']:
        declarations = [dict(root=root['directory'], relative_path=n,
            expected_bytes=r['bytes'], expected_sha256=r['sha256']) for n, r in root['files'].items()]
        verify_closed_namespace(root['directory'], declarations, root['links'])
    verify_controller_join(manifest)
    # Every retained binding file belongs to the finite closure requirement.
    # Extra/unbound child records cannot silently fall outside the manifest.
    found = {p.parent for root in directories for p in root.rglob('owned-unit.json')}
    require(found == {Path(u['directory']) for u in manifest['closed_units']},
            'primary_bundle_unit_inventory_changed')
    observations = []
    for unit in manifest['closed_units']:
        state = contained_process.inspect(unit['directory'])
        require(state['binding'] == unit['binding'] and state['all_processes_closed'] is True,
                'primary_bundle_unit_not_closed_or_changed')
        observations.append({'directory': unit['directory'], 'observation': state})
    return observations


def collect(manifest, output, guard, emit):
    before = verify_sources(manifest);guard()
    output = _canonical(Path(output), exists=False)
    require(not output.exists() and all(not output.is_relative_to(Path(r['directory'])) and
        not Path(r['directory']).is_relative_to(output) for r in manifest['roots']),
        'primary_bundle_fresh_separate_output_required')
    sources = {}
    for root in manifest['roots']:
        for name in [*root['files'], *root['links']]:
            sources[(PurePosixPath(root['prefix'])/name).as_posix()] = Path(root['directory'])/name
    bundle = portable_primary.create_native_bundle(sources, output, dictionary_bytes=32*1024**2,
                                                   deduplicate_content=True)
    require(bundle['expanded_bytes'] <= manifest['bounds']['maximum_total_bytes'] and
            bundle['archive_bytes'] <= manifest['bounds']['maximum_archive_bytes'],
            'primary_bundle_output_budget')
    after = verify_sources(manifest);guard()
    emit('primary-bundle-proof.json', {'manifest': manifest, 'before': before, 'after': after,
        'bundle': {k:v for k,v in bundle.items() if k != 'members'},
        'collection_status': 'completed', 'original_files_rewritten': False,
        'original_outcome_unchanged': True, 'scientific_verdict': None})
    return bundle
