#!/usr/bin/env python3
"""E0 compare: Console kernel (sig - ref traces, dendrite-0 input only, subthreshold, inh off)
vs segsim (fastmodels/sim/segsim.c) for the same C, L, TipR, dt.
usage: e05_e0_compare.py SIG_DIR REF_DIR SEGSIM_BIN TIPR0 STEP > table.tsv"""
import sys, subprocess
from pathlib import Path
sig, ref, sim, tipr, step = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], float(sys.argv[4]), int(sys.argv[5])
WIN = 0.98

def trace(d):
    tr = sorted(d.rglob("test_trace.csv"))
    out = {}
    if not tr:
        return out
    with tr[0].open() as f:
        hdr = f.readline().strip().split(",")
        for line in f:
            p = line.strip().split(",")
            if len(p) != len(hdr):
                continue
            r = dict(zip(hdr, p))
            try:
                if int(float(r["sample_id"])) != 0:
                    break
                t = float(r["time_rel_s"])
                if t > WIN:
                    break
                out[round(t * step)] = float(r["soma_sum"])
            except ValueError:
                continue
    return out

def stats(ts, vs):
    if not vs:
        return None
    k = max(range(len(vs)), key=lambda i: vs[i]); pk = vs[k]
    idx = [i for i in range(len(vs)) if vs[i] >= pk / 2]
    return ts[k] * 1000, pk, (ts[idx[-1]] - ts[idx[0]]) * 1000

def segsim(C, L):
    args = [sim, str(step), repr(C), "1e7", repr(C), "1e8", "1e7", "100", "2", "0.001", "0.001", "0.001", "0", "1.0", "1"]
    inp = f"{L} 1\n{L} 1 {tipr:.6g}\n1\n1 0.0\n"
    o = subprocess.run(args, input=inp, capture_output=True, text=True).stdout.split()
    a = [float(x) for x in o]
    ts = a[1::3]; vs = a[2::3]
    return stats(ts, vs)

rows = []
for d in sorted(sig.iterdir()):
    if not d.is_dir():
        continue
    C = float(d.name.split("_")[0][1:]); L = int(d.name.split("_L")[1])
    s, r = trace(d), trace(ref / d.name)
    keys = sorted(set(s) & set(r))
    ts = [k / step for k in keys]; vs = [s[k] - r[k] for k in keys]
    c = stats(ts, vs); m = segsim(C, L)
    rows.append((C, L, c, m, len(keys)))
print("C\ttau_ms\tL\tn\tcon_tpk_ms\tsim_tpk_ms\tcon_peak\tsim_peak\tpeak_ratio_con/sim\tcon_fwhm_ms\tsim_fwhm_ms")
for C, L, c, m, n in sorted(rows):
    if not c or not m:
        print(f"{C}\t{C*1e7*1e3:.3g}\t{L}\t{n}\tNA"); continue
    print(f"{C}\t{C*1e10:.3g}\t{L}\t{n}\t{c[0]:.2f}\t{m[0]:.2f}\t{c[1]:.4g}\t{m[1]:.4g}\t{c[1]/m[1]:.4f}\t{c[2]:.2f}\t{m[2]:.2f}")
