#!/usr/bin/env python3
"""
Восстановление пустых Interface.xml в Bin/Configs по данным отчёта
config-earliest-and-preceding*.json.

По умолчанию обрабатываются только Bin/Configs/SpikeSamples.
С --exclude-spikesamples — все Bin/Configs кроме SpikeSamples (отчёт: *-other.json).

Для каждого пустого (<= 20 байт) Interface.xml: ищем запись в отчёте, в предшествующих
коммитах — папку с тем же leaf и непустой Interface.xml, записываем в файл.

Запуск из корня Nmsdk. --dry-run только выводит, что было бы восстановлено.
"""
from pathlib import Path
import subprocess
import sys
import json
import argparse

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BIN_DIR = REPO_ROOT / "Bin"
CONFIGS_ROOT = BIN_DIR / "Configs"
SPIKESAMPLES = CONFIGS_ROOT / "SpikeSamples"
REPORT_JSON = REPO_ROOT / "Reports" / "config-earliest-and-preceding.json"
REPORT_OTHER_JSON = REPO_ROOT / "Reports" / "config-earliest-and-preceding-other.json"
EMPTY_THRESHOLD = 20


def run_git(cwd, *args, timeout=30):
    cmd = ["git", "-C", str(cwd)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def get_content_at_commit(bin_dir, commit, path_from_bin):
    code, out, err = run_git(bin_dir, "show", f"{commit}:{path_from_bin}")
    if code != 0:
        return None
    return out


def main():
    ap = argparse.ArgumentParser(description="Restore empty Interface.xml using report")
    ap.add_argument("--dry-run", action="store_true", help="Only print what would be restored")
    ap.add_argument("--report", type=Path, default=None, help="Path to JSON report (default: *-other.json if --exclude-spikesamples)")
    ap.add_argument("--exclude-spikesamples", action="store_true", help="Process all Configs except SpikeSamples")
    args = ap.parse_args()

    if args.report is None:
        args.report = REPORT_OTHER_JSON if args.exclude_spikesamples else REPORT_JSON

    if not BIN_DIR.is_dir():
        print(f"Каталог Bin не найден: {BIN_DIR}", file=sys.stderr)
        return 1
    if not args.report.exists():
        print(f"Отчёт не найден: {args.report}. Сначала выполните config_earliest_commit_and_preceding.py --exclude-spikesamples --json {args.report}", file=sys.stderr)
        return 1

    with open(args.report, encoding="utf-8") as f:
        report = json.load(f)
    by_config = {e["config_rel"]: e for e in report}

    empty_files = []
    if args.exclude_spikesamples:
        search_root = CONFIGS_ROOT
        skip_prefix = "Configs/SpikeSamples/"
    else:
        search_root = SPIKESAMPLES
        skip_prefix = None
    for path in sorted(search_root.rglob("Interface.xml")):
        try:
            if not path.is_file() or path.stat().st_size > EMPTY_THRESHOLD:
                continue
            rel = path.relative_to(BIN_DIR)
            config_rel = str(rel.parent).replace("\\", "/")
            if skip_prefix and config_rel.startswith(skip_prefix):
                continue
            empty_files.append((path, config_rel))
        except (ValueError, OSError):
            continue

    scope = "Configs (кроме SpikeSamples)" if args.exclude_spikesamples else "SpikeSamples"
    if not empty_files:
        print(f"Пустых Interface.xml в {scope} не найдено.")
        return 0

    restored = []
    no_source = []
    for abspath, config_rel in empty_files:
        entry = by_config.get(config_rel)
        if not entry or not entry.get("preceding"):
            no_source.append(config_rel + "/Interface.xml")
            continue
        # Перебираем все предшествующие коммиты (от новых к старым); первый с непустым Interface.xml — используем
        content = None
        used_commit = None
        used_old_path = None
        for p in entry["preceding"]:
            commit_short = p["commit"]
            for d, files in p["paths_by_dir"].items():
                if "Interface.xml" not in files:
                    continue
                old_path = f"{d}/Interface.xml"
                raw = get_content_at_commit(BIN_DIR, commit_short, old_path)
                if raw and len(raw.encode("utf-8")) > EMPTY_THRESHOLD:
                    content = raw
                    used_commit = commit_short
                    used_old_path = old_path
                    break
            if content is not None:
                break
        if not content:
            no_source.append(config_rel + "/Interface.xml")
            continue
        if not args.dry_run:
            abspath.write_text(content, encoding="utf-8")
        restored.append((config_rel + "/Interface.xml", used_commit, used_old_path, len(content)))

    print(f"Пустых Interface.xml в {scope}: {len(empty_files)}")
    print(f"Восстановлено: {len(restored)}")
    for rel, commit, old_path, size in restored:
        print(f"  {rel} <- {commit} ({old_path}, {size} байт)")
    if no_source:
        print(f"Без источника в !OldConfigs: {len(no_source)}")
        for p in no_source:
            print(f"  {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
