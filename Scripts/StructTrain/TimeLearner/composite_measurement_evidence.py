"""Independent composite group replay from complete self-contained primary.

This checks data consistency. It never recovers a live lease from JSON or
attests Rdk execution. Partial groups remain insufficient, never negative
scientific evidence and never a substitute for a consumed measurement.
"""
import csv

from .composite_configuration import METHOD, validate_composite_protocol
from .composite_measurement_contract import (ARCHIVE_FIELDS, RECORD_FIELDS, LOGICAL_FIELDS,
    MEASUREMENT_FIELDS, SELECTION_FIELDS, BUDGET_FIELDS, ATTEMPT_LIMIT_FIELDS, COUNTER_FIELDS,
    CLOCK_FIELDS, PURPOSE, STATUS, integral_number_view, expected_semantic_measurement_id,
    expected_artifact_document_id)
from .composite_primary import capture_primary_blobs
from .composite_raw_evidence import audit_native_packets, audit_raw_trials
from .composite_source_evidence import keys, audit_source_binding, audit_candidate_binding
from .declared_window_basin_evidence import recompute_declared_basin_geometry, _geometry_dimensions
from .matched_omission_evidence import _trace
from .matched_omission_portable import audit_portable_matched_evidence
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, count, number, require
from .response_domain_evidence import _same, _text, _finite_json
from .training_capacitance_witness import audit_training_capacitance_registry


def _positive(value):
    value = count(value); require(value > 0, 'composite_positive_budget_required'); return value


def _budgets(record, primary_bytes):
    budget = record['budgets']; keys(budget, BUDGET_FIELDS, 'composite_record_budget_fields')
    attempt = budget['attempt_limits']; keys(attempt, ATTEMPT_LIMIT_FIELDS, 'composite_record_attempt_budget_fields')
    for key in ('maximum_groups', 'maximum_native_probes', 'maximum_total_samples'): _positive(attempt[key])
    for key in ('maximum_model_seconds', 'maximum_wall_seconds'):
        require(number(attempt[key]) > 0, 'composite_record_attempt_time_budget')
    for axis in ('model', 'wall'):
        value = number(budget['maximum_group_'+axis+'_seconds'])
        require(0 < value <= number(attempt['maximum_'+axis+'_seconds']), 'composite_record_group_time_budget')
    require(primary_bytes <= _positive(budget['maximum_total_primary_bytes']), 'composite_record_primary_budget')
    clock = record['clock_observation']; keys(clock, CLOCK_FIELDS, 'composite_record_clock_fields')
    for axis in ('model', 'wall'):
        begin, end = (number(clock[key+'_'+axis+'_time']) for key in ('start', 'end'))
        require(end >= begin, 'composite_record_nonmonotonic_clock')
    require(clock['wall_enforcement'] in ('live_checked_before_mint', 'not_completed'), 'composite_record_wall_enforcement')
    if record['measurement'] is not None:
        require(clock['wall_enforcement'] == 'live_checked_before_mint', 'composite_measurement_without_live_clock_record')


def _capacitance(record, source, issued, native_ids):
    witnesses, bindings = record['capacitance_witnesses'], record['native_trial_witness_ids']
    require(type(witnesses) is dict and type(bindings) is dict, 'composite_raw_C0_inventory')
    if source['optional_C0_witness'] is None:
        require(witnesses == bindings == {}, 'composite_raw_invented_C0')
        return None
    expected = {record['group_id']+'/native/'+str(i) for i in range(issued)}
    require(set(bindings) == expected and native_ids <= expected, 'composite_raw_C0_trial_inventory')
    require(set(witnesses) == set(bindings.values()), 'composite_raw_C0_missing_or_extra_witness')
    if not witnesses: return {'witnesses': 0, 'native_trials': 0}
    revision = record['logical_request']['base_model_revision']
    required = {key: revision for key in witnesses}
    audits = audit_training_capacitance_registry(witnesses, required)
    candidate = record['candidate_binding']['optional_C0_witness']
    for key, witness in witnesses.items():
        require(key == digest(witness), 'composite_raw_C0_witness_digest')
        _same(witness['model'], record['candidate_binding']['model_identity'])
        _same(witness['controller_parameters'], candidate['controller_parameters'])
    return {'witnesses': len(audits), 'native_trials': len(bindings), 'revision_kind': 'unmuted_base'}


