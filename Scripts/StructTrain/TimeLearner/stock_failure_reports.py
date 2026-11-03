"""Audited stock training failure boundaries, with native soma/input plots.

This is an observation/search diagnostic. It neither repairs a missing wave nor
changes the training certificate, historical criterion or recognition verdict.
"""
import hashlib
import html
from pathlib import Path
import re
import shutil

from .model_identity import canonical_model_sha256
from .native_evidence import audit_probe, load, require
from .n1_protocol_robustness import _inventory, _write
from .probe_diagnostics import audit_recorded_wave_diagnostics, read_partial_probe


def select_failure_boundary(native):
    """Select from an audited run by actual sequence and physical input."""
    native = Path(native)
    execution = load(native/'execution.json')
    require(execution['training_outcome'] == 'invalid_observation' and
            execution['completed_boundary'] is False, 'stock_failure_requires_invalid_train')
    require(execution['package_path'] == 'train_stopped_state.json', 'stock_failure_unknown_package')
    summary = load(native/'train_stopped_summary.json')
    require(summary['outcome'] == 'invalid_observation' and summary['certificate'] is None,
            'stock_failure_summary_has_certificate_or_other_outcome')
    packets = []
    for path in native.glob('train_stopped_trial_*.json'):
        match = re.fullmatch(r'train_stopped_trial_(\d+)\.json', path.name)
        require(match is not None and not path.is_symlink(), 'stock_failure_invalid_probe_filename')
        packet = load(path)
        observation = packet.get('observation')
        require(type(observation) is dict and type(packet.get('prepared')) is dict,
                'stock_failure_unobserved_probe_requires_separate_diagnostic')
        packets.append((int(match[1]), path, packet))
    require(bool(packets), 'stock_failure_no_recorded_probes')
    packets.sort(key=lambda row: row[0])
    require(len({row[0] for row in packets}) == len(packets), 'stock_failure_duplicate_probe_sequence')
    ids = [row[2]['observation']['specification']['trial_id'] for row in packets]
    require(len(set(ids)) == len(ids), 'stock_failure_duplicate_trial_id')
    _, last, terminal = packets[-1]
    require(terminal['observation']['valid'] is False, 'stock_failure_last_probe_is_not_invalid')
    input_id = terminal['prepared']['input_id']
    require(re.fullmatch(r'input\d+', input_id) is not None, 'stock_failure_unknown_input_id')
    index = int(input_id[5:])
    require(index < len(summary['actual_parameters']), 'stock_failure_input_index_out_of_range')
    selected = []
    preceding = [row for row in packets[:-1] if row[2]['prepared']['input_id'] == input_id and
                 row[2]['observation']['valid'] is True]
    if preceding:
        _, previous, packet = preceding[-1]
        selected.append(('last-valid-same-input', previous, packet))
    selected.append(('terminal-invalid', last, terminal))
    records = []
    for role, path, packet in selected:
        trace = path.with_suffix('.csv')
        require(not trace.is_symlink() and trace.is_file(), 'stock_failure_trace_missing_or_symlink')
        audit = audit_probe(packet, trace)
        require(audit['valid_observation'] is (role == 'last-valid-same-input'),
                'stock_failure_selected_packet_audit_changed')
        diagnostic = None
        if role == 'terminal-invalid':
            observation, spec, _, samples, _, quality = read_partial_probe(packet, trace)
            diagnostic = {'trace_quality': quality,
                          'wave_arrays': audit_recorded_wave_diagnostics(observation, spec, samples, quality)}
        observation = packet['observation'];spec = observation['specification']
        candidate = next((e for e in summary['candidates'] if e['trial_id'] == spec['trial_id']), None)
        records.append({'role': role, 'packet': path.name, 'trace': trace.name,
            'trial_id': spec['trial_id'], 'input_id': input_id, 'input_index': index,
            'is_measured_search_candidate': candidate is not None,
            'candidate_parameters': candidate['full_parameters'] if candidate is not None else None,
            'complete': observation['complete'], 'valid': observation['valid'],
            'observation_reasons': observation['reasons'],
            'stimulus_count': len(observation['stimuli']),
            'burst_assignments': observation['burst_assignments'],
            'base_model_revision': packet['prepared']['base_model_revision'],
            'effective_model_revision': spec['effective_model_revision'],
            'packet_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'trace_sha256': hashlib.sha256(trace.read_bytes()).hexdigest(), 'audit': audit,
            'invalid_probe_diagnostics': diagnostic})
    require(len(summary['rejections']) >= 1 and
            summary['rejections'][-1]['trial_id'] == records[-1]['trial_id'],
            'stock_failure_terminal_rejection_mismatch')
    return {'input_id': input_id, 'input_index': index,
        'has_preceding_valid_same_input_probe': bool(preceding),
        'actual_terminal_parameters': summary['actual_parameters'],
        'maximum_invalid_observations': summary['configuration']['maximum_invalid_observations'],
        'training_outcome': execution['training_outcome'], 'certificate': None, 'probes': records}


