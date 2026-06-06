#!/usr/bin/env python3
"""Replace EN TODO placeholders with English translations of the RU section."""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import iter_markdown_files  # noqa: E402

TODO_MARKER = "<!-- TODO: English translation pending -->"
RU_HEADER = re.compile(r"^##\s+RU\b", re.MULTILINE)
EN_HEADER = re.compile(r"^##\s+EN\b", re.MULTILINE)
SEP = re.compile(r"^---\s*$", re.MULTILINE)

# Preserve code blocks, mermaid, inline code during translation
FENCE = re.compile(r"(```[\s\S]*?```|`[^`\n]+`|\[[^\]]*\]\([^)]+\))")

GLOSSARY_KEEP = (
    "UploadClass",
    "ADefault",
    "ABuild",
    "AReset",
    "ACalculate",
    "UNet",
    "UBitmap",
    "UEPtr",
    "MDMatrix",
    "Nmsdk",
    "Rdk",
    "PulseLib",
    "MotionControlLib",
    "HardwareLib",
    "CvBasicLib",
    "BasicLib",
    "Firmata",
    "Arduino",
    "CMake",
    "vcpkg",
    "Qt",
)


def split_sections(text: str) -> tuple[str, str, str] | None:
    m_ru = RU_HEADER.search(text)
    m_en = EN_HEADER.search(text)
    if not m_ru or not m_en:
        return None
    prefix = text[: m_ru.start()]
    ru_body = text[m_ru.end() : m_en.start()]
    en_body = text[m_en.end() :]
    return prefix, ru_body.strip(), en_body.strip()


def protect_segments(text: str) -> tuple[str, list[str]]:
    store: list[str] = []

    def repl(m: re.Match[str]) -> str:
        store.append(m.group(0))
        return f"⟦PROT{len(store) - 1}⟧"

    protected = FENCE.sub(repl, text)
    return protected, store


def restore_segments(text: str, store: list[str]) -> str:
    for i, seg in enumerate(store):
        text = text.replace(f"⟦PROT{i}⟧", seg)
    return text


def translate_text(text: str, translator) -> str:
    protected, store = protect_segments(text)
    # Chunk to avoid API limits
    max_chunk = 4500
    if len(protected) <= max_chunk:
        chunks = [protected]
    else:
        chunks = []
        lines = protected.split("\n")
        buf: list[str] = []
        size = 0
        for line in lines:
            if size + len(line) + 1 > max_chunk and buf:
                chunks.append("\n".join(buf))
                buf, size = [], 0
            buf.append(line)
            size += len(line) + 1
        if buf:
            chunks.append("\n".join(buf))

    out: list[str] = []
    for chunk in chunks:
        if not chunk.strip():
            out.append(chunk)
            continue
        try:
            out.append(translator.translate(chunk))
        except Exception as exc:  # noqa: BLE001
            print(f"  translate error: {exc}", file=sys.stderr)
            out.append(chunk)
        time.sleep(0.15)
    result = restore_segments("\n".join(out), store)
    for term in GLOSSARY_KEEP:
        # Fix common mangling of identifiers
        result = re.sub(rf"\b{term.lower()}\b", term, result, flags=re.IGNORECASE)
    return result


def needs_fill(en_body: str) -> bool:
    return TODO_MARKER in en_body or len(en_body.strip()) < 40


def process_file(path: Path, apply: bool, translator) -> bool:
    from lib_doc_audit import ROOT  # noqa: E402

    text = path.read_text(encoding="utf-8", errors="replace")
    parts = split_sections(text)
    if not parts:
        return False
    prefix, ru_body, en_body = parts
    if not needs_fill(en_body):
        return False

    en_translated = translate_text(ru_body, translator)
    new_text = f"{prefix}## RU\n\n{ru_body}\n\n---\n\n## EN\n\n{en_translated}\n"
    if apply:
        path.write_text(new_text, encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    print(f"{'APPLY' if apply else 'DRY'}: {rel} ({len(ru_body)} -> {len(en_translated)} bytes)")
    return True


def main() -> int:
    from lib_doc_audit import ROOT  # noqa: E402

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path", help="Single relative path")
    parser.add_argument("--zone", help="Zone prefix filter")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source="ru", target="en")
    except ImportError:
        print("deep-translator required: pip install deep-translator", file=sys.stderr)
        return 1

    zone_prefixes = {
        "motion": "Libraries/Nmsdk-MotionControlLib/",
        "pulse": "Libraries/Nmsdk-PulseLib/",
        "hardware": "Libraries/Rdk-HardwareLib/",
        "cvbasic": "Libraries/Rdk-CvBasicLib/",
        "basic": "Libraries/Rdk-BasicLib/",
        "rdk": "Rdk/",
        "bin": "Bin/",
        "docs": "Docs/",
        "tests": "Tests/",
        "misc": "",
    }

    files = iter_markdown_files()
    if args.path:
        files = [ROOT / args.path]
    elif args.zone:
        prefix = zone_prefixes.get(args.zone, args.zone)
        if prefix:
            files = [p for p in files if p.relative_to(ROOT).as_posix().startswith(prefix)]

    changed = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if TODO_MARKER not in text:
            continue
        if process_file(path, args.apply, translator):
            changed += 1
            if args.limit and changed >= args.limit:
                break

    print(f"Translated: {changed}, apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
