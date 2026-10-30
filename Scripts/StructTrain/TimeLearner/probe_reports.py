"""Plot actual training-probe traces, preserving raw potentials and source policy.

The default accepts completed, independently audited primary JSON/CSV only.
An explicit diagnostic policy displays partial raw traces without certifying them.
It does not fabricate frozen recognition trials, labels, units or spike absence.
"""
import csv
import gzip
import hashlib
import html
import json
import math
import platform
from pathlib import Path

from .native_evidence import audit_probe, load, number, require
from .plotting import padded_limits, render_soma


def _read_probe_data(packet_path: Path, trace_path: Path, allow_incomplete=False):
    packet = load(packet_path)
    audit = audit_probe(packet, trace_path)
    if audit["valid_observation"] is not True:
        require(allow_incomplete, "probe_plot_requires_complete_audited_primary_trace")
        from .probe_diagnostics import read_partial_probe
        return (packet, audit, *read_partial_probe(packet, trace_path))
    observation = packet["observation"];spec = observation["specification"]
    require(spec["record_spikes"] is False, "native_training_probe_spike_capture_not_supported")
    profile = spec.get("stimulus_profile")
    require(type(profile) is dict, "probe_plot_frequency_not_recorded")
    frequency = number(profile["frequency_hz"])
    require(frequency > 0, "invalid_probe_plot_frequency")
    with trace_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    # audit_probe verified every header, token, dimension and time against packet.
    samples = [{"time": float(row[0]), "stimulus": float(row[1]), "soma": [float(v) for v in row[2:]]}
               for row in rows[1:]]
    count = len(spec["baseline"])
    require(all(len(row["soma"]) == count for row in samples), "probe_plot_channel_dimension_mismatch")
    quality = ({"context_observed": True, "raw_trace_checked": True, "sample_count": len(samples),
                "recorded_window_complete": True, "first_sample_time": samples[0]["time"],
                "last_sample_time": samples[-1]["time"], "unobserved_intervals": [], "nonfinite_cells": [],
                "reason": "complete_audited_observation"} if allow_incomplete else None)
    return packet, audit, observation, spec, frequency, samples, count, quality


