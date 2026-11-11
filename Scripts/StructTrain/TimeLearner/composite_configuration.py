"""Explicit cold6/protocol4 declarations, without manufacturing measurements.

Projection is a private validation view. Callers retain the exact original
configuration for execution, identity, manifests and native readback. Native
storage/graph/scheduler validation and typed live admission remain mandatory.
"""
from copy import deepcopy

from .native_evidence import count, number, require

METHOD = 'declared-window-basin-necessity-v1'
COMPOSITE_FIELDS = {
    'schema_version', 'method_id', 'context_policy', 'geometry_policy',
    'attempt_limits', 'maximum_group_model_seconds', 'maximum_group_wall_seconds',
    'maximum_total_primary_bytes',
}
CONTEXT_FIELDS = {
    'schema_version', 'comparison_radius_ticks', 'maximum_samples',
    'maximum_total_samples', 'maximum_native_probes', 'time_comparison_tolerance',
    'baseline_absolute', 'repeatability_absolute', 'repeatability_relative',
    'influence_absolute', 'influence_relative',
}
GEOMETRY_FIELDS = {
    'schema_version', 'maximum_inputs', 'maximum_samples', 'maximum_total_samples',
    'repeatability_absolute',
}
ATTEMPT_FIELDS = {'maximum_groups', 'maximum_native_probes', 'maximum_total_samples'}
DIAGNOSTIC_ONLY_CONTEXT_FIELDS = {
    'comparison_radius_ticks', 'influence_absolute', 'influence_relative',
}
BASE_FIELDS = {
    'kind', 'schema_version', 'model', 'stimulus_profile', 'run_id', 'protocol_revision',
    'sample_id', 'duration', 'maximum_sample_gap', 'minimum_amplitude', 'maximum_samples',
    'record_spikes', 'peak_selection', 'windows', 'search', 'maximum_reference_probes',
    'maximum_invalid_reference_probes', 'maximum_model_seconds', 'maximum_wall_seconds',
}


def _keys(value, fields, reason):
    require(type(value) is dict and set(value) == fields, reason)


def _count(value):
    value = count(value)
    require(value > 0, 'invalid_composite_positive_integer')
    return value


def _version(value):
    require(count(value) == 1, 'unknown_composite_contract_schema')


def validate_composite_measurement(declaration, *, inputs, frequency, maximum_samples):
    """Check only the declared operational policy; never attest a live group."""
    _keys(declaration, COMPOSITE_FIELDS, 'unknown_composite_measurement_fields')
    _version(declaration['schema_version'])
    require(declaration['method_id'] == METHOD, 'unknown_composite_measurement_method')
    context, geometry, limits = (declaration[k] for k in ('context_policy', 'geometry_policy', 'attempt_limits'))
    _keys(context, CONTEXT_FIELDS, 'unknown_composite_context_policy_fields')
    _keys(geometry, GEOMETRY_FIELDS, 'unknown_composite_geometry_policy_fields')
    _keys(limits, ATTEMPT_FIELDS, 'unknown_composite_attempt_limits')
    _version(context['schema_version']); _version(geometry['schema_version'])
    for key in ('comparison_radius_ticks', 'maximum_samples', 'maximum_total_samples', 'maximum_native_probes'):
        _count(context[key])
    for key in ('maximum_inputs', 'maximum_samples', 'maximum_total_samples'):
        _count(geometry[key])
    for key in ATTEMPT_FIELDS:
        _count(limits[key])
    _count(declaration['maximum_total_primary_bytes'])
    for policy, fields in ((context, ('time_comparison_tolerance', 'baseline_absolute',
            'repeatability_absolute', 'repeatability_relative', 'influence_absolute', 'influence_relative')),
            (geometry, ('repeatability_absolute',))):
        require(all(number(policy[k]) >= 0 for k in fields), 'negative_composite_policy_tolerance')
    require(all(number(declaration[k]) > 0 for k in ('maximum_group_model_seconds', 'maximum_group_wall_seconds')),
            'invalid_composite_group_time_budget')
    require(2 <= inputs <= geometry['maximum_inputs'] and
            context['maximum_native_probes'] >= inputs+2 and
            3 <= maximum_samples <= context['maximum_samples'] and
            0 < context['comparison_radius_ticks'] < context['maximum_samples'] and
            context['maximum_total_samples'] >= context['maximum_samples'] and
            geometry['maximum_samples'] >= 3 and geometry['maximum_total_samples'] >= geometry['maximum_samples'],
            'composite_dimension_or_sample_budget_mismatch')
    require(number(frequency) > 0 and context['time_comparison_tolerance'] < .5/frequency,
            'composite_timestamp_tolerance_exceeds_native_grid')


