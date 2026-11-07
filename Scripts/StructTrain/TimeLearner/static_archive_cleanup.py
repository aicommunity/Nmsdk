"""Remove explicitly retired duplicate link caches, retaining a verified copy.

Only regular, singly linked runtime-*/Lib.CMake/lib*.a files are eligible.
Sources, executables, shared libraries and experiment data are never targets.
The caller must own a write reservation for the entire root. Unregistered
writers are outside the reservation protocol; stop external builds first.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat


def _require(value, reason):
    if not value:
        raise ValueError(reason)


def _directory(path):
    path = Path(path).absolute()
    _require(path.resolve(strict=True) == path, 'archive_directory_alias')
    _require(all(not p.is_symlink() for p in (path, *path.parents)), 'archive_directory_symlink')
    s = path.stat()
    _require(stat.S_ISDIR(s.st_mode), 'archive_root_not_directory')
    return path, [s.st_dev, s.st_ino]


def _relative(value):
    _require(type(value) is str, 'invalid_archive_path')
    p = PurePosixPath(value)
    _require(not p.is_absolute() and len(p.parts) == 3 and str(p) == value and
             p.parts[0].startswith('runtime-') and p.parts[0] not in ('.', '..') and
             p.parts[1] == 'Lib.CMake' and p.name.startswith('lib') and p.suffix == '.a' and
             '\\' not in value, 'invalid_archive_path')
    return p


def _record(root, relative):
    p = root.joinpath(*_relative(relative).parts)
    _require(not p.is_symlink() and not p.parent.is_symlink() and not p.parent.parent.is_symlink(),
             'archive_path_symlink')
    _require(p.resolve(strict=True).is_relative_to(root), 'archive_path_escape')
    with p.open('rb') as stream:
        before = os.fstat(stream.fileno())
        _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'archive_not_independent_regular_file')
        _require(stream.read(8) == b'!<arch>\n', 'unsupported_archive_format')
        stream.seek(0)
        checksum = hashlib.sha256()
        for block in iter(lambda: stream.read(1024*1024), b''):
            checksum.update(block)
        digest = checksum.hexdigest()
        after = os.fstat(stream.fileno())
    identity = lambda s: [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_nlink]
    _require(identity(before) == identity(after) == identity(p.stat()), 'archive_changed_during_read')
    return {'path': relative, 'sha256': digest, 'identity': identity(after)}


def make_plan(root, retired_runtimes):
    """Read-only inventory; never infer retirement from a broad glob."""
    root, identity = _directory(root)
    _require(type(retired_runtimes) is list and retired_runtimes and
             len(set(retired_runtimes)) == len(retired_runtimes), 'explicit_retired_runtime_list_required')
    retired = set(retired_runtimes)
    for name in retired:
        _relative(name+'/Lib.CMake/libcheck.a')
        _directory(root/name)
    groups = {}
    scanned = 0
    for runtime in sorted(root.glob('runtime-*')):
        folder = runtime/'Lib.CMake'
        if runtime.is_symlink() or folder.is_symlink():
            raise ValueError('archive_inventory_directory_symlink')
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob('lib*.a')):
            row = _record(root, path.relative_to(root).as_posix())
            groups.setdefault((row['sha256'], row['identity'][2]), []).append(row)
            scanned += 1
    rows = []
    for group in groups.values():
        # Prefer a nonretired copy. If every duplicate is retired, keep one.
        keeper = min(group, key=lambda r: (_relative(r['path']).parts[0] in retired, r['path']))
        for row in group:
            if row != keeper and _relative(row['path']).parts[0] in retired:
                rows.append({'target': row, 'keeper': keeper})
    return {'kind': 'timelearner_duplicate_static_archive_plan', 'schema_version': 1,
            'root': str(root), 'root_identity': identity, 'retired_runtimes': sorted(retired),
            'files_scanned': scanned, 'rows': rows, 'bytes_planned': sum(r['target']['identity'][2] for r in rows),
            'scientific_verdict': None}


def _lease(registry, token, root):
    registry.validate_paths(token)  # Also verifies caller identity and held state.
    leases = [v for v in registry.inspect()['leases'] if v['token'] == token]
    _require(len(leases) == 1 and leases[0]['state'] == 'held' and
             any(r['canonical_path'] == str(root) and r['access'] == 'write'
                 for r in leases[0]['resources']), 'archive_cleanup_requires_whole_root_write_lease')


def apply_plan(plan, registry, token, journal):
    """Preflight the whole plan before unlinking; record every completed unlink.

    A partial operation is not resumed implicitly. Its fsynced journal and
    retained-copy mappings allow inspection/restoration before a new plan.
    """
    _require(plan['kind'] == 'timelearner_duplicate_static_archive_plan' and plan['schema_version'] == 1,
             'unsupported_archive_cleanup_plan')
    root, identity = _directory(plan['root'])
    _require(identity == plan['root_identity'], 'archive_root_changed')
    _lease(registry, token, root)
    targets = [r['target']['path'] for r in plan['rows']]
    _require(len(set(targets)) == len(targets), 'duplicate_archive_cleanup_target')
    checked = {}
    for row in plan['rows']:
        target, keeper = row['target'], row['keeper']
        _require(_relative(target['path']).parts[0] in plan['retired_runtimes'] and
                 keeper['path'] not in targets and target['path'] != keeper['path'] and
                 target['sha256'] == keeper['sha256'] and target['identity'][2] == keeper['identity'][2],
                 'archive_retention_mapping_invalid')
        for value in (target, keeper):
            if value['path'] not in checked:
                checked[value['path']] = _record(root, value['path'])
            _require(checked[value['path']] == value, 'archive_preimage_changed')
    _require(sum(r['target']['identity'][2] for r in plan['rows']) == plan['bytes_planned'],
             'archive_plan_size_mismatch')
    journal = Path(journal).absolute()
    _require(journal.is_relative_to(root) and journal.parent.resolve(strict=True) == journal.parent and
             journal.parent.name != 'Lib.CMake', 'archive_journal_outside_reserved_root')
    freed = 0
    with journal.open('x', encoding='utf-8') as stream:
        def emit(value):
            stream.write(json.dumps(value, sort_keys=True, allow_nan=False)+'\n')
            stream.flush()
            os.fsync(stream.fileno())
        emit({'event': 'validated_plan', 'plan': plan})
        for row in plan['rows']:
            _lease(registry, token, root)
            _require(_directory(root)[1] == identity, 'archive_root_changed')
            # Full fresh hash checks, including the retained copy, before each unlink.
            for value in (row['target'], row['keeper']):
                _require(_record(root, value['path']) == value, 'archive_preimage_changed')
            emit({'event': 'unlink_intent', **row})
            path = root.joinpath(*_relative(row['target']['path']).parts)
            path.unlink()
            directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
            freed += row['target']['identity'][2]
            emit({'event': 'unlinked', **row})
        receipt = {'event': 'complete', 'files_removed': len(targets), 'logical_bytes_removed': freed,
                   'all_retained_copies_verified': True, 'scientific_verdict': None}
        emit(receipt)
    return receipt
