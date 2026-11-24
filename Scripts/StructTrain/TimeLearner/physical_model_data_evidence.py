"""Portable consistency of native physical DATA, never training/execution proof.

The source boundary identifies separately retained evidence. Its hash alone does
not establish the training outcome, calibration, native import or provenance.
"""
from .capacitance_evidence import _images
from .composite_source_evidence import _classes, audit_dataset_source, audit_snapshot, keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, count, number, require
from .native_model_spec import validate_model_spec
from .recognition_evidence import _physical
from .training_capacitance_witness import validate_graph_input_parameters
import copy

FIELDS = set(('kind schema_version data_only dynamic_checkpoint certificate implementation_id source_boundary '
    'configuration configuration_text protocol controls parameters model_revision source_solo_revision conversion_record '
    'dataset neuron sha256').split())
SOLO = {'timelearner_completed_state': 'learned_solo', 'timelearner_stopped_state': 'diagnostic'}
RECOGNITION = {'timelearner_recognition_state': 'recognition',
    'timelearner_diagnostic_recognition_state': 'diagnostic_recognition',
    'timelearner_recognition_threshold_candidate': 'recognition',
    'timelearner_diagnostic_threshold_candidate': 'diagnostic_recognition',
    'timelearner_calibrated_recognition_state': 'recognition'}


def _sha(value):
    require(type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value),
            'physical_data_invalid_sha256')



CONVERSION_FIELDS = {'source_model_data', 'conversion_spec', 'reference_amplitudes'}
THRESHOLD_FIELDS = {'source_recognition_data', 'threshold', 'candidate_record'}


def _threshold_source(package):
    source=package['source_recognition_data']
    require(type(source) is dict and type(source.get('schema_version')) is int and
            source['schema_version'] in (1,2), 'physical_threshold_requires_base_recognition_data')
    audit_physical_model_data(source,frozen=True)
    require(source['schema_version']==2 or source['source_boundary']['kind'] in
            ('timelearner_recognition_state','timelearner_diagnostic_recognition_state'),
            'physical_threshold_requires_base_recognition_data')
    require(all(package[k]==source[k] for k in ('source_boundary','source_solo_revision','configuration',
            'configuration_text','protocol','controls','parameters','conversion_record','dataset','implementation_id')),
            'physical_threshold_changed_source_conditions')
    require(_images(package['neuron']['class_definitions'])==_images(source['neuron']['class_definitions']),
            'physical_threshold_changed_storage_physics')
    threshold=number(package['threshold']);record=package['candidate_record']
    keys(record,{'schema_version','algorithm','source_recognition_sha256','source_model_revision',
         'model_revision','ltzone_path','original_threshold','threshold','calibrated'},'physical_threshold_record_fields')
    old_metadata=source['neuron']['metadata'];calibration=old_metadata['calibration'];path=calibration['ltzone_path']
    require(type(record['schema_version']) is int and record['schema_version']==1 and
            record['algorithm']=='explicit-native-threshold-v2' and record['source_recognition_sha256']==source['sha256'] and
            record['source_model_revision']==source['model_revision'] and record['model_revision']==package['model_revision'] and
            record['ltzone_path']==path and number(record['original_threshold'])==number(calibration['threshold']) and
            number(record['threshold'])==threshold and record['calibrated'] is False,'physical_threshold_record_scope')
    expected=copy.deepcopy(old_metadata)
    expected['calibration'].update(status='fixed',protocol='threshold-candidate-not-calibrated',
                                   threshold=threshold,candidate_record=record)
    expected['recognition_verification'].update(model_identity=package['model_revision'],status='unverified',certificate=None)
    require(package['neuron']['metadata']==expected,'physical_threshold_metadata_scope')
    # Native import is still a separate proof. This portable comparison also
    # rejects signed changes to any other part of the archived semantic graph.
    before=source['neuron']['graph']['identity']['model']
    after=copy.deepcopy(package['neuron']['graph']['identity']['model'])
    source_nodes={n['path']:n for n in before['nodes']};changed_nodes={n['path']:n for n in after['nodes']}
    require(path in source_nodes and path in changed_nodes,'physical_threshold_path_missing')
    old=source_nodes[path]['parameters']['Threshold'];new=changed_nodes[path]['parameters']['Threshold']
    require(old['binding'] is False and new['binding'] is False and
            old['data']['type']==new['data']['type']=='binary64','physical_threshold_not_fixed_scalar')
    new['data']['value']=old['data']['value']
    require(after==before,'physical_threshold_changed_other_graph_physics')
    return source


