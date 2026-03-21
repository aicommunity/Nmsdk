#!/usr/bin/env python3
"""Add Источники/References sections to component docs that don't have them."""

import os
import re

COMPONENTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "Libraries", "Nmsdk-PulseLib", "Docs", "Components"
)

# Default refs for unknown components
DEFAULT_REFS = "[A], 4, 25"

def refs_for_filename(name: str) -> str:
    """Choose literature refs by component name."""
    n = name.lower()
    if "cable" in n and ("neuron" in n or "membrane" in n or "channel" in n or "ltzone" in n):
        return "[C], 7, 5, 6"
    if "stdp" in n or "trainerstdp" in n or "synapsestdp" in n:
        return "[B]"
    if "bio" in n or "bio2" in n:
        return "26, 29, 30"
    if "motoneuron" in n or "renshow" in n or "muscle" in n or "eyemuscle" in n:
        return "19, 20, 21, 22, 28, 31"
    if "classifier" in n or "conditionedreflex" in n or "associationformer" in n or "statepredictor" in n:
        return "1, 6, 8, 9, 10"
    if "afferent" in n or "receptor" in n or "receiver" in n:
        return "25, 29"
    if "generator" in n or "delay" in n:
        return "14, 25"
    if "hebb" in n and "life" not in n:
        return "25, 29"
    if "izhikevich" in n or "iaf" in n or "integrateandfire" in n:
        return "25, 29, 30"
    if "neuron" in n or "membrane" in n or "channel" in n or "ltzone" in n or "synapse" in n:
        return "[A], 4, 25, 29"
    return DEFAULT_REFS

def main():
    os.chdir(COMPONENTS_DIR)
    added = 0
    for fname in sorted(os.listdir(".")):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(COMPONENTS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "### Источники" in content:
            continue
        base = os.path.splitext(fname)[0]
        refs_raw = refs_for_filename(base)
        refs_bold = ", ".join("**" + r.strip() + "**" for r in refs_raw.split(","))
        ru_block = f"""
### Источники

См. [Literature-References.md](../Literature-References.md): {refs_bold}.

"""
        en_block = f"""
### References

See [Literature-References.md](../Literature-References.md): {refs_bold}.

"""
        if "### См. также" not in content:
            print(f"Skip (no RU): {fname}")
            continue
        content = content.replace(
            "\n### См. также\n",
            ru_block + "### См. также\n",
            1
        )
        if "### See Also" in content:
            content = content.replace(
                "\n### See Also\n",
                en_block + "### See Also\n",
                1
            )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        added += 1
        print(f"Added: {fname}")
    print(f"Total added: {added}")

if __name__ == "__main__":
    main()
