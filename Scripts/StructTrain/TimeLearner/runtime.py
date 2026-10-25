"""Immutable runtime provenance; paths identify files, hashes identify contents."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

BUILD_KEYS = {"CMAKE_BUILD_TYPE", "CMAKE_C_COMPILER", "CMAKE_CXX_COMPILER",
              "CMAKE_CXX_COMPILER_ID", "CMAKE_CXX_COMPILER_VERSION", "CMAKE_CXX_FLAGS",
              "CMAKE_CXX_FLAGS_RELEASE", "CMAKE_CXX_FLAGS_DEBUG", "CMAKE_CXX_STANDARD",
              "QT_VERSION_MAJOR", "BUILD_SHARED_LIBS", "RDK_LLM_BUILD_EMBEDDED",
              "NO_MOTION_CONTROL", "NMSDK_DEPLOY_ROOT", "NMSDK_RESOURCE_ROOT"}


def digest_file(path: Path) -> str:
    before = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    after = path.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise RuntimeError(f"file changed during provenance capture: {path}")
    return digest.hexdigest()


def digest_json(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def file_record(path: Path) -> dict:
    path = path.resolve(strict=True)
    return {"path": str(path), "sha256": digest_file(path), "size": path.stat().st_size}


def parse_ldd(output: str) -> list[Path]:
    paths = set()
    for line in output.splitlines():
        line = line.strip()
        if "=> not found" in line:
            raise RuntimeError(f"unresolved runtime dependency: {line}")
        candidate = line.split("=>", 1)[-1].strip().split(" (", 1)[0].strip()
        if candidate.startswith("/"):
            paths.add(Path(candidate))
    return sorted(paths)


def resolved_libraries(executable: Path) -> list[dict]:
    result = subprocess.run(["ldd", str(executable)], capture_output=True, text=True, timeout=30)
    output = result.stdout + result.stderr
    if result.returncode != 0 and not any(s in output for s in ("not a dynamic executable", "statically linked")):
        raise RuntimeError(f"ldd failed: {output.strip()}")
    return [file_record(path) for path in parse_ldd(output)]


def loaded_process_files(pid: int, executable: Path, proc_root: Path = Path("/proc")) -> list[dict]:
    """Capture executable mappings only after checking the expected owned process."""
    process = proc_root / str(pid)
    if (process / "exe").resolve(strict=True) != executable.resolve(strict=True):
        raise RuntimeError("PID executable does not match the declared runtime")
    paths = set()
    for line in (process / "maps").read_text(encoding="utf-8").splitlines():
        fields = line.split(None, 5)
        if len(fields) < 6 or "x" not in fields[1] or not fields[5].startswith("/"):
            continue
        if fields[5].endswith(" (deleted)"):
            raise RuntimeError("a mapped runtime file was deleted")
        path = Path(fields[5])
        if path.stat().st_ino != int(fields[4]):
            raise RuntimeError(f"mapped runtime file was replaced: {path}")
        paths.add(path)
    if not paths:
        raise RuntimeError("no executable mappings found")
    return [file_record(path) for path in sorted(paths)]


def source_closure(root: Path) -> dict:
    def git(directory: Path, *args: str) -> str:
        return subprocess.check_output(["git", "-C", str(directory), *args]).decode("utf-8").strip()
    closure = {"root": {"head": git(root, "rev-parse", "HEAD"),
                        "status": git(root, "status", "--porcelain", "--untracked-files=no")}}
    records = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-r", "-z", "HEAD"])
    for record in records.split(b"\0"):
        if not record:
            continue
        metadata, path_raw = record.split(b"\t", 1)
        mode, _, recorded = metadata.decode().split()
        if mode != "160000":
            continue
        path = path_raw.decode("utf-8")
        closure[path] = {"recorded_gitlink": recorded,
                         "head": git(root / path, "rev-parse", "HEAD"),
                         "status": git(root / path, "status", "--porcelain", "--untracked-files=no")}
    for name, state in closure.items():
        if state["status"] or ("recorded_gitlink" in state and state["recorded_gitlink"] != state["head"]):
            raise RuntimeError(f"source closure is not immutable: {name}")
    return closure


def build_flags(cache: Path) -> dict[str, str]:
    result = {}
    for line in cache.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith(("#", "//")) or "=" not in line or ":" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.split(":", 1)[0]
        if key in BUILD_KEYS:
            result[key] = value
    return result


def snapshot(root: Path, executable: Path, app_ini: Path, cache: Path, pid: int | None = None) -> dict:
    executable = executable.resolve(strict=True)
    manifest = {"schema_version": 1, "source_closure": source_closure(root),
                "executable": file_record(executable), "app_ini": file_record(app_ini),
                "build_flags": build_flags(cache), "resolved_libraries": resolved_libraries(executable),
                "loader_environment": {k: os.environ[k] for k in ("LD_LIBRARY_PATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM") if k in os.environ}}
    compiler = Path(manifest["build_flags"]["CMAKE_CXX_COMPILER"])
    manifest["compiler"] = file_record(compiler)
    manifest["compiler"]["version"] = subprocess.check_output([str(compiler), "--version"], text=True, timeout=15).strip()
    # Resolved dependencies are not claimed to include plugins loaded later.
    manifest["loaded_process_files"] = loaded_process_files(pid, executable) if pid is not None else None
    manifest["runtime_fingerprint"] = digest_json({
        "executable": manifest["executable"]["sha256"],
        "app_ini": manifest["app_ini"]["sha256"],
        "resolved_libraries": sorted(r["sha256"] for r in manifest["resolved_libraries"]),
        "build_flags": manifest["build_flags"],
        "compiler": manifest["compiler"]["sha256"],
        "loaded_process_files": (sorted(r["sha256"] for r in manifest["loaded_process_files"])
                                 if manifest["loaded_process_files"] is not None else None),
    })
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--app-ini", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--pid", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = snapshot(args.root.resolve(), args.executable, args.app_ini, args.cache, args.pid)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
