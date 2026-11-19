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


def audit_physical_model_data(package, *, frozen=False):
    """Check retained physics; XML import and source-evidence joins stay separate."""
    try:
        keys(package, FIELDS, 'physical_data_field_set')
        require(package['kind'] == 'timelearner_physical_model_data' and type(package['schema_version']) is int
                and package['schema_version'] == 1 and package['data_only'] is True
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
        require(boundary['model_revision'] == package['model_revision'], 'physical_data_source_revision')
        solo = boundary['kind'] in SOLO
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
        require(metadata['implementation_id'] == package['implementation_id']
                and metadata['state_kind'] == boundary['state_kind']
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
            training_certificate_transferred=False, calibration_confirmed=False, evaluation_verdict=None)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError('malformed_physical_model_data:' + str(error)) from error
