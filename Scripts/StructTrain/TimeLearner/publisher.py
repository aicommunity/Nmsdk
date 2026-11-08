"""Publish an explicit immutable Git closure, children first, without force.

Schema 2 also verifies declared artifact bytes in Git objects. Scientific validity
and completeness of the declared inventory remain separate upstream gates.
"""
from pathlib import Path, PurePosixPath
import json
import hashlib
import re
import os
import stat
import subprocess
from urllib.parse import urlsplit

from .native_evidence import EvidenceError, require
from .publication_lock import hold as hold_publication_lock, recover as recover_lock, git_lock_arguments


LOOSE_REPORT_SCRIPT_SUFFIXES = frozenset({
    '.py', '.pyw', '.sh', '.bash', '.zsh', '.fish', '.ksh', '.ps1', '.psm1',
    '.bat', '.cmd', '.pl', '.rb', '.js', '.mjs', '.cjs', '.lua', '.awk',
    '.tcl', '.ipynb', '.vbs', '.wsf', '.command', '.c', '.cmake',
})


def _report_artifact(name):
    return tuple(part.casefold() for part in PurePosixPath(name).parts[:3]) == (
        'reports', 'structtrain', 'timelearner')


def _new_report_artifact_policy(name, mode, header=b''):
    """New publication policy; old read-only evidence verification stays intact."""
    if not _report_artifact(name):
        return
    path = PurePosixPath(name)
    reason = ('suffix' if path.suffix.casefold() in LOOSE_REPORT_SCRIPT_SUFFIXES or
              path.name.casefold() == 'cmakelists.txt' else
              'git_executable_mode' if mode == '100755' else
              'shebang' if header.removeprefix(b'\xef\xbb\xbf').startswith(b'#!') else None)
    require(reason is None, 'loose_report_script_forbidden:'+str(reason)+':'+name)


def _working_git_mode(directory, name, actual):
    result = subprocess.run(['git', '--literal-pathspecs', '-C', str(directory),
                             'ls-files', '--stage', '-z', '--', name],
                            capture_output=True, timeout=120)
    require(result.returncode == 0, 'artifact_index_mode_read_failed:'+name)
    entries = [entry for entry in result.stdout.split(b'\0') if entry]
    require(len(entries) <= 1, 'artifact_unmerged_index_path:'+name)
    mode = '100644'
    if entries:
        metadata, path = entries[0].split(b'\t', 1)
        indexed_mode, _, stage = metadata.decode('ascii').split()
        require(path.decode('utf-8') == name and stage == '0', 'artifact_unmerged_index_path:'+name)
        mode = indexed_mode
    # Windows X_OK/access bits do not describe Git executable mode. Existing
    # index mode is authoritative there; a suffix/shebang still catches new code.
    if os.name != 'nt' and mode != '100755':
        file_mode = _git(directory, 'config', '--type=bool', '--get', '--default', 'true', 'core.fileMode')
        if file_mode == 'true' and stat.S_IMODE(actual.stat().st_mode) & 0o111:
            mode = '100755'
    return mode


def _working_digest_and_header(path):
    digest = hashlib.sha256(); header = b''
    with path.open('rb') as stream:
        while chunk := stream.read(1024*1024):
            if not header:header = chunk[:512]
            digest.update(chunk)
    return digest.hexdigest(), header


def _git(directory, *args):
    result = subprocess.run(["git", "--no-replace-objects", "-C", str(directory), *args], capture_output=True, timeout=120,
                            **git_lock_arguments())
    require(result.returncode == 0, "git_operation_failed:"+args[0]+":"+
            result.stderr.decode("utf-8", errors="replace")[-3000:])
    return result.stdout.decode("utf-8", errors="strict").strip()


