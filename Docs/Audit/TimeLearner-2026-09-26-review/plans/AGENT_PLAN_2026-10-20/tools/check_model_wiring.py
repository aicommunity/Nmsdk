#!/usr/bin/env python3
"""Check TimeLearner Model_00.xml wiring.
Rules: (1) every ExcSynapse/InhSynapse drives SynapticInputs of exactly one channel and that channel
is in the same membrane; (2) Classic: Generator1 feeds exactly one segment per dendrite, the tip
(max segment index present); Branch: at most one segment per pulse (no duplicates).
Exit code 0 = OK, 1 = violations. Usage: check_model_wiring.py Model_00.xml [Parameters_00.xml] [--json]
With Parameters: taps must equal DendriteLength (Classic: one per dendrite; Branch: set of segments)."""
import re, sys, json, collections
def analyze(path, params_path=None):
    params_lengths = None
    if params_path:
        pt = open(params_path, encoding='utf-8', errors='replace').read()
        m = re.search(r'<DendriteLength [^>]*>([^<]*)<', pt)
        if m: params_lengths = [int(x) for x in m.group(1).split()]
    s = open(path, encoding='utf-8', errors='replace').read()
    branch = 'NeuronTimeLearnerBranch' in s
    syn = collections.defaultdict(set); gen = collections.Counter()
    for l in re.findall(r'<elem Type="ULink">(.*?)</elem>', s, re.S):
        it = re.search(r'Name="[^"]+">([^<]+)</Item>', l)
        if not it: continue
        src = it.group(1)
        for a, c in re.findall(r'Name="([^"]+)">([^<]+)</Connector>', l):
            if a == 'SynapticInputs' and 'Synapse' in src: syn[src].add(c)
            if a == 'Input' and src.endswith('Generator1'): gen[c] += 1
    seg = re.compile(r'Dendrite(\d+)_(\d+)\.(?:Exc|Inh)Synapse\d+$')
    segs_present = collections.defaultdict(set)
    for m in re.finditer(r'<Dendrite(\d+)_(\d+) Class=', s): segs_present[int(m.group(1))].add(int(m.group(2)))
    viol = []
    for k, v in syn.items():
        if len(v) != 1: viol.append(f'synapse_fanout {k.split("Neuron.")[-1]} -> {len(v)} channels')
        else:
            ch = next(iter(v)); mk = re.search(r'\.(Dendrite\d+_\d+|Soma\d+)\.', k); mc = re.search(r'\.(Dendrite\d+_\d+|Soma\d+)\.', ch)
            if mk and mc and mk.group(1) != mc.group(1): viol.append(f'synapse_cross_membrane {mk.group(1)} -> {mc.group(1)}')
    for c, n in gen.items():
        if n > 1: viol.append(f'generator_duplicate_link {c.split("Neuron.")[-1]} x{n}')
    per_d = collections.defaultdict(set)
    for c in gen:
        m = seg.search(c)
        if m and 'ExcSynapse' in c: per_d[int(m.group(1))].add(int(m.group(2)))
    if not branch:
        for d, ss in per_d.items():
            if len(ss) != 1: viol.append(f'classic_dendrite{d}_generator_taps {sorted(ss)} (expected exactly one tap)')
    if params_lengths:
        if branch:
            want = sorted(set(params_lengths)); got = sorted(per_d.get(1, set()))
            if got != want: viol.append(f'branch_taps {got} != DendriteLength {params_lengths}')
        else:
            for d, L in enumerate(params_lengths, start=1):
                got = sorted(per_d.get(d, set()))
                if got != [L]: viol.append(f'classic_dendrite{d}_taps {got} != DendriteLength {L}')
    return {'file': path, 'trainer': 'Branch' if branch else 'Classic', 'dendrite_lengths': {d: max(v) for d, v in segs_present.items()},
            'generator_exc_taps': {d: sorted(v) for d, v in per_d.items()}, 'params_dendrite_length': params_lengths, 'violations': viol, 'ok': not viol}
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args or '--help' in sys.argv or '-h' in sys.argv:
        print('usage: check_model_wiring.py Model_00.xml [Parameters_00.xml] [--json]\n'
              'exit 0 = OK, 1 = FAIL (violations printed), 2 = usage error')
        sys.exit(2)
    r = analyze(args[0], args[1] if len(args) > 1 else None)
    print(json.dumps(r, ensure_ascii=False, indent=1) if '--json' in sys.argv else ('OK' if r['ok'] else 'FAIL') + ' ' + r['file'] + ('' if r['ok'] else '\n  ' + '\n  '.join(r['violations'][:20])))
    sys.exit(0 if r['ok'] else 1)
