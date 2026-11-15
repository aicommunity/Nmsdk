"""Verify explicit C0 binding on a declared model, never infer cold history."""
from .capacitance_evidence import audit_capacitance_state, controller_capacitance_parameters
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, number, require


def _audit(record):
    require(type(record) is dict and set(record) == {
        'kind', 'schema_version', 'branch', 'normalization', 'phases', 'scientific_verdict'}
        and record['kind'] == 'native_training_capacitance_binding'
        and type(record['schema_version']) is int and record['schema_version'] == 1,
        'unknown_capacitance_binding_schema')
    require(type(record['branch']) is bool and type(record['normalization']) is int
            and record['normalization'] in (0, 1) and record['scientific_verdict'] is None,
            'invalid_capacitance_binding_metadata')
    frames = record['phases']
    require(type(frames) is list and len(frames) == 3 and all(type(f) is dict for f in frames)
            and [f.get('phase') for f in frames] == ['unbound', 'bound', 'trimmed'],
            'incomplete_capacitance_binding_phases')
    for frame in frames:
        require(set(frame) == {'phase', 'model', 'native_state', 'controller_parameters', 'storage_images'},
                'unknown_capacitance_binding_frame')
        identity = frame['model']
        require(identity['valid'] is True and not identity['diagnostics']
                and canonical_model_sha256(identity['model']) == identity['sha256'],
                'invalid_capacitance_binding_model')
        if frame['phase'] == 'unbound':
            require(frame['native_state'] == {} and frame['controller_parameters'] is None,
                    'fabricated_unbound_capacitance_binding')
            continue
        state = frame['native_state']
        audit_capacitance_state(state, state['baseline']['model_spec'], identity, frame['storage_images'])
        typed = frame['controller_parameters']
        require(type(typed) is dict and typed == controller_capacitance_parameters(state),
                'capacitance_binding_controller_mismatch')
        number(typed['maximum_relative_change'])
        for scale in typed['membrane_scales'].values(): number(scale)
    initial, bound, trimmed = frames
    require(initial['model'] == bound['model'], 'capacitance_binding_changed_model')
    baseline = bound['native_state']['baseline']
    require(baseline['capture_model'] == initial['model']['model']
            and baseline['model_revision'] == initial['model']['sha256'], 'capacitance_binding_initial_capture_mismatch')
    require(all(v == 1. for v in bound['controller_parameters']['membrane_scales'].values()),
            'capacitance_binding_initial_scale_not_unit')
    require(trimmed['native_state']['baseline'] == baseline
            and trimmed['controller_parameters']['origin'] == bound['controller_parameters']['origin']
            and trimmed['controller_parameters']['maximum_relative_change'] == bound['controller_parameters']['maximum_relative_change'],
            'capacitance_binding_recaptured_or_policy_changed')
    require(trimmed['model']['sha256'] != bound['model']['sha256']
            and any(v != 1. for v in trimmed['controller_parameters']['membrane_scales'].values()),
            'capacitance_binding_trim_not_witnessed')
    return {'kind': 'native_capacitance_binding_audit', 'schema_version': 1, 'consistent': True,
            'branch': record['branch'], 'normalization': record['normalization'],
            'cold_training_history_verified': False, 'native_lifecycle_verified': False,
            'probe_observations_verified': False, 'scientific_verdict': None}


def audit_capacitance_binding(record):
    try:
        return _audit(record)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_capacitance_binding:'+str(error)) from error
