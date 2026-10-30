#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конвертация файлов из Cp1251 в UTF-8.
Читает список путей из файла (по одному пути на строку) или из аргументов.
Пути задаются относительно root_dir (каталог библиотеки или корень репозитория).
"""

import os
import sys


def convert_file(root_dir: str, rel_path: str) -> bool:
    """Конвертировать один файл: прочитать как Cp1251, записать как UTF-8."""
    full = os.path.join(root_dir, rel_path)
    if not os.path.isfile(full):
        print(f"Skip (not found): {rel_path}", file=sys.stderr)
        return False
    try:
        with open(full, "rb") as f:
            data = f.read()
    except OSError as e:
        print(f"Error reading {rel_path}: {e}", file=sys.stderr)
        return False
    try:
        text = data.decode("cp1251", errors="replace")
    except Exception as e:
        print(f"Error decode {rel_path}: {e}", file=sys.stderr)
        return False
    try:
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except OSError as e:
        print(f"Error writing {rel_path}: {e}", file=sys.stderr)
        return False
    print(f"Converted: {rel_path}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_cp1251_to_utf8.py <root_dir> [--list FILE] | <path1> [path2 ...]")
        print("  root_dir     directory to resolve relative paths (e.g. Libraries/Nmsdk-PulseLib)")
        print("  --list FILE  read paths from FILE (one per line)")
        print("  path1 path2  convert these paths (relative to root_dir)")
        sys.exit(1)
    root_dir = os.path.abspath(sys.argv[1])
    args = list(sys.argv[2:])
    paths = []
    if args and args[0] == "--list":
        if len(args) < 2:
            sys.exit(2)
        list_file = args[1]
        try:
            with open(list_file, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().replace("\\", "/")
                    if p:
                        paths.append(p)
        except OSError as e:
            print(f"Error reading list {list_file}: {e}", file=sys.stderr)
            sys.exit(3)
    else:
        paths = [p.replace("\\", "/") for p in args if not p.startswith("--")]
    if not paths:
        print("No paths to convert.")
        sys.exit(0)
    ok = 0
    for p in paths:
        if convert_file(root_dir, p):
            ok += 1
    print(f"Done: {ok}/{len(paths)} converted.", file=sys.stderr)


if __name__ == "__main__":
    main()
