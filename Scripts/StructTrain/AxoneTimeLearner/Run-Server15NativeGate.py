"""Run the declared axon subset through the existing owned Windows native gate."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import traceback


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root: Path) -> dict:
    records = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink() and not path.is_junction(), "runtime_reparse_point")
        if path.is_file():
            stat = path.stat()
            records[path.relative_to(root).as_posix()] = {"size": stat.st_size, "sha256": sha(path)}
    return records


def compiler_record(cache: Path, file_record) -> tuple[dict, dict]:
    fields = {}
    for line in cache.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"(CMAKE_CACHE_(?:MAJOR|MINOR|PATCH)_VERSION):[^=]+=(.*)", line)
        if match:
            fields[match[1]] = match[2]
    require(len(fields) == 3, "cmake_cache_version_missing")
    version = ".".join(fields["CMAKE_CACHE_" + key + "_VERSION"] for key in ("MAJOR", "MINOR", "PATCH"))
    info = cache.parent / "CMakeFiles" / version / "CMakeCXXCompiler.cmake"
    matches = re.findall(r'^set\(CMAKE_CXX_COMPILER "([^"]+)"\)$',
                         info.read_text(encoding="utf-8"), re.MULTILINE)
    require(len(matches) == 1, "cmake_resolved_compiler_ambiguous")
    compiler = Path(matches[0]).resolve(strict=True)
    require(compiler.is_absolute() and compiler.is_file(), "cmake_resolved_compiler_missing")
    return file_record(compiler), file_record(info)


def declared_tests(recipe: dict, cpp: str, partition: str) -> list[str]:
    if recipe.get("kind") in ("axone_event_assignment_contract", "axone_factory_diagnostic_contract", "axone_local_timing_rule_contract", "axone_regeneration_comparison_contract"):
        require(recipe.get("schema_version") == 1 and partition == "all", "invalid_observation_contract")
        tests = recipe["expected_test_ids"]
        count = {"axone_event_assignment_contract": 10, "axone_factory_diagnostic_contract": 9,
                 "axone_local_timing_rule_contract": 11, "axone_regeneration_comparison_contract": 54}[recipe["kind"]]
        require(len(tests) == count and len(set(tests)) == count, "observation_inventory_changed")
        return tests
    require(recipe.get("kind") == "axone_native_contract_inputs" and recipe.get("schema_version") == 1,
            "unsupported_axon_native_contract")
    groups = {
        "lifecycle": ["AxoneLifecycle." + name for name in recipe["lifecycle_cases"]] +
            ["AxoneTreeTopology." + name for name in re.findall(r"TEST\(AxoneTreeTopology,\s*(\w+)\)", cpp)],
        "linear": [case["gtest_filter"] for case in recipe["cases"] if not case["id"].startswith("tree_equivalence_")],
        "tree": [case["gtest_filter"] for case in recipe["cases"] if case["id"].startswith("tree_equivalence_")],
    }
    require([len(groups[name]) for name in ("lifecycle", "linear", "tree")] == [17,45,6],
            "axon_native_contract_inventory_changed")
    selected = sum((groups[name] for name in ("lifecycle", "linear", "tree")), []) if partition == "all" else groups[partition]
    require(len(selected) == len(set(selected)), "duplicate_axon_test_identity")
    return selected


def verify_volume(data: Path, marker: dict) -> None:
    serial, maximum, flags = wintypes.DWORD(), wintypes.DWORD(), wintypes.DWORD()
    filesystem = ctypes.create_unicode_buffer(64)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    query = kernel.GetVolumeInformationW
    query.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD,
                      ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
                      ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD]
    query.restype = wintypes.BOOL
    require(data.anchor.upper() == "E:\\", "server15_e_data_drive_required")
    if not query(data.anchor, None, 0, ctypes.byref(serial), ctypes.byref(maximum),
                 ctypes.byref(flags), filesystem, len(filesystem)):
        raise ctypes.WinError(ctypes.get_last_error())
    require(filesystem.value == "NTFS" and f"{serial.value:08X}" == marker["volume_serial"],
            "axon_data_volume_identity_changed")


def run(args) -> dict:
    require(os.name == "nt" and socket.gethostname().upper() == "AQUA3060", "server15_windows_required")
    data = args.data_root.resolve(strict=True)
    marker = json.loads((data / "archive.root.json").read_bytes())
    require(marker.get("kind") == "nmsdk_axone_timelearner_data_root" and marker.get("schema_version") == 1 and
            marker.get("archive_id") == args.archive_id and marker.get("file_system") == "NTFS" and
            Path(marker["authoritative_root"]).resolve(strict=True) == data and
            marker.get("computer") == "AQUA3060", "axon_data_root_identity_mismatch")
    verify_volume(data, marker)
    source, runtime, cache, protocol = [path.resolve(strict=True) for path in
                                       (args.source_root, args.runtime, args.cache, args.protocol)]
    output = args.output.resolve()
    require(output.is_relative_to(data) and output != data and not output.exists() and
            not output.is_relative_to(source) and not output.is_relative_to(runtime),
            "fresh_external_gate_output_required")
    output.mkdir(parents=True, exist_ok=False)
    producer = Path(__file__).resolve(strict=True)
    producer_before = {"path": str(producer), "sha256": sha(producer), "size": producer.stat().st_size}
    result = {"kind": "axone_server15_native_gate", "schema_version": 1,
              "source_commit": args.expected_root_commit, "partition": args.partition,
              "selected_test_id": args.case_id,
              "archive_id": args.archive_id, "scientific_verdict": None,
              "complete": False, "native_checks_passed": False}
    try:
        require(not any(path.is_symlink() or path.is_junction() for path in
                        (data, source, runtime, output)), "axon_gate_reparse_root")
        def git(*arguments: str) -> str:
            return subprocess.check_output(["git", "-C", str(source), *arguments],
                creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8").strip()
        require(git("rev-parse", "HEAD") == args.expected_root_commit, "unexpected_compiled_source_revision")
        require(not git("status", "--porcelain", "--untracked-files=all"), "dirty_or_untracked_sdk_source")
        sys.path.insert(0, str(source))
        from Scripts.StructTrain.TimeLearner.runtime import (
            source_closure, file_record, build_flags, runtime_content_identity, digest_json)
        from Scripts.StructTrain.TimeLearner.native_gate import run_native_gate
        import Scripts.StructTrain.TimeLearner.windows_process as backend

        protocol_before = file_record(protocol)
        recipe = json.loads(protocol.read_bytes())
        if recipe.get("kind") in ("axone_event_assignment_contract", "axone_factory_diagnostic_contract", "axone_local_timing_rule_contract", "axone_regeneration_comparison_contract"):
            for record in recipe["source_records"]:
                declared = (source / record["workspace_path"]).resolve(strict=True)
                require(declared.is_relative_to(source), "declared_source_outside_sdk")
                payload = declared.read_bytes().replace(b"\r\n", b"\n")
                require(len(payload) == record["canonical_lf_bytes"] and
                        hashlib.sha256(payload).hexdigest() == record["canonical_lf_sha256"],
                        "declared_event_assignment_source_changed")
            cpp_text = ""
        else:
            cpp_path = (source / recipe["test_source"]["path"]).resolve(strict=True)
            require(cpp_path.is_relative_to(source) and cpp_path.is_file() and
                    cpp_path.stat().st_size == recipe["test_source"]["bytes"] and
                    sha(cpp_path) == recipe["test_source"]["sha256"], "declared_native_test_source_changed")
            cpp_text = cpp_path.read_text(encoding="utf-8")
        expected = declared_tests(recipe, cpp_text, args.partition)
        if args.case_id is not None:
            require(args.case_id in expected, "selected_case_not_in_declared_partition")
            expected = [args.case_id]
        closure = source_closure(source)
        before = inventory(runtime)
        require(before and "Test_PulseLib_StorageComponents.exe" in before and
                "NeuroModelerConsole.ini" in before, "native_runtime_incomplete")
        compiler, compiler_info = compiler_record(cache, file_record)
        backend_record = file_record(Path(backend.__file__))
        flags = build_flags(cache)
        flags.update({"role": "axon_engineering_native_gate",
                      "windows_backend_sha256": backend_record["sha256"],
                      "resolved_compiler_info_sha256": compiler_info["sha256"],
                      "axon_supervisor_sha256": producer_before["sha256"]})
        manifest = {
            "schema_version": 2, "windows_source_root": str(source), "source_closure": closure,
            "executable": file_record(runtime / "Test_PulseLib_StorageComponents.exe"),
            "app_ini": file_record(runtime / "NeuroModelerConsole.ini"), "compiler": compiler,
            "build_flags": flags,
            "resolved_libraries": [file_record(runtime / relative) for relative in before
                                   if relative.lower().endswith(".dll")],
            "loaded_process_files": None, "windows_backend": backend_record,
            "loader_environment": {name: os.environ.get(name) for name in
                                   ("PATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM")},
        }
        manifest["runtime_identity"] = runtime_content_identity(manifest)
        manifest["runtime_fingerprint"] = digest_json(manifest["runtime_identity"])
        write_new(output / "runtime.json", manifest)
        write_new(output / "runtime-files-before.json", before)
        write_new(output / "producer.json", producer_before)
        write_new(output / "resolved-compiler.json", {"compiler": compiler, "cmake_info": compiler_info,
                  "cache": file_record(cache)})
        write_new(output / "source-protocol.json", recipe)
        write_new(output / "source-protocol-record.json", protocol_before)
        specification = {
            "kind": "timelearner_native_test_gate", "schema_version": 7,
            "runtime_manifest": str(output / "runtime.json"), "source_root": str(source),
            "expected_test_ids": expected, "maximum_wall_seconds": args.wall_seconds,
            "asan_options": "", "cooperative_runtime_capture": True,
            "process_limits": {"memory_bytes": args.memory_bytes, "maximum_processes": 8},
            "worker_lock": str(data / "Locks" / "native-worker.lock"), "artifact_directories": {},
        }
        write_new(output / "gate-specification.json", specification)
        gate = run_native_gate(output / "gate-specification.json", output / "native-gate")
        after = inventory(runtime)
        write_new(output / "runtime-files-after.json", after)
        require(after == before and source_closure(source) == closure, "native_runtime_or_source_changed")
        require(sha(producer) == producer_before["sha256"], "native_gate_producer_changed")
        require(file_record(protocol) == protocol_before, "protocol_changed")
        require(not git("status", "--porcelain", "--untracked-files=all"), "native_gate_changed_sdk_files")
        result.update(complete=True, expected_cases=len(expected), gate=gate,
                      runtime_fingerprint=manifest["runtime_fingerprint"],
                      native_checks_passed=gate.get("validity") == "valid" and gate.get("assertion_status") == "passed")
    except BaseException as error:
        result.update(error=str(error), traceback=traceback.format_exc())
    finally:
        write_new(output / "result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-root", "runtime", "cache", "protocol", "data-root", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--archive-id", required=True)
    parser.add_argument("--expected-root-commit", required=True)
    parser.add_argument("--partition", choices=("lifecycle", "linear", "tree", "all"), default="all")
    parser.add_argument("--case-id", help="One exact test identity already present in the declared partition.")
    parser.add_argument("--wall-seconds", type=int, default=1800)
    parser.add_argument("--memory-bytes", type=int, default=2 * 1024**3)
    args = parser.parse_args()
    require(re.fullmatch("[0-9a-f]{40}", args.expected_root_commit) is not None, "invalid_expected_source_commit")
    require(1 <= args.wall_seconds <= 86400 and 32*1024**2 <= args.memory_bytes <= 64*1024**3,
            "invalid_native_gate_resource_limits")
    result = run(args)
    print(json.dumps({key: result.get(key) for key in
                      ("complete", "native_checks_passed", "expected_cases", "error")}, ensure_ascii=False))
    return 0 if result["native_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
