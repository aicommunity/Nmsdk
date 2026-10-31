"""All measured weight candidates and actual threshold confirmation, without Test claims."""
from pathlib import Path
import gzip
import hashlib
import html
import json

from .calibration_transaction_reports import _spec, render_calibration_transaction
from .learned_evidence import load_case
from .native_evidence import load, require
from .plotting import plotting_runtime
from .posttune_transaction_evidence import audit_posttune_transaction
from .recognition_metrics import score_recognition_evaluation, score_threshold_candidate
from .reports import render_evaluation


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def render_posttune_transaction(source: Path, source_solo: Path, output: Path):
    plotting_runtime()
    return render_posttune_transaction_data(load(source), load_case(source_solo), output)


def render_posttune_transaction_data(report, source_case, output: Path):
    """Same production audit/renderer for an explicit re-exported source case.

    The supplied summary/packets/CSVs still undergo the complete source audit;
    this entry point does not create or overwrite historical source files.
    """
    runtime = plotting_runtime()
    audit = audit_posttune_transaction(report, source_case)
    criterion = report["confirmation_specification"]["criterion"]
    jobs = []
    # Validate every complete matrix before creating even a partial report tree.
    # Active/cancelled matrices remain in the lossless transaction; they cannot
    # supply a complete-response picture or a synthetic missing foil.
    for index, row in enumerate(report["candidates"]):
        model = report["weight_measurement_candidates"][index] if report["schema_version"] == 3 else row["candidate"]
        row = {**row, "candidate": model, "role": "weight_measurement"}
        spec = _spec(row["matrix"], model, criterion)
        scorer = score_threshold_candidate if model["kind"] == "timelearner_recognition_threshold_candidate" else score_recognition_evaluation
        scored = scorer(spec, row["matrix"]["observations"], model)
        require(scored["validity"] == "valid", "invalid_posttune_plot_matrix")
        jobs.append((f"weights-{index:04d}", row, spec))
    if report["schema_version"] == 3 and report.get("finalization") == "keep_fixed_threshold" and report["final_threshold_responses_observed"]:
        row = {"candidate": report["selected_package"], "matrix": report["final_model_matrix"],
               "measured_gap": None, "role": "final_model_responses"}
        spec = _spec(row["matrix"], row["candidate"], criterion)
        scored = score_recognition_evaluation(spec, row["matrix"]["observations"], row["candidate"])
        require(scored["validity"] == "valid", "invalid_posttune_final_model_plot_matrix")
        jobs.append(("final-model", row, spec))
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary"
    primary.mkdir()
    (primary/"transaction.json.gz").write_bytes(gzip.compress(
        json.dumps(report, ensure_ascii=False, allow_nan=False).encode("utf-8"), mtime=0))
    matrices, links = [], []
    for name, row, spec in jobs:
        inputs = primary/name
        inputs.mkdir()
        _write(inputs/"model.json", row["candidate"])
        observations = {o["trial_id"]: o for o in row["matrix"]["observations"]}
        for q in spec["trials"]:
            (inputs/q["observation"]).write_bytes(gzip.compress(json.dumps(
                observations[q["trial_id"]], ensure_ascii=False, allow_nan=False).encode("utf-8"), mtime=0))
        _write(inputs/"evaluation.json", spec)
        result = render_evaluation(inputs/"evaluation.json", inputs/"model.json", output/name,
            calibration_probe=row["candidate"]["kind"] == "timelearner_recognition_threshold_candidate")
        item = {"name": name, "model_revision": row["candidate"]["model_revision"],
                "measured_gap": row["measured_gap"], "role": row["role"], "report": name+"/index.html", "result": result}
        matrices.append(item)
        description = ('fresh responses at preserved final threshold' if row["role"] == "final_model_responses" else
                       'measured '+html.escape(report["metric"])+" gap "+html.escape(str(item["measured_gap"])))
        links.append('<li><a href="'+item["report"]+'">'+name+'</a>; '+description+'</li>')
    child = None
    if report["calibration"]:
        _write(primary/"calibration.json", report["calibration"])
        child = render_calibration_transaction(primary/"calibration.json", output/"calibration")
        links.append('<li><a href="calibration/index.html">Actual threshold grid and fresh confirmation</a></li>')
    weights = [item for item in matrices if item["role"] == "weight_measurement"]
    final = [item for item in matrices if item["role"] == "final_model_responses"]
    pairs = sum(item["result"]["trial_soma_pairs"] for item in weights)
    final_pairs = sum(item["result"]["trial_soma_pairs"] for item in final)
    manifest = {"kind": "timelearner_posttune_transaction_visual_report", "schema_version": 1,
                "status": "diagnostic", "transaction_status": report["status"],
                "source_transaction_sha256": report["sha256"], "source_solo_sha256": source_case[0]["sha256"],
                "weight_matrices": weights, "weight_trial_soma_pairs": pairs,
                "final_model_matrices": final, "final_model_trial_soma_pairs": final_pairs,
                "calibration": child, "trial_soma_pairs": pairs+final_pairs+(child["trial_soma_pairs"] if child else 0),
                "runtime": runtime, "evidence_audit": audit, "source_primary_checked": True,
                "native_execution_verified": False, "visual_acceptance_complete": False,
                "incomplete_matrix_plotted_as_complete": False, "evaluation_verdict": None,
                "limitations": ["weight-selection data and same-matrix calibration are not independent Test",
                                "SI soma units unverified", "visual acceptance pending",
                                "partial probes retained without complete-response plots"]}
    fixed_note = ""
    if report.get("finalization") == "keep_fixed_threshold":
        manifest.update({"finalization": "keep_fixed_threshold", "calibration_policy": "fixed",
                         "calibration_status": audit["calibration_status"],
                         "recognition_success_confirmed": False})
        fixed_note = ('<p>Fixed-threshold finalization requested no threshold search. Only a selected package '
                      'binds its preserved threshold; recovery-required does not attest the live owner state. '
                      'Weights selected is a weight-phase outcome; '
                      'a silent target remains a false negative. Calibration and successful recognition '
                      'are not inferred from the measured analogue gap.</p>')
    _write(output/"manifest.json", manifest)
    note = '<p>No completed weight matrix is available.</p>' if not matrices else ''
    probe_note = ('Weight probes use the explicitly declared measurement threshold; fresh final-model responses '
                  'are shown separately at the preserved final threshold. ' if report["schema_version"] == 3 else
                  'Weight probes use the inherited threshold. ')
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>TimeLearner measured PostTune</title><style>body{font:18px sans-serif;margin:2em}</style>'
        '<h1>Measured PostTune: '+html.escape(report["mode"])+" / "+html.escape(report["status"])+'</h1>'
        '<p>Every completed weight-candidate matrix, every actual threshold candidate and fresh confirmation: '
        'all declared patterns and soma channels, measured input overlays, full native samples, '
        'overview and readable detail views. '+probe_note+'Their spike counts '
        'do not select weights or prove recognition. These data were used to select weights or calibrate '
        'the threshold and do not establish independent Test performance. Partial probes are retained '
        'without inferred complete responses. Visual acceptance remains pending.</p>'+fixed_note+note+
        '<ul>'+"".join(links)+'</ul><p><a href="primary/transaction.json.gz">Lossless source transaction</a>; '
        '<a href="manifest.json">Audit, scope and limitations</a>.</p></html>\n', encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()}
    _write(output/"SHA256SUMS.json", sums)
    return {"kind": manifest["kind"], "status": "diagnostic", "weight_matrices": len(weights),
            "trial_soma_pairs": manifest["trial_soma_pairs"], "files": len(sums), "evaluation_verdict": None}


