"""Seal a completed server .15 attempt in place and emit a compact archive pointer."""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import socket


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def read(path):
    return json.loads(path.read_bytes())


def write_new(path, document):
    payload = (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def record(path):
    before = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    after = path.stat()
    require((before.st_size, before.st_mtime_ns, before.st_ino) ==
            (after.st_size, after.st_mtime_ns, after.st_ino), "archive_file_changed_while_reading")
    return {"bytes": after.st_size, "sha256": digest.hexdigest()}


def private(path):
    absolute = path.absolute()
    for item in (absolute, *absolute.parents):
        require(not item.is_symlink() and not item.is_junction(), "archive_reparse_path")
    return absolute.resolve(strict=True)


def root_identity(root, archive_id):
    require(os.name == "nt" and socket.gethostname().upper() == "AQUA3060", "server15_required")
    root = private(root)
    marker_path = root/"archive.root.json"
    marker = read(marker_path)
    require(marker.get("kind") == "nmsdk_axone_timelearner_data_root" and marker.get("schema_version") == 1 and
            marker.get("archive_id") == archive_id and marker.get("computer") == "AQUA3060" and
            marker.get("file_system") == "NTFS" and root.anchor.upper() == "E:\\" and
            private(Path(marker["authoritative_root"])) == root, "archive_root_identity_mismatch")
    serial, maximum, flags = wintypes.DWORD(), wintypes.DWORD(), wintypes.DWORD()
    filesystem = ctypes.create_unicode_buffer(64)
    query = ctypes.WinDLL("kernel32", use_last_error=True).GetVolumeInformationW
    query.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                      ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
                      wintypes.LPWSTR, wintypes.DWORD]
    query.restype = wintypes.BOOL
    if not query(root.anchor, None, 0, ctypes.byref(serial), ctypes.byref(maximum),
                 ctypes.byref(flags), filesystem, len(filesystem)):
        raise ctypes.WinError(ctypes.get_last_error())
    require(filesystem.value == "NTFS" and f"{serial.value:08X}" == marker.get("volume_serial"),
            "archive_volume_changed")
    return root, marker, record(marker_path)


def inventory(attempt, maximum_bytes, maximum_files):
    files, total = {}, 0
    for path in sorted(attempt.rglob("*")):
        require(not path.is_symlink() and not path.is_junction(), "attempt_reparse_point")
        if not path.is_file():
            continue
        require(total+path.stat().st_size <= maximum_bytes and len(files) < maximum_files,
                "archive_inventory_budget_exceeded")
        value = record(path)
        total += value["bytes"]
        require(total <= maximum_bytes, "archive_inventory_budget_exceeded")
        files[path.relative_to(attempt).as_posix()] = value
    require(bool(files), "empty_attempt")
    return files, total


def terminal(attempt, role):
    if role == "native":
        document = read(attempt/"result.json")
        require(document.get("kind") == "axone_server15_native_gate" and
                (document.get("complete") is True or bool(document.get("error"))),
                "native_attempt_not_terminal")
        process = attempt/"native-gate/process"
        closure = "not_started"
        process_evidence = {"execution": "not_started", "validity": "not_assessed",
                            "runtime_provenance": "not_started", "cooperative_capture": "not_started"}
        if process.exists():
            owned = read(process/"result.json")
            require(owned.get("kind") == "timelearner_windows_process_result" and
                    owned.get("all_processes_closed") is True, "owned_native_processes_not_closed")
            closure = "bound_windows_job_closed"
            process_evidence = {name: owned.get(name) for name in
                                ("execution", "validity", "runtime_provenance", "cooperative_capture")}
        return {"role": role, "process_closure": closure, "process_evidence": process_evidence,
                "complete": document.get("complete"),
                "validity": document.get("gate", {}).get("validity"),
                "assertion_status": document.get("gate", {}).get("assertion_status"),
                "native_checks_passed": document.get("native_checks_passed"),
                "scientific_verdict": None}
    if role == "analysis":
        document = read(attempt/"result.json")
        require(document.get("kind") in ("axone_factory_diagnostic_analysis", "axone_p1_sparse_baseline_analysis",
                                        "axone_regeneration_diagnostic_analysis",
                                        "axone_calibrated_delay_input_generation",
                                        "axone_conduction_matrix_analysis", "axone_conduction_figures",
                                        "axone_recovery_matrix_analysis") and
                type(document.get("analysis_complete")) is bool, "analysis_not_terminal")
        return {"role": role, "analysis_complete": document["analysis_complete"],
                "process_closure": "not_captured_for_auxiliary_analysis_process",
                "scientific_verdict": None}
    if role == "build":
        document = read(attempt/"build-result.json")
        require(document.get("kind") == "axone_server15_build_result" and
                (document.get("completed") is True or bool(document.get("error"))),
                "build_entrypoint_not_terminal")
        return {"role": role, "entrypoint_completed": document["completed"],
                "configure_exit": document.get("configure_exit"), "build_exit": document.get("build_exit"),
                "deployment_exit": document.get("deployment_exit"),
                "process_closure": "not_captured_by_native_job_backend", "scientific_verdict": None}
    document = read(attempt/"initialization.json")
    require(document.get("completed") is True or bool(document.get("error")), "setup_entrypoint_not_terminal")
    return {"role": role, "entrypoint_completed": document["completed"],
            "process_closure": "not_captured_by_native_job_backend", "scientific_verdict": None}


