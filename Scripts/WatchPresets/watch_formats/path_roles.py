"""Normalize instance-relative watch paths to stable slot roles."""

from __future__ import annotations

import re
from typing import Optional, Tuple

_LTZONE = re.compile(r"(?:^|\.)LTZone$")
_SOMA = re.compile(r"(?:^|\.)Soma(\d+)$")
_DENDRITE = re.compile(
    r"(?:^|\.)Dendrite(\d+)_(\d+)(?:\.(ExcChannel|InhChannel|ExcSynapse\d+|InhSynapse\d+))?$"
)
_SOMA_CHILD = re.compile(
    r"(?:^|\.)Soma(\d+)\.(ExcChannel|InhChannel|ExcSynapse\d+|InhSynapse\d+)$"
)
_LTMEM = re.compile(r"(?:^|\.)LTMembrane$")


def normalize_role_path(rel_path: str) -> str:
    """Map instance-specific relative paths to canonical slot paths.

    Examples:
      Motoneuron1.LTZone → (if rel is Motoneuron1.LTZone under wrong anchor) —
      typically callers pass path relative to neuron: LTZone, Soma2, Dendrite3_1.ExcChannel
    """
    if not rel_path:
        return ""
    p = rel_path.strip(".")
    # Strip leading instance neuron names when path still contains LTZone/Soma/...
    # Keep last matching structural suffix.
    if _LTZONE.search(p):
        return "LTZone"
    if _LTMEM.search(p):
        return "LTMembrane"
    m = _SOMA_CHILD.search(p)
    if m:
        child = m.group(2)
        # Canonical first soma for aggregation
        if child.startswith("ExcSynapse"):
            return "Soma1.ExcSynapse1"
        if child.startswith("InhSynapse"):
            return "Soma1.InhSynapse1"
        return f"Soma1.{child}"
    m = _SOMA.search(p)
    if m:
        return "Soma1"
    m = _DENDRITE.search(p)
    if m:
        suffix = m.group(3)
        if suffix:
            if suffix.startswith("ExcSynapse"):
                return "Dendrite1_1.ExcSynapse1"
            if suffix.startswith("InhSynapse"):
                return "Dendrite1_1.InhSynapse1"
            return f"Dendrite1_1.{suffix}"
        return "Dendrite1_1"
    # Paths like NeuronTrainer1.Neuron.LTZone → LTZone
    parts = p.split(".")
    for i, part in enumerate(parts):
        if part == "LTZone":
            return "LTZone"
        if part.startswith("Soma") and part[4:].isdigit():
            rest = parts[i + 1 :]
            if not rest:
                return "Soma1"
            joined = "Soma1." + ".".join(rest)
            return normalize_role_path(joined)
        if part.startswith("Dendrite") and "_" in part:
            rest = parts[i + 1 :]
            base = "Dendrite1_1"
            if not rest:
                return base
            return normalize_role_path(base + "." + ".".join(rest))
    return p


def template_role_path(role_path: str) -> Optional[str]:
    """Optional wildcard template key for dendrite/synapse families."""
    if not role_path:
        return None
    if role_path.startswith("Dendrite1_1."):
        return "Dendrite*." + role_path.split(".", 1)[1]
    if role_path == "Dendrite1_1":
        return "Dendrite*"
    if role_path.startswith("Soma1.ExcSynapse"):
        return "Soma1.ExcSynapse*"
    if role_path.startswith("Soma1.InhSynapse"):
        return "Soma1.InhSynapse*"
    return None


def is_internal_role(role_path: str) -> bool:
    if not role_path:
        return False
    return (
        role_path == "LTZone"
        or role_path == "LTMembrane"
        or role_path.startswith("Soma")
        or role_path.startswith("Dendrite")
    )
