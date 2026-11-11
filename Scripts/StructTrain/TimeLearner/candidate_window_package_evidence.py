"""Self-contained package6 DATA joins; terminal provenance is separate.

Only original execution-export bytes/SHA and source-case ownership can promote
a completed classification. A coherent rewrite of public saved DATA cannot
prove that the producer actually completed; this auditor never claims it did.
"""
import re
import struct

from .candidate_window_archive_evidence import audit_candidate_window_archive
from .candidate_window_certificate_evidence import (audit_candidate_window_certificate,
                                                   replay_candidate_window_certificate)
from .candidate_window_runtime_plan import audit_candidate_window_runtime_plan
from .composite_certificate_evidence import accepted_measurement_records
from .composite_measurement_contract import integral_number_view
from .composite_package_evidence import FIELDS, COMPLETED, STOPPED, _physical_archive
from .composite_runtime_plan import validate_completed_parameters
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, count, number, require
from .response_domain_evidence import _same, _text, _finite_json


def _runtime_context(package):
    plan=package['runtime_plan'];archive=package['measurement_archive'];configuration=package['configuration']
    result=audit_candidate_window_runtime_plan(plan,configuration,package['protocol'])
    require(plan['search']['normalization']==configuration['model']['normalization'],
            'candidate_window_package_normalization_changed')
    require(plan['run_id']==archive['current_attempt_id'],'candidate_window_package_current_attempt')
    current=[r for r in archive['records'] if r['attempt_id']==archive['current_attempt_id']]
    initial=current[0]['logical_request'] if current else None
    revision=initial['base_model_revision'] if initial else package['model_revision']
    epoch=initial['model_epoch'] if initial else package['model_epoch']
    require(plan['initial_model_revision']==revision and count(plan['initial_model_epoch'])==count(epoch),
            'candidate_window_package_runtime_initial_model')
    return result


def _archive_metadata(package, references):
    """Bind the exact native saved metadata, including the actual LT threshold."""
    graph=package['neuron']['graph']['identity']['model']
    paths=[row['cached_ltzone'] for row in graph['caches'] if row.get('cached_ltzone')]
    require(paths,'candidate_window_package_missing_ltzone')
    path=paths[0];nodes={row['path']:row for row in graph['nodes']}
    data=nodes[path]['parameters']['Threshold']['data'];hexadecimal=data['value']
    require(data['type']=='binary64' and type(hexadecimal) is str
            and re.fullmatch('[0-9a-fA-F]{16}',hexadecimal) is not None,'candidate_window_package_threshold')
    threshold=number(struct.unpack('>d',bytes.fromhex(hexadecimal))[0])
    stopped=package['kind']=='timelearner_stopped_state';plan=package['runtime_plan']
    training=dict(status=package['training_outcome'],target_id=package['protocol']['sample_id'],
        trainer='Branch' if package['configuration']['model']['branch'] else 'Classic',
        normalization=plan['search']['normalization'],target_pattern=package['configuration']['model']['initial_isi'],
        captured_per_input=[r['measurement']['raw_potential'] for r in references] if package['reference_complete'] else [],
        certificate=None if stopped else dict(state_identity=package['model_revision'],status=package['training_outcome']))
    if stopped:
        training.update(reference_complete=package['reference_complete'],capture_revision=package['capture_revision'],
                        capture_epoch=package['capture_epoch'],reason=package['reason'])
    if plan['search']['capacitance_search'] is not None:training['capacitance_search']=plan['search']['capacitance_search']
    expected=dict(implementation_id=package['implementation_id'],state_kind=package['state_kind'],training=training,
        calibration=dict(status='fixed',protocol='fixed-trained-graph',ltzone_path=path,threshold=threshold),
        conversion=dict(mode='none'))
    _same(package['neuron']['metadata'],expected)


