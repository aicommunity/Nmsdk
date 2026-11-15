"""Protocol5 certificate3 DATA math from independently replayed archive2.

This does not attest a producer's terminal state or recreate live authority.
A stopped boundary may contain enough accepted DATA for Exact residuals while
its public certificate must remain null. Pipeline classification needs the
original execution's exported package bytes/digest and source-case binding.
"""
import re

from .candidate_window_contract import METHOD
from .composite_certificate_evidence import FIELDS as CERTIFICATE2_FIELDS, accepted_measurement_records
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import count, number, require
from .response_domain_evidence import _same

FIELDS = CERTIFICATE2_FIELDS | {'protocol_binding','current_attempt_id','final_run_id',
                              'final_window_recipe_ids','final_measurement_instance_ids'}


def _serial(text, *, positive=False):
    require(type(text) is str and re.fullmatch(r'0|[1-9][0-9]*',text) is not None,
            'candidate_window_certificate_serial')
    result=count(int(text))
    require(not positive or result>0,'candidate_window_certificate_serial')
    return result


def _measurement(record, protocol):
    # The archive auditor has independently replayed these actual peaks and
    # native events from each retained full-before CSV, including omit/repeat.
    peak=record['selection']['geometry']['measured_maximum']
    index=protocol['stimulus_ids'].index(protocol['origin_stimulus_id'])
    origin=number(record['native_group']['traces'][0]['native_evidence']['observation']['stimuli'][index]['time'])
    value=dict(raw_potential=number(peak['raw_potential']),arrival=number(peak['time']-origin),
               plateau_end=number(peak['plateau_end']-origin))
    for key,actual in value.items():_same(record['measurement'][key],actual)
    _same(record['measurement']['actual_origin_time'],origin)
    return value


