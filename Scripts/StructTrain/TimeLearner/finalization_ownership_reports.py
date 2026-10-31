"""Temporal responses of managed transactions, with explicit saved-Train lineage."""
from pathlib import Path
import gzip
import hashlib
import json

from .finalization_ownership_evidence import audit_managed_finalization
from .learned_evidence import load_case
from .native_evidence import load, require
from .plotting import plotting_runtime
from .posttune_transaction_reports import render_posttune_transaction_data


def render_managed_finalization(source: Path, original_solo: Path, output: Path):
    plotting_runtime()
    record, original = load(source), load_case(original_solo)
    audit = audit_managed_finalization(record, original)
    solo = record["boundary"]["source_solo"]
    output = Path(output)
    require(not output.resolve().is_relative_to(source.parent.resolve()) and
            not output.resolve().is_relative_to(original_solo.parent.resolve()),
            "managed_report_must_be_outside_primary_directory")
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary"
    primary.mkdir()

    def write(path, value):
        raw = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n").encode("utf-8")
        path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)

    write(primary/"managed-record.json.gz", record)
    # Preserve both sources as values; do not replace the original learned file
    # just to make the historical source loader accept a replay export.
    write(primary/"original-source.json.gz", original[0])
    write(primary/"replayed-source.json.gz", solo)
    result = render_posttune_transaction_data(record["transaction"], (solo, *original[1:]), output/"posttune")
    manifest = {"kind": "native_managed_finalization_visual_report", "schema_version": 1,
                "source_record_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "source_record_filename": source.name, "source_original_file_sha256": hashlib.sha256(original_solo.read_bytes()).hexdigest(),
                "original_training_source_sha256": original[0]["sha256"], "replayed_source_sha256": solo["sha256"],
                "original_training_calculate_mode": original[0]["calculate_mode"], "replay_calculate_mode": record["calculate_mode"],
                "original_trace_files": [{"trial_id": trial, "filename": path.name,
                                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                                         for trial, path in sorted(original[3].items())],
                "audit": audit, "transaction_report": result,
                "trial_soma_pairs": result["trial_soma_pairs"], "visual_acceptance_complete": False,
                "configured_phase_dispatch_implemented": False, "scientific_verdict": None}
    write(output/"manifest.json", manifest)
    (output/"index.html").write_text('<!doctype html><meta charset="utf-8"><title>Managed finalization</title>'
        '<h1>Managed finalization: actual soma and input responses</h1>'
        '<p>Saved Train source and post-import CalculateMode are recorded separately. Original training '
        'summary, packets and CSVs were audited without overwriting them. All declared target/foil patterns '
        'and native soma channels are shown for weight measurement and fresh final-model responses. '
        'Weights selected is not successful training or recognition; configured phase dispatch is not implemented.</p>'
        '<p><a href="posttune/index.html">All temporal plots and measured responses</a></p>', encoding="utf-8")
    write(output/"SHA256SUMS.json", {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(output.rglob("*")) if p.is_file()})
    return manifest
