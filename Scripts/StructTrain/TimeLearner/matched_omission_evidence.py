"""Independent reader of closed native matched-omission fixture evidence.

Recomputes the recorded operational method, not a causal theorem or Train
certificate. Schema1 fixture files do not include total budget declarations or
independent attestations of native object/reset ownership; those stay unknown.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath

from .native_evidence import (EvidenceError, after, count, load, measured_wave_plateaus,
                              number, require, require_primary_trace_clock)
from .response_domain_evidence import SPEC_FIELDS, _finite_json, _keys, _same, _text

METHOD = 'matched-omission-assigned-maximum-v1'
GROUP_FIELDS = ('schema_version kind method group_id native_probes packets traces reason assignment_validity '
                'training_certificate_eligible scientific_verdict source_pattern_sha256 reset_binding '
                'model_instance_binding physical_channel_paths assigned_input assigned_channel policy '
                'assignment_reasons maxima selected_full_maximum')
POLICY_FIELDS = ('comparison_radius_ticks time_comparison_tolerance baseline_absolute repeatability_absolute '
                 'repeatability_relative influence_absolute influence_relative')
MAXIMUM_FIELDS = ('first_sample last_sample amplitude raw_potential time plateau_end clipped '
                  'supported_inputs influence_by_input unknown precedes_assigned_stimulus')


def _dimension(value, reason='matched_invalid_dimension'):
    """Schema IDs and indices are JSON integers; real-valued measurements are not.

    The shared count contract also accepts integral floats. Do not change that
    contract or let its normalized return value mask an untyped original index.
    """
    require(type(value) is int, reason)
    return count(value)


def _maximum_dimensions(group, frames, inputs):
    maxima = group['maxima']; require(type(maxima) is list, 'matched_invalid_maxima')
    for maximum in maxima:
        _keys(maximum, MAXIMUM_FIELDS)
        first, last = (_dimension(maximum[key]) for key in ('first_sample', 'last_sample'))
        require(first <= last < frames, 'matched_maximum_sample_index')
        support = maximum['supported_inputs']; require(type(support) is list, 'matched_invalid_support_indices')
        for value in support: require(_dimension(value) < inputs, 'matched_support_input_index')
    selected = group['selected_full_maximum']
    if selected is not None:
        require(_dimension(selected) < len(maxima), 'matched_selected_maximum_index')


def _difference(a, b):
    return number(abs(a-b))


def _tolerance(absolute, relative, a, b):
    return number(absolute+relative*max(abs(a), abs(b)))


def _maxima(times, raw, baseline, minimum):
    signal = [number(v-baseline) for v in raw]
    regions = [(a, b, False) for a, b in measured_wave_plateaus(signal, minimum)]
    if signal[0] >= minimum and signal[0] >= signal[1]:
        last = 0
        while last+1 < len(signal) and signal[last+1] == signal[0]: last += 1
        regions.append((0, last, True))
    if signal[-1] >= minimum and signal[-1] >= signal[-2]:
        first = len(signal)-1
        while first and signal[first-1] == signal[-1]: first -= 1
        if first: regions.append((first, len(signal)-1, True))
    return [dict(first_sample=a, last_sample=b, amplitude=signal[a], raw_potential=raw[a],
                 time=times[a], plateau_end=times[b], clipped=clipped)
            for a, b, clipped in sorted(regions)]


def _trace(packet, record, raw, group, index):
    _keys(packet, 'kind evidence_schema_version native_status current_base_revision reasons '
                  'requires_fresh_verification requested_specification prepared observation')
    require(packet['kind'] == 'timelearner_native_probe_evidence' and
            _dimension(packet['evidence_schema_version']) == 2,
            'matched_unknown_native_schema')
    require(packet['native_status'] == 'completed' and packet['reasons'] == [] and
            packet['requires_fresh_verification'] is False, 'matched_native_not_completed')
    o, p, q = packet['observation'], packet['prepared'], packet['requested_specification']
    _keys(o, 'schema_version specification complete valid end_reason reasons sample_count stimuli peaks '
             'burst_assignments spikes spike_count first_stimulus_time')
    _keys(p, 'routing input_id protocol_revision base_model_revision effective_model_revision model_epoch selected_input_index')
    s = o['specification']
    for spec in (s, q):
        _keys(spec, SPEC_FIELDS+' stimulus_subset')
        _dimension(spec['maximum_samples'])
        _keys(spec['stimulus_subset'], 'purpose source_training_pattern_hash physical_input_count source_ordinals')
        _dimension(spec['stimulus_subset']['physical_input_count'])
        ordinals = spec['stimulus_subset']['source_ordinals']
        require(type(ordinals) is list and all(type(v) is int for v in ordinals), 'matched_mask_changed')
    require(_dimension(o['schema_version']) == _dimension(s['schema_version']) == _dimension(q['schema_version']) == 6 and
            o['complete'] is True and o['valid'] is True and o['end_reason'] == 'window_closed' and
            o['reasons'] == [] and o['peaks'] == [] and o['burst_assignments'] == [] and
            o['spikes'] == [] and o['spike_count'] is None, 'matched_invalid_native_observation')
    require(s['time_frame'] == 'absolute_model_time' and q['time_frame'] == 'relative_to_trial_start' and
            number(q['begin']) == 0 and s['end'] == number(s['begin'])+number(q['end']), 'matched_requested_clock')
    require(q['baseline'] == [] and q['effective_model_revision'] == '', 'matched_requested_model_fields')
    for key in ('schema_version', 'run_id', 'trial_id', 'sample_id', 'pattern_hash', 'maximum_samples',
                'maximum_sample_gap', 'minimum_amplitude', 'record_spikes', 'expected_stimulus_ids',
                'stimulus_profile', 'wave_assignment', 'peak_selection', 'stimulus_subset', 'windows'):
        _same(q[key], s[key])
    require(s['record_spikes'] is False and s['windows'] == [] and s['wave_assignment'] == 'window_only' and
            s['peak_selection'] == 'isolated_window', 'matched_unsupported_native_policy')
    for key in ('run_id', 'trial_id', 'sample_id', 'pattern_hash', 'effective_model_revision'): _text(s[key])
    for key in ('input_id', 'protocol_revision', 'base_model_revision', 'effective_model_revision'): _text(p[key])
    require(s['trial_id'] == group['group_id']+'/native/'+str(index) and
            s['effective_model_revision'] == p['effective_model_revision'] and
            packet['current_base_revision'] == p['base_model_revision'], 'matched_context_changed')
    _dimension(p['model_epoch'])
    sample_count = _dimension(o['sample_count'])
    subset = s['stimulus_subset']
    _keys(subset, 'purpose source_training_pattern_hash physical_input_count source_ordinals')
    n = _dimension(subset['physical_input_count']); mask = subset['source_ordinals']
    require(n >= 2 and subset['purpose'] == 'stimulus_subset_characterization' and
            subset['source_training_pattern_hash'] == group['source_pattern_sha256'], 'matched_original_target_changed')
    # Bind N to already supplied inventory BEFORE any range(N)/N-sized list.
    # A stopped group still contains a complete initial full presentation.
    require(type(mask) is list and mask and len(mask) in (n-1, n) and
            (index != 0 or len(mask) == n), 'matched_physical_input_inventory')
    declared_mask = record['presented_ordinals']
    require(type(declared_mask) is list and all(type(v) is int for v in declared_mask), 'matched_mask_changed')
    require(all(_dimension(v) < n for v in mask) and
            mask == sorted(set(mask)) and mask == declared_mask, 'matched_mask_changed')
    require(s['expected_stimulus_ids'] == ['pulse'+str(i) for i in mask], 'matched_event_ids_changed')
    baseline = [number(v) for v in s['baseline']]
    require(len(baseline) == len(group['physical_channel_paths']), 'matched_physical_dimensions')
    assigned, channel = _dimension(group['assigned_input']), _dimension(group['assigned_channel'])
    require(assigned < n and p['input_id'] == 'input'+str(assigned), 'matched_assigned_input_changed')
    require(channel < len(baseline), 'matched_assigned_channel_changed')
    if p['routing'] == 'classic_burst':
        require(len(baseline) == n and channel == assigned and p['selected_input_index'] is None,
                'matched_classic_routing')
    else:
        require(p['routing'] == 'branch_solo_burst' and len(baseline) == 1 and channel == 0 and
                _dimension(p['selected_input_index']) == assigned, 'matched_branch_routing')
    profile = s['stimulus_profile']
    _keys(profile, 'generator_class amplitude pulse_length frequency_hz frequency_deviation use_transit_signal use_pattern_output')
    frequency, amplitude, width = (number(profile[k]) for k in ('frequency_hz', 'amplitude', 'pulse_length'))
    require(frequency > 0 and amplitude > 0 and width >= 1/frequency and
            profile['generator_class'] == 'NPulseGeneratorTransit' and number(profile['frequency_deviation']) == 0 and
            profile['use_transit_signal'] is False and profile['use_pattern_output'] is False,
            'matched_unsupported_source')
    policy = group['policy']; epsilon = number(policy['time_comparison_tolerance'])
    require(0 <= epsilon < .5/frequency and s['maximum_sample_gap'] == 1/frequency and
            number(s['minimum_amplitude']) > 0, 'matched_invalid_sampling_policy')
    require(hashlib.sha256(raw).hexdigest() == record['sha256'], 'matched_trace_hash_changed')
    rows = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
    header = ['time', 'stimulus']+['soma'+str(i) for i in range(len(baseline))]
    require(rows and rows[0] == header and all(len(row) == len(header) for row in rows[1:]), 'matched_trace_columns')
    values = [[number(float(v)) for v in row] for row in rows[1:]]
    times = [row[0] for row in values]; require_primary_trace_clock(s, sample_count, times)
    require(all(abs(number(t-s['begin'])-i/frequency) <= epsilon for i, t in enumerate(times)), 'matched_grid_changed')
    require(not after(s['end'], times[-1]) and after(s['end'], times[-2]), 'matched_close_frame_changed')
    require(_dimension(policy['comparison_radius_ticks']) in range(1, len(times)), 'matched_invalid_neighbourhood')
    events = o['stimuli']; require(type(events) is list and [e['id'] for e in events] == s['expected_stimulus_ids'],
                                  'matched_missing_events')
    event_frames = []
    for event in events:
        _keys(event, 'id time relative_to_trial_start')
        t = number(event['time']); require(event['relative_to_trial_start'] == number(t-s['begin']), 'matched_relative_event_changed')
        candidates = [i for i, sample in enumerate(times) if _difference(t, sample) <= epsilon]
        require(len(candidates) == 1 and (not event_frames or candidates[0] > event_frames[-1]), 'matched_event_not_on_grid')
        event_frames.append(candidates[0])
    require(o['first_stimulus_time'] == events[0]['time'], 'matched_first_event_changed')
    pulse_ticks = math.floor(number(width*frequency)); active = set()
    for first in event_frames:
        require(pulse_ticks >= 1 and first+pulse_ticks < len(times), 'matched_pulse_clipped')
        region = set(range(first, first+pulse_ticks)); require(not active & region, 'matched_source_pulses_overlap')
        active.update(region)
    require(all(row[1] == (amplitude if i in active else 0.) for i, row in enumerate(values)), 'matched_source_waveform_changed')
    raws = [[row[i+2] for row in values] for i in range(len(baseline))]
    for ch, base in zip(raws, baseline):
        for v in ch: number(v-base)
    return dict(packet=packet, spec=s, prepared=p, mask=mask, n=n, times=times, raws=raws,
                baseline=baseline, event_frames=event_frames, source=profile)


def _support(maximum, before, after_trace, controls, group):
    policy = group['policy']; assigned, channel = group['assigned_input'], group['assigned_channel']
    radius = _dimension(policy['comparison_radius_ticks'])
    first = max(0, maximum['first_sample']-radius)
    last = min(len(before['times'])-1, maximum['last_sample']+radius)
    states = []
    for control in controls:
        lower, upper = [], []
        for i in range(first, last+1):
            a = number(before['raws'][channel][i]-before['baseline'][channel])
            b = number(after_trace['raws'][channel][i]-after_trace['baseline'][channel])
            c = number(control['raws'][channel][i]-control['baseline'][channel])
            lo, hi = sorted((a, b))
            threshold = _tolerance(policy['influence_absolute'], policy['influence_relative'], max(abs(a), abs(b)), c)
            lower.append((0. if lo <= c <= hi else min(_difference(c, lo), _difference(c, hi))) > threshold)
            upper.append(max(_difference(c, a), _difference(c, b)) > threshold)
        states.append('supported' if any(lower) else 'unknown' if any(upper) else 'not_supported')
    return dict(maximum, supported_inputs=[i for i, state in enumerate(states) if state == 'supported'],
                influence_by_input=states, unknown='unknown' in states,
                precedes_assigned_stimulus=maximum['first_sample'] < before['event_frames'][assigned])


def _choose(maxima, assigned):
    eligible = [i for i, peak in enumerate(maxima) if not peak['clipped'] and not peak['unknown'] and
                not peak['precedes_assigned_stimulus'] and peak['supported_inputs'] == [assigned]]
    best = max(eligible, key=lambda i: maxima[i]['amplitude']) if eligible else None
    for peak in maxima:
        if peak['influence_by_input'][assigned] == 'not_supported': continue
        if peak['precedes_assigned_stimulus']: return 'ambiguous', 'assigned_omission_changes_pre_stimulus_maximum', None
        if peak['clipped']: return 'clipped', 'possibly_assigned_maximum_is_clipped', None
        if (peak['unknown'] or len(peak['supported_inputs']) != 1) and (best is None or peak['amplitude'] >= maxima[best]['amplitude']):
            return 'ambiguous', 'highest_assigned_maximum_has_shared_or_unknown_support', None
    if best is None: return 'missing', 'no_exclusive_assigned_full_maximum', None
    if sum(maxima[i]['amplitude'] == maxima[best]['amplitude'] for i in eligible) != 1:
        return 'ambiguous', 'separated_assigned_maxima_tie', None
    return 'valid', None, best


def _recompute(group, traces):
    before, repeat = traces[0], traces[-1]; n = before['n']; policy = group['policy']
    require(n == len(before['mask']), 'matched_physical_input_inventory')
    require(len(traces) == n+2 and before['mask'] == repeat['mask'] == list(range(n)), 'matched_incomplete_group')
    controls = [None]*n
    for trace in traces[1:-1]:
        missing = set(range(n))-set(trace['mask'])
        require(len(missing) == 1, 'matched_invalid_omission')
        ordinal = missing.pop(); require(controls[ordinal] is None, 'matched_duplicate_control'); controls[ordinal] = trace
    require(all(controls), 'matched_missing_control')
    for previous, current in zip(traces, traces[1:]):
        require(previous['times'][-1] <= current['spec']['begin'], 'matched_trials_overlap')
    for trace in traces:
        require(trace['source'] == before['source'] and trace['prepared'] == before['prepared'] and
                len(trace['times']) == len(before['times']), 'matched_control_context_changed')
        for key in ('run_id', 'sample_id', 'maximum_sample_gap', 'minimum_amplitude'):
            require(trace['spec'][key] == before['spec'][key], 'matched_control_protocol_changed')
        require(_difference(trace['spec']['end']-trace['spec']['begin'], before['spec']['end']-before['spec']['begin']) <=
                policy['time_comparison_tolerance'], 'matched_duration_changed')
        require(all(_difference(a, b) <= policy['baseline_absolute'] for a, b in zip(trace['baseline'], before['baseline'])),
                'matched_baseline_changed')
        for i, ordinal in enumerate(trace['mask']):
            full_event = before['packet']['observation']['stimuli'][ordinal]['time']-before['spec']['begin']
            retained_event = trace['packet']['observation']['stimuli'][i]['time']-trace['spec']['begin']
            require(trace['event_frames'][i] == before['event_frames'][ordinal] and
                    _difference(full_event, retained_event) <= policy['time_comparison_tolerance'],
                    'matched_retained_event_shift')
        if len(trace['mask']) == n: require(trace['spec']['pattern_hash'] == group['source_pattern_sha256'], 'matched_full_target_changed')
    for a_channel, b_channel, a_base, b_base in zip(before['raws'], repeat['raws'], before['baseline'], repeat['baseline']):
        for a_raw, b_raw in zip(a_channel, b_channel):
            a, b = number(a_raw-a_base), number(b_raw-b_base)
            if _difference(a, b) > _tolerance(policy['repeatability_absolute'], policy['repeatability_relative'], a, b):
                return 'non_repeatable', ['full_response_not_repeatable'], [], None
    ch = group['assigned_channel']; minimum = before['spec']['minimum_amplitude']
    maxima = [_support(m, before, repeat, controls, group)
              for m in _maxima(before['times'], before['raws'][ch], before['baseline'][ch], minimum)]
    validity, reason, selected = _choose(maxima, group['assigned_input'])
    if validity == 'valid':
        again = [_support(m, before, repeat, controls, group)
                 for m in _maxima(repeat['times'], repeat['raws'][ch], repeat['baseline'][ch], minimum)]
        repeated_validity, _, repeated = _choose(again, group['assigned_input'])
        if repeated_validity != 'valid': return 'non_repeatable', ['assigned_maximum_not_repeated'], maxima, None
        if any(maxima[selected][k] != again[repeated][k] for k in ('first_sample', 'last_sample')):
            return 'non_repeatable', ['assigned_maximum_sample_range_not_repeated'], maxima, None
    return validity, [] if reason is None else [reason], maxima, selected


def audit_matched_omission_evidence(group, primary):
    """primary maps the declared relative CSV names to immutable bytes."""
    try:
        _keys(group, GROUP_FIELDS); _finite_json(group)
        require(group['kind'] == 'native_matched_omission_fixture' and _dimension(group['schema_version']) == 1 and
                group['method'] == METHOD and group['training_certificate_eligible'] is False and
                group['scientific_verdict'] is None, 'matched_unknown_fixture_schema')
        for key in ('group_id', 'source_pattern_sha256', 'reset_binding', 'model_instance_binding'): _text(group[key])
        paths = group['physical_channel_paths']; require(type(paths) is list and paths and len(set(paths)) == len(paths) and
                all(type(v) is str and v for v in paths), 'matched_physical_paths')
        _dimension(group['assigned_channel']); _dimension(group['assigned_input'])
        policy = group['policy']; _keys(policy, POLICY_FIELDS)
        for key, value in policy.items(): require(number(value) >= 0, 'matched_negative_policy')
        require(_dimension(policy['comparison_radius_ticks']) >= 1, 'matched_invalid_neighbourhood')
        packets, records = group['packets'], group['traces']
        require(type(packets) is list and type(records) is list and 0 < len(packets) == _dimension(group['native_probes']) and
                len(records) == len(packets), 'matched_missing_primary_trace')
        traces, names = [], set()
        for i, (packet, record) in enumerate(zip(packets, records)):
            _keys(record, 'path presented_ordinals sha256'); name = record['path']; path = PurePosixPath(name)
            require(type(name) is str and str(path) == name and ':' not in name and
                    not path.is_absolute() and '..' not in path.parts and '\\' not in name and
                    name not in names and name in primary, 'matched_unsafe_or_duplicate_trace_path')
            names.add(name); require(type(primary[name]) is bytes, 'matched_primary_not_bytes')
            traces.append(_trace(packet, record, primary[name], group, i))
        require(set(primary) == names, 'matched_unexpected_primary_files')
        n = traces[0]['n']; require(all(t['n'] == n for t in traces), 'matched_physical_input_count_changed')
        require(n == len(traces[0]['mask']), 'matched_physical_input_inventory')
        _maximum_dimensions(group, len(traces[0]['times']), n)
        require(traces[0]['mask'] == list(range(n)) and
                traces[0]['spec']['pattern_hash'] == group['source_pattern_sha256'], 'matched_missing_initial_full')
        complete = len(traces) == n+2
        if complete:
            require(group['reason'] == 'omission_group_closed', 'matched_group_not_closed')
            validity, reasons, maxima, selected = _recompute(group, traces)
            _same(group['assignment_validity'], validity); _same(group['assignment_reasons'], reasons)
            _same(group['maxima'], maxima); _same(group['selected_full_maximum'], selected)
        else:
            require(len(traces) == 1 and group['assignment_validity'] == 'not_available' and group['maxima'] == [] and
                    group['assignment_reasons'] == [] and group['selected_full_maximum'] is None and
                    group['reason'] in ('omission_group_external_stop', 'omission_group_model_changed'),
                    'matched_partial_group_claims_assignment')
            validity, maxima = 'not_available', []
        return dict(reader_version=1, method=METHOD, primary_traces_checked=len(traces), complete_group=complete,
                    assignment_validity=validity, assignment_recomputed=complete, maxima=maxima,
                    training_certificate_eligible=False, causal_origin_verified=False, native_execution_verified=False,
                    physical_paths_independently_verified=False, reset_instance_ownership_independently_verified=False,
                    total_budget_declarations_available=False, presented_isi_hashes_recomputed=False,
                    evaluation_verdict=None)
    except EvidenceError: raise
    except (KeyError, TypeError, ValueError, IndexError, UnicodeError, csv.Error, OverflowError) as error:
        raise EvidenceError('malformed_matched_omission_evidence') from error


def _audit_file(path):
    path = Path(path).resolve(); group = load(path); primary = {}
    require(type(group.get('traces')) is list, 'matched_missing_trace_records')
    for record in group['traces']:
        name = record.get('path'); require(type(name) is str, 'matched_missing_trace_path')
        relative = PurePosixPath(name)
        require(str(relative) == name and ':' not in name and not relative.is_absolute() and
                '..' not in relative.parts and '\\' not in name,
                'matched_unsafe_trace_path')
        source = (path.parent/name).resolve(); require(source.is_relative_to(path.parent), 'matched_trace_escapes_directory')
        require(name not in primary, 'matched_duplicate_trace_path'); primary[name] = source.read_bytes()
    return audit_matched_omission_evidence(group, primary)


def audit_matched_omission_file(path):
    try: return _audit_file(path)
    except EvidenceError: raise
    except (OSError, KeyError, TypeError, AttributeError, ValueError) as error:
        raise EvidenceError('malformed_or_missing_matched_primary') from error


def diagnose_declared_window(group, receipt, begin, end):
    """Applicability comparison only; does not change the audited method/verdict."""
    require(receipt['complete_group'] and receipt['assignment_recomputed'], 'matched_scope_requires_complete_replay')
    assigned = _dimension(group['assigned_input'])
    begin, end = number(begin), number(end)
    spec = group['packets'][0]['observation']['specification']; origin = number(spec['begin'])
    require(0 <= begin < end <= number(spec['end'])-origin, 'matched_invalid_diagnostic_window')
    inside, exclusive, shared_outside = [], [], []
    for i, maximum in enumerate(receipt['maxima']):
        within = begin <= number(maximum['time']-origin) and number(maximum['plateau_end']-origin) <= end
        if within:
            inside.append(i)
            if (maximum['supported_inputs'] == [assigned] and not maximum['unknown'] and
                    not maximum['clipped'] and not maximum['precedes_assigned_stimulus']): exclusive.append(i)
        elif (maximum['influence_by_input'][assigned] != 'not_supported' and
              (maximum['unknown'] or len(maximum['supported_inputs']) != 1)):
            shared_outside.append(i)
    return dict(declared_relative_window=[begin, end], hypothesis_only=True,
                audited_assignment_validity=receipt['assignment_validity'], in_window_maxima=inside,
                in_window_exclusive_assigned_maxima=exclusive, possibly_assigned_shared_maxima_outside=shared_outside,
                training_certificate_eligible=False, criterion_changed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('group'); parser.add_argument('--output')
    args = parser.parse_args(); result = audit_matched_omission_file(args.group)
    text = json.dumps(result, indent=2, allow_nan=False)+'\n'
    if args.output:
        output = Path(args.output).resolve()
        require(not output.is_relative_to(Path(args.group).resolve().parent), 'matched_report_overlaps_primary')
        with output.open('x', encoding='utf-8') as stream: stream.write(text)
    else: print(text, end='')
    return 0


if __name__ == '__main__': raise SystemExit(main())
