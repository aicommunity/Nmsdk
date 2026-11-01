"""Read-only Git verification of historical script retrieval and current absence.

No archived script is executed, copied back, or treated as scientific evidence.
This does not infer that every active tool has been migrated.
"""
import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess

from .history import resolve_revision
from .native_evidence import parse_json_bytes, require


def _git(repository, *arguments):
    result = subprocess.run(["git", "-C", str(repository), *arguments], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(result.returncode == 0, "migration_git_read_failed:"+arguments[0])
    return result.stdout


def _path(value):
    require(type(value) is str and value and "\\" not in value and ":" not in value
            and not PurePosixPath(value).is_absolute() and all(p not in ("", ".", "..") for p in value.split("/")),
            "invalid_migration_git_path")
    return value


def _sha(value, length=40):
    require(type(value) is str and re.fullmatch("[0-9a-f]{"+str(length)+"}", value) is not None,
            "invalid_migration_digest")
    return value


def _entry(repository, revision, path):
    raw = _git(repository, "ls-tree", revision, "--", path).decode("utf-8").strip()
    if not raw:return None
    metadata, actual_path = raw.split("\t", 1)
    require(actual_path == path, "migration_tree_path_mismatch")
    mode, kind, digest = metadata.split()
    return {"mode": mode, "kind": kind, "digest": digest}


def verify_migration(root, revision, bin_repository=None, pulselib_repository=None, mapping_file=None):
    root = Path(root).resolve(strict=True)
    resolved = resolve_revision(root, revision, mapping_file)
    target = resolved["resolved_revision"]
    repositories = {"root": root,
                    "Bin": Path(bin_repository or root/"Bin").resolve(strict=True),
                    "PulseLib": Path(pulselib_repository or root/"Libraries/Nmsdk-PulseLib").resolve(strict=True)}
    revisions = {"root": target}
    for name, path in (("Bin", "Bin"), ("PulseLib", "Libraries/Nmsdk-PulseLib")):
        entry = _entry(root, target, path)
        require(entry is not None and entry["mode"] == "160000" and entry["kind"] == "commit",
                "migration_submodule_gitlink_missing:"+name)
        revisions[name] = entry["digest"]
    for name, repository in repositories.items():
        require(Path(_git(repository, "rev-parse", "--show-toplevel").decode().strip()).resolve() == repository,
                "migration_repository_alias_mismatch:"+name)
        require(_git(repository, "cat-file", "-t", revisions[name]).strip() == b"commit",
                "migration_target_commit_missing:"+name)
    manifest = parse_json_bytes(_git(root, "show", target+":Docs/StructTrain/TimeLearner/script_migration.json"))
    require(type(manifest) is dict and manifest.get("kind") == "timelearner_script_migration" and type(manifest.get("schema_version")) is int
            and manifest["schema_version"] == 1 and type(manifest.get("complete")) is bool
            and type(manifest.get("retired_files")) is list and type(manifest.get("moved_files", [])) is list,
            "unknown_script_migration_manifest")
    checks = []; seen = set()
    for record in manifest["retired_files"]+manifest.get("moved_files", []):
        name = record["repository"];require(name in repositories, "unknown_migration_repository")
        path = _path(record["old_path"]);key = (name, path)
        require(key not in seen, "duplicate_migration_record");seen.add(key)
        original = _sha(record["archive_commit"])
        archive = resolve_revision(root, original, mapping_file)["resolved_revision"] if name == "root" else original
        repository = repositories[name]
        source = _entry(repository, archive, path)
        require(source is not None and source["kind"] == "blob" and source["mode"] in ("100644", "100755")
                and source["digest"] == _sha(record["blob_sha1"]), "migration_source_blob_mismatch:"+path)
        raw = _git(repository, "show", archive+":"+path)
        require(type(record["bytes"]) is int and record["bytes"] >= 0 and len(raw) == record["bytes"]
                and hashlib.sha256(raw).hexdigest() == _sha(record["content_sha256"], 64),
                "migration_source_content_mismatch:"+path)
        require(_entry(repository, revisions[name], path) is None, "migration_old_path_still_present:"+path)
        action = record["action"];replacement = record.get("replacement")
        if action == "retired_historical":
            require(replacement is None, "retired_script_must_not_have_wrapper")
        else:
            require(action == "moved_to_root" and replacement is not None, "unknown_migration_action")
            replacement = _path(replacement)
            require(replacement.startswith("Scripts/StructTrain/TimeLearner/"), "migration_replacement_outside_package")
            entry = _entry(root, target, replacement)
            require(entry is not None and entry["kind"] == "blob" and entry["mode"] in ("100644", "100755"),
                    "migration_replacement_missing:"+replacement)
        checks.append({"repository": name, "old_path": path, "archive_commit": original,
                       "resolved_archive_commit": archive, "blob_sha1": source["digest"],
                       "content_sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                       "action": action, "old_path_absent": True, "replacement": replacement})
    return {"kind": "timelearner_script_migration_verification", "schema_version": 1,
            "root_revision": resolved, "target_revisions": revisions, "checks": checks,
            "source_records_verified": len(checks), "manifest_declares_complete": manifest.get("complete") is True,
            "whole_migration_attested": False, "runtime_equivalence_attested": False, "scientific_verdict": None}
