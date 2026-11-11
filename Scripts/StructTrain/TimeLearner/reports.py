"""Portable primary-data reports for native recognition evaluation schema 1.

This adapter labels SumPotential in model units: schema 1 has no SI descriptor.
The report records that limitation instead of inventing mV or calibration.
"""
from pathlib import Path
import gzip
import hashlib
import html
import json

from .native_evidence import load, require
from .recognition_metrics import load_evaluation, score_recognition_evaluation, score_threshold_candidate
from .plotting import render_soma, render_series, plotting_runtime


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def render_evaluation(source: Path, model: Path, output: Path, *, calibration_probe=False):
    return _render_evaluation(source, model, output, calibration_probe=calibration_probe)


def render_diagnostic_evaluation(source: Path, model: Path, stopped: Path, output: Path):
    """Stopped Train responses, including censored/unstarted declared trials."""
    from .stopped_evidence import load_case
    return _render_evaluation(source, model, output, source_case=load_case(stopped))


def _render_evaluation(source, model, output, *, calibration_probe=False, source_case=None):
    runtime = plotting_runtime()
    diagnostic = source_case is not None
    from .recognition_metrics import load_partial_diagnostic_evaluation, score_partial_diagnostic_evaluation
    if diagnostic:
        spec, observations, missing = load_partial_diagnostic_evaluation(source)
    else:
        spec, observations = load_evaluation(source)
    package = load(model)
    context_label = 'Stopped Train: '+source_case[0]["training_outcome"] if diagnostic else None
    scorer = score_threshold_candidate if calibration_probe else score_recognition_evaluation
    analysis = (score_partial_diagnostic_evaluation(spec, observations, package, source_case)
                if diagnostic else scorer(spec, observations, package))
    calibrated = package.get("kind") == "timelearner_calibrated_recognition_state"
    context = package["source_candidate"]["source_recognition"] if calibrated else (
        package["source_recognition"] if calibration_probe else package)
    # Descriptors: native binding enumerates Soma1..N (Branch has one soma).
    count = 1 if context["source_solo"]["configuration"]["model"]["branch"] else len(context["recognition_inputs"])
    nodes = {node["path"]: node for node in package["neuron"]["graph"]["identity"]["model"]["nodes"]}
    descriptors = []
    for i in range(count):
        path = f"$.Soma{i+1}"
        require(path in nodes, "missing_native_soma_descriptor")
        descriptors.append({"index": i, "path": path+".SumPotential", "class": nodes[path]["class"],
                            "units": "model_units_SI_unverified", "adapter": "native_recognition_soma"})
    require(all((diagnostic or o["samples"]) and all(len(s["soma"]) == count for s in o["samples"]) for o in observations),
            "missing_report_soma_samples")
    limits = []
    for i in range(count):
        values = [s["soma"][i] for o in observations for s in o["samples"]]
        if not values:
            limits.append(None)
            continue
        lo, hi = min(values), max(values)
        padding = (hi-lo)*.08 if hi > lo else max(abs(lo)*.08, 1e-12)
        limits.append((lo-padding, hi+padding))
    # Never overwrite an existing report, source data or completed job directory.
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary";primary.mkdir()
    _write(primary/"model.json", package)
    if diagnostic:
        # Keep the audited stopped source and every original training trace.
        evidence = primary/"stopped-source"
        if source_case[0].get('schema_version') == 5:
            from .composite_primary import capture_primary_blobs, write_primary_snapshot, _paths
            archive = source_case[0]['measurement_archive']
            refs = [trial['primary_ref'] for group in archive['records'] for trial in group['raw_trials']]
            values = capture_primary_blobs(archive['primary_blobs'], refs, archive['maximum_total_primary_bytes'])
            _paths(list(values) + ['train_stopped_state.json'] + (['train_stopped_summary.json'] if source_case[1] is not None else []))
            write_primary_snapshot(values, evidence)
        else:
            evidence.mkdir()
        _write(evidence/"train_stopped_state.json", source_case[0])
        if source_case[1] is not None:
            _write(evidence/"train_stopped_summary.json", source_case[1])
        for trial_id, trace in source_case[3].items():
            (evidence/trace.name).write_bytes(trace.read_bytes())
            _write(evidence/trace.with_suffix(".json").name, source_case[2][trial_id])
    copied_spec = dict(spec);copied_spec["trials"] = []
    by_id = {o["trial_id"]: o for o in observations}
    figures, links = [], []
    for trial in sorted(spec["trials"], key=lambda t: t["presentation_index"]):
        if trial["trial_id"] not in by_id:
            copied_spec["trials"].append(dict(trial))
            links.append(f'<h2>{html.escape(trial["trial_id"])}</h2><p>Observation file absent; no curve or classification inferred.</p>')
            continue
        o = by_id[trial["trial_id"]]
        index = trial["presentation_index"]
        name = f"trial-{index:04d}.json.gz"
        encoded = (json.dumps(o, ensure_ascii=False, allow_nan=False)+"\n").encode("utf-8")
        (primary/name).write_bytes(gzip.compress(encoded, mtime=0))
        copied_spec["trials"].append({**trial, "observation": name})
        if not o["samples"]:
            links.append(f'<h2>{html.escape(o["trial_id"])}</h2><p>No observed samples; no response curve or classification inferred.</p>')
            continue
        for descriptor in descriptors:
            folder = output/f'trial-{index:04d}-soma-{descriptor["index"]+1:03d}'
            folder.mkdir()
            views = render_soma(o, descriptor["index"], descriptor["path"], limits[descriptor["index"]], folder,
                                context_label=context_label)
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
    # Preserve actual presentation order and gaps in a separate series view.
    ordered = [by_id[t["trial_id"]] for t in sorted(spec["trials"], key=lambda t: t["presentation_index"]) if t["trial_id"] in by_id]
    series = []
    for descriptor in descriptors:
        if limits[descriptor["index"]] is None:
            continue
        observed = [o for o in ordered if o["samples"]] if diagnostic else ordered
        folder = output/f'series-soma-{descriptor["index"]+1:03d}'
        rendered = render_series(observed, descriptor["index"], descriptor["path"],
                                 limits[descriptor["index"]], folder, context_label=context_label)
        for view in rendered["views"]:
            view["files"] = [f"{folder.name}/{p}" for p in view["files"]]
        series.append({"descriptor": descriptor, **rendered})
    _write(output/"series.json", series)
    manifest = {"kind": "timelearner_visual_report", "schema_version": 1,
                "purpose": "threshold_candidate_diagnostic" if calibration_probe else "recognition_evaluation_diagnostic",
                "calibration_claim": False,
                "source_calibration_evidence_checked": analysis.get("calibration_evidence_checked", False),
                "run_id": spec["run_id"], "model_revision": spec["model_revision"],
                "status": "diagnostic", "observation_validity": analysis["validity"],
                "expected_trial_soma_pairs": len(spec["trials"])*count, "figures": figures,
                "series": series,
                "runtime": runtime,
                "limitations": ["Soma SI units not recorded in native observations",

                                "visual acceptance pending"],
                "visual_acceptance_complete": False, "evaluation_verdict": None}
    if diagnostic:
        manifest.update(purpose="stopped_training_recognition_diagnostic", diagnostic_only=True,
                        training_completed=False, source_training_outcome=source_case[0]["training_outcome"],
                        source_stopped_sha256=source_case[0]["sha256"],
                        missing_observation_ids=missing,
                        declared_trials=[{"trial_id": t["trial_id"], "observation_present": t["trial_id"] in by_id,
                                          "complete": by_id[t["trial_id"]]["complete"] if t["trial_id"] in by_id else False,
                                          "sample_count": len(by_id[t["trial_id"]]["samples"]) if t["trial_id"] in by_id else 0}
                                         for t in spec["trials"]],
                        observed_trial_soma_pairs=len(figures))
    _write(output/"manifest.json", manifest)
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>TimeLearner visual diagnostic report</title><style>body{font:18px sans-serif;margin:2em}'
        'img{display:block;width:100%;max-width:1920px}p{max-width:90em}</style>'
        '<h1>TimeLearner visual diagnostic report</h1>'
        + ('<p>Unfinished Train: '+html.escape(source_case[0]["training_outcome"])+'. Diagnostic responses only; no convergence certificate. Missing curves mean unobserved trials.</p>' if diagnostic else '')
        + ('<p>Threshold candidate probe: this report does not certify calibration or independent evaluation.</p>' if calibration_probe else '')
        + '<p>Actual soma SumPotential and shared input samples. '
        'Full primary data: <a href="primary/evaluation.json">evaluation</a>, '
        '<a href="primary/model.json">model</a>. <a href="analysis.json">Metrics</a>. '
        'SI units unverified; diagnostic report, visual acceptance pending. '
        'Click full PNG/SVG/PDF for readable scale. Purple dotted markers: actual LT spike events.</p>'
        +'<h2>Presentation-order series</h2><p><a href="series.json">timing table and series manifest</a></p>'
        +''.join(f'<p>{v["view"]}: <a href="{p}">{p}</a></p>' for item in series for v in item["views"] for p in v["files"])
        +"\n".join(links)+'</html>\n', encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()}
    _write(output/"SHA256SUMS.json", sums)
    return {"kind": manifest["kind"], "status": manifest["status"],
            "trial_soma_pairs": len(figures), "files": len(sums), "evaluation_verdict": None,
            **({"diagnostic_only": manifest["diagnostic_only"],
                "training_completed": manifest["training_completed"],
                "source_training_outcome": manifest["source_training_outcome"]} if diagnostic else {})}
