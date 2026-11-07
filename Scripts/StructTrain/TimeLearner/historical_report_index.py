"""Build a readable local index of hash-verified historical temporal reports."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

from .native_evidence import load, require


def _leaf(value):
    require(type(value) is str and value not in (".", "..") and
            re.fullmatch(r"[A-Za-z0-9_.-]+", value) is not None, "report_index_unsafe_name")
    return value


def index_bytes(cache_root, cases):
    """Validate every linked figure; return HTML without changing the cache."""
    root = Path(cache_root).resolve(strict=True)
    require(type(cases) is list and bool(cases) and len(set(cases)) == len(cases),
            "report_index_invalid_case_set")
    sections, bindings = [], []
    escape = html.escape
    modes = ("full", "response", "positive_full", "positive_response")
    for case in cases:
        folder = (root/_leaf(case)).resolve(strict=True)
        require(folder.is_relative_to(root), "report_index_case_escape")
        report_path = folder/"report.json";report = load(report_path)
        require(report.get("kind") == "historical_protocol_temporal_report" and
                report.get("schema_version") == 1 and report.get("case") == case and
                report.get("minimum_font_size", 0) >= 12 and
                report.get("all_samples_drawn_without_decimation") is True,
                "report_index_unknown_report")
        observation = report["observation"];trials = observation["trials"]
        require(len(trials) == 8 and {t["sample_id"] for t in trials} ==
                {"phasea-"+str(i) for i in range(8)} and
                {t["position"] for t in trials} == set(range(8)), "report_index_incomplete_trial_set")
        figures = report["figures"]
        require(len(figures) == 32 and len({(f["sample_id"], f["mode"]) for f in figures}) == 32 and
                {(f["sample_id"], f["mode"]) for f in figures} ==
                {(t["sample_id"], m) for t in trials for m in modes}, "report_index_incomplete_figure_set")
        by_key = {}
        for figure in figures:
            path = (folder/_leaf(figure["path"])).resolve(strict=True)
            require(path.is_relative_to(folder) and path.is_file() and
                    path.stat().st_size == figure["bytes"] and
                    hashlib.sha256(path.read_bytes()).hexdigest() == figure["sha256"],
                    "report_index_figure_hash_mismatch")
            by_key[figure["sample_id"], figure["mode"]] = path.relative_to(root).as_posix()
        parts = []
        for trial in sorted(trials, key=lambda t: t["position"]):
            sample = trial["sample_id"]
            title = f"Position {trial['position']} | {sample} | {trial['label']} | actual LT spikes: {len(trial['full_interval_spike_times'])}"
            links = " · ".join(f'<a href="{escape(by_key[sample, mode], quote=True)}">{mode}</a>' for mode in modes)
            image = escape(by_key[sample, "positive_response"], quote=True)
            parts.append(f'<details><summary>{escape(title)}</summary><p>{links}</p>'
                         f'<a href="{image}"><img loading="lazy" src="{image}" alt="{escape(title, quote=True)}"></a></details>')
        counts = observation["native_counts"]
        summary = "; ".join(f"{key}={counts[key]}" for key in ("TP", "FP", "FN", "TN"))
        sections.append(f'<section><h2>{escape(case)}</h2><p>Historical criterion: {escape(summary)}. '
                        'Complete intervals and late events remain in report.json.</p>'+"\n".join(parts)+'</section>')
        bindings.append({"case": case, "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                         "figures_verified": len(figures)})
    document = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Frozen historical protocol: native temporal reports</title>
<style>body{font:18px/1.5 sans-serif;max-width:1920px;margin:32px auto;padding:0 24px;color:#17212b}
h1,h2{line-height:1.2}summary{cursor:pointer;padding:10px;background:#edf2f7;margin-top:10px}
img{display:block;width:100%;height:auto}a{color:#154e9d}section{margin:36px 0}</style>
<h1>Frozen historical protocol: native temporal reports</h1>
<p>Open each presentation to inspect its curves. Click a view link for the original 1920×1680 image.
Orange: actual recorded input; red: actual LT output spikes; black: global Test maximum.
Positive views may clip negative feedback; consult full views. No training-peak certificate is inferred.</p>
'''+"\n".join(sections)+"</html>\n"
    return document.encode("utf-8"), bindings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-root", required=True, type=Path)
    parser.add_argument("--case", action="append", required=True)
    parser.add_argument("--output-name", default="index.html")
    args = parser.parse_args();name = _leaf(args.output_name)
    data, bindings = index_bytes(args.cache_root, args.case)
    path = args.cache_root/name
    with path.open("xb") as stream:stream.write(data)
    print(json.dumps({"path": str(path), "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest(), "sources": bindings}))


if __name__ == "__main__":
    main()
