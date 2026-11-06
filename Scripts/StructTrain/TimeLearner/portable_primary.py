"""Lossless native bundle restoration with an explicit legacy glog-alias adapter.

The source archive is never changed. The adapter omits only verified redundant
alias bytes from a new derived tree; native artifact auditors stay unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, load, require

ALIAS_ADAPTER = "dereferenced-glog-aliases-v1"
ALIASES = {"NeuroModeler."+s for s in ("INFO", "WARNING", "ERROR", "FATAL")}


def _sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def _name(name):
    require(type(name) is str and name and "\\" not in name and ":" not in name
            and not PurePosixPath(name).is_absolute()
            and all(p not in ("", ".", "..") for p in name.split("/")), "bundle_member_path_invalid")
    return name


def _record(record):
    require(type(record) is dict and set(record) == {"bytes", "sha256"}
            and type(record["bytes"]) is int and record["bytes"] >= 0
            and type(record["sha256"]) is str
            and re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) is not None,
            "bundle_member_record_invalid")


def _alias(name):
    parts = PurePosixPath(name).parts
    return len(parts) >= 3 and parts[-3:-1] == ("native.events-log", "EventsLog") and parts[-1] in ALIASES


def _alias_plan(root, members):
    plan = []
    for name in sorted(n for n in members if _alias(n)):
        path = root/name
        run = path.parents[2]
        manifest_path = run/"run-manifest.json"
        owner_path = run/"process/owned-process.json"
        require(manifest_path.relative_to(root).as_posix() in members
                and owner_path.relative_to(root).as_posix() in members, "bundle_alias_owner_missing")
        manifest, owner = load(manifest_path), load(owner_path)
        require(manifest.get("sha256") == canonical_model_sha256(
                    {k: v for k, v in manifest.items() if k != "sha256"}), "bundle_alias_manifest_digest_mismatch")
        require(type(owner.get("pid")) is int and owner["pid"] > 0, "bundle_alias_owner_invalid")
        records = manifest.get("artifacts")
        require(type(records) is list and all(type(r) is dict and set(r) == {"path", "bytes", "sha256"}
                for r in records), "bundle_alias_inventory_invalid")
        for record in records:
            _name(record["path"])
            _record({k: v for k, v in record.items() if k != "path"})
        indexed = {r["path"]: r for r in records}
        require(len(indexed) == len(records) and path.relative_to(run).as_posix() not in indexed,
                "bundle_alias_not_redundant")
        owner_record = indexed.get("process/owned-process.json")
        require(owner_record == {"path": "process/owned-process.json", "bytes": owner_path.stat().st_size,
                                  "sha256": _sha(owner_path)}, "bundle_alias_owner_inventory_mismatch")
        severity = path.name.split(".")[-1]
        pattern = re.compile(r"NeuroModeler\.[^/]+\.log\."+severity+r"\.\d{8}-\d{6}\."+str(owner["pid"]))
        candidates = []
        for candidate in path.parent.iterdir():
            if pattern.fullmatch(candidate.name) is None:
                continue
            relative = candidate.relative_to(root).as_posix()
            source_record = indexed.get(candidate.relative_to(run).as_posix())
            if (relative in members and members[relative] == members[name]
                    and source_record == {"path": candidate.relative_to(run).as_posix(), **members[relative]}):
                candidates.append(candidate)
        require(len(candidates) == 1, "bundle_alias_target_missing_or_ambiguous")
        plan.append({"omitted_alias": name, "retained_target": candidates[0].relative_to(root).as_posix(),
                     **members[name], "owner_pid": owner["pid"], "original_symlink_target_attested": False})
    return plan


def restore_native_bundle(bundle_path, output, *, compatibility=None):
    require(compatibility in (None, ALIAS_ADAPTER), "unknown_bundle_restoration_adapter")
    bundle_path = Path(bundle_path).resolve(strict=True)
    bundle = load(bundle_path)
    members = bundle.get("members")
    require(type(members) is dict and bool(members), "bundle_member_inventory_invalid")
    for name, record in members.items():
        _name(name); _record(record)
    require(compatibility == ALIAS_ADAPTER or not any(_alias(n) for n in members),
            "bundle_legacy_alias_requires_explicit_adapter")
    archive = bundle_path.parent/"primary.tar.xz"
    before = archive.stat()
    require(type(bundle.get("archive_bytes")) is int and bundle["archive_bytes"] == before.st_size
            and type(bundle.get("archive_sha256")) is str and _sha(archive) == bundle["archive_sha256"],
            "bundle_archive_hash_mismatch")
    output = Path(output).absolute()
    require(not output.exists() and not output.is_symlink(), "bundle_output_already_exists")
    output = output.parent.resolve(strict=True)/output.name
    output.mkdir(exist_ok=False)
    seen = set()
    with tarfile.open(archive, "r:xz") as stream:
        for member in stream:
            name = _name(member.name)
            require(member.isfile() and name not in seen and name in members,
                    "bundle_member_type_duplicate_or_unknown")
            require(member.size == members[name]["bytes"], "bundle_member_size_mismatch")
            seen.add(name)
            path = output/name
            require(path.resolve().is_relative_to(output), "bundle_member_path_escape")
            path.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256(); size = 0
            with stream.extractfile(member) as source, path.open("xb") as destination:
                for block in iter(lambda: source.read(1024**2), b""):
                    digest.update(block); size += len(block); destination.write(block)
            require({"bytes": size, "sha256": digest.hexdigest()} == members[name], "bundle_member_hash_mismatch")
    require(seen == set(members), "bundle_member_missing")
    after = archive.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), "bundle_archive_changed_during_restore")
    # Verify every adapter candidate before removing any redundant derived copy.
    plan = _alias_plan(output, members) if compatibility == ALIAS_ADAPTER else []
    for row in plan:
        path = output/row["omitted_alias"]
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == row["bytes"]
                and _sha(path) == row["sha256"], "bundle_alias_changed_before_omission")
        path.unlink()
    return {"kind": "timelearner_native_bundle_restoration", "schema_version": 1,
            "archive_sha256": bundle["archive_sha256"], "archive_members_verified": len(seen),
            "retained_regular_files": len(seen)-len(plan), "compatibility": compatibility,
            "omitted_redundant_aliases": plan, "source_archive_modified": False,
            "native_execution_attested": False, "scientific_verdict": None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--compatibility", choices=[ALIAS_ADAPTER])
    args = parser.parse_args(argv)
    try:
        result = restore_native_bundle(args.bundle, args.output, compatibility=args.compatibility)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (EvidenceError, OSError, ValueError, tarfile.TarError) as error:
        print(json.dumps({"restoration": "failed", "reason": str(error), "scientific_verdict": None}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
