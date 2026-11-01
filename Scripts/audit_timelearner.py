#!/usr/bin/env python3
"""Read-only audit of repository Markdown and stored StructTrain measurements.

Run from any directory. Outputs go to --out; experiments are never executed or
modified. Link checking covers local file destinations, not anchors/web URLs.
"""
from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = "b1ee2711b599e0cee4a6e73f5b9bd209fef29108^"
MODULES = [".", "Rdk", "Bin", "Libraries/Nmsdk-PulseLib",
           "Libraries/Nmsdk-MotionControlLib", "Libraries/Rdk-BasicLib",
           "Libraries/Rdk-CvBasicLib", "Libraries/Rdk-HardwareLib"]
STRUCT = ROOT / "Bin/Configs/SpikeSamples/StructTrain"


def git(module: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT / module), *args]).decode("utf-8")


def load(name: str, filename: Path):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def prose_lines(text: str):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"\s*(`{3,}|~{3,})", line)
        if match:
            marker = match[1][0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None:
            yield number, line


def inventory():
    modules, broken, counts = [], [], collections.Counter()
    # File-target validation only: Markdown examples and inline code are skipped.
    link = re.compile(r"!?\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)")
    for module in MODULES:
        names = sorted(set(git(module, "ls-files", "-z").split("\0")))
        md = [ROOT / module / n for n in names if n.lower().endswith(".md")]
        extras = {
            ".": list((ROOT / "Docs/Audit/TimeLearner-2026-09-22").glob("*.md"))
                 + [ROOT / "Scripts/audit-probes/README.md"],
            "Bin": [STRUCT / "AUDIT_2026-09-22.md"],
            "Libraries/Nmsdk-PulseLib": [
                ROOT / "Libraries/Nmsdk-PulseLib/Docs/Components/TemporalNeuronVariants.md"],
            "Libraries/Rdk-HardwareLib": [
                ROOT / "Libraries/Rdk-HardwareLib/Docs/Components/ArduinoCustomFirmware.md"],
        }
        added_md = [p for p in extras.get(module, []) if p.is_file() and p not in md]
        scanned_md = md + added_md
        head = git(module, "rev-parse", "HEAD").strip()
        base = (git(".", "rev-parse", BASE).strip() if module == "."
                else git(".", "rev-parse", f"{BASE}:{module}").strip())
        modules.append({"module": module, "head": head, "baseline": base,
                        "markdown_files": len(md),
                        "additional_audit_markdown_files": len(added_md),
                        "commits": int(git(module, "rev-list", "--count", f"{base}..{head}")),
                        "status": git(module, "status", "--short"),
                        "changed_files": git(module, "diff", "--name-only", base, head).splitlines()})
        for path in scanned_md:
            if not path.is_file():
                continue
            raw = path.read_text(encoding="utf-8-sig", errors="replace")
            for number, line in prose_lines(raw):
                line = re.sub(r"`+[^`]*`+", "", line)
                for match in link.finditer(line):
                    target = match[1].strip("<>")
                    if re.match(r"^[a-zA-Z][\w+.-]*:", target) or target.startswith(("#", "/")):
                        continue
                    filepart = unquote(target.split("#", 1)[0].split("?", 1)[0])
                    if not filepart or any(x in filepart for x in ("<", ">", "{", "}")):
                        continue
                    destination = (path.parent / filepart).resolve()
                    if not destination.exists():
                        counts[module] += 1
                        broken.append({"source": path.relative_to(ROOT).as_posix(),
                                       "line": number, "target": target})
    return {"modules": modules, "markdown_files": sum(m["markdown_files"] for m in modules),
            "additional_audit_markdown_files": sum(m["additional_audit_markdown_files"] for m in modules),
            "broken_file_links_by_module": dict(counts), "broken_file_links": broken}


def stored_metrics():
    metrics = load("selectivity_metrics", STRUCT / "scripts/selectivity_metrics.py")
    audit = load("audit_structtrain", STRUCT / "scripts/audit_structtrain.py")
    records = []
    for path in sorted(STRUCT.glob("Selectivity*/**/Test/SelectivityLog/results.csv")):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        q = metrics.classify(rows)
        first = rows[0] if rows else {}
        isis = [float(first[k]) for k in ("isi0", "isi1", "isi2", "isi3") if first.get(k)]
        t = float(first.get("neuron_t_rel") or -1)
        records.append({"path": path.relative_to(ROOT).as_posix(), **q,
                        "legacy_last_pulse_ok": audit.last_pulse_ok(rows),
                        "target_t_rel": t, "target_end_rel": sum(isis),
                        "target_after_last_stim": bool(isis) and t + 1e-9 >= sum(isis)})
    return {"scope": "Selectivity*/**/Test/SelectivityLog/results.csv (archived/Test_* excluded)",
            "count": len(records),
            "ok_audit": sum(r["ok_audit"] for r in records),
            "complete_acc8": sum(r["n"] == 8 and r["acc_strict"] == 8 for r in records),
            "audit_false_last_pulse": [r["path"] for r in records if r["ok_audit"]
                                      and r["legacy_last_pulse_ok"] == "1"
                                      and not r["target_after_last_stim"]],
            "records": records}


def counterexamples():
    metrics = load("selectivity_metrics", STRUCT / "scripts/selectivity_metrics.py")
    audit = load("audit_structtrain", STRUCT / "scripts/audit_structtrain.py")
    def row(target, spike, fired, t="0.12"):
        return {"target_class": str(target), "stim_count": "4", "isi0": "0.01",
                "isi1": "0.02", "isi2": "0.03", "isi3": "",
                "neuron_fired": str(fired), "late_fired": "0",
                "neuron_t_rel": t if fired else "-1", "match": str(int(bool(target) == bool(fired))),
                "neuron_spike_count": str(spike),
                "neuron_spike_times": t if spike else "", "error_class": "ok"}
    early = row(1, 1, 1, "0.025")
    hidden_foil = [row(1, 1, 1)] + [row(0, 1, 0, "0.015") for _ in range(7)]
    # Four false positives still satisfy the explicitly weak legacy/strict gate.
    weak = [row(1, 1, 1)] + [row(0, 1, 1) for _ in range(4)] + [row(0, 0, 0) for _ in range(3)]
    return {
        "early_last_pulse": {"input": early, "actual": audit.last_pulse_ok([early]),
                             "correct_end": 0.06, "expected": "0"},
        "unflagged_foil_spikes": {"inputs": hidden_foil, "actual": metrics.classify(hidden_foil),
                                  "expected_fa": 7},
        "four_false_positives": {"actual": metrics.classify(weak),
                                 "note": "A weak audit pass is not perfect selectivity."},
        "single_spike_morphology": {"input": row(1, 1, 1, "0.002"),
                                    "actual": metrics.classify_trial_morphology(row(1, 1, 1, "0.002"))},
        "equal_isi_one_spike": {"actual": metrics.classify_trial_morphology({
            **row(1, 1, 1, "0.375"), "isi0": "0.125", "isi1": "0.125", "isi2": "0.125"}),
            "note": "One spike covers three overlapping per-stim windows."},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("inventory", inventory), ("stored_metrics", stored_metrics),
                     ("counterexamples", counterexamples)]:
        data = fn()
        (args.out / f"{name}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if name == "inventory":
            print(name, data["markdown_files"], data["broken_file_links_by_module"])
        elif name == "stored_metrics":
            print(name, {k: v for k, v in data.items() if k != "records"})
        else:
            print(name, "early gate:", data["early_last_pulse"]["actual"],
                  "hidden foil audit:", data["unflagged_foil_spikes"]["actual"]["ok_audit"],
                  "equal ISI morphology:", data["equal_isi_one_spike"]["actual"])


if __name__ == "__main__":
    main()
