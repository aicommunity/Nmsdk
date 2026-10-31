"""Actual cold Train, native finalization and frozen replay temporal reports."""
from pathlib import Path
import gzip
import hashlib
import html
import json
import re
import shutil

from .calibration_transaction_reports import _spec
from .learned_evidence import load_case
from .live_finalization_evidence import audit_completed_live_finalization, audit_pre_entry_live_finalization
from .native_evidence import EvidenceError, load, require
from .plotting import plotting_runtime
from .posttune_transaction_reports import render_posttune_transaction_data
from .probe_reports import render_probe_set
from .recognition_metrics import score_recognition_evaluation
from .reports import render_evaluation
from .stopped_evidence import load_case as load_stopped_case


def _write(path, value):
    raw = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n").encode("utf-8")
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)


def _read_live_report_source(source: Path, inventory: Path):
    """The published inventory declares the primary set; the directory does not."""
    source, inventory = Path(source), Path(inventory)
    declared = load(inventory)
    require(declared["kind"] in {"native_live_primary_composition", "native_live_primary_inventory"} and
            type(declared["schema_version"]) is int and declared["schema_version"] == 1,
            "unknown_live_report_primary_inventory")
    rows = declared["files"]
    require(type(rows) is list and all(type(row) is dict and type(row["path"]) is str and
            "/" not in row["path"] and "\\" not in row["path"] and row["path"] not in {"", ".", ".."} and
            type(row["bytes"]) is int and row["bytes"] >= 0 and type(row["sha256"]) is str and
            re.fullmatch("[0-9a-f]{64}", row["sha256"]) for row in rows), "invalid_live_report_primary_inventory")
    by_name = {row["path"]: row for row in rows}
    require(len(by_name) == len(rows), "duplicate_live_report_inventory_entry")

    def artifact(name):
        require(name in by_name, "live_report_undeclared_primary:" + name)
        path = source.parent/name
        require(path.is_file() and not path.is_symlink(), "live_report_primary_missing:" + name)
        raw = path.read_bytes();row = by_name[name]
        require(len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"],
                "live_report_primary_changed:" + name)
        return path

    record = load(artifact(source.name))
    require(type(record.get("scenario")) is int and record["scenario"] in range(8), "unknown_live_report_scenario")
    scenario = record["scenario"]
    identity = re.fullmatch(r"(Classic|Branch)_live_finalization_([01])_(local|connected)_([0-7])\.json", source.name)
    require(identity is not None and record["calculate_mode"] == int(identity[2]) and
            record["connected"] is (identity[3] == "connected") and scenario == int(identity[4]),
            "live_report_filename_condition_mismatch")
    if scenario in (6, 7):
        require(not any(name.startswith(source.stem+"_state_trial_") or name.startswith(source.stem+"_stopped_trial_")
                        for name in by_name), "live_preflight_report_has_probes")
        return record, None, [], [by_name[source.name]]
    suffix = "stopped" if scenario == 2 else "learned"
    package = artifact(source.stem+"_"+suffix+"_state.json")
    summary = artifact(source.stem+"_"+suffix+"_summary.json")
    trial_prefix = source.stem+("_stopped_trial_" if scenario == 2 else "_state_trial_")
    packets = sorted(name for name in by_name if name.startswith(trial_prefix) and name.endswith(".json"))
    require(bool(packets) and {p.name for p in source.parent.glob(trial_prefix+"*.json")} == set(packets),
            "live_report_primary_trial_set_changed")
    needed = [source.name, package.name, summary.name]
    for name in packets:
        artifact(name);artifact(Path(name).with_suffix(".csv").name)
        needed.extend((name, Path(name).with_suffix(".csv").name))
    case = (load_stopped_case if scenario == 2 else load_case)(package)
    require(case[0]["configuration"]["model"]["branch"] is (identity[1] == "Branch"),
            "live_report_filename_topology_mismatch")
    return record, case, [source.parent/name for name in packets], [by_name[name] for name in needed]


def read_live_report_source(source: Path, inventory: Path):
    try:
        return _read_live_report_source(source, inventory)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError("malformed_live_report_source:" + str(error)) from error


