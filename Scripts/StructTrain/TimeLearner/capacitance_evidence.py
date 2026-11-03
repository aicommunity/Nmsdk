"""Check persisted C0 witnesses against archived semantic physics.

This verifies data consistency. Native XML reconstruction and physical response
equivalence are separate integration checks, never inferred from these hashes.
"""
import hashlib
import re
import struct

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, number, require


def _signed(value):
    require(type(value) is dict and value.get('sha256') == canonical_model_sha256(
        {k: v for k, v in value.items() if k != 'sha256'}), 'capacitance_digest_mismatch')


def _nodes(model):
    require(type(model) is dict and type(model['schema_version']) is int
            and model['schema_version'] in (1, 2) and type(model['nodes']) is list,
            'invalid_capacitance_model')
    result = {}
    for node in model['nodes']:
        path = node['path']
        require(type(path) is str and path not in result, 'duplicate_capacitance_node')
        result[path] = node
    require('$' in result, 'missing_capacitance_model_root')
    return result


def _physical(node, name):
    p = node['parameters'][name]
    require(p['binding'] is False and p['data']['type'] == 'binary64'
            and type(p['data']['value']) is str and re.fullmatch('[0-9a-f]{16}', p['data']['value']),
            'invalid_capacitance_numeric_witness')
    return number(struct.unpack('>d', bytes.fromhex(p['data']['value']))[0])


def _physics(node):
    result = {}
    for name in ('Resistance', 'FBResistance', 'RestingResistance', 'Type'):
        _physical(node, name)
        result[name] = node['parameters'][name]['data']
    for name in ('UseAveragePotential', 'UseAverageSynapsis'):
        p = node['parameters'][name]
        require(p['binding'] is False and p['data']['type'] == 'boolean'
                and type(p['data']['value']) is bool, 'invalid_capacitance_boolean_witness')
        result[name] = p['data']
    return result


def _images(definitions):
    require(type(definitions) is list and 0 < len(definitions) <= 4096, 'invalid_capacitance_images')
    result, edges = {}, {}
    for d in definitions:
        require(type(d) is dict and set(d) == {'name', 'kind', 'base_class', 'snapshot', 'dependencies'}
                and type(d['name']) is str and d['name'] and d['name'] not in result
                and d['kind'] in ('derived_image', 'native_required') and type(d['base_class']) is str,
                'invalid_capacitance_image_definition')
        snapshot = d['snapshot']; identity = snapshot['identity']; model = identity['model']
        require(identity['valid'] is True and not identity['diagnostics']
                and identity['sha256'] == canonical_model_sha256(model)
                and snapshot['native_xml_sha256'] == hashlib.sha256(snapshot['native_xml'].encode()).hexdigest(),
                'invalid_capacitance_image_snapshot')
        nodes = _nodes(model)
        # Match ModelArchive::Classes: structural selectors govern future
        # growth even when no instance of the selected class exists yet.
        expected = {n['class'] for n in nodes.values()}
        for node in nodes.values():
            for name, parameter in node['parameters'].items():
                data = parameter['data']
                if name.endswith('ClassName') and data['type'] == 'utf8':
                    require(type(data['value']) is str, 'invalid_capacitance_class_selector')
                    if data['value']: expected.add(data['value'])
        expected.discard(d['name'])
        if d['base_class']: expected.add(d['base_class'])
        require(type(d['dependencies']) is list and all(type(x) is str for x in d['dependencies'])
                and len(set(d['dependencies'])) == len(d['dependencies']) and set(d['dependencies']) == expected
                and bool(d['base_class']) == (d['kind'] == 'derived_image'), 'invalid_capacitance_image_dependencies')
        edges[d['name']] = expected
        result[d['name']] = {'kind': d['kind'], 'base_class': d['base_class'], 'model': model}
    done, visiting = set(), set()

    def visit(name, depth):
        require(name in result and depth <= 128 and name not in visiting, 'invalid_capacitance_image_closure')
        if name in done: return
        visiting.add(name)
        for child in edges[name]: visit(child, depth + 1)
        visiting.remove(name); done.add(name)

    for name in result: visit(name, 0)
    return result