def _complete(record, protocol, configuration, raw, packets, primary):
    portable = record['native_group']; logical = record['logical_request']; n = len(protocol['inputs'])
    spec = portable['specification']; assigned = count(logical['input_index'])
    channel = assigned if protocol['routing'] == 'classic_burst' else 0
    expected = dict(run_id=logical['run_id'], group_id=record['group_id'], sample_id=logical['sample_id'],
        protocol_revision=protocol['revision'], pattern_hash=protocol['pattern_hash'], input_id=logical['input_id'],
        base_model_revision=logical['base_model_revision'], model_epoch=logical['model_epoch'],
        assigned_input=assigned, channel=channel, routing=protocol['routing'], stimulus_ids=protocol['stimulus_ids'],
        stimulus_profile=protocol['stimulus_profile'], duration=configuration['duration'], minimum_amplitude=protocol['minimum_amplitude'])
    for key, value in expected.items(): _same(spec[key], value)
    require(len(portable['traces']) == len(raw) == len(packets) == n+2, 'composite_complete_N_plus_two_inventory')
    _same(portable['policy'], protocol['composite_measurement']['context_policy'])
    group = dict(group_id=record['group_id'], source_pattern_sha256=protocol['pattern_hash'], assigned_input=assigned,
        assigned_channel=channel, physical_channel_paths=spec['physical_channel_paths'], policy=portable['policy'])
    captured = {}; decoded = []
    for index, trace in enumerate(portable['traces']):
        packet = trace['native_evidence']; trial_id = packet['requested_specification']['trial_id']
        require(trial_id in raw and trial_id in packets, 'composite_complete_native_primary_missing')
        _same(packet, packets[trial_id]); actual = raw[trial_id]['trial']
        _same(actual['primary_ref'], dict(relative_path=trace['relative_path'], bytes=trace['bytes'], sha256=trace['sha256']))
        path = trace['relative_path']; require(path not in captured, 'composite_complete_primary_reused')
        captured[path] = primary[path]
        decoded.append(_trace(packet, dict(path=path, presented_ordinals=trace['presented_ordinals'], sha256=trace['sha256']),
                              primary[path], group, index, expected_input_id=logical['input_id']))
    audit_portable_matched_evidence(portable, captured)
    first, repeat = decoded[0], decoded[-1]
    require(spec['effective_model_revision'] == first['prepared']['effective_model_revision'], 'composite_complete_effective_revision')
    for trace in decoded:
        require(trace['packet']['current_base_revision'] == logical['base_model_revision'], 'composite_complete_base_revision')
    selection_spec = record['method_specification']
    window = protocol['composite_measurement']['input_windows'][assigned]
    _same(selection_spec, dict(schema_version=1, method_id=METHOD, group_id=record['group_id'], input_id=logical['input_id'],
                              assigned_input=assigned, channel=channel, window_begin_offset=window['begin_offset'], window_end_offset=window['end_offset']))
    _same(record['geometry_policy'], protocol['composite_measurement']['geometry_policy'])
    geometry_spec = dict(schema_version=1, input_count=n, assigned_input=assigned,
        window_begin=number(first['spec']['begin']+window['begin_offset']),
        window_end=number(first['spec']['begin']+window['end_offset']), minimum_amplitude=protocol['minimum_amplitude'])
    shape = lambda trace: dict(baseline=trace['baseline'][channel], raw=trace['raws'][channel])
    geometry = recompute_declared_basin_geometry(geometry_spec, record['geometry_policy'], first['times'],
        shape(first), shape(repeat), [(i, shape(trace)) for i, trace in enumerate(decoded[1:-1])])
    onset = first['packet']['observation']['stimuli'][assigned]['time']
    peak = geometry['measured_maximum']
    causal = geometry['validity'] == 'valid' and (peak['first_sample'] < first['event_frames'][assigned] or peak['time'] < onset)
    selection = record['selection']
    if selection is not None:
        keys(selection, SELECTION_FIELDS, 'composite_selection_fields')
        expected_selection = (dict(status='causality_rejected',status_enum=2,
            reasons=['basin_native_selected_peak_precedes_actual_assigned_event'], actual_assigned_onset=None, geometry=None)
            if causal else dict(status='completed',status_enum=1,reasons=[],actual_assigned_onset=onset,geometry=geometry))
        _same(selection, expected_selection)
        if selection['geometry'] is not None: _geometry_dimensions(selection['geometry'],len(first['times']),n)
    measurement = record['measurement']
    if measurement is not None:
        require(selection is not None and not causal and geometry['validity'] == 'valid', 'composite_invalid_geometry_promoted')
        keys(measurement, MEASUREMENT_FIELDS, 'composite_measurement_fields')
        _same(measurement['actual_peak'], peak)
        origin_index = protocol['stimulus_ids'].index(protocol['origin_stimulus_id'])
        origin = first['packet']['observation']['stimuli'][origin_index]['time']
        _same(measurement['raw_potential'], peak['raw_potential'])
        _same(measurement['arrival'], number(peak['time']-origin)); _same(measurement['plateau_end'], number(peak['plateau_end']-origin))
        _same(measurement['actual_origin_time'], origin)
        require(measurement['semantic_proof_id'] == expected_semantic_measurement_id(record,protocol), 'composite_semantic_proof_mismatch')
    return dict(native_closure_recomputed=True, geometry_recomputed=True, geometry_validity=geometry['validity'],
                selection_checked=selection is not None, measured=measurement is not None,
                primary_traces_checked=n+2, rejection_reason_recomputed=False)


