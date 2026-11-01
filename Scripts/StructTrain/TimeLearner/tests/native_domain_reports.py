"""Render real C++ NativeResistanceDomains regression traces, not copied tests."""
import argparse
import hashlib
from pathlib import Path
import shutil
import time

from ..native_evidence import load, require
from ..probe_reports import render_probe_set
from .live_pipeline_corpus import write
from .native_dimension_reports import inventory


def run(primary, output, receipts):
    from PIL import Image

    before = inventory(primary)
    groups = {}
    for packet in sorted(primary.glob("*_domain_trial_*.json")):
        group = packet.name.split("_domain_trial_")[0]
        groups.setdefault(group, []).append(packet)
    expected = {f"{top}_{hz}_N1_effective_resistance_domain"
                for top in ("Classic", "Branch") for hz in (2000, 20000)}
    require(set(groups) == expected, "native_domain_report_groups")
    require(all(len(packets) == 12 for packets in groups.values()), "native_domain_report_probe_count")
    output.mkdir(parents=True, exist_ok=False)
    receipts.mkdir(parents=True, exist_ok=False)
    started = time.time()
    rows = []
    for name, packets in groups.items():
        print("RENDER", name, flush=True)
        inputs = output/name/"source"
        inputs.mkdir(parents=True)
        trials = []
        for packet in packets:
            trace = packet.with_suffix(".csv")
            require(trace.is_file(), "native_domain_report_missing_trace")
            for source in (packet, trace):
                shutil.copyfile(source, inputs/source.name)
            trials.append({"trial_id": load(packet)["requested_specification"]["trial_id"],
                           "packet": packet.name, "trace": trace.name})
        write(inputs/"report-spec.json", {"kind": "timelearner_probe_report_spec", "schema_version": 2,
              "observation_policy": "complete_or_partial", "trials": trials})
        folder = output/name/"report"
        result = render_probe_set(inputs/"report-spec.json", folder)
        manifest = load(folder/"manifest.json")
        require(len(manifest["reports"]) == len(packets), "native_domain_report_coverage")
        for entry, packet in zip(manifest["reports"], packets):
            probe = folder/entry["folder"]
            require(load(probe/"primary/probe.json") == load(packet), "native_domain_report_packet_changed")
            require((probe/"primary/trace.csv").read_bytes() == packet.with_suffix(".csv").read_bytes(),
                    "native_domain_report_samples_changed")
            meta = load(probe/"manifest.json")
            for figure in meta["figures"]:
                require(any(v["time_view"] != "overview" for v in figure["views"]),
                        "native_domain_report_missing_zoom")
                for view in figure["views"]:
                    require(not view["downsampling"], "native_domain_report_downsampled")
                    if view["time_view"] != "overview":
                        require(view["minimum_native_tick_pixels_on_zoom"] >= 8, "native_domain_report_zoom_scale")
                    png, svg, pdf = (probe/p for p in view["files"])
                    with Image.open(png) as image:
                        require(image.size == (1920, 960), "native_domain_report_resolution")
                    require("Actual shared input" in svg.read_text(), "native_domain_report_input_overlay")
                    require(pdf.read_bytes().startswith(b"%PDF-"), "native_domain_report_invalid_pdf")
        for path, digest in load(folder/"SHA256SUMS.json").items():
            require(hashlib.sha256((folder/path).read_bytes()).hexdigest() == digest,
                    "native_domain_report_checksum")
        rows.append({"name": name, "trials": len(packets), "trial_soma_pairs": result["trial_soma_pairs"]})
        write(receipts/"progress.json", rows)
    require(before == inventory(primary), "native_domain_report_source_changed")
    write(receipts/"validation.json", {"status": 0, "rows": rows,
          "source_files_unchanged": len(before), "wall_seconds": time.time()-started,
          "checks": ["full_probe_and_soma_coverage", "all_primary_samples", "all_report_checksums",
                     "1920x960", "input_overlay", "no_downsampling", "zoom_at_least_8px_per_tick"],
          "manual_visual_review_complete": False, "scientific_verdict": None,
          "limits": "depth=0 effective-domain regression; no nonzero-refinement 20000Hz claim"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("primary", "output", "receipts"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    run(args.primary, args.output, args.receipts)


if __name__ == "__main__":
    main()
