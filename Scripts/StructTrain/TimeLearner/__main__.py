"""Explicit CLI entry point; commands have no import-time side effects."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def analyze(args: argparse.Namespace) -> dict:
    from .native_evidence import EvidenceError, audit_probe, load, require
    require(args.format == "domain" or not args.allow_legacy, "legacy_adapter_is_only_for_domains")
    require(args.format in ("probe", "legacy-posttune-freerun") or args.trace is None, "trace_option_is_only_for_probes")
    require(args.format in ("recognition-trial", "recognition-evaluation", "native-calibration-assessment") or args.model is None, "model_option_is_only_for_recognition_trials")
    require(args.format in ("threshold-candidate", "native-calibration-assessment", "calibrated-state", "calibration-transaction") or args.source_solo is None, "source_solo_option_is_only_for_threshold_candidates")
    require(args.format == "native-calibration-assessment" or args.evaluation is None, "evaluation_option_is_only_for_native_calibration")
    source = args.source.resolve(strict=True)
    if args.format == "native-calibration-assessment":
        from .native_calibration_evidence import audit_native_calibration_assessment
        from .recognition_metrics import load_evaluation
        from .learned_evidence import load_case
        require(args.model is not None and args.evaluation is not None and args.source_solo is not None,
                "native_calibration_requires_model_evaluation_and_source_evidence")
        spec, observations = load_evaluation(args.evaluation.resolve(strict=True))
        result = audit_native_calibration_assessment(load(source), spec, observations,
            load(args.model.resolve(strict=True)), load_case(args.source_solo.resolve(strict=True)))
    elif args.format == "domain":
        from .domain_evidence import audit_resistance_domain
        result = audit_resistance_domain(load(source), allow_legacy=args.allow_legacy)
    elif args.format == "learned-solo":
        from .learned_evidence import audit_learned_state, load_case
        result = audit_learned_state(*load_case(source))
    elif args.format == "stopped-solo":
        from .stopped_evidence import audit_stopped_state, load_case
        result = audit_stopped_state(*load_case(source))
    elif args.format == "recognition-evaluation":
        from .recognition_metrics import load_evaluation, score_recognition_evaluation
        require(args.model is not None, "recognition_model_package_required")
        result = score_recognition_evaluation(*load_evaluation(source), load(args.model.resolve(strict=True)))
    elif args.format == "calibration-run":
        from .native_calibration_worker import audit_run_manifest
        result = audit_run_manifest(source)
    elif args.format == "pipeline-run":
        from .native_pipeline_worker import audit_run_manifest
        result = audit_run_manifest(source)
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TimeLearner reproducible experiment tools")
    commands = parser.add_subparsers(dest="command", required=True)
    for operation in ("train", "export", "evaluate"):
        native = commands.add_parser(operation, help="run an owned native Console "+operation+" job")
        native.add_argument("specification", type=Path)
        native.add_argument("--source-solo", type=Path, help="completed source package with primary trial siblings; export/evaluate only")
        native.add_argument("--runtime-manifest", type=Path, required=True)
        native.add_argument("--wall-seconds", type=float, required=True)
        native.add_argument("--output", type=Path, required=True, help="new immutable result directory")
    inventory = commands.add_parser("inventory", help="inventory source properties and tracked historical tools")
    inventory.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    inventory.add_argument("--output", type=Path, required=True)
    analysis = commands.add_parser("analyze", help="audit original native evidence; no recognition verdict")
    analysis.add_argument("source", type=Path)
    analysis.add_argument("--format", choices=("domain", "probe", "learned-solo", "stopped-solo", "recognition", "recognition-owner", "recognition-trial", "recognition-evaluation", "threshold-candidate", "calibrated-state", "calibration-transaction", "calibration-run", "pipeline-run", "native-calibration-assessment", "posttune-reconstruction", "posttune-transient", "legacy-posttune-freerun"), required=True)
    analysis.add_argument("--model", type=Path, help="recognition package required for recognition trial/evaluation")
    analysis.add_argument("--source-solo", type=Path, help="original learned-state package with primary trial siblings, required for threshold candidate")
    analysis.add_argument("--evaluation", type=Path, help="independently declared evaluation spec required for native calibration assessment")
    analysis.add_argument("--trace", type=Path, help="original primary CSV, required for probe")
    analysis.add_argument("--allow-legacy", action="store_true", help="descriptive domain schema-1 adapter only")
    analysis.add_argument("--output", type=Path, help="new output file; an existing file is never replaced")
    report = commands.add_parser("report", help="large native soma/input diagnostic figures with portable primary data")
    report.add_argument("source", type=Path, help="recognition evaluation spec")
    report.add_argument("--format", choices=("recognition-evaluation", "recognition-transport", "threshold-candidate-evaluation", "probe", "probe-diagnostic", "legacy-posttune-freerun", "probe-set", "native-test-run", "calibration-transaction", "calibration-run"), default="recognition-evaluation")
    report.add_argument("--artifacts", type=Path, help="native-test-run directory containing native.xml and native/")
    report.add_argument("--model", type=Path)
    report.add_argument("--trace", type=Path, help="primary CSV required for probe report")
    report.add_argument("--output", type=Path, required=True, help="new directory; never overwritten")
    publication = commands.add_parser("publish", help="publish exact Git closure children-first; no scientific verdict")
    publication.add_argument("specification", type=Path)
    publication.add_argument("--root", type=Path, required=True)
    publication.add_argument("--output", type=Path, required=True, help="new receipt outside source tree")
    calibration = commands.add_parser("calibrate", help="run a native Console calibration job or select/confirm from saved primary measurements")
    calibration.add_argument("action", choices=("run", "select", "confirm"))
    calibration.add_argument("specification", type=Path)
    calibration.add_argument("--measurements", type=Path, help="portable search measurement-set descriptor for select/confirm")
    calibration.add_argument("--runtime-manifest", type=Path, help="verified Console runtime required for run")
    calibration.add_argument("--wall-seconds", type=float, help="owned process wall budget required for run")
    calibration.add_argument("--source-solo", type=Path, required=True, help="original learned-state package with primary trial siblings")
    calibration.add_argument("--selection", type=Path, help="required for confirmation; recomputed against primary search evidence")
    calibration.add_argument("--confirmation", type=Path, help="one fresh measurement-set descriptor required for confirmation")
    calibration.add_argument("--output", type=Path, required=True, help="new result file; never overwritten")
    bundle = commands.add_parser("bundle", help="lossless primary archives; full plots remain in worker cache")
    bundle.add_argument("action", choices=("pack-native-tests", "verify", "extract"))
    bundle.add_argument("source", type=Path, help="native contract for pack; bundle directory otherwise")
    bundle.add_argument("--artifacts", type=Path)
    bundle.add_argument("--selected-report", type=Path, help="completed full native report with checked PDF previews")
    bundle.add_argument("--output", type=Path, help="new bundle or extraction directory")
    bundle.add_argument("--maximum-bytes", type=int, default=8*1024**3, help="maximum uncompressed extraction bytes")
    history = commands.add_parser("history", help="resolve historical root SHA after generated-report cleanup")
    history.add_argument("action", choices=("resolve",))
    history.add_argument("revision")
    history.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    history.add_argument("--map", type=Path)
    args = parser.parse_args(argv)
    if args.command in ("train", "export", "evaluate"):
        from .native_evidence import EvidenceError, require
        from .native_pipeline_worker import run_job
        try:
            require((args.source_solo is None) == (args.command == "train"), "pipeline_source_required_only_for_export_evaluate")
            result = run_job(args.command, args.specification, args.source_solo, args.runtime_manifest, args.output, args.wall_seconds)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return 0 if result["execution"] == "completed" and result["validity"] == "valid" else 2
        except (EvidenceError, OSError, ValueError) as error:
            print(json.dumps({"kind": "timelearner_native_pipeline_error", "operation": args.command,
                              "validity": "invalid", "reason": str(error), "evaluation_verdict": None}), file=sys.stderr)
            return 2
    elif args.command == "inventory":
        from .inventory import write_inventory
        write_inventory(args.root.resolve(), args.output.resolve())
    elif args.command == "history":
        from .history import resolve_revision
        from .native_evidence import EvidenceError
        try:
            print(json.dumps(resolve_revision(args.root, args.revision, args.map), ensure_ascii=False))
            return 0
        except (EvidenceError, OSError, ValueError) as error:
            print(json.dumps({"kind":"nmsdk_root_revision_resolution","status":"invalid","reason":str(error),"scientific_verdict":None}),file=sys.stderr)
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
                result = run_job(args.specification, args.source_solo, args.runtime_manifest, args.output, args.wall_seconds)
                print(json.dumps(result, ensure_ascii=False, allow_nan=False))
                return 0 if result["execution"] == "completed" and result["validity"] == "valid" else 2
            require(args.runtime_manifest is None and args.wall_seconds is None and args.measurements is not None,
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
            require(args.format == "native-test-run" or args.artifacts is None, "artifacts_option_is_only_for_native_test_run")
            if args.format == "native-test-run":
                from .native_test_reports import render_native_test_run
                require(args.artifacts is not None and args.trace is None and args.model is None,
                        "native_test_run_requires_artifacts_not_model_or_trace")
                result = render_native_test_run(args.source.resolve(strict=True), args.artifacts.resolve(strict=True), args.output.resolve())
            elif args.format in ("calibration-transaction", "calibration-run"):
                from .calibration_transaction_reports import render_calibration_transaction, render_calibration_run
                require(args.trace is None and args.model is None, "calibration_transaction_declares_its_models_and_observations")
                renderer = render_calibration_run if args.format == "calibration-run" else render_calibration_transaction
                result = renderer(args.source.resolve(strict=True), args.output.resolve())
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
        except (EvidenceError, ValueError) as error:
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
