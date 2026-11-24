"""Verify immutable inputs, pinned sources and canonical Release execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_paths import report_path
REPO = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args, directory=REPO):
    return subprocess.check_output(["git", *args], cwd=directory, text=True, encoding="utf-8").strip()


def main(run):
    original = json.loads((REPO / ".git/classic-struct-train/original-state.json").read_text(encoding="utf-8-sig"))
    manifest = json.loads((REPO / "Bin/Configs/StructTrainClassic/Prepared/manifest.json").read_text(encoding="utf-8"))
    errors = []
    archive = REPO / "Docs/ClassicStructTrainExperiments"
    for item in original["archive"]:
        if sha(archive / item["path"]).lower() != item["sha256"].lower():
            errors.append("Changed archive input: " + item["path"])
    for item in manifest["verbatim_configs"]:
        if sha(REPO / "Bin/Configs/StructTrainClassic" / item["path"]) != item["sha256"]:
            errors.append("Changed verbatim configuration: " + item["path"])
    if git("rev-parse", "HEAD") != manifest["root_sha"] or git("branch", "--show-current") != "autoPreset":
        errors.append("Unexpected main repository revision or branch")
    if git("branch", "--show-current", directory=REPO / "Bin") != "autoPreset":
        errors.append("Bin is not on the user-created autoPreset branch")
    submodules = git("submodule", "status", "--recursive").splitlines()
    if any(line.lstrip().startswith(("+", "-", "U")) for line in submodules):
        errors.append("A submodule does not match its pinned gitlink")
    production = {}
    for relative in ["Libraries/Nmsdk-PulseLib", "Rdk"]:
        production[relative] = git("status", "--short", directory=REPO / relative)
        if production[relative]:
            errors.append("Production source is modified: " + relative)
    cache = (REPO / "build/win-vs2022-ninja-release-localqt/CMakeCache.txt").read_text(encoding="utf-8")
    if "CMAKE_BUILD_TYPE:STRING=Release" not in cache or "/O2 /Ob2 /DNDEBUG" not in cache:
        errors.append("Release optimization is not enabled in CMake cache")
    canonical = (REPO / "Bin/Platform/Win").resolve()
    processes = []
    for path in sorted(run.glob("*/process.json")):
        p = json.loads(path.read_text(encoding="utf-8-sig"))
        if Path(p["cwd"]).resolve() != canonical or Path(p["command"][0]).resolve().parent != canonical:
            errors.append("Unexpected runtime path: " + str(path))
        processes.append({"job": path.parent.name, "binary_sha256": p["binary_sha256"], "cwd": p["cwd"], "status": p["status"]})
    scripts = {str(p.relative_to(REPO)): sha(p) for p in Path(__file__).parent.iterdir() if p.is_file()}
    result = {"passed": not errors, "errors": errors, "archive_files_checked": len(original["archive"]),
              "verbatim_configs_checked": len(manifest["verbatim_configs"]), "production_source_status": production,
              "main_sha": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
              "bin_branch": git("branch", "--show-current", directory=REPO / "Bin"),
              "submodules": submodules,
              "release_cache": {line.split("=", 1)[0]: line.split("=", 1)[1] for line in cache.splitlines()
                                if line.startswith(("CMAKE_BUILD_TYPE:", "CMAKE_CXX_FLAGS_RELEASE:", "NMSDK_CLASSIC_RUNTIME_DIR:"))},
              "processes": processes, "tooling_sha256": scripts}
    (run / "integrity-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["passed", "errors", "archive_files_checked", "verbatim_configs_checked"]}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    raise SystemExit(main(report_path(parser.parse_args().run.resolve())))
