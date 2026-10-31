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
from .recognition_metrics import score_recognition_evaluation
from .reports import render_evaluation


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def render_posttune_transaction(source: Path, source_solo: Path, output: Path):
    runtime = plotting_runtime()
    report = load(source)
    source_case = load_case(source_solo)
    audit = audit_posttune_transaction(report, source_case)
    criterion = report["confirmation_specification"]["criterion"]
    jobs = []
    # Validate every complete matrix before creating even a partial report tree.
    # Active/cancelled matrices remain in the lossless transaction; they cannot
    # supply a complete-response picture or a synthetic missing foil.
    for index, row in enumerate(report["candidates"]):
        spec = _spec(row["matrix"], row["candidate"], criterion)
        scored = score_recognition_evaluation(spec, row["matrix"]["observations"], row["candidate"])
        require(scored["validity"] == "valid", "invalid_posttune_plot_matrix")
        jobs.append((f"weights-{index:04d}", row, spec))
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
        result = render_evaluation(inputs/"evaluation.json", inputs/"model.json", output/name)
        item = {"name": name, "model_revision": row["candidate"]["model_revision"],
                "measured_gap": row["measured_gap"], "report": name+"/index.html", "result": result}
        matrices.append(item)
        links.append('<li><a href="'+item["report"]+'">'+name+'</a>; measured '+
                     html.escape(report["metric"])+" gap "+html.escape(str(item["measured_gap"]))+'</li>')
    child = None
    if report["calibration"] is not None:
        _write(primary/"calibration.json", report["calibration"])
        child = render_calibration_transaction(primary/"calibration.json", output/"calibration")
        links.append('<li><a href="calibration/index.html">Actual threshold grid and fresh confirmation</a></li>')
    pairs = sum(item["result"]["trial_soma_pairs"] for item in matrices)
    manifest = {"kind": "timelearner_posttune_transaction_visual_report", "schema_version": 1,
                "status": "diagnostic", "transaction_status": report["status"],
                "source_transaction_sha256": report["sha256"], "source_solo_sha256": source_case[0]["sha256"],
                "weight_matrices": matrices, "weight_trial_soma_pairs": pairs,
                "calibration": child, "trial_soma_pairs": pairs+(child["trial_soma_pairs"] if child else 0),
                "runtime": runtime, "evidence_audit": audit, "source_primary_checked": True,
                "native_execution_verified": False, "visual_acceptance_complete": False,
                "incomplete_matrix_plotted_as_complete": False, "evaluation_verdict": None,
                "limitations": ["weight-selection data and same-matrix calibration are not independent Test",
                                "SI soma units unverified", "visual acceptance pending",
                                "partial probes retained without complete-response plots"]}
    _write(output/"manifest.json", manifest)
    note = '<p>No completed weight matrix is available.</p>' if not matrices else ''
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>TimeLearner measured PostTune</title><style>body{font:18px sans-serif;margin:2em}</style>'
        '<h1>Measured PostTune: '+html.escape(report["mode"])+" / "+html.escape(report["status"])+'</h1>'
        '<p>Every completed weight-candidate matrix, every actual threshold candidate and fresh confirmation: '
        'all declared patterns and soma channels, measured input overlays, full native samples, '
        'overview and readable detail views. Weight probes use the inherited threshold; their spike counts '
        'do not select weights or prove recognition. These data were used to select weights or calibrate '
        'the threshold and do not establish independent Test performance. Partial probes are retained '
        'without inferred complete responses. Visual acceptance remains pending.</p>'+note+
        '<ul>'+"".join(links)+'</ul><p><a href="primary/transaction.json.gz">Lossless source transaction</a>; '
        '<a href="manifest.json">Audit, scope and limitations</a>.</p></html>\n', encoding="utf-8")
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()}
    _write(output/"SHA256SUMS.json", sums)
    return {"kind": manifest["kind"], "status": "diagnostic", "weight_matrices": len(matrices),
            "trial_soma_pairs": manifest["trial_soma_pairs"], "files": len(sums), "evaluation_verdict": None}
