#!/usr/bin/env python3
"""
Build Docs/ClDescLexicon.json from Libraries/*/Docs/Components/*.md.

Extracts class Header and Description from component documentation for use
by NeuroModelerConsole ClDescGenerator. Run from repository root (Nmsdk).

Usage:
  python scripts/build_cl_desc_lexicon_from_docs.py
  python scripts/build_cl_desc_lexicon_from_docs.py -o Docs/ClDescLexicon.json --verbose
  python scripts/build_cl_desc_lexicon_from_docs.py --no-merge  # overwrite entire lexicon
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Default paths relative to repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
LIBS = [
    "Rdk-CvBasicLib",
    "Nmsdk-PulseLib",
    "Nmsdk-MotionControlLib",
    "Rdk-HardwareLib",
    "Rdk-BasicLib",
]
DOCS_COMPONENTS = "Docs/Components"
DEFAULT_OUTPUT = "Docs/ClDescLexicon.json"
MAX_DESCRIPTION_LEN = 400

# Rdk-CvBasicLib: Storage class name (UploadClass) -> (md_filename, section_keyword or None).
# section_keyword: extract block under ### ... section_keyword ...; None = use whole file.
# From Basic.cpp and Component-Catalog.md.
CVBASICLIB_STORAGE_TO_DOC: dict[str, tuple[str, str | None]] = {
    "ColorConvert": ("ColorConvert.md", None),
    "ResizeEdges": ("GeometricTransformations.md", None),
    "RotateSimple": ("GeometricTransformations.md", None),
    "UBAFlipImageSimple": ("GeometricTransformations.md", None),
    "Model": ("PipelinesModelsStats.md", "UBAModel"),
    "Pipeline": ("PipelinesModelsStats.md", "UBPipeline"),
    "ParallelPipeline": ("PipelinesModelsStats.md", "UBParallelPipeline"),
    "Source": ("CaptureAndSources.md", None),
    "SourceFile": ("CaptureAndSources.md", None),
    "SourceMultiFile": ("CaptureAndSources.md", None),
    "Receiver": ("CaptureAndSources.md", None),
    "Crop": ("CropReduce.md", None),
    "Reduce": ("CropReduce.md", None),
    "UMDMatrixDoubleMux": ("MatrixMathMux.md", None),
    "UMDMatrixIntMux": ("MatrixMathMux.md", None),
    "BMathOperator": ("MatrixMathMux.md", None),
    "UMatrixIntMath": ("MatrixMathMux.md", None),
    "UMatrixDoubleMath": ("MatrixMathMux.md", None),
    "UMDScalarDoubleMux": ("MatrixMathMux.md", None),
    "UMDScalarIntMux": ("MatrixMathMux.md", None),
    "DifferenceFrameSimple": ("BackgroundBinarizationLabeling.md", None),
    "BackgroundAvg": ("BackgroundBinarizationLabeling.md", None),
    "TBinarizationSimple": ("BackgroundBinarizationLabeling.md", None),
    "TBinarizationSimpleAdaptiveThreshold": ("BackgroundBinarizationLabeling.md", None),
    "TLabelingSimple": ("BackgroundBinarizationLabeling.md", None),
    "BackgroundExponnential": ("BackgroundBinarizationLabeling.md", None),
    "DeltaBackgroundExponnential": ("BackgroundBinarizationLabeling.md", None),
    "BackgroundSimpleAdaptive": ("BackgroundBinarizationLabeling.md", None),
    "UBABinarizationOtsu": ("BackgroundBinarizationLabeling.md", None),
    "UBABackgroundDependDiff": ("BackgroundBinarizationLabeling.md", None),
    "UBShowRect": ("DetectorsSegmentators.md", None),
    "ShowObjectsSimple": ("DetectorsSegmentators.md", None),
    "VideoSimulatorSimple": ("VideoSimulators.md", None),
    "RotCameraSimulator": ("VideoSimulators.md", None),
    "VideoSimulatorSimpleBin": ("VideoSimulators.md", None),
    "DataSimulatorSimple": ("VideoSimulators.md", None),
    "BitmapSourceSimple": ("CaptureAndSources.md", None),
    "BitmapSourceFile": ("CaptureAndSources.md", None),
    "BStatisticSimple": ("PipelinesModelsStats.md", None),
    "UClassifierBase": ("DetectorsSegmentators.md", None),
    "UDetectorBase": ("DetectorsSegmentators.md", None),
    "USegmentatorBase": ("DetectorsSegmentators.md", None),
    "UClassifierResSaver": ("DetectorsSegmentators.md", None),
    "UDetResSaverPVOC": ("DetectorsSegmentators.md", None),
    "UCRPrincipalComponentAnalysis": ("UCRFamily.md", None),
    "UCRBarnesHutTSNE": ("UCRFamily.md", None),
    "TCaptureImageSequence": ("CaptureAndSources.md", None),
}


def extract_section(content: str, section_keyword: str | None) -> str:
    """If section_keyword is set, return the block under ### ... section_keyword ...; else return content."""
    if not section_keyword:
        return content
    # Split by ### headings and find block whose heading contains section_keyword
    parts = re.split(r"\n###\s+", content, maxsplit=1)
    if len(parts) < 2:
        return content
    rest = "\n### " + parts[1]
    # Find next ### or --- and take block
    blocks = re.split(r"\n(?:###\s+|---)", rest)
    for block in blocks:
        first_line = block.strip().split("\n")[0] if block.strip() else ""
        if section_keyword in first_line:
            return block.strip()
    return content


