"""Actual Recorder6 callbacks/CSV, including partial observations.

Partial data are inspected without filling missing packets, reset witnesses,
events, peaks, frames or a native closure. No training authority is produced.
"""
import csv
import io
import math

from .composite_measurement_contract import RAW_FIELDS
from .composite_source_evidence import keys
from .native_evidence import after, count, number, require
from .response_domain_evidence import SPEC_FIELDS, _same, _text

PREPARED_FIELDS = set(('routing input_id protocol_revision base_model_revision effective_model_revision '
                       'model_epoch selected_input_index').split())
PACKET_FIELDS = set(('kind evidence_schema_version native_status current_base_revision reasons '
                    'requires_fresh_verification requested_specification prepared observation').split())
OBSERVATION_FIELDS = set(('schema_version specification complete valid end_reason reasons sample_count stimuli '
                         'peaks burst_assignments spikes spike_count first_stimulus_time').split())
SPECIFICATION_FIELDS = set(SPEC_FIELDS.split()) | {'stimulus_subset'}


def _strings(values):
    require(type(values) is list and all(type(v) is str and v for v in values), 'composite_raw_reason_list')


def _specification(spec, *, frame):
    keys(spec, SPECIFICATION_FIELDS, 'composite_raw_specification_fields')
    require(count(spec['schema_version']) == 6 and spec['time_frame'] == frame
            and spec['record_spikes'] is False and spec['windows'] == []
            and spec['wave_assignment'] == 'window_only' and spec['peak_selection'] == 'isolated_window',
            'composite_raw_requires_recorder6_without_synthetic_peaks')
    count(spec['maximum_samples'])
    for field in ('run_id', 'trial_id', 'sample_id', 'pattern_hash'): _text(spec[field])
    for field in ('begin', 'end', 'maximum_sample_gap', 'minimum_amplitude'): number(spec[field])


def audit_native_packets(packets):
    require(type(packets) is list, 'composite_raw_packet_inventory')
    result = {}
    for packet in packets:
        keys(packet, PACKET_FIELDS, 'composite_raw_packet_fields')
        require(packet['kind'] == 'timelearner_native_probe_evidence' and count(packet['evidence_schema_version']) == 2
                and packet['native_status'] in ('idle', 'queued', 'running', 'completed', 'rejected', 'cancelled')
                and type(packet['requires_fresh_verification']) is bool, 'composite_raw_packet_schema_or_status')
        _strings(packet['reasons'])
        requested = packet['requested_specification']
        _specification(requested, frame='relative_to_trial_start')
        trial = requested['trial_id']; require(trial not in result, 'composite_raw_duplicate_native_packet')
        observation = packet['observation']
        if observation is not None:
            keys(observation, OBSERVATION_FIELDS, 'composite_raw_observation_fields')
            _specification(observation['specification'], frame='absolute_model_time')
            require(count(observation['schema_version']) == 6 and
                    type(observation['complete']) is type(observation['valid']) is bool and
                    observation['peaks'] == observation['burst_assignments'] == observation['spikes'] == []
                    and observation['spike_count'] is None, 'composite_raw_synthetic_observation')
            count(observation['sample_count']); _strings(observation['reasons'])
            for field in ('run_id', 'trial_id', 'sample_id', 'pattern_hash'):
                _same(observation['specification'][field], requested[field])
        else:
            require(packet['native_status'] != 'completed', 'composite_raw_completed_without_observation')
        result[trial] = packet
    return result


