#!/usr/bin/env python3
"""
Restore empty or nearly empty Interface.xml in Bin/Configs/SpikeSamples
by finding the earliest commit for each file and then searching preceding
commits for corresponding config folders and non-empty Interface.xml there.

Empty = size <= 20 bytes (e.g. <Interfaces/> only).
Runs from Nmsdk root; Bin repo is at Bin/. Paths for git are relative to Bin.
"""
from pathlib import Path
import subprocess
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BIN_DIR = REPO_ROOT / "Bin"
SPIKESAMPLES = BIN_DIR / "Configs" / "SpikeSamples"
EMPTY_THRESHOLD = 20


def run_git(cwd, *args):
    cmd = ["git", "-C", str(cwd)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    return r.returncode, r.stdout, r.stderr


def get_commits_for_file(bin_dir, path_from_bin):
    code, out, _ = run_git(bin_dir, "log", "--all", "--format=%H", "--", path_from_bin)
    if code != 0:
        return []
    return [h.strip() for h in out.strip().splitlines() if h.strip()]


def file_size_at_commit(bin_dir, commit, path_from_bin):
    code, out, err = run_git(bin_dir, "show", f"{commit}:{path_from_bin}")
    if code != 0:
        return 0
    return len(out.encode("utf-8"))


def get_content_at_commit(bin_dir, commit, path_from_bin):
    code, out, err = run_git(bin_dir, "show", f"{commit}:{path_from_bin}")
    if code != 0:
        return None
    return out


def ls_interface_xml_paths(bin_dir, commit):
    """Return list of paths under Configs that end with /Interface.xml at given commit."""
    code, out, _ = run_git(bin_dir, "ls-tree", "-r", "--name-only", commit, "--", "Configs/")
    if code != 0:
        return []
    return [p for p in out.strip().splitlines() if p.endswith("/Interface.xml")]


def rev_list_ancestors(bin_dir, commit, max_count=500):
    """Return list of commit hashes that are ancestors of commit (newest first)."""
    code, out, _ = run_git(bin_dir, "rev-list", "--ancestry-order", "--first-parent", str(commit), f"-n{max_count}")
    if code != 0:
        return []
    return [h.strip() for h in out.strip().splitlines() if h.strip()]


def main():
    if not BIN_DIR.is_dir():
        print(f"Bin directory not found: {BIN_DIR}", file=sys.stderr)
        return 1
    if not (BIN_DIR / ".git").exists():
        print("Bin is not a git repo; cannot use history.", file=sys.stderr)
        return 1

    empty_files = []
    for path in sorted(SPIKESAMPLES.rglob("Interface.xml")):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size <= EMPTY_THRESHOLD:
            rel = path.relative_to(BIN_DIR)
            empty_files.append((path, str(rel)))

    if not empty_files:
        print("No empty Interface.xml files found in SpikeSamples.")
        return 0

    restored = []
    no_history = []
    # Path from Bin: Configs/SpikeSamples/STDP/STDP-Simple-01/Interface.xml -> leaf = STDP-Simple-01
    for abspath, path_from_bin in empty_files:
        parts = path_from_bin.split("/")
        if len(parts) < 2:
            no_history.append(path_from_bin)
            continue
        leaf = parts[-2]  # config folder name containing Interface.xml

        # 1) Try current path history (same path, any commit)
        commits_current = get_commits_for_file(BIN_DIR, path_from_bin)
        for commit in commits_current:
            sz = file_size_at_commit(BIN_DIR, commit, path_from_bin)
            if sz > EMPTY_THRESHOLD:
                content = get_content_at_commit(BIN_DIR, commit, path_from_bin)
                if content:
                    abspath.write_text(content, encoding="utf-8")
                    restored.append((path_from_bin, commit[:7], path_from_bin))
                break
        else:
            # 2) No non-empty at current path: find earliest commit for this path, then search preceding commits
            if not commits_current:
                no_history.append(path_from_bin)
                continue
            earliest_commit = commits_current[-1]
            parent = earliest_commit + "^"
            code, _, _ = run_git(BIN_DIR, "rev-parse", parent)
            if code != 0:
                no_history.append(path_from_bin)
                continue
            ancestors = rev_list_ancestors(BIN_DIR, parent)
            found_commit = None
            found_old_path = None
            for anc in ancestors:
                paths = ls_interface_xml_paths(BIN_DIR, anc)
                # Match: path ends with /<leaf>/Interface.xml (same config folder name elsewhere)
                candidates = [p for p in paths if p.endswith(f"/{leaf}/Interface.xml")]
                for old_path in candidates:
                    sz = file_size_at_commit(BIN_DIR, anc, old_path)
                    if sz > EMPTY_THRESHOLD:
                        found_commit = anc
                        found_old_path = old_path
                        break
                if found_commit is not None:
                    break
            if found_commit and found_old_path:
                content = get_content_at_commit(BIN_DIR, found_commit, found_old_path)
                if content:
                    abspath.write_text(content, encoding="utf-8")
                    restored.append((path_from_bin, found_commit[:7], found_old_path))
            else:
                no_history.append(path_from_bin)

    print(f"Restored: {len(restored)} file(s)")
    for p, c, src in restored:
        print(f"  {p} <- {c} ({src})")
    print(f"No non-empty version in history: {len(no_history)} file(s)")
    for p in no_history:
        print(f"  {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