def extract_header_and_description(md_text: str) -> tuple[str, str]:
    """Parse markdown and return (header, description)."""
    header = ""
    description = ""

    # Header: from first # or ## line (or any line with " — "), take part after " — "; else full line
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            s = re.sub(r"^#+\s*", "", s)
        if "—" in s:
            header = s.split("—", 1)[1].strip()
            break
        if " - " in s and not s.startswith("```"):
            header = s.split(" - ", 1)[1].strip()
            break
        if s.startswith("#") and not header:
            header = s
            break
    if not header and md_text.strip():
        first = md_text.strip().splitlines()[0].strip()
        if "—" in first:
            header = first.split("—", 1)[1].strip()
        elif " - " in first:
            header = first.split(" - ", 1)[1].strip()

    # Description: prefer first paragraph under "### Purpose" (or Russian \"### Назначение\"); else first **Class**/**Classes** (or Russian **Класс**/**Классы**) sentence
    in_nazn = False
    para_lines: list[str] = []
    for line in md_text.splitlines():
        stripped = line.strip()
        if re.match(r"^###\s+(Назначение|Purpose)", stripped):
            in_nazn = True
            continue
        if in_nazn:
            if stripped.startswith("###") or stripped.startswith("---"):
                break
            if stripped:
                para_lines.append(stripped)
            elif para_lines:
                break
    if para_lines:
        description = " ".join(para_lines)

    if not description:
        # Fallback: first line containing **Class**/**Classes** (English) or **Класс**/**Классы** (Russian)
        for line in md_text.splitlines():
            if (
                "**Класс**:" in line
                or "**Классы**:" in line
                or "**Классы**：" in line
                or "**Class**:" in line
                or "**Classes**:" in line
            ):
                # Take text after colon, strip backticks and markdown
                m = re.search(r":\s*[`]?(?:\w+)[`]?\s*[—\-]\s*(.+)", line)
                if m:
                    description = m.group(1).strip()
                else:
                    description = line.split(":", 1)[-1].strip()
                break

    if not description:
        # First non-empty, non-heading, non-mermaid paragraph
        for line in md_text.splitlines():
            s = line.strip()
            if not s or s.startswith("#") or s.startswith("```") or s.startswith("- ") or s.startswith("*"):
                continue
            if len(s) > 30:
                description = s
                break

    # Truncate description for UI tooltips
    if len(description) > MAX_DESCRIPTION_LEN:
        description = description[: MAX_DESCRIPTION_LEN - 3].rsplit(" ", 1)[0] + "..."

    return (header or "", description or "")


