"""Compare complete frozen responses on the actual stimulus-relative clock.

The native observation auditor validates every input before comparison. Only
known timestamp fields are translated. Waveforms, onset-to-window offsets,
native sample grids and actual events remain subject to the fixed tolerance.
Pre-window detector history is retained in the primary data, but is outside
this response comparison, as in the native observation event extractor.
"""
from contextlib import contextmanager

from .native_evidence import after, number, require
from .recognition_trial_evidence import _recognition_trial_batch


def _delta(left, right):
    """Maximum absolute difference, or None when array dimensions differ."""
    if type(left) is list:
        if type(right) is not list or len(left) != len(right):
            return None
        values = [_delta(a, b) for a, b in zip(left, right)]
        return None if any(v is None for v in values) else max(values, default=0.)
    return number(abs(number(left)-number(right)))


def _maximum(values):
    return None if any(v is None for v in values) else max(values, default=0.)


def _compare(expected, observed, audit, tolerance):
    for item in (expected, observed):
        result = audit(item)
        require(result['valid_observation'] and result['complete'] and
                bool(item['stimulus_times']), 'response_comparison_requires_valid_closed_trial')
    require(expected['schema_version'] == observed['schema_version'],
            'response_comparison_observation_schema_changed')
    for key in ('sample_id', 'label', 'pattern_hash', 'pattern_isi', 'reset_policy',
                'frequency_hz', 'model_before', 'model_after'):
        require(expected[key] == observed[key], 'response_comparison_condition_changed:'+key)
    if expected['schema_version'] == 2:
        require(expected['threshold_potential_source'] == observed['threshold_potential_source'],
                'response_comparison_threshold_source_changed')

    origins = [number(o['stimulus_onset']) for o in (expected, observed)]
    def relative(o, key, origin):
        return [number(t)-origin for t in o[key]]
    window_delta = _delta(
        [number(expected[k])-origins[0] for k in ('begin', 'end', 'closed_at')],
        [number(observed[k])-origins[1] for k in ('begin', 'end', 'closed_at')])
    count_same = len(expected['samples']) == len(observed['samples'])
    signals = ('soma', 'lt_output', 'stimulus') + (
        ('lt_potential',) if expected['schema_version'] == 2 else ())
    signal_deltas, time_deltas, history_deltas = [], [], []
    for left, right in zip(expected['samples'], observed['samples']):
        signal_deltas.extend(_delta(left[k], right[k]) for k in signals)
        time_deltas.append(abs((number(left['time'])-origins[0])-
                               (number(right['time'])-origins[1])))
        for key in ('stimulus_history', 'spike_history'):
            projected = [[number(t)-origin for t in sample[key]
                          if not after(o['begin'], t)]
                         for o, sample, origin in zip((expected, observed), (left, right), origins)]
            history_deltas.append(_delta(*projected))
    signal_delta = _maximum(signal_deltas) if count_same else None
    time_delta = _maximum(time_deltas) if count_same else None
    history_delta = _maximum(history_deltas) if count_same else None
    event_delta = _maximum([_delta(relative(expected, key, origins[0]),
                                   relative(observed, key, origins[1]))
                            for key in ('stimulus_times', 'spike_times')])
    within = lambda value: value is not None and value <= tolerance
    window_same = within(window_delta)
    waveform_same = count_same and window_same and all(
        within(v) for v in (signal_delta, time_delta, history_delta))
    events_same = within(event_delta) and expected['spike_count'] == observed['spike_count']
    reasons = []
    for okay, reason in ((count_same, 'response_sample_count_changed'),
                         (window_same, 'response_window_or_onset_offset_changed'),
                         (within(signal_delta), 'response_signal_changed'),
                         (within(time_delta), 'response_relative_sample_times_changed'),
                         (within(history_delta), 'response_in_window_history_changed'),
                         (events_same, 'response_relative_events_changed')):
        if not okay:
            reasons.append(reason)
    return dict(kind='timelearner_trial_response_comparison', schema_version=1,
        comparator_version=1, time_basis='actual_stimulus_onset',
        absolute_tolerance=tolerance, observation_schema_version=expected['schema_version'],
        source_trial_id=expected['trial_id'], observed_trial_id=observed['trial_id'],
        sample_id=observed['sample_id'], model_revision=observed['model_before'],
        source_begin=expected['begin'], observed_begin=observed['begin'],
        source_stimulus_onset=origins[0], observed_stimulus_onset=origins[1],
        absolute_clock_shift=origins[1]-origins[0],
        source_samples=len(expected['samples']), observed_samples=len(observed['samples']),
        sample_counts_equal=count_same, window_offsets_equal=window_same,
        maximum_absolute_signal_difference=signal_delta,
        maximum_relative_sample_time_difference=time_delta,
        maximum_relative_history_difference=history_delta,
        maximum_relative_event_time_difference=event_delta,
        maximum_window_offset_difference=window_delta,
        maximum_absolute_sample_difference=_maximum([signal_delta,time_delta,history_delta]),
        waveforms_equal_within_declared_tolerance=waveform_same,
        stimulus_and_spike_events_equal=events_same,
        response_preserved=waveform_same and events_same, difference_reasons=reasons,
        pre_window_history_compared=False, scientific_verdict=None)


@contextmanager
def trial_response_comparison(package, *, physical_data=False, diagnostic=False,
                              absolute_tolerance=1e-12):
    """Audit the immutable model once and every complete observation in a batch."""
    tolerance = number(absolute_tolerance)
    require(tolerance == 1e-12, 'response_comparison_fixed_tolerance_required')
    with _recognition_trial_batch(package, physical_data=physical_data, diagnostic=diagnostic) as audit:
        yield lambda expected, observed: _compare(expected, observed, audit, tolerance)


def compare_trial_responses(expected, observed, package, **options):
    with trial_response_comparison(package, **options) as compare:
        return compare(expected, observed)