def audit_candidate_window_package(document, summary=None, *, external_resolver=None):
    """Replay actual embedded/raw primary and certificate DATA, never a lease."""
    try:
        keys(document,FIELDS,'candidate_window_package6_fields');_finite_json(document)
        require(count(document['schema_version'])==6 and document['sha256']==digest({
            k:v for k,v in document.items() if k!='sha256'}),'candidate_window_package6_schema_or_digest')
        package=integral_number_view(document);archive=package['measurement_archive'];protocol=package['protocol']
        require(package['kind'] in ('timelearner_completed_state','timelearner_stopped_state')
                and package['dynamic_checkpoint'] is False and count(package['controller_version'])==2
                and count(package['calculate_mode']) in (0,1) and count(package['structure_build_mode']) in (0,1),
                'candidate_window_package6_kind_or_control')
        _text(package['implementation_id']);_text(package['model_revision']);count(package['model_epoch'])
        require(count(package['session_attempt'])>0 and type(package['reference_complete']) is bool
                and type(package['reason']) is str,'candidate_window_package6_attempt_or_reason')
        _same(archive['protocol'],protocol)
        group_audit=audit_candidate_window_archive(document['measurement_archive'],package['configuration'],
            runtime_plan=package['runtime_plan'],external_resolver=external_resolver)
        source=archive['source_binding'];_same(package['capture_revision'],source['initial_model']['sha256'])
        require(count(package['capture_epoch'])==count(source['initial_epoch']),'candidate_window_package_capture_epoch')
        references,_=accepted_measurement_records(archive);n=len(protocol['inputs'])
        require(package['reference_complete'] is (len(references)==n),'candidate_window_package_reference_completeness')
        for record in references:
            require(record['logical_request']['base_model_revision']==package['capture_revision']
                    and count(record['logical_request']['model_epoch'])==count(package['capture_epoch']),
                    'candidate_window_package_reference_model')
        runtime=_runtime_context(package)
        capacitance=_physical_archive(package)
        _archive_metadata(package,references)
        images={row['name'] for row in package['neuron']['class_definitions']}
        required=package['dataset']['required_class_names']
        require(type(required) is list and all(type(name) is str and name in images for name in required),
                'candidate_window_package_dataset_dependency')
        math=replay_candidate_window_certificate(package,group_audit)
        completed=package['kind']=='timelearner_completed_state'
        if completed:
            require(package['state_kind']=='learned_solo' and package['training_outcome'] in COMPLETED
                    and package['reference_complete'] is True and package['certificate'] is not None,
                    'candidate_window_completed_package_without_proof')
            validate_completed_parameters(package['trained_inputs'],package['runtime_plan'])
            certificate=audit_candidate_window_certificate(package,group_audit)
        else:
            require(package['state_kind']=='diagnostic' and package['training_outcome'] in STOPPED
                    and package['certificate'] is None and package['reason'],
                    'candidate_window_stopped_package_claims_training')
            certificate=None
        # A supplied summary is mandatory evidence, never synthesized from DATA.
        summary_audit=None
        if summary is not None:
            from .candidate_window_summary_evidence import audit_candidate_window_summary
            summary_audit=audit_candidate_window_summary(summary,package,group_audit)
        counters=archive['counters']['archive']
        return dict(auditor_version=1,package_schema_version=6,package_digest_verified=True,
            certificate_consistent=certificate is not None,exact=certificate['exact'] if certificate else None,
            mathematical_exact=None if math is None else math['exact'],
            stopped_math_is_not_completion=not completed and math is not None,
            model_revision=package['model_revision'],training_outcome=package['training_outcome'],
            logical_groups=counters['groups'],native_probes=counters['native_probes'],sampled_frames=counters['sampled_frames'],
            primary_bytes=counters['primary_bytes'],source_origin=archive['source_origin'],
            owner_family_binding=archive['owner_family_binding'],composite_measurements=group_audit,
            runtime_plan=runtime,capacitance_state=capacitance,summary_checked=summary is not None,summary=summary_audit,
            search_history_retained=summary_audit['search_history_retained'] if summary_audit else None,
            terminal_provenance_verified=False,native_import_verified=False,native_execution_verified=False,
            live_authority_restored=False,completed_classification_requires_original_execution_binding=True,evaluation_verdict=None)
    except EvidenceError:raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,UnicodeError,OverflowError,OSError) as error:
        raise EvidenceError('malformed_candidate_window_package6') from error
