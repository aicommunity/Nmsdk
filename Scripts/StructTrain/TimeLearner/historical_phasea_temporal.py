"""Explicit historical Phase A trace reader; never upgrades legacy CSV verdicts."""
import argparse
import bisect
import hashlib
import json
import math
from pathlib import Path

from .historical_selectivity import analyze_historical_csv
from .native_evidence import require
from .plotting import plotting_runtime, padded_limits


def read_stream(path, width, expected_sha):
    before = path.stat()
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected_sha, "historical_trace_hash_mismatch")
    times, values = [], []
    for index, line in enumerate(raw.decode("utf-8").splitlines()):
        fields = line.split()
        require(len(fields) == width+2, "historical_trace_width")
        require(fields[0].isdigit() and int(fields[0]) == index, "historical_trace_index")
        numbers = [float(token) for token in fields[1:]]
        require(all(math.isfinite(v) for v in numbers), "historical_trace_nonfinite")
        # Clock validation, not an algorithm convergence tolerance.
        require(abs(numbers[0]-index/2000) < 1e-9, "historical_trace_clock")
        times.append(numbers[0]); values.append(numbers[1:])
    after = path.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
            "historical_trace_changed_during_read")
    require(len(times) == 80000, "historical_trace_incomplete_40s")
    return times, values


def rising_edges(values):
    require(all(row[0] >= 0 for row in values), "historical_negative_pulse")
    return [i for i, row in enumerate(values)
            if row[0] > 0 and (i == 0 or values[i-1][0] == 0)]


def read_case(folder):
    records = json.loads((folder/"trace-files.json").read_text())
    expected = {"stimulus", "lt_spikes", "neuron_soma_sum", "learner_cached_somas"}
    expected.update("soma"+str(i)+"_"+role for i in range(1, 5) for role in ("exc", "inh"))
    require(len(records) == len(expected) and {r["role"] for r in records} == expected,
            "historical_trace_roles")
    times, streams = None, {}
    for record in records:
        path = (folder/record["path"]).resolve(strict=True)
        require(path.is_relative_to(folder.resolve()), "historical_trace_path_escape")
        clock, values = read_stream(path, 5 if record["role"] == "learner_cached_somas" else 1,
                                    record["sha256"])
        require(times is None or times == clock, "historical_trace_clock_disagreement")
        times = clock; streams[record["role"]] = values
    somas = [[streams["soma"+str(i)+"_exc"][n][0]+streams["soma"+str(i)+"_inh"][n][0]
              for i in range(1, 5)] for n in range(len(times))]
    # This actual native record checks scheduler alignment of the derivation.
    require(all(row == cached[1:] for row, cached in zip(somas, streams["learner_cached_somas"])),
            "historical_soma_cached_disagreement")
    pulses = rising_edges(streams["stimulus"])
    require(len(pulses) == 32, "historical_stimulus_count")
    spikes = rising_edges(streams["lt_spikes"])
    csv = analyze_historical_csv(folder/"work/SelectivityLog/results.csv", [str(i) for i in range(8)])
    rows = sorted(csv["rows"], key=lambda r: int(r["trial_id"]))
    trials = []
    for index, row in enumerate(rows):
        actual = [times[i] for i in pulses[index*4:(index+1)*4]]
        require(all(abs((actual[j+1]-actual[j])-isi) < 1e-9
                    for j, isi in enumerate(row["isis"])), "historical_stimulus_isi")
        left, end = max(0, actual[0]-.01), actual[-1]+.5
        require(times[-1] >= end and (index == 7 or times[pulses[(index+1)*4]] > end),
                "historical_observation_window_not_covered")
        trial_spikes = [times[i] for i in spikes if actual[0] <= times[i] <= end]
        require(bool(trial_spikes) == row["reported_fired"], "historical_csv_spike_disagreement")
        trials.append({"trial_id": row["trial_id"], "label": row["label"], "onset": actual[0],
                       "stimulus_times": actual, "begin": left, "end": end,
                       "spike_times": trial_spikes, "native_match": row["native_match"],
                       "recorded_window_covered": True})
    comparison = json.loads((folder/"comparison.json").read_text())
    require(comparison["csv_byte_equal_to_untouched_replay"] is True,
            "historical_observer_changed_csv")
    return {"times": times, "somas": somas, "trials": trials,
            "validation": {"kind": "historical_phasea_temporal_descriptive", "samples": len(times),
                "streams": len(streams), "stimulus_edges": len(pulses), "spike_edges": len(spikes),
                "all_soma_samples_equal_native_learner_vector": True,
                "csv_byte_equal_to_untouched_replay": True, "native_counts": csv["reported_counts"],
                "native_correct": csv["native_match_count"], "trials": trials,
                "late_spikes_outside_native_windows": [times[i] for i in spikes
                    if not any(t["onset"] <= times[i] <= t["end"] for t in trials)],
                "legacy_csv_completeness": "unknown", "training_certificate": None,
                "strict_evaluation_verdict": None,
                "soma_derivation": "native ExcChannel.Output + InhChannel.Output; no source patch"}}


