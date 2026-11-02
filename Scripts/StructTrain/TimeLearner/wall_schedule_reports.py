"""Audit the declared native scheduling-policy controls and raw Reset traces.

No classification verdict or synthetic closed probe is constructed here.
"""
import hashlib
import json
import math
from pathlib import Path

from .native_evidence import load, require
from .native_test_reports import inventory_native_test_run
from .plotting import padded_limits, plotting_runtime, time_views


SPEC = Path(__file__).parent/"specs/native-wall-schedule-v1.json"
REASON = "unsupported_native_wall_limited_schedule"


def _read(root, name, kind):
    path = root/name
    require(path.is_file() and not path.is_symlink(), "wall_missing_regular_artifact:"+name)
    row = load(path)
    require(row.get("kind") == kind and row.get("schema_version") == 1, "wall_unknown_schema:"+name)
    return row


def inventory_wall_schedule(root):
    root = Path(root).resolve(strict=True)
    inventory = inventory_native_test_run(SPEC, root)
    native = root/"native"
    resets = []
    expected_resets = set()
    for topology in ("Classic", "Branch"):
        channels = 2 if topology == "Classic" else 1
        for n in (0, 1):
            prefix = f"{topology}_2000_N{n}"
            for location in ("owner", "ancestor", "neuron", "generator"):
                for limit in (0, 1000000000):
                    row = _read(native, f"{prefix}_wall_limit_{location}_{limit}_wall_policy.json",
                                "native_wall_schedule_policy")
                    require(row["location"] == location and row["configured_limit"] == limit
                            and row["effective_limit_after_probe"] == limit and row["observed_samples"] == 0
                            and row["status"] == "rejected" and REASON in row["reasons"]
                            and row["changed_individual_parameters"] is False, "wall_fresh_control_mismatch")
                row = _read(native, f"{prefix}_wall_begin_{location}_wall_begin_policy.json",
                            "native_wall_before_training")
                require(row["location"] == location and row["reason"] == REASON
                        and row["started_reference_probes"] == 0 and row["certificate_before_reset"] is False
                        and row["state_before_reset"] == "finished" and row["outcome_before_reset"] == "invalid_model"
                        and row["reset_build_preserved_parameters"] is True
                        and row["build_with_limited_owner"] is (location in ("owner", "ancestor")),
                        "wall_begin_control_mismatch")
            for mode in ("mid", "final"):
                row = _read(native, f"{prefix}_wall_live_{mode}_live_wall_policy.json", "native_live_wall_policy")
                require(row["changed_on_final_sample"] is (mode == "final") and row["valid"] is False
                        and row["window_complete"] is (mode == "final") and row["status"] == "rejected"
                        and row["partial_observation_preserved"] is True
                        and row["samples"] == (361 if mode == "final" else 2), "wall_live_control_mismatch")
        for location in ("owner", "generator"):
            row = _read(native, f"{topology}_2000_N1_wall_recognition_{location}_unarmed_recognition.json",
                        "native_recognition_trial")
            require(row["reason"] == REASON and row["armed"] is False and row["complete"] is False
                    and row["valid"] is False and row["samples"] == [], "wall_recognition_control_mismatch")
        row = _read(native, f"{topology}_2000_N1_wall_observation_sink_sink_policy_summary.json",
                    "native_wall_observation_sink_policy")
        require(row["reason"] == REASON and row["outcome"] == "invalid_observation"
                and row["observed_packets"] == 1 and row["certificate"] is False, "wall_sink_control_mismatch")
        for mode in ("mid", "final"):
            name = f"{topology}_2000_N1_wall_callback_reset_{mode}_reset_diagnostic.json"
            expected_resets.add(name)
            row = _read(native, name, "native_probe_explicit_reset_diagnostic")
            samples = row["raw_pre_reset_samples"]
            require(row["control_state"] == "idle" and row["closed_probe_available"] is False
                    and row["reset_on_final_sample"] is (mode == "final")
                    and row["sample_count"] == len(samples) == (361 if mode == "final" else 2),
                    "wall_reset_control_mismatch")
            for i, sample in enumerate(samples):
                values = [sample["time"], sample["stimulus"], *sample["soma"]]
                require(len(sample["soma"]) == channels and all(type(v) in (int, float) and math.isfinite(v) for v in values)
                        and type(sample["observed_revision"]) is str and len(sample["observed_revision"]) == 64,
                        "wall_reset_invalid_sample")
                if i:
                    require(abs(sample["time"]-samples[i-1]["time"]-1/2000) < 1e-10,
                            "wall_reset_sample_clock_mismatch")
            resets.append({"source": name, "sha256": hashlib.sha256((native/name).read_bytes()).hexdigest(),
                           "samples": samples, "channels": channels, "sample_count": len(samples),
                           "frequency_hz": 2000, "frequency_basis": "declared fixture and checked native sample intervals",
                           "closed_probe_available": False, "scientific_verdict": None})
    require({p.name for p in native.glob("*_reset_diagnostic.json")} == expected_resets,
            "wall_missing_or_extra_reset_diagnostic")
    require(inventory["tests"] == 66 and inventory["trials"] == 46
            and inventory["plottable_trial_soma_pairs"] == 21, "wall_declared_coverage_mismatch")
    return {"kind": "native_wall_schedule_report_inventory", "schema_version": 1,
            "native_inventory": inventory, "reset_diagnostics": resets,
            "visual_acceptance_complete": False, "scientific_verdict": None}


