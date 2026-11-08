"""Self-contained learned/stopped package5 consistency, without native admission.

Summary6 is an optional additional record. It is never synthesized from the
package to hide missing runtime artifacts. Actual pipeline execution requires
its own produced summary/artifact set and immutable native runtime checks.
"""
from .capacitance_evidence import _images, audit_capacitance_state
from .composite_certificate_evidence import accepted_measurement_records, audit_composite_certificate
from .composite_configuration import project_composite_configuration
from .composite_measurement_contract import integral_number_view
from .composite_measurement_evidence import audit_composite_measurement_archive
from .composite_runtime_plan import audit_runtime_plan, validate_completed_parameters
from .composite_source_evidence import audit_identity, audit_snapshot, keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, count, number, require
from .response_domain_evidence import _same, _text, _finite_json
from .training_capacitance_witness import validate_graph_input_parameters

FIELDS = set(('kind schema_version dynamic_checkpoint state_kind implementation_id controller_version '
    'calculate_mode structure_build_mode configuration protocol runtime_plan trained_inputs model_revision '
    'model_epoch session_attempt training_outcome reason certificate capture_revision capture_epoch '
    'reference_complete measurement_archive dataset neuron capacitance_state sha256').split())
COMPLETED = {'exact','search_unresolved'}
STOPPED = {'external_stop','budget_exhausted','invalid_model','invalid_observation','search_unresolved'}


def _physical_archive(package):
    archive=package['neuron']
    require(type(archive) is dict and archive.get('kind')=='timelearner_model_archive'
            and count(archive['schema_version'])==2 and archive['sha256']==digest({k:v for k,v in archive.items() if k!='sha256'}),
            'composite_native_archive_schema_or_digest')
    audit_snapshot(archive['graph']);identity=archive['graph']['identity'];audit_identity(identity)
    require(identity['sha256']==package['model_revision'],'composite_actual_trained_model_revision')
    images=_images(archive['class_definitions']);source=package['measurement_archive']['source_binding']
    require(digest(images)==source['storage_images_sha256'],'composite_actual_trained_storage_changed')
    validate_graph_input_parameters(package['configuration']['model'],identity,package['trained_inputs'])
    audit_snapshot(package['dataset'],dataset=True)
    metadata=archive['metadata'];training=metadata['training']
    require(metadata['implementation_id']==package['implementation_id'] and metadata['state_kind']==package['state_kind']
            and training['status']==package['training_outcome'] and training['target_id']==package['protocol']['sample_id']
            and metadata['conversion']['mode']=='none' and metadata['calibration']['status']=='fixed',
            'composite_actual_archive_metadata_binding')
    _same(training['target_pattern'],source['applied_source_isi'])
    references,_=accepted_measurement_records(package['measurement_archive'])
    _same(training['captured_per_input'],[r['measurement']['raw_potential'] for r in references] if package['reference_complete'] else [])
    if package['certificate'] is None:
        require(training['certificate'] is None,'composite_stopped_archive_has_certificate')
    else:
        _same(training['certificate'],dict(state_identity=package['model_revision'],status=package['training_outcome']))
    if 'capacitance_search' in training:
        _same(training['capacitance_search'],package['runtime_plan']['search']['capacitance_search'])
    state=package['capacitance_state'];initial=source['optional_C0_witness']
    if state is None:
        require(initial is None,'composite_actual_C0_lost')
        return None
    require(initial is not None,'composite_actual_C0_invented')
    result=audit_capacitance_state(state,state['baseline']['model_spec'],identity,archive['class_definitions'])
    _same(state['baseline']['model_spec'],initial['native_state']['baseline']['model_spec'])
    _same(state['maximum_relative_change'],initial['native_state']['maximum_relative_change'])
    for field in ('model_revision','capture_model','storage_images_sha256'):
        _same(state['baseline'][field],initial['native_state']['baseline'][field])
    return result


