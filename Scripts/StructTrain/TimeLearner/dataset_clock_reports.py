"""Real dataset clock controls; complete negative observations remain plottable.

This is a fixture-data adapter, not a classification scorer or native importer.
"""
import csv
import hashlib
import html
import io
import json
import math
from pathlib import Path
import re
import shutil
import sys

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, count, load, number, require
from .native_gate import FIELDS as GATE_FIELDS, audit_junit
from .plotting import padded_limits, plotting_runtime, render_soma


FIELDS = {'kind', 'schema_version', 'frequency_hz', 'mode', 'delay', 'origin', 'complete',
          'window_duration', 'sample_count', 'scheduled_isi', 'pulse_length', 'time_generation',
          'rising_edges', 'model', 'after_model', 'peak_abs_soma', 'trace', 'scientific_verdict'}


def _condition(identity):
    m = re.fullmatch(r'DatasetClockOrigin/(Continuous|Timed)(NoGap|FiveMs|ThirtyMs)At(2000|20000)', identity)
    if m:
        mode = 2 if m[1] == 'Continuous' else 1
        delay = {'NoGap': 0., 'FiveMs': .005, 'ThirtyMs': .03}[m[2]]
        frequency, tag, origins, near, cutoff = int(m[3]), '', [0., .1, 1.], False, False
    else:
        m = re.fullmatch(r'DatasetClockExtended/(Continuous|Timed|NearGrid|TimedFirstOnsetCutoff)At(2000|20000)', identity)
        require(m is not None, 'unknown_dataset_clock_case')
        frequency = int(m[2]); near = m[1] == 'NearGrid'; cutoff = m[1] == 'TimedFirstOnsetCutoff'
        mode = 1 if m[1] in ('Timed', 'TimedFirstOnsetCutoff') else 2
        delay, tag, origins = 0., '_near' if near else '_cutoff' if cutoff else '_long', [0., .1, 1., 86400., 1e9]
    return {'test_id': identity, 'frequency': frequency, 'mode': mode, 'delay': delay, 'origins': origins,
            'isi': [.01000001, .03999999] if near else [.01, .04], 'time_generation': .01 if cutoff else .18,
            'minimum_edges': 1 if cutoff else 4, 'first_tick': frequency//100+int(near),
            'stem': f'dataset_clock_{frequency}_mode{mode}_gap{round(delay*1000)}{tag}'}


def _identity(value):
    require(type(value) is dict and value.get('valid') is True and value.get('diagnostics') == []
            and value.get('kind') == 'semantic_model_identity' and type(value.get('schema_version')) is int
            and value['schema_version'] in (1, 2) and type(value['model']['schema_version']) is int
            and value['model']['schema_version'] == value['schema_version']
            and value.get('sha256') == canonical_model_sha256(value['model']), 'invalid_dataset_clock_model')
    return value['sha256']


