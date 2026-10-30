#!/usr/bin/env python3
"""Complete bilingual EN: sync mermaid, translate diagram labels, expand short EN."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import iter_markdown_files  # noqa: E402

MERMAID_BLOCK = re.compile(r"```mermaid\n([\s\S]*?)```", re.MULTILINE)
FENCE_BLOCK = re.compile(r"(```[\s\S]*?```)")

# Longest-first phrase replacements for mermaid labels (RU -> EN)
MERMAID_PHRASES: list[tuple[str, str]] = sorted(
    [
        ("Генерация спайков", "Spike generation"),
        ("Выходной спайк", "Output spike"),
        ("Определение направления", "Direction detection"),
        ("Обработка сигналов", "Signal processing"),
        ("Создание связей", "Creating links"),
        ("Создание нейронов", "Creating neurons"),
        ("Создание задержки", "Creating delay"),
        ("Создание генераторов", "Creating generators"),
        ("Создание нейронов принятия решений", "Creating decision neurons"),
        ("Создание связей между компонентами", "Creating links between components"),
        ("Готов к работе", "Ready"),
        ("После сброса", "After reset"),
        ("Завершение шага", "Step complete"),
        ("Начало ACalculate", "Start ACalculate"),
        ("Начало ABuild", "Start ABuild"),
        ("Изображение<br/>валидно?", "Image<br/>valid?"),
        ("Изображение валидно?", "Image valid?"),
        ("Обработка палочек", "Rod processing"),
        ("Обработка R колбочек", "R cone processing"),
        ("Обработка G колбочек", "G cone processing"),
        ("Обработка B колбочек", "B cone processing"),
        ("Обновление выходных изображений", "Update output images"),
        ("Инициализация ядер ретины", "Initialize retina cores"),
        ("Установка разрешения, сброс траектории", "Set resolution, reset trajectory"),
        ("Конвертация изображения", "Image conversion"),
        ("Обработка изображения", "Image processing"),
        ("Дендриты (N_d дендритов)", "Dendrites (N_d dendrites)"),
        ("Синапсы (N_syn синапсов)", "Synapses (N_syn synapses)"),
        ("Сома (N_s участков)", "Soma (N_s segments)"),
        ("Дендрит 1", "Dendrite 1"),
        ("Дендрит 2", "Dendrite 2"),
        ("Дендрит N_d", "Dendrite N_d"),
        ("Синапс 1", "Synapse 1"),
        ("Синапс 2", "Synapse 2"),
        ("Синапс N_syn", "Synapse N_syn"),
        ("LT-зона", "LT zone"),
        ("Создание", "Creation"),
        ("Уничтожение", "Destroy"),
        ("Создание LeftEngine", "Create LeftEngine"),
        ("Создание RightEngine", "Create RightEngine"),
        ("Создание Sinchro1", "Create Sinchro1"),
        ("Создание Sinchro2", "Create Sinchro2"),
        ("Создание NOTGenerator", "Create NOTGenerator"),
        ("Создание Delay1To2", "Create Delay1To2"),
        ("Создание ORNeuron", "Create ORNeuron"),
        ("Создание NOTNeuron", "Create NOTNeuron"),
        ("Создание IsForwardNeuron, IsLeftNeuron, IsRightNeuron, IsBackNeuron",
         "Create IsForwardNeuron, IsLeftNeuron, IsRightNeuron, IsBackNeuron"),
        ("Создание StayNeuron, ForwardNeuron, LeftNeuron, RightNeuron, BackNeuron",
         "Create StayNeuron, ForwardNeuron, LeftNeuron, RightNeuron, BackNeuron"),
        ("Каждый шаг вычислений", "Each calculation step"),
        ("Конец", "End"),
        ("Начало", "Start"),
        ("Сома", "Soma"),
        ("Дендриты", "Dendrites"),
        ("Дендрит", "Dendrite"),
        ("Синапсы", "Synapses"),
        ("Синапс", "Synapse"),
        ("Обработка", "Processing"),
        ("Создание", "Create"),
        ("Инициализация", "Initialization"),
        ("Построение", "Build"),
        ("Сброс", "Reset"),
        ("Вычисление", "Calculate"),
        ("Описание", "Description"),
        ("Назначение", "Purpose"),
        ("Свойства", "Properties"),
        ("Методы", "Methods"),
        ("Примеры", "Examples"),
        ("Источники", "References"),
        ("Литература", "Literature"),
        ("валидно", "valid"),
        ("Изображение", "Image"),
        ("Генератор левого двигателя", "Left engine generator"),
        ("Генератор правого двигателя", "Right engine generator"),
        ("Синхронизация 1", "Synchronization 1"),
        ("Синхронизация 2", "Synchronization 2"),
        ("Нейроны принятия решений", "Decision neurons"),
        ("Базовые компоненты", "Basic components"),
        ("Внешние компоненты", "External components"),
        ("Внешний стимул", "External stimulus"),
        ("Каналы", "Channels"),
        ("наследуется", "inherits"),
        ("создает", "creates"),
        ("входной сигнал", "input signal"),
        ("выходной сигнал", "output signal"),
        ("токи", "currents"),
        ("сигналы", "signals"),
        ("потенциал", "potential"),
        ("спайки", "spikes"),
        ("использует", "uses"),
        ("Создание связей между компонентами", "Creating links between components"),
        ("LinkComponents[Создание связей между компонентами]", "LinkComponents[Creating links between components]"),
    ],
    key=lambda x: -len(x[0]),
)

HEADING_MAP = {
    "UML-диаграмма классов": "Class Diagram",
    "UML-диаграмма последовательности": "Sequence Diagram",
    "UML-диаграмма состояний": "State Diagram",
    "UML-диаграмма активности": "Activity Diagram",
    "UML-диаграмма компонентов": "Component Diagram",
    "Примеры использования": "Usage Examples",
    "Свойства": "Properties",
    "Методы": "Methods",
    "Источники": "References",
    "Литература": "Literature",
    "Описание": "Description",
    "Назначение": "Purpose",
    "Требования": "Requirements",
    "Обзор": "Overview",
}

PROSE_PHRASES: list[tuple[str, str]] = sorted(
    [
        ("Сводный список классов, регистрируемых через",
         "Summary list of classes registered via"),
        ("Получено автоматически по исходникам",
         "Generated automatically from source files"),
        ("Повторяющиеся псевдонимы сохранены для трассировки.",
         "Duplicate aliases are kept for traceability."),
        ("зарегистрированных классов", "registered classes"),
        ("полный список:", "full list:"),
        ("отчёт:", "report:"),
        ("Эта инвентаризация — исходная точка для дальнейших шагов",
         "This inventory is the starting point for next steps"),
        ("(сопоставление с", "(mapping to"),
        ("группировка, подробная документация компонентов и диаграммы).",
         "grouping, detailed component documentation, and diagrams)."),
        ("см.", "see"),
        ("нейроморфная модель зрительной системы.",
         "neuromorphic model of the visual system."),
    ],
    key=lambda x: -len(x[0]),
)


def translate_mermaid_content(body: str) -> str:
    for ru, en in MERMAID_PHRASES:
        body = body.replace(ru, en)
    return body


def translate_mermaid_in_text(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return "```mermaid\n" + translate_mermaid_content(m.group(1)) + "```"

    return MERMAID_BLOCK.sub(repl, text)


def translate_heading(line: str) -> str:
    if not line.startswith("#"):
        return line
    out = line
    for ru, en in HEADING_MAP.items():
        out = out.replace(ru, en)
    return out


def translate_prose_chunk(text: str) -> str:
    if not re.search(r"[а-яА-ЯёЁ]", text):
        return text
    out = text
    for ru, en in PROSE_PHRASES:
        out = out.replace(ru, en)
    lines = []
    for line in out.split("\n"):
        if line.startswith("#"):
            lines.append(translate_heading(line))
        else:
            lines.append(line)
    return "\n".join(lines)


def split_fenced(text: str) -> list[tuple[str, str]]:
    """Return list of (kind, content) where kind is 'text' or 'fence'."""
    parts = FENCE_BLOCK.split(text)
    result: list[tuple[str, str]] = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if part.startswith("```"):
            result.append(("fence", part))
        else:
            result.append(("text", part))
    return result


def rebuild_from_ru(ru_body: str) -> str:
    """Build EN body mirroring RU structure with translations."""
    chunks = split_fenced(ru_body)
    out: list[str] = []
    for kind, content in chunks:
        if kind == "fence":
            if content.startswith("```mermaid"):
                out.append(translate_mermaid_in_text(content))
            else:
                out.append(content)
        else:
            out.append(translate_prose_chunk(content))
    return "".join(out)


def parse_sections(text: str) -> list[tuple[str, str]]:
    lines = text.split("\n")
    sections: list[tuple[str, str]] = []
    cur_h = ""
    cur_lines: list[str] = []
    for line in lines:
        if re.match(r"^##\s+", line):
            if cur_h or cur_lines:
                sections.append((cur_h, "\n".join(cur_lines).strip()))
            cur_h = line
            cur_lines = []
        else:
            cur_lines.append(line)
    sections.append((cur_h, "\n".join(cur_lines).strip()))
    return sections


def translate_section_heading(h: str) -> str:
    if not h:
        return h
    out = h
    for ru, en in HEADING_MAP.items():
        out = out.replace(ru, en)
    # Generic ## UML-... patterns
    out = re.sub(r"^## UML-диаграмма (\S+)", r"## \1 Diagram", out)
    return out


def sync_mermaid_by_section(ru_body: str, en_body: str) -> str:
    """Sync mermaid into existing EN sections only; never append full RU sections."""
    ru_secs = parse_sections(ru_body)
    en_secs = parse_sections(en_body)
    new_en_secs: list[tuple[str, str]] = []

    for i, (en_h, en_content) in enumerate(en_secs):
        en_h = translate_section_heading(en_h)
        if i < len(ru_secs):
            _, ru_content = ru_secs[i]
            ru_m = MERMAID_BLOCK.findall(ru_content)
            en_m_count = len(MERMAID_BLOCK.findall(en_content))
            if en_m_count < len(ru_m) and ru_m:
                extra = ru_m[en_m_count:]
                blocks = [
                    "```mermaid\n" + translate_mermaid_content(b) + "```" for b in extra
                ]
                en_content = (en_content + "\n\n" + "\n\n".join(blocks)).strip()
        en_content = translate_mermaid_in_text(en_content)
        new_en_secs.append((en_h, en_content))

    ru_all = MERMAID_BLOCK.findall(ru_body)
    en_all = MERMAID_BLOCK.findall("\n\n".join(c for _, c in new_en_secs))
    if len(en_all) < len(ru_all) and new_en_secs:
        extra = ru_all[len(en_all) :]
        blocks = ["```mermaid\n" + translate_mermaid_content(b) + "```" for b in extra]
        h, c = new_en_secs[-1]
        new_en_secs[-1] = (h, (c + "\n\n" + "\n\n".join(blocks)).strip())

    return "\n\n".join(
        (f"{h}\n\n{c}" if h else c).strip() for h, c in new_en_secs if h or c
    ).strip() + "\n"


def prose_cyrillic_words(en_body: str) -> int:
    en_nc = FENCE_BLOCK.sub("", en_body)
    en_nc = re.sub(r"`[^`]+`", "", en_nc)
    return len(re.findall(r"[а-яА-ЯёЁ]{4,}", en_nc))


def needs_expand(ru_body: str, en_body: str) -> bool:
    """Expand when EN prose is Russian or nearly empty."""
    if prose_cyrillic_words(en_body) > 2:
        return True
    ru_len = len(ru_body.strip())
    en_len = len(en_body.strip())
    if ru_len > 800 and en_len < 120:
        return True
    return False


def process_file(path: Path, apply: bool, force_expand: bool) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "## RU" not in text or "## EN" not in text:
        return {}

    prefix, en_old = text.split("## EN", 1)
    ru_body = prefix.split("## RU", 1)[1].strip()

    stats: dict[str, int] = {}
    en_stripped = en_old.strip()
    if needs_expand(ru_body, en_stripped) or force_expand:
        en_new = rebuild_from_ru(ru_body)
        stats["expand"] = 1
    else:
        en_new = sync_mermaid_by_section(ru_body, en_stripped)
        old_m = len(MERMAID_BLOCK.findall(en_stripped))
        new_m = len(MERMAID_BLOCK.findall(en_new))
        if new_m > old_m:
            stats["mermaid_sync"] = new_m - old_m
        if translate_mermaid_in_text(en_stripped) != translate_mermaid_in_text(en_new):
            stats["mermaid_labels"] = 1

    if en_new.strip() == en_old.strip():
        return {}

    if apply:
        path.write_text(prefix + "## EN\n\n" + en_new.strip() + "\n", encoding="utf-8")
    return stats


def main() -> int:
    from lib_doc_audit import ROOT  # noqa: E402

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path-prefix", default="")
    parser.add_argument("--expand-all-short", action="store_true")
    args = parser.parse_args()

    totals: dict[str, int] = {}
    files = 0
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(("Bin/Configs/SpikeSamples/", "Reports/", "Docs/Audit/")):
            continue
        if rel == "Docs/Overview/Markdown-Files-Index.md":
            continue
        if args.path_prefix and not rel.startswith(args.path_prefix):
            continue
        stats = process_file(path, args.apply, args.expand_all_short)
        if stats:
            files += 1
            print(f"{'APPLY' if args.apply else 'DRY'}: {rel} {stats}")
            for k, v in stats.items():
                totals[k] = totals.get(k, 0) + v

    print(f"Files: {files}, totals: {totals}, apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
