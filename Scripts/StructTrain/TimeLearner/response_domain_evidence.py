"""Independent complete-waveform/domain audit; never a Train certificate.

V1 supports valid declared domains and native schemas2/3 with a stock digital
source. Physical path labels and operating-system execution are not attested.
"""
import csv
import hashlib
import io
from pathlib import Path, PurePosixPath

from .native_evidence import (EvidenceError, after, count, equal, load, number,
                              require, require_primary_trace_clock)


METHOD = 'declared-response-domains-diagnostic-v1'


def _keys(value, fields):
    require(type(value) is dict and set(value) == set(fields.split()), 'domain_unknown_fields')


def _text(value):
    require(type(value) is str and bool(value), 'domain_missing_identity')
    return value


def _finite_json(value):
    if type(value) is dict:
        require(all(type(k) is str for k in value), 'domain_non_json_key')
        for item in value.values(): _finite_json(item)
    elif type(value) is list:
        for item in value: _finite_json(item)
    elif type(value) in (int, float): number(value)
    else: require(value is None or type(value) in (str, bool), 'domain_non_json_value')


def _same(actual, expected):
    """Exact binary64 roundtrip, with booleans distinct from numbers."""
    if type(expected) is dict:
        require(type(actual) is dict and set(actual) == set(expected), 'domain_recomputed_fields_changed')
        for key in expected: _same(actual[key], expected[key])
    elif type(expected) is list:
        require(type(actual) is list and len(actual) == len(expected), 'domain_recomputed_array_changed')
        for a, b in zip(actual, expected): _same(a, b)
    elif type(expected) in (int, float):
        require(number(actual) == number(expected), 'domain_recomputed_number_changed')
    else:
        require(type(actual) is type(expected) and actual == expected, 'domain_recomputed_value_changed')


def _slice(times, begin, end):
    first, last = 0, len(times)
    while first < last and after(begin, times[first]): first += 1
    while last > first and after(times[last-1], end): last -= 1
    return first, last


def _features(times, raw, baseline, minimum):
    result = dict(feature_validity='insufficient_samples', positive_maxima=[], global_maximum=None,
                  largest_interior_maximum_count=0, global_maximum_clipped=False, boundary_response_clipped=False)
    if len(times) < 3: return result
    signal = [number(v-baseline) for v in raw]
    def maximum(first, last):
        return dict(first_sample=first, last_sample=last, amplitude=signal[first], raw=raw[first],
                    time=times[first], plateau_end=times[last])
    first = max(range(len(raw)), key=signal.__getitem__); last = first
    while last+1 < len(raw) and signal[last+1] == signal[first]: last += 1
    result['global_maximum'] = maximum(first, last)
    result['global_maximum_clipped'] = first == 0 or last+1 == len(raw)
    i = 1
    while i+1 < len(raw):
        finish = i
        while finish+1 < len(raw) and signal[finish+1] == signal[i]: finish += 1
        if finish+1 < len(raw) and signal[i] >= minimum and signal[i] > signal[i-1] and signal[finish] > signal[finish+1]:
            result['positive_maxima'].append(maximum(i, finish))
            result['largest_interior_maximum_count'] += int(signal[i] == signal[first])
        i = finish+1
    result['boundary_response_clipped'] = ((signal[0] >= minimum and signal[0] >= signal[1]) or
        (signal[-1] >= minimum and signal[-1] >= signal[-2]))
    result['feature_validity'] = 'valid'
    return result


def _empty_peak(window, validity='incomplete'):
    return dict(input_id=window['input_id'], stimulus_id=window['stimulus_id'], validity=validity,
                amplitude=None, raw_potential=None, time=None, plateau_end=None,
                delay_from_stimulus=None, relative_to_trial_start=None, candidate_count=0)


