"""Audit the observed prefix before the second actual stimulus, not a new trial.

An isolated prefix can falsify one-maximum-per-stimulus without claiming that
later peaks have been decomposed into individual physical responses.
"""
from pathlib import Path
import argparse
import json

from .candidate_recovery_evidence import audit_unassigned_burst
from .native_evidence import load, measured_wave_plateaus, number, require
from .probe_diagnostics import read_partial_probe
from .stopped_evidence import load_case, audit_stopped_state
from .stock_wave_replay import select_packet


def audit_prefix(packet, trace, protocol):
    # Reuse the strict whole-trace auditor, including actual stimulus edge times
    # and every recorded wave. A valid prefix never repairs an invalid burst.
    whole = audit_unassigned_burst(packet, Path(trace), protocol)
    observation, spec, _, samples, _, quality = read_partial_probe(packet, Path(trace))
    require(quality['recorded_window_complete'] and len(observation['stimuli']) >= 2,
            'first_pulse_requires_complete_window_and_second_stimulus')
    first, second = [number(e['time']) for e in observation['stimuli'][:2]]
    prefix = [s for s in samples if s['time'] < second]
    require(len(prefix) >= 3 and prefix[0]['time'] <= first < prefix[-1]['time'] < second,
            'first_pulse_prefix_has_insufficient_samples')
    channel = spec['windows'][0]['channel']
    baseline = number(spec['baseline'][channel]);minimum = number(spec['minimum_amplitude'])
    signal = [number(s['soma'][channel])-baseline for s in prefix]
    peaks = []
    for start, end in measured_wave_plateaus(signal, minimum):
        require(prefix[start]['time'] >= first, 'first_pulse_peak_precedes_observed_stimulus')
        peaks.append({'time': prefix[start]['time'], 'plateau_end': prefix[end]['time'],
                      'delay_from_first_stimulus': prefix[start]['time']-first,
                      'amplitude_above_native_baseline': signal[start],
                      'raw_potential': prefix[start]['soma'][channel]})
    return {'kind': 'stock_first_stimulus_prefix_audit', 'schema_version': 1,
            'trial_id': spec['trial_id'], 'model_revision': whole['model_revision'],
            'input_id': whole['input_id'], 'channel': channel,
            'first_actual_stimulus': first, 'second_actual_stimulus': second,
            'prefix_end_exclusive': second, 'prefix_samples': len(prefix),
            'minimum_amplitude': minimum, 'interior_positive_maxima': peaks,
            'interior_positive_maxima_count': len(peaks),
            'selected_channel_only': True, 'original_burst_validity': whole['validity'],
            'whole_trace_and_stimuli_audited': True,
            'boundary_extrema_not_inferred': True,
            'new_single_pulse_trial_executed': False,
            'later_waves_decomposed': False, 'valid_training_measurement': False,
            'scientific_verdict': None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_stopped', type=Path)
    args = parser.parse_args()
    case = load_case(args.source_stopped.resolve(strict=True))
    audit_stopped_state(*case)
    packet = select_packet(case[0])
    trial = packet['requested_specification']['trial_id']
    print(json.dumps(audit_prefix(packet, case[3][trial], case[0]['protocol']), indent=2))


if __name__ == '__main__':
    main()
