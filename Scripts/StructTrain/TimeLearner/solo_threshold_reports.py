"""Actual Solo burst soma/LTZ plots; no invented foil or recognition verdict."""
from pathlib import Path
import gzip
import hashlib
import html
import json

from .native_evidence import load, require
from .plotting import padded_limits, plotting_runtime, render_soma
from .solo_threshold_evidence import audit_solo_threshold_trace


def render_solo_threshold_trace(source: Path, output: Path):
    source, output = Path(source), Path(output)
    report = load(source)
    audit = audit_solo_threshold_trace(report)
    samples = report["samples"]
    require(bool(samples), "no_solo_threshold_samples_to_render")
    require(not output.resolve().is_relative_to(source.parent.resolve()),
            "solo_threshold_report_must_be_outside_primary_directory")
    runtime = plotting_runtime()
    output.mkdir(parents=True, exist_ok=False)

    def write(path, value):
        raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+"\n").encode()
        path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)

    write(output/"source.json.gz", report)
    q = report["requested_specification"]
    frequency = report["source"]["frequency_hz"]
    # Interrupted records do not promise an absolute planned window. Show only
    # the recorded segment, with one tick of display room for a lone sample.
    begin, last = samples[0]["time"], samples[-1]["time"]
    end = last if last > begin else begin+1/frequency
    observation = {"begin": begin, "end": end, "closed_at": last,
                   "frequency_hz": frequency, "complete": audit["complete"],
                   "valid": audit["valid"], "sample_id": q["sample_id"],
                   "trial_id": q["trial_id"], "label": "Solo training-burst diagnostic",
                   "reset_policy": "native_probe_physical_reset",
                   "model_before": report["source"]["effective_model_revision"],
                   "spike_times": report["spike_times"], "sample_markers": len(samples) <= 2,
                   "samples": [{"time": f["time"], "stimulus": f["stimulus"], "soma": f["soma"]}
                               for f in samples]}
    figures = []
    for channel in range(len(samples[0]["soma"])):
        folder = output/f"soma-{channel:03d}"
        folder.mkdir()
        views = render_soma(observation, channel, f"Native Soma[{channel}] SumPotential",
                            padded_limits([f["soma"][channel] for f in samples]), folder)
        figures.append({"source": "soma", "channel": channel, "directory": folder.name, "views": views})
    lt_observation = {**observation, "samples": [{"time": f["time"], "stimulus": f["stimulus"],
                                                  "soma": [f["lt_potential"]]} for f in samples]}
    folder = output/"ltzone"
    folder.mkdir()
    views = render_soma(lt_observation, 0, "Native LTZone.Potential",
                        padded_limits([f["lt_potential"] for f in samples]), folder,
                        potential_axis_label="LTZone.Potential [model units; SI unverified]")
    figures.append({"source": "lt_potential", "channel": None, "directory": folder.name, "views": views})
    manifest = {"kind": "native_solo_threshold_visual_report", "schema_version": 1,
                "source_file_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "source_model_revision": report["source"]["effective_model_revision"],
                "trace_sha256": report["sha256"], "audit": audit, "runtime": runtime,
                "clock_scope": "complete_probe" if audit["complete"] else "recorded_segment_only",
                "display_begin": begin, "display_end": end, "last_sample": last,
                "samples": len(samples), "soma_channels": len(samples[0]["soma"]), "figures": figures,
                "termination_reason": report["termination_reason"],
                "threshold_observed": report["source"]["threshold"], "calibrated": False,
                "visual_acceptance_complete": False, "evaluation_verdict": None}
    write(output/"manifest.json", manifest)
    sections = []
    for figure in figures:
        sections.append("<h2>"+html.escape(figure["directory"])+"</h2>")
        for view in figure["views"]:
            for name in view["files"]:
                path = figure["directory"]+"/"+name
                sections.append(f'<a href="{path}">{html.escape(name)}</a> ')
            sections.append("<br>")
    (output/"index.html").write_text('<!doctype html><meta charset="utf-8">'
        '<title>Solo native burst diagnostic</title><style>body{font:18px sans-serif;margin:2em}</style>'
        '<h1>Solo native burst: every soma channel and LTZone with actual input</h1>'
        '<p>Only the recorded training pattern is shown; this is not an all-pattern recognition test. '
        'No foil response is invented. Interrupted traces show the recorded segment only. '
        'Spiking extrema are not nonspiking references. Model units: SI unverified. '
        'Complete primary source: <a href="source.json.gz">source.json.gz</a>. '
        'Overview plus native-tick zooms, no downsampling. Click PNG/SVG/PDF for full scale. '
        'Visual acceptance pending; no calibration or scientific verdict.</p>'
        +"\n".join(sections), encoding="utf-8")
    write(output/"SHA256SUMS.json", {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in sorted(output.rglob("*")) if p.is_file()})
    return manifest
