"""Readable frozen-protocol reports from verified native primary data.

Run on an analysis worker. Figures describe Test responses and never certify
assigned-impulse training peaks. Full reports are reproducible worker caches.
"""
import argparse
import bisect
import hashlib
import json
from pathlib import Path

from .historical_protocol_robustness import analyze_case
from .native_evidence import load, require
from .plotting import padded_limits, plotting_runtime


def trial_views(signals, trial):
    """Use half-open native trial boundaries, never the next trial's input."""
    times = signals["times"]
    begin = bisect.bisect_left(times, trial["onset"])
    end = bisect.bisect_left(times, trial["interval_end"])
    require(begin < end and times[end-1] < trial["interval_end"], "protocol_plot_empty_interval")
    left = max(0, bisect.bisect_left(times, trial["onset"]-.01))
    response_end = min(end, bisect.bisect_right(times, trial["stimulus_times"][-1]+.6))
    channels = [[row[i] for row in signals["somas"]] for i in range(4)]
    channels.append(signals["neuron_soma_sum"])
    peaks = []
    for values in channels:
        # Descriptive global Test maximum, with deterministic first-sample tie
        # handling. This does not infer impulse ownership or convergence.
        peak = max(range(begin, end), key=values.__getitem__)
        peaks.append({"time": times[peak], "value": values[peak],
                      "equal_maximum_samples": sum(v == values[peak] for v in values[begin:end])})
    return {"first": left, "end": end, "response_end": response_end,
            "peaks": peaks, "channels": channels}


