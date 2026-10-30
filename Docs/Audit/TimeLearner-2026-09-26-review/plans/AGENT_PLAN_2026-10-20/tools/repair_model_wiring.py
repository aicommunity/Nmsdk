#!/usr/bin/env python3
"""Repair TimeLearner Model_00.xml wiring damaged by Bin repro_cold_lib.fix_generator_tip_links (A15).

Textual repair of <Links> only; every other byte of the file is preserved. Fixes:
  1. synapse->channel links whose synapse membrane differs from the channel membrane
     (fix_generator_tip_links renamed the Item): the Item is renamed back to the channel's membrane;
  2. duplicate connectors / duplicate link elements;
  3. with --params Parameters_00.xml: Generator1 -> ExcSynapse taps are made to match DendriteLength
     (Classic: exactly one tap DendriteD_L(D) per dendrite D; Branch: segments in set(DendriteLength)).
     Stale taps are removed, missing taps are added, each tap appears once across all Generator1 links.
Usage: repair_model_wiring.py IN_Model_00.xml OUT_Model_00.xml [--params Parameters_00.xml]
Prints a JSON summary. OUT may equal IN. Exit code 0 always when the file was written.
"""
import re
import sys
import json

ELEM = re.compile(r'<elem Type="ULink">(.*?)</elem>', re.S)
ITEM = re.compile(r'<Item Type="ULinkSide" Index="[^"]*" Name="([^"]+)">([^<]+)</Item>')
CONN = re.compile(r'<Connector Type="ULinkSide" Index="([^"]*)" Name="([^"]+)">([^<]+)</Connector>')
MEMB = re.compile(r'\.(Dendrite\d+_\d+|Soma\d+)\.')
SYN = re.compile(r'^(.*\.)(Dendrite\d+_\d+|Soma\d+)(\.(?:Exc|Inh)Synapse\d+)$')
TAP = re.compile(r'Dendrite(\d+)_(\d+)\.ExcSynapse\d+$')


def fmt(item_name, item, conns, ib):
    lines = [f'{ib}<Item Type="ULinkSide" Index="-1" Name="{item_name}">{item}</Item>']
    lines += [f'{ib}<Connector Type="ULinkSide" Index="{idx}" Name="{n}">{c}</Connector>'
              for idx, n, c in conns]
    return '<elem Type="ULink">\n' + '\n'.join(lines) + '\n' + ib[:-1] + '</elem>'


def repair(text, lengths=None):
    branch = 'NeuronTimeLearnerBranch' in text
    st = {'renamed_items': 0, 'split_elems': 0, 'dup_connectors_removed': 0,
          'stale_taps_removed': 0, 'missing_taps_added': 0, 'dup_elems_removed': 0}
    parsed = []
    for m in ELEM.finditer(text):
        body = m.group(1)
        ind = re.search(r'\n(\s*)<Item', body)
        parsed.append({'m': m, 'item': ITEM.search(body),
                       'ib': ind.group(1) if ind else '\t\t\t\t',
                       'conns': [(c.group(1), c.group(2), c.group(3)) for c in CONN.finditer(body)]})
    want = None
    if lengths:
        want = ({(1, L) for L in set(lengths)} if branch
                else {(d + 1, L) for d, L in enumerate(lengths)})
    prefix = None
    first_gen = None
    for p in parsed:
        if p['item'] and p['item'].group(2).endswith('Generator1'):
            for _, n, c in p['conns']:
                if n == 'Input' and TAP.search(c):
                    prefix = c[:c.index('Dendrite')]
                    if first_gen is None:
                        first_gen = p
    if prefix is None:
        prefix = ('NeuronTimeLearnerBranch' if branch else 'NeuronTimeLearner') + '.Neuron.'

    have_taps = set()
    for p in parsed:
        im = p['item']
        if not im:
            continue
        src = im.group(2)
        conns = []
        for c in p['conns']:
            if c in conns:
                st['dup_connectors_removed'] += 1
                continue
            conns.append(c)
        sm = SYN.match(src)
        if sm and conns and all(n == 'SynapticInputs' for _, n, _ in conns):
            groups = {}
            for c in conns:
                mm = MEMB.search(c[2])
                memb = mm.group(1) if mm else sm.group(2)
                groups.setdefault(memb, []).append(c)
            new = []
            for memb, cs in groups.items():
                if memb != sm.group(2):
                    st['renamed_items'] += 1
                new.append((sm.group(1) + memb + sm.group(3), cs))
            if len(groups) > 1:
                st['split_elems'] += 1
            p['new'] = new
        elif src.endswith('Generator1') and want is not None:
            keep = []
            for c in conns:
                tm = TAP.search(c[2]) if c[1] == 'Input' else None
                if tm:
                    key = (int(tm.group(1)), int(tm.group(2)))
                    if key not in want:
                        st['stale_taps_removed'] += 1
                        continue
                    if key in have_taps:
                        st['dup_connectors_removed'] += 1
                        continue
                    have_taps.add(key)
                keep.append(c)
            p['new'] = [(src, keep)]
        else:
            p['new'] = [(src, conns)]

    if want is not None and first_gen is not None:
        for d, L in sorted(want - have_taps):
            first_gen['new'][0][1].append(('-1', 'Input', f'{prefix}Dendrite{d}_{L}.ExcSynapse1'))
            st['missing_taps_added'] += 1

    seen = set()
    edits = []
    for p in parsed:
        if 'new' not in p:
            continue
        src = p['item'].group(2)
        reps = []
        for item, cs in p['new']:
            key = (p['item'].group(1), item, tuple(cs))
            if key in seen:
                st['dup_elems_removed'] += 1
                continue
            seen.add(key)
            reps.append((item, cs))
        unchanged = (len(reps) == 1 and reps[0][0] == src and reps[0][1] == p['conns'])
        if unchanged:
            continue
        sep = '\n' + p['ib'][:-1]
        rep = sep.join(fmt(p['item'].group(1), item, cs, p['ib']) for item, cs in reps if cs)
        edits.append((p['m'].start(), p['m'].end(), rep))

    new = text
    for s, e, rep in sorted(edits, reverse=True):
        if rep:
            new = new[:s] + rep + new[e:]
        else:
            ws = re.search(r'\s*$', new[:s]).group(0)
            new = new[:s - len(ws)] + new[e:]
    n = len(ELEM.findall(new))
    if new != text:
        new = re.sub(r'(<Links Type="ULinksList" Size=")\d+(")',
                     lambda m: m.group(1) + str(n) + m.group(2), new, count=1)
    st['links_after'] = n
    return new, st


def main(argv):
    args = list(argv)
    params = None
    if '--params' in args:
        i = args.index('--params')
        params = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    src, dst = args
    lengths = None
    if params:
        pt = open(params, encoding='utf-8', errors='replace').read()
        m = re.search(r'<DendriteLength [^>]*>([^<]*)<', pt)
        lengths = [int(x) for x in m.group(1).split()] if m else None
    text = open(src, encoding='utf-8', errors='replace', newline='').read()
    new, st = repair(text, lengths)
    st.update({'in': src, 'out': dst, 'dendrite_length': lengths, 'changed': new != text})
    with open(dst, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
    print(json.dumps(st, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1:])
