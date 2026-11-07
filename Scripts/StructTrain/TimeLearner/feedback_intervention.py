"""Audit effective graph equality around a declared storage-profile intervention.

This does not construct images, prove their growth behaviour, certify training,
or establish a causal result from an arbitrary pair of JSON documents. Native
import, image readback and paired waveforms remain mandatory evidence.
"""
from copy import deepcopy
import re
import struct

from .model_identity import canonical_model_sha256
from .native_evidence import number, require


CLASS_PARAMETERS = frozenset({
    'MembraneClassName', 'LTMembraneClassName', 'LTZoneClassName',
    'ExcGeneratorClassName', 'InhGeneratorClassName', 'ExcChannelClassName',
    'InhChannelClassName', 'SynapseClassName', 'ExcSynapseClassName',
    'InhSynapseClassName',
})


def _model(identity):
    require(type(identity) is dict and set(identity) == {
        'kind', 'schema_version', 'canonical_encoding', 'valid', 'diagnostics', 'model', 'sha256'},
        'feedback_identity_fields')
    require(identity['kind'] == 'semantic_model_identity' and identity['valid'] is True and
            identity['diagnostics'] == [] and type(identity['schema_version']) is int and
            identity['schema_version'] in (1, 2) and
            identity['canonical_encoding'] == 'length-framed-utf8-binary64-v1',
            'feedback_invalid_identity')
    model = identity['model']
    require(type(model) is dict and model.get('schema_version') == identity['schema_version'] and
            canonical_model_sha256(model) == identity['sha256'], 'feedback_identity_digest')
    nodes = model.get('nodes')
    require(type(nodes) is list and nodes and all(type(n) is dict and
            type(n.get('path')) is str and type(n.get('parameters')) is dict for n in nodes) and
            len({n['path'] for n in nodes}) == len(nodes), 'feedback_invalid_nodes')
    return model


def _gain(prop):
    require(type(prop) is dict and prop.get('binding') is False and
            type(prop.get('data')) is dict and prop['data'].get('type') == 'binary64' and
            type(prop['data'].get('value')) is str and
            re.fullmatch('[0-9a-f]{16}', prop['data']['value']), 'feedback_invalid_gain')
    value = number(struct.unpack('>d', bytes.fromhex(prop['data']['value']))[0])
    require(value >= 0, 'feedback_invalid_gain')
    return value


def audit_profile_delta(source, candidate, class_renames, *, feedback_gain=None):
    """Allow only exact declared image renames and an optional uniform gain.

    feedback_gain=None is the baseline reconstruction gate: every physical
    parameter must be identical. A finite nonnegative value requires that gain
    on every actual membrane, including any existing LT membrane. Nothing is
    inferred from a parent property or from a membrane name.
    """
    before, after = _model(source), _model(candidate)
    require(type(class_renames) is dict and all(type(a) is str and a and
            type(b) is str and b and a != b for a, b in class_renames.items()) and
            len(set(class_renames.values())) == len(class_renames) and
            not set(class_renames).intersection(class_renames.values()), 'feedback_invalid_class_renames')
    gain = None if feedback_gain is None else number(feedback_gain)
    require(gain is None or gain >= 0, 'feedback_invalid_requested_gain')
    expected = deepcopy(before)
    used = set()

    def rename(name):
        if name in class_renames:
            used.add(name)
            return class_renames[name]
        return name

    membranes = []
    actual = {n['path']: n for n in after['nodes']}
    for node in expected['nodes']:
        node['class'] = rename(node['class'])
        for name, prop in node['parameters'].items():
            if name in CLASS_PARAMETERS:
                require(prop.get('binding') is False and prop.get('data', {}).get('type') == 'utf8',
                        'feedback_bound_or_invalid_class_reference')
                prop['data']['value'] = rename(prop['data']['value'])
        if 'FeedbackGain' in node['parameters']:
            previous = _gain(node['parameters']['FeedbackGain'])
            require(node['path'] in actual and 'FeedbackGain' in actual[node['path']]['parameters'],
                    'feedback_missing_membrane')
            current = _gain(actual[node['path']]['parameters']['FeedbackGain'])
            if gain is not None:
                require(current == gain, 'feedback_effective_gain_mismatch')
                node['parameters']['FeedbackGain']['data']['value'] = struct.pack('>d', gain).hex()
            membranes.append({'path': node['path'], 'source_gain': previous, 'candidate_gain': current})
    require(membranes, 'feedback_no_membranes')
    require(used == set(class_renames), 'feedback_unused_class_rename')
    # Includes graph edges, bindings, caches, order, timestep, LT threshold,
    # heterogeneous channel physics and every individual learned parameter.
    require(expected == after, 'feedback_undeclared_graph_change')
    return {'kind': 'feedback_effective_graph_delta_audit', 'schema_version': 1,
            'source_revision': source['sha256'], 'candidate_revision': candidate['sha256'],
            'mode': 'baseline_reconstruction' if gain is None else 'uniform_feedback_gain',
            'class_renames': deepcopy(class_renames), 'membranes': membranes,
            'all_other_effective_graph_fields_equal': True,
            'storage_image_closure_verified': False, 'waveform_equivalence_verified': False,
            'training_certificate': None, 'scientific_verdict': None}
