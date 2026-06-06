#!/usr/bin/env python3
"""Generate component and build documentation gap reports."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import (  # noqa: E402
    AUDIT_DIR,
    LIBRARY_REGISTRATION_FILES,
    ROOT,
    collect_cmake_metadata,
    parse_upload_classes,
    utc_now_iso,
    write_text,
)

BUILD_DOC = ROOT / "Docs" / "Build-And-Deploy" / "Build-System.md"
LIBRARIES_INDEX = ROOT / "Docs" / "Submodules" / "Libraries-Index.md"


def component_doc_names(lib_path: Path) -> set[str]:
    components_dir = lib_path / "Docs" / "Components"
    if not components_dir.exists():
        return set()
    names: set[str] = set()
    for md in components_dir.glob("*.md"):
        names.add(md.stem)
    return names


def catalog_mentions(lib_path: Path) -> set[str]:
    catalog = lib_path / "Docs" / "Component-Catalog.md"
    if not catalog.exists():
        return set()
    text = catalog.read_text(encoding="utf-8", errors="replace")
    names = set(re.findall(r"`([A-Za-z0-9_]+)`", text))
    names.update(re.findall(r"\*\*([A-Za-z][A-Za-z0-9_]*)\*\*", text))
    return names


# Libraries that document many UploadClass entries via group overview pages.
GROUP_DOC_LIBS = {"Rdk-CvBasicLib"}

CVBASIC_GROUP_MAP = {
    "Capture": "CaptureAndSources.md",
    "TCaptureImageSequence": "CaptureAndSources.md",
    "Source": "CaptureAndSources.md",
    "SourceFile": "CaptureAndSources.md",
    "SourceMultiFile": "CaptureAndSources.md",
    "Receiver": "ReceiverAndShowRect.md",
    "ColorConvert": "ColorConvert.md",
    "ResizeEdges": "GeometricTransformations.md",
    "RotateSimple": "GeometricTransformations.md",
    "UBAFlipImageSimple": "GeometricTransformations.md",
    "Crop": "CropReduce.md",
    "Reduce": "CropReduce.md",
}


def group_covered(lib: str, class_name: str, lib_path: Path) -> bool:
    if lib != "Rdk-CvBasicLib":
        return False
    components = lib_path / "Docs" / "Components"
    # Any group .md that mentions class in backticks
    for md in components.glob("*.md"):
        if class_name in md.read_text(encoding="utf-8", errors="replace"):
            return True
    return class_name in CVBASIC_GROUP_MAP


def render_component_gap() -> str:
    lines = [
        "# Component Gap Report",
        "",
        f"Generated: {utc_now_iso()}",
        "",
        "Comparison of `UploadClass` registrations vs `Docs/Components/*.md` and Component-Catalog mentions.",
        "",
    ]
    total_missing_docs = 0
    total_orphan_docs = 0
    for lib, reg_files in LIBRARY_REGISTRATION_FILES.items():
        lib_path = ROOT / "Libraries" / lib
        registered = set(parse_upload_classes(reg_files))
        doc_names = component_doc_names(lib_path)
        catalog = catalog_mentions(lib_path)
        if lib in GROUP_DOC_LIBS:
            group_ok = {c for c in registered if group_covered(lib, c, lib_path)}
            documented = doc_names | catalog | group_ok
        else:
            documented = doc_names
        missing_docs = sorted(registered - documented)
        missing_per_class = sorted(registered - doc_names)
        orphan_docs = sorted(doc_names - registered)
        missing_catalog = sorted(registered - catalog)
        total_missing_docs += len(missing_docs)
        total_orphan_docs += len(orphan_docs)
        lines.extend(
            [
                f"## {lib}",
                "",
                f"- Registered classes: **{len(registered)}**",
                f"- Component docs: **{len(doc_names)}**",
                f"- Missing documented (per-class or catalog): **{len(missing_docs)}**",
                f"- Missing per-class `.md` only: **{len(missing_per_class)}**",
                f"- Orphan component docs (no UploadClass): **{len(orphan_docs)}**",
                f"- Missing from catalog: **{len(missing_catalog)}**",
                "",
            ]
        )
        if lib in GROUP_DOC_LIBS:
            lines.append(
                f"_Group-doc library: classes listed in Component-Catalog count as documented._\n"
            )
        if missing_docs:
            lines.append("### Missing docs")
            for name in missing_docs[:50]:
                lines.append(f"- `{name}`")
            if len(missing_docs) > 50:
                lines.append(f"- ... and {len(missing_docs) - 50} more")
            lines.append("")
        if orphan_docs:
            lines.append("### Orphan docs (group/legacy names)")
            for name in orphan_docs[:30]:
                lines.append(f"- `{name}`")
            lines.append("")
    lines.extend(
        [
            "## Totals",
            "",
            f"- Missing component docs (all libs): **{total_missing_docs}**",
            f"- Orphan component docs (all libs): **{total_orphan_docs}**",
            "",
            "Note: group docs (e.g. `Neurons.md`) and legacy redirect stubs are expected orphans.",
            "",
        ]
    )
    return "\n".join(lines)


def render_build_gap() -> str:
    cmake = collect_cmake_metadata()
    build_text = BUILD_DOC.read_text(encoding="utf-8", errors="replace") if BUILD_DOC.exists() else ""
    key_targets = [
        "rdk.static.qt",
        "Rdk-BasicLib.qt",
        "Rdk-CvBasicLib.qt",
        "Rdk-HardwareLib.qt",
        "Nmsdk-MotionControlLib.qt",
        "Nmsdk-PulseLib.qt",
        "NeuroModeler",
        "NeuroModelerConsole",
        "llm-index-pack",
    ]
    key_options = [
        "RDK_USE_LLM",
        "RDK_USE_OPENCV",
        "NO_MOTION_CONTROL",
        "NMSDK_MOTIONCONTROLLIB_BUILD_CORE_ONLY",
        "NMSDK_PULSELIB_BUILD_CORE_ONLY",
        "BUILD_TESTS",
        "NMSDK_FORCE_QT_FROM_VCPKG",
    ]
    lines = [
        "# Build Documentation Gap Report",
        "",
        f"Generated: {utc_now_iso()}",
        "",
        "## Documented targets in Build-System.md",
        "",
    ]
    for target in key_targets:
        present = target in build_text
        in_cmake = target in cmake["targets"] or target.replace(".qt", "") in " ".join(cmake["targets"])
        lines.append(f"- `{target}`: doc={'yes' if present else '**NO**'}, cmake={'yes' if in_cmake else 'n/a'}")
    lines.extend(["", "## Documented options in Build-System.md", ""])
    for opt in key_options:
        present = opt in build_text
        in_cmake = opt in cmake["options"]
        lines.append(f"- `{opt}`: doc={'yes' if present else '**NO**'}, cmake={'yes' if in_cmake else 'no'}")
    lines.append("")
    return "\n".join(lines)


def render_index_gap() -> str:
    pulse_registered = len(
        parse_upload_classes(LIBRARY_REGISTRATION_FILES["Nmsdk-PulseLib"])
    )
    index_text = LIBRARIES_INDEX.read_text(encoding="utf-8", errors="replace") if LIBRARIES_INDEX.exists() else ""
    m = re.search(r"\((\d+)\s+компонента\)", index_text)
    claimed = int(m.group(1)) if m else None
    lines = [
        "# Index Count Gap Report",
        "",
        f"Generated: {utc_now_iso()}",
        "",
        f"- PulseLib registered classes: **{pulse_registered}**",
        f"- Libraries-Index claimed count: **{claimed if claimed is not None else 'not found'}**",
        "",
    ]
    if claimed is not None and claimed != pulse_registered:
        lines.append(
            f"Mismatch: update Libraries-Index from {claimed} to {pulse_registered} (registered) "
            f"or clarify group vs per-class doc count."
        )
    else:
        lines.append("PulseLib index count matches registration (or not present).")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write_text(AUDIT_DIR / "Component-Gap-Report.md", render_component_gap())
    write_text(AUDIT_DIR / "Build-Gap-Report.md", render_build_gap())
    write_text(AUDIT_DIR / "Index-Count-Gap-Report.md", render_index_gap())
    print("Wrote Component-Gap-Report.md, Build-Gap-Report.md, Index-Count-Gap-Report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
