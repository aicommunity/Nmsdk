"""Strict diagnostic-only native schema 4. Never training/certificate evidence."""
import csv
import math
from pathlib import Path

from .native_calibration_worker import _evidence_boundary
from .native_evidence import after, count, equal, number, require, require_primary_trace_clock

SPEC_FIELDS = {'time_frame', 'schema_version', 'run_id', 'trial_id', 'sample_id', 'pattern_hash',
    'effective_model_revision', 'begin', 'end', 'maximum_sample_gap', 'minimum_amplitude',
    'maximum_samples', 'record_spikes', 'baseline', 'windows', 'expected_stimulus_ids',
    'stimulus_profile', 'wave_assignment', 'peak_selection', 'characterization'}


def _declaration(spec):
    require(type(spec) is dict and set(spec) == SPEC_FIELDS and type(spec['schema_version']) is int and
            spec['schema_version'] == 4, 'single_pulse_unknown_specification')
    c = spec['characterization']
    require(type(c) is dict and set(c) == {'purpose', 'source_training_pattern_hash', 'physical_input_count',
            'selected_input_index'} and c['purpose'] == 'single_pulse_characterization', 'single_pulse_unknown_purpose')
    require(0 < count(c['physical_input_count']) and count(c['selected_input_index']) < c['physical_input_count'],
            'single_pulse_physical_input_mismatch')
    for value in (c['source_training_pattern_hash'], spec['pattern_hash']):
        require(type(value) is str and len(value) == 64 and all(v in '0123456789abcdef' for v in value),
                'single_pulse_invalid_pattern_hash')
    for key in ('run_id', 'trial_id', 'sample_id'):
        require(type(spec[key]) is str and bool(spec[key]), 'single_pulse_identity_missing')
    require(spec['wave_assignment'] == 'window_only' and spec['peak_selection'] == 'isolated_window' and
            spec['record_spikes'] is False and len(spec['expected_stimulus_ids']) == 1 and
            type(spec['expected_stimulus_ids'][0]) is str and bool(spec['expected_stimulus_ids'][0]) and
            number(spec['minimum_amplitude']) > 0 and number(spec['maximum_sample_gap']) > 0 and
            count(spec['maximum_samples']) > 0, 'single_pulse_policy_invalid')
    require(type(spec['windows']) is list and len(spec['windows']) == 1, 'single_pulse_window_count')
    return c


def _peak(observation, spec, samples, begin):
    window = spec['windows'][0];channel = count(window['channel'])
    values = [s for s in samples if not after(window['begin'], s['time']) and not after(s['time'], window['end'])]
    validity = 'incomplete';candidates = 0;maximum = last = None
    signal = [number(v['soma'][channel]-spec['baseline'][channel]) for v in values]
    if observation['complete'] and len(values) >= 3:
        maximum = max(range(len(signal)), key=signal.__getitem__);last = maximum
        while last+1 < len(signal) and signal[last+1] == signal[maximum]:last += 1
        if signal[maximum] < spec['minimum_amplitude']:validity = 'missing'
        elif maximum == 0 or last+1 == len(signal):validity = 'clipped'
        else:
            i = 1
            while i+1 < len(signal):
                end = i
                while end+1 < len(signal) and signal[end+1] == signal[i]:end += 1
                if end+1 < len(signal) and signal[i] >= spec['minimum_amplitude'] and signal[i] > signal[i-1] and signal[end] > signal[end+1]:candidates += 1
                i = end+1
            validity = 'valid' if candidates == 1 else 'ambiguous'
    peaks = observation['peaks']
    require(type(peaks) is list and len(peaks) == 1, 'single_pulse_peak_count')
    p = peaks[0]
    require(set(p) == {'input_id', 'stimulus_id', 'validity', 'amplitude', 'raw_potential', 'time', 'plateau_end',
            'delay_from_stimulus', 'candidate_count', 'relative_to_trial_start'} and
            p['input_id'] == window['input_id'] and p['stimulus_id'] == window['stimulus_id'] and
            p['validity'] == validity and count(p['candidate_count']) == candidates, 'single_pulse_peak_mismatch')
    measured = ('amplitude', 'raw_potential', 'time', 'plateau_end', 'delay_from_stimulus', 'relative_to_trial_start')
    if validity != 'valid':
        require(all(p[k] is None for k in measured), 'single_pulse_invalid_peak_has_measurement')
    else:
        expected = {'amplitude': signal[maximum], 'raw_potential': values[maximum]['soma'][channel],
                    'time': values[maximum]['time'], 'plateau_end': values[last]['time'],
                    'relative_to_trial_start': values[maximum]['time']-begin}
        for key, value in expected.items():require(equal(p[key], value), 'single_pulse_peak_trace_mismatch:'+key)
        if observation['stimuli']:
            require(equal(p['delay_from_stimulus'], p['time']-observation['stimuli'][0]['time']), 'single_pulse_peak_delay_mismatch')
        else:require(p['delay_from_stimulus'] is None, 'single_pulse_missing_stimulus_delay_claim')
    return validity


