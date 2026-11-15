"""Full-sample diagnostic plots. Scientific metrics never use rendered pixels."""
from pathlib import Path
import math
import textwrap

from .native_evidence import EvidenceError, require


def figure_title(fig, text, *, font_sizes=(11, 10, 9)):
    """Keep complete identifiers inside the title band of the fixed-size page.

    Measuring the actual backend avoids clipping long trial paths while keeping
    the waveform axes and native-tick resolution unchanged.
    """
    wrapped = '\n'.join(textwrap.fill(line, width=110, break_long_words=True,
                                      break_on_hyphens=False)
                        for line in text.splitlines())
    title = fig.suptitle(wrapped, y=.98, fontsize=11)
    for size in font_sizes:
        title.set_fontsize(size)
        fig.canvas.draw()
        bounds = title.get_window_extent(fig.canvas.get_renderer())
        width, height = fig.canvas.get_width_height()
        if (bounds.x0 >= .03*width and bounds.x1 <= .97*width
                and bounds.y0 >= .85*height and bounds.y1 <= .99*height):
            return title
    require(False, 'plot_title_does_not_fit_readable_band')


def plotting_runtime():
    """Check the actual headless backend before a report creates any outputs."""
    import platform
    import sys
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot  # load native backend dependencies now
        import PIL
    except (ImportError, OSError, RuntimeError) as error:
        raise EvidenceError("plotting_runtime_unavailable:"+str(error)) from error
    return {"python": platform.python_version(), "python_executable": sys.executable,
            "matplotlib": matplotlib.__version__, "pillow": PIL.__version__}


def render_boundary_roundtrip(before, after, output, *, context):
    """Readable transfer diagnostic from all recorded samples, with input overlay.

    These are active-input0 native bursts, not whole-matrix classification.
    The full time window is retained and a second view enlarges the response.
    """
    runtime = plotting_runtime()
    import matplotlib.pyplot as plt
    for document in (before, after):
        require(document.get('kind') == 'native_boundary_response_fixture' and
                document.get('routing') == 'native_burst_active_input0' and
                document.get('scientific_verdict') is None, 'boundary_plot_scope')
    rows, replay = (d['relative_time_stimulus_potentials'] for d in (before, after))
    require(bool(rows) and len(rows) == len(replay), 'boundary_plot_missing_samples')
    size = len(rows[0]);require(size >= 3, 'boundary_plot_missing_soma')
    require(all(len(row) == size and all(type(v) in (int, float) and math.isfinite(v) for v in row)
                for row in rows+replay), 'boundary_plot_nonfinite_or_dimension')
    require(all(a[0] < b[0] for a, b in zip(rows, rows[1:])) and
                all(a[0] < b[0] for a, b in zip(replay, replay[1:])), 'boundary_plot_clock_order')
    require(all(abs(a[0]-b[0]) <= 5e-10 and a[1] == b[1] for a, b in zip(rows, replay)),
            'boundary_plot_time_or_input_mismatch')
    target = Path(output);require(not target.exists(), 'boundary_plot_output_exists')
    target.mkdir(parents=True)
    times = [r[0] for r in rows];stimulus = [r[1] for r in rows]
    figures = []
    for channel in range(2, size):
        values = [r[channel] for r in rows];restored = [r[channel] for r in replay]
        delta = [b-a for a, b in zip(values, restored)]
        amplitude = max(abs(v-values[0]) for v in values)
        active = [i for i, row in enumerate(rows) if row[1] > 0 or
                  abs(row[channel]-values[0]) > max(1e-12, amplitude*1e-4)]
        detail = (max(times[0], times[active[0]]-.05), min(times[-1], times[active[-1]]+.05)) if active else (times[0], times[-1])
        for view, limits in (('full', (times[0], times[-1])), ('response', detail)):
            fig, axes = plt.subplots(2, 1, figsize=(12, 7.5), dpi=160, sharex=True,
                                     gridspec_kw={'height_ratios': [3, 1]})
            fig.subplots_adjust(top=.78, hspace=.12, left=.10, right=.90, bottom=.10)
            try:
                axes[0].plot(times, values, color='#1659a6', label='Before export', linewidth=1.8)
                axes[0].plot(times, restored, color='#ad2460', label='After fresh import', linestyle='--', linewidth=1.2)
                axes[0].set_ylim(*padded_limits(values+restored))
                axes[0].set_ylabel('Soma potential [native units]')
                overlay = axes[0].twinx()
                overlay.step(times, stimulus, where='post', color='#c46b08', alpha=.65,
                             label='Actual input', linewidth=1.)
                overlay.set_ylabel('Actual input [native units]', color='#a34d00')
                overlay.set_ylim(*padded_limits(stimulus))
                axes[1].plot(times, delta, color='#7040a5')
                axes[1].set_ylim(*padded_limits(delta));axes[1].set_ylabel('After − before')
                axes[1].set_xlabel('Time from first recorded sample [s]')
                for axis in axes:axis.set_xlim(*limits);axis.grid(True, alpha=.25)
                figure_title(fig, context+'\n'+f'Soma {channel-1} | {view} | native burst, active input 0\n'
                             'Model transfer diagnostic; no classification or successful training claim')
                handles, labels = axes[0].get_legend_handles_labels()
                extra, extra_labels = overlay.get_legend_handles_labels()
                fig.legend(handles+extra, labels+extra_labels, loc='upper center',
                           bbox_to_anchor=(.5, .85), frameon=False, ncol=3)
                filename = f'soma-{channel-1}-{view}.png';fig.savefig(target/filename)
                figures.append(dict(file=filename, soma_index=channel-2, view=view,
                    time_limits=list(limits), png_width=1920, png_height=1200,
                    downsampling=False, actual_input_overlay=True, samples=len(rows)))
            finally:
                plt.close(fig)
    return dict(kind='native_boundary_roundtrip_visual_report', schema_version=1,
                runtime=runtime, figures=figures, scientific_verdict=None,
                scope='active input0 transfer diagnostic; not whole-pattern matrix evaluation')


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


