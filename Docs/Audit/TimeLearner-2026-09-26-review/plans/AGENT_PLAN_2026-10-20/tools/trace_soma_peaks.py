#!/usr/bin/env python3
"""Per-trial soma/LTZ maxima from PatternResponseAnalyzer test_trace.csv.

Usage: trace_soma_peaks.py <dir or test_trace.csv> [--json]
Prints one line per (trial, sample_id): target_class, max soma_0..3, max ltz_potential.
Classic: soma_k is the live soma part of dendrite k+1.  Branch: rows are MaxIterSomaAmp.
"""
import json
import sys
from pathlib import Path


def main(argv):
    if not argv:
        sys.exit(__doc__)
    p = Path(argv[0])
    files = [p] if p.is_file() else sorted(p.rglob('test_trace.csv'))
    if not files:
        sys.exit('NO_TRACE')
    agg = {}
    with open(files[0], encoding='utf-8') as f:
        hdr = f.readline().strip().split(',')
        ix = {h: i for i, h in enumerate(hdr)}
        cols = [c for c in ('soma_0', 'soma_1', 'soma_2', 'soma_3', 'ltz_potential') if c in ix]
        for line in f:
            v = line.strip().split(',')
            if len(v) != len(hdr):
                continue
            key = (int(float(v[ix['trial']])), int(float(v[ix['sample_id']])))
            a = agg.setdefault(key, {'target_class': v[ix['target_class']], **{c: float('-inf') for c in cols}})
            for c in cols:
                a[c] = max(a[c], float(v[ix[c]]))
    rows = [{'trial': k[0], 'sample_id': k[1], **a} for k, a in sorted(agg.items())]
    if '--json' in argv:
        print(json.dumps({'trace': str(files[0]), 'rows': rows}, indent=1))
    else:
        print('trace', files[0])
        print('trial sample target ' + ' '.join(cols))
        for r in rows:
            print(r['trial'], r['sample_id'], r['target_class'], ' '.join(f'{r[c]:.6g}' for c in cols))


if __name__ == '__main__':
    main(sys.argv[1:])
