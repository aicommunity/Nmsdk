"""Physical evidence for one measured model revision; never a training verdict."""
from .capacitance_evidence import audit_capacitance_state, controller_capacitance_parameters, _nodes, _physical
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, count, number, require


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


def audit_training_capacitance_registry(witnesses, required_witnesses):
    """Bind evidence IDs to physical revisions without collapsing dormant history.

    Required entries map witness ID to model revision. Two valid parameter
    states can share the same physical revision when only dormant scales differ.
    """
    require(type(witnesses) is dict and bool(witnesses), 'missing_training_capacitance_witness_registry')
    require(type(required_witnesses) is dict and all(type(k) is str and type(v) is str and k and v
            for k, v in required_witnesses.items()), 'invalid_required_capacitance_witnesses')
    audits, origin, policy = {}, None, None
    immutable, inventories = None, {}
    inventory_fields = {'channels', 'channel_classes', 'channel_physics', 'channel_origins'}
    for witness_id, witness in witnesses.items():
        require(type(witness_id) is str and type(witness) is dict and
                canonical_model_sha256(witness) == witness_id, 'training_capacitance_registry_id_mismatch')
        audits[witness_id] = audit_training_capacitance_witness(witness)
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
    require(set(required_witnesses) <= set(audits), 'missing_training_capacitance_revision_witness')
    require(all(witnesses[k]['model_revision'] == revision for k, revision in required_witnesses.items()),
            'training_capacitance_registry_revision_mismatch')
    return audits


def validate_witness_input_parameters(witness, parameters):
    """Read every claimed input bank and its real stimulus links from the graph."""
    declaration = witness['native_state']['baseline']['model_spec']
    return validate_graph_input_parameters(declaration, witness['model'], parameters)


def validate_graph_input_parameters(declaration, identity, parameters):
    """The same graph/bank check, without manufacturing a C0 witness."""
    require(type(parameters) is list and len(parameters) == len(declaration['inputs']),
            'training_capacitance_parameter_dimensions_mismatch')
    nodes = _nodes(identity['model']); expected = set()
    for index, value in enumerate(parameters):
        require(type(value) is dict and set(value) == {'length', 'synapses', 'resistance'},
                'invalid_training_capacitance_input_parameters')
        length, synapses, resistance = count(value['length']), count(value['synapses']), number(value['resistance'])
        require(length >= 1 and 1 <= synapses <= 128 and resistance > 0,
                'invalid_training_capacitance_input_parameters')
        membrane = f"$.Dendrite{1 if declaration['branch'] else index+1}_{length}"
        require(membrane in nodes, 'training_capacitance_missing_input_membrane')
        actual = nodes[membrane]['parameters']['NumExcitatorySynapses']
        require(actual['binding'] is False and actual['data']['type'] == 'signed_integer' and
                actual['data']['value'] == str(synapses), 'training_capacitance_synapse_count_mismatch')
        for member in range(1, synapses+1):
            path = f'{membrane}.ExcSynapse{member}'
            require(path in nodes and _physical(nodes[path], 'Resistance') == resistance,
                    'training_capacitance_resistance_mismatch')
            expected.add(path+':Input')
    import re
    actual = [b['target'] for b in identity['model']['bindings'] if b['kind'] == 'stimulus_port'
              and b['source'] == 'burst' and re.fullmatch(r'\$\.Dendrite[1-9][0-9]*_[1-9][0-9]*\.ExcSynapse[1-9][0-9]*:Input', b['target'])]
    require(len(actual) == len(set(actual)) and set(actual) == expected, 'training_capacitance_stimulus_bank_mismatch')
