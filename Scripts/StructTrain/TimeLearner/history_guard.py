"""Reject experimental payloads anywhere in proposed Git ancestry.

Standard library only, so a verified copy can guard pushes independently of the
currently checked-out branch. The source of truth remains this module.
"""
import argparse
import ast
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

MAX_GIT_EXPERIMENT_BYTES = 1024**2
EXTERNAL_RESULT_SUFFIXES = frozenset({'.xz', '.gz', '.bz2', '.zip', '.7z', '.tar',
    '.zst', '.pack', '.bundle', '.bin', '.qz', '.npy', '.npz', '.h5', '.hdf5', '.pkl', '.pickle'})


def experiment_artifact(name):
    return any(name.casefold().startswith(prefix) for prefix in (
        'reports/structtrain/timelearner/', 'docs/structtrain/timelearner/',
        'docs/audit/timelearner-', 'scripts/structtrain/timelearner/tests/fixtures/',
        'tests/integration/data/native'))


def report_artifact(name):
    return name.casefold().startswith('reports/structtrain/timelearner/')


def artifact_policy(name, size, header=b''):
    if not experiment_artifact(name):
        return
    if size > MAX_GIT_EXPERIMENT_BYTES:
        raise ValueError('large_experiment_artifact_requires_archive:'+name)
    suffix = PurePosixPath(name).suffix.casefold()
    if suffix in EXTERNAL_RESULT_SUFFIXES:
        raise ValueError('binary_experiment_artifact_requires_archive:'+name)
    if report_artifact(name):
        if suffix in {'.png', '.svg', '.pdf'} and 'selected' not in [
                p.casefold() for p in PurePosixPath(name).parts[3:-1]]:
            raise ValueError('full_report_figure_requires_archive:'+name)
        if b'\0' in header and suffix not in {'.png', '.pdf'}:
            raise ValueError('binary_experiment_artifact_requires_archive:'+name)


def _git(repository, *args, data=None):
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1')
    result = subprocess.run(['git', '--no-replace-objects', '-C', str(repository),
        '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', *args],
        input=data, capture_output=True, env=environment, timeout=300)
    if result.returncode:
        raise ValueError('archive_history_guard_git_failed:'+args[0]+':'+
                         result.stderr.decode('utf-8', 'replace')[-600:])
    return result.stdout


def check_history(repository, commit, *, old=None):
    if not isinstance(commit, str) or not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('archive_history_guard_full_commit_required')
    if _git(repository, 'rev-parse', '--is-shallow-repository').strip() != b'false':
        raise ValueError('archive_history_guard_full_history_required')
    _git(repository, 'rev-parse', '--verify', commit+'^{commit}')
    revisions = [commit]
    if old and old != '0'*40:
        if not re.fullmatch('[0-9a-f]{40}', old):
            raise ValueError('archive_history_guard_invalid_old_commit')
        # Unknown advertised remote objects cannot be used as exclusions.
        available = subprocess.run(['git', '-C', str(repository), 'cat-file', '-e', old+'^{commit}'],
                                   capture_output=True, timeout=120)
        if available.returncode == 0:
            revisions.append('^'+old)
    # Inspect each changed path, not rev-list's first name for a shared blob.
    # --no-data keeps primary payloads out of memory. Commit messages still have
    # length-delimited data fields, which must be skipped before parsing M lines.
    raw = _git(repository, 'fast-export', '--no-data', *revisions)
    import io
    stream = io.BytesIO(raw); candidates = {}
    while line := stream.readline():
        if line.startswith(b'data '):
            size = int(line[5:])
            if len(stream.read(size)) != size:
                raise ValueError('archive_history_guard_truncated_export')
        elif line.startswith(b'M '):
            _, mode, oid, name = line.rstrip(b'\n').split(b' ', 3)
            if mode not in {b'100644', b'100755'}:
                continue
            if name.startswith(b'"'):
                name = ast.literal_eval('b'+name.decode('ascii'))
            name = name.decode('utf-8')
            if experiment_artifact(name):
                artifact_policy(name, 0)
                candidates.setdefault(oid.decode('ascii'), set()).add(name)
    if candidates:
        sizes = _git(repository, 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)',
                     data=('\n'.join(candidates)+'\n').encode())
        for line in sizes.decode('ascii').splitlines():
            fields = line.split()
            if len(fields) != 3 or fields[1] != 'blob':
                raise ValueError('archive_history_guard_missing_blob')
            oid, _, size = fields
            for name in candidates[oid]:
                artifact_policy(name, int(size))
    return {'kind': 'nmsdk_experiment_history_guard', 'schema_version': 1,
            'commit': commit, 'checked_blobs': len(candidates), 'scientific_verdict': None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path('.'))
    parser.add_argument('--new'); parser.add_argument('--old'); parser.add_argument('--pre-push', action='store_true')
    arguments = parser.parse_args(argv)
    try:
        results = []
        if arguments.pre_push:
            for line in sys.stdin:
                fields = line.split()
                if len(fields) != 4:
                    raise ValueError('archive_history_guard_invalid_push_input')
                _, new, _, old = fields
                if new != '0'*40:
                    results.append(check_history(arguments.repository, new, old=old))
        else:
            results.append(check_history(arguments.repository, arguments.new, old=arguments.old))
        print(json.dumps({'checked': results}))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print('Experiment archive policy: '+str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
