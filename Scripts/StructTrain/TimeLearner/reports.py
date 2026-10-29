"""Portable primary-data reports for native recognition evaluation schema 1.

This adapter labels SumPotential in model units: schema 1 has no SI descriptor.
The report records that limitation instead of inventing mV or calibration.
"""
from pathlib import Path
import gzip
import hashlib
import html
import json
import platform

from .native_evidence import load, require
from .recognition_metrics import load_evaluation, score_recognition_evaluation
from .plotting import render_soma


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def render_evaluation(source: Path, model: Path, output: Path):
    spec, observations = load_evaluation(source)
    package = load(model)
    analysis = score_recognition_evaluation(spec, observations, package)
    # Descriptors: native binding enumerates Soma1..N (Branch has one soma).
    count = 1 if package["source_solo"]["configuration"]["model"]["branch"] else len(package["recognition_inputs"])
    nodes = {node["path"]: node for node in package["neuron"]["graph"]["identity"]["model"]["nodes"]}
    descriptors = []
    for i in range(count):
        path = f"$.Soma{i+1}"
        require(path in nodes, "missing_native_soma_descriptor")
        descriptors.append({"index": i, "path": path+".SumPotential", "class": nodes[path]["class"],
                            "units": "model_units_SI_unverified", "adapter": "native_recognition_schema_1"})
    require(all(o["samples"] and all(len(s["soma"]) == count for s in o["samples"]) for o in observations),
            "missing_report_soma_samples")
    limits = []
    for i in range(count):
        values = [s["soma"][i] for o in observations for s in o["samples"]]
        lo, hi = min(values), max(values)
        padding = (hi-lo)*.08 if hi > lo else max(abs(lo)*.08, 1e-12)
        limits.append((lo-padding, hi+padding))
    # Never overwrite an existing report, source data or completed job directory.
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary";primary.mkdir()
    _write(primary/"model.json", package)
    copied_spec = dict(spec);copied_spec["trials"] = []
    by_id = {o["trial_id"]: o for o in observations}
    figures, links = [], []
    for trial in sorted(spec["trials"], key=lambda t: t["presentation_index"]):
        o = by_id[trial["trial_id"]]
        index = trial["presentation_index"]
        name = f"trial-{index:04d}.json.gz"
        encoded = (json.dumps(o, ensure_ascii=False, allow_nan=False)+"\n").encode("utf-8")
        (primary/name).write_bytes(gzip.compress(encoded, mtime=0))
        copied_spec["trials"].append({**trial, "observation": name})
        for descriptor in descriptors:
            folder = output/f'trial-{index:04d}-soma-{descriptor["index"]+1:03d}'
            folder.mkdir()
            views = render_soma(o, descriptor["index"], descriptor["path"], limits[descriptor["index"]], folder)
            for view in views:
                view["files"] = [f"{folder.name}/{p}" for p in view["files"]]
            figures.append({"trial_id": o["trial_id"], "sample_id": o["sample_id"], "label": o["label"],
                            "presentation_index": index, "descriptor": descriptor, "views": views})
            links.append(f'<h2>{html.escape(o["sample_id"])} / {html.escape(o["trial_id"])} / '
                         f'{html.escape(descriptor["path"])}</h2>')
            for view in views:
                png, svg, pdf = view["files"]
                links.append(f'<p>{view["view"]}: <a href="{svg}">SVG</a> · <a href="{pdf}">PDF</a> · '
                             f'<a href="{png}">full PNG</a></p><img src="{png}" alt="{view["view"]}">')
    _write(primary/"evaluation.json", copied_spec)
    _write(output/"analysis.json", analysis)
    import matplotlib
    manifest = {"kind": "timelearner_visual_report", "schema_version": 1,
                "run_id": spec["run_id"], "model_revision": spec["model_revision"],
                "status": "diagnostic", "observation_validity": analysis["validity"],
                "expected_trial_soma_pairs": len(spec["trials"])*count, "figures": figures,
                "runtime": {"python": platform.python_version(), "matplotlib": matplotlib.__version__},
                "limitations": ["SI units not recorded in observation schema 1", "continuous panorama not implemented",
                                "automatic weak-response detail scaling not implemented", "visual acceptance pending"],
                "visual_acceptance_complete": False, "evaluation_verdict": None}
    _write(output/"manifest.json", manifest)
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>TimeLearner visual diagnostic report</title><style>body{font:18px sans-serif;margin:2em}'
        'img{display:block;width:100%;max-width:1920px}p{max-width:90em}</style>'
        '<h1>TimeLearner visual diagnostic report</h1><p>Actual soma SumPotential and shared input samples. '
        'Full primary data: <a href="primary/evaluation.json">evaluation</a>, '
        '<a href="primary/model.json">model</a>. <a href="analysis.json">Metrics</a>. '
        'SI units unverified; diagnostic report, visual acceptance pending. '
        'Click full PNG/SVG/PDF for readable scale. Purple dotted markers: actual LT spike events.</p>'
        +"\n".join(links)+'</html>\n', encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()}
    _write(output/"SHA256SUMS.json", sums)
    return {"kind": manifest["kind"], "status": manifest["status"],
            "trial_soma_pairs": len(figures), "files": len(sums), "evaluation_verdict": None}
