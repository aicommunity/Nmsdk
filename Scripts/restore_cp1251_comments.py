#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Восстановление битых комментариев в исходниках: извлечение текста из истории Git
(кодировка Cp1251) и подстановка в текущий файл с сохранением в UTF-8.
Сопоставление комментариев по контексту — следующая строка кода (нормализованная).
"""

import re
import subprocess
import sys
import os


def get_ref_content(repo_dir: str, commit: str, file_path_from_repo_root: str) -> str:
    """Получить содержимое файла из коммита в виде сырых байтов и декодировать из Cp1251."""
    cmd = ["git", "-C", repo_dir, "show", f"{commit}:{file_path_from_repo_root}"]
    r = subprocess.run(cmd, capture_output=True, timeout=30, cwd=repo_dir)
    if r.returncode != 0:
        raise RuntimeError(f"git show failed: {r.stderr.decode('utf-8', errors='replace')}")
    return r.stdout.decode("cp1251", errors="replace")


def normalize_code_line(line: str) -> str:
    """Нормализация строки кода для сопоставления (старый ULProperty vs новый UProperty)."""
    s = " ".join(line.strip().split())
    s = re.sub(r",\s+", ",", s)  # убрать пробелы после запятых для единого ключа
    s = re.sub(r"\bULProperty\b", "UProperty", s)
    s = re.sub(r"RDK::UProperty", "UProperty", s)
    s = re.sub(r"\bUPropertyInputData\b", "UProperty", s)
    s = re.sub(r"\bUPropertyOutputData\b", "UProperty", s)
    return s


def is_comment_line(line: str) -> bool:
    """Строка — комментарий (// или ///)."""
    s = line.strip()
    return s.startswith("//") or s.startswith("///")


# Признаки закомментированного кода (не трогать, не заменять на эталонные комментарии)
_CODE_KEYWORDS = re.compile(
    r"^(return|if|else|for|while|switch|case|break|continue|goto|try|catch|throw|"
    r"class|struct|namespace|template|typedef|using|virtual|override|extern|static|"
    r"const|inline|explicit|public|protected|private|delete|new|sizeof|"
    r"static_cast|dynamic_cast|reinterpret_cast|const_cast)\b",
    re.IGNORECASE,
)
_CODE_PATTERNS = re.compile(
    r"[;{}]|"  # конец оператора или блок
    r"\)\s*;|"  # вызов функции;
    r"->|::|"  # C++ указатель/область видимости
    r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*\(",  # идентификатор(
)


def looks_like_commented_out_code(rest: str) -> bool:
    """
    Текст после // или /// похож на закомментированный код, а не на документационный комментарий.
    Такие строки не считаем битыми и не заменяем.
    """
    if not rest or len(rest) > 500:
        return False
    s = rest.strip()
    if re.match(r"^-+\s*$", s):
        return False
    # Ключевые слова C/C++ в начале
    if _CODE_KEYWORDS.search(s):
        return True
    # Символы/паттерны кода
    if _CODE_PATTERNS.search(s):
        return True
    # Строка вида ": something" — часто инициализатор в конструкторе
    if re.match(r"^:\s*\w", s):
        return True
    # Один идентификатор с точкой или стрелкой (вызов метода)
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*(\.|->)\s*\w", s):
        return True
    return False


def is_broken_comment(line: str) -> bool:
    """
    Комментарий «битый»: пустой или нет кириллицы в тексте после // (разделители не трогаем).
    Закомментированный код не считаем битым — не заменяем.
    """
    if not is_comment_line(line):
        return False
    rest = line.strip()
    if rest.startswith("///"):
        rest = rest[3:]
    elif rest.startswith("//"):
        rest = rest[2:]
    rest = rest.strip()
    # Разделители не трогаем
    if re.match(r"^-+\s*$", rest):
        return False
    # Похоже на закомментированный код — не трогать
    if looks_like_commented_out_code(rest):
        return False
    # Пустой или без кириллицы — битый (восстанавливаем из эталона)
    has_cyrillic = any("\u0400" <= c <= "\u04FF" for c in rest)
    return rest == "" or not has_cyrillic


def is_code_line(line: str) -> bool:
    """Строка не пустая и не только комментарий — считаем строкой кода для контекста."""
    s = line.strip()
    if not s:
        return False
    if s.startswith("//") or s.startswith("/*") or s.startswith("*"):
        return False
    return True


def build_comment_map(ref_lines: list[str]) -> dict[str, list[str]]:
    """
    По эталонному файлу (список строк) строим карту: нормализованная строка кода -> комментарии над ней.
    Несколько подряд идущих комментариев над одной строкой кода объединяются в список.
    """
    comment_map: dict[str, list[str]] = {}
    pending_comments: list[str] = []

    for line in ref_lines:
        if is_comment_line(line):
            pending_comments.append(line.rstrip("\r\n"))
        elif is_code_line(line):
            key = normalize_code_line(line)
            if key and pending_comments:
                comment_map[key] = pending_comments
            pending_comments = []
        else:
            # Пустая строка — сбрасываем накопленные комментарии к следующему блоку
            pending_comments = []

    return comment_map


def apply_restoration(
    current_lines: list[str], comment_map: dict[str, list[str]]
) -> list[str]:
    """
    Проход по текущему файлу: битые комментарии заменяем на эталонные по следующей строке кода.
    Для одного и того же следующего кода эталонный блок выводим только один раз (без дублей).
    """
    result: list[str] = []
    last_output_code_key: str | None = None
    i = 0
    while i < len(current_lines):
        line = current_lines[i]
        if not is_broken_comment(line):
            result.append(line)
            i += 1
            continue
        broken_block: list[int] = []
        j = i
        while j < len(current_lines) and is_broken_comment(current_lines[j]):
            broken_block.append(j)
            j += 1
        next_code = None
        next_code_idx = j
        while next_code_idx < len(current_lines):
            if is_code_line(current_lines[next_code_idx]):
                next_code = normalize_code_line(current_lines[next_code_idx])
                break
            next_code_idx += 1
        if next_code and next_code in comment_map:
            if next_code != last_output_code_key:
                ref_comments = comment_map[next_code]
                for c in ref_comments:
                    result.append(c + "\n")
                last_output_code_key = next_code
            # иначе дубликат — не выводим ни эталон, ни битые строки (убираем дубли)
        else:
            for idx in broken_block:
                result.append(current_lines[idx])
        i = j
    return result


def main():
    if len(sys.argv) < 3:
        print("Usage: restore_cp1251_comments.py <repo_dir> <file_path_from_repo_root> [commit]")
        print("  repo_dir = path to git repo (e.g. Libraries/Nmsdk-PulseLib)")
        print("  file_path_from_repo_root = path from repo root, e.g. Core/NPulseSynapse.h")
        print("  commit = optional, default bcf94ed")
        sys.exit(1)
    repo_dir = os.path.abspath(sys.argv[1])
    file_path = sys.argv[2]
    commit = sys.argv[3] if len(sys.argv) > 3 else "bcf94ed"
    current_path = os.path.join(repo_dir, file_path)
    if not os.path.isfile(current_path):
        print(f"File not found: {current_path}")
        sys.exit(2)
    try:
        ref_text = get_ref_content(repo_dir, commit, file_path)
    except RuntimeError as e:
        print(f"Skip (file not in commit {commit}): {file_path}", file=sys.stderr)
        sys.exit(0)
    ref_lines = ref_text.splitlines(keepends=False)
    ref_lines_with_eol = [ln + "\n" for ln in ref_text.splitlines()]
    if ref_lines_with_eol and not ref_text.endswith("\n"):
        ref_lines_with_eol[-1] = ref_lines[-1]
    with open(current_path, "r", encoding="utf-8", errors="replace") as f:
        current_content = f.read()
    current_lines = current_content.splitlines(keepends=True)
    if not current_lines and current_content:
        current_lines = [current_content]
    comment_map = build_comment_map(ref_lines)
    restored = apply_restoration(current_lines, comment_map)
    out_content = "".join(restored)
    with open(current_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out_content)
    print(f"Restored comments in {file_path} (commit {commit})")


if __name__ == "__main__":
    main()
