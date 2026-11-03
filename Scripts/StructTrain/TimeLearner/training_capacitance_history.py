"""Bind schema3 training history to actual per-trial physical C witnesses."""
from .domain_evidence import audit_resistance_domain
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, count, require
from .training_capacitance_witness import audit_training_capacitance_registry, validate_witness_input_parameters


def _audit(summary, packets):
    require(type(summary) is dict and summary.get('kind') == 'native_training_state_summary' and
            type(summary.get('schema_version')) is int and summary['schema_version'] == 3,
            'unknown_training_capacitance_history_schema')
    history = summary['capacitance_history']
    require(type(history) is dict and set(history) == {'capture_witness_id', 'current_witness_id',
            'current_verified', 'witnesses', 'trial_witness_ids', 'resistance_domain_witness_ids'},
            'unknown_training_capacitance_history_fields')
    witnesses, trial_ids = history['witnesses'], history['trial_witness_ids']
    require(type(witnesses) is dict and type(trial_ids) is dict and type(packets) is dict and
            type(history['current_verified']) is bool, 'invalid_training_capacitance_history')
    required = {}

    def witness(key, revision=None):
        require(type(key) is str and key in witnesses, 'missing_training_capacitance_history_witness')
        value = witnesses[key]
        require(type(value) is dict and (revision is None or value['model_revision'] == revision),
                'training_capacitance_history_revision_mismatch')
        required[key] = value['model_revision']
        return value

    def trial(trial_id, revision=None, parameters=None):
        require(type(trial_id) is str and trial_id in trial_ids, 'unwitnessed_training_history_trial')
        value = witness(trial_ids[trial_id], revision)
        if parameters is not None:
            require(value['controller_parameters'] == parameters, 'training_history_capacitance_context_mismatch')
        if trial_id in packets:
            packet = packets[trial_id]
            require(packet['requested_specification']['trial_id'] == trial_id and
                    packet['current_base_revision'] == value['model_revision'],
                    'training_history_packet_revision_mismatch')
        return value

    capture = witness(history['capture_witness_id'], summary.get('reference_model_revision'))
    current = witness(history['current_witness_id'])
    actual_id = summary['actual_capacitance_witness_id']
    if actual_id is None:
        require(not history['current_verified'] or current['model_revision'] != summary['actual_model_revision'],
                'missing_verified_actual_capacitance_witness')
        require(summary['certificate_matches_actual_model'] is False, 'unverified_capacitance_certificate')
    else:
        require(history['current_verified'] and actual_id == history['current_witness_id'],
                'invalid_actual_capacitance_witness')
        actual = witness(actual_id, summary['actual_model_revision'])
        validate_witness_input_parameters(actual, summary['actual_parameters'])
    for trial_id in trial_ids:
        trial(trial_id)
    for reference in summary['references']:
        value = trial(reference['trial_id'], summary['reference_model_revision'])
        require(reference['capacitance_witness_id'] == trial_ids[reference['trial_id']] and
                value['controller_parameters'] == capture['controller_parameters'],
                'reference_capacitance_context_mismatch')
    for candidate in summary['candidates']:
        value = trial(candidate['trial_id'], candidate['model_revision'], candidate['capacitance'])
        require(candidate['capacitance_witness_id'] == trial_ids[candidate['trial_id']],
                'candidate_capacitance_witness_mismatch')
        trial(candidate['anchor_trial_id'], candidate['model_revision'], candidate['capacitance'])
        validate_witness_input_parameters(value, candidate['full_parameters'])
    for group in summary['candidate_repeat_groups']:
        for field, id_field in [('trial_ids', 'capacitance_witness_ids'),
                                ('anchor_trial_ids', 'anchor_capacitance_witness_ids')]:
            require(type(group[id_field]) is list and len(group[id_field]) == len(group[field]),
                    'training_repeat_capacitance_dimensions_mismatch')
            for trial_id, key in zip(group[field], group[id_field]):
                value = trial(trial_id, group['model_revision'], group['capacitance'])
                require(key == trial_ids[trial_id], 'training_repeat_capacitance_witness_mismatch')
                validate_witness_input_parameters(value, group['full_parameters'])
    if summary['search_history_retained']:
        require(summary['accepted_capacitance'] == current['controller_parameters'],
                'accepted_capacitance_context_mismatch')
        validate_witness_input_parameters(current, summary['accepted_parameters'])
    else:
        require('accepted_capacitance' not in summary, 'unretained_search_contains_capacitance_candidate')
    ids, domains = history['resistance_domain_witness_ids'], summary['resistance_domains']
    require(type(ids) is list and len(ids) == len(domains), 'training_domain_capacitance_dimensions_mismatch')
    previews = {}
    for key, domain in zip(ids, domains):
        base = witness(key, domain['base_model_revision'])
        require(domain['schema_version'] == 3, 'unversioned_training_capacitance_domain')
        audit_resistance_domain(domain)
        require(domain['requested_capacitance']['origin'] == base['controller_parameters']['origin'] and
                domain['requested_capacitance']['maximum_relative_change'] == base['controller_parameters']['maximum_relative_change'],
                'training_domain_capacitance_origin_or_policy_changed')
        if domain['effective_capacitance'] is not None:
            preview = {'kind': 'native_training_capacitance_witness', 'schema_version': 1,
                'model_revision': domain['preview_model_revision'],
                'controller_parameters': domain['effective_capacitance'], 'native_state': domain['capacitance_state'],
                'model': {'model': domain['preview_model'], 'sha256': domain['preview_model_revision'],
                          'valid': True, 'diagnostics': []}, 'storage_images': domain['capacitance_storage_images']}
            previews[canonical_model_sha256(preview)] = preview
    audits = audit_training_capacitance_registry({**witnesses, **previews}, required)
    repeats = count(summary['configuration']['n0_candidate_repeats'])
    require(1 <= repeats <= 128 and (repeats == 1 or summary['configuration']['normalization'] == 'synapse_count'),
            'invalid_capacitance_history_repeat_policy')
    return {'kind': 'training_capacitance_history_audit', 'schema_version': 1,
            'physical_contexts_verified': True, 'actual_state_verified': actual_id is not None,
            'witnesses_checked': len(audits), 'trials_bound': len(trial_ids),
            'candidates_bound': len(summary['candidates']), 'repeat_groups_bound': len(summary['candidate_repeat_groups']),
            'certificate_verified': False, 'primary_traces_verified': False, 'scientific_verdict': None}


