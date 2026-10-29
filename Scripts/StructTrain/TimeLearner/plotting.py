"""Full-sample diagnostic plots. Scientific metrics never use rendered pixels."""
from pathlib import Path
import math

from .native_evidence import require


def time_views(begin, end, frequency):
    """Overview plus tiles: one native tick occupies >= 8 horizontal pixels.

    A 100-tick tile leaves substantial room for labels in a 1600-pixel figure.
    No inferred interpolation, decimation, pulse width or missing samples.
    """
    require(math.isfinite(begin) and math.isfinite(end) and end > begin
            and math.isfinite(frequency) and frequency > 0, "invalid_plot_clock")
    width = 100 / frequency
    views = [("overview", begin, end)]
    tiles = math.ceil((end - begin) / width)
    for i in range(tiles):
        left, right = begin+i*width, min(end, begin+(i+1)*width)
        if right > left:
            views.append((f"zoom-{i+1:03d}", left, right))
    return views


def render_soma(observation, channel, label, limits, output: Path):
    # Lazy backend import: inventory/analyze and module import need no GUI/backend.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    samples = observation["samples"]
    require(bool(samples), "no_primary_samples_for_plot")
    frequency = observation["frequency_hz"]
    times, soma, stimulus = [], [], []
    previous = None
    for sample in samples:
        time = sample["time"]
        # Break the line across a missing native tick; do not bridge it.
        if previous is not None and time-previous > 1.5/frequency:
            times.append((time+previous)/2);soma.append(float("nan"));stimulus.append(float("nan"))
        times.append(time);soma.append(sample["soma"][channel]);stimulus.append(sample["stimulus"])
        previous = time
    rows = []
    with plt.rc_context({"font.size": 12, "axes.titlesize": 12, "svg.fonttype": "none"}):
        for name, left, right in time_views(observation["begin"], observation["end"], frequency):
            fig, ax = plt.subplots(figsize=(12, 6), dpi=160)
            fig.subplots_adjust(left=.12, right=.86, bottom=.16, top=.76)
            overlay = ax.twinx()
            ax.plot(times, soma, color="#154c9a", linewidth=1.4, label=label)
            overlay.step(times, stimulus, where="post", color="#d46200", alpha=.65,
                         linewidth=1.2, label="Actual shared input (native samples)")
            ax.set_xlim(left, right);ax.set_ylim(*limits)
            ax.set_xlabel("Native absolute time [s]")
            ax.set_ylabel("Soma SumPotential [model units; SI unverified]")
            overlay.set_ylabel("Input [native generator units]", color="#a34d00")
            overlay.tick_params(axis="y", colors="#a34d00")
            ax.grid(True, alpha=.25)
            if not observation["complete"] and observation["closed_at"] < right:
                ax.axvspan(max(left, observation["closed_at"]), right, color="gray", alpha=.25,
                           label="Unobserved / censored")
            for event in observation["spike_times"]:
                if left <= event <= right:
                    ax.axvline(event, color="#8c2c91", alpha=.5, linestyle=":")
            fig.suptitle(f'{observation["sample_id"]} | {observation["label"]} | {observation["trial_id"]}\n'
                         f'{label} | {observation["reset_policy"]}\n'
                         f'{name} | valid={observation["valid"]}, complete={observation["complete"]} | '
                         f'model {observation["model_before"][:12]}', y=.98)
            handles, labels = ax.get_legend_handles_labels()
            more_handles, more_labels = overlay.get_legend_handles_labels()
            fig.legend(handles+more_handles, labels+more_labels, loc="upper center",
                       bbox_to_anchor=(.5, .84), frameon=False)
            files = []
            for extension in ("png", "svg", "pdf"):
                target = output / f"{name}.{extension}"
                fig.savefig(target)
                files.append(target.name)
            plt.close(fig)
            rows.append({"view": name, "begin": left, "end": right, "files": files,
                         "png_width": 1920, "png_height": 960,
                         "minimum_native_tick_pixels_on_zoom": 14.208 if name != "overview" else None,
                         "downsampling": False, "y_limits": list(limits)})
    return rows
