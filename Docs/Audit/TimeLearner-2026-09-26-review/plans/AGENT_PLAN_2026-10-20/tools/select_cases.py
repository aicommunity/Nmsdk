#!/usr/bin/env python3
"""List registered matrix cases with their factors (for G1 planning). No side effects.
Usage: select_cases.py <StructTrain dir> [--trainer Classic|Branch] [--norm 0|1] [--span MS] [--psi off|on]
                       [--exclude-tsv cards/data/A2_expected_test_failures.tsv]
Output TSV: wave case trainer span_ms norm psi nextseg template neuron_hint
"""
import json
import sys
from pathlib import Path


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


st = Path(sys.argv[1])
m = json.loads((st / 'TimeLearnerMatrix' / 'matrix.json').read_text(encoding='utf-8'))
cases = m['cases'] if 'cases' in m else [c for w in m.get('waves', []) for c in w.get('cases', [])]
excl = set()
if arg('--exclude-tsv'):
    for line in Path(arg('--exclude-tsv')).read_text(encoding='utf-8').splitlines()[1:]:
        excl.add(line.split('\t')[0].rstrip('/').split('/')[-1])
tr = {'Classic': 'NNeuronTimeLearner', 'Branch': 'NNeuronTimeLearnerBranch'}.get(arg('--trainer'))
print('wave\tcase\ttrainer\tspan_ms\tnorm\tpsi\tnextseg\ttemplate\texcluded_A15')
for c in cases:
    if tr and c.get('trainer') != tr:
        continue
    if arg('--norm') is not None and str(c.get('normalization_mode')) != arg('--norm'):
        continue
    if arg('--span') is not None and str(c.get('duration_ms')) != arg('--span'):
        continue
    psi = 'on' if c.get('presynaptic_inhibition') else 'off'
    if arg('--psi') and psi != arg('--psi'):
        continue
    print('\t'.join(str(x) for x in (c.get('wave'), c.get('id'), (c.get('trainer') or '').replace('NNeuronTimeLearner', 'TL'),
                                      c.get('duration_ms'), c.get('normalization_mode'), psi, c.get('branch_nextseg'),
                                      c.get('template'), c.get('id') in excl)))
