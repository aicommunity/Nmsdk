#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Определение кодировки файлов: Cp1251 vs UTF-8 по сырым байтам.
UTF-8 кириллица: пары 0xD0/0xD1 + 0x80-0xBF.
Cp1251 кириллица: одиночные байты 0xC0-0xFF (не второй байт UTF-8).
"""

import os
import sys


def classify_encoding(data: bytes) -> str:
    """
    Классификация по байтам: 'cp1251' или 'utf8'.
    - UTF-8 кириллица: 0xD0/0xD1 + (0x80-0xBF).
    - Одиночный 0xC0-0xFF (не после 0xD0/0xD1) -> признак Cp1251.
    """
    utf8_pairs = 0
    lone_high = 0
    i = 0
    while i < len(data):
        b = data[i]
        if b in (0xD0, 0xD1) and i + 1 < len(data) and 0x80 <= data[i + 1] <= 0xBF:
            utf8_pairs += 1
            i += 2
            continue
        if 0xC0 <= b <= 0xFF:
            lone_high += 1
        i += 1
    if lone_high > 0 and utf8_pairs == 0:
        return "cp1251"
    if lone_high > 0 and lone_high > utf8_pairs:
        return "cp1251"
    return "utf8"


def main():
    if len(sys.argv) < 2:
        print("Usage: detect_encoding.py <dir_or_file> [dir_or_file ...] [--list cp1251_files.txt]")
        print("  Scans .h and .cpp under given dirs (or single files).")
        print("  --list FILE  write paths of cp1251 files to FILE (one per line).")
        sys.exit(1)
    args = list(sys.argv[1:])
    out_list = None
    if "--list" in args:
        idx = args.index("--list")
        if idx + 1 < len(args):
            out_list = args[idx + 1]
            del args[idx : idx + 2]
    paths = [p for p in args if not p.startswith("--")]
    if not paths:
        sys.exit(2)
    files_to_scan = []
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(".h") or p.endswith(".cpp"):
                files_to_scan.append(os.path.normpath(p))
        elif os.path.isdir(p):
            for root, _, fnames in os.walk(p):
                for f in fnames:
                    if f.endswith(".h") or f.endswith(".cpp"):
                        files_to_scan.append(os.path.normpath(os.path.join(root, f)))
    cp1251_paths = []
    for fpath in sorted(files_to_scan):
        try:
            with open(fpath, "rb") as f:
                data = f.read()
        except OSError as e:
            print(f"{fpath}\t(error: {e})")
            continue
        enc = classify_encoding(data)
        print(f"{fpath}\t{enc}")
        if enc == "cp1251":
            cp1251_paths.append(fpath)
    if out_list and cp1251_paths:
        with open(out_list, "w", encoding="utf-8") as f:
            for p in cp1251_paths:
                f.write(p + "\n")
        print(f"Wrote {len(cp1251_paths)} paths to {out_list}", file=sys.stderr)


if __name__ == "__main__":
    main()