def audit_composite_package(document, summary=None, *, external_resolver=None):
    """Replay embedded groups/certificate; no execution or import is inferred."""
    try:
        keys(document,FIELDS,'unknown_composite_package_fields');_finite_json(document)
        require(count(document['schema_version'])==5 and document['sha256']==digest({k:v for k,v in document.items() if k!='sha256'}),
                'composite_package_schema_or_digest')
        package=integral_number_view(document);config=package['configuration'];protocol=package['protocol']
        require(package['kind'] in ('timelearner_completed_state','timelearner_stopped_state')
                and package['dynamic_checkpoint'] is False and count(package['controller_version'])==2
                and count(package['calculate_mode']) in (0,1) and count(package['structure_build_mode']) in (0,1),
                'composite_package_kind_or_control')
        _text(package['implementation_id']);_text(package['model_revision']);count(package['model_epoch'])
        require(count(package['session_attempt'])>0 and type(package['reference_complete']) is bool
                and type(package['reason']) is str,'composite_package_attempt_or_reason')
        project_composite_configuration(config)
        archive=package['measurement_archive']
        _same(archive['protocol'],protocol)
        group_audit=audit_composite_measurement_archive(document['measurement_archive'],config,
            runtime_plan=package['runtime_plan'],external_resolver=external_resolver)
        source=archive['source_binding'];_same(package['capture_revision'],source['initial_model']['sha256'])
        require(count(package['capture_epoch'])==count(source['initial_epoch']),'composite_package_capture_epoch')
        references,finals=accepted_measurement_records(archive);n=len(protocol['inputs'])
        require(package['reference_complete'] is (len(references)==n),'composite_package_reference_completeness')
        for reference in references:
            require(reference['logical_request']['base_model_revision']==package['capture_revision']
                    and count(reference['logical_request']['model_epoch'])==count(package['capture_epoch']),
                    'composite_package_reference_capture_model')
        runtime=audit_runtime_plan(package['runtime_plan'],config,protocol,capacitance_state=package['capacitance_state'])
        require(archive['current_attempt_id']==package['runtime_plan']['run_id'],'composite_package_current_attempt')
        capacitance=_physical_archive(package)
        completed=package['kind']=='timelearner_completed_state'
        if completed:
            require(package['state_kind']=='learned_solo' and package['training_outcome'] in COMPLETED
                    and package['reference_complete'] is True and package['certificate'] is not None,
                    'composite_completed_package_without_proof')
            validate_completed_parameters(package['trained_inputs'],package['runtime_plan'])
            certificate=audit_composite_certificate(package,group_audit)
        else:
            require(package['state_kind']=='diagnostic' and package['training_outcome'] in STOPPED
                    and package['certificate'] is None and package['reason'], 'composite_stopped_package_claims_training')
            certificate=None
        summary_audit=None
        if summary is not None:
            from .composite_summary_evidence import audit_composite_summary
            summary_audit=audit_composite_summary(summary,package,group_audit)
        counters=archive['counters']['archive']
        return {'auditor_version':1,'package_schema_version':5,'package_digest_verified':True,
            'certificate_consistent':certificate is not None,'exact':certificate['exact'] if certificate else None,
            'model_revision':package['model_revision'],'training_outcome':package['training_outcome'],
            'logical_groups':counters['groups'],'native_probes':counters['native_probes'],'sampled_frames':counters['sampled_frames'],
            'primary_bytes':counters['primary_bytes'],'source_origin':archive['source_origin'],
            'owner_family_binding':archive['owner_family_binding'],'composite_measurements':group_audit,
            'runtime_plan':runtime,'capacitance_state':capacitance,'summary_checked':summary is not None,
            'summary':summary_audit,'search_history_retained':summary['search_history_retained'] if summary is not None else None,
            'native_import_verified':False,'native_execution_verified':False,'live_authority_restored':False,'evaluation_verdict':None}
    except EvidenceError: raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,UnicodeError,OverflowError,OSError) as error:
        raise EvidenceError('malformed_composite_package') from error
