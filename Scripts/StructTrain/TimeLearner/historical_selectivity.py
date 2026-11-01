"""Descriptive August CSV adapter; missing observation evidence stays unknown."""
import csv
import hashlib
import io
import math
from pathlib import Path
import re

from .native_evidence import require


def _finite(text, field):
    try:
        value = float(text)
    except (ValueError, TypeError):
        raise ValueError("invalid_historical_number:" + field)
    require(math.isfinite(value), "nonfinite_historical_number:" + field)
    return value


def analyze_historical_csv(path: Path, expected_trial_ids) -> dict:
    require(type(expected_trial_ids) in (list, tuple, set) and bool(expected_trial_ids),
            "declared_historical_trial_set_required")
    require(all(type(value) is str and value.strip() == value and value for value in expected_trial_ids),
            "invalid_declared_historical_trial_id")
    expected = set(expected_trial_ids)
    require(len(expected) == len(expected_trial_ids), "duplicate_declared_historical_trial_id")
    before = path.stat();raw = path.read_bytes();after = path.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
            "historical_csv_changed_during_read")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), strict=True)
    fields = reader.fieldnames or []
    require(bool(fields) and len(fields) == len(set(fields)), "missing_or_duplicate_historical_header")
    fixed = {"trial", "target_class", "stim_count", "neuron_fired", "neuron_t_rel",
             "match", "ltz_potential_max", "soma_amp_sum"}
    isi_fields = sorted((name for name in fields if re.fullmatch(r"isi\d+", name)), key=lambda name: int(name[3:]))
    amps = sorted((name for name in fields if re.fullmatch(r"soma_amp_\d+", name)), key=lambda name: int(name[9:]))
    require(set(fields) == fixed | set(isi_fields) | set(amps) and bool(amps) and bool(isi_fields),
            "unknown_historical_selectivity_schema")
    require(isi_fields == ["isi"+str(i) for i in range(len(isi_fields))]
            and amps == ["soma_amp_"+str(i) for i in range(len(amps))], "noncontiguous_historical_columns")
    rows = [];seen = set()
    for row in reader:
        require(None not in row and all(value is not None for value in row.values()),
                "malformed_historical_csv_row")
        trial = row["trial"]
        require(trial and trial not in seen, "missing_or_duplicate_historical_trial")
        seen.add(trial)
        require(all(row[key] in {"0", "1"} for key in ("target_class", "neuron_fired", "match")),
                "invalid_historical_boolean")
        require(re.fullmatch(r"[1-9]\d*", row["stim_count"]) is not None, "invalid_historical_stimulus_count")
        count = int(row["stim_count"])
        require(count-1 <= len(isi_fields), "historical_stimulus_dimension_mismatch")
        isis = [_finite(row[key], key) for key in isi_fields[:count-1]]
        require(all(value > 0 for value in isis)
                and all(not row[key].strip() for key in isi_fields[count-1:]), "invalid_historical_isis")
        fired = int(row["neuron_fired"]);target = int(row["target_class"])
        at = _finite(row["neuron_t_rel"], "neuron_t_rel")
        require(at >= 0 if fired else at == -1, "inconsistent_historical_response_time")
        matched = int(fired == target)
        require(int(row["match"]) == matched, "historical_match_disagrees_with_label_and_response")
        rows.append({"trial_id": trial, "label": "target" if target else "foil", "isis": isis,
                     "reported_fired": bool(fired), "reported_response_time": at,
                     "native_match": matched, "ltz_potential_max": _finite(row["ltz_potential_max"], "ltz_potential_max"),
                     "soma_amplitudes": [_finite(row[key], key) for key in amps],
                     "soma_amp_sum": _finite(row["soma_amp_sum"], "soma_amp_sum"),
                     "complete": None, "censored": None, "spike_count": None})
    require(seen == expected, "historical_trial_set_mismatch")
    require(any(r["label"] == "target" for r in rows) and any(r["label"] == "foil" for r in rows),
            "historical_target_and_foils_required")
    counts = {key: 0 for key in ("TP", "FP", "FN", "TN")}
    for row in rows:
        counts[("TP" if row["reported_fired"] else "FN") if row["label"] == "target"
               else ("FP" if row["reported_fired"] else "TN")] += 1
    matched = sum(r["native_match"] for r in rows)
    return {"kind": "historical_selectivity_observations", "schema_version": 1,
            "criterion": "native_in_window_match_history_v1", "source_sha256": hashlib.sha256(raw).hexdigest(),
            "source_bytes": len(raw), "source_file": str(path), "rows": rows, "reported_counts": counts,
            "native_match_count": matched, "trials": len(rows), "historical_accuracy": matched/len(rows),
            "declared_trial_set_observed": True, "complete_observation_windows_verified": False,
            "late_responses": None, "actual_stimulus_timestamps": None, "training_certificate": None,
            "validity": "unknown", "evaluation_verdict": None,
            "limitations": ["Native historical in-window observations; no complete-window or late-spike evidence.",
                            "A detected response does not prove a single-spike morphology.",
                            "Historical accuracy is preserved separately from a strict scientific verdict."]}
