"""Certificate2 residuals from independently replayed complete N+2 groups."""
from .composite_configuration import METHOD
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import count, number, require
from .response_domain_evidence import _same

FIELDS = set(('schema_version method_id exact model_revision model_epoch protocol_revision source_origin '
    'owner_family_binding reference_model_revision reference_model_epoch reference_semantic_proof_ids '
    'final_semantic_proof_ids tolerances residuals semantic_certificate_id').split())
RESIDUAL_FIELDS = set(('input_id trial_id effective_model_revision target_raw_potential measured_raw_potential '
    'amplitude_residual amplitude_tolerance timing_low timing_high within_timing within_amplitude').split())


def accepted_measurement_records(archive):
    by_id = {record['group_id']: record for record in archive['records']}
    require(len(by_id)==len(archive['records']),'composite_duplicate_measurement_group')
    references = [by_id[identity] for identity in archive['reference_group_ids']]
    finals = [by_id[identity] for identity in archive['final_group_ids']]
    return references,finals


def reference_amplitudes(package):
    """Read only after the complete package/archive audit at the call boundary."""
    references,_=accepted_measurement_records(package['measurement_archive'])
    return {record['logical_request']['input_id']:number(record['measurement']['raw_potential']) for record in references}


def audit_composite_certificate(package, archive_audit):
    certificate=package['certificate'];keys(certificate,FIELDS,'unknown_composite_training_certificate_fields')
    archive=package['measurement_archive'];protocol=package['protocol'];plan=package['runtime_plan'];n=len(protocol['inputs'])
    require(count(certificate['schema_version'])==2 and certificate['method_id']==METHOD and type(certificate['exact']) is bool,
            'unknown_composite_training_certificate_schema')
    require(certificate['semantic_certificate_id']==digest({key:value for key,value in certificate.items() if key!='semantic_certificate_id'}),
            'composite_certificate_semantic_digest')
    for field,value in [('model_revision',package['model_revision']),('model_epoch',package['model_epoch']),
            ('protocol_revision',protocol['revision']),('source_origin',archive['source_origin']),
            ('owner_family_binding',archive['owner_family_binding']),('reference_model_revision',package['capture_revision']),
            ('reference_model_epoch',package['capture_epoch'])]:
        _same(certificate[field],value)
    _same(certificate['tolerances'],plan['search']['tolerances'])
    references,finals=accepted_measurement_records(archive)
    require(len(references)==len(finals)==n,'composite_certificate_incomplete_all_input_verification')
    audits={row['group_id']:row for row in archive_audit['groups']}
    for record in references+finals:
        row=audits[record['group_id']]
        require(row['native_closure_recomputed'] and row['geometry_recomputed'] and row['measured'] and row['consumed']
                and record['training_requested_at_consume'] is True,'composite_certificate_unconsumed_or_unverified_group')
    _same(certificate['reference_semantic_proof_ids'],[record['measurement']['semantic_proof_id'] for record in references])
    _same(certificate['final_semantic_proof_ids'],[record['measurement']['semantic_proof_id'] for record in finals])
    for record in references:
        require(record['logical_request']['base_model_revision']==package['capture_revision']
                and count(record['logical_request']['model_epoch'])==count(package['capture_epoch']),
                'composite_certificate_reference_revision')
    for record in finals:
        require(record['logical_request']['base_model_revision']==package['model_revision']
                and count(record['logical_request']['model_epoch'])==count(package['model_epoch']),
                'composite_certificate_final_revision')
    residuals=certificate['residuals'];require(type(residuals) is list and len(residuals)==n,'composite_certificate_residual_dimension')
    by_input={}
    for residual in residuals:
        keys(residual,RESIDUAL_FIELDS,'composite_certificate_residual_fields')
        identity=residual['input_id'];require(type(identity) is str and identity not in by_input,'composite_certificate_duplicate_residual')
        by_input[identity]=residual
    require(set(by_input)=={value['id'] for value in protocol['inputs']},'composite_certificate_residual_input_inventory')
    absolute,relative,sync=(number(certificate['tolerances'][key]) for key in ('amplitude_absolute','amplitude_relative','sync'))
    require(min(absolute,relative,sync)>=0,'composite_certificate_negative_tolerance')
    anchor=finals[-1]['measurement'];exact=True
    for index,value in enumerate(protocol['inputs']):
        reference,current=references[index],finals[index];measured=current['measurement'];target=number(reference['measurement']['raw_potential'])
        raw=number(measured['raw_potential']);error=number(raw-target);tolerance=number(absolute+relative*abs(target))
        low=number(measured['arrival']-anchor['plateau_end']) if index+1!=n else 0.
        high=number(measured['plateau_end']-anchor['arrival']) if index+1!=n else 0.
        within_amplitude=abs(error)<=tolerance;within_timing=max(abs(low),abs(high))<=sync
        expected=dict(input_id=value['id'],trial_id=current['logical_request']['trial_id'],
            effective_model_revision=current['native_group']['specification']['effective_model_revision'],
            target_raw_potential=target,measured_raw_potential=raw,amplitude_residual=error,amplitude_tolerance=tolerance,
            timing_low=low,timing_high=high,within_timing=within_timing,within_amplitude=within_amplitude)
        _same(by_input[value['id']],expected);exact &= within_amplitude and within_timing
    require(certificate['exact'] is exact and (package['training_outcome']=='exact') is exact,
            'composite_certificate_exact_or_outcome_mismatch')
    return {'schema_version':2,'certificate_consistent':True,'semantic_certificate_id':certificate['semantic_certificate_id'],
            'exact':exact,'residuals_recomputed':n,'model_revision':package['model_revision'],
            'native_execution_verified':False,'native_import_verified':False,'evaluation_verdict':None}