def _audit(state, declaration, identity, archive_images):
    require(type(state) is dict and type(state.get('schema_version')) is int
            and state['schema_version'] in (1, 2), 'unknown_capacitance_parameter_state')
    fields = {'kind', 'schema_version', 'baseline', 'membrane_scales',
              'maximum_relative_change', 'applied_model_revision', 'sha256'}
    if state['schema_version'] == 2: fields.add('dormant_membrane_scales')
    require(set(state) == fields and state['kind'] == 'timelearner_capacitance_parameter_state',
            'unknown_capacitance_parameter_state')
    _signed(state); b = state['baseline']; _signed(b)
    require(set(b) == {'kind', 'schema_version', 'model_revision', 'frequency_hz', 'channels', 'sha256', 'model_spec',
            'capture_model', 'storage_images', 'storage_images_sha256', 'channel_classes', 'channel_physics', 'channel_origins'}
            and b['kind'] == 'timelearner_capacitance_baseline' and type(b['schema_version']) is int
            and b['schema_version'] == 2, 'unknown_bound_capacitance_baseline')
    frequency = number(b['frequency_hz'])
    require(frequency > 0 and frequency == int(frequency) and b['model_spec'] == declaration and frequency == number(declaration['frequency_hz'])
            and b['model_revision'] == canonical_model_sha256(b['capture_model']), 'capacitance_capture_binding_mismatch')
    captured, current = _nodes(b['capture_model']), _nodes(identity['model'])
    require(identity['valid'] is True and not identity['diagnostics']
            and captured['$']['class'] == declaration['neuron_class']
            and identity['sha256'] == canonical_model_sha256(identity['model']) == state['applied_model_revision'],
            'capacitance_applied_revision_mismatch')
    images = _images(b['storage_images']); actual_images = _images(archive_images)
    require(b['storage_images_sha256'] == canonical_model_sha256(images)
            and all(actual_images.get(n) == d for n, d in images.items()), 'capacitance_storage_profile_mismatch')
    channels = b['channels']; classes, physics, origins = (b[k] for k in ('channel_classes', 'channel_physics', 'channel_origins'))
    require(all(type(v) is dict for v in (channels, classes, physics, origins)) and channels
            and set(channels) == set(classes) == set(physics) == set(origins), 'incomplete_capacitance_witnesses')
    for path, c0 in channels.items():
        require(type(path) is str and path and number(c0) > 0 and classes[path] in images, 'invalid_capacitance_channel')
        if origins[path] == 'capture':
            origin = captured['$.'+path]
            require(origin['class'] == classes[path], 'capacitance_capture_class_mismatch')
        else:
            require(origins[path] == 'storage_image' and '$.'+path not in captured, 'invalid_capacitance_channel_origin')
            origin = _nodes(images[classes[path]]['model'])['$']
        require(_physical(origin, 'Capacity') == c0 and _physics(origin) == physics[path], 'capacitance_channel_witness_mismatch')
    scales = state['membrane_scales']; limit = number(state['maximum_relative_change'])
    require(limit >= 0 and type(scales) is dict and scales, 'invalid_capacitance_scale_policy')
    for path, scale in scales.items():
        require(type(path) is str and re.fullmatch(r'Dendrite[1-9][0-9]*_[1-9][0-9]*', path)
                and '$.'+path in current and number(scale) > 0 and 1-limit <= scale <= 1+limit,
                'invalid_capacitance_scale')
    dormant = state.get('dormant_membrane_scales', {})
    require(type(dormant) is dict and (state['schema_version'] == 1 or dormant)
            and not set(dormant).intersection(scales), 'invalid_dormant_capacitance_scales')
    for path, scale in dormant.items():
        require(type(path) is str and re.fullmatch(r'Dendrite[1-9][0-9]*_[1-9][0-9]*', path)
                and '$.'+path not in current and any(c.startswith(path+'.') for c in channels)
                and number(scale) > 0 and 1-limit <= scale <= 1+limit, 'invalid_dormant_capacitance_scale')
    seen = set()
    for path, node in current.items():
        if 'Capacity' not in node.get('parameters', {}): continue
        key = path.removeprefix('$.'); seen.add(key)
        require(key in channels and node['class'] == classes[key] and _physics(node) == physics[key]
                and node['frequency_hz'] == str(int(b['frequency_hz'])), 'capacitance_effective_physics_mismatch')
        membrane = key.split('.', 1)[0]
        require(_physical(node, 'Capacity') == channels[key]*scales.get(membrane, 1.), 'incomplete_or_changed_capacitance_scales')
    require(seen, 'missing_capacitance_effective_channels')
    result = {'schema_version': 1, 'consistent': True, 'effective_channels': len(seen),
            'baseline_channels': len(channels), 'storage_images': len(images), 'native_import_verified': False}
    if state['schema_version'] == 2:
        result.update(schema_version=2, dormant_membranes=len(dormant))
    return result


def audit_capacitance_state(state, declaration, identity, class_definitions):
    """Check a real owner-state snapshot without inventing a Train certificate."""
    try:
        return _audit(state, declaration, identity, class_definitions)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_capacitance_evidence:'+str(error)) from error


def controller_capacitance_parameters(state):
    """Derive a full typed map after audit_capacitance_state has validated it."""
    baseline = state['baseline']
    scales = dict(state['membrane_scales'])
    scales.update(state.get('dormant_membrane_scales', {}))
    for path in baseline['channels']:
        membrane = path.split('.', 1)[0]
        if re.fullmatch(r'Dendrite[1-9][0-9]*_[1-9][0-9]*', membrane):
            scales.setdefault(membrane, 1.)
    origin = canonical_model_sha256({
        'kind': 'timelearner_training_capacitance_origin', 'schema_version': 1,
        'capture_model_revision': baseline['model_revision'], 'model_spec': baseline['model_spec'],
        'storage_images_sha256': baseline['storage_images_sha256']})
    return {'origin': origin, 'maximum_relative_change': state['maximum_relative_change'], 'membrane_scales': scales}


def audit_package_capacitance(package):
    """Schema 1 carries no C0 provenance; do not invent an untrimmed baseline."""
    try:
        version = package['schema_version']
        require(type(version) is int and version in (1, 2, 3, 4), 'unknown_capacitance_package_schema')
        if version == 1:
            require('capacitance_state' not in package, 'unversioned_capacitance_state')
            return None
        return _audit(package['capacitance_state'], package['configuration']['model'],
                      package['neuron']['graph']['identity'], package['neuron']['class_definitions'])
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_capacitance_evidence:'+str(error)) from error