def render_live_finalization(source: Path, inventory: Path, output: Path):
    runtime = plotting_runtime()
    source, inventory, output = Path(source), Path(inventory), Path(output)
    require(not output.resolve().is_relative_to(source.parent.resolve()), "live_report_must_be_outside_primary")
    record, case, packets, primary_rows = read_live_report_source(source, inventory)
    completed = record["scenario"] in (0, 1)
    audit = (audit_completed_live_finalization if completed else audit_pre_entry_live_finalization)(record, case)
    frozen_spec = None
    if completed:
        frozen_spec = _spec(record["frozen_replay"], record["final_package"],
                            record["live"]["plan"]["confirmation"]["criterion"])
        scored = score_recognition_evaluation(frozen_spec, record["frozen_replay"]["observations"], record["final_package"])
        require(scored["validity"] == "valid", "invalid_live_report_frozen_matrix")
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary";primary.mkdir()
    _write(primary/"live-record.json.gz", record)
    links, training, posttune, frozen = [], None, None, None
    if packets:
        inputs = primary/"training";inputs.mkdir();trials = []
        for path in packets:
            trace = path.with_suffix(".csv")
            shutil.copyfile(path, inputs/path.name);shutil.copyfile(trace, inputs/trace.name)
            trials.append({"trial_id": load(path)["requested_specification"]["trial_id"],
                           "packet": path.name, "trace": trace.name})
        _write(inputs/"report-spec.json", {"kind": "timelearner_probe_report_spec", "schema_version": 2,
                                          "observation_policy": "complete_or_partial", "trials": trials})
        training = render_probe_set(inputs/"report-spec.json", output/"training")
        links.append('<li><a href="training/index.html">Every recorded Train probe and soma; partial windows explicit</a></li>')
    if completed:
        posttune = render_posttune_transaction_data(record["live"]["post_tune"], case, output/"posttune")
        inputs = primary/"frozen";inputs.mkdir()
        _write(inputs/"model.json", record["final_package"])
        by_id = {row["trial_id"]: row for row in record["frozen_replay"]["observations"]}
        for q in frozen_spec["trials"]:
            _write(inputs/q["observation"], by_id[q["trial_id"]])
        _write(inputs/"evaluation.json", frozen_spec)
        frozen = render_evaluation(inputs/"evaluation.json", inputs/"model.json", output/"frozen")
        links.extend(('<li><a href="posttune/index.html">All complete PostTune and calibration matrices</a></li>',
                      '<li><a href="frozen/index.html">All declared frozen-replay patterns and somas</a></li>'))
    manifest = {"kind": "native_live_finalization_visual_report", "schema_version": 1,
                "source_control_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "source_control_filename": source.name,
                "source_inventory_sha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
                "source_primary_files": primary_rows, "audit": audit, "scenario": record["scenario"],
                "live_status": record["live"]["status"], "training_report": training,
                "posttune_report": posttune, "frozen_replay_report": frozen,
                "training_trial_soma_pairs": training["trial_soma_pairs"] if training else 0,
                "recognition_trial_soma_pairs": (posttune["trial_soma_pairs"]+frozen["trial_soma_pairs"]) if completed else 0,
                "recognition_presented": completed, "source_training_outcome": case[0]["training_outcome"] if case else None,
                "runtime": runtime, "native_execution_verified": False, "independent_test": False,
                "visual_acceptance_complete": False, "scientific_verdict": None}
    _write(output/"manifest.json", manifest)
    (output/"index.html").write_text('<!doctype html><meta charset="utf-8"><title>Live Train finalization</title>'
        '<style>body{font:18px sans-serif;margin:2em}</style><h1>Live Train to finalization: actual responses</h1><p>'+
        html.escape(source.name)+'; '+html.escape(record["live"]["status"])+'.</p>'
        '<p>Raw membrane potentials and actual shared inputs; every declared pattern and soma in complete matrices. '
        'Original samples, overview and readable zooms; no downsampling. Train, weight measurement and frozen replay '
        'are distinct phases. Partial or absent observations are never plotted as complete recognition.</p>'
        '<p>Frozen replay uses the declared same matrix; it is not independent Test. Silent target is a false negative. '
        'No classification PASS or training convergence is inferred.</p><ul>'+''.join(links)+'</ul>'+
        ('' if completed else '<p>No recognition model or pattern responses were produced for this rejected/stopped entry.</p>'),
        encoding="utf-8")
    _write(output/"SHA256SUMS.json", {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in sorted(output.rglob("*")) if p.is_file()})
    return manifest
