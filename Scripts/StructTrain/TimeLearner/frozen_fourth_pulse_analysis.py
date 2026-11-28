"""Audit fourth-impulse interventions against complete, same-history responses.

Prefixes are derived comparisons of retained complete trials. They are never
substituted for observations, classifier windows, or training certificates.
"""
from copy import deepcopy
from pathlib import Path

from .frozen_fourth_pulse_history import declare_job
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import after, load, number, require
from .recognition_trial_evidence import _recognition_trial_batch
from .runtime import file_record
from .trial_response_comparison import _delta, _maximum, trial_response_comparison

TOLERANCE = 1e-12


def compare_probe_prefix(reference, observed, package):
    """Compare recorded signals/history strictly before either fourth event.

    Both inputs must remain complete and pass the production observation audit.
    Different labels and fourth intervals are intentional; the caller separately
    validates the full intervention declaration and its five preceding trials.
    """
    with _recognition_trial_batch(package, physical_data=True) as audit:
        for item in (reference, observed):
            checked = audit(item)
            require(checked['valid_observation'] and checked['complete'],
                    'fourth_prefix_requires_complete_valid_trials')
    require(reference['schema_version'] == observed['schema_version'] == 2,
            'fourth_prefix_requires_recorded_threshold_potential')
    for key in ('frequency_hz', 'reset_policy', 'model_before', 'model_after',
                'threshold_potential_source'):
        require(reference[key] == observed[key], 'fourth_prefix_condition_changed:'+key)
    require(all(len(o['pattern_isi']) == len(o['stimulus_times']) == 4
                for o in (reference, observed)) and
            reference['pattern_isi'][:3] == observed['pattern_isi'][:3],
            'fourth_prefix_requires_same_first_three_of_M4')
    origins = [number(o['stimulus_onset']) for o in (reference, observed)]
    inputs = [[number(t)-origin for t in o['stimulus_times']]
              for o, origin in zip((reference, observed), origins)]
    require(_delta(inputs[0][:3], inputs[1][:3]) <= TOLERANCE,
            'fourth_prefix_actual_first_three_inputs_changed')
    offsets = [[number(o[k])-origin for k in ('begin', 'end', 'closed_at')]
               for o, origin in zip((reference, observed), origins)]
    require(_delta(*offsets) <= TOLERANCE, 'fourth_prefix_full_windows_changed')
    cutoff = min(inputs[0][3], inputs[1][3])
    selected = [[s for s in o['samples'] if after(cutoff, number(s['time'])-origin)]
                for o, origin in zip((reference, observed), origins)]
    require(all(selected), 'fourth_prefix_has_no_recorded_samples')
    same_count = len(selected[0]) == len(selected[1])
    signal_deltas, time_deltas, history_deltas = [], [], []
    for left, right in zip(*selected):
        signal_deltas.extend(_delta(left[k], right[k])
                             for k in ('soma', 'lt_output', 'lt_potential', 'stimulus'))
        time_deltas.append(abs((number(left['time'])-origins[0])-
                               (number(right['time'])-origins[1])))
        for key in ('stimulus_history', 'spike_history'):
            history = [[number(t)-origin for t in sample[key]
                        if after(cutoff, number(t)-origin)]
                       for sample, origin in zip((left, right), origins)]
            history_deltas.append(_delta(*history))
    spikes = [[number(t)-origin for t in o['spike_times']
               if after(cutoff, number(t)-origin)]
              for o, origin in zip((reference, observed), origins)]
    deltas = dict(signals=_maximum(signal_deltas) if same_count else None,
                  sample_times=_maximum(time_deltas) if same_count else None,
                  recorded_histories=_maximum(history_deltas) if same_count else None,
                  spike_times=_delta(*spikes))
    reasons = ([] if same_count else ['prefix_sample_count_changed']) + [
        'prefix_'+key+'_changed' for key, value in deltas.items()
        if value is None or value > TOLERANCE]
    return dict(kind='timelearner_fourth_probe_prefix_comparison', schema_version=1,
        source_trial_id=reference['trial_id'], observed_trial_id=observed['trial_id'],
        actual_fourth_relative_seconds=[v[3] for v in inputs],
        cutoff_relative_seconds=cutoff, cutoff_sample_excluded=True,
        source_prefix_samples=len(selected[0]), observed_prefix_samples=len(selected[1]),
        absolute_tolerance=TOLERANCE, maximum_absolute_differences=deltas,
        recorded_signal_and_event_prefix_preserved=not reasons, difference_reasons=reasons,
        source_spikes_before_cutoff=spikes[0], observed_spikes_before_cutoff=spikes[1],
        full_observations_retained=True, pre_window_recorded_history_compared=True,
        hidden_state_equality_claimed=False, classification_recomputed_from_prefix=False,
        scientific_verdict=None)


