"""Replay pinned historical completed packages through the real fresh-process importer.

No retraining, threshold selection, package migration, or scientific verdict.
Each case uses a fresh owned native process and the archived absolute clock.
"""
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from .native_evidence import EvidenceError, audit_probe, load, number, parse_json_bytes, require
from .native_gate import _environment, run_native_gate
from .process_runner import verify_runtime


FIELDS = {"kind", "schema_version", "archive_repository", "archive_snapshot_commit",
          "origin_evidence_commit", "runtime_manifest", "source_root", "maximum_wall_seconds",
          "asan_options", "cases"}


def _write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _archived(repo, revision, entry):
    require(type(entry) is dict and set(entry) == {"path", "stored_sha256", "raw_sha256"},
            "unknown_legacy_replay_archive_entry")
    name = entry["path"]
    require(type(name) is str and name.endswith(".gz") and "\\" not in name and ":" not in name
            and not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts,
            "invalid_legacy_replay_archive_path")
    try:
        from .history import read_bytes
        raw = read_bytes(repo, revision, name, maximum_bytes=128*1024**2)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise EvidenceError("legacy_replay_git_read_failed:"+name) from error
    require(_digest(raw) == entry["stored_sha256"], "legacy_replay_stored_hash_mismatch:"+name)
    decoded = gzip.decompress(raw)
    require(len(decoded) <= 128*1024**2 and _digest(decoded) == entry["raw_sha256"],
            "legacy_replay_raw_hash_mismatch:"+name)
    return decoded