def render_probe(packet_path: Path, trace_path: Path, output: Path, comparison_limits=None, allow_incomplete=False):
    packet, audit, observation, spec, frequency, samples, count, quality = _read_probe_data(packet_path, trace_path, allow_incomplete)
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary";primary.mkdir()
    packet_bytes=packet_path.read_bytes()
    if packet_path.suffix == ".gz":packet_bytes=gzip.decompress(packet_bytes)
    (primary/"probe.json").write_bytes(packet_bytes)
    (primary/"trace.csv").write_bytes(trace_path.read_bytes())
    figures, links = [], []
    for channel in range(count):
        folder=output/f"soma-{channel+1:03d}";folder.mkdir()
        values=[s["soma"][channel] for s in samples if math.isfinite(s["soma"][channel])]
        if not values:
            figures.append({"channel":channel,"source_column":f"soma{channel}","views":[],"status":"no_finite_soma_samples",
                            "signal":"native NPulseMembrane SumPotential","units":"model_units_SI_unverified"})
            links.append(f'<h2>Recorded soma {channel+1}</h2><p>No finite soma samples; no curve or numeric scale invented.</p>')
            continue
        chart = {"samples": samples, "frequency_hz": frequency, "begin": spec["begin"], "end": spec["end"],
                 "closed_at": spec["end"] if quality is None else samples[-1]["time"],
                 "complete": observation["complete"] if quality is None else quality["recorded_window_complete"],
                 "valid": observation["valid"],
                 "sample_id": spec["sample_id"], "trial_id": "/".join(spec["trial_id"].split("/")[-2:]), "label": "training probe",
                 "model_before": spec["effective_model_revision"], "reset_policy": "native probe; see primary specification",
                 "spike_times": []}  # unknown, explicitly labelled; this producer cannot capture spikes
        if quality is not None:chart["unobserved_intervals"]=quality["unobserved_intervals"]
        label=f"Soma{channel+1}.SumPotential (CSV soma{channel})"
        limits=padded_limits(values) if comparison_limits is None else comparison_limits[channel]
        require(limits[0] < min(values) <= max(values) < limits[1], "probe_comparison_limits_clip_primary_data")
        views=render_soma(chart, channel, label, limits, folder)
        for view in views:
            view["files"]=[folder.name+"/"+p for p in view["files"]]
        figures.append({"channel": channel, "source_column": f"soma{channel}", "signal": "native NPulseMembrane SumPotential",
                        "units": "model_units_SI_unverified", "views": views})
        links.append(f"<h2>Recorded soma {channel+1}</h2>")
        for view in views:
            png,svg,pdf=view["files"]
            links.append(f'<p>{view["view"]}: <a href="{png}">Full PNG</a> · '
                         f'<a href="{svg}">SVG</a> · <a href="{pdf}">PDF</a></p><img src="{png}" alt="recorded soma/input response">')
    import matplotlib
    manifest={"kind":"timelearner_native_probe_visual_report","schema_version":2 if allow_incomplete else 1,"status":"diagnostic",
              "run_id":spec["run_id"],"trial_id":spec["trial_id"],"sample_id":spec["sample_id"],
              "pattern_hash":spec["pattern_hash"],"base_model_revision":(packet["prepared"] or {}).get("base_model_revision"),
              "observed_model_revision":spec.get("effective_model_revision") or None,"frequency_hz":frequency,"figures":figures,
              "primary_audit":audit,"spike_recording_enabled":spec["record_spikes"],
              "source_packet_sha256":hashlib.sha256(packet_bytes).hexdigest(),
              "source_trace_sha256":hashlib.sha256(trace_path.read_bytes()).hexdigest(),
              "runtime":{"python":platform.python_version(),"matplotlib":matplotlib.__version__,"backend":"Agg"},
              "comparison_scope":"individual probe" if comparison_limits is None else "explicit shared probe set",
              "visual_acceptance_complete":False,"scientific_verdict":None}
    if quality is not None:
        manifest["trace_quality"]=quality
        manifest["observed_soma_count"]=count if quality["context_observed"] else None
        links.insert(0,'<p>Recorded samples: '+str(quality["sample_count"])+
                     '; complete recorded window: '+str(quality["recorded_window_complete"])+
                     '; nonfinite ordinate cells: '+str(len(quality["nonfinite_cells"]))+
                     '; reason: '+html.escape(str(quality["reason"]))+'</p>')
        if not quality["context_observed"]:
            links.insert(0,'<p>No observation was captured. No soma response, absolute clock or numeric scale is invented.</p>')
    (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>Native training probe</title><style>body{font:18px sans-serif;margin:2em}img{width:100%;max-width:1920px}</style>'
        '<h1>Actual training-probe response</h1><p>'+html.escape(spec["trial_id"])+
        '</p><p>Recorded native soma potentials with actual shared input samples. SI units unverified. '
        'This is a training probe, not a frozen classification trial. Spike recording enabled: '
        +str(spec["record_spikes"])+'. If disabled, absence of markers means unknown spike response. '
        'Y scales are recorded in the manifest; local detail views are explicitly labelled. '
        'Compare multiple probes using common limits.</p>'
        '<p><a href="primary/probe.json">Primary packet</a> · <a href="primary/trace.csv">Primary CSV</a></p>'
        + ('<p>Partial/unobserved diagnostic: unobserved intervals are unknown; no response is inferred beyond recorded samples.</p>'
           if quality is not None and not quality["recorded_window_complete"] else '')
        +"\n".join(links)+'</html>\n',encoding="utf-8")
    sums={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file()}
    (output/"SHA256SUMS.json").write_text(json.dumps(sums,indent=2)+"\n",encoding="utf-8")
    result={"kind":manifest["kind"],"status":"diagnostic","soma_count":count,"files":len(sums),"scientific_verdict":None}
    if quality is not None:
        result.update(plotted_soma_count=sum(bool(f["views"]) for f in figures),
                      observed_soma_count=count if quality["context_observed"] else None,
                      data_complete=quality["recorded_window_complete"] and audit["valid_observation"] is True)
    return result


