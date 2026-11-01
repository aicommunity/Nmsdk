"""Read-only inventory of tracked tools and Rdk property declarations."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

REPOSITORIES = {"root": ".", "PulseLib": "Libraries/Nmsdk-PulseLib", "Bin": "Bin"}
SCRIPT_SUFFIXES = {".py", ".sh", ".ps1", ".bat", ".cmd", ".c"}


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args]).decode("utf-8")


def build_inventory(root: Path) -> dict:
    repositories = {}
    scripts = []
    properties = []
    for repository, relative in REPOSITORIES.items():
        directory = root / relative
        commit = git(directory, "rev-parse", "HEAD").strip()
        repositories[repository] = {"path": relative, "commit": commit}
        for name in git(directory, "ls-files", "-z").split("\0"):
            path = Path(name)
            if path.suffix.lower() not in SCRIPT_SUFFIXES:
                continue
            if not any(word in name.lower() for word in ("timelearner", "structtrain", "normsync")):
                continue
            # New production tools are not historical migration candidates.
            if name.startswith("Scripts/StructTrain/TimeLearner/"):
                continue
            scripts.append({"repository": repository, "commit": commit,
                            "old_path": name, "blob": git(directory, "rev-parse", f"{commit}:{name}").strip(),
                            "disposition": "review_required"})
    pulse = root / REPOSITORIES["PulseLib"]
    for component in ("NNeuronTimeLearner", "NNeuronTimeLearnerBranch"):
        header = (pulse / "Core" / f"{component}.h").read_text(encoding="utf-8-sig")
        source = (pulse / "Core" / f"{component}.cpp").read_text(encoding="utf-8-sig")
        for match in re.finditer(r"UProperty<(.+?),\s*" + component + r",\s*([^>]+)>\s*(\w+)\s*;", header, re.S):
            name = match.group(3)
            registration = re.search(r"\b" + name + r'\("' + name + r'",\s*this(?:,\s*&' + component + r"::(\w+))?\)", source)
            # Expressions are evidence, not claimed evaluated runtime defaults.
            default_body = source.split(f"bool {component}::ADefault(void)", 1)[1].split(f"bool {component}::", 1)[0]
            defaults = re.findall(r"\b" + name + r"(?:\s*=\s*([^;]+)|\.SetDataDirect\(([^;]+)\));", default_body)
            properties.append({"component": component, "name": name,
                               "type": match.group(1).strip(), "flags": match.group(2).strip(),
                               "header_line": header.count("\n", 0, match.start()) + 1,
                               "setter": registration.group(1) if registration else None,
                               "default_expressions": [a or b for a, b in defaults],
                               "semantic_review": "pending"})
    return {"schema_version": 1, "repositories": repositories,
            "scripts": scripts, "properties": properties,
            "limitations": ["Path-based script selection is a lower bound; inspect imports and launch references before deleting.",
                            "Default expressions are source evidence, not effective runtime values.",
                            "Semantic property review remains explicit; no inferred lifecycle guarantees."]}


def write_inventory(root: Path, destination: Path) -> None:
    inventory = build_inventory(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