def _conversion_source(package):
    source = package['source_model_data']
    require(type(source) is dict and source.get('schema_version') == 1,
            'physical_data_conversion_requires_solo_data1')
    audit_physical_model_data(source)
    require(source['source_boundary']['kind'] in SOLO and package['source_boundary'] == source['source_boundary']
            and package['source_solo_revision'] == source['model_revision'], 'physical_data_conversion_source_boundary')
    expected = dict(source['configuration']); expected['model'] = dict(expected['model'])
    expected['model']['allow_muted_input_baseline'] = False
    require(package['configuration'] == expected and all(package[k] == source[k] for k in
            ('configuration_text', 'protocol', 'controls', 'dataset', 'implementation_id')),
            'physical_data_conversion_changed_source_conditions')
    # Windows and Linux may serialize equivalent native XML with different
    # attribute order/formatting. Validate both byte digests and compare the
    # complete semantic storage closure (including future growth selectors).
    # Only the native importer proves that XML reconstructs those identities.
    require(_images(package['neuron']['class_definitions']) == _images(source['neuron']['class_definitions']),
            'physical_data_conversion_changed_storage_physics')
    spec = package['conversion_spec']; require(type(spec) is dict, 'physical_data_conversion_spec_object')
    version = spec.get('schema_version')
    require(type(version) is int and version in (1, 2), 'physical_data_conversion_spec_schema')
    keys(spec, {'schema_version', 'mode', 'resistance_bounds'} | ({'post_tune'} if version == 2 else set()),
         'physical_data_conversion_spec_fields')
    references = package['reference_amplitudes']; mode = spec['mode']
    require(type(references) is list and mode in ('identity', 'historical_branch_n1_v1'),
            'physical_data_conversion_mode_or_references')
    n = len(source['parameters'])
    require((not references and spec['resistance_bounds'] == []) if mode == 'identity' else
            (source['configuration']['model']['branch'] is True and
             source['configuration']['model']['normalization'] == 'N1' and len(references) == n and
             all(number(a) > 0 for a in references) and type(spec['resistance_bounds']) is list and
             len(spec['resistance_bounds']) == n), 'physical_data_conversion_reference_scope')
    for bound in spec['resistance_bounds']:
        keys(bound, {'minimum', 'maximum'}, 'physical_data_conversion_bounds')
        require(0 < number(bound['minimum']) <= number(bound['maximum']), 'physical_data_conversion_bounds')
    record = package['conversion_record']
    require(record['schema_version'] == version and record['algorithm'] == mode and
            record['source_solo_sha256'] == source['source_boundary']['sha256'] and
            record['source_solo_identity'] == source['model_revision'] and
            record['result_identity'] == package['model_revision'] and
            len(record['decisions']) == n, 'physical_data_conversion_record_scope')
    metadata = package['neuron']['metadata']
    require(metadata['conversion']['record'] == record and
            metadata['conversion']['source_solo_sha256'] == source['source_boundary']['sha256'] and
            metadata['recognition_verification']['model_identity'] == package['model_revision'] and
            metadata['recognition_verification']['status'] == 'unverified' and
            metadata['recognition_verification']['certificate'] is None, 'physical_data_conversion_metadata_scope')
    if version == 2:
        post = spec['post_tune']
        keys(post, {'mode', 'source_model_revision', 'canonical_floor', 'canonical_last',
                    'requested_resistances', 'resistance_bounds'}, 'physical_data_post_tune_fields')
        require(post['mode'] in ('off', 'keep_done', 'canon_rmin', 'flat_last_r', 'search_synthetic_candidate')
                and record['post_tune']['mode'] == post['mode'] and
                record['post_tune']['source_model_revision'] == post['source_model_revision'] and
                record['post_tune']['selection_status'] == 'candidate_unmeasured' and
                record['post_tune']['calibration_status'] == 'unconfirmed', 'physical_data_post_tune_scope')
    # This checks retained conditions and declared provenance. Only the native
    # importer re-derives every graph edit and compares the entire DATA document.
    return source


