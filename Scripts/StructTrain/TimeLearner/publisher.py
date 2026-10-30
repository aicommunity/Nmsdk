"""Publish an explicit immutable Git closure, children first, without force.

This proves commit reachability, not scientific validity or artifact completeness.
The caller must finish analysis/artifact gates before preparing this specification.
"""
from pathlib import Path, PurePosixPath
import json
import os
import re
import subprocess
from urllib.parse import urlsplit

from .native_evidence import EvidenceError, require


def _git(directory, *args):
    result = subprocess.run(["git", "-C", str(directory), *args], capture_output=True, timeout=120)
    require(result.returncode == 0, "git_operation_failed:"+args[0]+":"+
            result.stderr.decode("utf-8", errors="replace")[-3000:])
    return result.stdout.decode("utf-8", errors="strict").strip()


def _links(directory, commit):
    raw = subprocess.check_output(["git", "-C", str(directory), "ls-tree", "-rz", commit], timeout=120)
    links = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, kind, sha = metadata.decode("ascii").split()
        if mode == "160000":
            require(kind == "commit", "invalid_gitlink_type")
            links[name.decode("utf-8")] = sha
    return links


def _repository_identity(url):
    """Equivalent SSH/HTTPS transport for one host/path; no guessed relative URLs."""
    if "://" in url:
        parsed = urlsplit(url)
        if parsed.scheme == "file":
            require(not parsed.netloc, "unsupported_file_remote_host")
            return ("file", str(Path(parsed.path).resolve()))
        require(parsed.scheme in ("ssh", "https", "http", "git") and parsed.hostname
                and not parsed.query and not parsed.fragment, "unsupported_repository_url")
        default = {"ssh": 22, "https": 443, "http": 80, "git": 9418}[parsed.scheme]
        host = parsed.hostname.lower() if parsed.port in (None, default) else parsed.hostname.lower()+":"+str(parsed.port)
        return (host, parsed.path.strip("/").removesuffix(".git"))
    scp = re.fullmatch(r"(?:[^/@:]+@)?([^/:]+):(.+)", url)
    if scp:
        return (scp[1].lower(), scp[2].strip("/").removesuffix(".git"))
    require(Path(url).is_absolute(), "relative_repository_urls_require_explicit_resolution")
    return ("file", str(Path(url).resolve()))


def _module_urls(directory, commit):
    result = subprocess.run(["git", "-C", str(directory), "config", "--null", "--blob", commit+":.gitmodules",
                             "--get-regexp", r"^submodule\..*\.path$"], capture_output=True, timeout=120)
    require(result.returncode == 0, "missing_or_invalid_committed_gitmodules")
    urls = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        key, value = record.decode("utf-8").split("\n", 1)
        require(value not in urls, "duplicate_committed_submodule_path")
        urls[value] = _git(directory, "config", "--blob", commit+":.gitmodules", "--get", key[:-5]+".url")
    return urls


