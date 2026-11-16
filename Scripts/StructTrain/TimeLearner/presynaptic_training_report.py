"""Read-only Stock/PSI cold comparison with verified effective image physics."""
import argparse
from copy import deepcopy
import html
from pathlib import Path

from .candidate_window_binding_evidence import reference_seed
from .composite_training_temporal import render
from .native_calibration_worker import _write
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest
from .presynaptic_storage_study import CLASSES, compare_stock_and_psi
from .runtime import file_record
from .uniform_profile_physics import audit_uniform_profile


def _case(native, role):
    native = Path(native).resolve(strict=True)
    manifest_path = native.parent/"run-manifest.json"
    audit = audit_run_manifest(manifest_path)
    manifest = load(manifest_path)
    require(audit["run_evidence_consistent"] and manifest["operation"] == "train" and
            manifest["execution"] == "completed" and manifest["validity"] == "valid",
            "psi_report_requires_completed_valid_execution:"+role)
    paths = [native/name for name in ("train_stopped_state.json", "train_learned_state.json")
             if (native/name).is_file()]
    require(len(paths) == 1, "psi_report_terminal_package:"+role)
    path = paths[0]
    summary_path = path.with_name(path.name.replace("_state.", "_summary."))
    package, summary = load(path), load(summary_path)
    configuration = package["configuration"]
    model = configuration["model"]
    require(model["neuron_class"] == CLASSES[role] and model["branch"] is True and
            model["normalization"] == "N1" and len(model["inputs"]) == 4 and
            package["reference_complete"], "psi_report_unsupported_condition:"+role)
    source = package["measurement_archive"]["source_binding"]
    records = package["measurement_archive"]["records"]
    references = [r for r in records if r["purpose"] == "reference"]
    references.sort(key=lambda r: r["logical_request"]["input_index"])
    require(len(references) == 4 and
            [r["logical_request"]["input_index"] for r in references] == list(range(4)),
            "psi_report_reference_inventory:"+role)
    configuration = deepcopy(configuration)
    configuration.pop("run_id")
    configuration["model"].pop("neuron_class")
    seeds = []
    for reference, policy in zip(references,
            configuration["composite_measurement"]["candidate_window_policy"]["inputs"]):
        seed = reference_seed(reference, source, package["protocol"])
        require(seed["frame_count"] == 3601 and policy["hard_first_frame"] == 0 and
                policy["hard_last_frame"] == 3600 and policy["maximum_window_frames"] == 3601 and
                all(policy[k] == 0 for k in ("delay_frames_per_segment", "length_guard_frames",
                    "synapse_count_guard_frames", "resistance_change_guard_frames",
                    "capacitance_change_guard_frames")) and
                seed["first_frame"]-policy["base_left_guard_frames"] == 0 and
                seed["last_frame"]+policy["base_right_guard_frames"] == 3600,
                "psi_report_effective_window_changed:"+role)
        seeds.append({k: seed[k] for k in ("first_frame", "last_frame", "frame_count")})
        policy.pop("base_left_guard_frames")
        policy.pop("base_right_guard_frames")
    require(all(r["method_specification"]["candidate_frame"] ==
                dict(first_frame=0, last_frame=3600)
                for r in records if r["purpose"] != "reference" and
                r["method_specification"] is not None), "psi_report_actual_window_changed:"+role)
    ordinal = {r["group_id"]: i for i, r in enumerate(records, 1)}
    selected = [ordinal[summary["reference_group_ids"][-1]]]
    candidates, tolerance = summary["candidates"], summary["tolerances"]

    def rank(candidate):
        timing = max(abs(candidate["timing_low"]), abs(candidate["timing_high"]))/tolerance["sync"]
        amplitude = abs(candidate["amplitude_residual"])/tolerance["amplitude_absolute"]
        return (not candidate["within_timing"], not candidate["within_amplitude"], timing+amplitude)

    best = {str(i): min((c for c in candidates if c["input_index"] == i), key=rank)
            for i in sorted({c["input_index"] for c in candidates})}
    selected.extend(ordinal[c["measurement_group_id"]] for c in best.values())
    rejected = [r for r in records if r["purpose"] != "reference" and r["measurement"] is None]
    selected.extend(ordinal[r["group_id"]] for r in rejected)
    selected.append(len(records))
    facts = {k: summary[k] for k in ("outcome", "reason", "certificate", "references",
        "reference_complete", "actual_parameters", "accepted_parameters", "search_probes",
        "applied_edits", "composite_counters", "rejections", "resistance_domains")}
    facts.update(all_scalar_candidates=candidates, selected_measured_by_input=best,
        selected_groups=list(dict.fromkeys(selected)), all_rejected_groups_selected=True,
        report_rank="outside timing, outside amplitude, normalized sum, first observed tie; diagnostic selection only",
        reference_seeds=seeds, physical_audit=audit_uniform_profile(
            source["initial_model"], package["neuron"]["graph"]["identity"]),
        classification_assessed=False, scientific_verdict=None)
    return dict(native=native, configuration=configuration, facts=facts,
        initial=source["initial_model"], runtime={k: manifest[k] for k in
            ("runtime_fingerprint", "source_closure")},
        bindings={str(p): file_record(p) for p in (manifest_path, path, summary_path)})


def compare(stock_native, psi_native, output):
    output = Path(output).resolve()
    cases = {role: _case(native, role) for role, native in
             (("stock", stock_native), ("psi", psi_native))}
    require(not output.exists() and all(not output.is_relative_to(c["native"]) and
            not c["native"].is_relative_to(output) for c in cases.values()),
            "psi_report_output_exists_or_overlap")
    require(cases["stock"]["configuration"] == cases["psi"]["configuration"] and
            cases["stock"]["runtime"] == cases["psi"]["runtime"],
            "psi_report_undeclared_scientific_factor")
    factor = compare_stock_and_psi(cases["stock"]["initial"], cases["psi"]["initial"])
    output.mkdir(parents=True)
    rows = {}
    for role, case in cases.items():
        report = render(case["native"], output/role, case["facts"]["selected_groups"],
                        native_window_zooms=True, native_response_zooms=True,
                        allow_incomplete_groups=True)
        require(case["bindings"] == {path: file_record(Path(path)) for path in case["bindings"]},
                "psi_report_source_changed:"+role)
        rows[role] = dict(facts=case["facts"], report=report, bindings=case["bindings"])
    result = dict(kind="timelearner_native_psi_cold_comparison", schema_version=1,
        common_configuration=cases["stock"]["configuration"], runtime=cases["stock"]["runtime"],
        effective_image_factor=factor, derived_guards_profile_specific=True,
        effective_full_window_frames=[0, 3600], rows=rows,
        source_setup_failure_excluded=True, new_model_execution=False,
        classification_assessed=False, scientific_verdict=None)
    _write(output/"comparison.json", result)
    links = "".join('<li><a href="'+html.escape(role)+'/index.html">'+role+'</a></li>' for role in cases)
    (output/"index.html").write_text('<!doctype html><meta charset="utf-8"><h1>Cold Stock / PSI2.5</h1>'
        '<p>Audited native images, equal effective full windows and unchanged search conditions. '
        'All recorded rejections retained. Response-maximum zooms are diagnostic axes; '
        'they do not replace assigned-impulse training measurements. No classifier verdict.</p><ul>'+links+'</ul>')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stock_native", type=Path)
    parser.add_argument("psi_native", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    compare(args.stock_native, args.psi_native, args.output)


if __name__ == "__main__":
    main()
