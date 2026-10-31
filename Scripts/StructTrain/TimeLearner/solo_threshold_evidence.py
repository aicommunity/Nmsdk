"""Replay fresh Solo LTZ trace consistency; not a calibrated threshold or Train PASS."""
import csv
from pathlib import Path
import tempfile

from .model_identity import canonical_model_sha256
from .native_evidence import audit_probe, count, equal, number, after, require


FIELDS = {"kind", "schema_version", "native_probe", "armed", "complete", "valid", "requested_specification",
          "termination_reason", "nonspiking", "proposal_eligible", "source", "baseline_before_children",
          "minimum_after_children", "maximum_after_children", "spike_times", "samples", "calibrated",
          "evaluation_verdict", "sha256"}


def audit_solo_threshold_trace(report):
    r = report
    require(type(r) is dict and set(r) == FIELDS and r["kind"] == "native_solo_threshold_trace"
            and type(r["schema_version"]) is int and r["schema_version"] == 1, "unknown_solo_threshold_trace")
    require(r["sha256"] == canonical_model_sha256({k: v for k, v in r.items() if k != "sha256"}),
            "solo_threshold_digest_mismatch")
    require(r["calibrated"] is False and r["evaluation_verdict"] is None, "unsupported_solo_threshold_claim")
    require(all(type(r[k]) is bool for k in ("armed", "complete", "valid", "proposal_eligible"))
            and type(r["termination_reason"]) is str and bool(r["termination_reason"]), "invalid_solo_threshold_status")
    q, frames = r["requested_specification"], r["samples"]
    require(q["time_frame"] == "relative_to_trial_start" and type(frames) is list
            and len(frames) <= count(q["maximum_samples"]), "invalid_solo_threshold_budget")
    if r["armed"]:
        s = r["source"]
        require(set(s) == {"path", "class", "threshold", "frequency_hz", "base_model_revision", "effective_model_revision",
                           "sample_phase", "units"} and s["path"] == "$.LTZone.Potential" and bool(s["class"])
                and s["sample_phase"] == "native_after_children" and s["units"] == "model_units_SI_unverified"
                and bool(s["base_model_revision"]) and bool(s["effective_model_revision"]), "invalid_solo_threshold_source")
        number(s["threshold"])
        require(number(s["frequency_hz"]) > 0 and s["frequency_hz"] == q["stimulus_profile"]["frequency_hz"],
                "solo_threshold_frequency_mismatch")
        number(r["baseline_before_children"])
    else:
        require(not frames and r["source"] == {} and r["baseline_before_children"] is None, "unarmed_solo_threshold_samples")
    spikes, stimuli, potentials, times = [], [], [], []
    channels = None
    for f in frames:
        require(type(f) is dict and set(f) == {"time", "stimulus", "soma", "lt_potential", "new_stimuli", "new_spikes"},
                "unknown_solo_threshold_frame")
        t = number(f["time"])
        require(not times or (t > times[-1] and not after(t, times[-1]+number(q["maximum_sample_gap"]))),
                "solo_threshold_sample_gap")
        times.append(t)
        number(f["stimulus"])
        require(type(f["soma"]) is list and len(f["soma"]) > 0, "missing_solo_threshold_soma")
        if channels is None:
            channels = len(f["soma"])
        require(channels == len(f["soma"]), "solo_threshold_soma_dimension_changed")
        for value in f["soma"]:
            number(value)
        potentials.append(number(f["lt_potential"]))
        for event in f["new_spikes"]:
            event = number(event)
            require(not after(times[0], event) and not after(event, t) and (not spikes or event > spikes[-1]),
                    "invalid_solo_threshold_spike")
            spikes.append(event)
        for event in f["new_stimuli"]:
            require(set(event) == {"id", "time"} and bool(event["id"]) and not after(number(event["time"]), t),
                    "invalid_solo_threshold_stimulus")
            stimuli.append(event)
    require(spikes == r["spike_times"] and len(spikes) <= count(q["maximum_samples"]), "solo_threshold_spikes_mismatch")
    if potentials:
        require(equal(min(potentials), r["minimum_after_children"]) and equal(max(potentials), r["maximum_after_children"]),
                "solo_threshold_extrema_mismatch")
    else:
        require(r["minimum_after_children"] is None and r["maximum_after_children"] is None, "empty_solo_threshold_extrema")
    native, complete, valid, native_audit = r["native_probe"], False, False, None
    if native is not None:
        require(native["requested_specification"] == q, "solo_threshold_request_mismatch")
        o = native["observation"]
        if r["armed"] and o is not None:
            spec = o["specification"]
            complete = o["complete"] is True and len(frames) == count(o["sample_count"]) and bool(times) and equal(times[0], spec["begin"]) and equal(times[-1], spec["end"])
            if complete:
                require(not any(after(spec["begin"], t) or after(t, spec["end"]) for t in times), "solo_threshold_window_mismatch")
                require(stimuli == [{"id": e["id"], "time": e["time"]} for e in o["stimuli"]], "solo_threshold_stimuli_mismatch")
            p, source = native["prepared"], r["source"]
            valid = (complete and native["native_status"] == "completed" and o["valid"] is True
                     and native["requires_fresh_verification"] is False and not native["reasons"]
                     and p is not None and p["base_model_revision"] == native["current_base_revision"] == source["base_model_revision"]
                     and p["effective_model_revision"] == spec["effective_model_revision"] == source["effective_model_revision"])
            if valid:
                # A lossless projection of the primary JSON samples, not a
                # synthetic physical trace: use the production peak replayer.
                with tempfile.TemporaryDirectory(prefix="tl-solo-ltz-") as folder:
                    path = Path(folder)/"primary-soma-projection.csv"
                    with path.open("w", newline="", encoding="utf-8") as stream:
                        writer = csv.writer(stream)
                        writer.writerow(["time", "stimulus"]+[f"soma{i}" for i in range(channels)])
                        writer.writerows([[f["time"], f["stimulus"], *f["soma"]] for f in frames])
                    native_audit = audit_probe(native, path)
    require(r["complete"] is complete and r["valid"] is valid, "solo_threshold_validity_mismatch")
    require(r["nonspiking"] is (not spikes if valid else None)
            and r["proposal_eligible"] is (valid and not spikes), "solo_threshold_eligibility_mismatch")
    return {"schema_version": 1, "complete": complete, "valid": valid, "proposal_eligible": valid and not spikes,
            "samples": len(frames), "spikes": len(spikes), "native_peak_audit": native_audit,
            "native_execution_attested": False, "calibrated": False, "evaluation_verdict": None}