def audit_raw_trials(record, protocol, configuration, primary, packets):
    raw = record['raw_trials']; logical = record['logical_request']
    require(type(raw) is list, 'composite_raw_trial_inventory')
    n = len(protocol['inputs']); assigned = count(logical['input_index'])
    require(assigned < n, 'composite_raw_assigned_index')
    channels = n if protocol['routing'] == 'classic_burst' else 1
    seen = {}; frames = 0; bytes_count = 0
    for ordinal, trial in enumerate(raw):
        keys(trial, RAW_FIELDS, 'composite_raw_trial_fields')
        identity = _text(trial['native_trial_id'])
        require(identity not in seen and identity == record['group_id']+'/native/'+str(ordinal),
                'composite_raw_native_trial_order_or_reuse')
        prepared, spec = trial['prepared_context'], trial['actual_specification']
        keys(prepared, PREPARED_FIELDS, 'composite_raw_prepared_fields')
        _specification(spec, frame='absolute_model_time')
        require(spec['trial_id'] == identity and prepared['input_id'] == logical['input_id']
                and prepared['routing'] == logical['routing'] == protocol['routing']
                and prepared['protocol_revision'] == logical['protocol_revision'] == protocol['revision']
                and prepared['base_model_revision'] == logical['base_model_revision']
                and count(prepared['model_epoch']) == count(logical['model_epoch'])
                and prepared['effective_model_revision'] == spec['effective_model_revision'],
                'composite_raw_prepared_logical_binding')
        _text(prepared['effective_model_revision'])
        if protocol['routing'] == 'classic_burst':
            require(prepared['selected_input_index'] is None, 'composite_raw_classic_solo_index')
        else:
            require(count(prepared['selected_input_index']) == assigned, 'composite_raw_branch_solo_index')
        require(spec['sample_id'] == logical['sample_id'] == protocol['sample_id']
                and spec['run_id'] == logical['run_id'] and spec['maximum_sample_gap'] == protocol['maximum_sample_gap']
                and count(spec['maximum_samples']) == count(configuration['maximum_samples'])
                and number(spec['minimum_amplitude']) == number(protocol['minimum_amplitude']),
                'composite_raw_source_or_recorder_binding')
        _same(spec['stimulus_profile'], protocol['stimulus_profile'])
        require(number(spec['end']) > number(spec['begin']) and
                number(spec['end']) == number(spec['begin'])+number(configuration['duration']),
                'composite_raw_actual_window')
        subset = spec['stimulus_subset']
        keys(subset, {'purpose', 'source_training_pattern_hash', 'physical_input_count', 'source_ordinals'},
             'composite_raw_subset_fields')
        require(subset['purpose'] == 'stimulus_subset_characterization' and
                subset['source_training_pattern_hash'] == protocol['pattern_hash'] and
                count(subset['physical_input_count']) == n and ordinal < n+2, 'composite_raw_subset_source')
        mask = subset['source_ordinals']
        require(type(mask) is list, 'composite_raw_subset_inventory')
        expected = list(range(n)) if ordinal in (0, n+1) else [i for i in range(n) if i != ordinal-1]
        require([count(i) for i in mask] == expected, 'composite_raw_subset_order')
        _same(spec['expected_stimulus_ids'], ['pulse'+str(i) for i in expected])
        require(type(spec['baseline']) is list and len(spec['baseline']) == channels, 'composite_raw_baseline_dimension')
        baseline = [number(v) for v in spec['baseline']]
        reference = trial['primary_ref']; raw_bytes = primary[reference['relative_path']]
        rows = list(csv.reader(io.StringIO(raw_bytes.decode('utf-8'), newline=''), strict=True))
        require(rows and rows[0] == ['time', 'stimulus']+['soma'+str(i) for i in range(channels)]
                and all(len(row) == len(rows[0]) for row in rows[1:]), 'composite_raw_csv_columns')
        values = [[float(v) for v in row] for row in rows[1:]]
        times = [number(row[0]) for row in values]
        require(len(times) <= count(spec['maximum_samples']) and all(b > a for a, b in zip(times, times[1:]))
                and all(not after(spec['begin'], t) and not after(t, spec['end']) for t in times),
                'composite_raw_partial_clock_or_sample_budget')
        nonfinite = [{'row':i+2, 'column':rows[0][j]} for i,row in enumerate(values)
                     for j,v in enumerate(row[1:], 1) if not math.isfinite(v)]
        events = trial['actual_stimuli']; require(type(events) is list, 'composite_raw_actual_event_inventory')
        previous = -1
        for index, event in enumerate(events):
            keys(event, {'id', 'time', 'frame_index'}, 'composite_raw_event_fields')
            frame = count(event['frame_index'])
            require(index < len(expected) and event['id'] == 'pulse'+str(expected[index])
                    and previous < frame < len(times) and number(event['time']) == times[frame],
                    'composite_raw_actual_event_binding')
            previous = frame
        packet = packets.get(identity)
        if packet is not None:
            if packet['prepared'] is not None: _same(packet['prepared'], prepared)
            observation = packet['observation']
            if observation is not None:
                _same(observation['specification'], spec)
                require(count(observation['sample_count']) >= len(values), 'composite_raw_observation_lost_retained_frames')
                declared_events = observation['stimuli']
                require(type(declared_events) is list and len(declared_events) >= len(events), 'composite_raw_observation_missing_events')
                for actual, declared in zip(events, declared_events):
                    _same(actual['id'], declared['id']); _same(actual['time'], declared['time'])
        seen[identity] = {'trial':trial, 'packet':packet, 'spec':spec, 'prepared':prepared,
                          'times':times, 'values':values, 'baseline':baseline, 'mask':expected,
                          'nonfinite_cells':nonfinite, 'events':events}
        frames += len(values); bytes_count += len(raw_bytes)
    return seen, frames, bytes_count