@_evidence_boundary
def read_single_pulse(packet, trace):
    """Return raw samples and diagnostic quality, including honest partial captures.

    Complete finite waves with missing/ambiguous peaks remain diagnostic waves.
    No result of this function is a training acceptance or recognition verdict.
    """
    require(set(packet) == {'kind', 'evidence_schema_version', 'native_status', 'current_base_revision', 'reasons',
            'requires_fresh_verification', 'requested_specification', 'prepared', 'observation'} and
            packet['kind'] == 'timelearner_native_probe_evidence' and type(packet['evidence_schema_version']) is int and
            packet['evidence_schema_version'] == 2 and packet['native_status'] in ('completed', 'rejected', 'cancelled'),
            'single_pulse_unknown_packet')
    require(type(packet['requires_fresh_verification']) is bool and type(packet['reasons']) is list and
            all(type(r) is str for r in packet['reasons']), 'single_pulse_invalid_packet_flags')
    requested = packet['requested_specification'];c = _declaration(requested)
    require(requested['time_frame'] == 'relative_to_trial_start' and number(requested['begin']) == 0 and
            number(requested['end']) > 0 and requested['baseline'] == [] and requested['effective_model_revision'] == '',
            'single_pulse_invalid_relative_request')
    with Path(trace).open(newline='', encoding='utf-8') as stream:rows = list(csv.reader(stream))
    require(bool(rows) and len(rows[0]) >= 3 and rows[0] == ['time', 'stimulus']+[f'soma{i}' for i in range(len(rows[0])-2)] and
            all(len(r) == len(rows[0]) for r in rows[1:]), 'single_pulse_trace_shape')
    data = [[number(float(v)) for v in r] for r in rows[1:]]
    observation = packet['observation'];spec = requested if observation is None else observation['specification']
    if observation is None:
        require(not data and packet['native_status'] != 'completed' and packet['prepared'] is None,
                'single_pulse_samples_without_context')
        return None, spec, None, [], len(rows[0])-2, {'recorded_window_complete': False, 'context_observed': False,
                'diagnostic_only': True, 'training_eligible': False, 'evaluation_verdict': None}
    require(set(observation) == {'schema_version', 'specification', 'complete', 'valid', 'end_reason', 'reasons',
            'sample_count', 'stimuli', 'peaks', 'burst_assignments', 'spikes', 'spike_count', 'first_stimulus_time'} and
            type(observation['schema_version']) is int and observation['schema_version'] == 4 and
            type(observation['valid']) is type(observation['complete']) is bool and type(observation['reasons']) is list and
            all(type(r) is str for r in observation['reasons']), 'single_pulse_observation_shape')
    _declaration(spec)
    for key in SPEC_FIELDS-{'time_frame', 'begin', 'end', 'baseline', 'effective_model_revision', 'stimulus_profile', 'windows'}:
        require(requested[key] == spec[key], 'single_pulse_requested_field_changed:'+key)
    begin, end = number(spec['begin']), number(spec['end'])
    require(spec['time_frame'] == 'absolute_model_time' and end > begin and equal(end, begin+requested['end']),
            'single_pulse_absolute_window_changed')
    profile = spec['stimulus_profile']
    require(type(profile) is dict and set(profile) == {'generator_class', 'amplitude', 'pulse_length', 'frequency_hz',
            'frequency_deviation', 'use_transit_signal', 'use_pattern_output'} and
            type(profile['generator_class']) is str and bool(profile['generator_class']) and
            number(profile['frequency_hz']) > 0 and number(profile['amplitude']) > 0 and
            number(profile['pulse_length']) >= 1/number(profile['frequency_hz']) and number(profile['frequency_deviation']) == 0 and
            profile['use_transit_signal'] is False and profile['use_pattern_output'] is False and
            (requested['stimulus_profile'] is None or requested['stimulus_profile'] == profile), 'single_pulse_source_profile_changed')
    require(all(r[1] in (0., profile['amplitude']) for r in data), 'single_pulse_stimulus_amplitude_changed')
    frequency = profile['frequency_hz'];prepared = packet['prepared']
    require(not after(number(spec['maximum_sample_gap']), 1/frequency), 'single_pulse_unsupported_sample_gap')
    require(type(prepared) is dict and set(prepared) == {'routing', 'input_id', 'protocol_revision', 'base_model_revision',
            'effective_model_revision', 'model_epoch', 'selected_input_index'} and
            prepared['routing'] in ('classic_burst', 'branch_solo_burst') and prepared['input_id'] == 'input'+str(c['selected_input_index']) and
            type(prepared['protocol_revision']) is str and bool(prepared['protocol_revision']) and
            prepared['effective_model_revision'] == spec['effective_model_revision'] and bool(prepared['effective_model_revision']) and
            packet['current_base_revision'] == prepared['base_model_revision'] and bool(prepared['base_model_revision']),
            'single_pulse_prepared_context_changed')
    branch = prepared['routing'] == 'branch_solo_burst';n = 1 if branch else c['physical_input_count']
    require((count(prepared['selected_input_index']) == c['selected_input_index']) if branch else prepared['selected_input_index'] is None,
            'single_pulse_solo_selector_changed')
    require(len(spec['baseline']) == len(rows[0])-2 == n and all(math.isfinite(number(v)) for v in spec['baseline']),
            'single_pulse_physical_dimension_changed')
    w = spec['windows'][0];rw = requested['windows'][0]
    require(set(w) == set(rw) == {'input_id', 'stimulus_id', 'channel', 'begin', 'end'} and
            w['input_id'] == prepared['input_id'] and w['stimulus_id'] == spec['expected_stimulus_ids'][0] and
            count(w['channel']) == (0 if branch else c['selected_input_index']) and
            all(w[k] == rw[k] for k in ('input_id', 'stimulus_id', 'channel')) and
            equal(w['begin'], begin+number(rw['begin'])) and equal(w['end'], begin+number(rw['end'])) and
            begin <= number(w['begin']) < number(w['end']) <= end, 'single_pulse_window_mapping_changed')
    require(len(data) == count(observation['sample_count']) <= count(spec['maximum_samples']) and
            observation['burst_assignments'] == [] and observation['spikes'] == [] and observation['spike_count'] is None,
            'single_pulse_unexpected_evidence')
    times = [r[0] for r in data]
    require(all(b > a and not after(b, a+number(spec['maximum_sample_gap'])) for a,b in zip(times,times[1:])) and
            all(not after(begin,t) and not after(t,end) for t in times), 'single_pulse_invalid_clock')
    if observation['complete']:require_primary_trace_clock(spec, observation['sample_count'], times)
    events = observation['stimuli'];require(type(events) is list and len(events) <= 1, 'single_pulse_extra_stimulus')
    if observation['complete']:require(len(events) == 1, 'single_pulse_missing_stimulus')
    for event in events:
        require(set(event) == {'id', 'time', 'relative_to_trial_start'} and event['id'] == spec['expected_stimulus_ids'][0] and
                equal(event['relative_to_trial_start'], number(event['time'])-begin) and
                any(equal(r[0], event['time']) and r[1] > 0 for r in data), 'single_pulse_stimulus_not_observed')
    require(observation['first_stimulus_time'] == (events[0]['time'] if events else None), 'single_pulse_first_stimulus_changed')
    rises = [r[0] for i,r in enumerate(data) if r[1] > 0 and (i == 0 or data[i-1][1] <= 0)]
    require(len(rises) == len(events) and all(equal(t,e['time']) for t,e in zip(rises,events)), 'single_pulse_unrecorded_stimulus')
    samples = [{'time':r[0], 'stimulus':r[1], 'soma':r[2:]} for r in data]
    validity = _peak(observation, spec, samples, begin)
    if packet['native_status'] == 'completed':
        require(not packet['reasons'] and packet['requires_fresh_verification'] is False and observation['complete'] and
                observation['end_reason'] == 'window_closed', 'single_pulse_completion_contradiction')
    else:
        require(packet['requires_fresh_verification'] and bool(packet['reasons']) and observation['valid'] is False,
                'single_pulse_rejection_contradiction')
    require(observation['valid'] == (observation['complete'] and not observation['reasons']), 'single_pulse_validity_contradiction')
    if validity != 'valid':require('peak_'+validity+':'+w['input_id'] in observation['reasons'], 'single_pulse_missing_peak_reason')
    return observation, spec, frequency, samples, n, {'recorded_window_complete': observation['complete'],
            'context_observed': True, 'measured_peak_validity': validity, 'sample_count':len(samples),
            'diagnostic_only':True, 'training_eligible':False, 'source_pattern_independently_verified':False, 'evaluation_verdict':None}
