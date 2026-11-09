"""Preserve one explicitly frozen, closed native acceptance run.

The original run, its sources and runtime are read only. This finite collector
uses the existing reservation, frozen-file and compact-primary mechanisms; it
does not launch/recover native jobs or infer a scientific verdict from cleanup.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import threading

from . import archive_retirement, collector_provenance as provenance
from . import closed_python_validation as markers
from . import contained_process, owned_native_job, owned_python_job, portable_primary
from .native_evidence import EvidenceError, require
from .native_acceptance_worker import observed_junit
from .resource_reservations import Reservations


ROOT = Path(__file__).resolve().parents[3]


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _read(path, maximum=16*1024**2):
    raw, record = provenance._frozen(Path(path), maximum)
    return provenance._json(raw), raw, record


def _keys(value, names, reason):
    require(type(value) is dict and set(value) == set(names.split()), reason)


def _regular_projection(snapshot, name):
    return {path: {'bytes': row['bytes'], 'sha256': row['sha256']}
            for path, row in snapshot['regular'][name].items()}


def verify_closed_namespace(directory, declarations, expected_links):
    """Reject added/missing files, not only mutations of the declared subset."""
    directory = provenance._canonical(Path(directory))
    expected = {}
    for row in declarations:
        require(Path(row['root']) == directory, 'native_collection_role_root')
        relative = provenance._relative(row['relative_path'])
        require(relative not in expected, 'native_collection_duplicate_regular_path')
        expected[relative] = {'bytes': row['expected_bytes'], 'sha256': row['expected_sha256']}
    # Check names and sizes before hashing: an undeclared large cache must not
    # turn a bounded frozen capture into an unbounded filesystem read.
    regular, links = set(), set()
    for path in directory.rglob('*'):
        entry = path.lstat()
        if stat.S_ISDIR(entry.st_mode):
            continue
        relative = path.relative_to(directory).as_posix()
        if stat.S_ISLNK(entry.st_mode):
            links.add(relative)
            continue
        require(stat.S_ISREG(entry.st_mode) and relative in expected and
                entry.st_size == expected[relative]['bytes'], 'native_collection_regular_namespace_changed')
        regular.add(relative)
    require(regular == set(expected), 'native_collection_regular_namespace_changed')
    require(links == set(expected_links), 'native_collection_link_namespace_changed')
    observed = archive_retirement.snapshot(directory.parent, [directory.name])
    require(_regular_projection(observed, directory.name) == expected,
            'native_collection_regular_namespace_changed')
    require(observed['links'][directory.name] == expected_links,
            'native_collection_link_namespace_changed')
    return expected


def verify_child_records(controller, output, expected, outer_binding):
    """The frozen finite child map must agree with intents, bindings and cleanup."""
    require(type(expected) is dict and expected, 'native_collection_children_required')
    intents = {p.name.removeprefix('child-intent-').removesuffix('.json'): p
               for p in controller.glob('child-intent-*.json')}
    bindings = {p.name.removeprefix('child-binding-').removesuffix('.json'): p
                for p in controller.glob('child-binding-*.json')}
    require(set(intents) == set(bindings) == set(expected), 'native_collection_child_map_changed')
    prepared, _, _ = _read(controller/'inputs/preparation.json')
    leaves = {r['name'] for r in prepared['current']['runplan']}
    require(set(expected) <= leaves, 'native_collection_child_outside_plan')
    result, _, _ = _read(controller/'supervisor-result.json')
    require(result['record_errors'] == [] and result['outer_closed'] is True and
            result['outer_binding'] == outer_binding and result['scientific_verdict'] is None,
            'native_collection_supervisor_cleanup_unproven')
    closed = result['children_closed']
    require(type(closed) is list and len(closed) == len(expected), 'native_collection_child_cleanup_count')
    for name, declaration in expected.items():
        directory = output/name/'process/contained'
        require(declaration['directory'] == str(directory), 'native_collection_child_directory')
        intent, _, _ = _read(intents[name]); binding, _, _ = _read(bindings[name])
        require(intent == {'directory': str(directory)} and binding == declaration,
                'native_collection_child_records_changed')
        state = contained_process.inspect(directory)
        require(state['all_processes_closed'] is True and state['binding'] == declaration['binding'],
                'native_collection_child_not_closed')
        matches = [row for row in closed if row['directory'] == str(directory)]
        require(len(matches) == 1 and matches[0]['closure']['all_processes_closed'] is True and
                matches[0]['closure']['binding'] == state['binding'], 'native_collection_child_cleanup_changed')
    return result


def _source_namespace(root, expected):
    physical = set()
    for directory, children, files in os.walk(root, followlinks=False):
        children[:] = [n for n in children if n != '.git']
        require(not any((Path(directory)/n).is_symlink() for n in children), 'native_collection_source_directory_link')
        for name in files:
            if name == '.git':
                continue
            path = Path(directory)/name
            require(not path.is_symlink(), 'native_collection_source_file_link')
            physical.add(path.relative_to(root).as_posix())
    require(physical == set(expected), 'native_collection_source_namespace_changed')
    for relative, row in expected.items():
        _, record = provenance._frozen(root/relative, 64*1024**2)
        require(record['bytes'] == row['bytes'] and record['sha256'] == row['sha256'],
                'native_collection_source_bytes_changed')


def verify_native_observations(output, runplan, children, incomplete_children=None):
    """Read actual JUnit, or retain a declared closed timeout with no XML.

    Ownership/kernel closure are checked independently by verify_child_records.
    This function never completes an expected ID from a process exit or plan.
    Schema1 callers omit incomplete_children and keep their original contract.
    """
    selected = {r['name']: r['expected_ids'] for r in runplan}
    incomplete_children = {} if incomplete_children is None else incomplete_children
    require(type(incomplete_children) is dict and set(incomplete_children) <= set(children),
            'native_collection_incomplete_child_scope')
    actual, failed = [], []
    for name in children:
        require(name in selected, 'native_collection_child_outside_plan')
        if name in incomplete_children:
            declaration = incomplete_children[name]
            _keys(declaration, 'execution gate_reason junit_state record_state',
                  'native_collection_incomplete_child_schema')
            require(declaration['execution'] == 'timeout' and declaration['junit_state'] == 'missing' and
                    declaration['record_state'] in ('missing', 'present'),
                    'native_collection_incomplete_child_contract')
            gate, _, _ = _read(output/(name+'-result.json'))
            copied, _, _ = _read(output/name/'result.json')
            process, _, _ = _read(output/name/'process/result.json')
            require(gate == copied and gate['execution'] == declaration['execution'] and
                    gate['reason'] == declaration['gate_reason'] and
                    gate['validity'] == 'incomplete_test_observation' and
                    gate['assertion_status'] == 'not_assessed' and gate['inventory'] is None and
                    gate['scientific_verdict'] is None and
                    process['execution'] == 'timeout' and process['all_processes_closed'] is True,
                    'native_collection_timeout_outcome_changed')
            require(not (output/name/'native.xml').exists(), 'native_collection_timeout_xml_state_changed')
            record_path = output/(name+'-actual-tests.json')
            require(record_path.exists() == (declaration['record_state'] == 'present'),
                    'native_collection_timeout_record_state_changed')
            if record_path.exists():
                record, _, _ = _read(record_path)
                require(record['source'] == 'native.xml' and
                        record['observed_ids'] == record['failed_ids'] == record['not_completed_ids'] == [] and
                        record['unobserved_expected_ids'] == selected[name] and
                        record['gate_execution'] == gate['execution'] and
                        record['gate_validity'] == gate['validity'] and record['gate_reason'] == gate['reason'] and
                        record['observation_error']['type'] == 'FileNotFoundError' and
                        record['scientific_verdict'] is None, 'native_collection_timeout_invented_cpp_observation')
            continue
        record, _, _ = _read(output/(name+'-actual-tests.json'))
        require(record['source'] == 'native.xml' and
                observed_junit(output/name/'native.xml') ==
                (record['observed_ids'], record['failed_ids'], record['not_completed_ids']),
                'native_collection_actual_junit_changed')
        require(record['not_completed_ids'] == [], 'native_collection_incomplete_cpp_case')
        actual += record['observed_ids']; failed += record['failed_ids']
    return actual, failed


def _check_original(manifest, observation):
    paths = {k: provenance._canonical(Path(v)) for k, v in manifest['original_paths'].items()}
    output, controller = paths['native-output'], paths['controller']
    terminal, _, _ = _read(output/'terminal.json')
    outcome = manifest['original_outcome']
    require(terminal == observation['original_terminal'] and terminal['built'] is True and
            terminal['expected_cpp_cases'] == outcome['planned'] and
            terminal['audited_completed_cpp_cases'] == outcome['executed'] and
            terminal['actual_audited_assertion_passed_cpp_cases'] == outcome['passed'] and
            terminal['actual_audited_failed_cpp_ids'] == outcome['failed_ids'] and
            terminal['scientific_verdict'] is None, 'native_collection_original_outcome_changed')
    pending = outcome['not_run_ids'] if manifest['schema_version'] == 1 else outcome['not_completed_ids']
    require(outcome['executed'] == outcome['passed']+len(outcome['failed_ids']) and
            outcome['planned'] == outcome['executed']+len(pending),
            'native_collection_original_count_mismatch')
    controller_state = owned_native_job.status(controller)
    require(not controller_state['supervisor_live'] and not controller_state['unbound_outer_intent'] and
            controller_state['outer']['all_processes_closed'] is True and
            controller_state['outer']['binding'] == observation['outer']['binding'],
            'native_collection_original_outer_not_closed')
    verify_child_records(controller, output, manifest['children'], observation['outer']['binding'])
    prepared, _, _ = _read(output/'canonical-preparation.json')
    selected = [i for leaf in prepared['current']['runplan'] for i in leaf['expected_ids']]
    actual, failed = verify_native_observations(output, prepared['current']['runplan'], manifest['children'],
        manifest.get('incomplete_children'))
    require(len(selected) == len(set(selected)) == outcome['planned'] and
            len(actual) == len(set(actual)) == outcome['executed'] and failed == outcome['failed_ids'] and
            [i for i in selected if i not in actual] == pending,
            'native_collection_actual_cpp_inventory_changed')
    rows = [r for r in Reservations.read_snapshot(Path(manifest['base'])/'resource-reservations.sqlite3')['leases']
            if r['token'] == manifest['old_lease_token']]
    require(len(rows) == 1, 'native_collection_original_lease_missing')
    markers.compare_released_lease(observation['released_original_lease'], rows[0])
    for tag in ('native-output', 'controller'):
        verify_closed_namespace(paths[tag], [r for r in manifest['regular_files'] if Path(r['root']) == paths[tag]],
                                observation['retained_symlinks_no_follow'][tag])
    _source_namespace(paths['source'], observation['source_namespace_physical_tracked_postclosure'])
    before, _, _ = _read(output/'source-closure.json')
    after, _, _ = _read(output/'source-closure-after.json')
    require(before == after, 'native_collection_original_source_closure_changed')
    for name, row in after.items():
        repository = paths['source'] if name == 'root' else paths['source']/name
        require(provenance._git(repository, 'rev-parse', 'HEAD').decode().strip() == row['head'] and
                not provenance._git(repository, 'status', '--porcelain', '--untracked-files=no',
                                    '--ignore-submodules=all').strip(), 'native_collection_source_git_changed')
    actual_cache, _ = provenance._frozen(paths['build']/'CMakeCache.txt', 16*1024**2)
    saved_cache, _ = provenance._frozen(output/'CMakeCache-terminal.txt', 16*1024**2)
    require(actual_cache == saved_cache, 'native_collection_saved_build_cache_changed')
    runtime = paths['runtime']
    snapshot = archive_retirement.snapshot(runtime.parent, [runtime.name])
    projected = _regular_projection(snapshot, runtime.name)
    projected.update({n: {'kind': 'symlink', 'text': v['link_text']} for n, v in snapshot['links'][runtime.name].items()})
    require(projected == observation['runtime_postclosure_matches_saved_after'] and
            snapshot['links'][runtime.name] == observation['runtime_retained_symlinks_no_follow'],
            'native_collection_runtime_changed')
    supervisor, _, _ = _read_json_lines(controller/'supervisor.log')
    require([v['binding'] for v in supervisor if v.get('kind') == 'STARTED'] == [observation['outer']['binding']],
            'native_collection_native_json_supervisor_binding')
    return controller_state


def _read_json_lines(path):
    raw, record = provenance._frozen(path, 1024**2)
    return [provenance._json(line) for line in raw.splitlines() if line.strip()], raw, record


def read_readonly_inventory(inventory):
    packed, packed_record = provenance._frozen(Path(inventory['path']), 1024**2)
    require(packed_record['bytes'] == inventory['compressed_bytes'] and
            packed_record['sha256'] == inventory['compressed_sha256'], 'native_collection_inventory_digest')
    require(type(inventory['raw_bytes']) is int and 0 < inventory['raw_bytes'] <= 16*1024**2,
            'native_collection_inventory_expanded_limit')
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        observed_raw = stream.read(inventory['raw_bytes']+1)
    require(len(observed_raw) == inventory['raw_bytes'] and _sha(observed_raw) == inventory['raw_sha256'],
            'native_collection_inventory_expanded_digest')
    return provenance._json(observed_raw)


def validate_original_roles(original_paths, regular_files):
    roots = {original_paths[tag]: tag for tag in ('native-output', 'controller')}
    if 'build' in original_paths:
        roots[original_paths['build']] = 'postclosure-build'
    archive_paths = []
    for row in regular_files:
        require(row['root'] in roots and row['archive_path'] == roots[row['root']]+'/'+
                provenance._relative(row['relative_path']), 'native_collection_original_role_scope')
        require(roots[row['root']] != 'postclosure-build' or row['relative_path'] == 'CMakeCache.txt',
                'native_collection_build_role_not_cache')
        archive_paths.append(row['archive_path'])
    require(archive_paths and len(archive_paths) == len(set(archive_paths)),
            'native_collection_original_archive_alias')


def collect(manifest_path, manifest_sha256):
    manifest, raw, record = _read(manifest_path, 1024**2)
    require(record['sha256'] == manifest_sha256, 'native_collection_manifest_digest')
    version = manifest.get('schema_version')
    _keys(manifest, 'kind schema_version tool base output repository parent collection_id original_paths '
          'readonly_inventory regular_files original_outcome children bounds supervisor_dialect old_lease_token scientific_verdict' +
          (' incomplete_children' if version == 2 else ''),
          'native_collection_manifest_schema')
    require(manifest['kind'] == 'timelearner_closed_native_acceptance_collection' and
            type(version) is int and version in (1, 2) and
            manifest['scientific_verdict'] is None and manifest['supervisor_dialect'] == 'owned-native-json-lines-v1',
            'native_collection_manifest_version')
    require(Path(manifest['tool']['path']) == ROOT, 'native_collection_tool_namespace')
    tool_before = owned_python_job._source_snapshot(ROOT, manifest['tool']['commit'])
    base = provenance._canonical(Path(manifest['base']))
    require(base in owned_native_job._BASES, 'native_collection_base')
    output = provenance._canonical(Path(manifest['output']), exists=False)
    repository = provenance._canonical(Path(manifest['repository']))
    require(output.is_relative_to(repository) and repository.is_relative_to(base) and not output.exists(),
            'native_collection_new_output_required')
    require(provenance._git(repository, 'rev-parse', 'HEAD').decode().strip() == manifest['parent'],
            'native_collection_evidence_parent')
    inventory = manifest['readonly_inventory']
    observation = read_readonly_inventory(inventory)
    bounds = manifest['bounds']
    require(bounds == {'maximum_capture_bytes': (64 if version == 1 else 256)*1024**2,
                       'maximum_output_bytes': (128 if version == 1 else 512)*1024**2,
                       'minimum_free_bytes': 512*1024**2}, 'native_collection_fixed_copy_bounds')
    validate_original_roles(manifest['original_paths'], manifest['regular_files'])
    _check_original(manifest, observation)
    declarations = list(manifest['regular_files'])
    for role, path, archive in [('frozen-manifest', Path(manifest_path), 'observer/frozen-inputs.json'),
                                ('readonly-inventory', Path(inventory['path']), 'observer/readonly-inventory.json.gz')]:
        _, entry = provenance._frozen(path, 1024**2)
        declarations.append(dict(role=role, root=str(path.parent), relative_path=path.name, expected_bytes=entry['bytes'],
            expected_sha256=entry['sha256'], maximum_bytes=max(entry['bytes'], 1), staged_name=role+'.dat', archive_path=archive))
    requirements = [provenance.RequiredFileRole(**{k: (Path(v) if k == 'root' else v)
        for k, v in row.items() if k != 'archive_path'}) for row in declarations]
    captured = provenance.capture_required_file_roles(requirements, maximum_total_bytes=bounds['maximum_capture_bytes'])
    read_roots = {str(ROOT), str(Path(manifest_path).parent), str(Path(inventory['path']).parent),
                  *manifest['original_paths'].values()}
    require(all(not owned_native_job._overlap(output, Path(p)) for p in read_roots), 'native_collection_input_output_overlap')
    require(shutil.disk_usage(output.parent).free >= bounds['minimum_free_bytes']+bounds['maximum_output_bytes'],
            'native_collection_free_space')
    registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
    require(not registry.managed_units, 'native_collection_managed_registry_unsupported')
    lease = registry.reserve(manifest['collection_id'], [{'path': str(output), 'access': 'write'}]+
        [{'path': p, 'access': 'read'} for p in sorted(read_roots)], ttl_seconds=120,
        demands={'slots': 1, 'memory_bytes': 512*1024**2, 'disk_bytes': bounds['maximum_output_bytes']}
        if registry.capacity is not None else None)
    stopped, errors = threading.Event(), []

    def heartbeat():
        while not stopped.wait(10):
            try:
                registry.heartbeat(lease['token'], ttl_seconds=120); registry.validate_paths(lease['token'])
            except BaseException as error:
                errors.append(str(error)); return

    thread = threading.Thread(target=heartbeat, daemon=True); thread.start()
    try:
        _check_original(manifest, observation)
        require(provenance.capture_required_file_roles(requirements, maximum_total_bytes=bounds['maximum_capture_bytes']).descriptor
                == captured.descriptor, 'native_collection_inputs_changed')
        output.mkdir(); identity = (output.stat().st_dev, output.stat().st_ino)
        staged = captured.materialize(output, output/'captured')
        sources = {r['archive_path']: staged['collector-file-inputs/'+r['staged_name']] for r in declarations}
        proof = dict(kind='closed_native_acceptance_capture', schema_version=version, capture_status='prepared_only',
            original_outcome=manifest['original_outcome'], regular_capture_descriptor=captured.descriptor,
            links_no_follow=observation['retained_symlinks_no_follow'], original_outer=observation['outer'],
            original_leaf=observation['leaf'], original_released_lease=observation['released_original_lease'],
            own_reservation=lease, collector_tool_snapshot=tool_before, original_model_JSON_CSV_rewritten=False,
            supervisor_dialect=manifest['supervisor_dialect'], capture_owned_supervisor_used=False, scientific_verdict=None)
        markers._write(output/'capture-proof.json', proof); sources['observer/capture-proof.json'] = output/'capture-proof.json'
        expanded = sum(p.stat().st_size for p in sources.values())
        require(expanded <= bounds['maximum_capture_bytes'], 'native_collection_expanded_budget')
        bundle = portable_primary.create_native_bundle(sources, output/'packed', dictionary_bytes=32*1024**2)
        require(bundle['expanded_bytes'] == expanded, 'native_collection_packed_byte_count')
        _check_original(manifest, observation)
        require(provenance.capture_required_file_roles(requirements, maximum_total_bytes=bounds['maximum_capture_bytes']).descriptor
                == captured.descriptor and owned_python_job._source_snapshot(ROOT, manifest['tool']['commit']) == tool_before,
                'native_collection_final_inputs_changed')
        require(not errors and shutil.disk_usage(output).free >= bounds['minimum_free_bytes']+4*1024**2 and
                sum(p.lstat().st_blocks*512 for p in output.rglob('*'))+4*1024**2 <= bounds['maximum_output_bytes'],
                'native_collection_final_budget_or_heartbeat')
        artifacts = {n: _sha((output/n).read_bytes()) for n in ('packed/primary.tar.xz', 'packed/bundle.json', 'capture-proof.json')}
    finally:
        stopped.set(); thread.join()
        registry.release(lease['token'], note='Closed native metadata preserved or collection failed; original outcome unchanged.')
    released = [r for r in Reservations.read_snapshot(registry.path)['leases'] if r['token'] == lease['token']]
    require(len(released) == 1 and released[0]['state'] == 'released' and not errors and
            all(released[0][k] == lease[k] for k in ('token', 'job_id', 'owner', 'resources')) and
            (output.stat().st_dev, output.stat().st_ino) == identity, 'native_collection_final_lease_or_directory')
    provenance._canonical(output)
    receipt = dict(kind='closed_native_acceptance_preservation_receipt', schema_version=version, collection_status='completed',
        original_outcome=manifest['original_outcome'], manifest_sha256=record['sha256'], artifact_hashes=artifacts,
        released_collection_lease=released[0], collector_external_cgroup_attested=False, scientific_verdict=None)
    artifacts['verification.json'] = markers._atomic_marker(output/'verification.json', receipt)['sha256']
    final = markers._atomic_marker(output/'artifact-inventory.json', artifacts)
    return dict(collection_status='completed', original_outcome=manifest['original_outcome'],
                artifact_inventory=final, released_collection_lease=released[0], scientific_verdict=None)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path); parser.add_argument('--manifest-sha256', required=True)
    arguments = parser.parse_args(argv)
    try:
        result = collect(arguments.manifest, arguments.manifest_sha256)
    except (EvidenceError, OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'collection_status': 'failed', 'reason': str(error), 'scientific_verdict': None}))
        return 2
    print(json.dumps(result, allow_nan=False)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
