"""LT decision views from observations already checked by the report scorer.

Projection is for plotting only. It must never be passed to a scorer in place
of the original soma observations or be used to infer missing spike events.
"""
from pathlib import Path

from .native_evidence import number, require
from .plotting import padded_limits, render_soma, render_positive_lobe_views


def render_lt_decisions(spec, observations, threshold, output: Path, *, context_label=None):
    by_id = {o['trial_id']: o for o in observations}
    require(len(by_id) == len(observations), 'lt_plot_duplicate_observation')
    trials = sorted(spec['trials'], key=lambda t: t['presentation_index'])
    require(set(by_id).issubset({t['trial_id'] for t in trials}), 'lt_plot_foreign_observation')
    available, unavailable = [], []
    for trial in trials:
        observation = by_id.get(trial['trial_id'])
        if observation is None or not observation['samples']:
            unavailable.append(dict(trial_id=trial['trial_id'], reason='no_recorded_samples'))
        elif observation['schema_version'] == 1:
            unavailable.append(dict(trial_id=trial['trial_id'], reason='legacy_lt_channel_not_recorded'))
        else:
            require(observation['schema_version'] == 2, 'lt_plot_unknown_observation_schema')
            descriptor = observation.get('threshold_potential_source')
            require(type(descriptor) is dict and type(descriptor.get('path')) is str and
                    descriptor['path'], 'lt_plot_missing_source_descriptor')
            require(all('lt_potential' in s for s in observation['samples']),
                    'lt_plot_missing_recorded_potential')
            values = [number(s['lt_potential']) for s in observation['samples']]
            available.append((trial, observation, descriptor, values))
    # Validate all scalars before creating a figure or silently hiding a bad value.
    threshold = number(threshold) if available else threshold
    values = [v for _, _, _, row in available for v in row]
    limits = padded_limits([threshold]+values) if available else None
    decisions = []
    for trial, observation, descriptor, values in available:
        index = trial['presentation_index']
        maximum = max(range(len(values)), key=values.__getitem__)
        peak_details = ([maximum] if min(values) < max(values) and
                        0 < maximum < len(values)-1 else [])
        projected = {**observation, 'diagnostic_peak_indices': peak_details,
                     'samples': [{**s, 'soma': [s['lt_potential']]}
                                 for s in observation['samples']]}
        folder = output/f'trial-{index:04d}-lt-decision'
        require(not folder.exists(), 'lt_plot_output_exists')
        folder.mkdir()
        context = context_label
        views = render_soma(projected, 0, descriptor['path'], limits, folder,
            potential_axis_label='LT decision potential [model units; SI unverified]',
            reference_level=threshold, context_label=context)
        views.extend(render_positive_lobe_views(projected, 0, descriptor["path"], folder,
            potential_axis_label="LT decision potential [model units; SI unverified]",
            reference_level=threshold, context_label=context, shared_minimum=min(
                v for _, _, _, row in available for v in row)))
        decisions.append(dict(sample_id=observation['sample_id'], trial_id=observation['trial_id'],
            folder=folder.name, source_descriptor=descriptor,
            observation_complete=observation['complete'], observation_valid=observation['valid'],
            actual_spike_times=list(observation['spike_times']),
            recorded_global_maximum=dict(sample_index=maximum,
                time=observation['samples'][maximum]['time'], value=values[maximum],
                at_recording_boundary=maximum in (0, len(values)-1)), views=views))
    return dict(kind='native_lt_decision_plot_views', schema_version=1,
        source_model_revision=spec['model_revision'], threshold=threshold,
        projection_for_plotting_only=True, native_observations_changed=False,
        note='Native after-children samples may already reflect LT event/reset; actual spike markers are authoritative.',
        declared_trial_count=len(trials), all_declared_trials_rendered=len(decisions)==len(trials),
        all_observations_complete=bool(decisions) and all(d['observation_complete'] for d in decisions),
        unavailable_trials=unavailable, trials=decisions,
        visual_acceptance_complete=False, scientific_verdict=None)