def replay_candidate_window_certificate(package, archive_audit):
    """Return recomputed certificate DATA or None for an incomplete allN set."""
    archive=package['measurement_archive'];protocol=package['protocol'];n=len(protocol['inputs'])
    require(count(protocol['schema_version'])==5 and count(archive['schema_version'])==2,
            'candidate_window_certificate_requires_protocol5_archive2')
    references,finals=accepted_measurement_records(archive)
    if len(references)!=n or len(finals)!=n:return None
    rows={row['group_id']:row for row in archive_audit['groups']}
    for index,(reference,current) in enumerate(zip(references,finals)):
        for record,purpose in ((reference,'reference'),(current,'final')):
            row=rows[record['group_id']]
            require(record['purpose']==purpose and count(record['logical_request']['input_index'])==index
                    and record['logical_request']['input_id']==protocol['inputs'][index]['id']
                    and row['native_closure_recomputed'] and row['geometry_recomputed'] and row['measured']
                    and row['consumed'] and record['training_requested_at_consume'] is True,
                    'candidate_window_certificate_unverified_all_input_set')
        require(reference['logical_request']['base_model_revision']==package['capture_revision']
                and count(reference['logical_request']['model_epoch'])==count(package['capture_epoch']),
                'candidate_window_certificate_reference_context')
    attempt=archive['current_attempt_id'];prefix=attempt+'/final/'
    observed=[r for r in archive['records'] if r['purpose']=='final' and r['attempt_id']==attempt]
    require(observed,'candidate_window_certificate_final_run_missing')
    for record in observed:
        require(record['logical_request']['run_id'].startswith(prefix),'candidate_window_certificate_final_namespace')
    latest=max(observed,key=lambda r:_serial(r['logical_request']['run_id'][len(prefix):]))['logical_request']['run_id']
    witness=None;previous=0
    order=range(n) if protocol['routing']=='classic_burst' else reversed(range(n))
    for index in order:
        record=finals[index];logical=record['logical_request'];proposal=record['window_proposal']
        serial=_serial(logical['trial_id'].rsplit('/',1)[-1],positive=True)
        require(record['attempt_id']==attempt and logical['run_id']==latest and serial>previous
                and logical['base_model_revision']==package['model_revision']
                and count(logical['model_epoch'])==count(package['model_epoch'])
                and record['method_specification']['coordinate_mode']=='candidate_frame'
                and proposal is not None and proposal['attempt_id']==attempt and proposal['run_id']==latest
                and proposal['protocol_binding']==digest(protocol), 'candidate_window_certificate_final_context')
        previous=serial;current=digest(record['candidate_binding'])
        if witness is None:witness=current
        require(current==witness and record['candidate_binding']['model_identity']['sha256']==package['model_revision'],
                'candidate_window_certificate_mixed_candidate')
    tolerances=package['runtime_plan']['search']['tolerances']
    absolute,relative,sync=(number(tolerances[k]) for k in ('amplitude_absolute','amplitude_relative','sync'))
    require(min(absolute,relative,sync)>=0,'candidate_window_certificate_negative_tolerance')
    measured=[_measurement(record,protocol) for record in finals];anchor=measured[-1];residuals=[];exact=True
    for index,(reference,current,value) in enumerate(zip(references,finals,measured)):
        target=number(reference['measurement']['raw_potential']);error=number(value['raw_potential']-target)
        tolerance=number(absolute+relative*abs(target))
        low=number(value['arrival']-anchor['plateau_end']) if index+1!=n else 0.
        high=number(value['plateau_end']-anchor['arrival']) if index+1!=n else 0.
        amplitude=abs(error)<=tolerance;timing=max(abs(low),abs(high))<=sync;exact &= amplitude and timing
        residuals.append(dict(input_id=protocol['inputs'][index]['id'],trial_id=current['logical_request']['trial_id'],
            effective_model_revision=current['native_group']['specification']['effective_model_revision'],
            target_raw_potential=target,measured_raw_potential=value['raw_potential'],amplitude_residual=error,
            amplitude_tolerance=tolerance,timing_low=low,timing_high=high,within_timing=timing,within_amplitude=amplitude))
    result=dict(schema_version=3,method_id=METHOD,exact=exact,model_revision=package['model_revision'],
        model_epoch=package['model_epoch'],protocol_revision=protocol['revision'],source_origin=archive['source_origin'],
        owner_family_binding=archive['owner_family_binding'],reference_model_revision=package['capture_revision'],
        reference_model_epoch=package['capture_epoch'],reference_semantic_proof_ids=[r['measurement']['semantic_proof_id'] for r in references],
        final_semantic_proof_ids=[r['measurement']['semantic_proof_id'] for r in finals],tolerances=tolerances,residuals=residuals,
        protocol_binding=digest(protocol),current_attempt_id=attempt,final_run_id=latest,
        final_window_recipe_ids=[r['window_proposal']['window_recipe_id'] for r in finals],
        final_measurement_instance_ids=[r['window_proposal']['measurement_instance_id'] for r in finals])
    return {**result,'semantic_certificate_id':digest(result)}


def audit_candidate_window_certificate(package, archive_audit):
    certificate=package['certificate'];keys(certificate,FIELDS,'candidate_window_certificate3_fields')
    require(count(certificate['schema_version'])==3 and type(certificate['exact']) is bool,
            'candidate_window_certificate3_schema')
    expected=replay_candidate_window_certificate(package,archive_audit)
    require(expected is not None,'candidate_window_certificate_incomplete_all_input_set')
    _same(certificate,expected)
    require(package['training_outcome']==('exact' if expected['exact'] else 'search_unresolved'),
            'candidate_window_certificate_outcome')
    return dict(schema_version=3,certificate_consistent=True,exact=expected['exact'],
        semantic_certificate_id=expected['semantic_certificate_id'],residuals_recomputed=len(expected['residuals']),
        relative_arrival_from_each_actual_origin=True,anchor_input_index=len(expected['residuals'])-1,
        latest_observed_final_sweep_checked=True,terminal_provenance_verified=False,
        native_execution_verified=False,native_import_verified=False,evaluation_verdict=None)
