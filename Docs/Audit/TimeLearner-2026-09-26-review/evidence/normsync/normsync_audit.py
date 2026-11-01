#!/usr/bin/env python3
"""NORMALIZATION_SYNC 2026-10-25: from TimeLearnerTrainingAudit.log measure how a normalization edit
(tip_r change for N1, num_synapse change for N0) shifts the measured peak delay of a dendrite whose length
did NOT change. Pairs of consecutive iteration records (i -> i+1) per dendrite k (anchor excluded):
  L(k) same in both measurements (length_before) and length_after[i]==length_before[i] (no L edit applied),
  normalization edit = tip_r or num_synapse differs between records.
Output per pair: dDelay = delay_from_pulse[i+1]-delay_from_pulse[i] (s), Rs ratio, dN, L, span sync_tol.
Also per-run: sync error e_k = delay_from_pulse[k]-delay_from_pulse[anchor] at first eol_sync=1 and at end."""
import sys, re, json, math, glob, os
ACTIVE_ONLY = os.environ.get('ACTIVE_ONLY', '1') == '1'
def parse(line):
    d = {}
    for kv in line.rstrip('\n').split(';'):
        if '=' in kv:
            k, v = kv.split('=', 1); d[k] = v
    return d
def arr(d, k, f=float):
    v = d.get(k)
    if v is None or not v.startswith('['): return None
    v = v.strip('[]')
    return [f(x) for x in v.split(',')] if v else []
def analyse(path):
    recs = []
    for line in open(path, errors='replace'):
        if 'kind=iteration' not in line: continue
        d = parse(line)
        r = dict(iter=int(d.get('iter', -1)), mode=d.get('normalization_mode'), trainer=d.get('trainer'), tol=float(d.get('sync_tol', 'nan')),
                 eol_sync=d.get('eol_sync'), tip=arr(d, 'tip_r'), Lb=arr(d, 'length_before', int), La=arr(d, 'length_after', int),
                 N=arr(d, 'num_synapse', int), dfp=arr(d, 'delay_from_pulse'), pv=arr(d, 'peak_valid', int), act=d.get('active_dendrite'), epr=arr(d, 'expected_pulse_rel'), prl=arr(d, 'peak_rel'), est=float(d.get('est_delay_per_seg','nan')))
        if r['tip'] and r['Lb'] and r['dfp']: recs.append(r)
    pairs = []
    for a, b in zip(recs, recs[1:]):
        if b['iter'] != a['iter'] + 1: continue
        n = min(len(a['tip']), len(b['tip']), len(a['dfp']), len(b['dfp']))
        for k in range(n - 1):
            if a['Lb'][k] != b['Lb'][k] or a['La'][k] != a['Lb'][k]: continue
            if not (a['pv'] and b['pv'] and a['pv'][k] and b['pv'][k]): continue
            if ACTIVE_ONLY and not (a['act'] == str(k) and b['act'] == str(k)): continue
            dR = b['tip'][k] / a['tip'][k] if a['tip'][k] > 0 else float('nan')
            dN = (b['N'][k] - a['N'][k]) if a['N'] and b['N'] else 0
            if abs(math.log(dR)) < 1e-9 and dN == 0: continue
            pairs.append(dict(iter=a['iter'], k=k, L=a['Lb'][k], R0=a['tip'][k], R1=b['tip'][k], ratio=dR, dN=dN, N0=(a['N'][k] if a['N'] else None),
                              dDelay_ms=1e3 * (b['dfp'][k] - a['dfp'][k]), tol_ms=1e3 * a['tol']))
    def serr(r):
        # arrival error vs anchor (last input): peak_rel difference (sync target = equal arrival)
        v = r.get('prl') or r['dfp']
        an = len(v) - 1
        return [round(1e3 * (v[k] - v[an]), 3) for k in range(an)]
    # sync-loss events: all |err|<=tol at record a, some |err|>tol at b, and no length edit applied at a (La==Lb)
    loss = []
    for a, b in zip(recs, recs[1:]):
        if b['iter'] != a['iter'] + 1 or not a.get('prl') or not b.get('prl'): continue
        ea, eb = serr(a), serr(b); tol = 1e3 * a['tol']
        if a['La'] != a['Lb']: continue
        if max(map(abs, ea)) <= tol and max(map(abs, eb)) > tol:
            loss.append(dict(iter=a['iter'], ea=ea, eb=eb, tol=round(tol,3), tipa=a['tip'], tipb=b['tip'], Na=a['N'], Nb=b['N'], L=a['La']))
    first_sync = next((r for r in recs if r['eol_sync'] == '1'), None)
    span = max((max(r['epr']) for r in recs if r['epr']), default=None)
    return dict(path=path, span=span, est0=recs[0]['est'] if recs else None, n_iter=len(recs), mode=recs[0]['mode'] if recs else None, trainer=recs[0]['trainer'] if recs else None,
                tol_ms=1e3 * recs[0]['tol'] if recs else None, pairs=pairs, sync_loss=loss,
                first_sync=dict(iter=first_sync['iter'], L=first_sync['Lb'], tip=first_sync['tip'], err_ms=serr(first_sync)) if first_sync else None,
                last=dict(iter=recs[-1]['iter'], L=recs[-1]['La'], tip=recs[-1]['tip'], err_ms=serr(recs[-1])) if recs else None)
if __name__ == '__main__':
    out = [analyse(p) for p in sys.argv[1:]]
    json.dump(out, sys.stdout, indent=None, default=str)
