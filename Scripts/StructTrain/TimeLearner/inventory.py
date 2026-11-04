"""Read-only inventory of a root commit and its exact recorded child commits.

Working-copy status is separate evidence; it never supplies catalog content.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from .native_evidence import require
from .property_drift import catalog

REPOSITORIES = {"root": ".", "PulseLib": "Libraries/Nmsdk-PulseLib", "Bin": "Bin"}
SCRIPT_SUFFIXES = {".py", ".sh", ".bash", ".ps1", ".bat", ".cmd", ".c", ".js", ".mjs", ".cjs", ".psm1", ".pl", ".rb"}
RELATED_TOKENS = ("timelearner", "structtrain", "normsync")


def git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE).decode("utf-8")
    except subprocess.CalledProcessError:
        require(False, 'inventory_git_read_failed:'+args[0])


def build_inventory(root: Path, revision: str | None = None, *, include_related: bool = False) -> dict:
    require(type(include_related) is bool, "inventory_related_scope_must_be_boolean")
    root = Path(root).resolve(strict=True)
    head = git(root, 'rev-parse', 'HEAD').strip()
    revision = head if revision is None else revision
    require(type(revision) is str and re.fullmatch('[0-9a-f]{40}', revision) is not None,
            'inventory_full_root_commit_required')
    require(git(root, 'cat-file', '-t', revision).strip() == 'commit', 'inventory_root_commit_required')
    repositories = {}
    scripts = []
    for repository, relative in REPOSITORIES.items():
        directory = root / relative
        require(Path(git(directory, 'rev-parse', '--show-toplevel').strip()).resolve() == directory,
                'inventory_repository_alias_mismatch:'+repository)
        if repository == 'root':
            commit = revision
        else:
            entry = git(root, 'ls-tree', revision, '--', relative).strip()
            require(bool(entry), 'inventory_recorded_gitlink_missing:'+repository)
            metadata, recorded_path = entry.split('\t', 1)
            mode, kind, commit = metadata.split()
            require(recorded_path == relative and mode == '160000' and kind == 'commit',
                    'inventory_recorded_gitlink_missing:'+repository)
        require(git(directory, 'cat-file', '-t', commit).strip() == 'commit',
                'inventory_recorded_child_commit_missing:'+repository)
        actual_head = git(directory, 'rev-parse', 'HEAD').strip()
        repositories[repository] = {'path': relative, 'commit': commit, 'checkout_head': actual_head,
                                    'checkout_matches_snapshot': actual_head == commit,
                                    'tracked_working_tree_status': git(directory, 'status', '--porcelain', '--untracked-files=no').strip()}
        for entry in git(directory, 'ls-tree', '-r', '-z', commit).split('\0'):
            if not entry:
                continue
            metadata, name = entry.split('\t', 1)
            mode, kind, blob = metadata.split()
            if kind != 'blob':
                continue
            path_tokens = [word for word in RELATED_TOKENS if word in name.lower()]
            if not path_tokens and not include_related:
                continue
            # New production tools are not historical migration candidates.
            if repository == 'root' and name.startswith("Scripts/StructTrain/TimeLearner/"):
                continue
            raw = None
            if Path(name).suffix.lower() not in SCRIPT_SUFFIXES:
                if mode != '100755':
                    continue
                raw = subprocess.check_output(['git', '-C', str(directory), 'show', commit+':'+name])
                if not raw.startswith(b'#!'):
                    continue
            if raw is None:
                raw = subprocess.check_output(['git', '-C', str(directory), 'show', commit+':'+name])
            content_tokens = [word for word in RELATED_TOKENS if word.encode("ascii") in raw.lower()] if include_related else []
            if not path_tokens and not content_tokens:
                continue
            selection = {'selection_reasons': {'path_tokens': path_tokens, 'content_tokens': content_tokens}} if include_related else {}
            scripts.append({**selection, "repository": repository, "commit": commit,
                            "old_path": name, "blob": blob, 'mode': mode,
                            'bytes': len(raw), 'content_sha256': hashlib.sha256(raw).hexdigest(),
                            'symlink': mode == '120000',
                            "disposition": "review_required"})
    pulse = root / REPOSITORIES["PulseLib"]
    source_catalog = catalog(pulse, repositories['PulseLib']['commit'])
    properties = [{**row, 'semantic_review': 'not_inferred_by_inventory'} for row in source_catalog['properties']]
    scope = {'script_discovery_scope': 'path_and_content_tokens',
             'selection_tokens': list(RELATED_TOKENS),
             'script_suffixes': sorted(SCRIPT_SUFFIXES)} if include_related else {}
    return {**scope, "schema_version": 3 if include_related else 2, 'source_kind': 'root_commit_and_recorded_gitlinks',
            'root_revision': revision, "repositories": repositories,
            "scripts": scripts, "properties": properties, 'property_sources': source_catalog['sources'],
            "limitations": ["Path/content token selection is a lower bound; imports, computed names, nonexecutable unknown suffixes and external callers require separate review." if include_related else "Path-based script selection is a lower bound; inspect imports and launch references before deleting.",
                            "Content matches include comments and string literals; selection never proves active use or authorizes deletion.",
                            "Untracked/ignored files and inherited Rdk properties are outside this committed catalog.",
                            "Default expressions are source evidence, not effective runtime values.",
                            "Semantic property review remains explicit; no inferred lifecycle guarantees."]}


def write_inventory(root: Path, destination: Path, revision: str | None = None, *, include_related: bool = False) -> None:
    inventory = build_inventory(root, revision, include_related=include_related)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
