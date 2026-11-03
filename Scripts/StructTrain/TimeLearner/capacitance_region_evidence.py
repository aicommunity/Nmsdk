"""Audit topology-selected C requests, effective physics and native burst CSV."""
from pathlib import Path

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, audit_probe, count, load, number, require
from .training_capacitance_witness import audit_training_capacitance_registry, validate_witness_input_parameters


def _audit(record, root):
    require(type(record) is dict and set(record) == {'kind', 'schema_version', 'frequency_hz', 'normalization',
            'branch', 'input_index', 'scale', 'region', 'input_parameters', 'before', 'after', 'probes', 'scientific_verdict'} and
            record['kind'] == 'native_capacitance_region' and type(record['schema_version']) is int and
            record['schema_version'] == 1 and record['scientific_verdict'] is None, 'unknown_capacitance_region_schema')
    before, after = record['before'], record['after']
    witnesses = {canonical_model_sha256(w): w for w in (before, after)}
    audit_training_capacitance_registry(witnesses, {key: w['model_revision'] for key, w in witnesses.items()})
    parameters = record['input_parameters']
    for witness in (before, after):
        validate_witness_input_parameters(witness, parameters)
    declaration = before['native_state']['baseline']['model_spec']
    require(type(record['branch']) is bool and record['branch'] == declaration['branch'] and
            count(record['frequency_hz']) == declaration['frequency_hz'] and
            count(record['normalization']) == {'N0': 0, 'N1': 1}[declaration['normalization']],
            'capacitance_region_profile_mismatch')
    index = count(record['input_index'])
    require(index+1 < len(parameters), 'capacitance_region_anchor_or_unknown_input')
    lengths = [count(p['length']) for p in parameters]
    require(all(length >= 1 for length in lengths) and (not record['branch'] or
            all(a >= b for a, b in zip(lengths, lengths[1:]))), 'capacitance_region_geometry_invalid')
    dendrite = 1 if record['branch'] else index+1
    first, last = (lengths[index+1]+1 if record['branch'] else 1), lengths[index]
    require(type(record['region']) is dict and set(record['region']) == {'dendrite', 'first', 'last'} and
            {k: count(v) for k, v in record['region'].items()} == {'dendrite': dendrite, 'first': first, 'last': last},
            'capacitance_region_scope_mismatch')
    scale = number(record['scale'])
    initial, actual = before['controller_parameters'], after['controller_parameters']
    require(scale > 0 and 1.-initial['maximum_relative_change'] <= scale <= 1.+initial['maximum_relative_change'],
            'capacitance_region_scale_outside_owned_policy')
    expected = dict(initial['membrane_scales'])
    require(last-first+1 <= len(initial['membrane_scales'])+len(before['native_state']['baseline']['channels']),
            'capacitance_region_scope_exceeds_native_inventory')
    for segment in range(first, last+1):
        expected[f'Dendrite{dendrite}_{segment}'] = scale
    require(actual == dict(initial, membrane_scales=expected), 'capacitance_region_changed_unselected_parameters')
    require(before['native_state']['baseline'] == after['native_state']['baseline'] and
            before['storage_images'] == after['storage_images'], 'capacitance_region_recaptured_or_changed_storage')
    probes = record['probes']
    require(type(probes) is list and len(probes) == 2*len(parameters), 'capacitance_region_incomplete_probe_set')
    seen, trials, files, protocols = set(), set(), set(), {}
    for item in probes:
        require(type(item) is dict and set(item) == {'phase', 'input_index', 'packet', 'record_file', 'trace_file'},
                'unknown_capacitance_region_probe_schema')
        phase, input_index = item['phase'], count(item['input_index'])
        require(phase in ('before', 'after') and input_index < len(parameters) and
                (phase, input_index) not in seen, 'capacitance_region_duplicate_or_unknown_probe')
        seen.add((phase, input_index))
        paths = []
        for field in ('record_file', 'trace_file'):
            name = item[field]
            require(type(name) is str and Path(name).name == name and '\\' not in name and name not in files,
                    'capacitance_region_unsafe_or_duplicate_primary_path')
            files.add(name);path = root/name
            require(path.is_file() and not path.is_symlink(), 'capacitance_region_missing_primary')
            paths.append(path)
        packet = load(paths[0]);require(packet == item['packet'], 'capacitance_region_changed_primary_packet')
        result = audit_probe(packet, paths[1])
        require(result['valid_observation'] and result['trace_checked'], 'capacitance_region_invalid_observation')
        witness = before if phase == 'before' else after
        require(packet['current_base_revision'] == witness['model_revision'] and
                packet['prepared']['input_id'] == 'input'+str(input_index), 'capacitance_region_probe_context_mismatch')
        trial = packet['requested_specification']['trial_id']
        require(trial not in trials, 'capacitance_region_reused_trial')
        trials.add(trial)
        protocol = {k: v for k, v in packet['requested_specification'].items() if k != 'trial_id'}
        require(input_index not in protocols or protocols[input_index] == protocol,
                'capacitance_region_probe_protocol_changed')
        protocols[input_index] = protocol
    require(seen == {(phase, i) for phase in ('before', 'after') for i in range(len(parameters))},
            'capacitance_region_incomplete_probe_set')
    return {'kind': 'capacitance_region_audit', 'schema_version': 1, 'physical_state_verified': True,
            'selected_membranes': max(0, last-first+1), 'primary_trials': len(trials),
            'scientific_verdict': None, 'training_certificate_verified': False}


def audit_capacitance_region(path):
    path = Path(path).resolve(strict=True)
    try:
        return _audit(load(path), path.parent)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_capacitance_region:'+str(error)) from error