def render_probe_set(specification: Path, output: Path):
    """An expected trial set with common per-soma numeric axes, no inferred labels."""
    spec=load(specification)
    allow_incomplete=spec.get("schema_version")==2 and spec.get("observation_policy")=="complete_or_partial"
    fields={"kind","schema_version","trials"}|({"observation_policy"} if allow_incomplete else set())
    require(type(spec) is dict and set(spec)==fields and
            spec["kind"]=="timelearner_probe_report_spec" and type(spec["schema_version"]) is int and
            spec["schema_version"]==(2 if allow_incomplete else 1) and type(spec["trials"]) is list and bool(spec["trials"]), "unknown_probe_report_set")
    root=specification.resolve(strict=True).parent
    prepared=[];seen=set();profile=None;routing=None;amplitudes=None
    def artifact(relative):
        require(type(relative) is str and relative and "\\" not in relative and ":" not in relative
                and not Path(relative).is_absolute() and ".." not in Path(relative).parts, "invalid_probe_report_path")
        path=(root/relative).resolve(strict=True)
        require(path.is_relative_to(root), "probe_report_path_escapes_root")
        return path
    for trial in spec["trials"]:
        require(type(trial) is dict and set(trial)=={"trial_id","packet","trace"}, "unknown_probe_report_trial")
        require(type(trial["trial_id"]) is str and trial["trial_id"] and trial["trial_id"] not in seen,
                "duplicate_or_invalid_probe_report_trial")
        packet_path,trace_path=artifact(trial["packet"]),artifact(trial["trace"])
        packet,audit,_,actual,_,samples,count,_=_read_probe_data(packet_path,trace_path,allow_incomplete)
        require((allow_incomplete or audit["valid_observation"] is True) and audit["trial_id"]==trial["trial_id"], "probe_report_expected_trial_mismatch")
        actual_profile=actual.get("stimulus_profile");actual_routing=(packet["prepared"] or {}).get("routing")
        if profile is None:profile=actual_profile
        if routing is None:routing=actual_routing
        if amplitudes is None and count:amplitudes=[[] for _ in range(count)]
        require((actual_profile is None or actual_profile==profile) and (actual_routing is None or actual_routing==routing)
                and (not count or count==len(amplitudes)), "incompatible_probe_comparison_profile")
        for sample in samples:
            for channel,value in enumerate(sample["soma"]):
                if math.isfinite(value):amplitudes[channel].append(value)
        prepared.append((trial,packet_path,trace_path));seen.add(trial["trial_id"])
    limits=[padded_limits(values) if values else None for values in amplitudes] if amplitudes is not None else []
    output.mkdir(parents=True,exist_ok=False)
    entries=[];links=[]
    for index,(trial,packet_path,trace_path) in enumerate(prepared):
        folder=output/f"probe-{index:04d}"
        result=render_probe(packet_path,trace_path,folder,limits,allow_incomplete)
        entry={"trial_id":trial["trial_id"],"folder":folder.name,"soma_count":result["soma_count"]}
        if allow_incomplete:entry.update(plotted_soma_count=result["plotted_soma_count"],observed_soma_count=result["observed_soma_count"],
                                        data_complete=result["data_complete"])
        entries.append(entry)
        links.append(f'<li><a href="{folder.name}/index.html">{html.escape(trial["trial_id"])}</a></li>')
    portable={"kind":spec["kind"],"schema_version":spec["schema_version"],"trials":[
        {"trial_id":entry["trial_id"],"packet":entry["folder"]+"/primary/probe.json",
         "trace":entry["folder"]+"/primary/trace.csv"} for entry in entries]}
    if allow_incomplete:portable["observation_policy"]="complete_or_partial"
    (output/"report-spec.json").write_text(json.dumps(portable,indent=2)+"\n",encoding="utf-8")
    manifest={"kind":"timelearner_probe_set_visual_report","schema_version":spec["schema_version"],"status":"diagnostic",
              "expected_trials":portable["trials"],"reports":entries,"common_y_limits":limits,
              "comparison_profile":profile,"routing":routing,"visual_acceptance_complete":False,"scientific_verdict":None}
    if allow_incomplete:
        manifest["data_complete"]=all(e["data_complete"] for e in entries)
        manifest["observation_policy"]="complete_or_partial"
        manifest["rendered_trial_soma_pairs"]=sum(e["plotted_soma_count"] for e in entries)
        manifest["known_trial_soma_pairs"]=sum(e["observed_soma_count"] or 0 for e in entries)
        manifest["unknown_soma_trials"]=[e["trial_id"] for e in entries if e["observed_soma_count"] is None]
    (output/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    (output/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>Actual training probes</title><style>body{font:18px sans-serif;margin:2em}</style>'
        '<h1>Actual training-probe set</h1><p>Common per-soma numeric Y limits across all expected probes; '
        'SI units remain unverified. Local detail views are additional and explicitly labelled. '
        'Training diagnostics, no classification verdict. '
        '<a href="report-spec.json">Portable report specification</a>.</p><ul>'+''.join(links)+'</ul></html>\n',encoding="utf-8")
    sums={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file()}
    (output/"SHA256SUMS.json").write_text(json.dumps(sums,indent=2)+"\n",encoding="utf-8")
    return {"kind":manifest["kind"],"status":"diagnostic","trials":len(entries),
            "trial_soma_pairs":sum(e.get("plotted_soma_count",e["soma_count"]) for e in entries),
            "files":len(sums),"scientific_verdict":None}