def audit_physical_model_data(package, *, frozen=False):
    """Check retained physics; XML import and source-evidence joins stay separate."""
    try:
        converted = type(package) is dict and package.get('schema_version') == 2
        candidate = type(package) is dict and package.get('schema_version') == 3
        keys(package, FIELDS | (CONVERSION_FIELDS if converted else THRESHOLD_FIELDS if candidate else set()), 'physical_data_field_set')
        require(package['kind'] == 'timelearner_physical_model_data' and type(package['schema_version']) is int
                and package['schema_version'] in (1, 2, 3) and package['data_only'] is True
                and package['dynamic_checkpoint'] is False and package['certificate'] is None,
                'physical_data_not_certificate_or_checkpoint')
        _sha(package['sha256'])
        require(package['sha256'] == digest({k: v for k, v in package.items() if k != 'sha256'}),
                'physical_data_document_digest')
        require(type(package['implementation_id']) is str and bool(package['implementation_id'].strip())
                and type(package['configuration_text']) is str and bool(package['configuration_text'].strip()),
                'physical_data_missing_implementation_or_configuration')
        boundary = package['source_boundary']
        keys(boundary, {'kind', 'schema_version', 'state_kind', 'sha256', 'model_revision'}, 'physical_data_source_fields')
        states = SOLO | RECOGNITION
        require(boundary['kind'] in states and boundary['state_kind'] == states[boundary['kind']]
                and 1 <= count(boundary['schema_version']) <=
                (8 if boundary['kind'] in SOLO else 7), 'physical_data_source_kind')
        for value in (boundary['sha256'], boundary['model_revision'], package['source_solo_revision']):
            _sha(value)
        require(converted or candidate or boundary['model_revision'] == package['model_revision'], 'physical_data_source_revision')
        solo = boundary['kind'] in SOLO and not converted and not candidate
        if candidate:
            _threshold_source(package)
        elif converted:
            _conversion_source(package)
        require((package['conversion_record'] is None) if solo else type(package['conversion_record']) is dict,
                'physical_data_conversion_scope')
        require(not solo or package['source_solo_revision'] == package['model_revision'], 'physical_data_solo_revision')
        model = package['configuration']['model']; validate_model_spec(model)
        require(type(model['branch']) is bool and number(model['frequency_hz']) > 0
                and type(model['inputs']) is list and bool(model['inputs'])
                and len(model['initial_isi']) == len(model['inputs']), 'physical_data_model_dimension_or_clock')
        controls = package['controls']
        keys(controls, {'controller_version', 'calculate_mode', 'structure_build_mode'}, 'physical_data_controls')
        require(count(controls['controller_version']) in (1, 2) and count(controls['calculate_mode']) in (0, 1)
                and count(controls['structure_build_mode']) in (0, 1), 'physical_data_controls')
        archive = package['neuron']
        require(archive['kind'] == 'timelearner_model_archive' and count(archive['schema_version']) == 2
                and archive['dynamic_checkpoint'] is False
                and archive['sha256'] == digest({k: v for k, v in archive.items() if k != 'sha256'}),
                'physical_data_archive_digest_or_schema')
        nodes = audit_snapshot(archive['graph']); images = _images(archive['class_definitions'])
        require(bool(images) and archive['graph']['identity']['sha256'] == package['model_revision']
                and nodes['$']['class'] == model['neuron_class'], 'physical_data_graph_revision_or_class')
        validate_graph_input_parameters(model, archive['graph']['identity'], package['parameters'])
        dataset = audit_snapshot(package['dataset'], dataset=True)
        require((_classes(nodes) | _classes(dataset)) <= set(images), 'physical_data_storage_closure')
        audit_dataset_source(dataset, model, package['configuration']['stimulus_profile'], model['initial_isi'])
        require(all(node['frequency_hz'] == str(count(model['frequency_hz']))
                    for node in list(nodes.values()) + list(dataset.values())), 'physical_data_effective_clock')
        protocol = package['protocol']; configuration = package['configuration']
        require(protocol['pattern_hash'] == digest(model['initial_isi'])
                and protocol['routing'] == ('branch_solo_burst' if model['branch'] else 'classic_burst')
                and len(protocol['inputs']) == len(model['inputs'])
                and protocol['sample_id'] == configuration['sample_id']
                and protocol['revision'] == configuration['protocol_revision']
                and protocol['minimum_amplitude'] == configuration['minimum_amplitude']
                and protocol['maximum_sample_gap'] == configuration['maximum_sample_gap']
                and protocol['stimulus_profile'] == configuration['stimulus_profile'], 'physical_data_protocol_scope')
        metadata = archive['metadata']; training = metadata['training']; calibration = metadata['calibration']
        expected_state=(package['source_recognition_data']['neuron']['metadata']['state_kind'] if candidate else
            ('diagnostic_recognition' if boundary['kind']=='timelearner_stopped_state' else 'recognition') if converted else
            boundary['state_kind'])
        require(metadata['implementation_id'] == package['implementation_id']
                and metadata['state_kind'] == expected_state
                and training['trainer'] == ('Branch' if model['branch'] else 'Classic')
                and training['normalization'] == model['normalization']
                and training['target_pattern'] == model['initial_isi']
                and training['target_id'] == protocol['sample_id'], 'physical_data_metadata_scope')
        path = calibration['ltzone_path']
        require(type(path) is str and path in nodes, 'physical_data_threshold_path')
        threshold = _physical(nodes[path], 'Threshold')
        require(threshold == number(calibration['threshold']), 'physical_data_threshold_metadata_mismatch')
        if frozen:
            require(not solo and model['allow_muted_input_baseline'] is False,
                    'physical_data_frozen_requires_recognition_and_all_inputs')
        return dict(kind='physical_model_data_audit', schema_version=1, data_only=True,
            model_revision=package['model_revision'], pattern_size=len(model['inputs']), branch=model['branch'],
            frequency_hz=number(model['frequency_hz']), threshold_path=path, threshold_classes=(nodes[path]['class'],),
            effective_threshold=threshold, source_training_evidence_checked=False, native_import_verified=False,
            training_certificate_transferred=False, calibration_confirmed=False, evaluation_verdict=None,
            explicit_conversion_data=converted, native_conversion_verified=False,
            **(dict(explicit_threshold_candidate_data=True,native_threshold_candidate_verified=False) if candidate else {}))
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError('malformed_physical_model_data:' + str(error)) from error
