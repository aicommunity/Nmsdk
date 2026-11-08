"""Source-family/candidate consistency from retained native snapshots.

This reads historical data. It does not import XML or attest actual Rdk
execution/storage ownership; those checks require the native production gate.
"""
import hashlib

from .capacitance_evidence import _images
from .composite_configuration import project_composite_configuration
from .composite_measurement_contract import SOURCE_FIELDS, CANDIDATE_FIELDS
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import count, number, require
from .response_domain_evidence import _same, _text
from .training_capacitance_witness import audit_training_capacitance_witness, validate_graph_input_parameters

SNAPSHOT_FIELDS = {'component_name', 'component_class', 'native_xml', 'native_xml_sha256', 'identity'}


def keys(value, fields, reason):
    require(type(value) is dict and set(value) == fields, reason)


def audit_identity(identity):
    keys(identity, {'kind', 'schema_version', 'valid', 'diagnostics', 'canonical_encoding', 'model', 'sha256'},
         'composite_identity_fields')
    require(identity['kind'] == 'semantic_model_identity' and count(identity['schema_version']) in (1, 2)
            and identity['valid'] is True and identity['diagnostics'] == []
            and identity['canonical_encoding'] == 'length-framed-utf8-binary64-v1'
            and identity['sha256'] == digest(identity['model']), 'composite_identity_digest_or_validity')
    model = identity['model']
    require(type(model) is dict and count(model['schema_version']) == count(identity['schema_version'])
            and type(model['nodes']) is list and bool(model['nodes']), 'composite_identity_model_missing')
    nodes = {}
    for node in model['nodes']:
        require(type(node) is dict and type(node.get('parameters')) is dict, 'composite_identity_node_invalid')
        path = _text(node['path']); require(path not in nodes, 'composite_identity_duplicate_node')
        _text(node['class']); nodes[path] = node
    require('$' in nodes, 'composite_identity_root_missing')
    return nodes


def _classes(nodes):
    result = {node['class'] for node in nodes.values()}
    for node in nodes.values():
        for name, parameter in node['parameters'].items():
            data = parameter['data']
            if name.endswith('ClassName') and data['type'] == 'utf8':
                require(type(data['value']) is str, 'composite_class_selector_invalid')
                if data['value']: result.add(data['value'])
    return result


def audit_snapshot(snapshot, *, dataset=False):
    keys(snapshot, SNAPSHOT_FIELDS | ({'required_class_names'} if dataset else set()), 'composite_snapshot_fields')
    _text(snapshot['component_name']); _text(snapshot['component_class'])
    text = _text(snapshot['native_xml'])
    require(hashlib.sha256(text.encode('utf-8')).hexdigest() == snapshot['native_xml_sha256'],
            'composite_snapshot_xml_digest')
    nodes = audit_identity(snapshot['identity'])
    require(nodes['$']['class'] == snapshot['component_class'], 'composite_snapshot_root_class')
    if dataset:
        _same(snapshot['required_class_names'], sorted(_classes(nodes), key=lambda name: name.encode('utf-16-be')))
    return nodes


def audit_source_binding(source, source_origin, configuration):
    project_composite_configuration(configuration)
    keys(source, SOURCE_FIELDS, 'composite_initial_source_fields')
    require(source['kind'] == 'composite_train_initial_source_v1' and count(source['schema_version']) == 2
            and source_origin == digest(source), 'composite_initial_source_identity')
    initial = audit_identity(source['initial_model']); count(source['initial_epoch'])
    audit_snapshot(source['initial_native_snapshot'])
    _same(source['initial_native_snapshot']['identity'], source['initial_model'])
    dataset = audit_snapshot(source['initial_dataset'], dataset=True)
    from .native_model_spec import validate_model_spec
    validate_model_spec(source['model_spec'])
    # The creation declaration may retain null/default Rs, while the immutable
    # planning declaration records the actual initial L/Ns/R readback. Neither
    # declaration substitutes for the retained effective graph.
    _same({key:value for key,value in source['model_spec'].items() if key != 'inputs'},
          {key:value for key,value in configuration['model'].items() if key != 'inputs'})
    require(len(source['model_spec']['inputs']) == len(configuration['model']['inputs']),
            'composite_initial_creation_input_dimension')
    parameters=[dict(length=p['attachment'],synapses=p['synapses'],resistance=p['resistance'])
                for p in configuration['model']['inputs']]
    validate_graph_input_parameters(configuration['model'],source['initial_model'],parameters)
    _same(source['applied_source_isi'], configuration['model']['initial_isi'])
    require(source['pattern_hash'] == digest(source['applied_source_isi']), 'composite_initial_source_pattern')
    profile = configuration['stimulus_profile']
    _same(source['actual_source_profile'], [profile[k] for k in ('generator_class', 'amplitude', 'pulse_length',
          'frequency_hz', 'frequency_deviation', 'use_transit_signal', 'use_pattern_output')])
    images = _images(source['storage_images'])
    require(source['storage_images_sha256'] == digest(images)
            and _classes(initial) | _classes(dataset) <= set(images), 'composite_initial_storage_closure')
    for name in ('neuron_class', 'dataset_class', 'generator_class'):
        require(configuration['model'][name] in images, 'composite_initial_storage_profile_missing')
    origin = source['optional_C0_origin']; require(type(origin) is str, 'composite_initial_C0_origin_invalid')
    witness = source['optional_C0_witness']
    if witness is None:
        require(origin == '', 'composite_initial_C0_witness_missing')
    else:
        audit_training_capacitance_witness(witness)
        require(origin == witness['controller_parameters']['origin'] and
                witness['model_revision'] == source['initial_model']['sha256'], 'composite_initial_C0_binding')
        _same(witness['model'], source['initial_model'])
        require(digest(_images(witness['storage_images'])) == source['storage_images_sha256'],
                'composite_initial_C0_storage_changed')
    return {'source_origin': source_origin, 'initial_model_revision': source['initial_model']['sha256'],
            'initial_epoch': count(source['initial_epoch']), 'storage_images': len(images),
            'C0_present': witness is not None, 'native_import_verified': False}


def audit_candidate_binding(candidate, witness_id, logical, source, source_origin):
    keys(candidate, CANDIDATE_FIELDS, 'composite_candidate_fields')
    require(candidate['kind'] == 'composite_train_candidate_binding_v1' and candidate['source_origin'] == source_origin
            and witness_id == digest(candidate) and candidate['storage_images_sha256'] == source['storage_images_sha256'],
            'composite_candidate_source_or_digest')
    audit_identity(candidate['model_identity'])
    require(candidate['model_identity']['sha256'] == logical['base_model_revision'], 'composite_candidate_model_revision')
    current = candidate['optional_C0_witness']
    if source['optional_C0_witness'] is None:
        require(current is None, 'composite_candidate_invented_C0')
    else:
        require(current is not None, 'composite_candidate_C0_lost')
        audit_training_capacitance_witness(current)
        require(current['model_revision'] == logical['base_model_revision'] and
                current['controller_parameters']['origin'] == source['optional_C0_origin'], 'composite_candidate_C0_binding')
        _same(current['model'], candidate['model_identity'])
        _same(current['controller_parameters']['maximum_relative_change'],
              source['optional_C0_witness']['controller_parameters']['maximum_relative_change'])
        require(digest(_images(current['storage_images'])) == source['storage_images_sha256'],
                'composite_candidate_C0_storage_changed')
    return {'candidate_witness_id': witness_id, 'model_revision': logical['base_model_revision'],
            'C0_present': current is not None, 'native_import_verified': False}
