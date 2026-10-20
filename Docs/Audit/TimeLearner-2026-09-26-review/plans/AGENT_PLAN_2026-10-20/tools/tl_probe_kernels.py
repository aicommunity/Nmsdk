#!/usr/bin/env python3
"""Measure single-pulse soma kernels of a Classic NNeuronTimeLearner in NeuroModelerConsole
and compare them with the offline cable model (evidence/cable_model).

The probe is a Test-only run (IsNeedToTrain=0): four dendrites with given lengths, one pattern
whose four pulses are ISI seconds apart, so the response of dendrite d to pulse 0 is isolated in
[0, ISI) on soma_(d-1) of the analyzer trace (test_trace.csv).

Subcommands
  prepare  --template <Classic Test dir> --out <new dir> --lengths L1,L2,L3,L4 [--isi 2.0] [--tipr 8.6e7]
  analyze  --probe <dir after Console run> --cable-dir <evidence/cable_model> [--json out.json]
  enable-trace --dir <Test dir copy>   (switch on test_trace.csv only; used by task A3)

Console (run by the operator between prepare and analyze; see task C1):
  "$NMSDK_CONSOLE" -c <out>/Project.ini -s -t <ceil(3*ISI+2)> -x -S > <out>/console.log 2>&1

Only Python 3.8+ standard library is required (analyze also needs the compiled cable model).
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import repair_model_wiring  # noqa: E402
import check_model_wiring   # noqa: E402

LEARNER_BLOCK = re.compile(r'(<NeuronTimeLearner Class="NNeuronTimeLearner">.*?<Parameters>)(.*?)(</Parameters>)', re.S)
DATASET_BLOCK = re.compile(r'(<DatasetMatrix Class="NDatasetMatrix">.*?<Parameters>)(.*?)(</Parameters>)', re.S)


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def set_prop(body, name, value, typ, attrs=''):
    """Replace <name ...>...</name> keeping attributes (or replacing them if attrs given)."""
    pat = re.compile(rf'<{name}\b([^>]*)>.*?</{name}>', re.S)
    m = pat.search(body)
    if m:
        a = attrs if attrs else m.group(1)
        return body[:m.start()] + f'<{name}{a}>{value}</{name}>' + body[m.end():], True
    a = attrs if attrs else f' Type="{typ}" PType="257" IoType="17"'
    return body.rstrip() + f'\n\t\t\t\t\t<{name}{a}>{value}</{name}>\n\t\t\t\t', False


def matrix_attrs(rows, cols, elem='d'):
    return f' Type="MDMatrix&lt;{elem}&gt;" Rows="{rows}" Cols="{cols}" PType="257" IoType="17"'


def edit_file(path, lengths, isi, tipr, report):
    text = path.read_text(encoding='utf-8', errors='replace')
    pattern = '\n'.join(['0.0005', repr(isi), repr(isi), repr(isi)])
    lm = LEARNER_BLOCK.search(text)
    if not lm:
        raise SystemExit(f'{path}: no NNeuronTimeLearner block (this tool supports Classic only)')
    body = lm.group(2)
    learner_props = [
        ('IsNeedToTrain', '0', 'b', ''), ('StructureBuildMode', '1', 'i', ''),
        ('NormalizationMode', '1', 'i', ''), ('UseFixedLTZThreshold', '1', 'b', ''),
        ('FixedLTZThreshold', '100', 'd', ''), ('LTZThreshold', '100', 'd', ''),
        ('AutoCalibrateFixedLTZThreshold', '0', 'b', ''), ('EnablePostTrainTuning', '0', 'b', ''),
        ('EnablePostTrainMidThreshold', '0', 'b', ''),
        ('DendriteLength', ' '.join(map(str, lengths)), None,
         ' Type="simplevector" Size="4" elemType="i" PType="257" IoType="33"'),
        ('NumSynapse', '1 1 1 1', None, ' Type="simplevector" Size="4" elemType="i" PType="257" IoType="33"'),
        ('TipSynapseResistance', ' '.join([repr(tipr)] * 4), None,
         ' Type="simplevector" Size="4" elemType="d" PType="259" IoType="33"'),
        ('InputPattern', pattern, None, matrix_attrs(4, 1)),
    ]
    for name, val, typ, attrs in learner_props:
        body, existed = set_prop(body, name, val, typ, attrs)
        report.setdefault(path.name, []).append(f'{name}={"set" if existed else "added"}')
    text = text[:lm.start(2)] + body + text[lm.end(2):]
    dm = DATASET_BLOCK.search(text)
    if dm:
        db = dm.group(2)
        for name, val, attrs in [('MatrixData', pattern, matrix_attrs(4, 1)),
                                 ('MatrixClasses', '1', matrix_attrs(1, 1, 'i')),
                                 ('NumSamples', '1', ''), ('LoopSamples', '0', '')]:
            db, existed = set_prop(db, name, val, 'i' if name == 'NumSamples' else 'b', attrs)
            report.setdefault(path.name, []).append(f'Dataset.{name}={"set" if existed else "added"}')
        text = text[:dm.start(2)] + db + text[dm.end(2):]
    # tip synapse resistance on the actual tip components (Model and Parameters both carry them)
    for d, L in enumerate(lengths, start=1):
        pat = re.compile(rf'(<Dendrite{d}_{L} Class="[^"]+">.*?<ExcSynapse1 Class="[^"]+">.*?<Resistance Type="d"[^>]*>)[^<]*(</Resistance>)', re.S)
        text, n = pat.subn(lambda m: m.group(1) + repr(tipr) + m.group(2), text, count=1)
        report.setdefault(path.name, []).append(f'tip{d}_{L}_resistance={"set" if n else "MISSING_SEGMENT"}')
    path.write_text(text, encoding='utf-8')


def enable_trace(model):
    text = model.read_text(encoding='utf-8')
    comp = re.search(r'<PatternResponseAnalyzer\b[^>]*>.*?</PatternResponseAnalyzer\s*>', text, re.S)
    if not comp:
        raise SystemExit(f'{model}: no PatternResponseAnalyzer component; choose another template')
    block = comp.group(0)
    pm = re.search(r'(<Parameters\b[^>]*>)(.*?)(</Parameters\s*>)', block, re.S)
    body = pm.group(2)
    # same two properties as Bin repro_cold_lib.enable_pattern_response_trace
    for name, typ, val in (('TraceLogEnabled', 'b', '1'), ('TraceLogFileName', 'std::string', 'test_trace.csv')):
        body, _ = set_prop(body, name, val, typ)
    block2 = block[:pm.start(2)] + body + block[pm.end(2):]
    model.write_text(text[:comp.start()] + block2 + text[comp.end():], encoding='utf-8')


def cmd_prepare(a):
    tpl, out = Path(a.template), Path(a.out)
    lengths = [int(x) for x in a.lengths.split(',')]
    if len(lengths) != 4 or min(lengths) < 1:
        raise SystemExit('--lengths must be four positive integers')
    mt = (tpl / 'Model_00.xml').read_text(encoding='utf-8', errors='replace')
    avail = [max([int(x) for x in re.findall(rf'<Dendrite{d}_(\d+) Class', mt)] or [0]) for d in range(1, 5)]
    bad = [(d + 1, L, avail[d]) for d, L in enumerate(lengths) if L > avail[d]]
    if bad:
        raise SystemExit(f'LENGTH_TOO_LONG: template segments per dendrite = {avail}; requested {lengths}. '
                         f'Choose lengths <= available (offending: {bad}).')
    if out.exists():
        raise SystemExit(f'{out} exists; use a new directory')
    shutil.copytree(tpl, out)
    for junk in ('SelectivityLog', 'StatisticLog', 'EventsLog', 'posttune_complete.flag'):
        p = out / junk
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    report = {}
    for f in ('Parameters_00.xml', 'Model_00.xml'):
        edit_file(out / f, lengths, a.isi, a.tipr, report)
    enable_trace(out / 'Model_00.xml')
    rep_stats = []
    tpl_chk = check_model_wiring.analyze(str(tpl / 'Model_00.xml'))
    template_taps = {str(k): v for k, v in tpl_chk['generator_exc_taps'].items()}
    if not a.keep_links:
        with (out / 'Model_00.xml').open('r', encoding='utf-8', newline='') as f:
            text = f.read()
        new, st = repair_model_wiring.repair(text, lengths)
        with (out / 'Model_00.xml').open('w', encoding='utf-8', newline='') as f:
            f.write(new)
        rep_stats.append(st)
    chk = check_model_wiring.analyze(str(out / 'Model_00.xml'), str(out / 'Parameters_00.xml'))
    manifest = {'tool': 'tl_probe_kernels.py prepare', 'template': str(tpl), 'template_sha256': {
        f: sha256(tpl / f) for f in ('Parameters_00.xml', 'Model_00.xml', 'Project.ini') if (tpl / f).exists()},
        'lengths': lengths, 'keep_links': bool(a.keep_links), 'template_taps': template_taps, 'isi_s': a.isi, 'tipr_ohm': a.tipr, 'edits': report, 'wiring_repair': rep_stats,
        'wiring_check_before_run': chk,
        'prepared_sha256': {f: sha256(out / f) for f in ('Parameters_00.xml', 'Model_00.xml', 'Project.ini')},
        'console_t_s': math.ceil(3 * a.isi + 2), 'first_pulse_s': 0.0005}
    (out / 'probe_manifest.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding='utf-8')
    missing = [x for x in report.get('Model_00.xml', []) if 'MISSING' in x]  # Parameters_00 may lack segments; Model is authoritative
    print(json.dumps({'out': str(out), 'wiring_ok': chk['ok'], 'missing': missing,
                      'console_cmd': f'"$NMSDK_CONSOLE" -c "{out}/Project.ini" -s -t {manifest["console_t_s"]} -x -S > "{out}/console.log" 2>&1'},
                     ensure_ascii=False, indent=1))
    if missing or (not chk['ok'] and not a.keep_links):
        print('PREPARE_WARNING: see missing/wiring above; the template does not have these segments', file=sys.stderr)
        sys.exit(2)


def read_tag(text, name):
    m = re.search(rf'<{name}\b[^>]*>([^<]*)</{name}>', text)
    return m.group(1).strip() if m else None


def model_physics(model_text, d=1):
    blk = re.search(rf'<Dendrite{d}_1 Class="[^"]+">(.*?)</Dendrite{d}_1>', model_text, re.S)
    src = blk.group(1) if blk else model_text
    ch = re.search(r'<ExcChannel Class="[^"]+">(.*?)</ExcChannel>', src, re.S)
    chs = ch.group(1) if ch else src
    C = float(read_tag(chs, 'Capacity').replace(',', '.'))
    R = float(read_tag(chs, 'Resistance').replace(',', '.'))
    sy = re.search(r'<ExcSynapse1 Class="[^"]+">(.*?)</ExcSynapse1>', src, re.S)
    sys_ = sy.group(1) if sy else src
    D = float(read_tag(sys_, 'DissociationTC').replace(',', '.'))
    S = float((read_tag(sys_, 'SecretionTC') or '0.001').replace(',', '.'))
    return C, R, D, S


def kernel_stats(t, v):
    if not v:
        return None
    base = v[0]
    vv = [x - base for x in v]
    k = max(range(len(vv)), key=lambda i: vv[i])
    pk = vv[k]
    if pk <= 0:
        return {'peak': pk, 't_peak_s': None, 'fwhm_s': None}
    half = pk / 2
    lo = next(i for i in range(len(vv)) if vv[i] >= half)
    hi = max(i for i in range(len(vv)) if vv[i] >= half)
    return {'peak': pk, 't_peak_s': t[k], 'fwhm_s': t[hi] - t[lo], 'baseline': base}


def cmd_analyze(a):
    probe = Path(a.probe)
    man = json.loads((probe / 'probe_manifest.json').read_text(encoding='utf-8'))
    lengths, isi = man['lengths'], man['isi_s']
    traces = sorted(probe.rglob('test_trace.csv'))
    if not traces:
        raise SystemExit('NO_TRACE: test_trace.csv not found under probe dir; check console.log')
    rows = []
    with open(traces[0], encoding='utf-8') as f:
        header = f.readline().strip().split(',')
        for line in f:
            p = line.strip().split(',')
            if len(p) == len(header):
                rows.append(dict(zip(header, p)))
    rows = [r for r in rows if r['trial'] == rows[0]['trial']]
    traw = [float(r['time_rel_s']) for r in rows]
    # Pulse onset: the pattern puts pulse 0 at first_pulse_s inside the sample, but the trace time base
    # may carry an offset.  Detect onset as the first sample where any soma channel exceeds 1% of its
    # own peak inside the first ISI window (the shortest dendrite reacts within ~1 step), minus 1 step.
    ini0 = (probe / 'Project.ini').read_text(encoding='utf-8', errors='replace')
    f0 = int(re.search(r'<DefaultTimeStep>(\d+)<', ini0).group(1))
    onset = None
    for k in range(4):
        col = [float(r[f'soma_{k}']) for r in rows]
        base = col[0]
        win = [i for i, x in enumerate(traw) if x < traw[0] + 0.95 * isi]
        pk = max(col[i] - base for i in win) if win else 0.0
        if pk > 0:
            first = next(i for i in win if col[i] - base > 0.01 * pk)
            onset = traw[first] if onset is None else min(onset, traw[first])
    t0_nominal = man.get('first_pulse_s', 0.0005)
    t0 = (onset - 1.0 / f0) if onset is not None else t0_nominal
    t = [x - t0 for x in traw]
    sel = [i for i, x in enumerate(t) if 0.0 <= x < 0.95 * isi]
    model_text = (probe / 'Model_00.xml').read_text(encoding='utf-8', errors='replace')
    params_text = (probe / 'Parameters_00.xml').read_text(encoding='utf-8', errors='replace')
    ini = (probe / 'Project.ini').read_text(encoding='utf-8', errors='replace')
    f_hz = int(re.search(r'<DefaultTimeStep>(\d+)<', ini).group(1))
    C, R, D, S = model_physics(model_text)
    wiring_after = check_model_wiring.analyze(str(probe / 'Model_00.xml'), str(probe / 'Parameters_00.xml'))
    saved_lengths = [int(x) for x in (read_tag(params_text, 'DendriteLength') or '').split()]
    sys.path.insert(0, str(Path(a.cable_dir).resolve()))
    os.environ.setdefault('CABLE_SIM', str(Path(a.cable_dir).resolve() / 'cable'))
    import library  # noqa: E402
    out = {'probe': str(probe), 'trace': str(traces[0]), 'f_hz': f_hz,
           'pulse_onset_nominal_s': t0_nominal, 'pulse_onset_used_s': t0,
           'onset_offset_warning': abs(t0 - t0_nominal) > 2.0 / f_hz, 'C': C, 'Rm': R, 'tau_s': C * R,
           'D_s': D, 'secretion_s': S, 'lengths_requested': lengths, 'lengths_saved': saved_lengths,
           'wiring_after_run': {'ok': wiring_after['ok'], 'violations': wiring_after['violations'],
                                'taps': wiring_after['generator_exc_taps']}, 'dendrites': []}
    verdict_ok = wiring_after['ok'] and saved_lengths == lengths
    for d, L in enumerate(lengths):
        v = [float(rows[i][f'soma_{d}']) for i in sel]
        tt = [t[i] for i in sel]
        meas = kernel_stats(tt, v)
        tr = library.sim(L, [(L, man['tipr_ohm'], [0.0])], C * R, D, max(0.3, 0.95 * isi), f=f_hz, Rm=R, sub=1)
        pt = [i / f_hz for i in range(len(tr))]
        pred = kernel_stats(pt, [float(x) for x in tr])
        cmp = {}
        for key, tol in (('peak', 0.10), ('t_peak_s', 0.05), ('fwhm_s', 0.10)):
            mv, pv = (meas or {}).get(key), (pred or {}).get(key)
            if mv is None or pv in (None, 0):
                cmp[key] = {'measured': mv, 'predicted': pv, 'rel_err': None, 'ok': False}
            else:
                re_ = (mv - pv) / pv
                cmp[key] = {'measured': float(mv), 'predicted': float(pv), 'rel_err': float(re_), 'ok': bool(abs(re_) <= tol)}
        ok = all(c['ok'] for c in cmp.values())
        taps = man.get('template_taps', {}).get(str(d + 1)) or []
        if man.get('keep_links') and taps and meas and meas.get('t_peak_s') is not None:
            alt = {}
            for tap in sorted(set(taps) | {L}):
                trt = library.sim(tap, [(tap, man['tipr_ohm'], [0.0])], C * R, D, max(0.3, 0.95 * isi), f=f_hz, Rm=R, sub=1)
                ks = kernel_stats([i / f_hz for i in range(len(trt))], [float(x) for x in trt])
                alt[str(tap)] = ks['t_peak_s'] if ks else None
            best = min(alt, key=lambda k: abs((alt[k] or 1e9) - meas['t_peak_s']))
            cmp['relink_test'] = {'measured_t_peak_s': meas['t_peak_s'], 'predicted_t_peak_by_tap': alt,
                                  'best_matching_tap': int(best), 'requested_L': L, 'template_taps': taps,
                                  'ok': True}

        verdict_ok = verdict_ok and ok
        out['dendrites'].append({'dendrite': d + 1, 'L': L, 'compare': cmp, 'ok': ok})
    out['verdict'] = 'MODEL_MATCH' if verdict_ok else 'MODEL_MISMATCH_OR_INVALID'
    if man.get('keep_links'):
        bt = [x['compare'].get('relink_test', {}).get('best_matching_tap') for x in out['dendrites']]
        out['relink_verdict'] = ('CPP_RELINKS_TO_DENDRITELENGTH' if bt == lengths
                                 else 'CPP_KEEPS_XML_LINKS' if all(b in (man['template_taps'].get(str(i + 1)) or []) for i, b in enumerate(bt))
                                 else 'MIXED_OR_UNCLEAR')
        out['relink_best_taps'] = bt
    js = json.dumps(out, indent=1, ensure_ascii=False)
    if a.json:
        Path(a.json).write_text(js, encoding='utf-8')
    print(js)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--template', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--lengths', required=True)
    p.add_argument('--isi', type=float, default=2.0)
    p.add_argument('--tipr', type=float, default=8.6e7)
    p.add_argument('--keep-links', action='store_true',
                   help='A3: change DendriteLength but keep the template generator taps, to test C++ relinking')
    e = sub.add_parser('enable-trace', help='only switch on PatternResponseAnalyzer trace in DIR/Model_00.xml')
    e.add_argument('--dir', required=True)
    q = sub.add_parser('analyze')
    q.add_argument('--probe', required=True)
    q.add_argument('--cable-dir', required=True)
    q.add_argument('--json')
    a = ap.parse_args()
    if a.cmd == 'prepare':
        cmd_prepare(a)
    elif a.cmd == 'enable-trace':
        enable_trace(Path(a.dir) / 'Model_00.xml')
        print('TRACE_ENABLED', Path(a.dir) / 'Model_00.xml')
    else:
        cmd_analyze(a)


if __name__ == '__main__':
    main()
