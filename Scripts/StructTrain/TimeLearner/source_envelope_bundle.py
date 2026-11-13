"""Lossless primary package with exact jobs reconstructed from literal sources."""
import hashlib
from pathlib import Path, PurePosixPath
import re

from . import portable_primary
from .native_calibration_worker import _digest, _signed, _write
from .native_evidence import load, require
from .source_job_envelope import MAX_DOCUMENT_BYTES, factor, reference_encodings, restore as restore_job

KIND = 'timelearner_source_enveloped_primary'
MAX_TOTAL_BYTES = 64*1024**3


def _record(path):
    return dict(bytes=path.stat().st_size, sha256=portable_primary._sha(path))


def _members(members, maximum):
    require(type(maximum) is int and 0 < maximum <= MAX_TOTAL_BYTES,
            'envelope_bundle_total_budget')
    require(type(members) is dict and members, 'envelope_bundle_members_required')
    for name, row in members.items():
        portable_primary._name(name);portable_primary._record(row)
        require(not any(p.as_posix() in members for p in PurePosixPath(name).parents if p.as_posix() != '.'),
                'envelope_bundle_file_directory_collision')
    require(sum(r['bytes'] for r in members.values()) <= maximum, 'envelope_bundle_expansion_budget')


def assignments(rows, members):
    require(type(rows) is list and rows and len(rows) <= 10000, 'envelope_bundle_assignments_required')
    targets=set()
    for row in rows:
        require(type(row) is dict and set(row) == {'target', 'source'} and
            type(row['target']) is str and type(row['source']) is str and
            row['target'] in members and row['source'] in members and
            row['target'] != row['source'] and row['target'] not in targets and
            not portable_primary._alias(row['target']) and not portable_primary._alias(row['source']),
            'envelope_bundle_assignment')
        targets.add(row['target'])
    require(not any(row['source'] in targets for row in rows), 'envelope_bundle_reference_must_be_literal')
    return targets


def create(sources, rows, output, *, maximum_total_bytes, dictionary_bytes=32*1024**2):
    """Sources must already be owned/frozen by the caller; no execution proof."""
    require(type(sources) is dict and sources, 'envelope_bundle_sources_required')
    paths={name:Path(path).resolve(strict=True) for name,path in sources.items()}
    require(all(p.is_file() for p in paths.values()), 'envelope_bundle_regular_source_required')
    sizes={name:dict(bytes=p.stat().st_size,sha256='0'*64) for name,p in paths.items()}
    _members(sizes,maximum_total_bytes);assignments(rows,sizes)
    output=Path(output).absolute();require(not output.exists() and not output.is_symlink(),
                                         'envelope_bundle_fresh_output_required')
    output=output.parent.resolve(strict=True)/output.name
    require(all(not p.is_relative_to(output) for p in paths.values()), 'envelope_bundle_source_inside_output')
    records={name:_record(path) for name,path in paths.items()}
    output.mkdir();(output/'recipes').mkdir();recipes={};fallback={}
    cached_key=None;reference=None;prepared=None
    for row in sorted(rows,key=lambda r:(records[r['source']]['sha256'],r['target'])):
        target,source=row['target'],row['source']
        if max(records[target]['bytes'],records[source]['bytes']) > MAX_DOCUMENT_BYTES:
            fallback[target]='document_budget';continue
        key=(records[source]['sha256'],records[source]['bytes'])
        if key != cached_key:
            reference=paths[source].read_bytes();prepared=reference_encodings(reference);cached_key=key
        require(prepared['source'] == records[source], 'envelope_bundle_reference_changed')
        original=paths[target].read_bytes()
        recipe=factor(original,reference,prepared_reference=prepared)
        require(dict(bytes=len(original),sha256=hashlib.sha256(original).hexdigest()) == records[target],
                'envelope_bundle_original_changed')
        if recipe is None:
            fallback[target]='unsupported_encoding';continue
        relative='recipes/'+hashlib.sha256(target.encode('utf-8')).hexdigest()+'.json'
        _write(output/relative,recipe)
        recipes[target]=dict(source=source,path=relative,record=_record(output/relative))
    literal={name:path for name,path in paths.items() if name not in recipes}
    bundle=portable_primary.create_native_bundle(literal,output/'literals',
        dictionary_bytes=dictionary_bytes,deduplicate_content=True)
    require(all(_record(path) == records[name] for name,path in paths.items()),
            'envelope_bundle_source_changed_during_pack')
    index=_signed(dict(kind=KIND,schema_version=1,members=records,recipes=recipes,
        literal_fallbacks=fallback,literals_bundle=dict(path='literals/bundle.json',
            record=_record(output/'literals/bundle.json')),
        maximum_total_bytes=maximum_total_bytes,expanded_bytes=sum(v['bytes'] for v in records.values()),
        native_execution_attested=False,scientific_verdict=None))
    _write(output/'bundle.json',index)
    return dict(kind=KIND,schema_version=1,members=records,expanded_bytes=index['expanded_bytes'],
        archive_bytes=bundle['archive_bytes'],package_bytes=sum(p.stat().st_size for p in output.rglob('*') if p.is_file()),
        factored_files=len(recipes),literal_fallbacks=fallback,native_execution_attested=False,scientific_verdict=None)


