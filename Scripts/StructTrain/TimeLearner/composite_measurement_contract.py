"""Portable composite record names and hash encodings; no live authority.

Computing an expected digest is not validation of a measurement or a native
execution. Readers must separately replay primary/context/geometry and source.
"""
from .composite_configuration import METHOD
from .model_identity import canonical_model_sha256
from .native_evidence import number, require

ARCHIVE_FIELDS = set(('kind schema_version method_id protocol source_origin owner_family_binding '
    'source_binding maximum_total_primary_bytes records reference_group_ids final_group_ids counters '
    'primary_blobs artifact_document_sha256 current_attempt_id').split())
RECORD_FIELDS = set(('kind schema_version logical_request purpose group_id source_origin owner_family_binding '
    'live_attempt_binding method_specification geometry_policy candidate_binding candidate_witness_id '
    'group_state complete_group native_group raw_trials native_packets selection measurement consumed '
    'training_requested_at_consume rejection_reason budgets counters clock_observation '
    'capacitance_witnesses native_trial_witness_ids attempt_id').split())
LOGICAL_FIELDS = set(('run_id trial_id input_id sample_id pattern_hash protocol_revision base_model_revision '
    'routing model_epoch input_index').split())
RAW_FIELDS = {'native_trial_id', 'prepared_context', 'actual_specification', 'primary_ref', 'actual_stimuli'}
MEASUREMENT_FIELDS = {'raw_potential', 'arrival', 'plateau_end', 'actual_peak', 'actual_origin_time', 'semantic_proof_id'}
SELECTION_FIELDS = {'status', 'status_enum', 'reasons', 'actual_assigned_onset', 'geometry'}
BUDGET_FIELDS = {'attempt_limits', 'maximum_group_model_seconds', 'maximum_group_wall_seconds', 'maximum_total_primary_bytes'}
ATTEMPT_LIMIT_FIELDS = {'maximum_groups', 'maximum_native_probes', 'maximum_total_samples', 'maximum_model_seconds', 'maximum_wall_seconds'}
COUNTER_FIELDS = {'native_probes', 'sampled_frames', 'retained_frames', 'primary_bytes'}
CLOCK_FIELDS = {'start_model_time', 'start_wall_time', 'end_model_time', 'end_wall_time', 'wall_enforcement'}
SOURCE_FIELDS = set(('kind schema_version initial_model initial_native_snapshot initial_dataset initial_epoch '
    'model_spec storage_images storage_images_sha256 applied_source_isi pattern_hash actual_source_profile '
    'optional_C0_origin optional_C0_witness').split())
CANDIDATE_FIELDS = {'kind', 'source_origin', 'model_identity', 'storage_images_sha256', 'optional_C0_witness'}
PURPOSE = {'reference': 0, 'search': 1, 'final': 2}
STATUS = {'rejected': 0, 'completed': 1, 'causality_rejected': 2}


def integral_number_view(value):
    """Private bridge to existing integer-index readers for the new JSON codec.

    Qt treats 1 and 1.0 as the same number. Booleans remain distinct. Raw CSV,
    serialized documents and public legacy reader behavior are not changed.
    """
    def visit(item):
        if type(item) is float:
            actual = number(item)
            return int(actual) if actual.is_integer() and abs(actual) <= 2**53-1 else actual
        if type(item) is dict: return {key: visit(child) for key, child in item.items()}
        if type(item) is list: return [visit(child) for child in item]
        return item
    result = visit(value)
    require(canonical_model_sha256(result) == canonical_model_sha256(value), 'composite_numeric_view_changed_semantics')
    return result


def protocol_semantic_binding(protocol):
    """Exact C++ ProtocolBinding encoding, separate from a condition projection."""
    c = protocol['composite_measurement']; context = c['context_policy']; geometry = c['geometry_policy']
    source = protocol['stimulus_profile']
    require(c['method_id'] == METHOD and protocol['routing'] in ('classic_burst', 'branch_solo_burst'),
            'unknown_composite_semantic_protocol')
    return {
        'schema_version': 4, 'method': c['method_id'], 'contract_schema': c['schema_version'],
        'routing': 0 if protocol['routing'] == 'classic_burst' else 1,
        'revision': protocol['revision'], 'sample': protocol['sample_id'], 'pattern': protocol['pattern_hash'],
        'origin': protocol['origin_stimulus_id'],
        'inputs': [[item['id'], item['stimulus_id']] for item in protocol['inputs']],
        'stimuli': protocol['stimulus_ids'], 'sample_gap': protocol['maximum_sample_gap'],
        'minimum_amplitude': protocol['minimum_amplitude'],
        'windows': [[w['begin_offset'], w['end_offset']] for w in c['input_windows']],
        'source': [source[k] for k in ('generator_class', 'amplitude', 'pulse_length', 'frequency_hz',
                                      'frequency_deviation', 'use_transit_signal', 'use_pattern_output')],
        'context_policy': [context[k] for k in ('schema_version', 'comparison_radius_ticks', 'maximum_samples',
            'maximum_total_samples', 'maximum_native_probes', 'time_comparison_tolerance', 'baseline_absolute',
            'repeatability_absolute', 'repeatability_relative', 'influence_absolute', 'influence_relative')],
        'geometry_policy': [geometry[k] for k in ('schema_version', 'maximum_inputs', 'maximum_samples',
                                                 'maximum_total_samples', 'repeatability_absolute')],
    }


def expected_semantic_measurement_id(record, protocol):
    """Digest the specified proof payload after independent measurement audit.

    Paths/document digests are excluded. Anti-replay run/trial/group/attempt
    identities remain; changing them is a different measurement, not relocation.
    """
    purpose = record['purpose']; require(purpose in PURPOSE, 'unknown_composite_measurement_purpose')
    require(type(record['native_group']) is dict and type(record['measurement']) is dict,
            'composite_semantic_id_requires_complete_measurement')
    budgets = record['budgets']; attempt = budgets['attempt_limits']; peak = record['measurement']['actual_peak']
    primary = [{'native': trace['native_evidence'], 'csv_sha256': trace['sha256']}
               for trace in record['native_group']['traces']]
    payload = {
        'kind': 'live-composite-training-measurement-v1', 'method_binding': protocol_semantic_binding(protocol),
        'source_origin': record['source_origin'], 'candidate_witness': record['candidate_witness_id'],
        'live_attempt_binding': record['live_attempt_binding'],
        'attempt_limits': [attempt[k] for k in ('maximum_groups', 'maximum_native_probes', 'maximum_total_samples',
                                              'maximum_model_seconds', 'maximum_wall_seconds')],
        'group_limits': [budgets['maximum_group_model_seconds'], budgets['maximum_group_wall_seconds']],
        'logical_trial': record['logical_request']['trial_id'], 'group_id': record['group_id'], 'purpose': PURPOSE[purpose],
        'primary': primary, 'raw': peak['raw_potential'], 'time': peak['time'], 'plateau_end': peak['plateau_end'],
    }
    return canonical_model_sha256(payload)


def expected_artifact_document_id(document):
    """Whole JSON document consistency, including relative paths and blobs."""
    return canonical_model_sha256({key: value for key, value in document.items() if key != 'artifact_document_sha256'})
