"""Read-only inventory of one explicitly declared, closed native acceptance run.

No compilation, numerical trace parsing, Git writes, lease recovery or deletion.
Print original metadata as JSON; callers must preserve stdout bytes losslessly.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

from . import archive_retirement, collector_provenance as provenance
from . import closed_native_collection as collection, owned_native_job
from .native_evidence import require
from .resource_reservations import Reservations

ROOT = Path(__file__).resolve().parents[3]


def inventory(specification):
    require(__debug__, 'native_inventory_optimized_python_unsupported')
    spec_raw, _ = provenance._frozen(Path(specification), 1024**2)
    spec = provenance._json(spec_raw)
    collection._keys(spec, 'kind schema_version tool_commit base original_paths expected_source_commit '
                          'expected_source_files expected_planned expected_executed expected_passed '
                          'expected_failed_ids expected_outer_binding_sha256 old_lease_token',
                     'native_inventory_specification_schema')
    require(spec['kind'] == 'timelearner_closed_native_readonly_inventory' and
            type(spec['schema_version']) is int and spec['schema_version'] == 1,
            'native_inventory_specification_version')
    os.environ.update(GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0')
    def git(root, *arguments):
        return subprocess.check_output(['git','--no-replace-objects','-C',str(root),*arguments],
                                       stdin=subprocess.DEVNULL, timeout=60)
    require(git(ROOT,'rev-parse','HEAD').decode().strip() == spec['tool_commit'], 'native_inventory_tool_changed')
    base = provenance._canonical(Path(spec['base']))
    require(base in owned_native_job._BASES, 'native_inventory_base')
    collection._keys(spec['original_paths'], 'native-output controller source build runtime', 'native_inventory_paths')
    paths = {name: provenance._canonical(Path(value)) for name,value in spec['original_paths'].items()}
    require(all(p.is_dir() and p.is_relative_to(base) and p != base for p in paths.values()), 'native_inventory_path_scope')
    require(len(set(paths.values())) == len(paths) and
            all(a == b or not a.is_relative_to(b) for a in paths.values() for b in paths.values()),
            'native_inventory_overlapping_paths')
    output, controller, source = paths['native-output'], paths['controller'], paths['source']
    read = lambda path: collection._read(path)[0]
    state = owned_native_job.status(controller)
    outer = state['outer']
    require(not state['supervisor_live'] and not state['unbound_outer_intent'] and
            outer['all_processes_closed'] is True and
            outer['binding']['sha256'] == spec['expected_outer_binding_sha256'], 'native_inventory_outer_not_closed')
    children = {p.name.removeprefix('child-binding-').removesuffix('.json'): read(p)
                for p in controller.glob('child-binding-*.json')}
    collection.verify_child_records(controller, output, children, outer['binding'])
    terminal = read(output/'terminal.json')
    require(terminal['built'] is True and terminal['scientific_verdict'] is None and
            terminal['expected_cpp_cases'] == spec['expected_planned'] and
            terminal['audited_completed_cpp_cases'] == spec['expected_executed'] and
            terminal['actual_audited_assertion_passed_cpp_cases'] == spec['expected_passed'] and
            terminal['actual_audited_failed_cpp_ids'] == spec['expected_failed_ids'], 'native_inventory_outcome_changed')
    prepared = read(output/'canonical-preparation.json')
    runplan = prepared['current']['runplan']
    observed, failed = collection.verify_native_observations(output, runplan, children)
    selected = [test for leaf in runplan for test in leaf['expected_ids']]
    require(len(selected) == len(set(selected)) == spec['expected_planned'] and
            len(observed) == len(set(observed)) == spec['expected_executed'] and
            failed == spec['expected_failed_ids'] and len(observed)-len(failed) == spec['expected_passed'],
            'native_inventory_actual_cpp_ids_changed')
    leases = [row for row in Reservations.read_snapshot(base/'resource-reservations.sqlite3')['leases']
              if row['token'] == spec['old_lease_token']]
    require(len(leases) == 1 and leases[0]['state'] == 'released', 'native_inventory_original_lease_not_released')
    owner = leases[0]['owner']
    require(owner['pid'] == outer['binding']['initial_main_pid'] and
            owner['start_ticks'] == outer['binding']['initial_start_ticks'], 'native_inventory_lease_owner_changed')
    before, after = read(output/'source-closure.json'), read(output/'source-closure-after.json')
    require(before == after and after['root']['head'] == spec['expected_source_commit'], 'native_inventory_source_changed')
    namespace = {}
    for name,row in after.items():
        repository = source if name == 'root' else source/name
        require(git(repository,'rev-parse','HEAD').decode().strip() == row['head'] and
                not git(repository,'status','--porcelain','--untracked-files=no','--ignore-submodules=all').strip(),
                'native_inventory_source_git_changed')
        for entry in git(repository,'ls-files','--stage','-z').split(b'\0'):
            if not entry:
                continue
            metadata, relative = entry.split(b'\t',1)
            mode, blob, stage = metadata.decode().split()
            require(stage == '0', 'native_inventory_unmerged_source')
            if mode == '160000':
                continue
            path = repository/relative.decode('utf-8')
            if not path.exists() and not path.is_symlink():
                continue
            require(mode in ('100644','100755'), 'native_inventory_source_type')
            _, record = provenance._frozen(path, 64*1024**2)
            key = path.relative_to(source).as_posix()
            require(key not in namespace, 'native_inventory_duplicate_source')
            namespace[key] = {'git_mode':mode,'git_blob':blob,'bytes':record['bytes'],'sha256':record['sha256']}
    require(len(namespace) == spec['expected_source_files'], 'native_inventory_source_count')
    collection._source_namespace(source, namespace)
    roles, links, total = [], {}, 0
    for tag in ('native-output','controller'):
        root = paths[tag]; links[tag] = {}
        for path in sorted(root.rglob('*')):
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                continue
            relative = path.relative_to(root).as_posix()
            if stat.S_ISLNK(mode):
                links[tag][relative] = archive_retirement._link(path)
                continue
            require(stat.S_ISREG(mode) and len(roles) < 4096, 'native_inventory_original_type_or_count')
            raw, record = provenance._frozen(path, min(64*1024**2,512*1024**2-total))
            total += len(raw)
            roles.append({'role':'original-'+str(len(roles)),'root':str(root),'relative_path':relative,
                'expected_bytes':record['bytes'],'expected_sha256':record['sha256'],
                'maximum_bytes':max(record['bytes'],1),'staged_name':'original-%04d.dat'%len(roles),
                'archive_path':tag+'/'+relative})
    cache = paths['build']/'CMakeCache.txt'
    raw, record = provenance._frozen(cache,16*1024**2)
    require(raw == provenance._frozen(output/'CMakeCache-terminal.txt',16*1024**2)[0], 'native_inventory_saved_cache_changed')
    total += len(raw);require(total <= 512*1024**2, 'native_inventory_total_size')
    roles.append({'role':'actual-cmake-cache','root':str(paths['build']),'relative_path':'CMakeCache.txt',
        'expected_bytes':record['bytes'],'expected_sha256':record['sha256'],'maximum_bytes':max(record['bytes'],1),
        'staged_name':'actual-CMakeCache.txt','archive_path':'postclosure-build/CMakeCache.txt'})
    runtime = paths['runtime']; snapshot = archive_retirement.snapshot(runtime.parent,[runtime.name])
    projected = collection._regular_projection(snapshot,runtime.name)
    projected.update({name:{'kind':'symlink','text':row['link_text']} for name,row in snapshot['links'][runtime.name].items()})
    require(projected == read(output/'current-runtime-after.json'), 'native_inventory_runtime_changed')
    availability = []
    for rule in read(output/'job.json')['artifacts']:
        candidates = sorted(output.glob(rule['glob']))
        matches = [p.relative_to(output).as_posix() for p in candidates if stat.S_ISREG(p.lstat().st_mode)]
        availability.append({**rule,'actual_count':len(matches),'present_paths':matches,
            'nonregular_matches':[{'path':p.relative_to(output).as_posix(),'mode':p.lstat().st_mode}
                                  for p in candidates if not stat.S_ISREG(p.lstat().st_mode)],
            'within_declared_count_bounds':len(matches) >= rule['minimum'] and
                (rule['maximum'] is None or len(matches) <= rule['maximum'])})
    return {'kind':'closed_native_readonly_capture_inventory','schema_version':1,'source_root':spec['expected_source_commit'],
        'original_terminal':terminal,'outer':outer,'children':children,'released_original_lease':leases[0],
        'source_before_equals_after':True,'source_namespace_physical_tracked_postclosure':namespace,
        'source_namespace_count':len(namespace),'files':roles,'captured_file_count':len(roles),'captured_total_bytes':total,
        'retained_symlinks_no_follow':links,'runtime_retained_symlinks_no_follow':snapshot['links'][runtime.name],
        'runtime_postclosure_matches_saved_after':projected,'artifact_availability':availability,
        'original_outcome':{'planned':len(selected),'executed':len(observed),'passed':len(observed)-len(failed),
                            'failed_ids':failed,'not_completed_ids':[test for test in selected if test not in observed]},
        'rawCSV_values_parsed':False,'file_or_git_or_lease_writes':False,'scientific_verdict':None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('specification',type=Path)
    args = parser.parse_args()
    print(json.dumps(inventory(args.specification),allow_nan=False))


if __name__ == '__main__':
    main()
