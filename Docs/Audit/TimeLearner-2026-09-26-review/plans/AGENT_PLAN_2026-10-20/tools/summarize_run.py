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

KEYS = ('train_status', 'training_convergence', 'fires', 'separation_quality', 'detection_quality',
         'training_failure_reason', 'training_failure_phase')
EXTRA_METRIC_KEYS = ('sep_margin', 'margin', 'amp_over_target', 'delay_residue', 'sync_exit', 'done_be')


def flat(d):
    r = d.get('result') if isinstance(d.get('result'), dict) else d
    after = r.get('after') or {}
    metrics = r.get('metrics') if isinstance(r.get('metrics'), dict) else {}
    row = {
        'case': r.get('case') or d.get('case') or '-',
        **{k: r.get(k) if r.get(k) not in (None, '') else '-' for k in KEYS},
        'DendriteLength': after.get('DendriteLength', '-') or '-',
        'TipSynapseResistance': after.get('TipSynapseResistance', '-') or '-',
        'FixedLTZThreshold': after.get('FixedLTZThreshold', '-') or '-',
        'metrics': r.get('metrics') or '-',
        'runtime_execution_options': d.get('runtime_execution_options') or r.get('runtime_execution_options'),
    }
    # Stage0: prefer C++ Train emit (sep_margin), else gate selectivity peaks.
    sel = r.get('selectivity') if isinstance(r.get('selectivity'), dict) else {}
    explicit = r.get('sep_margin')
    if explicit in (None, ''):
        explicit = metrics.get('sep_margin')
    if explicit not in (None, ''):
        row['sep_margin'] = explicit
    else:
        tgt = sel.get('target_peak') or metrics.get('target_peak')
        foil = sel.get('max_foil_peak') or metrics.get('max_foil_peak')
        if tgt not in (None, '') and foil not in (None, ''):
            try:
                row['sep_margin'] = (float(tgt) - float(foil)) / float(tgt) if float(tgt) else '-'
            except Exception:
                row['sep_margin'] = '-'
        else:
            row['sep_margin'] = '-'
    for k in ('delay_residue', 'amp_over_target', 'sync_exit', 'done_be', 'amp_target_ratio',
              'sep_gap', 'sep_tgt', 'sep_max_foil'):
        row[k] = r.get(k) or metrics.get(k) or '-'
    return row



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
    cols = ('wave', 'case', 'attempt') + KEYS + ('DendriteLength', 'TipSynapseResistance', 'FixedLTZThreshold', 'sep_margin', 'delay_residue', 'amp_over_target', 'sync_exit', 'done_be', 'metrics')
    print('\t'.join(cols))
    for r in rows:
        print('\t'.join(str(r.get(c, 'ERR')) for c in cols) if 'error' not in r else f"ERROR\t{r['file']}\t{r['error']}")
    if '--json' in argv:
        Path(argv[argv.index('--json') + 1]).write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1:])
