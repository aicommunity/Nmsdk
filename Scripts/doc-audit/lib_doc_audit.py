#!/usr/bin/env python3
"""Shared helpers for Nmsdk documentation audit scripts."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "Docs" / "Audit"

EXCLUDE_DIRS = {
    "build",
    "build-llm",
    "build-llm-ci",
    ".git",
    "node_modules",
    "vcpkg_installed",
}

SUBMODULE_PATHS = {
    "Rdk": ROOT / "Rdk",
    "Bin": ROOT / "Bin",
    "Nmsdk-PulseLib": ROOT / "Libraries" / "Nmsdk-PulseLib",
    "Nmsdk-MotionControlLib": ROOT / "Libraries" / "Nmsdk-MotionControlLib",
    "Rdk-BasicLib": ROOT / "Libraries" / "Rdk-BasicLib",
    "Rdk-CvBasicLib": ROOT / "Libraries" / "Rdk-CvBasicLib",
    "Rdk-HardwareLib": ROOT / "Libraries" / "Rdk-HardwareLib",
}

LIBRARY_REGISTRATION_FILES = {
    "Rdk-BasicLib": [
        ROOT / "Libraries" / "Rdk-BasicLib" / "Core" / "UBCLLibrary.cpp",
        ROOT / "Libraries" / "Rdk-BasicLib" / "Core" / "UIOLibrary.cpp",
    ],
    "Rdk-CvBasicLib": [ROOT / "Libraries" / "Rdk-CvBasicLib" / "Core" / "Basic.cpp"],
    "Rdk-HardwareLib": [ROOT / "Libraries" / "Rdk-HardwareLib" / "Core" / "UHardwareLibrary.cpp"],
    "Nmsdk-PulseLib": [ROOT / "Libraries" / "Nmsdk-PulseLib" / "Core" / "NPulseLibrary.cpp"],
    "Nmsdk-MotionControlLib": [
        ROOT / "Libraries" / "Nmsdk-MotionControlLib" / "Core" / "NMotionControlLibrary.cpp",
        ROOT / "Libraries" / "Nmsdk-MotionControlLib" / "Core" / "NWinAPIActLibrary.cpp",
    ],
}

LINK_PATTERN = re.compile(r"(!?\[[^\]]*\])\(([^)]+)\)")
UPLOAD_CLASS_PATTERN = re.compile(r'UploadClass\s*\(\s*"([^"]+)"')
OPTION_PATTERN = re.compile(r"option\s*\(\s*([A-Z0-9_]+)")
ADD_EXECUTABLE_PATTERN = re.compile(r"add_executable\s*\(\s*([A-Za-z0-9_.-]+)")
ADD_LIBRARY_PATTERN = re.compile(r"add_library\s*\(\s*([A-Za-z0-9_.-]+)")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def should_skip_path(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    if "build/_deps" in str(path):
        return True
    return False


def iter_markdown_files(base: Path | None = None) -> list[Path]:
    base = base or ROOT
    files: list[Path] = []
    for path in base.rglob("*.md"):
        if should_skip_path(path.relative_to(ROOT)):
            continue
        files.append(path)
    return sorted(files)


def submodule_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if not parts:
        return "nmsdk"
    if parts[0] == "Rdk":
        return "Rdk"
    if parts[0] == "Bin":
        return "Bin"
    if parts[0] == "Libraries" and len(parts) > 1:
        return parts[1]
    return "nmsdk"


def detect_bilingual(text: str) -> str:
    has_ru = bool(re.search(r"^##\s+RU\b", text, re.MULTILINE))
    has_en = bool(re.search(r"^##\s+EN\b", text, re.MULTILINE))
    if has_ru and has_en:
        return "both"
    if has_en:
        return "en"
    if has_ru:
        return "ru"
    return "unknown"


def has_mermaid(text: str) -> bool:
    return "```mermaid" in text


def parse_upload_classes(files: Iterable[Path]) -> list[str]:
    classes: list[str] = []
    for file in files:
        if not file.exists():
            continue
        text = file.read_text(encoding="utf-8", errors="replace")
        classes.extend(UPLOAD_CLASS_PATTERN.findall(text))
    return sorted(set(classes))


def collect_cmake_metadata() -> dict:
    cmake_files = list(ROOT.rglob("CMakeLists.txt"))
    options: set[str] = set()
    targets: set[str] = set()
    for cmake_file in cmake_files:
        if should_skip_path(cmake_file.relative_to(ROOT)):
            continue
        text = cmake_file.read_text(encoding="utf-8", errors="replace")
        options.update(OPTION_PATTERN.findall(text))
        targets.update(ADD_EXECUTABLE_PATTERN.findall(text))
        targets.update(ADD_LIBRARY_PATTERN.findall(text))
    return {
        "generated_at": utc_now_iso(),
        "options": sorted(options),
        "targets": sorted(targets),
    }


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@dataclass
class BrokenLink:
    source: str
    target: str
    reason: str
