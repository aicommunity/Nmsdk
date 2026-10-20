#!/usr/bin/env python3
"""Compact per-case summary of a queue run (reads every matrix_result.json under a RUN dir).

Usage: summarize_run.py "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID" [--json out.json]
Columns: wave case attempt train_status training_convergence fires separation detection
         DendriteLength TipSynapseResistance FixedLTZThreshold metrics
Fields missing in a result are printed as '-'; nothing is inferred.
"""
import json
import sys
from pathlib import Path

KEYS = ('train_status', 'training_convergence', 'fires', 'separation_quality', 'detection_quality')


def flat(d):
    r = d.get('result') if isinstance(d.get('result'), dict) else d
    after = r.get('after') or {}
    return {
        'case': r.get('case') or d.get('case') or '-',
        **{k: r.get(k) if r.get(k) not in (None, '') else '-' for k in KEYS},
        'DendriteLength': after.get('DendriteLength', '-') or '-',
        'TipSynapseResistance': after.get('TipSynapseResistance', '-') or '-',
        'FixedLTZThreshold': after.get('FixedLTZThreshold', '-') or '-',
        'metrics': r.get('metrics') or '-',
        'runtime_execution_options': d.get('runtime_execution_options') or r.get('runtime_execution_options'),
    }


def main(argv):
    if not argv:
        sys.exit(__doc__)
    root = Path(argv[0])
    rows = []
    for p in sorted(root.rglob('matrix_result.json')):
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:  # keep going, report the broken file
            rows.append({'file': str(p), 'error': repr(e)})
            continue
        row = flat(d)
        parts = p.relative_to(root).parts
        row['wave'] = parts[0] if len(parts) > 3 else '-'
        row['attempt'] = p.parent.name
        row['file'] = str(p)
        rows.append(row)
    if not rows:
        print('NO_RESULTS under', root)
        sys.exit(1)
    cols = ('wave', 'case', 'attempt') + KEYS + ('DendriteLength', 'TipSynapseResistance', 'FixedLTZThreshold', 'metrics')
    print('\t'.join(cols))
    for r in rows:
        print('\t'.join(str(r.get(c, 'ERR')) for c in cols) if 'error' not in r else f"ERROR\t{r['file']}\t{r['error']}")
    if '--json' in argv:
        Path(argv[argv.index('--json') + 1]).write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1:])