def _peak(window, times, raw, baseline, minimum):
    peak = _empty_peak(window); first, last = _slice(times, window['begin'], window['end'])
    f = _features(times[first:last], raw[first:last], baseline, minimum)
    if f['feature_validity'] != 'valid': return peak
    m = f['global_maximum']
    if m['amplitude'] < minimum: peak['validity'] = 'missing'; return peak
    if f['global_maximum_clipped']: peak['validity'] = 'clipped'; return peak
    peak['candidate_count'] = len(f['positive_maxima'])
    if peak['candidate_count'] != 1: peak['validity'] = 'ambiguous'; return peak
    peak.update(validity='valid', amplitude=m['amplitude'], raw_potential=m['raw'],
                time=m['time'], plateau_end=m['plateau_end'])
    return peak


def _replay(spec, observation, times, raws, event_times):
    """Recompute the production schema2/3 recorder, including failed assignment."""
    reasons, assignments, peaks = [], [], []
    def reason(value):
        if value not in reasons: reasons.append(value)
    if spec['schema_version'] == 3:
        for ch in sorted({count(w['channel']) for w in spec['windows']}):
            f = _features(times, raws[ch], spec['baseline'][ch], spec['minimum_amplitude'])
            waves = [dict(stimulus_id='', amplitude=m['amplitude'], raw_potential=m['raw'], time=m['time'],
                          plateau_end=m['plateau_end'], relative_to_trial_start=m['time']-spec['begin'])
                     for m in f['positive_maxima']]
            validity = 'valid'
            if f['boundary_response_clipped']: validity = 'clipped'
            elif len(waves) != len(event_times): validity = 'missing' if len(waves) < len(event_times) else 'ambiguous'
            elif any(after(t, w['time']) for t, w in zip(event_times, waves)): validity = 'ambiguous'
            if validity == 'valid':
                for wave, sid in zip(waves, spec['expected_stimulus_ids']): wave['stimulus_id'] = sid
            else: reason('burst_'+validity+':'+str(ch))
            assignments.append(dict(channel=ch, validity=validity, waves=waves))
    for window in spec['windows']:
        ch = count(window['channel']); peak = _peak(window, times, raws[ch], spec['baseline'][ch], spec['minimum_amplitude'])
        if spec['schema_version'] == 3:
            assignment = next(a for a in assignments if a['channel'] == ch)
            wave = next((w for w in assignment['waves'] if w['stimulus_id'] == window['stimulus_id']), None)
            if spec['peak_selection'] == 'assigned_burst_wave':
                peak = _empty_peak(window, assignment['validity'])
                if assignment['validity'] == 'valid':
                    if wave is None: peak['validity'] = 'missing'
                    else:
                        first = times.index(wave['time']); last = times.index(wave['plateau_end'])
                        if first == 0 or last+1 == len(times) or after(window['begin'], times[first-1]) or after(times[last+1], window['end']):
                            peak['validity'] = 'clipped'
                        else:
                            peak.update(candidate_count=1, amplitude=wave['amplitude'], raw_potential=wave['raw_potential'],
                                        time=wave['time'], plateau_end=wave['plateau_end'])
            elif assignment['validity'] != 'valid': peak = _empty_peak(window, assignment['validity'])
            elif peak['validity'] == 'valid' and (wave is None or any(peak[k] != wave[k] for k in ('time','plateau_end','raw_potential','amplitude'))):
                peak = _empty_peak(window, 'ambiguous'); reason('burst_window_assignment_mismatch:'+window['input_id'])
        if peak['validity'] == 'valid':
            onset = event_times[spec['expected_stimulus_ids'].index(window['stimulus_id'])]
            peak['delay_from_stimulus'] = number(peak['time']-onset)
            peak['relative_to_trial_start'] = number(peak['time']-spec['begin'])
            if after(onset, peak['time']): reason('peak_precedes_stimulus:'+window['input_id'])
        else: reason('peak_'+peak['validity']+':'+window['input_id'])
        peaks.append(peak)
    _same(observation['peaks'], peaks); _same(observation['burst_assignments'], assignments)
    _same(observation['reasons'], reasons); _same(observation['valid'], not reasons)


