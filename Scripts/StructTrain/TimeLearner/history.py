"""Resolve historical root SHA without modifying archived scientific provenance."""
import re
import subprocess
from pathlib import Path
from .native_evidence import load, parse_json_bytes, require


def resolve_revision(repository, original, mapping_file=None):
    require(type(original) is str and re.fullmatch("[0-9a-fA-F]{40}", original) is not None, "full_commit_sha_required")
    original=original.lower();repository=repository.resolve(strict=True)
    if mapping_file is None:
        maps = sorted((repository/'Docs/StructTrain/TimeLearner/History').glob('RootRevisionMap-*.json'))
    else:
        maps = [mapping_file]
    mapped=original
    for mapping_file in maps:
        if mapping_file.is_file():
            record=load(mapping_file)
            require(record.get("kind")=="nmsdk_root_revision_aliases" and type(record.get("schema_version")) is int
                    and record["schema_version"]==1 and type(record.get("mapping")) is dict, "unknown_root_revision_map")
            mapped=record["mapping"].get(mapped,mapped)
            require(type(mapped) is str and re.fullmatch('[0-9a-f]{40}', mapped), 'invalid_mapped_commit_sha')
    require(type(mapped) is str and re.fullmatch("[0-9a-f]{40}",mapped) is not None, "invalid_mapped_commit_sha")
    result=subprocess.run(["git","-C",str(repository),"cat-file","-t",mapped],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    require(result.returncode==0 and result.stdout.strip()=="commit", "mapped_revision_not_available")
    return {"kind":"nmsdk_root_revision_resolution","schema_version":1,"original_revision":original,
            "resolved_revision":mapped,"rewritten":mapped!=original,"scientific_verdict":None}


def read_bytes(repository, original, name, *, maximum_bytes=512*1024**2):
    """Historical content survives externalization without rewriting its provenance."""
    from pathlib import PurePosixPath
    from .external_archive import resolve
    require(type(name) is str and name and '\\' not in name and ':' not in name
            and not PurePosixPath(name).is_absolute()
            and all(p not in ('', '.', '..', '.git') for p in name.split('/')), 'invalid_historical_blob_path')
    require(type(maximum_bytes) is int and maximum_bytes > 0, 'invalid_historical_blob_budget')
    repository = Path(repository).resolve(strict=True)
    revision = resolve_revision(repository, original)['resolved_revision']

    def blob(path, budget):
        obj = revision+':'+path
        size = subprocess.run(['git', '--no-replace-objects', '-C', str(repository), 'cat-file', '-s', obj],
                              capture_output=True, timeout=120)
        if size.returncode:
            return None
        require(int(size.stdout) <= budget, 'historical_blob_budget_exceeded')
        return subprocess.check_output(['git', '--no-replace-objects', '-C', str(repository),
                                        'show', obj], timeout=120)

    raw = blob(name, maximum_bytes)
    if raw is not None:
        return raw
    reference = blob(name+'.archive.json', 64*1024)
    require(reference is not None, 'historical_blob_or_archive_reference_missing:'+name)
    record = parse_json_bytes(reference)
    require(type(record) is dict and type(record.get('bytes')) is int
            and record['bytes'] <= maximum_bytes, 'historical_blob_budget_exceeded')
    return resolve(record).read_bytes()
