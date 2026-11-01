"""Resolve historical root SHA without modifying archived scientific provenance."""
import re
import subprocess
from pathlib import Path
from .native_evidence import load, require


def resolve_revision(repository, original, mapping_file=None):
    require(type(original) is str and re.fullmatch("[0-9a-fA-F]{40}", original) is not None, "full_commit_sha_required")
    original=original.lower();repository=repository.resolve(strict=True)
    if mapping_file is None:
        mapping_file=repository/"Docs/StructTrain/TimeLearner/History/RootRevisionMap-2026-10-30.json"
    mapped=original
    if mapping_file.is_file():
        record=load(mapping_file)
        require(record.get("kind")=="nmsdk_root_revision_aliases" and type(record.get("schema_version")) is int
                and record["schema_version"]==1 and type(record.get("mapping")) is dict, "unknown_root_revision_map")
        mapped=record["mapping"].get(original,original)
    require(type(mapped) is str and re.fullmatch("[0-9a-f]{40}",mapped) is not None, "invalid_mapped_commit_sha")
    result=subprocess.run(["git","-C",str(repository),"cat-file","-t",mapped],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    require(result.returncode==0 and result.stdout.strip()=="commit", "mapped_revision_not_available")
    return {"kind":"nmsdk_root_revision_resolution","schema_version":1,"original_revision":original,
            "resolved_revision":mapped,"rewritten":mapped!=original,"scientific_verdict":None}
