"""Lossless primary bundles that reuse source files already committed to Git.

Run manifests and native data are never rewritten. Restore reconstructs every
original file byte for byte before a production audit is allowed to consume it.
References identify an immutable Git archive blob, never a worker cache path.
"""
from collections import defaultdict
import hashlib
import io
import lzma
from pathlib import Path
import re
import subprocess
import tarfile

from .native_calibration_worker import _digest, _signed, _write
from .native_evidence import EvidenceError, count, load, require

LIMIT = 2*1024**3


def _name(name):
    require(type(name) is str and name and not name.startswith('/') and ':' not in name and '\\' not in name and
            all(p not in ('', '.', '..') for p in name.split('/')), 'unsafe_reuse_member_path')
    return name


def _record(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def _records(records):
    require(type(records) is dict and records, 'missing_reuse_original_members')
    for name, row in records.items():
        _name(name)
        require(type(row) is dict and set(row) == {'bytes', 'sha256'} and type(row['bytes']) is int and
                0 <= row['bytes'] <= LIMIT and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
                'invalid_reuse_member_record')
    require(sum(row['bytes'] for row in records.values()) <= LIMIT, 'reuse_expansion_budget_exceeded')


def _git_archive(repository, reference):
    require(type(reference['commit']) is str and re.fullmatch('[0-9a-f]{40}', reference['commit']), 'reuse_requires_full_git_commit')
    path = _name(reference['archive_path'])
    from .history import read_bytes
    try:
        raw = read_bytes(repository, reference['commit'], path, maximum_bytes=512*1024**2)
    except EvidenceError as error:
        if str(error) == 'historical_blob_budget_exceeded':
            raise EvidenceError('reuse_reference_compressed_budget_exceeded') from error
        raise EvidenceError('reuse_git_archive_unavailable:'+str(error)) from error
    require(0 < len(raw) <= 512*1024**2, 'reuse_reference_compressed_budget_exceeded')
    if 'archive_sha256' in reference:
        require(hashlib.sha256(raw).hexdigest() == reference['archive_sha256'], 'reuse_git_archive_changed')
    return raw


def _stream(raw):
    """Only regular safe members; no links, duplicate names or device entries."""
    seen = set();size = 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r|xz') as archive:
        for member in archive:
            name = _name(member.name)
            require(member.isfile() and name not in seen, 'reuse_archive_member_type_or_duplicate')
            seen.add(name);size += member.size
            require(member.size >= 0 and size <= LIMIT, 'reuse_expansion_budget_exceeded')
            data = archive.extractfile(member).read()
            require(len(data) == member.size, 'reuse_member_truncated')
            yield name, data


def pack(directory, repository, commit, archive_path, output):
    directory, output = Path(directory).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(directory) and not directory.is_relative_to(output),
            'reuse_requires_separate_new_bundle')
    original = load(directory/'bundle.json');records = original['members'];_records(records)
    require(original['acceptance_status'] == 'passed', 'reuse_requires_closed_accepted_evidence')
    candidates = {name: row for name, row in records.items() if re.fullmatch(r'runs/[^/]+/input/source/[^/]+', name)}
    require(candidates, 'reuse_requires_explicit_input_source_members')
    reference = {'commit': commit, 'archive_path': archive_path}
    reference_raw = _git_archive(repository, reference)
    reference['archive_sha256'] = hashlib.sha256(reference_raw).hexdigest()
    wanted = {(r['sha256'], r['bytes'], Path(n).name) for n, r in candidates.items()}
    found = {}
    for name, raw in _stream(reference_raw):
        row = _record(raw);key = (row['sha256'], row['bytes'], Path(name).name)
        if key in wanted and key not in found:
            found[key] = name
    reused = {}
    for name, row in candidates.items():
        key = (row['sha256'], row['bytes'], Path(name).name)
        require(key in found, 'reuse_source_not_found_in_git:'+name)
        reused[name] = found[key]
    output.mkdir(parents=True)
    # A large dictionary also avoids repeating inline source packages in job
    # envelopes. It changes compression only, not a single primary byte.
    destination = output/'primary.tar.xz'
    filters = [{'id': lzma.FILTER_LZMA2, 'preset': 3, 'dict_size': 64*1024**2}]
    # tarfile.xzopen does not forward arbitrary LZMA filters on the supported
    # Python versions. Own the compression stream and pass a plain tar stream.
    with lzma.open(destination, 'wb', filters=filters) as compressed_stream:
        with tarfile.open(fileobj=compressed_stream, mode='w') as archive:
            for name, row in records.items():
                path = directory/name
                require(path.resolve(strict=True).is_relative_to(directory) and not path.is_symlink(), 'reuse_source_file_escape')
                raw = path.read_bytes();require(_record(raw) == row, 'reuse_original_file_changed:'+name)
                if name in reused:
                    continue
                info = tarfile.TarInfo(name);info.size = len(raw);info.mode = 0o644
                archive.addfile(info, io.BytesIO(raw))
    compressed = destination.read_bytes()
    metadata = _signed({'kind': 'timelearner_reused_primary_bundle', 'schema_version': 1,
        'original_bundle': original, 'reference': reference, 'reused_members': reused,
        'archive_sha256': hashlib.sha256(compressed).hexdigest(), 'archive_bytes': len(compressed)})
    _write(output/'reuse.json', metadata)
    return {'reused_files': len(reused), 'retained_files': len(records)-len(reused), 'archive_bytes': len(compressed),
            'original_archive_bytes': original['archive_bytes'], 'scientific_verdict': None}