def _same_physical_model(left, right):
    # Each complete model is audited by the production execution reader below.
    # Raw native XML can use different compiler type spellings; use its audited
    # typed identities and compare every physical/control field used by the wire.
    fields = ('model_revision', 'parameters', 'configuration', 'configuration_text',
              'threshold', 'controls', 'dataset')
    require(all(left[k] == right[k] for k in fields) and
            left['neuron']['graph']['identity'] == right['neuron']['graph']['identity'],
            'fourth_analysis_physical_model_changed')
    def classes(model):
        rows = model['neuron']['class_definitions']
        result = {r['name']:r['snapshot']['identity'] for r in rows}
        require(len(result) == len(rows), 'fourth_analysis_duplicate_class_image')
        return result
    require(classes(left) == classes(right), 'fourth_analysis_storage_physics_changed')


def analyze(baseline_job_path, reference_directory, observed_directory, *, tick, reset_policy):
    """Reaudit the two full native runs, their declared jobs and causal prefix."""
    from .native_pipeline_worker import audit_execution, validate_job
    baseline_job_path = Path(baseline_job_path).resolve(strict=True)
    paths = [Path(p).resolve(strict=True) for p in (reference_directory, observed_directory)]
    baseline = load(baseline_job_path)
    validate_job('physical-model-evaluate', baseline, (baseline['source_model_data'],))
    jobs = [load(p/'job.json') for p in paths]
    models = [j['source_model_data'] for j in jobs]
    _same_physical_model(models[0], models[1])
    _same_physical_model(baseline['source_model_data'], models[0])
    audits, observations = [], []
    for path, job, model, value in zip(paths, jobs, models, (960, tick)):
        # Project only the already verified equivalent model representation into
        # an expected declaration. No source document is edited or imported.
        source = deepcopy(baseline)
        source.pop('sha256'); source['source_model_data'] = model; source['sha256'] = sha(source)
        expected, _ = declare_job(source, job['run_id'], fourth_from_first_ticks=value,
                                  reset_policy=reset_policy)
        require(job == expected, 'fourth_analysis_job_outside_declared_protocol')
        audit = audit_execution('physical-model-evaluate', path, job, (model,))
        require(audit['frozen_model_verified'] and audit['metrics']['validity'] == 'valid'
                and len(audit['metrics']['trials']) == 8, 'fourth_analysis_full_run_invalid')
        audits.append(audit)
        observations.append([load(path/f'trial-{i}.json') for i in range(8)])
    history = []
    with trial_response_comparison(models[1], physical_data=True) as compare:
        for i in range(5):
            history.append(compare(observations[0][i], observations[1][i]))
    prefix = compare_probe_prefix(observations[0][5], observations[1][5], models[1])
    history_same = all(row['response_preserved'] for row in history)
    bindings = {'baseline_job':file_record(baseline_job_path)}
    for role, path in zip(('reference', 'observed'), paths):
        bindings[role] = {n:file_record(path/n) for n in
                         ('job.json', 'execution.json', 'evaluation.json',
                          *[f'trial-{i}.json' for i in range(8)])}
    return dict(kind='timelearner_fourth_history_scientific_analysis', schema_version=1,
        tick=tick, reset_policy=reset_policy, model_revision=models[1]['model_revision'],
        fixed_threshold=models[1]['threshold'], primary_bindings=bindings,
        full_runs_audited=True, common_history_comparisons=history,
        common_five_complete_responses_preserved=history_same, probe_prefix=prefix,
        prefix_comparability_verified=history_same and
            prefix['recorded_signal_and_event_prefix_preserved'],
        reference_counts=audits[0]['metrics']['pooled_counts'],
        observed_counts=audits[1]['metrics']['pooled_counts'],
        counts_from_complete_native_windows=True, new_training=False,
        threshold_selected=False, independent_holdout_claimed=False,
        training_certificate_inferred=False, scientific_verdict=None)
