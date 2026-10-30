#!/usr/bin/env python3
"""Separability margin (one generator line -> all dendrites, as library.response) vs shift and the exc+inh-on-segments variant (offline, linear superposition).

margin_vs_shift.py TAU D TAU_INH SPANS(ms, comma) [--json out]
 * L: physical sync lengths (as sweep.py), amplitude-normalised weights (Rs floor ignored).
 * m8: margin on the standard 8-pattern set.
 * m(dshift): target vs synthetic foils where ONE spike (worst of 4, both signs) is shifted by dshift;
   m2(dshift): TWO spikes shifted (worst pair, worst signs).
 * EI: each input = Exc synapse at segment L_k minus alpha * Inh synapse of the SAME dendrite at segment
   L_k + d (more distal: its signal reaches the soma later through the same cable; no new delay elements),
   d in {1,2,3,4,6,8,12,16,24}, alpha in [0..1.2] (scaled to the exc peak). Inh kernel uses TAU_INH
   (inh channel Rm*C). Exc L re-synced to the combined kernel peak. Best (d,alpha) shared by all inputs.
"""
import itertools, json, sys
import numpy as np
import library as lib
SEPARATE = '--separate-lines' in sys.argv

def kern_set(tau, D, Lmax, Rm=1e7):
    T = min(4.0, 0.05 + Lmax * tau + 8 * tau * np.sqrt(Lmax) + 0.05)
    return {L: lib.sim(L, [(L, 8.6e7, [0.0])], tau, D, T, Rm=Rm) for L in range(1, Lmax + 1)}

def peak_t(k): return k.argmax() * lib.DT

def resp(kerns, ts, w):
    base = -min(0.0, min(ts)); ts = [t + base for t in ts]
    n = max(len(k) for k in kerns) + int(max(ts) / lib.DT) + 2
    R = np.zeros(n)
    # one generator line feeds ALL dendrite tips (Classic/Branch topology): every dendrite sees every spike
    if SEPARATE:          # reformulated task: spike k arrives only on afferent line k -> dendrite k
        for k, ww, t in zip(kerns, w, ts):
            s = int(round(t / lib.DT)); R[s:s + len(k)] += ww * k
        return R.max()
    for k, ww in zip(kerns, w):
        for t in ts:
            s = int(round(t / lib.DT)); R[s:s + len(k)] += ww * k
    return R.max()

def sync(kfun, t, Lmax, pad):
    """choose L_k so that combined-kernel peaks align with input 4 (L=1)."""
    tp = {L: peak_t(kfun(L)) for L in range(1, Lmax + 1 - pad)}
    target = t[3] + tp[1]
    Ls = [min(tp, key=lambda L: abs(tp[L] - (target - t[k]))) for k in range(3)] + [1]
    return Ls

def margins(kerns, t, w, S, pats, dshifts):
    P0 = resp(kerns, t, w)
    m8 = (P0 - max(resp(kerns, p, w) for p in pats[1:])) / P0
    out1, out2 = {}, {}
    for ds in dshifts:
        f1 = max(resp(kerns, [tt + (s * ds if i == j else 0) for i, tt in enumerate(t)], w)
                 for j in range(4) for s in (-1, 1))
        f2 = max(resp(kerns, [tt + (s1 * ds if i == a else s2 * ds if i == b else 0) for i, tt in enumerate(t)], w)
                 for a, b in itertools.combinations(range(4), 2) for s1 in (-1, 1) for s2 in (-1, 1))
        out1[ds] = (P0 - f1) / P0; out2[ds] = (P0 - f2) / P0
    return m8, out1, out2

def main():
    tau, D, tau_i = map(float, sys.argv[1:4]); spans = [float(x) for x in sys.argv[4].split(',')]
    Lmax = 100; pad = 24
    KE = kern_set(tau, D, Lmax)
    KI = kern_set(tau_i, D, Lmax, Rm=1e7 * tau_i / tau)          # same C, inh Rm = Rm*tau_i/tau
    rows = []
    for S in spans:
        S /= 1000.0; pats = lib.patterns(S); t = pats[0]
        Ls = sync(lambda L: KE[L], t, Lmax, 0)
        fw0 = (lambda a: (a[-1] - a[0]) * lib.DT)(np.where(KE[Ls[0]] >= KE[Ls[0]].max() / 2)[0])
        fr = [1/24, 1/8, 1/4, 1/2, 1.0]                       # shift as fraction of span
        fw_fr = [0.25, 0.5, 1.0, 2.0]                         # shift as fraction of FWHM
        ds = [round(S * f, 6) for f in fr] + [round(fw0 * f, 6) for f in fw_fr]
        labels = [f"S*{f:.3f}" for f in fr] + [f"W*{f:.2f}" for f in fw_fr]
        w = [KE[1].max() / KE[L].max() for L in Ls]
        m8, m1, m2 = margins([KE[L] for L in Ls], t, w, S, pats, ds)
        fw = (lambda a: (a[-1] - a[0]) * lib.DT)(np.where(KE[Ls[0]] >= KE[Ls[0]].max() / 2)[0])
        row = dict(separate_lines=SEPARATE, tau_ms=tau*1e3, D_ms=D*1e3, tau_inh_ms=tau_i*1e3, S_ms=S*1e3, L=Ls, fwhm_ms=round(fw*1e3, 2),
                   m8=round(m8, 4), m1={l: round(m1[d], 4) for l, d in zip(labels, ds)},
                   m2={l: round(m2[d], 4) for l, d in zip(labels, ds)})
        # exc + inh on distal segment of the same dendrite
        best = None
        for d in (-8, -4, -2, -1, 0, 1, 2, 3, 4, 6, 8, 12, 16, 24):
            for a in (0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0):
                def comb(L, d=d, a=a):
                    e = KE[L]; i = KI[max(1, min(L + d, Lmax))]
                    n = max(len(e), len(i)); c = np.zeros(n); c[:len(e)] += e
                    c[:len(i)] -= a * i * (e.max() / i.max()); return c
                LL = sync(comb, t, Lmax, max(0, d) if d < pad else pad)
                ks = [comb(L) for L in LL]
                if min(k.max() / KE[L].max() for k, L in zip(ks, LL)) < 0.2: continue   # keep a measurable EPSP
                ww = [ks[3].max() / k.max() for k in ks]
                em8, em1, _ = margins(ks, t, ww, S, pats, ds[:1])
                score = min(em8, em1[ds[0]])
                if best is None or score > best[0]:
                    fwc = (lambda c: (lambda a_: (a_[-1] - a_[0]) * lib.DT)(np.where(c >= c.max() / 2)[0]))(ks[0])
                    best = (score, dict(d=d, side=('distal' if d > 0 else 'same' if d == 0 else 'proximal'), alpha=a, L=LL, fwhm_ms=round(fwc*1e3, 2), m8=round(em8, 4),
                                        m1_min=round(em1[ds[0]], 4), peak_rel=round(ks[0].max()/KE[LL[0]].max(), 3)))
        row['EI_best'] = best[1] if best else None
        rows.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
    if '--json' in sys.argv:
        json.dump(rows, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)

if __name__ == '__main__':
    main()
