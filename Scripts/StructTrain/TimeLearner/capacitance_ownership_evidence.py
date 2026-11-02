"""Audit native C0 owner snapshots and the continuity of original parameters."""
from pathlib import Path

from .capacitance_evidence import audit_capacitance_state, _nodes, _physical
from .native_evidence import EvidenceError, load, number, require
from .native_gate import audit_junit, supported_specification

PHASES = ('first_bound_edit', 'second_membrane_edit', 'native_reset',
          'ordinary_growth_without_correction_argument', 'ordinary_shrink',
          'ordinary_regrowth_without_correction_argument')


def _all_scales(state):
    active, dormant = state['membrane_scales'], state.get('dormant_membrane_scales', {})
    require(not set(active).intersection(dormant), 'overlapping_owner_capacitance_scales')
    return dict(active, **dormant)


def audit_ownership(specification, artifacts):
    """Consistency of declared native tests; never infer scientific convergence."""
    try:
        spec = load(Path(specification)); root = Path(artifacts)
        require(supported_specification(spec), 'unknown_capacitance_owner_contract')
        expected = spec['expected_test_ids']
        require(type(expected) is list and len(expected) == len(set(expected)) == 8
                and all(type(x) is str and x.startswith('NativeCapacitanceOwnership/') for x in expected),
                'invalid_capacitance_owner_inventory')
        gate, result = load(root/'specification.json'), load(root/'result.json')
        require(supported_specification(gate) and set(expected) <= set(gate['expected_test_ids']),
                'missing_capacitance_owner_test')
        inventory = audit_junit(root/'native.xml', gate['expected_test_ids'])
        require(result['kind'] == 'timelearner_native_test_gate_result'
                and type(result['schema_version']) is int and result['schema_version'] == 1
                and type(load(root/'runtime.json')) is dict
                and result['execution'] == 'completed' and result['validity'] == 'valid'
                and result['assertion_status'] == inventory['assertion_status'] == 'passed'
                and result['inventory'] == inventory and result['scientific_verdict'] is None,
                'capacitance_owner_native_gate_not_passed')
        records = {name: {} for name in expected}; graph_roundtrips = 0
        for path in sorted((root/'native').glob('*_ownership_*.json')):
            require(path.is_file() and not path.is_symlink(), 'invalid_capacitance_owner_primary')
            record = load(path)
            require(type(record) is dict and set(record) == {'kind', 'schema_version', 'test_id', 'phase',
                    'state', 'declaration', 'effective_model', 'class_definitions', 'input_parameters'}
                    and record['kind'] == 'native_capacitance_owner_snapshot'
                    and type(record['schema_version']) is int and record['schema_version'] == 2,
                    'unknown_capacitance_owner_snapshot')
            name, phase = record['test_id'], record['phase']
            require(name in records and phase in PHASES and phase not in records[name],
                    'duplicate_or_unknown_capacitance_owner_phase')
            audit_capacitance_state(record['state'], record['declaration'],
                                    record['effective_model'], record['class_definitions'])
            inputs = record['input_parameters']
            require(type(inputs) is list and inputs and len(inputs) == len(record['declaration']['inputs'])
                    and all(type(p) is dict and set(p) == {'length', 'synapses', 'resistance'}
                            and type(p['length']) is int and p['length'] > 0
                            and type(p['synapses']) is int and p['synapses'] > 0
                            and number(p['resistance']) > 0 for p in inputs), 'invalid_owned_input_parameters')
            branch = record['declaration']['branch']
            require(type(branch) is bool, 'invalid_capacitance_owner_topology')
            nodes = _nodes(record['effective_model']['model'])
            for index, value in enumerate(inputs):
                membrane = f"$.Dendrite{1 if branch else index+1}_{value['length']}"
                count = nodes[membrane]['parameters']['NumExcitatorySynapses']
                require(count['binding'] is False and count['data']['type'] == 'signed_integer'
                        and count['data']['value'] == str(value['synapses']), 'owned_synapse_count_readback_mismatch')
                for synapse in range(1, value['synapses']+1):
                    require(_physical(nodes[f'{membrane}.ExcSynapse{synapse}'], 'Resistance') == value['resistance'],
                            'owned_resistance_readback_mismatch')
            records[name][phase] = record
        for name, phases in records.items():
            require(set(phases) == set(PHASES), 'incomplete_capacitance_owner_phases:'+name)
            states = [phases[p]['state'] for p in PHASES]; original = states[0]['baseline']
            for state in states:
                baseline = state['baseline']
                require(all(baseline[k] == original[k] for k in ('model_revision', 'model_spec', 'capture_model',
                        'storage_images', 'storage_images_sha256'))
                        and all(baseline['channels'].get(k) == v for k, v in original['channels'].items()),
                        'capacitance_owner_original_c0_changed')
            require(states[1] == states[2], 'capacitance_owner_reset_changed_parameter_state')
            require(_all_scales(states[3]) == _all_scales(states[4]) == _all_scales(states[5])
                    and states[4]['schema_version'] == 2 and states[4]['dormant_membrane_scales']
                    and not states[5].get('dormant_membrane_scales', {})
                    and phases[PHASES[3]]['input_parameters'] == phases[PHASES[5]]['input_parameters'],
                    'capacitance_owner_shrink_regrowth_lost_parameters')
            graph_roundtrips += states[3]['applied_model_revision'] == states[5]['applied_model_revision']
        return {'kind': 'native_capacitance_owner_audit', 'schema_version': 1, 'cases': len(records),
                'snapshots': sum(len(x) for x in records.values()), 'consistent': True,
                'parameter_roundtrip_cases': len(records), 'whole_graph_roundtrip_cases': graph_roundtrips,
                'native_import_verified': False, 'scientific_verdict': None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_capacitance_owner_evidence:'+str(error)) from error
