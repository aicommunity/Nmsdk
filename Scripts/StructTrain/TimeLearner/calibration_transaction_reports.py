"""All-candidate soma/input plots from validated native transaction matrices."""
from pathlib import Path
import gzip
import hashlib
import html
import json

from .calibration_transaction_evidence import audit_native_calibration_transaction
from .calibrated_evidence import REQUEST_FIELDS
from .recognition_metrics import score_threshold_candidate
from .native_evidence import load, require
from .plotting import plotting_runtime
from .reports import render_evaluation


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def _spec(matrix, candidate, criterion):
    require(type(matrix) is dict and set(matrix) == {"requests", "observations"} and
            type(matrix["requests"]) is list and type(matrix["observations"]) is list and
            len(matrix["requests"]) == len(matrix["observations"]) >= 2,
            "incomplete_calibration_transaction_report_matrix")
    trials = []
    for index, q in enumerate(matrix["requests"]):
        require(type(q) is dict and set(q) == REQUEST_FIELDS, "unknown_calibration_transaction_report_request")
        trials.append({**{k: q[k] for k in ("trial_id", "sample_id", "label", "pattern_hash", "reset_policy", "duration")},
                       "presentation_index": index, "observation": f"trial-{index:04d}.json.gz"})
    return {"kind": "timelearner_recognition_evaluation_spec", "schema_version": 1,
            "run_id": matrix["requests"][0]["run_id"], "model_revision": candidate["model_revision"],
            "coverage_policy": "per_trial_windows",
            "criterion": {"id": "post_anchor_target_whole_window_foil_v1", **criterion}, "trials": trials}


def render_calibration_transaction(source: Path, output: Path):
    # As for the other report entry points, backend/schema failures must occur
    # before any output directory is created.
    runtime = plotting_runtime()
    report = load(source)
    audit = audit_native_calibration_transaction(report)
    jobs = [(f"candidate-{i:04d}", row["candidate"], row["matrix"])
            for i, row in enumerate(report["candidates"])]
    if report["status"] in {"calibrated", "confirmation_failed"}:
        candidate = report["candidates"][report["selected_index"]]["candidate"]
        jobs.append(("fresh-confirmation", candidate, report["confirmation"]))
    for _, candidate, matrix in jobs:
        spec = _spec(matrix, candidate, report["criterion"])
        scored = score_threshold_candidate(spec, matrix["observations"], candidate)
        require(scored["validity"] == "valid", "invalid_calibration_transaction_plot_observations")
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary";primary.mkdir()
    encoded = json.dumps(report, ensure_ascii=False, allow_nan=False).encode("utf-8")
    (primary/"transaction.json.gz").write_bytes(gzip.compress(encoded, mtime=0))
    matrices, links = [], []
    for name, candidate, matrix in jobs:
        inputs = primary/name;inputs.mkdir()
        _write(inputs/"model.json", candidate)
        observations = {o["trial_id"]: o for o in matrix["observations"]}
        spec = _spec(matrix, candidate, report["criterion"])
        for index, q in enumerate(matrix["requests"]):
            filename = f"trial-{index:04d}.json.gz"
            raw = json.dumps(observations[q["trial_id"]], ensure_ascii=False, allow_nan=False).encode("utf-8")
            (inputs/filename).write_bytes(gzip.compress(raw, mtime=0))
        _write(inputs/"evaluation.json", spec)
        result = render_evaluation(inputs/"evaluation.json", inputs/"model.json", output/name, calibration_probe=True)
        item = {"name": name, "model_revision": candidate["model_revision"], "threshold": candidate["threshold"],
                "trials": len(spec["trials"]), "report": name+"/index.html", "result": result}
        matrices.append(item)
        links.append('<li><a href="'+html.escape(item["report"], quote=True)+'">'+html.escape(name)+
                     '</a>; threshold '+html.escape(str(candidate["threshold"]))+'</li>')
    pairs = sum(item["result"]["trial_soma_pairs"] for item in matrices)
    require(len(matrices) == len(jobs), "calibration_transaction_report_missing_matrix")
    manifest = {"kind": "timelearner_calibration_transaction_visual_report", "schema_version": 1,
                "status": "diagnostic", "transaction_status": report["status"],
                "source_transaction_sha256": report["sha256"], "matrices": matrices,
                "completed_matrices": len(matrices), "trial_soma_pairs": pairs, "runtime": runtime,
                "evidence_audit": audit, "source_primary_checked": False, "calibration_claim": False,
                "incomplete_matrix_plotted_as_complete": False, "visual_acceptance_complete": False,
                "limitations": ["SI soma units unverified", "visual acceptance pending",
                                "incomplete active probes retained in primary transaction; no complete-response plot inferred"],
                "evaluation_verdict": None}
    _write(output/"manifest.json", manifest)
    note = "" if matrices else '<p>No completed matrix is available. This diagnostic state supplies no complete response evidence.</p>'
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>TimeLearner calibration transaction</title><style>body{font:18px sans-serif;margin:2em}</style>'
        '<h1>Calibration transaction: '+html.escape(report["status"])+'</h1>'
        '<p>Every completed candidate matrix and fresh confirmation: all patterns, all soma channels, '
        'full native samples and overlaid measured input pulses. Each report provides full-size PNG/SVG/PDF, '
        'overview, detail views and presentation-order timelines. Threshold measurements are calibration diagnostics, '
        'not independent Test performance. Visual acceptance is pending.</p>'+note+'<ul>'+"".join(links)+'</ul>'
        '<p><a href="primary/transaction.json.gz">Lossless source transaction</a>; '
        '<a href="manifest.json">Report manifest</a>.</p></html>\n', encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()}
    _write(output/"SHA256SUMS.json", sums)
    return {"kind": manifest["kind"], "status": "diagnostic", "completed_matrices": len(matrices),
            "trial_soma_pairs": pairs, "files": len(sums), "evaluation_verdict": None}


def render_calibration_run(source: Path, output: Path):
    """Render the full grid only after auditing the portable run/primary closure."""
    plotting_runtime()
    from .native_calibration_worker import audit_run_manifest
    audit = audit_run_manifest(source)
    run = load(source)
    require(run["execution"] == "completed", "incomplete_calibration_run_has_no_complete_report")
    result = render_calibration_transaction(source.parent/"native/transaction.json", output)
    _write(output/"run-binding.json", {"kind": "calibration_report_run_binding", "schema_version": 1,
        "run_manifest_sha256": run["sha256"], "attempt_id": run["attempt_id"],
        "runtime_fingerprint": run["runtime_fingerprint"], "source_primary_checked": True,
        "run_audit": audit, "visual_acceptance_complete": False, "evaluation_verdict": None})
    index = output/"index.html";text = index.read_text(encoding="utf-8")
    require(text.count("</html>") == 1, "unknown_calibration_report_index")
    index.write_text(text.replace("</html>", '<p>Portable run and source primaries audited: '
        '<a href="run-binding.json">model/grid/runtime binding</a>. '
        'This does not establish independent Test or scientific PASS.</p></html>'), encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file() and p.name != "SHA256SUMS.json"}
    _write(output/"SHA256SUMS.json", sums)
    return {**result, "source_primary_checked": True, "run_evidence_consistent": True, "files": len(sums)}
