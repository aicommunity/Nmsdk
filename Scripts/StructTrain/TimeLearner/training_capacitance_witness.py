"""Physical evidence for one measured model revision; never a training verdict."""
from .capacitance_evidence import audit_capacitance_state, controller_capacitance_parameters
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, number, require


def _audit(record):
    require(type(record) is dict and set(record) == {
        'kind', 'schema_version', 'model_revision', 'controller_parameters',
        'model', 'native_state', 'storage_images'} and
        record['kind'] == 'native_training_capacitance_witness' and
        type(record['schema_version']) is int and record['schema_version'] == 1,
        'unknown_training_capacitance_witness_schema')
    identity, state = record['model'], record['native_state']
    require(type(identity) is dict and identity['valid'] is True and not identity['diagnostics']
            and identity['sha256'] == canonical_model_sha256(identity['model'])
            and identity['sha256'] == record['model_revision'],
            'training_capacitance_witness_revision_mismatch')
    require(type(state) is dict and state and state['applied_model_revision'] == record['model_revision'],
            'training_capacitance_witness_state_revision_mismatch')
    physical = audit_capacitance_state(state, state['baseline']['model_spec'], identity, record['storage_images'])
    typed = record['controller_parameters']
    require(type(typed) is dict and set(typed) == {'origin', 'maximum_relative_change', 'membrane_scales'}
            and type(typed['origin']) is str and type(typed['membrane_scales']) is dict,
            'invalid_training_capacitance_witness_parameters')
    number(typed['maximum_relative_change'])
    for path, scale in typed['membrane_scales'].items():
        require(type(path) is str, 'invalid_training_capacitance_witness_path')
        number(scale)
    require(typed == controller_capacitance_parameters(state),
            'training_capacitance_witness_parameter_mismatch')
    return {'kind': 'training_capacitance_witness_audit', 'schema_version': 1,
            'model_revision': record['model_revision'], 'physical_state_verified': True,
            'effective_channels': physical['effective_channels'],
            'probe_observations_verified': False, 'scientific_verdict': None}


def audit_training_capacitance_witness(record):
    try:
        return _audit(record)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_training_capacitance_witness:'+str(error)) from error


def audit_training_capacitance_registry(witnesses, required_revisions):
    """Require physical proof for every referenced revision before history audit."""
    require(type(witnesses) is dict and bool(witnesses), 'missing_training_capacitance_witness_registry')
    require(type(required_revisions) in (list, set, tuple) and
            all(type(r) is str and r for r in required_revisions), 'invalid_required_capacitance_revisions')
    audits, origin, policy = {}, None, None
    immutable, inventories = None, {}
    inventory_fields = {'channels', 'channel_classes', 'channel_physics', 'channel_origins'}
    for revision, witness in witnesses.items():
        require(type(revision) is str and type(witness) is dict and witness.get('model_revision') == revision,
                'training_capacitance_registry_revision_mismatch')
        audits[revision] = audit_training_capacitance_witness(witness)
        typed, baseline = witness['controller_parameters'], witness['native_state']['baseline']
        stable = {k: v for k, v in baseline.items() if k not in inventory_fields | {'sha256'}}
        if origin is not None:
            require(typed['origin'] == origin and typed['maximum_relative_change'] == policy,
                    'training_capacitance_registry_origin_or_policy_changed')
            require(stable == immutable, 'training_capacitance_registry_baseline_recaptured')
        origin, policy, immutable = typed['origin'], typed['maximum_relative_change'], stable
        for field in inventory_fields:
            union = inventories.setdefault(field, {})
            for path, value in baseline[field].items():
                require(path not in union or union[path] == value,
                        'training_capacitance_registry_channel_baseline_changed')
                union[path] = value
    require(set(required_revisions) <= set(audits), 'missing_training_capacitance_revision_witness')
    return audits
