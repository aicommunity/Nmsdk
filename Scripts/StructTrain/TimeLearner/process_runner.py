"""Linux owned-process execution; pidfds prevent PID reuse during cancellation.

Execution/provenance results do not imply valid training or recognition.
This supervisor owns the launched executable, not arbitrary process names.
"""
from pathlib import Path
import json
import math
import os
import signal
import subprocess
import time

from .native_evidence import require
from .runtime import digest_file, digest_json, loaded_process_files, runtime_content_identity


def verify_runtime(manifest):
    require(type(manifest) is dict and manifest.get("schema_version") == 2, "unsupported_runtime_manifest")
    identity = runtime_content_identity(manifest)
    require(manifest["runtime_identity"] == identity and manifest["runtime_fingerprint"] == digest_json(identity),
            "runtime_fingerprint_mismatch")
    records = [manifest["executable"], manifest["app_ini"], manifest["compiler"], *manifest["resolved_libraries"]]
    if manifest["loaded_process_files"] is not None:
        records.extend(manifest["loaded_process_files"])
    for record in records:
        path = Path(record["path"]).resolve(strict=True)
        require(path.is_file() and path.stat().st_size == record["size"] and digest_file(path) == record["sha256"],
                "runtime_content_changed:"+str(path))
    return Path(manifest["executable"]["path"]).resolve(strict=True)


def _start_identity(pid):
    # comm can contain spaces and ')'; numeric fields follow its final ')'.
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return fields[19]  # field 22, with field 3 at index zero


def _write(path, value):
    temporary = path.with_name(path.name+".pending")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n");stream.flush();os.fsync(stream.fileno())
    os.replace(temporary, path)


def inspect_attempt(directory):
    directory = Path(directory).resolve(strict=True)
    if (directory/"result.json").exists():
        return json.loads((directory/"result.json").read_text())
    if not (directory/"owned-process.json").exists():
        return {"execution": "unknown", "reason": "no_committed_process_identity", "scientific_verdict": None}
    owned = json.loads((directory/"owned-process.json").read_text())
    try:
        if owned["boot_id"] != Path("/proc/sys/kernel/random/boot_id").read_text().strip():
            return {"execution": "unknown", "reason": "worker_boot_changed", "scientific_verdict": None}
        same = (_start_identity(owned["pid"]) == owned["start_ticks"] and
                Path(f'/proc/{owned["pid"]}/exe').resolve(strict=True) == Path(owned["executable"]))
    except (FileNotFoundError, ProcessLookupError):
        same = False
    return {"execution": "running" if same else "unknown", "reason": "identity_live" if same else "owned_process_missing",
            "owned_process": owned, "scientific_verdict": None}


def execute(manifest, arguments, working_directory, output, maximum_wall_seconds, cancel_file=None, terminate_grace_seconds=2.):
    require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"), "linux_pidfd_support_required")
    require(type(arguments) is list and all(type(a) is str and "\0" not in a for a in arguments), "invalid_process_arguments")
    require(type(maximum_wall_seconds) in (int, float) and math.isfinite(maximum_wall_seconds)
            and maximum_wall_seconds > 0, "invalid_wall_budget")
    require(type(terminate_grace_seconds) in (int, float) and math.isfinite(terminate_grace_seconds)
            and terminate_grace_seconds >= 0, "invalid_termination_grace")
    executable = verify_runtime(manifest)
    cwd = Path(working_directory).resolve(strict=True)
    require(cwd.is_dir(), "invalid_process_working_directory")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    cancel = Path(cancel_file).resolve() if cancel_file is not None else output/"cancel.request"
    require(not cancel.exists(), "cancellation_request_already_exists")
    _write(output/"runtime.json", manifest)
    _write(output/"request.json", {"arguments": arguments, "working_directory": str(cwd),
           "maximum_wall_seconds": maximum_wall_seconds, "cancel_file": str(cancel),
           "terminate_grace_seconds": terminate_grace_seconds, "model_time": None})
    begin = time.monotonic()
    process, pidfd = None, None
    outcome, reason, mappings, mapping_error = "process_error", "launch_not_completed", None, None
    try:
        with (output/"stdout.log").open("xb") as stdout, (output/"stderr.log").open("xb") as stderr:
            # Environment must match the captured loader inputs.
            for key in ("LD_LIBRARY_PATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM"):
                require(os.environ.get(key) == manifest["loader_environment"].get(key), "loader_environment_changed:"+key)
            process = subprocess.Popen([str(executable), *arguments], cwd=cwd, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=True)
            pidfd = os.pidfd_open(process.pid)
            try:
                owned = {"pid": process.pid, "start_ticks": _start_identity(process.pid),
                         "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                         "executable": str(executable), "executable_sha256": manifest["executable"]["sha256"],
                         "runtime_fingerprint": manifest["runtime_fingerprint"]}
                _write(output/"owned-process.json", owned)
                mappings = loaded_process_files(process.pid, executable)
                _write(output/"loaded-files.json", mappings)
            except (FileNotFoundError, ProcessLookupError, RuntimeError) as error:
                mapping_error = str(error)  # a fast exit is not evidence of loaded-file closure
            while process.poll() is None:
                if cancel.exists():
                    outcome, reason = "interrupted", "cancellation_request"
                    break
                if time.monotonic()-begin >= maximum_wall_seconds:
                    outcome, reason = "timeout", "wall_budget_exhausted"
                    break
                time.sleep(.02)
            else:
                outcome, reason = ("completed", "exit_zero") if process.returncode == 0 else ("process_error", "nonzero_exit")
            if process.poll() is None:
                try:
                    signal.pidfd_send_signal(pidfd, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=terminate_grace_seconds)
                except subprocess.TimeoutExpired:
                    try:
                        signal.pidfd_send_signal(pidfd, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait()
        verify_runtime(manifest)
        provenance = "loaded_files_captured" if mappings is not None else "incomplete_loaded_files"
    except Exception as error:
        outcome, reason, provenance = "process_error", str(error), "invalid_or_incomplete_runtime"
    finally:
        if process is not None and process.poll() is None:
            # Popen still owns an unreaped child; direct kill is safe even if pidfd_open failed.
            process.kill();process.wait()
        if pidfd is not None:
            os.close(pidfd)
    result = {"kind": "timelearner_process_result", "schema_version": 1, "execution": outcome, "reason": reason,
              "returncode": process.returncode if process is not None else None,
              "wall_seconds": time.monotonic()-begin, "model_time": None, "runtime_provenance": provenance,
              "mapping_error": mapping_error, "runtime_fingerprint": manifest["runtime_fingerprint"],
              "ownership_scope": "launched_executable_only", "scientific_verdict": None}
    _write(output/"result.json", result)
    return result
