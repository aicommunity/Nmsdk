"""Explicit adapters for legacy numeric traces; no inferred trial or training PASS."""
import hashlib
import math
from pathlib import Path, PurePosixPath
import re

from .native_evidence import load, require


def read_trace(path, *, layout, width, expected_sha256):
    require(layout in ("time-values", "index-time-values"), "unknown_statistic_trace_layout")
    require(type(width) is int and width > 0, "invalid_statistic_trace_width")
    require(type(expected_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", expected_sha256),
            "invalid_statistic_trace_digest")
    path = Path(path)
    before = path.stat()
    times, values, digest = [], [], hashlib.sha256()
    indexed = layout == "index-time-values"
    with path.open("rb") as stream:
        for index, raw in enumerate(stream):
            digest.update(raw)
            fields = raw.decode("utf-8-sig" if index == 0 else "utf-8").split()
            require(len(fields) == width + 1 + indexed, "statistic_trace_width_mismatch")
            if indexed:
                require(re.fullmatch(r"0|[1-9][0-9]*", fields[0]) is not None
                        and int(fields[0]) == index, "statistic_trace_index_mismatch")
                fields = fields[1:]
            require(all(re.fullmatch(r"[+-]?(?:[0-9]+(?:[.,][0-9]*)?|[.,][0-9]+)(?:[eE][+-]?[0-9]+)?", token)
                        is not None for token in fields), "invalid_statistic_trace_number")
            row = [float(token.replace(",", ".")) for token in fields]
            require(all(math.isfinite(v) for v in row), "nonfinite_statistic_trace")
            require(row[0] >= 0 and (not times or row[0] > times[-1]),
                    "statistic_trace_clock_not_increasing")
            times.append(row[0]); values.append(row[1:])
    after = path.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
            "statistic_trace_changed_during_read")
    require(digest.hexdigest() == expected_sha256, "statistic_trace_hash_mismatch")
    require(bool(times), "empty_statistic_trace")
    return times, values


def analyze_inputs(source):
    source = Path(source).resolve(strict=True)
    spec = load(source)
    require(type(spec) is dict and set(spec) == {"kind", "schema_version", "traces"}
            and spec["kind"] == "timelearner_legacy_statistic_inputs"
            and type(spec["schema_version"]) is int and spec["schema_version"] == 1
            and type(spec["traces"]) is list and bool(spec["traces"]),
            "unknown_statistic_inputs_schema")
    ids, paths, traces = set(), set(), []
    for record in spec["traces"]:
        require(type(record) is dict and set(record) == {"id", "path", "layout", "width", "sha256"},
                "unknown_statistic_trace_binding")
        identity, name = record["id"], record["path"]
        require(type(identity) is str and bool(identity.strip()) and identity not in ids,
                "duplicate_or_invalid_statistic_trace_id")
        require(type(name) is str and bool(name) and "\\" not in name and ":" not in name
                and not PurePosixPath(name).is_absolute()
                and all(p not in ("", ".", "..") for p in name.split("/")),
                "invalid_statistic_trace_path")
        path = (source.parent/name).resolve(strict=True)
        require(path.is_relative_to(source.parent) and path not in paths, "statistic_trace_path_alias_or_escape")
        times, rows = read_trace(path, layout=record["layout"], width=record["width"],
                                 expected_sha256=record["sha256"])
        ids.add(identity); paths.add(path)
        channels = [{"minimum": min(column), "maximum": max(column), "last": column[-1]}
                    for column in zip(*rows)]
        traces.append({**record, "rows": len(times), "first_time": times[0], "last_time": times[-1],
                       "channels": channels})
    return {"kind": "timelearner_legacy_statistic_summary", "schema_version": 1,
            "validity": "unknown", "numeric_files_verified": True, "traces": traces,
            "complete_observation_windows_verified": False, "training_certificate": None,
            "classification_verified": False, "evaluation_verdict": None}