SPEC_FIELDS = ('time_frame schema_version run_id trial_id sample_id pattern_hash effective_model_revision begin end '
               'maximum_sample_gap minimum_amplitude maximum_samples record_spikes baseline windows expected_stimulus_ids '
               'stimulus_profile wave_assignment peak_selection')


def _audit(packet, raw):
    _finite_json(packet)
    _keys(packet, 'kind schema_version method diagnostic_only training_certificate_eligible scientific_verdict native_evidence domain_spec capture trace analysis')
    require(packet['kind'] == 'timelearner_native_response_domain_evidence' and type(packet['schema_version']) is int and
            packet['schema_version'] == 1 and packet['method'] == METHOD and packet['diagnostic_only'] is True and
            packet['training_certificate_eligible'] is False and packet['scientific_verdict'] is None, 'domain_unknown_contract')
    trace = packet['trace']; _keys(trace, 'format path bytes sha256 header time_frame')
    relative = PurePosixPath(_text(trace['path']))
    require(not relative.is_absolute() and '\\' not in trace['path'] and ':' not in trace['path'] and
            all(p not in ('', '.', '..') for p in trace['path'].split('/')), 'domain_unsafe_trace_path')
    require(trace['format'] == 'native-probe-csv-v1' and trace['time_frame'] == 'absolute_model_time' and
            len(raw) == count(trace['bytes']) and hashlib.sha256(raw).hexdigest() == trace['sha256'], 'domain_trace_identity_changed')
    e = packet['native_evidence']; _keys(e, 'kind evidence_schema_version native_status current_base_revision reasons requires_fresh_verification requested_specification prepared observation')
    require(e['kind'] == 'timelearner_native_probe_evidence' and type(e['evidence_schema_version']) is int and
            e['evidence_schema_version'] == 2 and e['native_status'] == 'completed' and e['reasons'] == [] and
            e['requires_fresh_verification'] is False, 'domain_native_not_completed')
    o = e['observation']; _keys(o, 'schema_version specification complete valid end_reason reasons sample_count stimuli peaks burst_assignments spikes spike_count first_stimulus_time')
    s, q, p = o['specification'], e['requested_specification'], e['prepared']; _keys(s, SPEC_FIELDS); _keys(q, SPEC_FIELDS)
    _keys(p, 'routing input_id protocol_revision base_model_revision effective_model_revision model_epoch selected_input_index')
    require(type(s['schema_version']) is int and s['schema_version'] in (2,3) and o['schema_version'] == s['schema_version'] and
            type(o['valid']) is bool and o['complete'] is True and o['end_reason'] == 'window_closed', 'domain_unsupported_native_observation')
    require(s['time_frame'] == 'absolute_model_time' and q['time_frame'] == 'relative_to_trial_start' and
            number(q['begin']) == 0 and equal(s['end'], number(s['begin'])+number(q['end'])), 'domain_requested_clock_changed')
    for key in ('schema_version','run_id','trial_id','sample_id','pattern_hash','maximum_samples','maximum_sample_gap',
                'minimum_amplitude','record_spikes','expected_stimulus_ids','wave_assignment','peak_selection'):
        _same(q[key], s[key])
    for key in ('run_id','trial_id','sample_id','pattern_hash','effective_model_revision'): _text(s[key])
    require(type(q['effective_model_revision']) is str and q['baseline'] == [], 'domain_unsupported_requested_model_fields')
    for key in ('base_model_revision','effective_model_revision','protocol_revision','input_id'): _text(p[key])
    require(p['effective_model_revision'] == s['effective_model_revision'] and e['current_base_revision'] == p['base_model_revision'], 'domain_native_revision_changed')
    count(p['model_epoch'])
    require(s['record_spikes'] is False and o['spikes'] == [] and o['spike_count'] is None, 'domain_unsupported_spike_capture')
    require(s['wave_assignment'] == ('ordered_whole_burst' if s['schema_version'] == 3 else 'window_only') and
            s['peak_selection'] in (('isolated_window','assigned_burst_wave') if s['schema_version'] == 3 else ('isolated_window',)), 'domain_unsupported_peak_policy')
    ids = s['expected_stimulus_ids']; require(type(ids) is list and bool(ids) and all(type(v) is str and v for v in ids) and len(set(ids)) == len(ids), 'domain_invalid_stimulus_ids')
    baseline = [number(v) for v in s['baseline']]; require(bool(baseline), 'domain_missing_baseline')
    profile = s['stimulus_profile']; _keys(profile, 'generator_class amplitude pulse_length frequency_hz frequency_deviation use_transit_signal use_pattern_output')
    frequency = number(profile['frequency_hz']); amplitude = number(profile['amplitude']); width = number(profile['pulse_length'])
    require(frequency > 0 and amplitude > 0 and width >= 1/frequency and profile['generator_class'] == 'NPulseGeneratorTransit' and
            number(profile['frequency_deviation']) == 0 and profile['use_transit_signal'] is False and profile['use_pattern_output'] is False,
            'domain_unsupported_source_profile')
    require(q['stimulus_profile'] is None or q['stimulus_profile'] == profile, 'domain_requested_profile_changed')
    require(number(s['minimum_amplitude']) > 0 and equal(s['maximum_sample_gap'], 1/frequency), 'domain_invalid_measurement_policy')
    require(p['routing'] in ('classic_burst','branch_solo_burst'), 'domain_unknown_routing')
    if p['routing'] == 'classic_burst': require(p['selected_input_index'] is None and len(baseline) == len(ids), 'domain_classic_channel_shape')
    else: require(len(baseline) == 1 and count(p['selected_input_index']) < len(ids), 'domain_branch_selector')
    require(type(s['windows']) is list and bool(s['windows']) and len({w['input_id'] for w in s['windows']}) == len(s['windows']) and
            len(q['windows']) == len(s['windows']) and p['input_id'] in {w['input_id'] for w in s['windows']}, 'domain_window_set_changed')
    for w, r in zip(s['windows'], q['windows']):
        _keys(w, 'input_id stimulus_id channel begin end'); _keys(r, 'input_id stimulus_id channel begin end')
        _text(w['input_id']); require(w['stimulus_id'] in ids and count(w['channel']) < len(baseline) and
            number(w['begin']) < number(w['end']) and not after(s['begin'], w['begin']) and not after(w['end'], s['end']), 'domain_invalid_native_window')
        for key in ('input_id','stimulus_id','channel'): _same(r[key], w[key])
        require(equal(number(r['begin'])+s['begin'], w['begin']) and equal(number(r['end'])+s['begin'], w['end']), 'domain_requested_window_changed')
        if s['schema_version'] == 3:
            ordinal = ids.index(w['stimulus_id'])
            require(count(w['channel']) == (ordinal if p['routing'] == 'classic_burst' else 0) and
                (p['routing'] == 'classic_burst' or (count(p['selected_input_index']) == ordinal and w['input_id'] == p['input_id'])), 'domain_native_physical_mapping_changed')
    c = packet['capture']; _keys(c, 'run_id trial_id sample_id complete sample_count begin end maximum_sample_gap minimum_amplitude channel_mapping')
    require(c['complete'] is True, 'domain_capture_not_complete')
    for key in ('run_id','trial_id','sample_id','begin','end','maximum_sample_gap','minimum_amplitude'): _same(c[key], s[key])
    _same(c['sample_count'], o['sample_count'])
    mappings = c['channel_mapping']; require(type(mappings) is list and len(mappings) == len(baseline), 'domain_channel_mapping_changed')
    for i, mapping in enumerate(mappings):
        _keys(mapping, 'channel physical_path csv_column baseline'); _text(mapping['physical_path'])
        require(count(mapping['channel']) == i and mapping['csv_column'] == 'soma'+str(i), 'domain_channel_order_changed')
        _same(mapping['baseline'], baseline[i])
    require(len({m['physical_path'] for m in mappings}) == len(mappings), 'domain_duplicate_physical_path')
    rows = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
    header = ['time','stimulus']+['soma'+str(i) for i in range(len(baseline))]
    require(rows and rows[0] == trace['header'] == header and all(len(r) == len(header) for r in rows[1:]), 'domain_trace_schema_changed')
    values = [[number(float(v)) for v in row] for row in rows[1:]]; times = [r[0] for r in values]
    require_primary_trace_clock(s, o['sample_count'], times)
    raws = [[r[i+2] for r in values] for i in range(len(baseline))]
    events = o['stimuli']; require(type(events) is list and len(events) == len(ids), 'domain_actual_stimulus_count_changed')
    event_times = []
    for sid, event in zip(ids, events):
        _keys(event, 'id time relative_to_trial_start'); t = number(event['time'])
        require(event['id'] == sid and not after(s['begin'], t) and not after(t, s['end']) and
            (not event_times or t > event_times[-1]) and equal(event['relative_to_trial_start'], t-s['begin']), 'domain_actual_stimulus_changed')
        require(sum(equal(t, v) for v in times) == 1, 'domain_actual_stimulus_not_sampled'); event_times.append(t)
    _same(o['first_stimulus_time'], event_times[0])
    # Restrict v1 to separately visible digital pulses. Source aliases/analog
    # output and merged consecutive pulse widths need a separate source adapter.
    starts = [i for i, row in enumerate(values) if row[1] > 0 and (i == 0 or values[i-1][1] <= 0)]
    require(all(r[1] in (0., amplitude) for r in values) and len(starts) == len(event_times) and
            all(equal(times[i], t) for i, t in zip(starts, event_times)), 'domain_digital_source_events_changed')
    pulse_ticks = int(number(width*frequency))
    require(0 < pulse_ticks <= len(values), 'domain_unsupported_source_duration')
    for start in starts:
        finish = start
        while finish < len(values) and values[finish][1] > 0: finish += 1
        require(finish < len(values) and finish-start == pulse_ticks, 'domain_digital_source_width_changed')
    _replay(s, o, times, raws, event_times)
    d = packet['domain_spec']; _keys(d, 'schema_version model_revision protocol_revision pattern_hash stimulus_ids channel_ids domains')
    require(type(d['schema_version']) is int and d['schema_version'] == 1 and d['model_revision'] == s['effective_model_revision'] and
            d['protocol_revision'] == p['protocol_revision'] and d['pattern_hash'] == s['pattern_hash'], 'domain_spec_revision_changed')
    _same(d['stimulus_ids'], ids)
    require(type(d['channel_ids']) is list and len(d['channel_ids']) == len(baseline) and
            {count(v) for v in d['channel_ids']} == set(range(len(baseline))), 'domain_spec_channels_changed')
    domains = d['domains']; require(type(domains) is list, 'domain_invalid_domains')
    pairs = set()
    for domain in domains:
        _keys(domain, 'channel stimulus_id begin end'); ch = count(domain['channel']); sid = domain['stimulus_id']
        require(ch < len(baseline) and sid in ids and (ch,sid) not in pairs and
            number(domain['begin']) < number(domain['end']) and not after(s['begin'], domain['begin']) and not after(domain['end'], s['end']), 'domain_invalid_competing_pair')
        pairs.add((ch,sid))
    require(pairs == {(ch,sid) for ch in range(len(baseline)) for sid in ids}, 'domain_missing_competing_pair')
    channels, full = [], {}
    for ch in range(len(baseline)):
        first, last = _slice(times, s['begin'], s['end']); f = _features(times[first:last], raws[ch][first:last], baseline[ch], s['minimum_amplitude'])
        full[ch] = f
        channels.append(dict(channel=ch, first_source_sample=first, **f))
    associations = []
    for domain in domains:
        ch, sid = count(domain['channel']), domain['stimulus_id']; f = full[ch]; onset = event_times[ids.index(sid)]
        def intersects(other, m): return not after(other['begin'], m['plateau_end']) and not after(m['time'], other['end'])
        a = dict(channel=ch, stimulus_id=sid, status='invalid_specification', reason='', candidate_maxima=[],
                 largest_measured_maximum=None, selected_maximum=None, actual_stimulus_time=onset,
                 maximum_offset_low=None, maximum_offset_high=None, competing_stimulus_ids=[])
        a['candidate_maxima'] = [i for i,m in enumerate(f['positive_maxima']) if intersects(domain,m)]
        first, last = _slice(times, domain['begin'], domain['end']); local = _features(times[first:last], raws[ch][first:last], baseline[ch], s['minimum_amplitude'])
        status, reason = 'hypothesis', 'exclusive_maximum_under_declared_domains_not_proven_origin'
        m = local['global_maximum']
        if local['feature_validity'] != 'valid': status, reason = 'incomplete', 'response_domain_has_insufficient_samples'
        elif m['amplitude'] < s['minimum_amplitude']: status, reason = 'no_candidate', 'no_measurable_maximum_in_declared_domain'
        elif local['global_maximum_clipped']: status, reason = 'clipped', 'declared_domain_clips_maximum'
        elif local['largest_interior_maximum_count'] != 1: status, reason = 'ambiguous', 'separated_largest_maxima_tie'
        else:
            selected = next((i for i in a['candidate_maxima'] if channels[ch]['first_source_sample']+f['positive_maxima'][i]['first_sample'] == first+m['first_sample'] and
                channels[ch]['first_source_sample']+f['positive_maxima'][i]['last_sample'] == first+m['last_sample']), None)
            if selected is None: status, reason = 'incomplete', 'maximum_not_bound_to_full_observation'
            else:
                a.update(largest_measured_maximum=selected, maximum_offset_low=number(m['time']-onset), maximum_offset_high=number(m['plateau_end']-onset))
                if after(onset, m['time']): status, reason = 'outside_applicability', 'maximum_precedes_actual_stimulus'
                else:
                    a['competing_stimulus_ids'] = sorted(other['stimulus_id'] for other in domains if other['channel'] == ch and other['stimulus_id'] != sid and
                        not after(event_times[ids.index(other['stimulus_id'])], min(other['end'],m['plateau_end'])) and intersects(other,m))
                    if a['competing_stimulus_ids']: status, reason = 'ambiguous', 'maximum_shared_by_competing_domains'
                    else: a['selected_maximum'] = selected
        a.update(status=status, reason=reason); associations.append(a)
    analysis = dict(channels=channels, associations=associations, reasons=[]); _same(packet['analysis'], analysis)
    return dict(kind='timelearner_response_domain_audit', schema_version=1, method=METHOD,
                diagnostic_only=True, training_certificate_eligible=False, primary_trace_checked=True,
                features_recomputed=True, domain_graph_recomputed=True, legacy_recorder_recomputed=True,
                sample_count=len(times), channel_count=len(baseline), association_count=len(associations),
                native_execution_verified=False, physical_paths_independently_verified=False,
                causal_origin_verified=False, evaluation_verdict=None)


def audit_response_domain_evidence(packet, trace):
    """Audit supplied packet and exact CSV bytes (or a regular, unaliased file)."""
    try:
        if type(trace) is bytes: raw = trace
        else:
            path = Path(trace); require(path.is_file() and not path.is_symlink(), 'domain_trace_missing_or_alias')
            raw = path.read_bytes()
        return _audit(packet, raw)
    except EvidenceError: raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, UnicodeError, csv.Error, OSError) as error:
        raise EvidenceError('malformed_response_domain_evidence:'+str(error)) from error


def audit_response_domain_file(path):
    """Resolve the packet's safe relative trace inside its artifact directory."""
    path = Path(path); require(path.is_file() and not path.is_symlink(), 'domain_packet_missing_or_alias')
    packet = load(path); relative = packet['trace']['path']
    require(type(relative) is str and relative and '\\' not in relative and ':' not in relative and
            not PurePosixPath(relative).is_absolute() and all(p not in ('','.','..') for p in relative.split('/')), 'domain_unsafe_trace_path')
    root = path.parent.resolve(strict=True); trace = path.parent/relative
    require(trace.resolve(strict=True).is_relative_to(root), 'domain_trace_escape')
    return audit_response_domain_evidence(packet, trace)
