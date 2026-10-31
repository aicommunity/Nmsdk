"""Native boundary replay plots; capture consistency is not a training verdict."""
from pathlib import Path
import gzip
import hashlib
import json

from .finalization_boundary_evidence import audit_capture, audit_replay
from .native_evidence import load, require
from .plotting import plotting_runtime
from .recognition_metrics import score_recognition_evaluation
from .reports import render_evaluation


def render_boundary_replay(source: Path, comparison: Path, job: Path, output: Path):
    replay, captured, declaration = load(source), load(comparison), load(job)
    run_id = source.name.removesuffix("_replay.json")
    capture_audit = audit_capture(captured, replay["boundary"])
    replay_audit = audit_replay(replay, declaration, run_id)
    spec = {"kind": "timelearner_recognition_evaluation_spec", "schema_version": 1,
            "run_id": run_id, "model_revision": replay["recognition"]["model_revision"],
            "coverage_policy": "per_trial_windows",
            "criterion": {"id": "post_anchor_target_whole_window_foil_v1",
                          **declaration["specification"]["criterion"]},
            "trials": [{**{k: q[k] for k in ("trial_id", "sample_id", "label", "pattern_hash", "reset_policy", "duration")},
                        "presentation_index": i, "observation": f"trial-{i:04d}.json.gz"}
                       for i, q in enumerate(declaration["trials"])]}
    scored = score_recognition_evaluation(spec, replay["observations"], replay["recognition"])
    require(scored["validity"] == "valid", "invalid_boundary_plot_observations")
    output = Path(output)
    require(all(not output.resolve().is_relative_to(p.parent.resolve()) for p in (source, comparison, job)),
            "boundary_report_must_be_outside_primary_directory")
    plotting_runtime()  # Fail before creating the report tree if backend is unavailable.
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary"
    primary.mkdir()

    def write(path, value):
        raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+"\n").encode("utf-8")
        path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)

    write(primary/"replay.json.gz", replay)
    write(primary/"job.json", declaration)
    write(primary/"model.json", replay["recognition"])
    write(primary/"evaluation.json", spec)
    observations = {o["trial_id"]: o for o in replay["observations"]}
    for q in spec["trials"]:
        write(primary/q["observation"], observations[q["trial_id"]])
    result = render_evaluation(primary/"evaluation.json", primary/"model.json", output/"evaluation")
    manifest = {"kind": "native_finalization_boundary_visual_report", "schema_version": 1,
                "source_replay_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "source_comparison_sha256": hashlib.sha256(comparison.read_bytes()).hexdigest(),
                "source_job_sha256": hashlib.sha256(job.read_bytes()).hexdigest(),
                "capture_audit": capture_audit, "replay_audit": replay_audit,
                "boundary_sha256": replay["boundary"]["sha256"], "rendered_evaluation": result,
                "visual_acceptance_complete": False, "configured_phase_dispatch_implemented": False,
                "training_evidence_checked": False, "scientific_verdict": None}
    write(output/"manifest.json", manifest)
    (output/"index.html").write_text('<!doctype html><meta charset="utf-8"><title>Native boundary replay</title>'
        '<h1>Native Train boundary replay: recorded soma and input</h1>'
        '<p>Both declared target/foil patterns and every native soma channel. Complete recording windows; '
        'model units, SI unverified. These imported-model controls do not establish training convergence, '
        'independent evaluation or configured phase dispatch. Queued/stopped controls have no invented curves.</p>'
        '<p><a href="evaluation/index.html">All temporal plots and observed recognition metrics</a></p>', encoding="utf-8")
    write(output/"SHA256SUMS.json", {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(output.rglob("*")) if p.is_file()})
    return manifest
