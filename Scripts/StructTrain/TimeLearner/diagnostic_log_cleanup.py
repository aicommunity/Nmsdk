"""Compact superseded tick-debug logs before explicitly authorized removal.

This is deliberately NOT a lossless log archive. Repeated EolGateAudit messages
retain their payload and first/last original lines, count and byte interval;
intermediate wall-clock timestamps are discarded. Every other line is retained
verbatim. Scientific observations, model files and arbitrary logs are ineligible.
"""
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess


def _unused(path):
    result = subprocess.run(["fuser", "-s", str(path)], capture_output=True)
    if result.returncode != 1:
        raise RuntimeError("log is open or ownership check failed: "+str(path))


def _identity(path):
    s = path.stat()
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns


def compact_tick_log(source, destination, *, delete_original=False, maximum_archive_bytes=64*1024**2):
    source, destination = Path(source), Path(destination)
    if (source.is_symlink() or source.parent.name != "EventsLog" or
            not source.name.startswith("NeuroModeler.") or ".log.INFO." not in source.name or
            not stat.S_ISREG(source.stat().st_mode)):
        raise ValueError("only native informational diagnostic logs are eligible")
    if source.resolve() == destination.resolve() or destination.exists():
        raise ValueError("archive must be new and separate")
    _unused(source)
    identity = _identity(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name+".partial")
    digest = hashlib.sha256();line_count = groups = collapsed = offset = 0
    pending = None
    def raw(line):
        return base64.b64encode(line).decode("ascii")
    with temporary.open("xb") as disk, gzip.GzipFile(fileobj=disk, mode="wb", mtime=0) as archive:
        def emit(record):
            archive.write((json.dumps(record, separators=(",", ":"))+"\n").encode("utf-8"))
            if disk.tell() > maximum_archive_bytes:
                raise RuntimeError("diagnostic summary budget exceeded; original retained")
        emit({"kind": "superseded_tick_log_summary", "schema_version": 1,
              "source": str(source), "source_bytes": identity[2], "lossless_original_log": False,
              "policy": "EolGateAudit_equal_payload_first_last_count; all_other_lines_verbatim"})
        with source.open("rb") as stream:
            for line in stream:
                digest.update(line);line_count += 1
                # Only this known verbose tick diagnostic may lose intermediate
                # wall-clock headers. Other messages are never deduplicated.
                prefix, separator, payload = line.partition(b"] ")
                eligible = (line.startswith(b"I") and separator and b"EolGateAudit " in payload)
                if eligible and pending is not None and pending["payload"] == payload:
                    pending["count"] += 1;pending["last"] = raw(line)
                    pending["end_byte"] = offset+len(line);collapsed += 1
                else:
                    if pending is not None:
                        pending.pop("payload");emit(pending);groups += 1
                    pending = ({"kind": "repeat", "payload": payload, "first": raw(line), "last": raw(line),
                                "count": 1, "begin_byte": offset, "end_byte": offset+len(line)} if eligible else None)
                    if not eligible:
                        emit({"kind": "raw", "line": raw(line), "begin_byte": offset, "end_byte": offset+len(line)})
                offset += len(line)
        if pending is not None:
            pending.pop("payload");emit(pending);groups += 1
        if _identity(source) != identity:
            raise RuntimeError("source changed during compaction; original retained")
        footer = {"kind": "complete", "source_sha256": digest.hexdigest(), "source_bytes": offset,
                  "source_lines": line_count, "repeat_groups": groups, "collapsed_tick_lines": collapsed}
        emit(footer)
    # Independent bounded-memory structural readback before deleting anything.
    restored_lines = next_byte = repeats = 0
    with gzip.open(temporary, "rt", encoding="utf-8") as check:
        header = json.loads(next(check))
        if header["source_bytes"] != identity[2]:raise RuntimeError("summary header changed")
        last = None
        for text in check:
            record = json.loads(text);last = record
            if record["kind"] == "complete":continue
            if record["begin_byte"] != next_byte or record["end_byte"] <= next_byte:
                raise RuntimeError("summary byte interval gap")
            if record["kind"] == "raw":
                data = base64.b64decode(record["line"], validate=True)
                if len(data) != record["end_byte"]-next_byte:raise RuntimeError("raw line size changed")
                restored_lines += 1
            elif record["kind"] == "repeat":
                first = base64.b64decode(record["first"], validate=True)
                final = base64.b64decode(record["last"], validate=True)
                if record["count"] < 1 or first.partition(b"] ")[2] != final.partition(b"] ")[2]:
                    raise RuntimeError("repeat endpoints changed")
                restored_lines += record["count"];repeats += 1
            else:raise RuntimeError("unknown diagnostic summary record")
            next_byte = record["end_byte"]
        if last != footer or restored_lines != line_count or next_byte != identity[2] or repeats != groups:
            raise RuntimeError("incomplete diagnostic summary")
    if not collapsed:
        # No information was reduced: retain the original and discard only
        # this invocation's completed scratch copy, after checking it again.
        _unused(source)
        if _identity(source) != identity:
            raise RuntimeError("source changed before scratch cleanup; original retained")
        temporary.unlink()
        raise RuntimeError("no redundant tick messages; original retained")
    os.replace(temporary, destination)
    _unused(source)
    if _identity(source) != identity:
        raise RuntimeError("source changed before removal; original retained")
    result = {**footer, "source": str(source), "summary": str(destination),
              "summary_bytes": destination.stat().st_size,
              "summary_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
              "original_removed": False, "lossless_original_log": False}
    # Flush verified summary and its receipt before the authorized unlink.
    with destination.open("rb") as file:os.fsync(file.fileno())
    receipt = destination.with_name(destination.name+".json")
    receipt.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    with receipt.open("rb") as file:os.fsync(file.fileno())
    directory = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:os.fsync(directory)
    finally:os.close(directory)
    if delete_original:
        source.unlink();result["original_removed"] = True
        receipt.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    return result