def project_composite_configuration(configuration):
    """Return an unchanged-meaning base view; never send the projection native."""
    require(type(configuration) is dict and configuration.get('kind') == 'timelearner_native_cold_configuration',
            'unknown_composite_configuration_schema')
    require(count(configuration.get('schema_version')) == 6, 'unknown_composite_configuration_schema')
    base = count(configuration.get('base_schema_version'))
    require(base in (1, 2, 3, 4) and
            'invalid_measurement_recovery' not in configuration, 'unsupported_composite_base_or_recovery_envelope')
    _keys(configuration, BASE_FIELDS | {'base_schema_version', 'composite_measurement'} |
          ({'capacitance_history'} if base in (3, 4) else set()) |
          ({'capacitance_search'} if base == 4 else set()), 'unknown_composite_configuration_fields')
    from .native_model_spec import validate_model_spec
    model = configuration['model']; validate_model_spec(model)
    inputs = model['inputs']; windows = configuration['windows']
    require(type(inputs) is list and len(inputs) >= 2 and type(windows) is list and len(windows) == len(inputs),
            'composite_requires_multiinput_declared_windows')
    frequency, duration = number(model['frequency_hz']), number(configuration['duration'])
    require(frequency > 0 and duration > 0 and number(configuration['maximum_sample_gap']) == 1/frequency and
            configuration['record_spikes'] is False and configuration['peak_selection'] == 'isolated_window',
            'unsupported_composite_recorder_or_grid')
    profile = configuration['stimulus_profile']
    _keys(profile, {'generator_class', 'amplitude', 'pulse_length', 'frequency_hz',
                    'frequency_deviation', 'use_transit_signal', 'use_pattern_output'},
          'unknown_composite_stimulus_profile_fields')
    require(profile['generator_class'] == model['generator_class'] == 'NPulseGeneratorTransit'
            and number(profile['frequency_hz']) == frequency and number(profile['amplitude']) > 0
            and number(profile['pulse_length']) >= 1/frequency and number(profile['frequency_deviation']) == 0
            and profile['use_transit_signal'] is False and profile['use_pattern_output'] is False,
            'unsupported_composite_stock_stimulus_profile')
    for window in windows:
        _keys(window, {'begin', 'end'}, 'unknown_composite_window_fields')
        require(0 <= number(window['begin']) < number(window['end']) <= duration,
                'invalid_composite_declared_window')
    require(number(configuration['maximum_model_seconds']) > 0 and number(configuration['maximum_wall_seconds']) > 0,
            'invalid_composite_attempt_time_budget')
    validate_composite_measurement(configuration['composite_measurement'], inputs=len(inputs), frequency=frequency,
                                   maximum_samples=_count(configuration['maximum_samples']))
    projected = deepcopy(configuration)
    projected.pop('base_schema_version'); projected.pop('composite_measurement'); projected['schema_version'] = base
    return projected


def project_training_configuration(configuration):
    """Select the explicit envelope without changing legacy1–5 validation."""
    if type(configuration) is dict and configuration.get('schema_version') == 7:
        from .candidate_window_contract import configuration_view
        return project_composite_configuration(configuration_view(configuration))
    if type(configuration) is dict and configuration.get('schema_version') == 6:
        return project_composite_configuration(configuration)
    from .candidate_recovery import project_recovery_configuration
    return project_recovery_configuration(configuration)[0]