def render_reset_diagnostics(root, output):
    """Plot raw callback samples without inventing the result discarded by Reset."""
    root, output = Path(root).resolve(strict=True), Path(output).resolve()
    require(not output.is_relative_to(root), "wall_output_inside_immutable_artifacts")
    inventory = inventory_wall_schedule(root)
    runtime = plotting_runtime()
    import matplotlib.pyplot as plt
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for diagnostic in inventory["reset_diagnostics"]:
        samples = diagnostic["samples"]
        for channel in range(diagnostic["channels"]):
            name = diagnostic["source"].removesuffix(".json")+f"-soma{channel}"
            directory = output/name
            directory.mkdir()
            limits = padded_limits([s["soma"][channel] for s in samples])
            for view, begin, end in time_views(samples[0]["time"], samples[-1]["time"], diagnostic["frequency_hz"]):
                fig, ax = plt.subplots(figsize=(12, 6), dpi=160)
                fig.subplots_adjust(left=.12, right=.86, bottom=.15, top=.70)
                overlay = ax.twinx()
                times = [s["time"] for s in samples]
                ax.plot(times, [s["soma"][channel] for s in samples], color="#154c9a", marker="o", markersize=2,
                        label=f"Soma {channel}: actual native samples")
                overlay.step(times, [s["stimulus"] for s in samples], where="post", color="#d46200", alpha=.65,
                             label="Actual input samples")
                ax.set(xlim=(begin, end), ylim=limits, xlabel="Native absolute time [s]",
                       ylabel="Soma potential [native model units]")
                overlay.set_ylabel("Input [native generator units]")
                ax.grid(alpha=.25)
                fig.suptitle(f"{name}\nExplicit Reset: raw pre-reset samples only; closed probe discarded\n"
                             f"{view}; no validity, spike detection or classification inferred", fontsize=11)
                handles, labels = ax.get_legend_handles_labels()
                h2, l2 = overlay.get_legend_handles_labels()
                fig.legend(handles+h2, labels+l2, loc="upper center", bbox_to_anchor=(.5, .83), frameon=False)
                file = directory/(view+".png")
                fig.savefig(file)
                plt.close(fig)
                rows.append({"source": diagnostic["source"], "source_sha256": diagnostic["sha256"],
                             "channel": channel, "view": view, "begin": begin, "end": end,
                             "file": str(file.relative_to(output)), "downsampling": False,
                             "planned_window": None, "closed_probe_available": False,
                             "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    result = {"kind": "native_wall_reset_raw_report", "schema_version": 1, "runtime": runtime,
              "plots": rows, "visual_acceptance_complete": False, "scientific_verdict": None}
    (output/"index.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    return result
