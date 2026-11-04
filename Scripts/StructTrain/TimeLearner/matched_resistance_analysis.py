"""Measured Rs controls with identical model clocks and actual input pulses.

Only soma/burst characterization is reported. No training, spiking detection or
classification verdict can be obtained from these diagnostic source models.
"""
import csv
import math
from pathlib import Path

from .model_identity import canonical_model_sha256 as sha
from .native_characterization import audit_execution
from .native_evidence import audit_probe, load, number, require
from .probe_diagnostics import audit_recorded_wave_diagnostics, read_partial_probe


def _trace(folder, stem='probe_trial_1'):
    packet, path = load(folder/(stem+'.json')), folder/(stem+'.csv')
    checked = audit_probe(packet, path)
    if checked['valid_observation']:
        observation = packet['observation'];spec = observation['specification']
        with path.open(newline='', encoding='utf-8') as stream:rows = list(csv.reader(stream))[1:]
        samples = [{'time': number(float(r[0])), 'stimulus': number(float(r[1])),
                    'soma': [number(float(v)) for v in r[2:]]} for r in rows]
    else:
        observation, spec, _, samples, _, quality = read_partial_probe(packet, path)
        require(quality['recorded_window_complete'] and not quality['nonfinite_cells'], 'matched_control_requires_closed_finite_trace')
        audit_recorded_wave_diagnostics(observation, spec, samples, quality)
    require(observation is not None and observation['complete'] and samples, 'matched_control_requires_complete_observation')
    return packet, spec, samples


def analyze(directory):
    directory = Path(directory).resolve(strict=True)
    rows = load(directory/'index.json')['rows']
    require(type(rows) is list and len(rows) == 6 and
            {(r['branch'], r['variant']) for r in rows} == {(b, v) for b in (False, True) for v in ('baseline', 'resistance', 'matched-control')},
            'matched_control_coverage_missing')
    results = []
    for branch in (False, True):
        selected = {r['variant']: directory/'runs'/r['name']/'native' for r in rows if r['branch'] is branch}
        for folder in selected.values():audit_execution(folder)
        jobs = {k: load(v/'job.json') for k, v in selected.items()}
        require(len({j['source_stopped']['sha256'] for j in jobs.values()}) == 1, 'matched_control_source_models_differ')
        replay, _, _ = _trace(selected['baseline'])
        control, control_spec, a = _trace(selected['matched-control'])
        changed, changed_spec, b = _trace(selected['resistance'])
        # Equal absolute times also control generator sampling/rounding at the
        # scheduler boundary. Merely shifting a picture to onset is insufficient.
        times_match = len(a) == len(b) and [v['time'] for v in a] == [v['time'] for v in b]
        windows_match = control_spec['begin'] == changed_spec['begin'] and control_spec['end'] == changed_spec['end']
        stimulus_match = times_match and [v['stimulus'] for v in a] == [v['stimulus'] for v in b] and control['observation']['stimuli'] == changed['observation']['stimuli']
        source_warm_equal = (selected['matched-control']/'baseline_trial_1.csv').read_bytes() == (selected['resistance']/'baseline_trial_1.csv').read_bytes()
        replay_warm_equal = (selected['baseline']/'probe_trial_1.csv').read_bytes() == (selected['matched-control']/'baseline_trial_1.csv').read_bytes()
        runtime_match = load(selected['matched-control'].parent/'process/runtime.json')['runtime_fingerprint'] == load(selected['resistance'].parent/'process/runtime.json')['runtime_fingerprint']
        matched = times_match and windows_match and stimulus_match and source_warm_equal and replay_warm_equal and runtime_match
        differences = []
        if matched:
            channels = len(control_spec['baseline'])
            require(channels == len(changed_spec['baseline']), 'matched_control_channel_dimension_changed')
            for channel in range(channels):
                delta = [number(y['soma'][channel]-x['soma'][channel]) for x, y in zip(a, b)]
                differences.append({'channel': channel, 'maximum_absolute_potential_difference': max(abs(d) for d in delta),
                    'rms_potential_difference': math.sqrt(math.fsum(d*d for d in delta)/len(delta)),
                    'control_maximum_potential': max(v['soma'][channel] for v in a),
                    'changed_maximum_potential': max(v['soma'][channel] for v in b)})
        def waves(packet):
            return [{'channel': x['channel'], 'count': len(x['waves']), 'assignment_validity': x['validity']}
                    for x in packet['observation']['burst_assignments']]
        results.append({'branch': branch, 'source_stopped_sha256': jobs['baseline']['source_stopped']['sha256'],
            'conditions_matched': matched, 'absolute_sample_times_equal': times_match, 'windows_equal': windows_match,
            'actual_stimulus_rows_and_events_equal': stimulus_match, 'runtime_equal': runtime_match,
            'warm_source_traces_byte_equal': source_warm_equal, 'replay_and_warm_source_traces_byte_equal': replay_warm_equal,
            'model_time_begin': control_spec['begin'], 'model_time_end': control_spec['end'],
            'replay_waves': waves(replay), 'control_waves': waves(control), 'changed_waves': waves(changed),
            'potential_differences': differences, 'source_model_revision': jobs['baseline']['source_stopped']['model_revision'],
            'control_model_revision': load(selected['matched-control']/'initial-state.json')['identity']['sha256'],
            'changed_model_revision': load(selected['resistance']/'initial-state.json')['identity']['sha256']})
    return {'kind': 'matched_resistance_characterization', 'schema_version': 1, 'rows': results,
            'all_conditions_matched': all(r['conditions_matched'] for r in results),
            'training_executed': False, 'spiking_response_measured': False, 'scientific_classification_verdict': None,
            'analysis_version': 1, 'input_matrix_sha256': sha(rows)}
