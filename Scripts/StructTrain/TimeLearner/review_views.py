"""Choose informative existing views from actual samples, without scoring them."""
import math

from .native_evidence import require


def select_review_views(views, samples, channel):
    """Overview, first actual pulse, and largest first-response excursion.

    A grid's first zoom can precede the stimulus at high sampling frequencies.
    The response anchor is only an inspection aid, never a learned peak, spike,
    convergence certificate, or classification measurement.
    """
    require(type(channel) is int and channel >= 0 and bool(samples), "review_samples_required")
    require(all(type(s) is dict and math.isfinite(s["time"]) and math.isfinite(s["stimulus"])
                and len(s["soma"]) > channel and math.isfinite(s["soma"][channel]) for s in samples),
            "invalid_review_samples")
    require(all(a["time"] < b["time"] for a, b in zip(samples, samples[1:])), "unordered_review_samples")
    active = [i for i, s in enumerate(samples) if s["stimulus"] != 0]
    require(bool(active), "review_actual_stimulus_missing")
    first = active[0]
    last = first
    while last+1 < len(samples) and samples[last+1]["stimulus"] != 0:
        last += 1
    next_pulse = next((i for i in active if i > last), len(samples))
    pulse_time = (samples[first]["time"]+samples[last]["time"])/2
    baseline = samples[first-1 if first else first]["soma"][channel]
    peak = max(range(first, next_pulse), key=lambda i: abs(samples[i]["soma"][channel]-baseline))
    peak_time = samples[peak]["time"]
    overview = [v for v in views if v["view"] == "overview"]
    zooms = [v for v in views if v["view"].startswith("zoom-") and v["y_scale"] == "shared"]
    require(len(overview) == 1 and bool(zooms), "review_views_missing")
    require(all(math.isfinite(v["begin"]) and math.isfinite(v["end"]) and v["begin"] < v["end"]
                for v in overview+zooms), "invalid_review_view_window")
    result = [{"purpose": "overview", "anchor_time": None, "view": overview[0]}]
    for purpose, time in (("first_actual_pulse", pulse_time), ("first_response_excursion", peak_time)):
        candidates = [v for v in zooms if v["begin"] <= time <= v["end"]]
        require(bool(candidates), "review_anchor_not_covered:"+purpose)
        view = min(candidates, key=lambda v: (abs((v["begin"]+v["end"])/2-time)/(v["end"]-v["begin"]), v["view"]))
        result.append({"purpose": purpose, "anchor_time": time, "view": view})
    return result