def render_failure_report(directory, output):
    from .probe_reports import render_probe_set
    from .stock_threshold_study import audit
    directory, output = Path(directory).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(directory) and
            not directory.is_relative_to(output), 'stock_failure_requires_separate_new_cache')
    before = _inventory(directory)
    analysis = audit(directory)
    prepared = [(row, select_failure_boundary(directory/'runs'/row['name']/'native'))
                for row in analysis['rows']]
    output.mkdir(parents=True)
    _write(output/'analysis.json', analysis)
    reports, links, pairs = [], [], 0
    for row, selection in prepared:
        name = row['name'];native = directory/'runs'/name/'native'
        sources = output/'primary'/name;sources.mkdir(parents=True)
        trials = []
        for selected in selection['probes']:
            for kind in ('packet', 'trace'):
                path = native/selected[kind]
                require(not path.is_symlink() and path.is_file(), 'stock_failure_source_missing_or_symlink')
                shutil.copyfile(path, sources/path.name)
            trials.append({'trial_id': selected['trial_id'], 'packet': selected['packet'], 'trace': selected['trace']})
        spec = {'kind': 'timelearner_probe_report_spec', 'schema_version': 2,
                'observation_policy': 'complete_or_partial', 'trials': trials}
        _write(sources/'specification.json', spec)
        result = render_probe_set(sources/'specification.json', output/name)
        pairs += result['trial_soma_pairs']
        reports.append({**row, 'selection': selection, 'report': result, 'index': name+'/index.html'})
        links.append('<li><a href="'+html.escape(name, quote=True)+'/index.html">'+html.escape(name)+'</a></li>')
    require(before == _inventory(directory), 'stock_failure_source_changed_during_report')
    manifest = {'kind': 'stock_training_failure_temporal_report', 'schema_version': 1,
        'source_analysis_sha256': canonical_model_sha256(analysis), 'reports': reports,
        'trial_soma_pairs': pairs, 'physics_profile': 'stock-four-input-NSPNeuronGen-without-LTMembrane',
        'native_rerun': False, 'training_completed': False, 'calibration_performed': False,
        'visual_acceptance_complete': False, 'scientific_verdict': None}
    _write(output/'manifest.json', manifest)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Stock training failure boundaries</title>'
        '<style>body{font:18px sans-serif;margin:2em}</style><h1>Actual stock training failure boundaries</h1>'
        '<p>Last recorded invalid probe and last preceding valid probe of the same physical input, when present. '
        'Four cold stock conditions, original thresholds0.0117/100 and original search domains/tolerances. '
        'Missing preceding evidence stays absent. Valid observation does not imply convergence or classification. '
        'No Train, calibration or Test was rerun.</p><p>All recorded somas, actual input overlays, common per-soma '
        'axes within each comparison, full overviews and100-tick zooms. Sources and measured wave assignments '
        'are retained. Missing wave is not equivalent to zero membrane response. SI units remain unverified.</p><ul>'
        +''.join(links)+'</ul>', encoding='utf-8')
    _write(output/'SHA256SUMS.json', {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in sorted(output.rglob('*')) if p.is_file()})
    return manifest