def restore(bundle, repository, output):
    bundle, output = Path(bundle).resolve(strict=True), Path(output).resolve()
    metadata = load(bundle/'reuse.json');_digest(metadata)
    require(set(metadata) == {'kind', 'schema_version', 'original_bundle', 'reference', 'reused_members', 'archive_sha256',
            'archive_bytes', 'sha256'} and metadata['kind'] == 'timelearner_reused_primary_bundle' and
            type(metadata['schema_version']) is int and metadata['schema_version'] == 1, 'unknown_primary_reuse_bundle')
    require(not output.exists() and not output.is_relative_to(bundle) and not bundle.is_relative_to(output), 'reuse_requires_new_restore_directory')
    records, reused = metadata['original_bundle']['members'], metadata['reused_members'];_records(records)
    require(type(reused) is dict and reused and set(reused) <= set(records), 'invalid_reused_member_set')
    for name, member in reused.items():
        _name(name);_name(member)
        require(re.fullmatch(r'runs/[^/]+/input/source/[^/]+', name), 'reuse_not_an_input_source_member')
    reference = metadata['reference']
    require(type(reference) is dict and set(reference) == {'commit', 'archive_path', 'archive_sha256'}, 'invalid_reuse_git_reference')
    reference_raw = _git_archive(repository, reference)
    from .external_archive import locate
    compressed = locate(bundle/'primary.tar.xz').read_bytes()
    require(len(compressed) == count(metadata['archive_bytes']) and hashlib.sha256(compressed).hexdigest() == metadata['archive_sha256'],
            'reuse_primary_archive_changed')
    output.mkdir(parents=True);written = set()
    def write(name, raw):
        require(name in records and name not in written and _record(raw) == records[name], 'reuse_restored_member_changed:'+name)
        path = output/_name(name);path.parent.mkdir(parents=True, exist_ok=True)
        require(path.parent.resolve().is_relative_to(output), 'reuse_restore_path_escape')
        with path.open('xb') as stream:stream.write(raw)
        written.add(name)
    retained = set(records)-set(reused)
    for name, raw in _stream(compressed):
        require(name in retained, 'reuse_unexpected_primary_member')
        write(name, raw)
    require(written == retained, 'reuse_missing_retained_member')
    targets = defaultdict(list)
    for name, member in reused.items():targets[member].append(name)
    for member, raw in _stream(reference_raw):
        for name in targets.pop(member, []):write(name, raw)
    require(not targets and written == set(records), 'reuse_missing_referenced_member')
    return {'restored_files': len(written), 'reused_files': len(reused), 'all_primary_bytes_verified': True,
            'run_manifests_rewritten': False, 'scientific_verdict': None}