def publication_plan(root: Path, specification):
    require(type(specification) is dict and set(specification) == {"kind", "schema_version", "repositories"}
            and specification["kind"] == "timelearner_git_publication"
            and type(specification["schema_version"]) is int and specification["schema_version"] == 1,
            "unknown_publication_spec")
    require(type(specification["repositories"]) is list and bool(specification["repositories"]), "empty_publication")
    root = root.resolve(strict=True)
    records = {}
    for record in specification["repositories"]:
        require(type(record) is dict and set(record) == {"path", "commit", "remote", "branch"}, "invalid_publication_record")
        name = record["path"]
        require(type(name) is str and name and "\\" not in name and ":" not in name
                and not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts
                and (name == "." or PurePosixPath(name).as_posix() == name), "invalid_repository_path")
        require(name not in records, "duplicate_publication_repository")
        require(type(record["commit"]) is str and re.fullmatch(r"[0-9a-f]{40}", record["commit"]), "invalid_publication_commit")
        require(type(record["remote"]) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", record["remote"]),
                "invalid_publication_remote")
        require(type(record["branch"]) is str and record["branch"].startswith("refs/heads/"), "publication_requires_branch_ref")
        directory = (root/name).resolve(strict=True)
        require(directory == root or directory.is_relative_to(root), "repository_path_escapes_root")
        require(Path(_git(directory, "rev-parse", "--show-toplevel")).resolve() == directory,
                "uninitialized_or_wrong_repository:"+name)
        _git(directory, "check-ref-format", record["branch"])
        require(_git(directory, "rev-parse", record["branch"]+"^{commit}") == record["commit"], "local_branch_commit_mismatch:"+name)
        require(_git(directory, "rev-parse", "HEAD") == record["commit"], "checkout_commit_mismatch:"+name)
        require(not _git(directory, "status", "--porcelain", "--untracked-files=all"), "dirty_publication_repository:"+name)
        _git(directory, "remote", "get-url", "--push", record["remote"])
        records[name] = (directory, record)
    require("." in records, "missing_root_publication")
    ordered, visited = [], set()

    def visit(name):
        require(name not in visited, "duplicate_or_cyclic_publication_path")
        require(name in records, "missing_child_publication:"+name)
        visited.add(name)
        directory, record = records[name]
        links = _links(directory, record["commit"])
        urls = _module_urls(directory, record["commit"]) if links else {}
        require(set(urls) == set(links), "committed_submodule_paths_disagree_with_gitlinks")
        for relative, commit in sorted(links.items()):
            child = relative if name == "." else name+"/"+relative
            require(child in records and records[child][1]["commit"] == commit, "gitlink_commit_mismatch:"+child)
            child_directory, child_record = records[child]
            remote = child_record["remote"]
            push_url = _git(child_directory, "remote", "get-url", "--push", remote)
            fetch_url = _git(child_directory, "remote", "get-url", remote)
            require(_repository_identity(urls[relative]) == _repository_identity(push_url) == _repository_identity(fetch_url),
                    "child_remote_differs_from_committed_gitmodules:"+child)
            visit(child)
        ordered.append((directory, record))

    visit(".")
    require(visited == set(records), "publication_contains_unreferenced_repository")
    return ordered


def publish_closure(root: Path, specification):
    root = root.resolve(strict=True)
    # A common-git-dir lock serializes publishers across linked worktrees.
    common = Path(_git(root, "rev-parse", "--git-common-dir"))
    common = common if common.is_absolute() else root/common
    lock = common.resolve()/"timelearner-publication.lock"
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise EvidenceError("publication_lock_exists_inspect_owner_before_recovery") from error
    published = []
    try:
        (lock/"owner.json").write_text(json.dumps({"pid": os.getpid()}), encoding="utf-8")
        plan = publication_plan(root, specification)
        for directory, record in plan:
            # Revalidate the complete local closure before each remote mutation.
            publication_plan(root, specification)
            _git(directory, "-c", "push.recurseSubmodules=no", "push", record["remote"],
                 record["commit"]+":"+record["branch"])
            actual = _git(directory, "ls-remote", "--exit-code", record["remote"], record["branch"])
            require(actual.split() == [record["commit"], record["branch"]], "remote_publication_verification_failed:"+record["path"])
            published.append(dict(record))
        # A child ref may have moved while root was being pushed: fail closed.
        for directory, record in plan:
            actual = _git(directory, "ls-remote", "--exit-code", record["remote"], record["branch"])
            require(actual.split() == [record["commit"], record["branch"]], "published_closure_changed:"+record["path"])
        return {"kind": "timelearner_git_publication_result", "schema_version": 1,
                "publication": "published", "repositories": published, "scientific_verdict": None}
    except (EvidenceError, OSError, subprocess.SubprocessError, UnicodeError) as error:
        return {"kind": "timelearner_git_publication_result", "schema_version": 1,
                "publication": "failed", "repositories_published_before_failure": published,
                "reason": str(error), "scientific_verdict": None}
    finally:
        owner = lock/"owner.json"
        if owner.exists():
            owner.unlink()
        lock.rmdir()