def _record(record, protocol, configuration, source, origin, family, primary):
    keys(record, RECORD_FIELDS, 'unknown_composite_measurement_record_fields')
    require(record['kind'] == 'timelearner_composite_measurement' and count(record['schema_version']) == 1
            and record['purpose'] in PURPOSE and record['source_origin'] == origin and record['owner_family_binding'] == family,
            'composite_record_source_or_schema')
    for field in ('group_id', 'live_attempt_binding'): _text(record[field])
    require(record['group_state'] in ('idle','running','completed','rejected','cancelled','budget_exhausted')
            and type(record['complete_group']) is type(record['consumed']) is bool
            and (record['training_requested_at_consume'] is None or type(record['training_requested_at_consume']) is bool)
            and type(record['rejection_reason']) is str, 'composite_record_status_or_control')
    logical = record['logical_request']; keys(logical, LOGICAL_FIELDS, 'composite_logical_request_fields')
    index = count(logical['input_index']); n = len(protocol['inputs']); require(index < n, 'composite_logical_input_index')
    require(logical['input_id'] == protocol['inputs'][index]['id'] and logical['sample_id'] == protocol['sample_id']
            and logical['pattern_hash'] == protocol['pattern_hash'] and logical['protocol_revision'] == protocol['revision']
            and logical['routing'] == protocol['routing'], 'composite_logical_protocol_binding')
    for field in ('run_id','trial_id','base_model_revision'): _text(logical[field])
    attempt_id=_text(record['attempt_id'])
    from .composite_measurement_contract import validate_logical_namespace
    validate_logical_namespace(record)
    count(logical['model_epoch'])
    channel = index if protocol['routing'] == 'classic_burst' else 0
    window = protocol['composite_measurement']['input_windows'][index]
    _same(record['method_specification'],dict(schema_version=1,method_id=METHOD,group_id=record['group_id'],
        input_id=logical['input_id'],assigned_input=index,channel=channel,
        window_begin_offset=window['begin_offset'],window_end_offset=window['end_offset']))
    _same(record['geometry_policy'],protocol['composite_measurement']['geometry_policy'])
    audit_candidate_binding(record['candidate_binding'],record['candidate_witness_id'],logical,source,origin)
    packets = audit_native_packets(record['native_packets'])
    raw, retained, primary_bytes = audit_raw_trials(record,protocol,configuration,primary,packets)
    counters = record['counters']; keys(counters, COUNTER_FIELDS, 'composite_record_counter_fields')
    issued = count(counters['native_probes']); sampled = count(counters['sampled_frames'])
    require(issued <= n+2 and count(counters['retained_frames']) == retained and sampled >= retained
            and count(counters['primary_bytes']) == primary_bytes, 'composite_record_counter_units_or_bytes')
    allowed_ids = {record['group_id']+'/native/'+str(i) for i in range(issued)}
    require((set(raw) | set(packets)) <= allowed_ids, 'composite_record_observed_native_inventory')
    _budgets(record,primary_bytes)
    c0 = _capacitance(record,source,issued,set(raw)|set(packets))
    require(not record['consumed'] or (record['training_requested_at_consume'] is True and record['measurement'] is not None),
            'composite_record_consumed_without_request_or_measurement')
    if not record['complete_group']:
        require(record['native_group'] is None and record['measurement'] is None and record['consumed'] is False,
                'composite_partial_group_promoted')
        if record['selection'] is not None:
            selection=record['selection'];keys(selection,SELECTION_FIELDS,'composite_partial_selection_fields')
            require(selection['status'] in STATUS and count(selection['status_enum'])==STATUS[selection['status']]
                    and type(selection['reasons']) is list and all(type(v) is str and v for v in selection['reasons']),
                    'composite_partial_selection_status')
            if selection['actual_assigned_onset'] is not None:number(selection['actual_assigned_onset'])
            if selection['geometry'] is not None:
                require(bool(raw),'composite_partial_geometry_without_trace')
                first=next(iter(raw.values()));_geometry_dimensions(selection['geometry'],len(first['times']),n)
        result = dict(native_closure_recomputed=False,geometry_recomputed=False,measured=False,
            partial_syntax_checked=True,rejection_reason_recomputed=False,validity='insufficient_evidence')
    else:
        require(record['group_state'] == 'completed' and type(record['native_group']) is dict and issued == n+2
                and sampled == retained, 'composite_complete_group_state_or_frame_loss')
        result = _complete(record,protocol,configuration,raw,packets,primary)
    return {**result,'group_id':record['group_id'],'purpose':record['purpose'],'input_index':index,
            'attempt_id':attempt_id,
            'consumed':record['consumed'],'native_probes':issued,'sampled_frames':sampled,
            'retained_frames':retained,'primary_bytes':primary_bytes,'capacitance':c0,
            'native_execution_verified':False,'training_certificate_verified':False,'scientific_verdict':None}