def render_posttune_run(source: Path, output: Path):
    """Bind every plotted matrix to a validated portable production run."""
    from .native_calibration_worker import audit_run_manifest
    plotting_runtime()
    proof = audit_run_manifest(source, post_tune=True)
    run = load(source)
    require(run["execution"] == "completed", "incomplete_posttune_run_has_no_complete_report")
    result = render_posttune_transaction(source.parent/"native/transaction.json",
                                        source.parent/run["source_package_path"], output)
    binding = {"kind": "timelearner_posttune_run_visual_binding", "schema_version": 1,
               "run_manifest_sha256": run["sha256"], "attempt_id": run["attempt_id"],
               "runtime_fingerprint": run["runtime_fingerprint"], "source_closure": run["source_closure"],
               "source_primary_checked": True, "run_audit": proof,
               "native_execution_verified": False, "visual_acceptance_complete": False, "evaluation_verdict": None}
    _write(output/"run-binding.json", binding)
    manifest = load(output/"manifest.json")
    manifest["run_manifest_sha256"] = run["sha256"]
    manifest["runtime_fingerprint"] = run["runtime_fingerprint"]
    _write(output/"manifest.json", manifest)
    index = output/"index.html"
    text = index.read_text(encoding="utf-8")
    require(text.count("</html>") == 1, "unknown_posttune_report_index")
    index.write_text(text.replace("</html>", '<p>Production run, owned-process records, source primaries and actual final model audited: '
        '<a href="run-binding.json">run/runtime/source binding</a>. Independent Test and scientific PASS are not inferred.</p></html>'),
        encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file() and p != output/"SHA256SUMS.json"}
    _write(output/"SHA256SUMS.json", sums)
    return {**result, "files": len(sums), "run_evidence_consistent": True, "source_primary_checked": True}