def audit_training_capacitance_history(summary, packets):
    try:
        return _audit(summary, packets)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_training_capacitance_history:'+str(error)) from error


def load_training_capacitance_case(summary_path):
    from .native_evidence import load
    require(summary_path.name.endswith('_tracked_summary.json'), 'unexpected_tracked_summary_filename')
    stem = summary_path.name.removesuffix('_tracked_summary.json')
    summary, packets, traces = load(summary_path), {}, {}
    for path in sorted(summary_path.parent.glob(stem+'_training_proof_*.json')):
        packet = load(path); trial = packet['requested_specification']['trial_id']
        require(trial not in packets, 'duplicate_tracked_primary_trial')
        packets[trial], traces[trial] = packet, path.with_suffix('.csv')
    require(set(packets) == set(summary['capacitance_history']['trial_witness_ids']),
            'incomplete_tracked_primary_trial_inventory')
    return summary, packets, traces


def audit_training_capacitance_case(summary_path):
    from .native_evidence import audit_probe, audit_training_summary
    summary, packets, traces = load_training_capacitance_case(summary_path)
    require(bool(packets), 'missing_tracked_primary_trials')
    for trial, packet in packets.items():
        audit_probe(packet, traces[trial])
    # Reference, candidate and repeated-group residuals are recomputed even
    # when a completed search has no final certificate. Default callers of
    # audit_training_summary still require the certificate.
    measured = audit_training_summary(summary, packets, 'pulse0', require_certificate=False)
    return {'kind': 'training_capacitance_case_audit', 'schema_version': 1,
            'physical_history': measured['capacitance_history'],
            'measurement_consistent': True, 'certificate_verified': measured['certificate_consistent'],
            'exact': measured['exact'], 'primary_traces_verified': True, 'primary_trials': len(packets),
            'scientific_verdict': None}
