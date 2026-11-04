"""Strict wire versions of the native model declaration, before component work."""
from .native_evidence import number, require


FIELDS = {'schema_version', 'branch', 'frequency_hz', 'neuron_class', 'dataset_class',
          'generator_class', 'neuron_structure_mode', 'normalization', 'inputs',
          'initial_isi', 'allocated_cable_lengths', 'maximum_cable_length',
          'preserve_allocated_cable', 'maximum_resistance_ratio', 'configured_minimum_resistance',
          'inhibition', 'scale_inhibition_with_input', 'allow_muted_input_baseline'}


def validate_model_spec(specification):
    require(type(specification) is dict and type(specification.get('schema_version')) is int and
            specification['schema_version'] in (1, 2), 'unknown_native_model_spec_schema')
    version = specification['schema_version']
    require(set(specification) == FIELDS | ({'initial_threshold'} if version == 2 else set()),
            'native_model_spec_field_set_mismatch')
    if version == 2:
        # Signed/zero thresholds have the same explicit finite scalar semantics
        # as native calibration; a boolean is never a numerical factor.
        number(specification['initial_threshold'])
    return version


def audit_initial_threshold(specification, identity):
    """Construction readback only; never constrain a later calibrated graph."""
    version = validate_model_spec(specification)
    if version == 1:
        return
    from .recognition_evidence import _physical
    zones = [n for n in identity['model']['nodes'] if n['path'] == '$.LTZone']
    require(len(zones) == 1 and _physical(zones[0], 'Threshold') == specification['initial_threshold'],
            'native_initial_threshold_readback_mismatch')