def render_case(folder, output, case):
    runtime = plotting_runtime()
    import matplotlib.pyplot as plt
    folder = Path(folder).resolve(strict=True);output = Path(output).absolute()
    require(not output.exists() and not output.is_relative_to(folder)
            and not folder.is_relative_to(output), "protocol_plot_output_exists_or_overlaps")
    observation = analyze_case(folder, include_signals=True)
    signals = observation.pop("signals");declared = load(folder/"protocol.json")
    output.mkdir(parents=True, exist_ok=False)
    figures = []
    style = {"font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 12,
             "ytick.labelsize": 12, "legend.fontsize": 12, "axes.titlesize": 12}
    with plt.rc_context(style):
        for trial in observation["trials"]:
            view = trial_views(signals, trial)
            for mode in ("full", "response", "positive_full", "positive_response"):
                focus = mode.startswith("positive")
                first = view["first"];end = view["response_end"] if mode.endswith("response") else view["end"]
                x = [(t-trial["onset"])*1000 for t in signals["times"][first:end]]
                fig, axes = plt.subplots(5, 1, figsize=(16, 14), dpi=120, sharex=True)
                axis_records = []
                for index, (ax, values, peak) in enumerate(zip(axes, view["channels"], view["peaks"])):
                    y = values[first:end]
                    ax.plot(x, y, color="navy", lw=1.2, label="native potential")
                    for j, t in enumerate(trial["full_interval_spike_times"]):
                        ax.axvline((t-trial["onset"])*1000, color="crimson", lw=1.2,
                                   label="actual LT output spike" if j == 0 else None)
                    if signals["times"][first] <= peak["time"] <= signals["times"][end-1]:
                        ax.plot((peak["time"]-trial["onset"])*1000, peak["value"], "o",
                                color="black", ms=5, label="global Test maximum (not LT spike)")
                    limits = padded_limits(y)
                    if focus:
                        # Native pre-onset baseline, retaining all positive waves.
                        # Negative spike feedback is visible in the full companion.
                        start = bisect.bisect_left(signals["times"], trial["onset"])
                        baseline = min(values[first:start] or [values[start]])
                        limits = padded_limits([baseline]+[v for v in values[first:view["end"]] if v >= baseline])
                    below = [k for k, v in enumerate(y) if v < limits[0]]
                    above = [k for k, v in enumerate(y) if v > limits[1]]
                    for clipped, edge, marker in ((below, limits[0], "v"), (above, limits[1], "^")):
                        if clipped:
                            ax.scatter([x[k] for k in clipped], [edge]*len(clipped),
                                       marker=marker, s=7, color="crimson", clip_on=False)
                    ax.set_ylim(*limits);ax.grid(alpha=.25)
                    name = "Soma "+str(index+1)+" (Exc + Inh)" if index < 4 else "Neuron.SomaSumPotential"
                    ax.set_ylabel(name+"\nnative units; SI unverified")
                    if focus:
                        ax.text(.99, .93, f"clipped: {len(below)} below, {len(above)} above; see full view",
                                transform=ax.transAxes, ha="right", va="top", fontsize=12)
                    # Actual recorded generator trace, not an inferred pulse train.
                    input_axis = ax.twinx()
                    input_axis.step(x, signals["stimulus"][first:end], where="post",
                                    color="darkorange", lw=1.2, alpha=.8, label="actual input")
                    input_axis.set_ylim(-.05, 1.1);input_axis.set_yticks([0, 1])
                    input_axis.set_ylabel("input", color="darkorange")
                    axis_records.append({"channel": name, "limits": list(limits),
                                         "clipped_below": len(below), "clipped_above": len(above),
                                         "global_test_maximum": peak})
                axes[-1].set_xlim(x[0], x[-1])
                axes[-1].set_xlabel("time since first actual input pulse, ms")
                handles, labels = axes[0].get_legend_handles_labels()
                handles2, labels2 = input_axis.get_legend_handles_labels()
                fig.legend(handles+handles2, labels+labels2, loc="upper center",
                           bbox_to_anchor=(.5, .935), ncol=2)
                fig.suptitle(f"{case} | {trial['sample_id']} | position {trial['position']} | {trial['label']} | {mode}\n"
                             f"Frozen historical Test; threshold {declared['threshold']}; declared delay {declared['iti_declared']} s\n"
                             "Complete interval and response zoom are separate; no training-peak certificate", fontsize=13)
                fig.tight_layout(rect=(.02, .01, .98, .89))
                # Fail on clipped text rather than silently reducing the font.
                fig.canvas.draw();renderer = fig.canvas.get_renderer()
                width, height = fig.canvas.get_width_height()
                for text in fig.findobj(match=lambda artist: isinstance(artist, plt.Text)):
                    if not text.get_visible() or not text.get_text():continue
                    box = text.get_window_extent(renderer)
                    # Tick text outside the displayed interval is not drawn.
                    if text.axes is not None and text in text.axes.get_xticklabels():
                        if not axes[-1].get_xlim()[0] <= text.get_position()[0] <= axes[-1].get_xlim()[1]:continue
                    require(box.x0 >= 0 and box.x1 <= width and box.y0 >= 0 and box.y1 <= height,
                            "protocol_plot_text_clipped:"+text.get_text())
                path = output/(trial["sample_id"]+"-"+mode+".png")
                fig.savefig(path);plt.close(fig)
                figures.append({"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size, "pixels": [width, height], "mode": mode,
                    "sample_id": trial["sample_id"], "position": trial["position"], "label": trial["label"],
                    "absolute_window": [signals["times"][first], signals["times"][end-1]],
                    "actual_stimulus_times": trial["stimulus_times"],
                    "actual_lt_spikes": trial["full_interval_spike_times"], "axes": axis_records})
    result = {"kind": "historical_protocol_temporal_report", "schema_version": 1,
        "case": case, "runtime": runtime, "minimum_font_size": 12,
        "all_samples_drawn_without_decimation": True, "figures": figures,
        "observation": observation, "training_certificate": None, "independent_evaluation": False}
    (output/"report.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", required=True)
    args = parser.parse_args();result = render_case(args.input, args.output, args.case)
    print(json.dumps({"case": result["case"], "figures": len(result["figures"])}))


if __name__ == "__main__":
    main()
