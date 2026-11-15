"""Build a shallow Git code projection with complete Git policy metadata.

Selection is explicit. Attribute/ignore/module files remain available as Git
objects even outside a sparse checkout, so checkout and strict status do not
silently depend on a reachable promisor remote. No checkout or source mutation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess


POLICY_FILES = {'.gitattributes', '.gitignore', '.gitmodules'}


def build_projection(repository, commit, prefixes, output):
    repository, output = Path(repository).resolve(strict=True), Path(output)
    if not re.fullmatch('[0-9a-f]{40}', commit) or not prefixes:
        raise ValueError('source_projection_commit_or_prefixes')
    for prefix in prefixes:
        value = prefix.removesuffix('/')
        if not value or str(PurePosixPath(value)) != value or value.startswith('/') or '\\' in value or '..' in value.split('/'):
            raise ValueError('source_projection_unsafe_prefix')
    env = {**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_OPTIONAL_LOCKS': '0'}
    def git(*args, **kwargs):
        return subprocess.check_output(['git', '-C', str(repository), *args], env=env, **kwargs)
    if git('rev-parse', '--verify', commit+'^{commit}').decode().strip() != commit:
        raise ValueError('source_projection_not_exact_commit')
    objects = [commit, git('rev-parse', commit+'^{tree}').decode().strip()]
    selected, policies = {}, {}
    for record in git('ls-tree', '-r', '-t', '-z', commit).split(b'\0'):
        if not record:
            continue
        metadata, encoded = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode('ascii').split(); name = encoded.decode('utf-8')
        if kind == 'tree':
            objects.append(oid)
        elif kind == 'blob':
            wanted = any(name.startswith(p) if p.endswith('/') else name == p for p in prefixes)
            policy = PurePosixPath(name).name in POLICY_FILES
            if wanted or policy:
                if mode not in ('100644', '100755'):
                    raise ValueError('source_projection_symlink_or_special_file:'+name)
                objects.append(oid)
                row = {'git_mode': mode, 'git_blob': oid}
                if wanted:
                    selected[name] = row
                if policy:
                    policies[name] = row
    if not selected:
        raise ValueError('source_projection_empty_selection')
    # Read policies too: a missing metadata blob must fail before producing a
    # supposedly usable pack, not during a later numerical job's source guard.
    inventory = {}
    process = subprocess.Popen(['git', '-C', str(repository), 'cat-file', '--batch'],
                               env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for name, row in sorted({**selected, **policies}.items()):
            process.stdin.write((row['git_blob']+'\n').encode()); process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3 or header[1] != b'blob':
                raise ValueError('source_projection_blob_unavailable:'+name)
            size = int(header[2])
            if size > 64*1024**2:
                raise ValueError('source_projection_file_budget:'+name)
            raw = process.stdout.read(size)
            if len(raw) != size or process.stdout.read(1) != b'\n':
                raise ValueError('source_projection_truncated_blob:'+name)
            inventory[name] = {**row, 'bytes': size, 'sha256': hashlib.sha256(raw).hexdigest()}
    finally:
        process.stdin.close()
        process.stdout.close()
        if process.wait() != 0:
            raise ValueError('source_projection_blob_reader_failed')
    raw = git('pack-objects', '--stdout', '--threads=1', input=('\n'.join(dict.fromkeys(objects))+'\n').encode())
    with output.open('xb') as stream:
        stream.write(raw)
    return {'kind': 'timelearner_git_source_projection', 'schema_version': 1, 'commit': commit,
            'shallow_root': True, 'prefixes': list(prefixes), 'selected_files': len(selected),
            'git_policy_files': sorted(policies), 'inventory': inventory,
            'pack': {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()},
            'full_SDK_verified': False, 'scientific_verdict': None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository'); parser.add_argument('commit'); parser.add_argument('output')
    parser.add_argument('--prefix', action='append', required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build_projection(args.repository, args.commit, args.prefix, args.output), sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
