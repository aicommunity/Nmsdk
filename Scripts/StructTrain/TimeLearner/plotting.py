"""Full-sample diagnostic plots. Scientific metrics never use rendered pixels."""
from pathlib import Path
import math

from .native_evidence import require


def padded_limits(values):
    require(bool(values) and all(math.isfinite(v) for v in values), "invalid_plot_amplitudes")
    low, high = min(values), max(values)
    padding = (high-low)*.08 if high > low else max(abs(low)*.08, 1e-12)
    return low-padding, high+padding


def detail_limits(samples, channel, left, right, shared):
    # Include the two bracketing samples: the visible boundary line must fit too.
    inside = [i for i, sample in enumerate(samples) if left <= sample["time"] <= right]
    if not inside:
        return None
    begin, end = max(0, inside[0]-1), min(len(samples), inside[-1]+2)
    values = [s["soma"][channel] for s in samples[begin:end] if math.isfinite(s["soma"][channel])]
    if not values:return None
    low, high = min(values), max(values)
    if 0 < high-low < .25*(shared[1]-shared[0]):
        return padded_limits(values)
    return None


def series_timeline(observations):
    """Actual clock gaps and stimulus intervals, never invented ITI or reset time."""
    require(bool(observations), "empty_plot_series")
    timeline, previous = [], None
    for index, o in enumerate(observations):
        row = {"presentation_index": index, "trial_id": o["trial_id"], "sample_id": o["sample_id"],
               "label": o["label"], "begin": o["begin"], "planned_end": o["end"],
               "last_observed": o["closed_at"], "reset_policy": o["reset_policy"],
               "reset_boundary": o["begin"] if o["reset_policy"] == "reset_per_trial" else None,
               "exact_reset_timestamp": None, "onset_to_onset_seconds": None,
               "last_to_first_stimulus_seconds": None, "unobserved_gap": None}
        if previous is not None:
            require(o["begin"] > previous["closed_at"], "overlapping_plot_series")
            if o["begin"]-previous["closed_at"] > 1.5/previous["frequency_hz"]:
                row["unobserved_gap"] = [previous["closed_at"], o["begin"]]
            if previous["stimulus_times"] and o["stimulus_times"]:
                row["onset_to_onset_seconds"] = o["stimulus_times"][0]-previous["stimulus_times"][0]
                row["last_to_first_stimulus_seconds"] = o["stimulus_times"][0]-previous["stimulus_times"][-1]
        timeline.append(row);previous = o
    return timeline


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
    sample_markers=observation.get("sample_markers",False) or len(samples)==1
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
        views = []
        for name, left, right in time_views(observation["begin"], observation["end"], frequency):
            views.append((name, left, right, limits, "shared", name))
            detail = detail_limits(samples, channel, left, right, limits)
            if detail is not None:
                views.append((name+"-detail", left, right, detail, "local_detail", name))
        for name, left, right, y_limits, scale, time_view in views:
            fig, ax = plt.subplots(figsize=(12, 6), dpi=160)
            fig.subplots_adjust(left=.12, right=.86, bottom=.16, top=.70)
            overlay = ax.twinx()
            ax.plot(times, soma, color="#154c9a", linewidth=1.4, label=label,
                    marker="o" if sample_markers else None,markersize=4,markerfacecolor="none")
            overlay.step(times, stimulus, where="post", color="#d46200", alpha=.65,
                         linewidth=1.2, label="Actual shared input (native samples)",
                         marker="x" if sample_markers else None,markersize=3)
            ax.set_xlim(left, right);ax.set_ylim(*y_limits)
            ax.set_xlabel("Native absolute time [s]")
            ax.set_ylabel("Soma SumPotential [model units; SI unverified]")
            overlay.set_ylabel("Input [native generator units]", color="#a34d00")
            overlay.tick_params(axis="y", colors="#a34d00")
            ax.grid(True, alpha=.25)
            if "unobserved_intervals" in observation:
                labelled=False
                for begin,end in observation["unobserved_intervals"]:
                    if max(left,begin)<min(right,end):
                        ax.axvspan(max(left,begin),min(right,end),color="gray",alpha=.25,
                                   label=None if labelled else "Unobserved / censored")
                        labelled=True
            elif not observation["complete"] and observation["closed_at"] < right:
                ax.axvspan(max(left, observation["closed_at"]), right, color="gray", alpha=.25,
                           label="Unobserved / censored")
            for event in observation["spike_times"]:
                if left <= event <= right:
                    ax.axvline(event, color="#8c2c91", alpha=.5, linestyle=":")
            fig.suptitle(f'{observation["sample_id"]} | {observation["label"]} | {observation["trial_id"]}\n'
                         f'{label} | {observation["reset_policy"]}\n'
                         f'{name} ({scale} Y) | valid={observation["valid"]}, complete={observation["complete"]} | '
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
                         "minimum_native_tick_pixels_on_zoom": 14.208 if time_view != "overview" else None,
                         "downsampling": False, "y_scale": scale, "time_view": time_view,
                         "sample_markers":bool(sample_markers),
                         "shared_y_limits": list(limits), "y_limits": list(y_limits)})
    return rows