def run_legacy_completed_replay(specification, output):
    specification = Path(specification).resolve(strict=True)
    spec = load(specification)
    require(type(spec) is dict and set(spec) == FIELDS and
            spec["kind"] == "timelearner_legacy_completed_replay" and
            type(spec["schema_version"]) is int and spec["schema_version"] == 1,
            "unknown_legacy_completed_replay")
    for key in ("archive_snapshot_commit", "origin_evidence_commit"):
        require(type(spec[key]) is str and re.fullmatch("[0-9a-f]{40}", spec[key]),
                "invalid_legacy_replay_revision:"+key)
    wall = number(spec["maximum_wall_seconds"])
    require(wall > 0 and type(spec["asan_options"]) is str and "\x00" not in spec["asan_options"],
            "invalid_legacy_replay_execution_policy")

    def resolve(key):
        value = spec[key]
        require(type(value) is str and bool(value), "invalid_legacy_replay_path:"+key)
        path = Path(value)
        return (path if path.is_absolute() else specification.parent/path).resolve(strict=True)

    repository, source, runtime_path = (resolve(k) for k in
                                        ("archive_repository", "source_root", "runtime_manifest"))
    executable = verify_runtime(load(runtime_path))
    output = Path(output).resolve()
    require(not output.exists() and all(not output.is_relative_to(p) and not p.is_relative_to(output)
            for p in (source, repository, executable.parent)), "legacy_replay_output_overlaps_inputs")
    cases = spec["cases"]
    require(type(cases) is list and bool(cases), "missing_legacy_replay_cases")
    prepared, identities = [], set()
    for row in cases:
        require(type(row) is dict and set(row) == {"id", "package", "expected_trace", "expected_probe"}
                and type(row["id"]) is str and re.fullmatch("[A-Za-z][A-Za-z0-9_]*", row["id"])
                and row["id"] not in identities, "invalid_legacy_replay_case")
        identities.add(row["id"])
        package_bytes, trace_bytes, probe_bytes = (_archived(repository, spec["archive_snapshot_commit"], row[k])
                                                  for k in ("package", "expected_trace", "expected_probe"))
        package, probe = parse_json_bytes(package_bytes), parse_json_bytes(probe_bytes)
        require(package["kind"] == "timelearner_completed_state" and package["schema_version"] == 1
                and package["state_kind"] == "learned_solo" and package["training_outcome"] == "search_unresolved"
                and package["certificate"]["exact"] is False, "legacy_replay_requires_saved_nonexact_completed_state")
        observation = probe["observation"]
        require(observation["valid"] is True and observation["complete"] is True,
                "legacy_replay_expected_probe_is_not_complete")
        begin = number(observation["specification"]["begin"])
        start_us = round(begin*1e6)
        require(begin >= 0 and 0 <= start_us <= 2**53-1 and abs(start_us/1e6-begin) <=
                32*2.220446049250313e-16*max(1., abs(begin)), "legacy_replay_clock_not_native_microseconds")
        prepared.append((row, package, package_bytes, trace_bytes, probe_bytes, start_us))

    # All declarations, stored/raw hashes, package kinds and clock values are
    # checked before output creation or any native process can start.
    output.mkdir(parents=True, exist_ok=False)
    _write(output/"specification.json", spec)
    results = []
    for row, package, package_bytes, trace_bytes, probe_bytes, start_us in prepared:
        case = output/row["id"]
        case.mkdir()
        (case/"input-state.json").write_bytes(package_bytes)
        (case/"expected.csv").write_bytes(trace_bytes)
        (case/"expected-probe.json").write_bytes(probe_bytes)
        gate_spec = {"kind": "timelearner_native_test_gate", "schema_version": 1,
                     "runtime_manifest": str(runtime_path), "source_root": str(source),
                     "expected_test_ids": ["NativeLearnedState/FreshProcessImport"],
                     "maximum_wall_seconds": wall, "asan_options": spec["asan_options"]}
        _write(case/"gate-specification.json", gate_spec)
        environment = {"TIMELEARNER_LEARNED_IMPORT": str(case/"input-state.json"),
                       "TIMELEARNER_LEARNED_OUTPUT": str(case/"actual.json"),
                       "TIMELEARNER_LEARNED_START_US": str(start_us)}
        _write(case/"fixture-environment.json", environment)
        result = {"case_id": row["id"], "execution": "not_started", "validity": "invalid",
                  "reason": "not_assessed", "gate": None, "scientific_verdict": None}
        try:
            with _environment(environment):
                gate = run_native_gate(case/"gate-specification.json", case/"gate")
            result.update(execution=gate["execution"], gate=gate)
            require(gate["validity"] == "valid" and gate["assertion_status"] == "passed",
                    "legacy_replay_native_import_not_passed")
            actual = load(case/"actual.json")
            require(actual["model"]["sha256"] == package["model_revision"], "legacy_replay_model_revision_changed")
            require(actual["certificate"] == package["certificate"] and actual["need"] is False,
                    "legacy_replay_certificate_or_frozen_control_changed")
            audit = audit_probe(actual["probe"], case/"actual.json.csv")
            require(audit["valid_observation"] is True, "legacy_replay_actual_probe_invalid")
            actual_trace = (case/"actual.json.csv").read_bytes()
            require(actual_trace == trace_bytes, "legacy_replay_waveform_bytes_changed")
            result.update(validity="valid", reason="saved_completed_certificate_and_frozen_waveform_preserved",
                          model_revision=package["model_revision"], source_training_outcome="search_unresolved",
                          source_certificate_exact=False, certificate_preserved=True, waveform_bytes_equal=True,
                          expected_trace_sha256=_digest(trace_bytes), actual_trace_sha256=_digest(actual_trace),
                          actual_probe_audit=audit)
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            result["reason"] = str(error)
        _write(case/"result.json", result)
        results.append(result)
    result = {"kind": "timelearner_legacy_completed_replay_result", "schema_version": 1,
              "assertion_status": "passed" if all(r["validity"] == "valid" for r in results) else "failed",
              "cases": results, "origin_evidence_commit": spec["origin_evidence_commit"],
              "archive_snapshot_commit": spec["archive_snapshot_commit"], "scientific_verdict": None}
    _write(output/"result.json", result)
    return result
