"""D1.2: N=1..8 CSV morphology + censored silence must fail ok_audit.

Builds synthetic schema_version=3 rows, classifies via selectivity_metrics,
and optionally validates one real gold results.csv (N=8) if present.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".gitmodules").exists())
sys.path.insert(0, str(ROOT / "Bin/Configs/SpikeSamples/StructTrain/scripts"))
import selectivity_metrics as sm  # noqa: E402

EVIDENCE = ROOT / "Docs/Audit/TimeLearner-2026-09-24-review/evidence/tails"
OUT_BUILD = ROOT / "build/audit-review-20260924/metrics"
OUT_BUILD.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)

HEADER_V3 = [
    "trial",
    "target_class",
    "stim_count",
    "isi0",
    "isi1",
    "isi2",
    "isi3",
    "neuron_fired",
    "neuron_t_rel",
    "match",
    "late_fired",
    "late_t_rel",
    "error_class",
    "ltz_potential_max",
    "soma_amp_0",
    "soma_amp_1",
    "soma_amp_2",
    "soma_amp_3",
    "soma_amp_sum",
    "neuron_spike_count",
    "neuron_spike_times",
    "response_class",
    "complete",
    "censored",
    "actual_observe_end",
    "stim_times",
    "isis",
    "schema_version",
]


def _isis(n: int) -> list[str]:
    # Pack four ISI columns; unused trailing empty.
    vals = ["0.004"] * max(0, n - 1)
    while len(vals) < 4:
        vals.append("")
    return vals[:4]


def _stim_times(n: int) -> str:
    t = 0.0
    parts = []
    for i in range(n):
        parts.append(f"{t:.6g}")
        if i + 1 < n:
            t += 0.004
    return ";".join(parts)


def make_row(
    *,
    trial: int,
    target: int,
    n_stim: int,
    fired: int = 0,
    spike_times: str = "",
    censored: int = 0,
    complete: int = 1,
    error: str = "ok",
) -> dict[str, str]:
    spikes = [s for s in spike_times.split(";") if s.strip()] if spike_times else []
    count = len(spikes)
    t_rel = spikes[0] if spikes else "-1"
    isis = _isis(n_stim)
    return {
        "trial": str(trial),
        "target_class": str(target),
        "stim_count": str(n_stim),
        "isi0": isis[0],
        "isi1": isis[1],
        "isi2": isis[2],
        "isi3": isis[3],
        "neuron_fired": str(fired),
        "neuron_t_rel": t_rel,
        "match": "1" if (target != 0 and fired) or (target == 0 and not fired) else "0",
        "late_fired": "0",
        "late_t_rel": "-1",
        "error_class": error if not censored else "censored",
        "ltz_potential_max": "0",
        "soma_amp_0": "0",
        "soma_amp_1": "0",
        "soma_amp_2": "0",
        "soma_amp_3": "0",
        "soma_amp_sum": "0",
        "neuron_spike_count": str(count),
        "neuron_spike_times": spike_times,
        "response_class": "single" if count == 1 else ("silent" if count == 0 else "multi"),
        "complete": str(complete),
        "censored": str(censored),
        "actual_observe_end": "0.2",
        "stim_times": _stim_times(n_stim),
        "isis": ";".join(x for x in isis if x),
        "schema_version": "3",
    }


def pack8_silence_censored_foil(n_stim: int) -> list[dict[str, str]]:
    """Target fires once; foils silent but one foil censored → silence must not PASS."""
    rows = []
    rows.append(
        make_row(trial=0, target=1, n_stim=n_stim, fired=1, spike_times="0.05", complete=1)
    )
    for i in range(1, 8):
        cens = 1 if i == 3 else 0
        rows.append(
            make_row(
                trial=i,
                target=0,
                n_stim=n_stim,
                fired=0,
                spike_times="",
                censored=cens,
                complete=0 if cens else 1,
                error="censored" if cens else "ok",
            )
        )
    return rows


def pack_n1_morphology() -> dict[str, str]:
    # Single stim + two spikes near stim → must NOT be per_stim (R07).
    return make_row(
        trial=0,
        target=1,
        n_stim=1,
        fired=1,
        spike_times="0.001;0.002",
        complete=1,
    )


def classify_pack(rows: list[dict[str, str]]) -> dict:
    c = sm.classify(rows)
    morph0 = sm.classify_trial_morphology(rows[0]) if rows else {}
    return {
        "n_rows": len(rows),
        "stim_count_row0": int(rows[0].get("stim_count") or 0) if rows else 0,
        "ok_audit": c.get("ok_audit"),
        "ok_audit_strict_shape": c.get("ok_audit_strict_shape"),
        "censored_any": c.get("censored_any"),
        "schema_ok": c.get("schema_ok"),
        "complete": c.get("complete"),
        "mode": c.get("mode"),
        "fires": c.get("fires"),
        "morph0_per_stim": morph0.get("per_stim"),
        "morph0_burst": morph0.get("burst"),
        "morph0_ok_single": morph0.get("ok_single"),
    }


def main() -> int:
    per_n: dict[str, dict] = {}
    checks: list[dict] = []

    for n in (1, 2, 3, 4, 5, 8):
        rows = pack8_silence_censored_foil(n)
        path = OUT_BUILD / f"n{n}_censored_foil.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=HEADER_V3)
            w.writeheader()
            w.writerows(rows)
        summary = classify_pack(rows)
        summary["csv"] = str(path)
        per_n[str(n)] = summary
        # censored_any==1 ⇒ ok_audit must be 0 (silence not PASS)
        ok = summary["censored_any"] == 1 and summary["ok_audit"] == 0
        checks.append({"name": f"n{n}_censored_blocks_silence", "pass": bool(ok), **summary})

    n1 = pack_n1_morphology()
    morph = sm.classify_trial_morphology(n1)
    n1_ok = morph.get("per_stim") is False
    checks.append(
        {
            "name": "n1_not_per_stim",
            "pass": bool(n1_ok),
            "per_stim": morph.get("per_stim"),
            "spike_count": morph.get("spike_count"),
        }
    )
    per_n["n1_morphology"] = {
        "per_stim": morph.get("per_stim"),
        "burst": morph.get("burst"),
        "ok_single": morph.get("ok_single"),
        "pass": bool(n1_ok),
    }

    # advance_window-style: incomplete+censored single trial
    adv = [
        make_row(
            trial=0,
            target=1,
            n_stim=4,
            fired=1,
            spike_times="0.05",
            censored=1,
            complete=0,
            error="censored",
        )
    ]
    adv_c = sm.classify(adv)
    checks.append(
        {
            "name": "advance_window_censored",
            "pass": adv_c.get("censored_any") == 1,
            "censored_any": adv_c.get("censored_any"),
            "ok_audit": adv_c.get("ok_audit"),
        }
    )

    gold_candidates = [
        ROOT
        / "Bin/Configs/SpikeSamples/StructTrain/_repro/runs/br25_on_20260924T165949Z/Test/results.csv",
        ROOT
        / "Bin/Configs/SpikeSamples/StructTrain/TimeNeuronTimeLearnerBranch/Test/SelectivityLog/results.csv",
    ]
    gold_info = {"found": False}
    for g in gold_candidates:
        if g.is_file():
            with g.open(encoding="utf-8", newline="") as f:
                gold_rows = list(csv.DictReader(f))
            gc = sm.classify(gold_rows)
            gold_info = {
                "found": True,
                "path": str(g),
                "n_rows": len(gold_rows),
                "has_schema_version": "schema_version" in (gold_rows[0] if gold_rows else {}),
                "has_censored": "censored" in (gold_rows[0] if gold_rows else {}),
                "ok_audit": gc.get("ok_audit"),
                "schema_ok": gc.get("schema_ok"),
                "fires": gc.get("fires"),
            }
            break

    all_pass = all(c["pass"] for c in checks)
    out = {
        "probe": "n_stim_csv_probe",
        "all_pass": all_pass,
        "per_n": per_n,
        "checks": checks,
        "gold_csv": gold_info,
    }
    out_path = EVIDENCE / "d1_n1_to_n8.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    (OUT_BUILD / "d1_n1_to_n8.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_pass": all_pass, "evidence": str(out_path)}, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