def render_series(observations, channel, label, limits, output: Path):
    """Unsqueezed native clock; grey gaps are unknown, not silent ITI evidence."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    output.mkdir(parents=True, exist_ok=False)
    timeline = series_timeline(observations)
    pages = [("series-overview", 0, len(observations))]
    if len(observations) > 4:
        pages.extend((f"series-page-{i//4+1:03d}", i, min(len(observations), i+4))
                     for i in range(0, len(observations), 4))
    rows = []
    with plt.rc_context({"font.size": 12, "axes.titlesize": 12, "svg.fonttype": "none"}):
        for name, first, last in pages:
            selected = observations[first:last]
            left, right = selected[0]["begin"], max(o["end"] for o in selected)
            fig, ax = plt.subplots(figsize=(12, 6), dpi=160)
            fig.subplots_adjust(left=.12, right=.86, bottom=.16, top=.70)
            overlay = ax.twinx()
            for position, o in enumerate(selected):
                # Separate trials explicitly, even on adjacent native ticks.
                # Missing internal samples also break both lines.
                x, y, stimulus = [], [], []
                previous = None
                for sample in o["samples"]:
                    if previous is not None and sample["time"]-previous > 1.5/o["frequency_hz"]:
                        x.append((sample["time"]+previous)/2);y.append(float("nan"));stimulus.append(float("nan"))
                    x.append(sample["time"]);y.append(sample["soma"][channel]);stimulus.append(sample["stimulus"])
                    previous = sample["time"]
                ax.plot(x, y, color="#154c9a", linewidth=1.4, label=label if position == 0 else None)
                overlay.step(x, stimulus, where="post", color="#d46200", alpha=.65, linewidth=1.2,
                             label="Actual shared input samples" if position == 0 else None)
                row = timeline[first+position]
                if row["unobserved_gap"]:
                    begin, end = row["unobserved_gap"]
                    if end > left:
                        ax.axvspan(max(left, begin), end, color="gray", alpha=.25)
                if not o["complete"]:
                    # Stop this censored shading at a later actual trial boundary.
                    end = min(o["end"], selected[position+1]["begin"]) if position+1 < len(selected) else o["end"]
                    ax.axvspan(o["closed_at"], end, color="gray", alpha=.25)
                color = "#3b893e" if row["reset_boundary"] is not None else "#666666"
                ax.axvline(o["begin"], color=color, linestyle="--", alpha=.5)
                for spike in o["spike_times"]:
                    ax.axvline(spike, color="#8c2c91", alpha=.5, linestyle=":")
            ax.set_xlim(left, right);ax.set_ylim(*limits)
            ax.set_xlabel("Native absolute time [s]; gaps retain actual duration")
            ax.set_ylabel("Soma SumPotential [model units; SI unverified]")
            overlay.set_ylabel("Input [native generator units]", color="#a34d00")
            overlay.tick_params(axis="y", colors="#a34d00")
            ax.grid(True, alpha=.25)
            fig.suptitle(f'{name} | {label} | trials {first}..{last-1}\n'
                         'Green boundary: reset policy; grey area: unobserved\n'
                         'Actual order and stimulus intervals: timing table in index/manifest', y=.98)
            handles, labels = ax.get_legend_handles_labels()
            more_handles, more_labels = overlay.get_legend_handles_labels()
            fig.legend(handles+more_handles, labels+more_labels, loc="upper center",
                       bbox_to_anchor=(.5, .84), frameon=False)
            files = []
            for extension in ("png", "svg", "pdf"):
                target = output/f"{name}.{extension}";fig.savefig(target);files.append(target.name)
            plt.close(fig)
            rows.append({"view": name, "begin": left, "end": right, "first_presentation": first,
                         "last_presentation": last-1, "files": files, "y_scale": "shared",
                         "y_limits": list(limits), "png_width": 1920, "png_height": 960,
                         "downsampling": False, "clock_compression": False})
    return {"timeline": timeline, "views": rows}
