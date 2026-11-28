"""Propose a diagnostic threshold from complete, frozen physical DATA reactions.

The whole-response LT maximum proposes a scalar; only a subsequent native run
can measure spiking classification. No training or calibration proof transfers
from a physical DATA file or from this portable primary-data audit.
"""
import math
from pathlib import Path

from .collector_provenance import _frozen
from .native_evidence import number, parse_json_bytes, require
from .runtime import file_record


RULE = 'midpoint_of_target_maximum_and_highest_strictly_lower_foil_maximum'
CRITERION = dict(id='post_anchor_target_whole_window_foil_v1', anchor='onset',
                 begin_offset=0., end_offset=None, reject_target_outside_window=True)


def midgap_from_rows(rows):
    """Original eight-pattern diagnostic rule, including negative outcomes.

    A foil above the target stays a predicted false positive; it does not make
    the gap below the target disappear. Equal peaks are never separated by an
    invented epsilon. Returned counts are nonspiking proxies only.
    """
    require(type(rows) is list and len(rows) == 8 and
            all(type(r) is dict and all(type(r.get(k)) is str and r[k]
                for k in ('trial_id', 'sample_id', 'label')) for r in rows),
            'physical_threshold_eight_identified_rows_required')
    require(len({r['trial_id'] for r in rows}) == len({r['sample_id'] for r in rows}) == 8,
            'physical_threshold_duplicate_identity')
    targets = [number(r['lt_maximum']) for r in rows if r['label'] == 'target']
    foils = [number(r['lt_maximum']) for r in rows if r['label'] == 'foil']
    require(len(targets) == 1 and len(foils) == 7, 'physical_threshold_phasea_labels')
    upper = targets[0]
    below = [v for v in foils if v < upper]
    margin = upper-max(foils)
    if not below:
        return dict(status='nonseparable', reason='no_strictly_lower_foil_maximum',
                    threshold=None, lower_peak=None, upper_peak=upper,
                    full_matrix_peak_margin=margin, nonspiking_proxy=None)
    lower = max(below)
    threshold = lower+(upper-lower)/2
    if not math.isfinite(threshold) or not lower < threshold < upper:
        return dict(status='unresolved', reason='midgap_not_representable',
                    threshold=None, lower_peak=lower, upper_peak=upper,
                    full_matrix_peak_margin=margin, nonspiking_proxy=None)
    return dict(status='candidate', reason='', threshold=threshold,
        lower_peak=lower, upper_peak=upper, full_matrix_peak_margin=margin,
        nonspiking_proxy=dict(TP=1, FN=0, FP=sum(v >= threshold for v in foils),
                             TN=sum(v < threshold for v in foils)))


def propose_physical_same_matrix_threshold(directory, job, model):
    """Audit the actual full baseline before proposing one native candidate.

    Callers must separately verify the owned process and publish provenance.
    This function requires the original nonspiking threshold 100, complete
    reset-per-trial observations, recorded LT potential and the onset criterion.
    It retains the source boundary without claiming to audit source training.
    """
    from .native_pipeline_worker import audit_execution, _artifact_records

    directory = Path(directory).resolve(strict=True)
    before = file_record(directory/'execution.json')
    audited = audit_execution('physical-model-evaluate', directory, job, (model,))
    metrics = audited['metrics']
    require(audited['frozen_model_verified'] and metrics is not None and
            metrics['validity'] == 'valid' and metrics['data_only'] and
            metrics['effective_threshold'] == 100. and model['schema_version'] in (1, 2),
            'physical_threshold_original_nonspiking_baseline_required')
    execution_raw, _ = _frozen(directory/'execution.json', 16*1024**2)
    execution = parse_json_bytes(execution_raw)
    require(execution['execution'] == 'completed', 'physical_threshold_baseline_incomplete')
    records = {r['path']: r for r in execution['artifacts']}

    def bound(name):
        require(type(name) is str and name in records and Path(name).name == name,
                'physical_threshold_primary_path')
        raw, record = _frozen(directory/name, 16*1024**2)
        require(all(record[k] == records[name][k] for k in ('bytes', 'sha256')),
                'physical_threshold_primary_changed')
        return parse_json_bytes(raw)

    spec = bound('evaluation.json')
    require(spec['criterion'] == CRITERION and spec['coverage_policy'] == 'per_trial_windows'
            and len(spec['trials']) == 8, 'physical_threshold_original_eight_onset_protocol_required')
    rows = []
    for trial in spec['trials']:
        observation = bound(trial['observation'])
        require(observation['schema_version'] == 2 and observation['complete'] is True
            and observation['valid'] is True and observation['censored'] is False
            and observation['spike_count'] == 0 and observation['spike_times'] == []
            and observation['reset_policy'] == 'reset_per_trial'
            and observation['model_before'] == observation['model_after'] == model['model_revision']
            and all(observation[k] == trial[k] for k in
                    ('trial_id', 'sample_id', 'label', 'pattern_hash')),
            'physical_threshold_complete_nonspiking_observation_required')
        samples = observation['samples']
        require(type(samples) is list and samples, 'physical_threshold_missing_recorded_samples')
        potentials = [number(s['lt_potential']) for s in samples]
        maximum = max(potentials)
        frame = potentials.index(maximum)
        rows.append(dict(trial_id=trial['trial_id'], sample_id=trial['sample_id'],
            label=trial['label'], pattern_hash=trial['pattern_hash'], lt_maximum=maximum,
            first_maximum_frame=frame, maximum_time=number(samples[frame]['time']),
            samples=len(samples), threshold_potential_source=observation['threshold_potential_source']))
    proposal = midgap_from_rows(rows)
    _artifact_records(directory, execution)
    require(file_record(directory/'execution.json') == before,
            'physical_threshold_execution_changed')
    return dict(kind='physical_DATA_same_matrix_threshold_proposal', schema_version=1,
        rule=RULE, source_execution=before, source_model_revision=model['model_revision'],
        source_model_data_sha256=model['sha256'], source_boundary=model['source_boundary'],
        rows=rows, **proposal, protocol='historical_same_matrix',
        all_baseline_primary_bytes_verified=True, frozen_model_verified=True,
        source_training_evidence_checked=False, training_certificate_transferred=False,
        calibrated=False, classification_assessed=False, actual_native_confirmation_required=True,
        native_execution_attested=False, scientific_verdict=None)
