#!/usr/bin/env python3
"""A2: audit wiring of every TimeLearnerMatrix input (no Console).

Usage: audit_matrix_wiring.py <StructTrain dir> [--side Test|Train|both] [--out audit.tsv]
Output TSV: side  case_dir  status  n_violations  categories  first_violation
Summary lines at the end: TOTAL <side> <n>  FAIL <side> <n>.  Exit 0 always (it is a report).
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_model_wiring  # noqa: E402


def category(v):
    if v.startswith('synapse_fanout'):
        return 'synapse_fanout'
    if v.startswith('generator_duplicate_link'):
        return 'generator_duplicate_link'
    if v.startswith('classic_dendrite') and 'generator_taps' in v:
        return 'classic_multi_tap'
    if v.startswith('classic_dendrite') and '_taps' in v:
        return 'taps_ne_DendriteLength'
    return v.split()[0]


def main(argv):
    if not argv:
        sys.exit(__doc__)
    root = Path(argv[0])
    side = argv[argv.index('--side') + 1] if '--side' in argv else 'Test'
    sides = ['Test', 'Train'] if side == 'both' else [side]
    lines, totals, fails = [], Counter(), Counter()
    for s in sides:
        for m in sorted(root.glob(f'TimeLearnerMatrix/**/inputs/*/{s}/Model_00.xml')):
            params = m.parent / 'Parameters_00.xml'
            if not params.is_file():
                continue
            r = check_model_wiring.analyze(str(m), str(params))
            totals[s] += 1
            case_dir = str(m.parent.parent.relative_to(root))
            if r['ok']:
                lines.append(f'{s}\t{case_dir}\tOK\t0\t-\t-')
            else:
                fails[s] += 1
                cats = ','.join(sorted({category(v) for v in r['violations']}))
                lines.append(f"{s}\t{case_dir}\tFAIL\t{len(r['violations'])}\t{cats}\t{r['violations'][0]}")
    out = '\n'.join(['side\tcase_dir\tstatus\tn_violations\tcategories\tfirst_violation'] + lines)
    out += '\n' + '\n'.join(f'TOTAL {s} {totals[s]}\nFAIL {s} {fails[s]}' for s in sides) + '\n'
    if '--out' in argv:
        Path(argv[argv.index('--out') + 1]).write_text(out, encoding='utf-8')
    print(out[-400:] if '--out' in argv else out)


if __name__ == '__main__':
    main(sys.argv[1:])