def composite_declaration_scope(configuration):
    """Expose policy roles; a serialized legacy diagnostic is not a Train factor."""
    project_composite_configuration(configuration)
    return {
        'method_id': METHOD,
        'context_policy_field_roles': {
            key: ('diagnostic_only' if key in DIAGNOSTIC_ONLY_CONTEXT_FIELDS else
                  'schema_identity' if key == 'schema_version' else 'context_integrity_or_budget')
            for key in sorted(CONTEXT_FIELDS)
        },
        'geometry_policy_role': 'declared_window_training_measurement',
        'native_effective_preflight_required': True,
        'live_measurement_admission_verified': False,
        'training_certificate_verified': False,
    }


def validate_composite_protocol(protocol, configuration):
    """Bind protocol4 to the original cold6 declaration, without a certificate."""
    project_composite_configuration(configuration)
    from .model_identity import canonical_model_sha256
    fields = {'schema_version', 'routing', 'revision', 'sample_id', 'pattern_hash',
              'origin_stimulus_id', 'inputs', 'stimulus_ids', 'maximum_sample_gap',
              'minimum_amplitude', 'stimulus_profile', 'wave_assignment',
              'peak_selection', 'composite_measurement'}
    _keys(protocol, fields, 'unknown_composite_protocol_fields')
    require(count(protocol['schema_version']) == 4, 'unknown_composite_protocol_schema')
    model = configuration['model']; n = len(model['inputs'])
    require(type(model['branch']) is bool, 'invalid_composite_routing_declaration')
    inputs = protocol['inputs']; stimulus_ids = ['pulse'+str(i) for i in range(n)]
    require(type(inputs) is list and len(inputs) == n, 'composite_protocol_input_dimension')
    names = []
    for index, item in enumerate(inputs):
        _keys(item, {'id', 'stimulus_id'}, 'unknown_composite_protocol_input_fields')
        require(type(item['id']) is str and bool(item['id']) and item['stimulus_id'] == stimulus_ids[index],
                'composite_protocol_input_mapping')
        names.append(item['id'])
    require(len(set(names)) == n and protocol['origin_stimulus_id'] in stimulus_ids,
            'composite_protocol_input_or_origin_identity')
    declared = configuration['composite_measurement']
    contract = {key: deepcopy(declared[key]) for key in
                ('schema_version', 'method_id', 'context_policy', 'geometry_policy')}
    contract['input_windows'] = [{'begin_offset': w['begin'], 'end_offset': w['end']}
                                 for w in configuration['windows']]
    expected = {
        'schema_version': 4, 'routing': 'branch_solo_burst' if model['branch'] else 'classic_burst',
        'revision': configuration['protocol_revision'], 'sample_id': configuration['sample_id'],
        'pattern_hash': canonical_model_sha256(model['initial_isi']), 'origin_stimulus_id': protocol['origin_stimulus_id'],
        'inputs': inputs, 'stimulus_ids': stimulus_ids,
        'maximum_sample_gap': configuration['maximum_sample_gap'],
        'minimum_amplitude': configuration['minimum_amplitude'],
        'stimulus_profile': configuration['stimulus_profile'], 'wave_assignment': 'window_only',
        'peak_selection': 'isolated_window', 'composite_measurement': contract,
    }
    # Equality alone would equate JSON booleans and numbers in nested policy.
    _keys(protocol['composite_measurement'], set(contract), 'unknown_composite_protocol_contract_fields')
    wire = protocol['composite_measurement']
    _version(wire['schema_version'])
    policy = {**wire, **{key: declared[key] for key in COMPOSITE_FIELDS-set(wire)}}
    policy.pop('input_windows')
    validate_composite_measurement(policy, inputs=n, frequency=model['frequency_hz'],
                                   maximum_samples=count(configuration['maximum_samples']))
    require(type(wire['input_windows']) is list and len(wire['input_windows']) == n,
            'composite_protocol_window_dimension_mismatch')
    for window in wire['input_windows']:
        _keys(window, {'begin_offset', 'end_offset'}, 'unknown_composite_protocol_window_fields')
        number(window['begin_offset']); number(window['end_offset'])
    require(canonical_model_sha256(protocol) == canonical_model_sha256(expected),
            'composite_protocol_configuration_mismatch')