def _trial(native, condition, index):
    stem = condition['stem']+f'_origin{index}'; path = native/(stem+'.json')
    trace = native/(stem+'.csv')
    require(path.is_file() and trace.is_file() and not path.is_symlink() and not trace.is_symlink(),
            'missing_dataset_clock_primary:'+stem)
    record = load(path); origin = condition['origins'][index]; frequency = condition['frequency']
    version = record.get('schema_version') if type(record) is dict else None
    require(type(record) is dict and type(version) is int and version in (1, 2)
            and set(record) == FIELDS | ({'assertion_contract', 'playback_phase'} if version == 2 else set())
            and record['kind'] == 'native_dataset_clock_observation',
            'unknown_dataset_clock_observation')
    if version == 2:
        require(record['assertion_contract'] == 'origin_and_pulse_program_v1'
                and record['playback_phase'] == 'before_children', 'unknown_dataset_clock_assertion_contract')
    require(type(record['frequency_hz']) is int and record['frequency_hz'] == frequency
            and type(record['mode']) is int and record['mode'] == condition['mode']
            and number(record['delay']) == condition['delay'] and number(record['origin']) == origin
            and record['complete'] is True and number(record['window_duration']) == .25
            and type(record['scheduled_isi']) is list and list(map(number, record['scheduled_isi'])) == condition['isi']
            and number(record['pulse_length']) == .001 and number(record['time_generation']) == condition['time_generation']
            and record['trace'] == trace.name and record['scientific_verdict'] is None,
            'dataset_clock_condition_mismatch')
    revision = _identity(record['model'])
    require(_identity(record['after_model']) == revision, 'dataset_clock_model_changed')
    require(all(node['frequency_hz'] == str(frequency) for node in record['model']['model']['nodes']),
            'dataset_clock_physical_frequency_mismatch')
    raw = trace.read_bytes(); rows = list(csv.reader(io.StringIO(raw.decode('utf-8'))))
    require(rows and rows[0] == ['time', 'stimulus', 'soma0'] and len(rows)-1 == frequency//4+1
            and count(record['sample_count']) == len(rows)-1, 'incomplete_dataset_clock_trace')
    samples, edges, was_high = [], [], False
    for tick, row in enumerate(rows[1:]):
        require(len(row) == 3 and all(token and token == token.strip() for token in row), 'corrupt_dataset_clock_row')
        time, stimulus, soma = [number(float(token)) for token in row]
        roundoff = max(1e-12, 32*sys.float_info.epsilon*max(1., abs(time), abs(origin)))
        require(abs((time-origin)-tick/frequency) <= roundoff, 'dataset_clock_sample_grid_mismatch')
        if stimulus > 0. and not was_high: edges.append({'tick': tick, 'time': time})
        was_high = stimulus > 0.; samples.append({'time': time, 'stimulus': stimulus, 'soma': [soma]})
    require(type(record['rising_edges']) is list and all(type(e) is dict and set(e) == {'tick', 'time'}
            and count(e['tick']) >= 0 and math.isfinite(number(e['time'])) for e in record['rising_edges']), 'invalid_dataset_clock_events')
    require(record['rising_edges'] == edges and len(edges) >= condition['minimum_edges'], 'dataset_clock_stimulus_events_mismatch')
    peak = max(abs(s['soma'][0]) for s in samples)
    require(peak == number(record['peak_abs_soma']) and
            max(s['soma'][0] for s in samples)-min(s['soma'][0] for s in samples) > 1e-6, 'dataset_clock_soma_witness_mismatch')
    period = frequency*51//1000+round(condition['delay']*frequency)
    first, last, width = condition['first_tick'], frequency//20, frequency//1000
    cutoff = round(condition['time_generation']*frequency)
    wrong = sum((s['stimulus'] > 0.) != ((condition['mode'] != 1 or tick <= cutoff) and
                (first <= tick % period < first+width or last <= tick % period < last+width))
                for tick, s in enumerate(samples))
    return {'stem': stem, 'record': record, 'samples': samples, 'revision': revision,
            'wrong_pulse_samples': wrong, 'first_tick_correct': count(edges[0]['tick']) == condition['first_tick'],
            'record_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'trace_sha256': hashlib.sha256(raw).hexdigest()}


def audit_dataset_clock(specification, artifacts):
    """Independently check declared recordings, including failed invariance cases."""
    try:
        root = Path(artifacts).resolve(strict=True); spec = load(Path(specification))
        require(type(spec) is dict and set(spec) == GATE_FIELDS
                and spec['kind'] == 'timelearner_native_test_gate' and type(spec['schema_version']) is int
                and spec['schema_version'] == 1, 'unknown_dataset_clock_specification')
        expected = spec['expected_test_ids']
        require(type(expected) is list and expected and len(expected) == len(set(expected)), 'invalid_dataset_clock_inventory')
        conditions = [_condition(identity) for identity in expected]
        gate = load(root/'specification.json'); result = load(root/'result.json')
        require(type(gate) is dict and set(gate) == GATE_FIELDS and gate['kind'] == 'timelearner_native_test_gate'
                and type(gate['schema_version']) is int and gate['schema_version'] == 1,
                'unknown_dataset_clock_source_gate')
        require(type(result) is dict and result['kind'] == 'timelearner_native_test_gate_result'
                and type(result['schema_version']) is int and result['schema_version'] == 1
                and result['scientific_verdict'] is None, 'unknown_dataset_clock_gate_result')
        inventory = audit_junit(root/'native.xml', gate['expected_test_ids'])
        require(set(expected) <= set(gate['expected_test_ids']) and result['validity'] == 'valid'
                and result['inventory'] == inventory and result['assertion_status'] == inventory['assertion_status']
                and result['execution'] == ('completed' if inventory['assertion_status'] == 'passed' else 'process_error'),
                'dataset_clock_gate_inventory_mismatch')
        require(all((root/n).is_file() and not (root/n).is_symlink() for n in
                    ('specification.json', 'result.json', 'runtime.json', 'native.xml'))
                and type(load(root/'runtime.json')) is dict, 'missing_dataset_clock_runtime_record')
        native = root/'native'; require(native.is_dir() and not native.is_symlink(), 'invalid_dataset_clock_primary_directory')
        cases = []; primary = set()
        for condition in conditions:
            trials = [_trial(native, condition, i) for i in range(len(condition['origins']))]
            require(len({t['revision'] for t in trials}) == 1, 'dataset_clock_models_differ_between_origins')
            versions = {t['record']['schema_version'] for t in trials}
            require(len(versions) == 1, 'dataset_clock_mixed_assertion_contracts')
            differences = []
            for trial in trials[1:]:
                pairs = list(zip(trials[0]['samples'], trial['samples']))
                differences.append({'origin': trial['record']['origin'],
                    'changed_input_samples': sum(a['stimulus'] != b['stimulus'] for a, b in pairs),
                    'changed_soma_samples': sum(a['soma'][0] != b['soma'][0] for a, b in pairs),
                    'maximum_soma_difference': max(abs(a['soma'][0]-b['soma'][0]) for a, b in pairs)})
            passed = all(d['changed_input_samples'] == d['changed_soma_samples'] == 0 for d in differences)
            program_passed = all(t['wrong_pulse_samples'] == 0 and t['first_tick_correct'] for t in trials)
            cpp_passed = condition['test_id'] not in inventory['failed_test_ids']
            if versions == {2}:
                require((passed and program_passed) == cpp_passed, 'dataset_clock_junit_measurements_disagree')
            else:
                # Legacy records did not declare the additional assertion set.
                # A positive C++ case still must satisfy its origin invariant;
                # an extra legacy failure is preserved as unknown, not invented.
                require(not cpp_passed or passed, 'dataset_clock_junit_measurements_disagree')
            primary.update(t['stem']+'.'+extension for t in trials for extension in ('json', 'csv'))
            cases.append({'condition': condition, 'trials': trials, 'differences': differences, 'invariant': passed,
                          'pulse_program_passed': program_passed, 'cpp_passed': cpp_passed,
                          'cpp_assertion_contract_verified': versions == {2} or (not passed and not cpp_passed) or cpp_passed})
        actual = {p.name for p in native.glob('dataset_clock_*')}
        require(actual == primary, 'dataset_clock_unrecorded_or_extra_primary')
        return {'cases': cases, 'reported_test_ids': expected, 'source_gate_inventory': inventory,
                'invariance_status': 'passed' if all(c['invariant'] for c in cases) else 'failed',
                'pulse_program_status': 'passed' if all(c['pulse_program_passed'] for c in cases) else 'failed',
                'cpp_assertion_contract_verified': all(c['cpp_assertion_contract_verified'] for c in cases),
                'observations': sum(len(c['trials']) for c in cases), 'scientific_verdict': None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OSError, OverflowError) as error:
        raise EvidenceError('malformed_dataset_clock_evidence:'+str(error)) from error


def render_dataset_clock_report(specification, artifacts, output):
    audited = audit_dataset_clock(specification, artifacts); backend = plotting_runtime()
    root = Path(artifacts).resolve(strict=True); output = Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(root) and not root.is_relative_to(output), 'dataset_clock_report_output_overlaps_source')
    output.mkdir(parents=True, exist_ok=False); (output/'primary').mkdir()
    for name in ('specification.json', 'result.json', 'native.xml', 'runtime.json'):
        shutil.copyfile(root/name, output/'primary'/name)
    shutil.copyfile(specification, output/'primary'/'report-contract.json')
    records = []; links = []
    for case in audited['cases']:
        limits = padded_limits([s['soma'][0] for t in case['trials'] for s in t['samples']])
        for trial in case['trials']:
            destination = output/trial['stem']; destination.mkdir()
            for extension in ('json', 'csv'):
                shutil.copyfile(root/'native'/(trial['stem']+'.'+extension), output/'primary'/(trial['stem']+'.'+extension))
            record = trial['record']; condition = case['condition']
            observation = {'samples': trial['samples'], 'frequency_hz': condition['frequency'],
                'begin': record['origin'], 'end': record['origin']+.25, 'closed_at': trial['samples'][-1]['time'],
                'complete': True, 'valid': True, 'spike_times': [], 'model_before': trial['revision'],
                'sample_id': condition['test_id'], 'trial_id': trial['stem'], 'label': 'Dataset playback characterisation',
                'reset_policy': 'independent native physical Reset; LT events not collected'}
            views = render_soma(observation, 0, 'Soma1 SumPotential', limits, destination,
                context_label=f"Origin={record['origin']}s | origin={'PASS' if case['invariant'] else 'FAIL'}; pulse program={'PASS' if case['pulse_program_passed'] else 'FAIL'}; no classification verdict")
            records.append({'test_id': condition['test_id'], 'origin': record['origin'], 'model_revision': trial['revision'],
                'source_record': 'primary/'+trial['stem']+'.json', 'source_record_sha256': trial['record_sha256'],
                'source_trace': 'primary/'+trial['stem']+'.csv', 'source_trace_sha256': trial['trace_sha256'],
                'spikes_recorded': False, 'invariant': case['invariant'], 'differences': case['differences'],
                'pulse_program_passed': case['pulse_program_passed'], 'wrong_pulse_samples': trial['wrong_pulse_samples'],
                'directory': trial['stem'], 'views': views})
            links.append(f'<li>{html.escape(trial["stem"])}: <a href="{trial["stem"]}/overview.png">overview</a> | invariance {case["invariant"]}</li>')
    manifest = {'kind': 'timelearner_dataset_clock_report', 'schema_version': 1, 'backend': backend,
                'renderer_files_sha256': {name: hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
                    for name in ('dataset_clock_reports.py', 'plotting.py', 'native_gate.py', 'native_evidence.py', 'model_identity.py')},
                'reported_test_ids': audited['reported_test_ids'], 'source_gate_inventory': audited['source_gate_inventory'],
                'invariance_status': audited['invariance_status'], 'observations': audited['observations'], 'records': records,
                'pulse_program_status': audited['pulse_program_status'],
                'cpp_assertion_contract_verified': audited['cpp_assertion_contract_verified'],
                'all_gate_tests_reported': set(audited['reported_test_ids']) == set(load(root/'specification.json')['expected_test_ids']),
                'scientific_verdict': None, 'global_visual_acceptance': False}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><h1>Dataset clock controls</h1>'
        '<p>Full native input/soma samples; no classification verdict. LT events were not collected. Shared Y per condition. '
        'Zooms retain at least 14 pixels per native tick; all PNG/SVG/PDF views are listed in manifest.json.</p><ul>'+''.join(links)+'</ul>', encoding='utf-8')
    checksums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob('*')) if p.is_file()}
    (output/'SHA256SUMS.json').write_text(json.dumps(checksums, indent=2)+'\n', encoding='utf-8')
    return manifest
