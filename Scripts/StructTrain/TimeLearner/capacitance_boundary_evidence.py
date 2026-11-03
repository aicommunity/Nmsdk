"""Audit portable C-history boundaries without inventing search checkpoints."""
from .capacitance_evidence import audit_package_capacitance
from .native_evidence import EvidenceError, number, require
from .training_capacitance_witness import audit_training_capacitance_registry


def _audit(package, summary):
    version = package['schema_version']
    require(type(version) is int and version in (1, 2, 3), 'unknown_capacitance_boundary_package_schema')
    if version != 3:
        require('capacitance_history' not in package and package['configuration']['schema_version'] in (1, 2),
                'unversioned_learned_capacitance_history')
        return None
    audit_package_capacitance(package)
    configuration = package['configuration'];policy = configuration['capacitance_history']
    require(type(configuration['schema_version']) is int and configuration['schema_version'] == 3 and
            type(policy) is dict and set(policy) == {'record', 'maximum_relative_change'} and
            policy['record'] is True and number(policy['maximum_relative_change']) >= 0 and
            policy['maximum_relative_change'] == package['capacitance_state']['maximum_relative_change'],
            'learned_capacitance_history_policy_mismatch')
    history = package['capacitance_history']
    require(type(history) is dict and set(history) == {'schema_version', 'capture_witness_id',
            'current_witness_id', 'current_verified', 'witnesses', 'trial_witness_ids'} and
            type(history['schema_version']) is int and history['schema_version'] == 1 and history['current_verified'] is True,
            'unknown_capacitance_boundary_schema')
    witnesses, trial_ids = history['witnesses'], history['trial_witness_ids']
    require(type(witnesses) is dict and 0 < len(witnesses) <= 4096 and type(trial_ids) is dict and len(trial_ids) <= 100000,
            'invalid_capacitance_boundary_inventory')
    required, trials = {}, set()

    def witness(key, revision=None):
        require(type(key) is str and key in witnesses, 'missing_capacitance_boundary_witness')
        value = witnesses[key]
        require(type(value) is dict and (revision is None or value['model_revision'] == revision),
                'capacitance_boundary_revision_mismatch')
        required[key] = value['model_revision']
        return value

    stopped = package['kind'] == 'timelearner_stopped_state'
    require(stopped or package['kind'] == 'timelearner_completed_state', 'unknown_capacitance_boundary_kind')
    capture_revision = package['capture_revision'] if stopped else package['certificate']['reference_model_revision']
    witness(history['capture_witness_id'], capture_revision)
    current = witness(history['current_witness_id'], package['model_revision'])
    require(current['native_state'] == package['capacitance_state'] and
            current['model'] == package['neuron']['graph']['identity'], 'capacitance_boundary_current_archive_mismatch')

    def packet(record, revision=None):
        trial = record['requested_specification']['trial_id']
        require(type(trial) is str and trial in trial_ids, 'capacitance_boundary_trial_unwitnessed')
        value = witness(trial_ids[trial], revision)
        if record['current_base_revision']:
            require(value['model_revision'] == record['current_base_revision'], 'capacitance_boundary_packet_revision_mismatch')
        else:
            require(record['native_status'] != 'completed' and record['prepared'] is None and record['observation'] is None,
                    'capacitance_boundary_armed_revision_unknown')
        trials.add(trial)

    for record in package['reference_packets']:
        packet(record, capture_revision)
    for record in package['final_packets']:
        packet(record, package['model_revision'])
    if stopped:
        for record in package['observed_packets']:
            packet(record)
    require(set(trial_ids) == trials and set(witnesses) == set(required), 'capacitance_boundary_contains_missing_or_extra_contexts')
    audits = audit_training_capacitance_registry(witnesses, required)
    baseline = current['native_state']['baseline']
    for value in witnesses.values():
        for field in ('channels', 'channel_classes', 'channel_physics', 'channel_origins'):
            require(all(baseline[field].get(k) == v for k, v in value['native_state']['baseline'][field].items()),
                    'capacitance_boundary_current_baseline_history_lost')
    if summary is not None:
        require(type(summary['schema_version']) is int and summary['schema_version'] == 3, 'capacitance_boundary_summary_schema_mismatch')
        source = summary['capacitance_history']
        require(source['capture_witness_id'] == history['capture_witness_id'] and
                source['current_witness_id'] == history['current_witness_id'] and source['current_verified'] is True and
                summary['actual_capacitance_witness_id'] == history['current_witness_id'] and
                all(source['witnesses'].get(k) == v for k, v in witnesses.items()) and
                all(source['trial_witness_ids'].get(k) == v for k, v in trial_ids.items()),
                'capacitance_boundary_summary_context_mismatch')
    return {'schema_version': 1, 'consistent': True, 'physical_witnesses': len(audits),
            'bound_trials': len(trials), 'search_checkpoint': False, 'dynamic_checkpoint': False,
            'native_import_verified': False, 'scientific_verdict': None}


def audit_package_capacitance_history(package, summary=None):
    try:
        return _audit(package, summary)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_capacitance_boundary:'+str(error)) from error