def collect_from_cvbasiclib(lib_path: Path, verbose: bool) -> dict[str, dict[str, str]]:
    """Collect classOverrides from Rdk-CvBasicLib using explicit Storage -> (file, section) mapping."""
    overrides: dict[str, dict[str, str]] = {}
    components_dir = lib_path / DOCS_COMPONENTS
    if not components_dir.is_dir():
        return overrides

    for storage_name, (filename, section_kw) in CVBASICLIB_STORAGE_TO_DOC.items():
        md_path = components_dir / filename
        if not md_path.is_file():
            if verbose:
                print(f"  skip {storage_name}: {filename} not found", file=sys.stderr)
            continue
        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception as e:
            if verbose:
                print(f"  skip {storage_name}: {e}", file=sys.stderr)
            continue
        block = extract_section(text, section_kw)
        header, desc = extract_header_and_description(block)
        if header or desc:
            overrides[storage_name] = {"header": header, "description": desc}
            if verbose:
                print(f"  {storage_name} <- {filename}" + (f" (section {section_kw})" if section_kw else ""))
    return overrides


def collect_from_lib_by_filename(lib_path: Path, verbose: bool) -> dict[str, dict[str, str]]:
    """Collect classOverrides from a library where each .md file name = class name (stem)."""
    overrides: dict[str, dict[str, str]] = {}
    components_dir = lib_path / DOCS_COMPONENTS
    if not components_dir.is_dir():
        return overrides

    for md_path in sorted(components_dir.glob("*.md")):
        if md_path.name.lower() == "readme.md":
            continue
        class_name = md_path.stem
        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception as e:
            if verbose:
                print(f"  skip {class_name}: {e}", file=sys.stderr)
            continue
        header, desc = extract_header_and_description(text)
        if header or desc:
            overrides[class_name] = {"header": header, "description": desc}
            if verbose:
                print(f"  {class_name} <- {md_path.name}")
    return overrides


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build ClDescLexicon.json from Libraries/*/Docs/Components/*.md"
    )
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output JSON path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Overwrite entire lexicon; default is to merge with existing (keep tokens, propertyFallbacks).",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print processed classes and files.",
    )
    args = parser.parse_args()

    root = REPO_ROOT
    if not (root / "Libraries").is_dir():
        print("Error: run from Nmsdk repository root (Libraries/ not found).", file=sys.stderr)
        return 1

    all_overrides: dict[str, dict[str, str]] = {}

    for lib in LIBS:
        lib_path = root / "Libraries" / lib
        if not lib_path.is_dir():
            if args.verbose:
                print(f"Skip {lib}: not found.")
            continue
        if args.verbose:
            print(f"Scanning {lib} ...")
        if lib == "Rdk-CvBasicLib":
            overrides = collect_from_cvbasiclib(lib_path, args.verbose)
        else:
            overrides = collect_from_lib_by_filename(lib_path, args.verbose)
        for k, v in overrides.items():
            all_overrides[k] = v

    if args.verbose:
        print(f"Total classes: {len(all_overrides)}")

    out_path = root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    merge = not args.no_merge
    if merge and out_path.is_file():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
        if not isinstance(existing, dict):
            existing = {}
        existing["classOverrides"] = all_overrides
        if not existing.get("tokens"):
            existing["tokens"] = {"Id": "Identifier", "Name": "Name"}
        out_data = existing
    else:
        # ClDescGenerator requires non-empty "tokens" to accept the file
        out_data = {
            "tokens": {"Id": "Identifier", "Name": "Name"},
            "classOverrides": all_overrides,
            "propertyOverrides": {},
            "propertyFallbacks": {},
        }

    out_path.write_text(
        json.dumps(out_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(all_overrides)} class overrides to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
