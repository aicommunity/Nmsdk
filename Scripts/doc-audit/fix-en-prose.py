#!/usr/bin/env python3
"""Fix common Russian leftovers in EN prose and remove duplicate EN tails."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import iter_markdown_files  # noqa: E402

translate_mermaid_in_text = None  # set in main()

PROSE_FIXES = [
    (r"^См\. ", "See "),
    (r"^### См\. также\s*$", "### See Also"),
    (r"^## Источники\s*$", "## References"),
    (r" — общий ", " — common "),
    (r" — рецептор ", " — receptor "),
    (r" — классический ", " — classical "),
    (r" — простой ", " — simple "),
    (r" — архитектура библиотеки", " — library architecture"),
    (r"Семейства:", "Families:"),
    (r" в библиотеках ", " in libraries "),
    (r"нейроморфная модель зрительной системы", "neuromorphic model of the visual system"),
    (r"сигналы актуаторов и нейронные структуры управления", "actuator signals and neural control structures"),
]


def dedupe_en_tail(en: str) -> str:
    """Remove duplicate Russian ## References block appended after English one."""
    markers = list(re.finditer(r"^## References\s*$", en, re.M))
    if len(markers) < 2:
        return en
    # Keep content before second ## References if tail is mostly Russian
    tail = en[markers[1].start() :]
    if len(re.findall(r"[а-яА-ЯёЁ]{4,}", tail)) > 2:
        return en[: markers[1].start()].rstrip() + "\n"
    return en


def fix_en_body(en: str) -> str:
    en = dedupe_en_tail(en)
    en = translate_mermaid_in_text(en)
    lines = []
    for line in en.split("\n"):
        out = line
        for pat, repl in PROSE_FIXES:
            out = re.sub(pat, repl, out)
        lines.append(out)
    return "\n".join(lines)


def process_file(path: Path, apply: bool) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "## EN" not in text:
        return False
    prefix, en_old = text.split("## EN", 1)
    en_new = fix_en_body(en_old)
    if en_new == en_old:
        return False
    if apply:
        path.write_text(prefix + "## EN" + en_new, encoding="utf-8")
    return True


def main() -> int:
    import importlib.util

    global translate_mermaid_in_text
    _spec = importlib.util.spec_from_file_location(
        "cbe", Path(__file__).resolve().parent / "complete-bilingual-en.py"
    )
    _mod = importlib.util.module_from_spec(_spec)
    assert _spec.loader
    _spec.loader.exec_module(_mod)
    translate_mermaid_in_text = _mod.translate_mermaid_in_text

    from lib_doc_audit import ROOT  # noqa: E402

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path-prefix", default="")
    args = parser.parse_args()

    n = 0
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        if args.path_prefix and not rel.startswith(args.path_prefix):
            continue
        if process_file(path, args.apply):
            n += 1
            print(f"{'APPLY' if args.apply else 'DRY'}: {rel}")
    print(f"Fixed: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
