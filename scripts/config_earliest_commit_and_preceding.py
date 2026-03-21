#!/usr/bin/env python3
"""
Для каждой конфигурации в Bin/Configs/SpikeSamples:
1) Найти самый ранний коммит в истории Bin, где появляется эта конфигурация (по пути).
2) В предшествующих коммитах (предки родителя самого раннего коммита) искать
   соответствующие папки с тем же именем (leaf) под Configs/ и вывести список файлов в них.

Запуск из корня Nmsdk; репозиторий Bin — Bin/. Пути для git — относительно Bin.
Результат: отчёт в stdout и опционально JSON/Markdown в файл.
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
MAX_ANCESTORS = 800


def run_git(cwd, *args, timeout=60):
    cmd = ["git", "-C", str(cwd)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def get_commits_for_file(bin_dir, path_from_bin):
    """Все коммиты, в которых фигурирует path_from_bin (относительно Bin), от новых к старым."""
    code, out, _ = run_git(bin_dir, "log", "--all", "--format=%H", "--", path_from_bin)
    if code != 0:
        return []
    return [h.strip() for h in out.strip().splitlines() if h.strip()]


def rev_list_ancestors(bin_dir, commit, max_count=MAX_ANCESTORS):
    """Список хешей коммитов-предков commit (от новых к старым)."""
    code, out, _ = run_git(bin_dir, "rev-list", "--max-count", str(max_count), str(commit))
    if code != 0:
        return []
    return [h.strip() for h in out.strip().splitlines() if h.strip()]


def ls_tree_dir(bin_dir, commit, prefix):
    """Список путей под prefix в коммите (рекурсивно). prefix вида 'Configs/'."""
    code, out, _ = run_git(bin_dir, "ls-tree", "-r", "--name-only", commit, "--", prefix)
    if code != 0:
        return []
    return [p for p in out.strip().splitlines() if p.startswith(prefix)]


def get_commit_date_subject(bin_dir, commit):
    code, out, _ = run_git(bin_dir, "log", "-1", "--format=%ci %s", commit)
    if code != 0:
        return ""
    return out.strip()


def collect_config_folders(exclude_spikesamples=False):
    """Папки конфигураций: каждая содержит project.ini или Interface.xml.
    Если exclude_spikesamples=True — только под Configs, но не под Configs/SpikeSamples.
    Иначе — только под SpikeSamples (как раньше).
    """
    seen = set()
    if exclude_spikesamples:
        search_root = CONFIGS_ROOT
        skip_prefix = "Configs/SpikeSamples/"
    else:
        search_root = SPIKESAMPLES
        skip_prefix = None
    for marker in ["project.ini", "Project.ini", "Interface.xml"]:
        for path in sorted(search_root.rglob(marker)):
            try:
                if not path.is_file():
                    continue
                dir_path = path.parent
                rel = dir_path.relative_to(BIN_DIR)
                key = str(rel).replace("\\", "/")
                if skip_prefix and key.startswith(skip_prefix):
                    continue
                if key not in seen:
                    seen.add(key)
                    yield dir_path, key
            except (ValueError, OSError):
                continue


def path_from_bin_relative(rel_dir, filename):
    return f"{rel_dir}/{filename}".replace("\\", "/")


def find_earliest_commit_for_path(bin_dir, path_from_bin):
    """Самый ранний коммит, в котором существует path_from_bin."""
    commits = get_commits_for_file(bin_dir, path_from_bin)
    if not commits:
        return None
    return commits[-1]


def same_leaf_paths_under_configs(all_paths, leaf_name):
    """Из списка путей под Configs/ отобрать те, что заканчиваются на /<leaf_name>/<file>."""
    prefix = f"/{leaf_name}/"
    return [p for p in all_paths if prefix in p and p.count("/") >= 2 and p.split("/")[-2] == leaf_name]


def paths_containing_leaf(all_paths, leaf_name):
    """Любые пути под Configs/, в которых leaf_name встречается как компонент пути (директория)."""
    return [p for p in all_paths if f"/{leaf_name}/" in p or p.rstrip("/").endswith(f"/{leaf_name}")]


def group_paths_by_parent_dir(paths):
    """Сгруппировать пути по родительской директории (конфиг-папка)."""
    by_dir = {}
    for p in paths:
        parts = p.rsplit("/", 1)
        if len(parts) == 2:
            d, f = parts
            by_dir.setdefault(d, []).append(f)
    return {d: sorted(files) for d, files in sorted(by_dir.items())}


def main():
    ap = argparse.ArgumentParser(description="Earliest commit per config and preceding commits search")
    ap.add_argument("--json", type=Path, help="Write JSON report to file")
    ap.add_argument("--md", type=Path, help="Write Markdown report to file")
    ap.add_argument("--max-ancestors", type=int, default=MAX_ANCESTORS, help="Max preceding commits to scan")
    ap.add_argument("--exclude-spikesamples", action="store_true", help="Process all Configs except SpikeSamples")
    args = ap.parse_args()
    max_ancestors = args.max_ancestors

    if not BIN_DIR.is_dir():
        print(f"Каталог Bin не найден: {BIN_DIR}", file=sys.stderr)
        return 1
    if not (BIN_DIR / ".git").exists():
        print("Bin не является git-репозиторием.", file=sys.stderr)
        return 1

    configs = list(collect_config_folders(exclude_spikesamples=args.exclude_spikesamples))
    # Кэш: один ls_tree и один rev-list на коммит
    cache_paths = {}
    cache_date = {}
    cache_preceding = {}

    report = []
    for dir_path, rel_dir in configs:
        # rel_dir относительно Bin, например Configs/SpikeSamples/STDP/STDP-Simple-01
        parts = rel_dir.replace("\\", "/").split("/")
        if len(parts) < 2:
            continue
        leaf_name = parts[-1]

        # Репрезентативный файл для поиска истории по текущему пути
        probe_file = "Interface.xml"
        probe_path = path_from_bin_relative(rel_dir, probe_file)
        if not (dir_path / probe_file).exists():
            probe_file = "project.ini"
            probe_path = path_from_bin_relative(rel_dir, probe_file)
        if not (dir_path / probe_file).exists():
            for f in ["project.ini", "Project.ini"]:
                if (dir_path / f).exists():
                    probe_file = f
                    probe_path = path_from_bin_relative(rel_dir, probe_file)
                    break

        earliest = find_earliest_commit_for_path(BIN_DIR, probe_path) if probe_path else None
        if not earliest:
            entry = {
                "config_rel": rel_dir,
                "leaf": leaf_name,
                "earliest_commit": None,
                "earliest_date_subject": None,
                "preceding": [],
                "preceding_broad": [],
            }
            report.append(entry)
            continue

        date_subj = get_commit_date_subject(BIN_DIR, earliest)
        parent = earliest + "^"
        code, _, _ = run_git(BIN_DIR, "rev-parse", parent)
        if code != 0:
            preceding_commits = []
        else:
            if parent not in cache_preceding:
                cache_preceding[parent] = rev_list_ancestors(BIN_DIR, parent, max_count=max_ancestors)
            preceding_commits = cache_preceding[parent]

        preceding_found = []
        preceding_broad = []
        for anc in preceding_commits:
            if anc not in cache_paths:
                cache_paths[anc] = ls_tree_dir(BIN_DIR, anc, "Configs/")
                cache_date[anc] = get_commit_date_subject(BIN_DIR, anc)
            all_paths = cache_paths[anc]
            anc_date = cache_date[anc]
            same_leaf = same_leaf_paths_under_configs(all_paths, leaf_name)
            contains_leaf = paths_containing_leaf(all_paths, leaf_name)
            if same_leaf:
                by_dir = group_paths_by_parent_dir(same_leaf)
                preceding_found.append({
                    "commit": anc[:8],
                    "date_subject": anc_date,
                    "paths_by_dir": by_dir,
                })
            if contains_leaf and not same_leaf:
                by_dir_broad = group_paths_by_parent_dir(contains_leaf)
                preceding_broad.append({
                    "commit": anc[:8],
                    "date_subject": anc_date,
                    "paths_by_dir": by_dir_broad,
                })

        entry = {
            "config_rel": rel_dir,
            "leaf": leaf_name,
            "earliest_commit": earliest[:8],
            "earliest_date_subject": date_subj,
            "preceding": preceding_found,
            "preceding_broad": preceding_broad,
        }
        report.append(entry)

    # Вывод в stdout (кратко)
    for e in report:
        print(f"Config: {e['config_rel']}")
        print(f"  Leaf: {e['leaf']}")
        print(f"  Earliest commit: {e['earliest_commit']}  {e['earliest_date_subject'] or 'N/A'}")
        if e["preceding"]:
            print(f"  In preceding commits (exact leaf folder):")
            for p in e["preceding"][:10]:
                print(f"    {p['commit']} {p['date_subject'][:50]}")
                for dir_path, files in list(p["paths_by_dir"].items())[:3]:
                    print(f"      {dir_path}: {files}")
            if len(e["preceding"]) > 10:
                print(f"    ... and {len(e['preceding']) - 10} more preceding commits with matches")
        if e.get("preceding_broad"):
            print(f"  In preceding commits (path contains leaf name):")
            for p in e["preceding_broad"][:5]:
                print(f"    {p['commit']} {p['date_subject'][:50]}")
                for dir_path, files in list(p["paths_by_dir"].items())[:2]:
                    print(f"      {dir_path}: {files}")
        if not e["preceding"] and not e.get("preceding_broad"):
            print("  (No matching folders in preceding commits)")
        print()

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"JSON report written to {args.json}", file=sys.stderr)

    if args.md:
        write_md_report(report, args.md)
        print(f"Markdown report written to {args.md}", file=sys.stderr)

    return 0


def write_md_report(report, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Отчёт: самый ранний коммит для каждой конфигурации и поиск в предшествующих коммитах",
        "",
        "Для каждой папки конфигурации в `Bin/Configs/SpikeSamples` указан самый ранний коммит репозитория Bin, "
        "в котором она появляется по текущему пути, и в предшествующих коммитах — соответствующие папки с тем же именем (leaf) и файлы в них.",
        "",
    ]
    for e in report:
        lines.append(f"## {e['config_rel']}")
        lines.append("")
        lines.append(f"- **Leaf (имя папки):** `{e['leaf']}`")
        lines.append(f"- **Самый ранний коммит:** `{e['earliest_commit']}` — {e['earliest_date_subject'] or 'N/A'}")
        if e["preceding"]:
            lines.append("- **В предшествующих коммитах найдены папки с тем же именем (leaf):**")
            for p in e["preceding"]:
                lines.append(f"  - `{p['commit']}` {p['date_subject']}")
                for dir_path, files in p["paths_by_dir"].items():
                    lines.append(f"    - `{dir_path}/` → {', '.join(files)}")
        if e.get("preceding_broad"):
            lines.append("- **В предшествующих коммитах пути, содержащие имя папки:**")
            for p in e["preceding_broad"]:
                lines.append(f"  - `{p['commit']}` {p['date_subject']}")
                for dir_path, files in p["paths_by_dir"].items():
                    lines.append(f"    - `{dir_path}/` → {', '.join(files)}")
        if not e["preceding"] and not e.get("preceding_broad"):
            lines.append("- В предшествующих коммитах папок/путей с таким именем не найдено.")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