def render_case(data, output, case):
    import matplotlib.pyplot as plt
    output.mkdir(parents=True, exist_ok=False)
    paths = []
    for trial in data["trials"]:
        onset = trial["onset"]
        for mode in ("full", "detail"):
            left, right = ((trial["begin"], trial["end"]+.02) if mode == "full" else
                           (trial["stimulus_times"][-1]-.02, trial["stimulus_times"][-1]+.08))
            first = max(0, bisect.bisect_left(data["times"], left)-1)
            last = min(len(data["times"]), bisect.bisect_right(data["times"], right)+1)
            x = [(t-onset)*1000 for t in data["times"][first:last]]
            fig, axes = plt.subplots(4, 1, figsize=(16, 10), dpi=120, sharex=True)
            for i, ax in enumerate(axes):
                y = [s[i] for s in data["somas"][first:last]]
                ax.plot(x, y, lw=1, color="navy", label="soma "+str(i+1)+" membrane potential")
                for j, t in enumerate(trial["stimulus_times"]):
                    if left <= t <= right:
                        ax.axvline((t-onset)*1000, color="darkorange", lw=1.2, ls="--",
                                   label="actual input pulse" if j == next(k for k,v in enumerate(trial["stimulus_times"]) if left <= v <= right) else None)
                for j, t in enumerate(trial["spike_times"]):
                    if left <= t <= right:ax.axvline((t-onset)*1000, color="crimson", lw=1,
                                                   label="LT output spike" if j == 0 else None)
                ax.set_ylim(*padded_limits(y));ax.set_ylabel("potential, native units")
                ax.grid(alpha=.25);ax.legend(loc="upper left", fontsize=8)
            axes[-1].set_xlim((left-onset)*1000, (right-onset)*1000)
            axes[-1].set_xlabel("time since first actual input pulse, ms")
            fig.suptitle(case+" | trial "+trial["trial_id"]+" | "+trial["label"]+
                         " | "+mode+" | orange: actual input; red: actual LT spikes\n"+
                         "Historical saved-state replay; soma = ExcChannel + InhChannel; CSV A/B unchanged")
            fig.tight_layout(rect=(0, 0, 1, .94))
            path = output/("trial-"+trial["trial_id"]+"-"+mode+".png")
            fig.savefig(path);plt.close(fig);paths.append(path.name)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args()
    runtime = plotting_runtime() if args.plots else None
    require(not args.output.exists(), "historical_temporal_output_exists")
    result = {}; names = ("baseline", "threshold0130", "threshold0135")
    # Validate all cases before producing any positive report.
    data = {name: read_case(args.input/name) for name in names}
    args.output.mkdir(parents=True)
    for name in names:
        result[name] = data[name]["validation"]
        if args.plots:result[name]["figures"] = render_case(data[name], args.output/name, name)
    (args.output/"validation.json").write_text(json.dumps({"cases": result,
        "plotting_runtime": runtime, "schema": "historical_phasea_temporal_v1",
        "strict_evaluation_verdict": None}, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()
