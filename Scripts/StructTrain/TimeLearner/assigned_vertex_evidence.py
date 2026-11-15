"""Audit a native shared-vertex rejection; never score it as recognition."""
import csv
import hashlib
import io
import sys
from pathlib import Path

from .model_identity import canonical_model_sha256
from .native_evidence import (EvidenceError, after, count, equal, measured_wave_plateaus,
                              number, parse_json_bytes, require)


def audit_shared_vertex(packet, execution, rows):
    try:
        return _audit_shared_vertex(packet, execution, rows)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError('malformed_shared_vertex_evidence:'+str(error)) from error


def _audit_shared_vertex(packet, execution, rows):
    require(type(packet) is dict and set(packet) == {'kind', 'schema_version', 'observation',
            'rejection', 'native_pattern', 'model_revision', 'scientific_training_result'} and
            packet['kind'] == 'native_shared_vertex_certificate_guard' and
            type(packet['schema_version']) is int and packet['schema_version'] == 1 and
            packet['scientific_training_result'] is False, 'unknown_shared_vertex_schema')
    require(packet['rejection'] == 'shared_measured_peak_between_stimuli', 'shared_vertex_not_rejected')
    require(execution['kind'] == 'native_learner_probe_execution' and
            type(execution['schema_version']) is int and execution['schema_version'] == 1 and
            execution['status'] == 'completed' and execution['complete'] is True and
            execution['valid'] is True and execution['scientific_training_result'] is False and
            execution['selected_input_index'] is None and not execution['requires_fresh_verification'] and
            not execution['reasons'] and not execution['adapter_reasons'], 'shared_vertex_execution_not_complete')
    o = packet['observation']
    require(type(o['schema']) is int and o['schema'] == execution['observation_schema'] == 2 and
            o['complete'] is True and o['valid'] is True and not o['burst_assignments'],
            'shared_vertex_requires_historical_window_only')
    for key in ('run_id', 'trial_id', 'sample_id', 'protocol_revision', 'pattern_hash'):
        require(type(o[key]) is str and bool(o[key]), 'missing_shared_vertex_identity:'+key)
    require(o['trial_id'] == o['run_id']+'/probe0', 'shared_vertex_trial_identity_mismatch')
    revision = packet['model_revision']
    require(type(revision) is str and len(revision) == 64 and
            o['base_model_revision'] == revision == execution['current_base_revision'], 'shared_vertex_revision_mismatch')
    for key in ('model_before', 'model_after'):
        identity = execution[key]
        require(identity['valid'] is True and identity['sha256'] == revision and
                canonical_model_sha256(identity['model']) == revision, 'shared_vertex_effective_graph_changed')
    require(o['effective_model_revision'] == execution['effective_revision'], 'shared_vertex_effective_revision_mismatch')
    baseline = [number(v) for v in o['baseline']];n = count(execution['input_count'])
    require(len(baseline) == n >= 2, 'shared_vertex_physical_dimension_mismatch')
    pattern = packet['native_pattern']
    require(type(pattern) is list and len(pattern) == n and all(number(v) >= 0 for v in pattern) and
            canonical_model_sha256(pattern) == o['pattern_hash'], 'shared_vertex_pattern_mismatch')
    frequency = number(execution['frequency_hz']);gap = number(o['maximum_sample_gap'])
    profile = execution['stimulus_profile']
    require(frequency > 0 and equal(frequency, profile['frequency_hz']) and equal(gap, 1/frequency),
            'shared_vertex_frequency_mismatch')
    require(number(profile['amplitude']) > 0 and number(profile['pulse_length_s']) >= gap and
            number(profile['frequency_deviation']) == 0 and profile['transit'] is False and
            profile['pattern_output'] is False and type(profile['class']) is str and bool(profile['class']),
            'unsupported_shared_vertex_source')
    require(bool(rows) and rows[0] == ['native_tick_start_s', 'stimulus']+
            ['raw_soma_'+str(i) for i in range(n)] and all(len(row) == n+2 for row in rows[1:]),
            'unknown_shared_vertex_trace_schema')
    values = [[number(float(token)) for token in row] for row in rows[1:]]
    times = [v[0] for v in values];begin, end = number(o['begin']), number(o['end'])
    require(end > begin and len(times) == count(o['sample_count']) == count(execution['sampled_frames']) >= 3 and
            equal(times[0], begin) and equal(times[-1], end), 'incomplete_shared_vertex_trace')
    require(gap > 64*sys.float_info.epsilon*max(1., abs(begin), abs(end)),
            'insufficient_shared_vertex_timestamp_resolution')
    require(all(b > a and not after(b, a+gap) for a, b in zip(times, times[1:])), 'shared_vertex_sample_gap')
    stimuli = o['actual_stimuli'];ids = ['pulse'+str(i) for i in range(n)]
    require([e['id'] for e in stimuli] == ids and stimuli == execution['actual_stimuli'], 'shared_vertex_stimulus_mismatch')
    event_times = [number(e['time']) for e in stimuli]
    require(all(b > a for a, b in zip(event_times, event_times[1:])), 'shared_vertex_stimulus_order')
    for time in event_times:
        matches = [i for i, t in enumerate(times) if equal(t, time)]
        require(len(matches) == 1 and values[matches[0]][1] > 0, 'shared_vertex_stimulus_not_observed')
    windows, peaks = o['windows'], o['peaks']
    require(len(windows) == len(peaks) == n and len({w['input_id'] for w in windows}) == n and
            len({p['input_id'] for p in peaks}) == n, 'shared_vertex_duplicate_or_missing_input')
    peaks = {p['input_id']: p for p in peaks};channels = {count(w['channel']) for w in windows}
    require(len(channels) == 1 and next(iter(channels)) < n, 'shared_vertex_channel_mismatch')
    channel = next(iter(channels));shared = []
    require(number(o['minimum_amplitude']) > 0, 'invalid_shared_vertex_minimum_amplitude')
    require({w['stimulus_id'] for w in windows} == set(ids), 'shared_vertex_window_stimulus_mismatch')
    for window in windows:
        i = ids.index(window['stimulus_id']);peak = peaks[window['input_id']]
        require(window['input_id'] == 'input'+str(i) and peak['stimulus_id'] == window['stimulus_id'] and
                peak['validity'] == 'valid', 'shared_vertex_peak_mapping_mismatch')
        left, right = number(window['begin']), number(window['end'])
        require(begin <= left < right <= end, 'shared_vertex_window_outside_probe')
        indices = [j for j, t in enumerate(times) if not after(left, t) and not after(t, right)]
        require(len(indices) >= 3, 'shared_vertex_window_incomplete')
        signal = [number(values[j][channel+2]-baseline[channel]) for j in indices]
        waves = measured_wave_plateaus(signal, number(o['minimum_amplitude']))
        require(len(waves) == 1, 'shared_vertex_isolated_window_not_unique')
        first, last = waves[0];maximum = max(signal)
        require(signal[first] == maximum and signal[0] < maximum and signal[-1] < maximum,
                'shared_vertex_window_clipped')
        first, last = indices[first], indices[last]
        require(equal(times[first], peak['time']) and equal(times[last], peak['plateau_end']) and
                equal(values[first][channel+2], peak['raw']) and
                equal(values[first][channel+2]-baseline[channel], peak['amplitude']) and
                not after(event_times[i], times[first]), 'shared_vertex_peak_trace_mismatch')
        shared.append((first, last))
    require(len(set(shared)) == 1, 'shared_vertex_has_different_measured_vertices')
    first, last = shared[0]
    return {'kind': 'native_shared_vertex_trace_audit', 'schema_version': 1,
            'run_id': o['run_id'], 'model_revision': revision, 'sample_count': len(times),
            'channel_count': n, 'shared_channel': channel, 'shared_first_sample': first,
            'shared_last_sample': last, 'shared_peak_time': times[first], 'plateau_end': times[last],
            'actual_stimuli': stimuli, 'window_labels': ids, 'rejection_observed': packet['rejection'],
            'recorded_window_complete': True, 'spike_response': 'unknown', 'scientific_verdict': None}


def read_shared_vertex(path):
    path = Path(path);suffix = '_certificate_guard.json'
    require(path.name.endswith(suffix), 'unknown_shared_vertex_filename')
    stem = path.name[:-len(suffix)]
    names = {'guard': path, 'execution': path.with_name(stem+'.json'), 'trace': path.with_name(stem+'.csv')}
    raw = {key: value.read_bytes() for key, value in names.items()}
    packet, execution = (parse_json_bytes(raw[key]) for key in ('guard', 'execution'))
    rows = list(csv.reader(io.StringIO(raw['trace'].decode('utf-8'))))
    result = audit_shared_vertex(packet, execution, rows)
    require(result['run_id'] == stem, 'shared_vertex_filename_identity_mismatch')
    result['source_files'] = {key: {'name': names[key].name, 'bytes': len(value),
                            'sha256': hashlib.sha256(value).hexdigest()} for key, value in raw.items()}
    return result, packet, execution, rows