def _artifact_path(name):
    require(type(name) is str and name and "\\" not in name and ":" not in name and
            all(ord(c) >= 32 and ord(c) != 127 for c in name), "invalid_artifact_path")
    path = PurePosixPath(name)
    require(not path.is_absolute() and path.as_posix() == name and
            not any(p in {".", "..", ".git"} for p in path.parts) and name != ".", "invalid_artifact_path")
    return path


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate_artifact_manifest_key")
        result[key] = value
    return result


def _artifact_inventory(raw, expected):
    require(type(expected) is str and re.fullmatch(r"[0-9a-f]{64}", expected) and
            hashlib.sha256(raw).hexdigest() == expected, "artifact_manifest_digest_mismatch")
    require(len(raw) <= 16*1024*1024, "artifact_manifest_too_large")
    try:
        inventory = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise EvidenceError("invalid_artifact_manifest_json") from error
    require(type(inventory) is dict and 0 < len(inventory) <= 100000, "invalid_artifact_inventory")
    for name, digest in inventory.items():
        _artifact_path(name)
        require(type(digest) is str and re.fullmatch(r"[0-9a-f]{64}", digest), "invalid_artifact_digest")
    return inventory


def _blob_entry(directory, commit, name):
    raw = subprocess.check_output(["git", "--literal-pathspecs", "--no-replace-objects", "-C", str(directory),
                                   "ls-tree", "-z", commit, "--", name], timeout=120)
    entries = [v for v in raw.split(b"\0") if v]
    require(len(entries) == 1, "missing_committed_artifact:"+name)
    meta, path = entries[0].split(b"\t", 1)
    mode, kind, oid = meta.decode("ascii").split()
    require(path.decode("utf-8") == name and mode in {"100644", "100755"} and kind == "blob",
            "artifact_is_not_regular_committed_blob:"+name)
    return mode, oid


def _blob_id(directory, commit, name):
    return _blob_entry(directory, commit, name)[1]


