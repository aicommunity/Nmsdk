"""Paired native import waveforms, with honest transport-only scope."""
import csv
import hashlib
import html
import json
from pathlib import Path

from .native_evidence import require
from .plotting import padded_limits, plotting_runtime, render_soma
from .recognition_evidence import audit_recognition_state, load_case


def render_transport(package_path, output):
    case = load_case(package_path)
    package, source, spec, observation, trace = case
    audit = audit_recognition_state(*case)
    runtime = plotting_runtime()
    with trace.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream))
    channels = spec["channels"]
    samples = [{"time": float(row[0]), "stimulus": float(row[1]),
                "soma": [float(row[3+2*i]) for i in range(channels)]} for row in rows[1:]]
    root, output = package_path.parent.resolve(strict=True), Path(output).resolve()
    require(not output.is_relative_to(root), "transport_report_must_be_outside_immutable_primary_directory")
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary"; primary.mkdir()
    stem = package_path.name.removesuffix("_recognition_state.json")
    # Keep all referenced solo-proof packets/CSVs and the exact converted package.
    for path in sorted(root.glob(stem+"_*")):
        require(path.is_file() and not path.is_symlink(), "invalid_transport_primary_file")
        (primary/path.name).write_bytes(path.read_bytes())
    chart = {"samples": samples, "frequency_hz": source[0]["configuration"]["model"]["frequency_hz"],
             "begin": spec["begin"], "end": spec["end"], "closed_at": observation["last_sample_time"],
             "complete": True, "valid": True, "sample_id": "pattern "+spec["pattern_hash"][:12], "trial_id": spec["trial_id"],
             "label": "transport A = B",
             "reset_policy": "native import Init/Reset",
             "model_before": package["model_revision"], "spike_times": []}
    figures, links = [], []
    for channel in range(channels):
        folder = output/f"soma-{channel+1:03d}"; folder.mkdir()
        descriptor = f"$.Soma{channel+1}.SumPotential"
        views = render_soma(chart, channel, descriptor, padded_limits([s["soma"][channel] for s in samples]), folder)
        for view in views:
            view["files"] = [folder.name+"/"+name for name in view["files"]]
            png, svg, pdf = view["files"]
            links.append(f'<p>{html.escape(descriptor)} · {html.escape(view["view"])}: '
                         f'<a href="{svg}">SVG</a> · <a href="{pdf}">PDF</a></p><img src="{png}" alt="actual soma and input samples">')
        figures.append({"channel": channel, "descriptor": descriptor, "views": views})
    manifest = {"kind": "native_recognition_transport_visual_report", "schema_version": 1,
                "status": "diagnostic", "audit": audit, "runtime": runtime, "figures": figures,
                "model_revision": package["model_revision"], "pattern_hash": spec["pattern_hash"], "trial_id": spec["trial_id"],
                "soma_channels": channels, "recorded_native_ticks": len(samples),
                "paired_model_waveform_values_exact": True, "plotted_model": "a",
                "spikes": "not_recorded", "units": "model_units_SI_unverified",
                "visual_acceptance_complete": False, "scientific_verdict": None}
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>Native import transport: soma and input</title><style>body{font:18px sans-serif;margin:2em}'
        'img{width:100%;max-width:1920px}</style><h1>Native import transport</h1>'
        '<p>Actual model A waveform; independent audit verifies every model B waveform value is identical. '
        'All recorded soma samples and generator impulses are preserved. Overview and 100-tick tiles; '
        'no spikes or SI units are inferred. This single-pattern transport control does not establish '
        'calibration, selectivity, complete PostTune search or convergence.</p>'+"".join(links), encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()}
    (output/"SHA256SUMS.json").write_text(json.dumps(sums, indent=2)+"\n", encoding="utf-8")
    return {"kind": manifest["kind"], "status": "diagnostic", "patterns": 1,
            "soma_channels": channels, "files": len(sums), "scientific_verdict": None}
