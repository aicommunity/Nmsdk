#!/usr/bin/env python3
"""Replace EN sections that still contain Cyrillic prose with RU->EN translation."""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import importlib.util

from lib_doc_audit import iter_markdown_files  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "cbe", Path(__file__).resolve().parent / "complete-bilingual-en.py"
)
_cbe = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_cbe)

translate_mermaid_in_text = _cbe.translate_mermaid_in_text
rebuild_from_ru = _cbe.rebuild_from_ru
prose_cyrillic_words = _cbe.prose_cyrillic_words

RU_HEADER = re.compile(r"^##\s+RU\b", re.MULTILINE)
EN_HEADER = re.compile(r"^##\s+EN\b", re.MULTILINE)
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
    "Cp1251",
    "UTF-8",
    "HITL",
    "MVP",
    "LLM",
    "GUI",
    "RPC",
    "XML",
    "UBA",
    "API",
)

SKIP_PREFIXES = ("Bin/Configs/SpikeSamples/", "Reports/", "Docs/Audit/")
SKIP_EXACT = {"Docs/Overview/Markdown-Files-Index.md"}


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
    max_chunk = 4500
    lines = protected.split("\n")
    chunks: list[str] = []
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
        if not re.search(r"[а-яА-ЯёЁ]", chunk):
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
        result = re.sub(rf"\b{term.lower()}\b", term, result, flags=re.IGNORECASE)
    return result


def build_en_from_ru(ru_body: str, translator) -> str:
    translated = translate_text(ru_body, translator)
    translated = translate_mermaid_in_text(translated)
    return translated.strip() + "\n"


def add_en_section(text: str, translator) -> str:
    if "## RU" not in text:
        return text
    prefix, ru_body = text.split("## RU", 1)
    ru_body = ru_body.strip()
    en_body = build_en_from_ru(ru_body, translator)
    return f"{prefix}## RU\n\n{ru_body}\n\n---\n\n## EN\n\n{en_body}"


def process_file(path: Path, apply: bool, translator, force: bool) -> str | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    has_en = "## EN" in text

    if not has_en:
        if "## RU" not in text:
            return None
        new_text = add_en_section(text, translator)
        action = "add_en"
    else:
        prefix, en_old = text.split("## EN", 1)
        ru_body = prefix.split("## RU", 1)[1].strip() if "## RU" in prefix else ""
        cyr_count = prose_cyrillic_words(en_old)
        if not force and cyr_count == 0:
            return None
        en_new = build_en_from_ru(ru_body, translator)
        new_text = prefix + "## EN\n\n" + en_new
        action = f"retranslate({cyr_count})"

    if new_text == text:
        return None
    if apply:
        path.write_text(new_text, encoding="utf-8")
    return action


def main() -> int:
    from lib_doc_audit import ROOT  # noqa: E402

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source="ru", target="en")
    except ImportError:
        print("deep-translator required: pip install deep-translator", file=sys.stderr)
        return 1

    if args.path:
        files = [ROOT / p for p in args.path]
    else:
        files = iter_markdown_files()

    changed = 0
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(SKIP_PREFIXES) or rel in SKIP_EXACT:
            continue
        if not path.exists():
            continue
        action = process_file(path, args.apply, translator, args.force)
        if action:
            changed += 1
            print(f"{'APPLY' if args.apply else 'DRY'}: {rel} — {action}")

    print(f"Changed: {changed}, apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