def _blob_sha256(directory, oid, *, new_report_path=None):
    # Large primary archives are streamed rather than copied into memory.
    with subprocess.Popen(["git", "--no-replace-objects", "-C", str(directory), "cat-file", "blob", oid],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
        digest = hashlib.sha256()
        first = True
        while chunk := process.stdout.read(1024*1024):
            if first and new_report_path is not None:
                _new_report_artifact_policy(new_report_path, '100644', chunk[:512])
            first = False
            digest.update(chunk)
        require(process.wait(timeout=120) == 0, "artifact_blob_read_failed")
    return digest.hexdigest()


def verify_artifact_set(directory, commit, record, *, enforce_new_artifact_policy=False):
    require(type(record) is dict and set(record) == {"repository", "manifest", "manifest_sha256"},
            "invalid_publication_artifact_set")
    manifest = _artifact_path(record["manifest"])
    mode, oid = _blob_entry(directory, commit, manifest.as_posix())
    if enforce_new_artifact_policy:_new_report_artifact_policy(manifest.as_posix(), mode)
    size = int(_git(directory, "cat-file", "-s", oid))
    require(size <= 16*1024*1024, "artifact_manifest_too_large")
    raw = subprocess.check_output(["git", "--no-replace-objects", "-C", str(directory),
                                   "cat-file", "blob", oid], timeout=120)
    if enforce_new_artifact_policy:_new_report_artifact_policy(manifest.as_posix(), mode, raw[:512])
    inventory = _artifact_inventory(raw, record["manifest_sha256"])
    require(manifest.name not in inventory, "artifact_manifest_cannot_include_itself")
    for name, expected in inventory.items():
        path = (manifest.parent/_artifact_path(name)).as_posix()
        mode, oid = _blob_entry(directory, commit, path)
        if enforce_new_artifact_policy:_new_report_artifact_policy(path, mode)
        require(_blob_sha256(directory, oid, new_report_path=path if enforce_new_artifact_policy else None) == expected,
                "committed_artifact_content_changed:"+path)
    return {**record, "files_verified": len(inventory)+1}


def stage_artifact_set(directory: Path, manifest: str, manifest_sha256: str):
    """Stage exactly one verified inventory, including explicitly selected ignored files.

    Does not commit or publish. A post-add filter mismatch leaves the index
    reviewable and fails closed; it must never be followed by publication.
    """
    directory = Path(directory).resolve(strict=True)
    require(Path(_git(directory, "rev-parse", "--show-toplevel")).resolve() == directory,
            "artifact_repository_root_required")
    relative = _artifact_path(manifest)
    path = directory/relative.as_posix()
    require(path.is_file() and path.resolve(strict=True).is_relative_to(directory) and
            not any(p.is_symlink() for p in [path, *path.parents]), "artifact_missing_or_symlink:"+manifest)
    raw = path.read_bytes()
    inventory = _artifact_inventory(raw, manifest_sha256)
    require(relative.name not in inventory, "artifact_manifest_cannot_include_itself")
    paths = [relative, *(relative.parent/_artifact_path(n) for n in inventory)]
    for name in paths:
        actual = directory/name.as_posix()
        require(actual.is_file() and actual.resolve(strict=True).is_relative_to(directory) and
                not any(p.is_symlink() for p in [actual, *actual.parents] if p != directory.parent),
                "artifact_missing_or_symlink:"+name.as_posix())
        require(Path(_git(actual.parent, "rev-parse", "--show-toplevel")).resolve() == directory,
                "artifact_belongs_to_other_repository")
        digest, header = ((manifest_sha256, raw[:512]) if name == relative else
                          _working_digest_and_header(actual))
        if _report_artifact(name.as_posix()):
            _new_report_artifact_policy(name.as_posix(),
                _working_git_mode(directory, name.as_posix(), actual), header)
        if name != relative:
            require(digest == inventory[name.relative_to(relative.parent).as_posix()],
                    "working_artifact_content_changed:"+name.as_posix())
    # Literal NUL pathspecs avoid glob expansion and argument-size limits.
    payload = b"".join((":(literal)"+p.as_posix()).encode("utf-8")+b"\0" for p in paths)
    result = subprocess.run(["git", "-C", str(directory), "add", "--force", "--sparse",
                             "--pathspec-from-file=-", "--pathspec-file-nul"], input=payload, capture_output=True, timeout=120)
    require(result.returncode == 0, "artifact_staging_failed:"+result.stderr.decode("utf-8", errors="replace")[-1000:])
    for name in paths:
        result = subprocess.check_output(["git", "-C", str(directory), "show", ":"+name.as_posix()], timeout=120)
        expected = manifest_sha256 if name == relative else inventory[name.relative_to(relative.parent).as_posix()]
        require(hashlib.sha256(result).hexdigest() == expected, "staged_artifact_filter_or_content_changed:"+name.as_posix())
    return {"files_staged": len(paths), "manifest_sha256": manifest_sha256, "committed": False}


def _links(directory, commit):
    raw = subprocess.check_output(["git", "--no-replace-objects", "-C", str(directory), "ls-tree", "-rz", commit], timeout=120)
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
    result = subprocess.run(["git", "--no-replace-objects", "-C", str(directory), "config", "--null", "--blob", commit+":.gitmodules",
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


def publication_plan(root: Path, specification, *, enforce_new_artifact_policy=False):
    version = specification.get("schema_version") if type(specification) is dict else None
    fields = {"kind", "schema_version", "repositories"} | ({"artifacts"} if version == 2 else set())
    require(type(specification) is dict and set(specification) == fields
            and specification["kind"] == "timelearner_git_publication"
            and type(version) is int and version in (1, 2),
            "unknown_publication_spec")
    require(type(specification["repositories"]) is list and bool(specification["repositories"]), "empty_publication")
    root = root.resolve(strict=True)
    records = {}
    for record in specification["repositories"]:
        keys = {"path", "commit", "remote", "branch"} | ({"push_url"} if version == 2 else set())
        require(type(record) is dict and set(record) == keys, "invalid_publication_record")
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
        if version == 2:
            url = record["push_url"]
            require(type(url) is str and url and not url.startswith("-") and
                    all(ord(c) >= 32 for c in url), "invalid_publication_push_url")
            if "://" in url:
                parsed = urlsplit(url)
                require(parsed.password is None and (parsed.scheme == "ssh" or parsed.username is None),
                        "publication_url_must_not_contain_credentials")
            require(_repository_identity(url) == _repository_identity(_git(directory, "remote", "get-url", record["remote"])),
                    "explicit_push_repository_mismatch:"+name)
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
            push_url = child_record["push_url"] if version == 2 else _git(child_directory, "remote", "get-url", "--push", remote)
            fetch_url = _git(child_directory, "remote", "get-url", remote)
            require(_repository_identity(urls[relative]) == _repository_identity(push_url) == _repository_identity(fetch_url),
                    "child_remote_differs_from_committed_gitmodules:"+child)
            visit(child)
        ordered.append((directory, record))

    visit(".")
    require(visited == set(records), "publication_contains_unreferenced_repository")
    if version == 2:
        artifacts = specification["artifacts"]
        require(type(artifacts) is list and bool(artifacts), "missing_publication_artifact_inventory")
        seen = set()
        for artifact in artifacts:
            require(type(artifact) is dict and type(artifact.get("repository")) is str and
                    artifact["repository"] in records, "unknown_artifact_repository")
            directory, record = records[artifact["repository"]]
            proof = verify_artifact_set(directory, record["commit"], artifact,
                                       enforce_new_artifact_policy=enforce_new_artifact_policy)
            key = (proof["repository"], proof["manifest"])
            require(key not in seen, "duplicate_publication_artifact_set");seen.add(key)
    return ordered


def _common_directory(root):
    common = Path(_git(root, "rev-parse", "--git-common-dir"))
    return (common if common.is_absolute() else root/common).resolve(strict=True)


def recover_publication_lock(root):
    root = Path(root).resolve(strict=True)
    require(Path(_git(root, "rev-parse", "--show-toplevel")).resolve() == root,
            "publication_repository_root_required")
    return recover_lock(_common_directory(root))


def publish_closure(root: Path, specification):
    root = root.resolve(strict=True)
    # The kernel guard also fences inherited Git children after frontend death.
    with hold_publication_lock(_common_directory(root)):
        published = []
        version = 2 if type(specification) is dict and specification.get("schema_version") == 2 else 1
        try:
            plan = publication_plan(root, specification, enforce_new_artifact_policy=True)
            for directory, record in plan:
                # Revalidate the complete local closure before each remote mutation.
                publication_plan(root, specification, enforce_new_artifact_policy=True)
                target = record["push_url"] if version == 2 else record["remote"]
                _git(directory, "-c", "push.recurseSubmodules=no", "push", target,
                     record["commit"]+":"+record["branch"])
                actual = _git(directory, "ls-remote", "--exit-code", target, record["branch"])
                require(actual.split() == [record["commit"], record["branch"]], "remote_publication_verification_failed:"+record["path"])
                published.append(dict(record))
            # A child ref may have moved while root was being pushed: fail closed.
            for directory, record in plan:
                target = record["push_url"] if version == 2 else record["remote"]
                actual = _git(directory, "ls-remote", "--exit-code", target, record["branch"])
                require(actual.split() == [record["commit"], record["branch"]], "published_closure_changed:"+record["path"])
            return {"kind": "timelearner_git_publication_result", "schema_version": version,
                    "publication": "published", "repositories": published, "scientific_verdict": None,
                    **({"artifact_sets_verified": specification["artifacts"]} if version == 2 else {})}
        except (EvidenceError, OSError, subprocess.SubprocessError, UnicodeError, ValueError) as error:
            return {"kind": "timelearner_git_publication_result", "schema_version": version,
                    "publication": "failed", "repositories_published_before_failure": published,
                    "reason": str(error), "scientific_verdict": None}
