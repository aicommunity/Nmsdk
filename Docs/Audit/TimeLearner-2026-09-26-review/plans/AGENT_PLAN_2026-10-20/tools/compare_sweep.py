#!/usr/bin/env python3
"""C2: compare a fresh sweep.jsonl with the expected one. Usage: compare_sweep.py expected.jsonl got.jsonl
Match key (tau_ms, D_ms, S_ms). L must be equal; margins (m_equal, m_ampnorm, m_oracle) within 0.005."""
import json
import sys


def load(p):
    out = {}
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if line.startswith('{'):
            d = json.loads(line)
            out[(d['tau_ms'], d['D_ms'], d['S_ms'])] = d
    return out


e, g = load(sys.argv[1]), load(sys.argv[2])
bad = 0
for k in sorted(e):
    if k not in g:
        print('MISSING', k); bad += 1; continue
    diffs = []
    if e[k].get('L') != g[k].get('L'):
        diffs.append(f"L {e[k].get('L')} != {g[k].get('L')}")
    for m in ('m_equal', 'm_ampnorm', 'm_oracle'):
        if abs(float(e[k][m]) - float(g[k][m])) > 0.005:
            diffs.append(f'{m} {e[k][m]} != {g[k][m]}')
    print(('OK   ' if not diffs else 'DIFF ') + str(k) + ('' if not diffs else '  ' + '; '.join(diffs)))
    bad += bool(diffs)
print('C2_MATCH' if not bad else f'C2_DIFF {bad}')
sys.exit(1 if bad else 0)