def seal(args):
    root, marker, marker_record = root_identity(args.data_root, args.archive_id)
    attempt = private(args.attempt)
    require(attempt.is_dir() and attempt.is_relative_to(root) and attempt != root and
            attempt.relative_to(root).parts[0] in ("Setup", "Builds", "NativeChecks", "Experiments"),
            "unsupported_external_attempt_scope")
    destination = root/"Seals"/args.seal_id
    require(not destination.exists(), "archive_seal_already_exists")
    status = terminal(attempt, args.role)
    files, total = inventory(attempt, args.maximum_bytes, args.maximum_files)
    destination.mkdir(parents=True, exist_ok=False)
    producer = Path(__file__).resolve(strict=True)
    manifest = {"kind": "axone_server15_attempt_manifest", "schema_version": 1,
                "archive_id": args.archive_id, "volume_serial": marker["volume_serial"],
                "attempt_relative": attempt.relative_to(root).as_posix(), "status": status,
                "files": files, "file_count": len(files), "total_bytes": total,
                "producer": {"path": str(producer), **record(producer)},
                "marker": marker_record, "created_utc": datetime.now(timezone.utc).isoformat()}
    write_new(destination/"manifest.json", manifest)
    second, second_total = inventory(attempt, args.maximum_bytes, args.maximum_files)
    require(second == files and second_total == total and terminal(attempt, args.role) == status,
            "attempt_changed_before_seal")
    root_after, marker_after, marker_record_after = root_identity(args.data_root, args.archive_id)
    require(root_after == root and marker_after == marker and marker_record_after == marker_record,
            "archive_root_changed_before_seal")
    pointer = {"kind": "axone_server15_archive_pointer", "schema_version": 1,
               "archive_id": args.archive_id, "computer": marker["computer"],
               "authoritative_root": str(root), "volume_serial": marker["volume_serial"],
               "attempt_relative": manifest["attempt_relative"],
               "manifest_relative": (destination/"manifest.json").relative_to(root).as_posix(),
               "manifest": record(destination/"manifest.json"), "file_count": len(files), "total_bytes": total,
               "integrity": "two_equal_full_inventories", "status": status, "scientific_verdict": None}
    write_new(destination/"pointer.archive.json", pointer)
    print(json.dumps({"pointer": str(destination/"pointer.archive.json"),
                      "file_count": len(files), "total_bytes": total, "status": status}, ensure_ascii=False))


def verify(args):
    root, marker, marker_record = root_identity(args.data_root, args.archive_id)
    pointer = read(private(args.verify_pointer))
    require(pointer.get("kind") == "axone_server15_archive_pointer" and pointer.get("schema_version") == 1 and
            pointer.get("archive_id") == args.archive_id and pointer.get("volume_serial") == marker["volume_serial"] and
            Path(pointer["authoritative_root"]).resolve(strict=True) == root, "archive_pointer_identity_mismatch")
    def member(relative):
        value = Path(relative)
        require(not value.is_absolute() and not value.drive and not value.root and ".." not in value.parts, "archive_member_escape")
        result = private(root/value)
        require(result.is_relative_to(root) and result != root, "archive_member_escape")
        return result
    manifest_path = member(pointer["manifest_relative"])
    require(record(manifest_path) == pointer["manifest"], "archive_manifest_hash_mismatch")
    manifest = read(manifest_path)
    require(manifest.get("kind") == "axone_server15_attempt_manifest" and manifest.get("schema_version") == 1 and
            manifest.get("archive_id") == args.archive_id and manifest.get("marker") == marker_record and
            manifest.get("attempt_relative") == pointer["attempt_relative"], "archive_manifest_identity_mismatch")
    attempt = member(pointer["attempt_relative"])
    actual, total = inventory(attempt, args.maximum_bytes, args.maximum_files)
    require(actual == manifest["files"] and len(actual) == manifest["file_count"] == pointer["file_count"] and
            total == manifest["total_bytes"] == pointer["total_bytes"] and
            terminal(attempt, pointer["status"]["role"]) == manifest["status"] == pointer["status"],
            "archive_attempt_changed")
    print(json.dumps({"verified": True, "file_count": len(actual), "total_bytes": total,
                      "scientific_verdict": None}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--attempt", type=Path)
    parser.add_argument("--verify-pointer", type=Path)
    parser.add_argument("--archive-id", required=True)
    parser.add_argument("--seal-id")
    parser.add_argument("--role", choices=("setup", "build", "native", "analysis"))
    parser.add_argument("--maximum-bytes", type=int, default=4*1024**3)
    parser.add_argument("--maximum-files", type=int, default=20000)
    args = parser.parse_args()
    require(args.maximum_bytes > 0 and args.maximum_files > 0, "invalid_archive_seal_limits")
    if args.verify_pointer is not None:
        require(args.attempt is None and args.role is None and args.seal_id is None, "mixed_archive_operations")
        verify(args)
    else:
        require(args.attempt is not None and args.role is not None and args.seal_id is not None and
                re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", args.seal_id), "incomplete_archive_seal_request")
        seal(args)


if __name__ == "__main__":
    main()
