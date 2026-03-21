#!/usr/bin/env python3
"""
Set ProjectAutoSaveFlag to 0 in all project.ini/Project.ini under Bin/Configs/SpikeSamples.
Only the ProjectAutoSaveFlag tag is changed; ProjectAutoSaveStateFlag is left unchanged.
"""
import re
from pathlib import Path

# Repo root: script lives in scripts/
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SPIKESAMPLES = REPO_ROOT / "Bin" / "Configs" / "SpikeSamples"

# Replace <ProjectAutoSaveFlag>1</ProjectAutoSaveFlag> with 0 (any whitespace around tag body)
PATTERN = re.compile(r"<ProjectAutoSaveFlag>\s*1\s*</ProjectAutoSaveFlag>", re.IGNORECASE)
REPLACEMENT = "<ProjectAutoSaveFlag>0</ProjectAutoSaveFlag>"


def process_file(path):
    """Return (1, 0) if file was changed, (0, 1) if already 0 or no match."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if PATTERN.search(text):
        new_text = PATTERN.sub(REPLACEMENT, text)
        path.write_text(new_text, encoding="utf-8")
        return 1, 0
    return 0, 1


if __name__ == "__main__":
    if not SPIKESAMPLES.is_dir():
        print(f"Directory not found: {SPIKESAMPLES}")
        exit(1)

    changed = 0
    skipped = 0
    seen = set()
    for pat in ["project.ini", "Project.ini"]:
        for path in sorted(SPIKESAMPLES.rglob(pat)):
            # On case-insensitive FS, project.ini and Project.ini can be the same
            key = path.resolve()
            if key in seen:
                continue
            seen.add(key)
            c, s = process_file(path)
            changed += c
            skipped += s

    print(f"Changed: {changed} file(s), already 0: {skipped} file(s)")
    exit(0)
