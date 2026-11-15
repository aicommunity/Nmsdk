"""Readable actual fresh-process soma/input traces; full renders are a cache."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path

from .native_evidence import count, load, require
from .plotting import padded_limits, plotting_runtime, render_soma
from .recognition_owner_evidence import load_case
from .recognition_owner_replay import audit_case_replay


def render_replays(source, replay, output):
    source, replay, output = Path(source).resolve(strict=True), Path(replay).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and all(not output.is_relative_to(p) and not p.is_relative_to(output)
            for p in (source, replay)), "owner_replay_report_overlaps_primaries")
    index = load(replay/"index.json")
    cases = []
    for row in index["cases"]:
        package = source/row["source_filename"]
        audit = audit_case_replay(package, replay)
        cases.append((row, load_case(package), audit))
    require(bool(cases), "owner_replay_report_cases_missing")
    runtime = plotting_runtime()
    output.mkdir(parents=True, exist_ok=False)
    records, links = [], []
    for row, case, audit in cases:
        package, solo, spec, paired, _, _, _ = case
        actual = load(replay/row["id"]/"actual.json")
        trace = replay/row["id"]/"actual.json.csv"
        with trace.open(newline="", encoding="utf-8") as stream:
            raw = list(csv.reader(stream))
        channels = count(spec["channels"])
        samples = [{"time": float(r[0]), "stimulus": float(r[1]),
                    "soma": [float(r[2+i]) for i in range(channels)]} for r in raw[1:]]
        chart = {"samples": samples, "frequency_hz": solo[0]["configuration"]["model"]["frequency_hz"],
            "begin": spec["begin"], "end": spec["end"], "closed_at": actual["last_sample_time"],
            "complete": True, "valid": True, "sample_id": row["id"], "trial_id": spec["trial_id"],
            "label": "actual fresh-process transport", "reset_policy": "native Init/Reset in a fresh process",
            "model_before": package["model_revision"], "spike_times": []}
        folder = output/row["id"]
        folder.mkdir()
        figures = []
        for channel in range(channels):
            target = folder/f"soma-{channel+1:03d}"
            target.mkdir()
            descriptor = f"$.Soma{channel+1}.SumPotential"
            views = render_soma(chart, channel, descriptor,
                padded_limits([s["soma"][channel] for s in samples]), target)
            for view in views:
                view["files"] = [row["id"]+"/"+target.name+"/"+name for name in view["files"]]
                png, svg, pdf = view["files"]
                links.append(f'<h3>{html.escape(row["id"])} · {html.escape(descriptor)} · '
                    f'{html.escape(view["view"])}</h3><a href="{svg}">SVG</a> · <a href="{pdf}">PDF</a>'
                    f'<p><img src="{png}" alt="Actual soma potential overlaid with actual input samples"></p>')
            figures.append({"channel": channel, "descriptor": descriptor, "views": views})
        records.append({"id": row["id"], "source_filename": row["source_filename"],
            "source_file_sha256": row["source_file_sha256"], "actual_trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest(),
            "pattern_hash": spec["pattern_hash"], "trial_id": spec["trial_id"],
            "model_revision": package["model_revision"], "native_ticks": len(samples),
            "soma_channels": channels, "transport_audit": audit, "figures": figures})
    manifest = {"kind": "native_recognition_owner_replay_visual_report", "schema_version": 1,
        "status": "diagnostic", "runtime": runtime, "cases": records,
        "source_archive_sha256": index["source_archive_sha256"],
        "origin_evidence_commit": index["origin_evidence_commit"],
        "patterns_per_case": 1, "spikes": "not_recorded_by_paired_transport",
        "units": "model_units_SI_unverified", "primary_data_copied_into_report": False,
        "visual_acceptance_complete": False, "scientific_verdict": None}
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>Fresh-process model transport</title><style>body{font:18px sans-serif;margin:2em}'
        'img{width:100%;max-width:1920px}</style><h1>Fresh-process model transport</h1>'
        '<p>Actual soma outputs and actual shared input samples. Every declared soma and recorded tick is plotted. '
        'Overview, 100-tick zoom tiles and local amplitude detail are provided. Each case presents its one declared '
        'transport pattern; this is not an eight-pattern selectivity experiment. Original paired and fresh-process '
        'waveforms were independently compared byte for byte. LT spike events were not recorded by this protocol. '
        'No scientific classification verdict is inferred. Full renders are a reproducible cache; original '
        'primaries remain in their referenced Git evidence.</p>'+"".join(links), encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()}
    (output/"SHA256SUMS.json").write_text(json.dumps(sums, indent=2)+"\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("replay", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = render_replays(args.source, args.replay, args.output)
    print(json.dumps({"cases": len(result["cases"]), "scientific_verdict": None}))