def restore(bundle_path, output, *, compatibility=None):
    """Restore all original bytes before any production artifact audit."""
    bundle_path=Path(bundle_path).resolve(strict=True);package=bundle_path.parent
    index=load(bundle_path);_digest(index)
    require(set(index) == {'kind','schema_version','members','recipes','literal_fallbacks','literals_bundle',
        'maximum_total_bytes','expanded_bytes','native_execution_attested','scientific_verdict','sha256'} and
        index['kind'] == KIND and type(index['schema_version']) is int and index['schema_version'] == 1 and
        index['native_execution_attested'] is False and index['scientific_verdict'] is None,
        'envelope_bundle_schema')
    records=index['members'];_members(records,index['maximum_total_bytes'])
    require(type(index['expanded_bytes']) is int and index['expanded_bytes'] == sum(r['bytes'] for r in records.values()),
            'envelope_bundle_total_changed')
    recipes=index['recipes'];fallback=index['literal_fallbacks']
    require(type(recipes) is dict and set(recipes) <= set(records) and type(fallback) is dict and
        set(fallback) <= set(records)-set(recipes) and
        all(v in ('document_budget','unsupported_encoding') for v in fallback.values()),
        'envelope_bundle_recipe_inventory')
    expected={bundle_path.name,'literals/bundle.json','literals/primary.tar.xz'}
    for target,row in recipes.items():
        require(type(row) is dict and set(row) == {'source','path','record'} and
            type(row['source']) is str and row['source'] in records and row['source'] not in recipes and
            not portable_primary._alias(target) and not portable_primary._alias(row['source']) and
            type(row['path']) is str and re.fullmatch(r'recipes/[0-9a-f]{64}\.json',row['path']),
            'envelope_bundle_recipe_record')
        portable_primary._record(row['record']);expected.add(row['path'])
        require(not (package/row['path']).is_symlink() and _record(package/row['path']) == row['record'],
                'envelope_bundle_recipe_bytes_changed')
    actual=set()
    for p in package.rglob('*'):
        require(not p.is_symlink(), 'envelope_bundle_package_symlink')
        if p.is_file():actual.add(p.relative_to(package).as_posix())
    require(actual == expected, 'envelope_bundle_package_namespace_changed')
    literal=index['literals_bundle']
    require(type(literal) is dict and set(literal) == {'path','record'} and literal['path'] == 'literals/bundle.json',
            'envelope_bundle_literal_binding')
    require(_record(package/literal['path']) == literal['record'], 'envelope_bundle_literal_index_changed')
    literal_index=load(package/literal['path'])
    portable_primary._bundle_version(literal_index)
    require(literal_index['members'] == {n:r for n,r in records.items() if n not in recipes},
            'envelope_bundle_literal_members_changed')
    output=Path(output).resolve();require(not output.exists() and not output.is_relative_to(package) and
        not package.is_relative_to(output), 'envelope_bundle_new_separate_restore_required')
    portable_primary.restore_native_bundle(package/literal['path'],output,compatibility=compatibility)
    cached_key=None;reference=None;prepared=None
    for target,row in sorted(recipes.items(),key=lambda pair:(records[pair[1]['source']]['sha256'],pair[0])):
        source=row['source'];key=(records[source]['sha256'],records[source]['bytes'])
        if key != cached_key:
            reference=(output/source).read_bytes();prepared=reference_encodings(reference);cached_key=key
        require(prepared['source'] == records[source], 'envelope_bundle_restored_reference_changed')
        recipe=load(package/row['path'])
        require(recipe['source'] == records[source] and recipe['original'] == records[target],
                'envelope_bundle_recipe_binding_changed')
        original=restore_job(recipe,reference,prepared_reference=prepared)
        path=output/target;path.parent.mkdir(parents=True,exist_ok=True)
        require(path.parent.resolve().is_relative_to(output), 'envelope_bundle_restore_path_escape')
        with path.open('xb') as stream:stream.write(original)
    retained={n:r for n,r in records.items() if not (compatibility == portable_primary.ALIAS_ADAPTER and portable_primary._alias(n))}
    actual={p.relative_to(output).as_posix():_record(p) for p in output.rglob('*') if p.is_file()}
    require(actual == retained, 'envelope_bundle_restored_namespace_or_bytes_changed')
    return dict(restored_files=len(actual),reconstructed_job_files=len(recipes),all_primary_bytes_verified=True,
                run_manifests_rewritten=False,native_execution_attested=False,scientific_verdict=None)
