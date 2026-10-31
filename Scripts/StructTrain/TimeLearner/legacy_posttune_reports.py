"""Physical legacy calibration traces; never manufacture V2 trial/certificate data."""
import hashlib
import html
import json
from pathlib import Path

from .legacy_posttune_evidence import read_free_run
from .plotting import padded_limits, plotting_runtime, render_soma


def render_free_run(packet_path, trace_path, output):
    runtime = plotting_runtime()
    packet,samples,audit = read_free_run(packet_path, trace_path)
    output = Path(output);output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary";primary.mkdir()
    (primary/"run.json").write_bytes(Path(packet_path).read_bytes())
    (primary/"trace.csv").write_bytes(Path(trace_path).read_bytes())
    chart = {"samples": samples, "frequency_hz": packet["frequency_hz"], "begin": samples[0]["time"],
             "end": samples[-1]["time"], "closed_at": samples[-1]["time"],
             "complete": True, "valid": True, "sample_id": "target then foil",
             "trial_id": Path(packet_path).stem, "label": "legacy recorded trace",
             "reset_policy": "native inference playback; no inferred settling",
             "model_before": "not-recorded", "spike_times": []}
    figures,links = [],[]
    for channel in range(packet["soma_channels"]):
        folder = output/f"soma-{channel+1:03d}";folder.mkdir()
        limits = padded_limits([q["soma"][channel] for q in samples])
        views = render_soma(chart, channel, f"$.Soma{channel+1}.SumPotential", limits, folder)
        for view in views:view["files"] = [folder.name+"/"+name for name in view["files"]]
        figures.append({"channel": channel, "descriptor": f"$.Soma{channel+1}.SumPotential", "views": views})
        links.append(f"<h2>Soma {channel+1}</h2>")
        for view in views:
            png,svg,pdf = view["files"]
            links.append(f'<p>{html.escape(view["view"])}: <a href="{svg}">SVG</a> · <a href="{pdf}">PDF</a></p>'
                         f'<img src="{png}" alt="actual soma and input samples">')
    manifest = {"kind": "legacy_posttune_physical_visual_report", "schema_version": 1,
                "status": "diagnostic", "audit": audit, "runtime": runtime, "figures": figures,
                "declared_patterns": packet["pattern_isi"], "sample_labels": packet["sample_labels"],
                "soma_channels": packet["soma_channels"], "recorded_native_ticks": len(samples),
                "model_identity": "not_recorded_by_legacy_producer", "spikes": "not_recorded",
                "units": "model_units_SI_unverified", "physical_settling_verified": False,
                "visual_acceptance_complete": False, "scientific_verdict": None}
    (output/"manifest.json").write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>Legacy inference soma/input traces</title><style>body{font:18px sans-serif;margin:2em}'
        'img{width:100%;max-width:1920px}</style><h1>Actual legacy inference playback</h1>'
        '<p>All recorded native soma and input samples, target then foil. Complete/valid on the figure means '
        'the recorded trace passed the primary-data audit, not a V2 calibration certificate or verified physical settling. '
        'No model identity, spike timestamps or SI units were recorded by this producer; these are not inferred. '
        'The native simulator terminates playback. Full-interval overview and 100-tick zoom tiles preserve all samples.</p>'
        '<p><a href="primary/run.json">Source metadata</a> · <a href="primary/trace.csv">Source CSV</a></p>'
        +"".join(links),encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()}
    (output/"SHA256SUMS.json").write_text(json.dumps(sums,indent=2)+"\n",encoding="utf-8")
    return {"kind": manifest["kind"], "status": "diagnostic", "patterns": 2,
            "soma_channels": packet["soma_channels"], "files": len(sums), "scientific_verdict": None}