def render_soma(observation, channel, label, limits, output: Path, *,
                potential_axis_label="Soma SumPotential [model units; SI unverified]",
                reference_level=None, context_label=None, include_native_tiles=True):
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
    require(type(include_native_tiles) is bool, "invalid_native_tile_plot_flag")
    rows = []
    with plt.rc_context({"font.size": 12, "axes.titlesize": 12, "svg.fonttype": "none"}):
        views = []
        windows = time_views(observation["begin"], observation["end"], frequency)
        if not include_native_tiles:
            # A companion Y-detail reuses the original full-resolution tiles.
            # The default still renders every native time window.
            windows = windows[:1]
        for name, left, right in windows:
            views.append((name, left, right, limits, "shared", name))
            detail = detail_limits(samples, channel, left, right, limits)
            if detail is not None:
                views.append((name+"-detail", left, right, detail, "local_detail", name))
        peak_details = {}
        for index in observation.get("diagnostic_peak_indices", []):
            require(type(index) is int and 0 < index < len(samples)-1, "invalid_plot_peak_sample_index")
            first, last = max(0,index-10), min(len(samples)-1,index+10)
            left, right = samples[first]["time"], samples[last]["time"]
            detail = detail_limits(samples, channel, left, right, limits)
            if detail is None:
                continue
            name = f"measured-peak-{index:05d}-detail"
            views.append((name,left,right,detail,"local_detail","measured_peak_detail"))
            peak_details[name] = {"peak_sample_index":index,"peak_sample_time":samples[index]["time"],
                                  "first_sample_index":first,"last_sample_index":last}
        for name, left, right, y_limits, scale, time_view in views:
            fig, ax = plt.subplots(figsize=(12, 6), dpi=160)
            # A threshold adds a fourth legend row. Reserve its own band above
            # the axes instead of drawing the input legend across the waveform.
            fig.subplots_adjust(left=.12, right=.86, bottom=.16,
                                top=.64 if reference_level is not None else .70)
            overlay = ax.twinx()
            ax.plot(times, soma, color="#154c9a", linewidth=1.4, label=label)
            if reference_level is not None:
                require(math.isfinite(reference_level), "nonfinite_plot_reference_level")
                ax.axhline(reference_level, color="#477a32", linestyle="--", linewidth=1.,
                           label="Actual scalar spike threshold")
            overlay.step(times, stimulus, where="post", color="#d46200", alpha=.65,
                         linewidth=1.2, label="Actual shared input (native samples)")
            visible_sample_markers = sample_markers or name in peak_details
            if visible_sample_markers:
                # Only visible samples get unclipped glyphs. The waveform itself
                # stays clipped: disabling clipping for its full line would draw
                # other time windows across labels and neighbouring panels.
                visible=[i for i,time in enumerate(times) if left <= time <= right]
                x=[times[i] for i in visible]
                ax.plot(x,[soma[i] for i in visible],linestyle="none",color="#154c9a",
                        marker="o",markersize=4,markerfacecolor="none",clip_on=False)
                overlay.plot(x,[stimulus[i] for i in visible],linestyle="none",color="#d46200",
                             alpha=.65,marker="x",markersize=3,clip_on=False)
            ax.set_xlim(left, right);ax.set_ylim(*y_limits)
            ax.set_xlabel("Native absolute time [s]")
            ax.set_ylabel(potential_axis_label)
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
            labelled_spike = False
            for event in observation["spike_times"]:
                if left <= event <= right:
                    ax.axvline(event, color="#8c2c91", alpha=.5, linestyle=":",
                               label=None if labelled_spike else "Actual LT spike event")
                    labelled_spike = True
            figure_title(fig, (context_label+' | ' if context_label else '')+
                         f'{observation["sample_id"]} | {observation["label"]} | {observation["trial_id"]}\n'
                         f'{label} | {observation["reset_policy"]}\n'
                         f'{name} ({scale} Y) | valid={observation["valid"]}, complete={observation["complete"]} | '
                         f'model {observation["model_before"][:12]}')
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
                         "sample_markers":bool(visible_sample_markers),
                         "shared_y_limits": list(limits), "y_limits": list(y_limits)})
            if name in peak_details:
                rows[-1]["peak_detail"] = peak_details[name]
                rows[-1]["minimum_native_tick_pixels_on_zoom"] = 1420.8/(frequency*(right-left))
            if reference_level is not None:
                rows[-1]["reference_level"] = reference_level
    return rows


def render_series(observations, channel, label, limits, output: Path, *, context_label=None):
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
            labelled_spike = False
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
                    ax.axvline(spike, color="#8c2c91", alpha=.5, linestyle=":",
                               label=None if labelled_spike else "Actual LT spike event")
                    labelled_spike = True
            ax.set_xlim(left, right);ax.set_ylim(*limits)
            ax.set_xlabel("Native absolute time [s]; gaps retain actual duration")
            ax.set_ylabel("Soma SumPotential [model units; SI unverified]")
            overlay.set_ylabel("Input [native generator units]", color="#a34d00")
            overlay.tick_params(axis="y", colors="#a34d00")
            ax.grid(True, alpha=.25)
            figure_title(fig, (context_label+' | ' if context_label else '')+
                         f'{name} | {label} | trials {first}..{last-1}\n'
                         'Green boundary: reset policy; grey area: unobserved\n'
                         'Actual order and stimulus intervals: timing table in index/manifest')
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