def audit_composite_measurement_archive(document, configuration, *, runtime_plan=None, external_resolver=None):
    """Strict archive/index consistency; certificate and actual import are separate."""
    if type(document) is dict and document.get('schema_version') == 2:
        from .candidate_window_archive_evidence import audit_candidate_window_archive
        return audit_candidate_window_archive(document,configuration,runtime_plan=runtime_plan,external_resolver=external_resolver)
    try:
        keys(document,ARCHIVE_FIELDS,'unknown_composite_measurement_archive_fields'); _finite_json(document)
        require(document['kind']=='timelearner_composite_measurement_archive' and count(document['schema_version'])==1
                and document['method_id']==METHOD and document['artifact_document_sha256']==expected_artifact_document_id(document),
                'composite_archive_schema_or_document_digest')
        archive=integral_number_view(document); config=integral_number_view(configuration)
        protocol=archive['protocol']; validate_composite_protocol(protocol,config)
        source=audit_source_binding(archive['source_binding'],archive['source_origin'],config)
        _text(archive['owner_family_binding'])
        _text(archive['current_attempt_id'])
        require(type(archive['records']) is list, 'composite_archive_record_inventory')
        references=[]
        for record in archive['records']:
            keys(record,RECORD_FIELDS,'unknown_composite_measurement_record_fields')
            require(type(record['raw_trials']) is list,'composite_raw_trial_inventory')
            references += [trial['primary_ref'] for trial in record['raw_trials']]
        primary=capture_primary_blobs(archive['primary_blobs'],references,archive['maximum_total_primary_bytes'],external_resolver=external_resolver)
        if runtime_plan is not None:
            require(count(archive['maximum_total_primary_bytes'])==count(runtime_plan['composite_measurement']['maximum_total_primary_bytes'])
                    and archive['current_attempt_id']==runtime_plan['run_id'],'composite_archive_current_runtime_declaration')
        rows={}
        for record in archive['records']:
            result=_record(record,protocol,config,archive['source_binding'],archive['source_origin'],archive['owner_family_binding'],primary)
            require(result['group_id'] not in rows,'composite_archive_duplicate_group');rows[result['group_id']]=result
            if runtime_plan is not None and record['attempt_id']==archive['current_attempt_id']:
                policy=runtime_plan['composite_measurement']
                _same(record['budgets']['attempt_limits'],{**policy['attempt_limits'],
                    'maximum_model_seconds':runtime_plan['maximum_model_seconds'],'maximum_wall_seconds':runtime_plan['maximum_wall_seconds']})
                _same(record['budgets']['maximum_total_primary_bytes'],policy['maximum_total_primary_bytes'])
                for axis in ('model','wall'):
                    field='maximum_group_'+axis+'_seconds'
                    require(number(record['budgets'][field])<=number(policy[field]),'composite_current_group_limit_exceeds_declaration')
        for field,purpose in (('reference_group_ids','reference'),('final_group_ids','final')):
            ids=archive[field];require(type(ids) is list and len(ids)<=len(protocol['inputs']) and len(set(ids))==len(ids),
                                      'composite_archive_accepted_group_inventory')
            for index,identity in enumerate(ids):
                require(identity in rows and rows[identity]['purpose']==purpose and rows[identity]['input_index']==index
                        and rows[identity]['consumed'] and rows[identity]['measured'] and rows[identity]['native_closure_recomputed'],
                        'composite_archive_unverified_accepted_group')
        require(not set(archive['reference_group_ids']) & set(archive['final_group_ids']),'composite_archive_reference_final_overlap')
        final_ids = set(archive['final_group_ids'])
        final_records = [record for record in archive['records'] if record['group_id'] in final_ids]
        require(all(record['attempt_id'] == archive['current_attempt_id'] for record in final_records)
                and len({record['logical_request']['run_id'] for record in final_records}) <= 1,
                'composite_archive_final_generation_mixed')
        observed_final_runs = {record['logical_request']['run_id'] for record in archive['records']
            if record['purpose'] == 'final' and record['attempt_id'] == archive['current_attempt_id']}
        if final_records:
            # Namespaces were checked above. A recorded partial/rejected group
            # starts a newer sweep too; an unrecorded live intent is unknown.
            latest_run = max(observed_final_runs, key=lambda run: int(run.rsplit('/', 1)[1]))
            require(all(record['logical_request']['run_id'] == latest_run for record in final_records),
                    'composite_archive_final_generation_stale')
        counters=archive['counters'];keys(counters,{'attempt','archive'},'composite_archive_counter_fields')
        keys(counters['attempt'],{'logical_groups','native_probes','sampled_frames'},'composite_attempt_counter_fields')
        keys(counters['archive'],{'groups','native_probes','sampled_frames','primary_bytes'},'composite_archive_total_counter_fields')
        expected={'groups':len(rows),**{key:sum(row[key] for row in rows.values()) for key in ('native_probes','sampled_frames','primary_bytes')}}
        _same(counters['archive'],expected)
        current=[row for row in rows.values() if row['attempt_id']==archive['current_attempt_id']]
        expected_attempt={'logical_groups':len(current),**{key:sum(row[key] for row in current) for key in ('native_probes','sampled_frames')}}
        _same(counters['attempt'],expected_attempt)
        return {'reader_version':1,'method_id':METHOD,'source':source,'groups':list(rows.values()),
                'archive_counters_recomputed':True,'attempt_membership_recomputed':True,
                'current_runtime_budget_binding_checked':runtime_plan is not None,
                'primary_files_checked':len(primary),'primary_bytes':sum(len(raw) for raw in primary.values()),
                'artifact_document_sha256':archive['artifact_document_sha256'],'native_execution_verified':False,
                'live_authority_restored':False,'training_certificate_verified':False,'scientific_verdict':None}
    except EvidenceError: raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,UnicodeError,OverflowError,OSError,csv.Error) as error:
        raise EvidenceError('malformed_composite_measurement_archive') from error
