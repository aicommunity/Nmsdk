"""Explicit CLI entry point; commands have no import-time side effects."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


def analyze(args: argparse.Namespace) -> dict:
    from .native_evidence import EvidenceError, audit_probe, load, require
    historical_analysis = getattr(args, 'historical_analysis', None)
    require(args.format == 'pipeline-run' or historical_analysis is None,
            'historical_analysis_is_only_for_pipeline_run')
    require(args.format == "historical-selectivity" or getattr(args, "expected_trial_ids", None) is None,
            "expected_trial_ids_is_only_for_historical_selectivity")
    for option in ("rest_bound", "soma_abs_limit", "time_step_hz"):
        require(args.format == "branch-dynamics" or getattr(args, option, None) is None,
                option + "_is_only_for_branch_dynamics")
    require(args.format == "native-live-finalization" or getattr(args, "primary_inventory", None) is None,
            "primary_inventory_is_only_for_live_finalization")
    require(args.format == "domain" or not args.allow_legacy, "legacy_adapter_is_only_for_domains")
    require(args.format in ("probe", "legacy-posttune-freerun") or args.trace is None, "trace_option_is_only_for_probes")
    require(args.format in ("recognition-trial", "recognition-evaluation", "native-calibration-assessment") or args.model is None, "model_option_is_only_for_recognition_trials")
    require(args.format in ("threshold-candidate", "native-calibration-assessment", "calibrated-state", "calibration-transaction", "posttune-transaction") or args.source_solo is None, "source_solo_option_is_only_for_threshold_candidates")
    require(args.format == "native-calibration-assessment" or args.evaluation is None, "evaluation_option_is_only_for_native_calibration")
    source = args.source.resolve(strict=True)
    if args.format == "historical-selectivity":
        from .historical_selectivity import analyze_historical_csv
        result = analyze_historical_csv(source, args.expected_trial_ids)
    elif args.format == "legacy-statistic-traces":
        from .statistic_traces import analyze_inputs
        result = analyze_inputs(source)
    elif args.format == "branch-dynamics":
        from .legacy_dynamics import analyze_telemetry
        result = analyze_telemetry(source, rest_bound=args.rest_bound,
                                  soma_abs_limit=args.soma_abs_limit, time_step_hz=args.time_step_hz)
    elif args.format == "native-live-finalization":
        from .live_finalization_reports import read_live_report_source
        from .live_finalization_evidence import audit_completed_live_finalization, audit_pre_entry_live_finalization
        require(args.primary_inventory is not None, "live_finalization_primary_inventory_required")
        record, case, _, _ = read_live_report_source(source, args.primary_inventory.resolve(strict=True))
        result = (audit_completed_live_finalization if record["scenario"] in (0, 1) else audit_pre_entry_live_finalization)(record, case)
    elif args.format == "native-calibration-assessment":
        from .native_calibration_evidence import audit_native_calibration_assessment
        from .recognition_metrics import load_evaluation
        from .learned_evidence import load_case
        require(args.model is not None and args.evaluation is not None and args.source_solo is not None,
                "native_calibration_requires_model_evaluation_and_source_evidence")
        spec, observations = load_evaluation(args.evaluation.resolve(strict=True))
        result = audit_native_calibration_assessment(load(source), spec, observations,
            load(args.model.resolve(strict=True)), load_case(args.source_solo.resolve(strict=True)))
    elif args.format == "capacitance-history":
        from .training_capacitance_history import audit_training_capacitance_case
        result = audit_training_capacitance_case(source)
    elif args.format == "capacitance-witness":
        from .training_capacitance_witness import audit_training_capacitance_witness
        result = audit_training_capacitance_witness(load(source))
    elif args.format == "capacitance-region":
        from .capacitance_region_evidence import audit_capacitance_region
        result = audit_capacitance_region(source)
    elif args.format == "capacitance-binding":
        from .capacitance_binding_evidence import audit_capacitance_binding
        result = audit_capacitance_binding(load(source))
    elif args.format == "training-capacitance-bridge":
        from .training_capacitance_bridge_evidence import audit_training_capacitance_bridge
        result = audit_training_capacitance_bridge(load(source))
    elif args.format == "domain":
        from .domain_evidence import audit_resistance_domain
        result = audit_resistance_domain(load(source), allow_legacy=args.allow_legacy)
    elif args.format == "learned-solo":
        from .learned_evidence import audit_learned_state, load_case
        result = audit_learned_state(*load_case(source))
    elif args.format == "stopped-solo":
        from .stopped_evidence import audit_stopped_state, load_case
        result = audit_stopped_state(*load_case(source))
    elif args.format == "stopped-final-pass":
        from .stopped_final_pass import audit_negative_final_pass, load_inputs
        result = audit_negative_final_pass(*load_inputs(source))
    elif args.format == "recognition-evaluation":
        from .recognition_metrics import load_evaluation, score_recognition_evaluation
        require(args.model is not None, "recognition_model_package_required")
        result = score_recognition_evaluation(*load_evaluation(source), load(args.model.resolve(strict=True)))
    elif args.format in ("calibration-run", "posttune-run"):
        from .native_calibration_worker import audit_run_manifest
        result = audit_run_manifest(source, post_tune=args.format == "posttune-run")
    elif args.format == "pipeline-run":
        from .native_pipeline_worker import audit_run_manifest
        result = audit_run_manifest(source, historical_analysis=historical_analysis)
    elif args.format == "posttune-transaction":
        from .posttune_transaction_evidence import audit_posttune_transaction
        from .learned_evidence import load_case
        require(args.source_solo is not None, "posttune_transaction_source_evidence_required")
        result = audit_posttune_transaction(load(source), load_case(args.source_solo.resolve(strict=True)))
    elif args.format == "calibration-transaction":
        from .calibration_transaction_evidence import audit_native_calibration_transaction
        from .learned_evidence import load_case
        require(args.source_solo is not None, "calibration_transaction_source_evidence_required")
        result = audit_native_calibration_transaction(load(source), load_case(args.source_solo.resolve(strict=True)))
    elif args.format == "calibrated-state":
        from .calibrated_evidence import audit_calibrated_state
        from .learned_evidence import load_case
        require(args.source_solo is not None, "calibrated_state_source_evidence_required")
        result = audit_calibrated_state(load(source), load_case(args.source_solo.resolve(strict=True)))
    elif args.format == "threshold-candidate":
        from .threshold_candidate_evidence import audit_threshold_candidate
        from .learned_evidence import load_case
        require(args.source_solo is not None, "threshold_candidate_source_evidence_required")
        result = audit_threshold_candidate(load(source), load_case(args.source_solo.resolve(strict=True)))
    elif args.format == "recognition-trial":
        from .recognition_trial_evidence import audit_recognition_trial
        require(args.model is not None, "recognition_model_package_required")
        result = audit_recognition_trial(load(source), load(args.model.resolve(strict=True)))
    elif args.format == "recognition-owner":
        from .recognition_owner_evidence import audit_owner_recognition, load_case
        result = audit_owner_recognition(*load_case(source))
    elif args.format == "recognition":
        from .recognition_evidence import audit_recognition_state, load_case
        result = audit_recognition_state(*load_case(source))
    elif args.format == "posttune-reconstruction":
        from .posttune_evidence import audit_reconstruction, load_case
        result = audit_reconstruction(*load_case(source))
    elif args.format == "posttune-transient":
        from .transient_evidence import audit_transient_presentation, load_case
        result = audit_transient_presentation(*load_case(source))
    elif args.format == "probe":
        require(args.trace is not None, "primary_probe_trace_required")
        result = audit_probe(load(source), args.trace.resolve(strict=True))
    elif args.format == "legacy-posttune-freerun":
        from .legacy_posttune_evidence import audit_free_run
        require(args.trace is not None, "legacy_posttune_primary_csv_required")
        result = audit_free_run(source, args.trace.resolve(strict=True))
    else:
        raise EvidenceError("unsupported_analysis_format")
    return {"kind": "timelearner_analysis", "schema_version": 1,
            "execution": "completed", "validity": result.get("validity", "valid"), "format": args.format,
            "analysis": result, "evaluation_verdict": None}


def _process_policy(args):
    from .native_evidence import load
    return None if args.process_policy is None else load(args.process_policy.resolve(strict=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TimeLearner reproducible experiment tools")
    commands = parser.add_subparsers(dest="command", required=True)
    controller_ab = commands.add_parser("controller-ab", help="compare pinned pure controller kernels on a Linux worker")
    controller_ab.add_argument("specification", type=Path)
    controller_ab.add_argument("--root-repository", type=Path, required=True)
    controller_ab.add_argument("--pulselib-repository", type=Path, required=True)
    controller_ab.add_argument("--compiler", type=Path, required=True)
    controller_ab.add_argument("--gtest-source", type=Path, required=True)
    controller_ab.add_argument("--output", type=Path, required=True)
    controller_kernel = commands.add_parser("controller-kernel", help="run pinned pure decision kernel tests on a Linux worker")
    controller_kernel.add_argument("specification", type=Path)
    controller_kernel.add_argument("--root-repository", type=Path, required=True)
    controller_kernel.add_argument("--pulselib-repository", type=Path, required=True)
    controller_kernel.add_argument("--compiler", type=Path, required=True)
    controller_kernel.add_argument("--gtest-source", type=Path, required=True)
    controller_kernel.add_argument("--output", type=Path, required=True)
    pipeline = commands.add_parser("pipeline", help="managed Train/export/optional tuning/frozen Test with a durable boundary journal")
    pipeline.add_argument("action", choices=("run", "continue", "audit", "reconcile"))
    pipeline.add_argument("directory", type=Path)
    pipeline.add_argument("--specification", type=Path)
    pipeline.add_argument("--runtime-manifest", type=Path)
    pipeline.add_argument("--process-policy", type=Path)
    pipeline.add_argument("--stop-after", choices=("train", "export", "posttune", "calibrate", "evaluate"))
    gate = commands.add_parser("native-gate", help="run an explicit native test set in an immutable existing runtime")
    gate.add_argument("specification", type=Path)
    gate.add_argument("--output", type=Path, required=True)
    replay = commands.add_parser("legacy-completed-replay", help="replay pinned saved nonexact completed states without retraining")
    replay.add_argument("specification", type=Path)
    replay.add_argument("--output", type=Path, required=True)
    regression = commands.add_parser("preflight-regression", help="run the declared public Console regression matrix")
    regression.add_argument("specification", type=Path)
    regression.add_argument("--output", type=Path, required=True)
    diagnostic = commands.add_parser("diagnostic-regression", help="run declared public stopped-Train diagnostic regressions")
    diagnostic.add_argument("specification", type=Path)
    diagnostic.add_argument("--output", type=Path, required=True)
    prepare = commands.add_parser("prepare", help="prepare a declared native cold-job matrix without running models")
    prepare.add_argument("specification", type=Path)
    prepare.add_argument("--output", type=Path, required=True, help="new immutable job matrix directory")
    for operation in ("train", "preflight", "export", "evaluate", "diagnostic-evaluate", "probe"):
        native = commands.add_parser(operation, help="run an owned native Console "+operation+" job")
        native.add_argument("specification", type=Path)
        if operation == "diagnostic-evaluate":
            native.add_argument("--source-stopped", dest="source_solo", type=Path, required=True,
                                help="stopped package with its original primary trial siblings; never completed Train")
        elif operation == "probe":
            native.add_argument("--source-stopped", dest="source_solo", type=Path,
                                help="schema2 probe: original stopped package and primary trial siblings")
        else:
            native.add_argument("--source-solo", type=Path, help="completed source package with primary trial siblings; export/evaluate only")
        native.add_argument("--runtime-manifest", type=Path, required=True)
        native.add_argument("--wall-seconds", type=float, required=True)
        native.add_argument("--process-policy", type=Path, help="explicit whole-cgroup limits; omitted retains legacy process scope")
        native.add_argument("--output", type=Path, required=True, help="new immutable result directory")
    transfer = commands.add_parser("model-spec-transport", help="replay pinned positive engineering N1 jobs, then measure calibration and fresh import")
    transfer.add_argument("action", choices=("prepare", "run"))
    transfer.add_argument("source", type=Path, help="Git repository for prepare; prepared declarations for run")
    transfer.add_argument("--runtime-manifest", type=Path)
    transfer.add_argument("--completed-prefix", type=Path, help="verified closed operation prefix; never a mid-probe checkpoint")
    transfer.add_argument("--output", type=Path, required=True)
    study = commands.add_parser("n1-protocol-study", help="probe preregistered N1 thresholds across order/reset/quiet-tail conditions")
    study.add_argument("action", choices=("prepare", "run", "analyze", "report"))
    study.add_argument("source", type=Path)
    study.add_argument("--runtime-manifest", type=Path)
    study.add_argument("--source-evidence")
    study.add_argument("--output", type=Path, required=True)
    stock = commands.add_parser("stock-phasea-preflight", help="build and inspect the stock four-input NSPNeuronGen without LT membrane; no Train")
    stock.add_argument("source", type=Path)
    stock.add_argument("--runtime-manifest", type=Path, required=True)
    stock.add_argument("--initial-threshold", type=float, help="explicit native model-spec2 construction value; e.g. 100 for training")
    stock.add_argument("--output", type=Path, required=True)
    pair = commands.add_parser("stock-threshold-study", help="paired cold stock Train at explicit thresholds 0.0117 and 100 on one runtime")
    pair.add_argument("action", choices=("prepare", "run", "analyze", "failure-report"))
    pair.add_argument("source", type=Path)
    pair.add_argument("--runtime-manifest", type=Path)
    pair.add_argument("--code-identity", type=Path)
    pair.add_argument("--output", type=Path, required=True)
    phasea = commands.add_parser("phasea-matrix", help="recover all four ISIs and labels from exact historical Bin Git data; no model execution")
    phasea.add_argument("--bin-repository", type=Path, required=True)
    phasea.add_argument("--revision", default="1c1464e248f8744e858bd66df0be99e39969fd65")
    phasea.add_argument("--output", type=Path, required=True)
    stopped_stock = commands.add_parser("stock-stopped-evaluation", help="diagnostic eight-pattern frozen probes of actual unfinished stock models; preserves inherited thresholds")
    stopped_stock.add_argument("action", choices=("prepare", "run", "analyze", "report"))
    stopped_stock.add_argument("source", type=Path)
    stopped_stock.add_argument("--bin-repository", type=Path)
    stopped_stock.add_argument("--output", type=Path, required=True)
    inventory = commands.add_parser("inventory", help="inventory source properties and tracked historical tools")
    inventory.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    inventory.add_argument("--output", type=Path, required=True)
    inventory.add_argument('--revision', help='full root commit SHA; defaults to current root HEAD and its recorded gitlinks')
    inventory.add_argument('--include-related', action='store_true', help='schema3 review catalog: also match TimeLearner tokens in committed script content; never execute tools')
    analysis = commands.add_parser("analyze", help="audit original native evidence; no recognition verdict")
    analysis.add_argument("source", type=Path)
    analysis.add_argument("--format", choices=('capacitance-region', 'capacitance-history', 'capacitance-witness', 'capacitance-binding', 'training-capacitance-bridge', 'domain', 'probe', 'learned-solo', 'stopped-solo', 'recognition', 'recognition-owner', 'recognition-trial', 'recognition-evaluation', 'threshold-candidate', 'calibrated-state', 'calibration-transaction', 'posttune-transaction', 'calibration-run', 'posttune-run', 'pipeline-run', 'native-calibration-assessment', 'posttune-reconstruction', 'posttune-transient', 'legacy-posttune-freerun', 'native-live-finalization', 'branch-dynamics', 'historical-selectivity', 'stopped-final-pass', 'legacy-statistic-traces'), required=True)
    analysis.add_argument("--expected-trial-ids", nargs="+", help="independently declared IDs required for historical-selectivity CSV")
    analysis.add_argument("--rest-bound", type=float, help="descriptive channel envelope for branch-dynamics; legacy default 1")
    analysis.add_argument("--soma-abs-limit", type=float, help="optional descriptive soma bound for branch-dynamics")
    analysis.add_argument("--time-step-hz", type=float, help="actual model update frequency for branch-dynamics local gain estimates")
    analysis.add_argument("--primary-inventory", type=Path, help="declared native live primary inventory/composition")
    analysis.add_argument("--model", type=Path, help="recognition package required for recognition trial/evaluation")
    analysis.add_argument("--source-solo", type=Path, help="original learned-state package with primary trial siblings, required for threshold candidate")
    analysis.add_argument("--evaluation", type=Path, help="independently declared evaluation spec required for native calibration assessment")
    analysis.add_argument("--trace", type=Path, help="original primary CSV, required for probe")
    analysis.add_argument("--allow-legacy", action="store_true", help="descriptive domain schema-1 adapter only")
    analysis.add_argument("--historical-analysis", choices=("learned-v2-no-capacitance",
                         "training-v3-no-capacitance-history"),
                         help="explicit archived training analysis adapter for pipeline-run only; defaults to strict equality")
    analysis.add_argument("--output", type=Path, help="new output file; an existing file is never replaced")
    report = commands.add_parser("report", help="large native soma/input diagnostic figures with portable primary data")
    report.add_argument("source", type=Path, help="recognition evaluation spec")
    report.add_argument("--format", choices=("capacitance-search", "capacitance-region", "pipeline-run", "recognition-evaluation", "recognition-transport", "threshold-candidate-evaluation", "probe", "probe-diagnostic", "legacy-posttune-freerun", "probe-set", "native-test-run", "dataset-clock", "calibration-transaction", "calibration-run", "posttune-transaction", "posttune-run", "native-live-finalization"), default="recognition-evaluation")
    report.add_argument("--primary-inventory", type=Path, help="declared native live primary inventory/composition")
    report.add_argument("--artifacts", type=Path, help="native-test-run directory containing native.xml and native/")
    report.add_argument("--model", type=Path)
    report.add_argument("--trace", type=Path, help="primary CSV required for probe report")
    report.add_argument("--source-solo", type=Path, help="original learned-state and adjacent primaries required for posttune-transaction")
    report.add_argument("--output", type=Path, required=True, help="new directory; never overwritten")
    publication = commands.add_parser("publish", help="publish exact Git closure children-first; no scientific verdict")
    publication.add_argument("specification", type=Path)
    publication.add_argument("--root", type=Path, required=True)
    publication.add_argument("--output", type=Path, required=True, help="new receipt outside source tree")
    recovery = commands.add_parser("publish-recover", help="explicit Linux recovery of a closed publication lock; no push")
    recovery.add_argument("--root", type=Path, required=True)
    recovery.add_argument("--output", type=Path, required=True, help="new recovery receipt outside source tree")
    calibration = commands.add_parser("calibrate", help="run a native Console calibration job or select/confirm from saved primary measurements")
    calibration.add_argument("action", choices=("run", "select", "confirm"))
    calibration.add_argument("specification", type=Path)
    calibration.add_argument("--measurements", type=Path, help="portable search measurement-set descriptor for select/confirm")
    calibration.add_argument("--runtime-manifest", type=Path, help="verified Console runtime required for run")
    calibration.add_argument("--wall-seconds", type=float, help="owned process wall budget required for run")
    calibration.add_argument("--process-policy", type=Path, help="whole-cgroup execution policy; run only")
    calibration.add_argument("--source-solo", type=Path, required=True, help="original learned-state package with primary trial siblings")
    calibration.add_argument("--selection", type=Path, help="required for confirmation; recomputed against primary search evidence")
    calibration.add_argument("--confirmation", type=Path, help="one fresh measurement-set descriptor required for confirmation")
    calibration.add_argument("--output", type=Path, required=True, help="new result file; never overwritten")
    posttune = commands.add_parser("posttune", help="owned native measured weight search with explicit fixed threshold or calibration")
    posttune.add_argument("specification", type=Path)
    posttune.add_argument("--source-solo", type=Path, required=True)
    posttune.add_argument("--runtime-manifest", type=Path, required=True)
    posttune.add_argument("--wall-seconds", type=float, required=True)
    posttune.add_argument("--process-policy", type=Path, help="explicit whole-cgroup execution policy")
    posttune.add_argument("--output", type=Path, required=True, help="new run directory; never overwritten")
    bundle = commands.add_parser("bundle", help="lossless primary archives; full plots remain in worker cache")
    bundle.add_argument("action", choices=("pack-native-tests", "verify", "extract"))
    bundle.add_argument("source", type=Path, help="native contract for pack; bundle directory otherwise")
    bundle.add_argument("--artifacts", type=Path)
    bundle.add_argument("--selected-report", type=Path, help="completed full native report with checked PDF previews")
    bundle.add_argument("--output", type=Path, help="new bundle or extraction directory")
    bundle.add_argument("--maximum-bytes", type=int, default=8*1024**3, help="maximum uncompressed extraction bytes")
    history = commands.add_parser("history", help="resolve historical root SHA after generated-report cleanup")
    history.add_argument("action", choices=("resolve", "verify-migration"))
    history.add_argument("revision")
    history.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    history.add_argument("--map", type=Path)
    history.add_argument("--bin-repository", type=Path)
    history.add_argument("--pulselib-repository", type=Path)
    history.add_argument("--output", type=Path)
    probe = commands.add_parser("probe-job", help="prepare or audit a native whole-burst characterization without training")
    probe.add_argument("action", choices=["prepare", "prepare-stopped", "analyze", "analyze-matched", "report-matched"])
    probe.add_argument("source", type=Path)
    probe.add_argument("--input-index", type=int)
    probe.add_argument("--trial-id")
    probe.add_argument("--resistance-intervention", type=Path)
    probe.add_argument("--output", type=Path, required=True)
    fixed = commands.add_parser("fixed-geometry-resistance", help="gate stock Rs controls on the complete stopped model graph")
    fixed.add_argument("action", choices=["prepare", "run"])
    fixed.add_argument("source", type=Path)
    fixed.add_argument("--runtime-manifest", type=Path)
    fixed.add_argument("--output", type=Path, required=True)
    reuse = commands.add_parser("primary-reuse", help="losslessly reuse primary source files already published in Git")
    reuse.add_argument("action", choices=["pack", "restore"])
    reuse.add_argument("source", type=Path)
    reuse.add_argument("--repository", type=Path, required=True)
    reuse.add_argument("--reference-commit")
    reuse.add_argument("--reference-archive")
    reuse.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "pipeline":
        from .managed_pipeline import run_pipeline, audit_pipeline, reconcile_pipeline
        from .native_evidence import load, require, EvidenceError
        try:
            if args.action in ("audit", "reconcile"):
                require(all(v is None for v in (args.specification, args.runtime_manifest,
                                               args.process_policy, args.stop_after)), "pipeline_audit_execution_options")
                result = (reconcile_pipeline if args.action == "reconcile" else audit_pipeline)(args.directory)
            else:
                require(all(v is not None for v in (args.specification, args.runtime_manifest,
                                                   args.process_policy)), "pipeline_execution_inputs_required")
                result = run_pipeline(args.specification, args.runtime_manifest, load(args.process_policy),
                                      args.directory, resume=args.action == "continue", stop_after=args.stop_after)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return 0 if result["pending_phase"] is None and result["halted_phase"] is None else 2
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"kind": "timelearner_managed_pipeline_error", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    if args.command == "primary-reuse":
        from .primary_reuse import pack, restore
        from .native_evidence import EvidenceError, require
        try:
            if args.action == "pack":
                require(args.reference_commit is not None and args.reference_archive is not None, "primary_reuse_reference_required")
                result = pack(args.source, args.repository, args.reference_commit, args.reference_archive, args.output)
            else:
                require(args.reference_commit is None and args.reference_archive is None, "primary_reuse_restore_cannot_override_reference")
                result = restore(args.source, args.repository, args.output)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False));return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error), "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "fixed-geometry-resistance":
        from .fixed_geometry_resistance import prepare, run
        from .native_evidence import EvidenceError, require
        try:
            if args.action == "prepare":
                require(args.runtime_manifest is None, "fixed_geometry_prepare_has_no_runtime")
                result = prepare(args.source, args.output)
            else:
                require(args.runtime_manifest is not None, "fixed_geometry_runtime_required")
                result = run(args.source, args.runtime_manifest, args.output)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False));return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "probe-job":
        from .native_characterization import prepare_job, prepare_stopped_job, audit_execution
        from .native_evidence import EvidenceError, load, require
        from .native_calibration_worker import _write
        try:
            if args.action == "report-matched":
                require(args.input_index is None and args.trial_id is None and args.resistance_intervention is None, "probe_report_has_no_configuration_overrides")
                from .matched_resistance_reports import render
                result = render(args.source, args.output)
                print(json.dumps(result, ensure_ascii=False, allow_nan=False));return 0
            if args.action == "prepare":
                require(args.input_index is not None and args.trial_id is not None, "probe_identity_required")
                require(args.resistance_intervention is None, "cold_probe_prepare_has_no_import_intervention")
                result = prepare_job(load(args.source), args.input_index, args.trial_id)
            elif args.action == "prepare-stopped":
                from .stopped_evidence import load_case as load_stopped_case
                require(args.input_index is not None and args.trial_id is not None, "probe_identity_required")
                changes = None
                if args.resistance_intervention is not None:
                    from .native_evidence import load_json
                    changes = load_json(args.resistance_intervention)
                result = prepare_stopped_job(load_stopped_case(args.source), args.input_index, args.trial_id, resistance_intervention=changes)
            else:
                require(args.input_index is None and args.trial_id is None and args.resistance_intervention is None, "probe_analysis_has_no_configuration_overrides")
                if args.action == "analyze-matched":
                    from .matched_resistance_analysis import analyze as analyze_matched_resistance
                    result = analyze_matched_resistance(args.source)
                else:
                    result = audit_execution(args.source)
            _write(args.output, result)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False));return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "diagnostic-regression":
        from .diagnostic_regression import run_diagnostic_regression
        from .native_evidence import EvidenceError
        try:
            print(json.dumps(run_diagnostic_regression(args.specification, args.output), ensure_ascii=False, allow_nan=False))
            return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"kind": "timelearner_diagnostic_regression_error", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    if args.command == "prepare":
        from .prepare import write_prepared_matrix
        from .native_evidence import EvidenceError
        try:
            result = write_prepared_matrix(args.specification, args.output)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False));return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"kind": "timelearner_preparation_error", "validity": "invalid",
                              "reason": str(error), "evaluation_verdict": None}), file=sys.stderr)
            return 2
    if args.command == "posttune":
        from .native_evidence import EvidenceError
        from .native_calibration_worker import run_job
        try:
            result = run_job(args.specification, args.source_solo, args.runtime_manifest, args.output,
                             args.wall_seconds, post_tune=True, process_policy=_process_policy(args))
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return 0 if result["validity"] == "valid" else 2
        except (EvidenceError, OSError, ValueError) as error:
            print(json.dumps({"validity": "invalid", "reason": str(error), "scientific_verdict": None}), file=sys.stderr)
            return 2
    if args.command == "legacy-completed-replay":
        from .legacy_completed_replay import run_legacy_completed_replay
        from .native_evidence import EvidenceError
        try:
            result = run_legacy_completed_replay(args.specification, args.output)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return 0 if result["assertion_status"] == "passed" else 2
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"kind": "timelearner_legacy_completed_replay_error", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    if args.command in ("controller-ab", "controller-kernel"):
        from .native_evidence import EvidenceError
        from .controller_ab import run_controller_ab, run_controller_kernel
        try:
            runner = run_controller_kernel if args.command == "controller-kernel" else run_controller_ab
            result = runner(args.specification, args.root_repository, args.pulselib_repository,
                                       args.compiler, args.gtest_source, args.output)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return 0 if result['assertion_status'] == 'passed' else 2
        except (EvidenceError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
            print(json.dumps({'kind': 'timelearner_controller_kernel_error' if args.command == 'controller-kernel' else 'timelearner_controller_ab_error', 'reason': str(error),
                              'scientific_verdict': None}), file=sys.stderr)
            return 2
    if args.command == "native-gate":
        from .native_evidence import EvidenceError
        from .native_gate import run_native_gate
        try:
            result = run_native_gate(args.specification, args.output)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return 0 if result["validity"] == "valid" and result["assertion_status"] == "passed" else 2
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"kind": "timelearner_native_gate_error", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    if args.command == "preflight-regression":
        from .native_evidence import EvidenceError
        from .preflight_regression import run_preflight_regression
        try:
            result = run_preflight_regression(args.specification, args.output)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False));return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"kind": "timelearner_preflight_regression_error", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    if args.command in ("train", "preflight", "export", "evaluate", "diagnostic-evaluate", "probe"):
        from .native_evidence import EvidenceError, require
        from .native_pipeline_worker import run_job
        try:
            if args.command == "probe":
                from .native_evidence import load
                require((args.source_solo is None) == (load(args.specification)['schema_version'] == 1), 'probe_source_required_only_for_import')
            else:
                require((args.source_solo is None) == (args.command in ("train", "preflight")), "pipeline_source_required_only_for_export_evaluate")
            result = run_job(args.command, args.specification, args.source_solo, args.runtime_manifest, args.output, args.wall_seconds,
                             process_policy=_process_policy(args))
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return 0 if result["execution"] == "completed" and result["validity"] == "valid" else 2
        except (EvidenceError, OSError, ValueError) as error:
            print(json.dumps({"kind": "timelearner_native_pipeline_error", "operation": args.command,
                              "validity": "invalid", "reason": str(error), "evaluation_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "inventory":
        import subprocess
        from .native_evidence import EvidenceError
        from .inventory import write_inventory
        try:
            write_inventory(args.root.resolve(), args.output.resolve(), args.revision, include_related=args.include_related)
        except (EvidenceError, OSError, ValueError, subprocess.SubprocessError) as error:
            print(json.dumps({'kind': 'timelearner_inventory_error', 'reason': str(error),
                              'scientific_verdict': None}), file=sys.stderr)
            return 2
    elif args.command == "history":
        from .history import resolve_revision
        from .native_evidence import EvidenceError, require
        try:
            if args.action == "resolve":
                require(args.bin_repository is None and args.pulselib_repository is None and args.output is None,
                        "migration_options_require_verify_migration")
                result = resolve_revision(args.root, args.revision, args.map)
            else:
                from .migration import verify_migration
                require(args.output is not None, "migration_receipt_output_required")
                result = verify_migration(args.root, args.revision, args.bin_repository, args.pulselib_repository, args.map)
                with args.output.open("x", encoding="utf-8", newline="\n") as output:
                    json.dump(result, output, ensure_ascii=False, indent=2, allow_nan=False);output.write("\n")
            print(json.dumps(result, ensure_ascii=False))
            return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            kind = "nmsdk_root_revision_resolution" if args.action == "resolve" else "timelearner_script_migration_verification"
            print(json.dumps({"kind":kind,"status":"invalid","reason":str(error),"scientific_verdict":None}),file=sys.stderr)
            return 2
    elif args.command == "bundle":
        from .artifact_bundle import pack_native_tests, verify_bundle, extract_bundle
        from .native_evidence import EvidenceError, require
        import tarfile
        try:
            require(args.maximum_bytes > 0, "invalid_extraction_budget")
            if args.action == "pack-native-tests":
                require(args.artifacts is not None and args.selected_report is not None and args.output is not None,
                        "native_bundle_requires_artifacts_selected_report_and_output")
                result = pack_native_tests(args.source.resolve(strict=True), args.artifacts.resolve(strict=True),
                                          args.output.resolve(), args.selected_report.resolve(strict=True), args.maximum_bytes)
            else:
                require(args.artifacts is None and args.selected_report is None, "unexpected_bundle_source_options")
                if args.action == "extract":
                    require(args.output is not None, "bundle_extraction_requires_output")
                    result = extract_bundle(args.source.resolve(strict=True), args.output.resolve(), args.maximum_bytes)
                else:
                    require(args.output is None, "bundle_verification_has_no_output")
                    value = verify_bundle(args.source.resolve(strict=True), args.maximum_bytes)
                    result = {"kind": "timelearner_primary_bundle_verification", "files": len(value["files"]),
                              "archive_sha256": value["archive"]["sha256"], "scientific_verdict": None}
            print(json.dumps(result, ensure_ascii=False)); return 0
        except (EvidenceError, OSError, ValueError, tarfile.TarError, EOFError) as error:
            print(json.dumps({"kind": "timelearner_primary_artifact_bundle", "status": "invalid",
                              "reason": str(error), "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "calibrate":
        from .native_evidence import EvidenceError, load, require
        from .learned_evidence import load_case
        from .calibration import select_threshold, confirm_threshold
        from .calibration_io import load_measurements
        try:
            if args.action == "run":
                from .native_calibration_worker import run_job
                require(args.runtime_manifest is not None and args.wall_seconds is not None and
                        args.measurements is None and args.selection is None and args.confirmation is None,
                        "native_calibration_requires_runtime_wall_budget_and_no_saved_measurements")
                result = run_job(args.specification, args.source_solo, args.runtime_manifest, args.output, args.wall_seconds,
                                 process_policy=_process_policy(args))
                print(json.dumps(result, ensure_ascii=False, allow_nan=False))
                return 0 if result["execution"] == "completed" and result["validity"] == "valid" else 2
            require(args.runtime_manifest is None and args.wall_seconds is None and args.process_policy is None and args.measurements is not None,
                    "saved_calibration_requires_measurements_and_no_runtime")
            require(args.action == "confirm" or (args.selection is None and args.confirmation is None),
                    "selection_does_not_accept_confirmation_options")
            spec = load(args.specification.resolve(strict=True))
            measurements = load_measurements(args.measurements)
            source = load_case(args.source_solo.resolve(strict=True))
            if args.action == "select":
                result = select_threshold(spec, measurements, source)
            else:
                require(args.selection is not None and args.confirmation is not None,
                        "calibration_confirmation_requires_selection_and_fresh_measurement")
                fresh = load_measurements(args.confirmation)
                require(len(fresh) == 1, "calibration_confirmation_requires_one_measurement")
                result = confirm_threshold(spec, measurements, source, load(args.selection.resolve(strict=True)), fresh[0])
            with args.output.open("x", encoding="utf-8") as output:
                json.dump(result, output, ensure_ascii=False, indent=2, allow_nan=False)
                output.write("\n")
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return 0
        except (EvidenceError, OSError, ValueError) as error:
            print(json.dumps({"kind": "timelearner_calibration_analysis_error", "validity": "invalid",
                              "reason": str(error), "calibrated": False, "evaluation_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "publish-recover":
        from .native_evidence import EvidenceError
        from .publisher import recover_publication_lock
        try:
            with args.output.open("x", encoding="utf-8") as receipt:
                result = recover_publication_lock(args.root)
                json.dump(result, receipt, ensure_ascii=False, indent=2, allow_nan=False)
                receipt.write("\n")
            print(json.dumps(result, ensure_ascii=False))
            return 0
        except (EvidenceError, OSError, ValueError) as error:
            print(json.dumps({"kind": "timelearner_publication_lock_recovery", "recovery": "refused",
                              "reason": str(error), "publication": "not_attempted",
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "publish":
        from .native_evidence import EvidenceError, load
        from .publisher import publish_closure
        try:
            # Reserve the receipt before any push; never overwrite an old result.
            with args.output.open("x", encoding="utf-8") as receipt:
                result = publish_closure(args.root, load(args.specification))
                json.dump(result, receipt, ensure_ascii=False, indent=2, allow_nan=False)
                receipt.write("\n")
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result["publication"] == "published" else 2
        except (EvidenceError, OSError, ValueError) as error:
            print(json.dumps({"kind": "timelearner_git_publication_result", "publication": "failed",
                              "reason": str(error), "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "report":
        from .native_evidence import EvidenceError
        from .reports import render_evaluation
        try:
            from .native_evidence import require
            require(args.format in ("native-test-run", "dataset-clock") or args.artifacts is None, "artifacts_option_is_only_for_native_test_run")
            require(args.format == "posttune-transaction" or args.source_solo is None, "report_source_solo_is_only_for_posttune")
            require(args.format == "native-live-finalization" or args.primary_inventory is None,
                    "primary_inventory_is_only_for_live_finalization")
            if args.format == "native-live-finalization":
                from .live_finalization_reports import render_live_finalization
                require(args.primary_inventory is not None and args.trace is None and args.model is None,
                        "live_report_requires_primary_inventory_and_no_model_or_trace_overlay")
                result = render_live_finalization(args.source.resolve(strict=True), args.primary_inventory.resolve(strict=True), args.output.resolve())
            elif args.format == "pipeline-run":
                from .live_pipeline_reports import render_pipeline_run
                require(args.trace is None and args.model is None and args.source_solo is None and args.artifacts is None,
                        "pipeline_report_declares_its_own_primary_closure")
                result = render_pipeline_run(args.source.resolve(strict=True), args.output.resolve())
            elif args.format == "posttune-run":
                from .posttune_transaction_reports import render_posttune_run
                require(args.trace is None and args.model is None, "posttune_run_declares_its_models_and_observations")
                result = render_posttune_run(args.source.resolve(strict=True), args.output.resolve())
            elif args.format == "posttune-transaction":
                from .posttune_transaction_reports import render_posttune_transaction
                require(args.source_solo is not None and args.trace is None and args.model is None,
                        "posttune_report_requires_source_solo_not_model_or_trace")
                result = render_posttune_transaction(args.source.resolve(strict=True),
                    args.source_solo.resolve(strict=True), args.output.resolve())
            elif args.format == "dataset-clock":
                from .dataset_clock_reports import render_dataset_clock_report
                require(args.artifacts is not None and args.trace is None and args.model is None,
                        "dataset_clock_report_requires_artifacts_not_model_or_trace")
                result = render_dataset_clock_report(args.source.resolve(strict=True), args.artifacts.resolve(strict=True), args.output.resolve())
            elif args.format == "native-test-run":
                from .native_test_reports import render_native_test_run
                require(args.artifacts is not None and args.trace is None and args.model is None,
                        "native_test_run_requires_artifacts_not_model_or_trace")
                result = render_native_test_run(args.source.resolve(strict=True), args.artifacts.resolve(strict=True), args.output.resolve())
            elif args.format in ("calibration-transaction", "calibration-run"):
                from .calibration_transaction_reports import render_calibration_transaction, render_calibration_run
                require(args.trace is None and args.model is None, "calibration_transaction_declares_its_models_and_observations")
                renderer = render_calibration_run if args.format == "calibration-run" else render_calibration_transaction
                result = renderer(args.source.resolve(strict=True), args.output.resolve())
            elif args.format == "capacitance-search":
                from .capacitance_search_reports import render_capacitance_search
                require(args.trace is None and args.model is None and args.artifacts is None,
                        "capacitance_search_report_declares_its_own_primary_files")
                result = render_capacitance_search(args.source.resolve(strict=True), args.output.resolve())
            elif args.format == "capacitance-region":
                from .capacitance_region_reports import render_capacitance_region
                require(args.trace is None and args.model is None and args.artifacts is None,
                        "capacitance_region_report_declares_its_own_primary_files")
                result = render_capacitance_region(args.source.resolve(strict=True), args.output.resolve())
            elif args.format == "probe-set":
                from .probe_reports import render_probe_set
                require(args.trace is None and args.model is None, "probe_set_declares_its_own_primary_files")
                result = render_probe_set(args.source.resolve(strict=True), args.output.resolve())
            elif args.format == "recognition-transport":
                from .recognition_transport_reports import render_transport
                require(args.trace is None and args.model is None, "transport_report_declares_its_models_and_traces")
                result = render_transport(args.source.resolve(strict=True), args.output.resolve())
            elif args.format == "legacy-posttune-freerun":
                from .legacy_posttune_reports import render_free_run
                require(args.trace is not None and args.model is None, "legacy_posttune_report_requires_trace_not_model")
                result = render_free_run(args.source.resolve(strict=True), args.trace.resolve(strict=True), args.output.resolve())
            elif args.format in ("probe", "probe-diagnostic"):
                from .probe_reports import render_probe
                require(args.trace is not None and args.model is None, "probe_report_requires_trace_not_model")
                result = render_probe(args.source.resolve(strict=True), args.trace.resolve(strict=True), args.output.resolve(),
                                      allow_incomplete=args.format=="probe-diagnostic")
            else:
                require(args.model is not None and args.trace is None, "recognition_report_requires_model_not_trace")
                result = render_evaluation(args.source.resolve(strict=True), args.model.resolve(strict=True), args.output.resolve(),
                                           calibration_probe=args.format == "threshold-candidate-evaluation")
            print(json.dumps(result, ensure_ascii=False))
        except (EvidenceError, OSError, ValueError, ImportError) as error:
            print(json.dumps({"kind": "timelearner_visual_report", "status": "incomplete",
                              "reason": str(error), "evaluation_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "model-spec-transport":
        from .model_spec_transport import prepare, run
        from .native_evidence import EvidenceError, require
        try:
            if args.action == "prepare":
                require(args.runtime_manifest is None and args.completed_prefix is None, "transport_prepare_does_not_execute_runtime")
                result = prepare(args.source.resolve(strict=True), args.output.resolve())
            else:
                require(args.runtime_manifest is not None, "transport_runtime_required")
                result = run(args.source.resolve(strict=True), args.runtime_manifest.resolve(strict=True), args.output.resolve(),
                             completed_prefix=args.completed_prefix.resolve(strict=True) if args.completed_prefix is not None else None)
            print(json.dumps(result, allow_nan=False));return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "stock-stopped-evaluation":
        from .stock_stopped_evaluation import prepare, run, audit, report
        from .native_evidence import EvidenceError, require
        try:
            if args.action in ("analyze", "report"):
                require(args.bin_repository is None, "stock_diagnostic_analysis_uses_bound_matrix")
                if args.action == "report":
                    result = report(args.source, args.output)
                else:
                    result = audit(args.source)
                    with args.output.open("x", encoding="utf-8") as stream:
                        json.dump(result, stream, indent=2, allow_nan=False);stream.write("\n")
            else:
                require(args.bin_repository is not None, "stock_diagnostic_bin_repository_required")
                result = (prepare if args.action == "prepare" else run)(args.source, args.bin_repository, args.output)
            print(json.dumps(result, allow_nan=False));return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "phasea-matrix":
        from .phasea_matrix import from_git
        from .native_evidence import EvidenceError
        try:
            result = from_git(args.bin_repository, args.revision)
            raw = (json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)+"\n").encode("utf-8")
            with args.output.open("xb") as stream:
                stream.write(raw)
            print(json.dumps({"pattern_matrix_sha256": result["pattern_matrix_sha256"], "patterns": len(result["patterns"]),
                              "historical_presentation_reproduced": False, "scientific_verdict": None}))
            return 0
        except (EvidenceError, OSError, ValueError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "stock-threshold-study":
        from .stock_threshold_study import prepare, run, audit
        from .native_evidence import EvidenceError, require, load
        try:
            if args.action in ("analyze", "failure-report"):
                require(args.runtime_manifest is None and args.code_identity is None, "stock_pair_analysis_has_no_runtime")
                if args.action == "failure-report":
                    from .stock_failure_reports import render_failure_report
                    result = render_failure_report(args.source, args.output)
                else:
                    result = audit(args.source)
                    with args.output.open("x", encoding="utf-8") as stream:
                        json.dump(result, stream, indent=2, allow_nan=False);stream.write("\n")
            else:
                require(args.runtime_manifest is not None and args.code_identity is not None, "stock_pair_runtime_and_code_required")
                result = (prepare if args.action == "prepare" else run)(args.source, args.runtime_manifest,
                          load(args.code_identity), args.output)
            print(json.dumps(result, allow_nan=False));return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "stock-phasea-preflight":
        import tarfile
        from .stock_phasea_preflight import run_stock_preflight
        from .native_evidence import EvidenceError
        try:
            print(json.dumps(run_stock_preflight(args.source, args.runtime_manifest, args.output,
                             initial_threshold=args.initial_threshold), allow_nan=False))
            return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError, tarfile.TarError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error),
                              "training_started": False, "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "n1-protocol-study":
        import tarfile
        from .n1_protocol_robustness import prepare_study, run_study, audit_study
        from .native_evidence import EvidenceError, require
        try:
            if args.action in {"analyze", "report"}:
                require(args.runtime_manifest is None and args.source_evidence is None, "n1_study_analyze_has_no_runtime")
                if args.action == "report":
                    from .n1_protocol_reports import render_study
                    result = render_study(args.source, args.output)
                else:
                    result = audit_study(args.source)
                    with args.output.open("x", encoding="utf-8") as stream:
                        json.dump(result, stream, indent=2, allow_nan=False)
                        stream.write("\n")
            else:
                require(args.runtime_manifest is not None and args.source_evidence is not None, "n1_study_requires_runtime_and_source")
                result = (prepare_study if args.action == "prepare" else run_study)(
                    args.source, args.runtime_manifest, args.output, args.source_evidence)
            print(json.dumps(result, allow_nan=False)); return 0
        except (EvidenceError, OSError, ValueError, KeyError, TypeError, tarfile.TarError) as error:
            print(json.dumps({"execution": "failed", "validity": "unverified", "reason": str(error),
                              "scientific_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "analyze":
        from .native_evidence import EvidenceError
        try:
            result = analyze(args)
            text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
            if args.output is None:
                print(text, end="")
            else:
                with args.output.open("x", encoding="utf-8") as output:
                    output.write(text)
            if result["validity"] == "invalid":
                return 2
        except (EvidenceError, ValueError, csv.Error) as error:
            print(json.dumps({"kind": "timelearner_analysis", "schema_version": 1,
                              "execution": "completed", "validity": "invalid", "reason": str(error),
                              "evaluation_verdict": None}, ensure_ascii=False), file=sys.stderr)
            return 2
        except OSError as error:
            print(json.dumps({"kind": "timelearner_analysis", "schema_version": 1,
                              "execution": "process_error", "validity": "unknown", "reason": str(error),
                              "evaluation_verdict": None}, ensure_ascii=False), file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
