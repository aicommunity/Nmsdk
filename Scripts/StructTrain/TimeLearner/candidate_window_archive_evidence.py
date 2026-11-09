"""Independent archive2 DATA replay, never a restored live Train authority.

The schema1 reader remains separate. This layer accepts only cold7/protocol5
declarations and replays primary, graph features and reference-anchored windows.
Package6/certificate3/CLI admission are outside this DATA reader.
"""
import csv

from .candidate_window_contract import (METHOD, bounded_count, hash_id,
    validate_protocol, validate_proposal_data, validate_specification, expected_measurement_id)
from .candidate_window_binding_evidence import audit_candidate_binding2, reference_seed, replay_proposal
from .composite_measurement_contract import (ARCHIVE_FIELDS, RECORD_FIELDS, LOGICAL_FIELDS,
    COUNTER_FIELDS, MEASUREMENT_FIELDS, SELECTION_FIELDS, PURPOSE, integral_number_view,
    expected_artifact_document_id, validate_logical_namespace)
from .composite_measurement_evidence import _budgets, _capacitance
from .composite_primary import capture_primary_blobs
from .composite_raw_evidence import audit_native_packets, audit_raw_trials
from .composite_source_evidence import keys, audit_source_binding
from .declared_window_basin_evidence import recompute_declared_basin_geometry
from .matched_omission_evidence import _trace
from .matched_omission_portable import audit_portable_matched_evidence, _presented, _canonical_csv
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, count, number, require
from .response_domain_evidence import _same, _text, _finite_json

RECORD2_FIELDS = RECORD_FIELDS | {'window_proposal'}


def _geometry(record, protocol, decoded):
    """Project a declared frame only onto retained ACTUAL timestamps."""
    first, repeat = decoded[0], decoded[-1]
    spec = record['method_specification']; channel = count(spec['channel'])
    if spec['coordinate_mode'] == 'reference_time':
        window = spec['reference_time']
        require(type(record['native_group']) is dict,'candidate_window_geometry_requires_closed_group')
        duration=number(record['native_group']['specification']['duration'])
        if not 0<=number(window['begin_offset'])<number(window['end_offset'])<=duration:
            return dict(status='rejected',status_enum=0,reasons=['basin_native_method_or_window_binding_changed'],
                        actual_assigned_onset=None,geometry=None)
        begin = number(first['spec']['begin'] + window['begin_offset'])
        end = number(first['spec']['begin'] + window['end_offset'])
    else:
        frame = spec['candidate_frame']; left, right = (count(frame[k]) for k in ('first_frame','last_frame'))
        if right >= len(first['times']):
            return dict(status='rejected', status_enum=0, reasons=['window_frames_not_captured'],
                        actual_assigned_onset=None, geometry=None)
        begin, end = first['times'][left], first['times'][right]
    geometry_spec = dict(schema_version=1, input_count=len(protocol['inputs']), assigned_input=spec['assigned_input'],
        window_begin=begin, window_end=end, minimum_amplitude=protocol['minimum_amplitude'])
    def shape(trace): return dict(baseline=trace['baseline'][channel], raw=trace['raws'][channel])
    geometry = recompute_declared_basin_geometry(geometry_spec, record['geometry_policy'], first['times'],
        shape(first), shape(repeat), [(i,shape(trace)) for i,trace in enumerate(decoded[1:-1])])
    assigned = count(spec['assigned_input']); onset = first['packet']['observation']['stimuli'][assigned]['time']
    peak = geometry['measured_maximum']
    if geometry['validity']=='valid' and (peak['first_sample']<first['event_frames'][assigned] or peak['time']<onset):
        return dict(status='causality_rejected',status_enum=2,
            reasons=['basin_native_selected_peak_precedes_actual_assigned_event'],actual_assigned_onset=None,geometry=None)
    return dict(status='completed',status_enum=1,reasons=[],actual_assigned_onset=onset,geometry=geometry)


def _complete(record, protocol, source, raw, packets, primary):
    portable=record['native_group'];logical=record['logical_request'];n=len(protocol['inputs'])
    spec=portable['specification'];assigned=count(logical['input_index']);channel=assigned if protocol['routing']=='classic_burst' else 0
    expected=dict(run_id=logical['run_id'],group_id=record['group_id'],sample_id=logical['sample_id'],
        protocol_revision=protocol['revision'],pattern_hash=protocol['pattern_hash'],input_id=logical['input_id'],
        base_model_revision=logical['base_model_revision'],model_epoch=logical['model_epoch'],assigned_input=assigned,
        channel=channel,routing=protocol['routing'],stimulus_ids=protocol['stimulus_ids'],
        stimulus_profile=protocol['stimulus_profile'],minimum_amplitude=protocol['minimum_amplitude'])
    for key,value in expected.items():_same(spec[key],value)
    require(spec['reset_binding']=='native-neuron-dataset-reset-before-children-v1',
            'candidate_window_native_reset_binding')
    _same(portable['source']['planned_isi'],source['applied_source_isi'])
    for axis in ('model','wall'):
        _same(portable['time_budget']['maximum_'+axis+'_seconds'],record['budgets']['maximum_group_'+axis+'_seconds'])
    require(len(portable['traces'])==len(raw)==len(packets)==n+2,'candidate_window_complete_N_plus_two_inventory')
    _same(portable['policy'],protocol['composite_measurement']['context_policy'])
    group=dict(group_id=record['group_id'],source_pattern_sha256=protocol['pattern_hash'],assigned_input=assigned,
        assigned_channel=channel,physical_channel_paths=spec['physical_channel_paths'],policy=portable['policy'])
    captured={};decoded=[]
    for i,trace in enumerate(portable['traces']):
        packet=trace['native_evidence'];trial=packet['requested_specification']['trial_id']
        require(trial==record['group_id']+'/native/'+str(i) and trial in raw and trial in packets
            and list(packets)[i]==trial,'candidate_window_complete_primary_missing_or_order')
        _same(packet,packets[trial])
        path=trace['relative_path'];require(path not in captured,'candidate_window_complete_primary_reused')
        _same(raw[trial]['trial']['primary_ref'],dict(relative_path=path,bytes=trace['bytes'],sha256=trace['sha256']))
        captured[path]=primary[path]
        decoded.append(_trace(packet,dict(path=path,presented_ordinals=trace['presented_ordinals'],sha256=trace['sha256']),
            primary[path],group,i,expected_input_id=logical['input_id']))
    # Full source/mask/grid/event/model/reset/repeat/chronology replay, including
    # the old diagnostic assignment. Its validity never admits this new method.
    audit_portable_matched_evidence(portable,captured)
    first=decoded[0]
    require(spec['effective_model_revision']==first['prepared']['effective_model_revision'] and
        all(t['packet']['current_base_revision']==logical['base_model_revision'] for t in decoded),
        'candidate_window_complete_revision_binding')
    actual=_geometry(record,protocol,decoded)
    if record['selection'] is not None:
        keys(record['selection'],SELECTION_FIELDS,'candidate_window_selection_fields');_same(record['selection'],actual)
    measurement=record['measurement']
    if measurement is not None:
        require(record['group_state']=='completed','candidate_window_measurement_without_completed_state')
        require(record['selection'] is not None and actual['status']=='completed' and actual['geometry']['validity']=='valid',
                'candidate_window_invalid_geometry_promoted')
        keys(measurement,MEASUREMENT_FIELDS,'candidate_window_measurement_fields')
        peak=actual['geometry']['measured_maximum'];_same(measurement['actual_peak'],peak)
        origin_index=protocol['stimulus_ids'].index(protocol['origin_stimulus_id'])
        origin=first['packet']['observation']['stimuli'][origin_index]['time']
        _same(measurement['raw_potential'],peak['raw_potential']);_same(measurement['actual_origin_time'],origin)
        _same(measurement['arrival'],number(peak['time']-origin));_same(measurement['plateau_end'],number(peak['plateau_end']-origin))
        require(measurement['semantic_proof_id']==expected_measurement_id(record,protocol),'candidate_window_semantic_proof_mismatch')
    return dict(native_closure_recomputed=True,geometry_recomputed=actual['geometry'] is not None,
        geometry_validity=None if actual['geometry'] is None else actual['geometry']['validity'],
        measured=measurement is not None,selection_checked=record['selection'] is not None,
        primary_traces_checked=n+2,rejection_reason_recomputed=record['selection'] is not None)


def _record(record, protocol, configuration, source, origin, family, primary):
    keys(record,RECORD2_FIELDS,'candidate_window_record2_fields')
    require(record['kind']=='timelearner_composite_measurement' and count(record['schema_version'])==2
        and record['purpose'] in PURPOSE and record['source_origin']==origin and record['owner_family_binding']==family,
        'candidate_window_record_source_or_schema')
    for key in ('group_id','live_attempt_binding','attempt_id'):_text(record[key])
    require(record['group_state'] in ('idle','running','completed','rejected','cancelled','budget_exhausted')
        and type(record['complete_group']) is type(record['consumed']) is bool
        and (record['training_requested_at_consume'] is None or type(record['training_requested_at_consume']) is bool)
        and type(record['rejection_reason']) is str,'candidate_window_record_status_or_control')
    logical=record['logical_request'];keys(logical,LOGICAL_FIELDS,'candidate_window_logical_fields')
    index=count(logical['input_index']);n=len(protocol['inputs']);require(index<n,'candidate_window_logical_input_index')
    require(logical['input_id']==protocol['inputs'][index]['id'] and logical['sample_id']==protocol['sample_id']
        and logical['pattern_hash']==protocol['pattern_hash'] and logical['protocol_revision']==protocol['revision']
        and logical['routing']==protocol['routing'],'candidate_window_logical_protocol_binding')
    for key in ('run_id','trial_id'):_text(logical[key])
    hash_id(logical['base_model_revision']);count(logical['model_epoch']);validate_logical_namespace(record)
    validate_specification(record['method_specification'],protocol,logical,record['group_id'],record['purpose'])
    if record['purpose']=='reference':require(record['window_proposal'] is None,'candidate_window_reference_has_proposal')
    else:validate_proposal_data(record['window_proposal'])
    _same(record['geometry_policy'],protocol['composite_measurement']['geometry_policy'])
    facts=audit_candidate_binding2(record['candidate_binding'],record['candidate_witness_id'],logical,source,origin,protocol)
    packets=audit_native_packets(record['native_packets']);native=record['native_group']
    # A partial duration is only a recorder declaration, never a closure claim.
    duration=native['specification']['duration'] if native is not None else configuration['duration']
    policy=protocol['composite_measurement']['context_policy']
    raw,retained,primary_bytes=audit_raw_trials(record,protocol,configuration,primary,packets,
        maximum_samples_limit=policy['maximum_samples'],declared_duration=duration,ordinal_stimulus_ids=protocol['stimulus_ids'],
        partial_duration_unbound=native is None,actual_event_frame_interval=True)
    for trace in raw.values():
        _canonical_csv(primary[trace['trial']['primary_ref']['relative_path']],len(trace['baseline']))
        require(trace['spec']['pattern_hash']==digest(_presented(source['applied_source_isi'],trace['mask'])),
                'candidate_window_raw_presented_pattern')
    counters=record['counters'];keys(counters,COUNTER_FIELDS,'candidate_window_record_counter_fields')
    issued=count(counters['native_probes']);sampled=count(counters['sampled_frames'])
    require(issued<=n+2 and sampled==retained==count(counters['retained_frames'])
        and sampled<=count(policy['maximum_total_samples']) and primary_bytes==count(counters['primary_bytes']),
        'candidate_window_retained_sample_charge')
    allowed={record['group_id']+'/native/'+str(i) for i in range(issued)}
    require((set(raw)|set(packets))<=allowed,'candidate_window_observed_native_inventory')
    _budgets(record,primary_bytes);limits=record['budgets']['attempt_limits']
    require(record['clock_observation']['wall_enforcement']==('not_completed' if record['measurement'] is None else 'live_checked_before_mint'),
            'candidate_window_clock_record_identity')
    require(count(limits['maximum_native_probes'])>=n+2 and issued<=count(limits['maximum_native_probes'])
        and sampled<=count(limits['maximum_total_samples']),'candidate_window_record_attempt_budget')
    c0=_capacitance(record,source,issued,set(raw)|set(packets))
    require(not record['consumed'] or (record['training_requested_at_consume'] is True and record['measurement'] is not None),
            'candidate_window_consumed_without_request_or_measurement')
    if not record['complete_group']:
        require(native is None and record['measurement'] is None and record['consumed'] is False
            and record['group_state']!='completed','candidate_window_partial_promoted')
        if record['selection'] is not None:
            selection=record['selection'];keys(selection,SELECTION_FIELDS,'candidate_window_partial_selection_fields')
            require(selection['status']=='rejected' and count(selection['status_enum'])==0 and selection['geometry'] is None
                and selection['actual_assigned_onset'] is None and type(selection['reasons']) is list
                and all(type(v) is str and v for v in selection['reasons']),'candidate_window_partial_selection_claim')
        result=dict(native_closure_recomputed=False,geometry_recomputed=False,measured=False,
                    partial_syntax_checked=True,rejection_reason_recomputed=False,validity='insufficient_evidence')
    else:
        require(type(native) is dict and issued==n+2,'candidate_window_complete_group_state')
        result=_complete(record,protocol,source,raw,packets,primary)
    return {**result,'group_id':record['group_id'],'purpose':record['purpose'],'input_index':index,
        'attempt_id':record['attempt_id'],'consumed':record['consumed'],'native_probes':issued,'sampled_frames':sampled,
        'retained_frames':retained,'primary_bytes':primary_bytes,'capacitance':c0,'candidate_facts':facts,
        'native_execution_verified':False,'training_certificate_verified':False,'scientific_verdict':None}


def _ledger(archive, rows):
    """Declared append order and retained-prefix caps, not a global time proof."""
    current=archive['current_attempt_id'];caps={};limits={};totals={};blocks=set();block=None;ordinal={};seen=set();prefix=0
    cap=bounded_count(archive['maximum_total_primary_bytes'],positive=True)
    for record,row in zip(archive['records'],rows):
        attempt=record['attempt_id'];budget=record['budgets'];value=count(budget['maximum_total_primary_bytes'])
        if block!=attempt:
            require(attempt not in blocks,'candidate_window_reopened_attempt_block');blocks.add(attempt);block=attempt
        number_=bounded_count(int(record['group_id'].rsplit('/',1)[1]),positive=True)
        require(number_>ordinal.get(attempt,0),'candidate_window_group_append_order');ordinal[attempt]=number_
        if record['purpose']!='reference':
            require(archive['reference_group_ids'] and set(archive['reference_group_ids'])<=seen,
                    'candidate_window_candidate_precedes_references')
        seen.add(record['group_id'])
        require(attempt not in caps or caps[attempt]==value,'candidate_window_attempt_primary_cap_changed');caps[attempt]=value
        require(attempt not in limits or limits[attempt]==budget['attempt_limits'],'candidate_window_attempt_limits_changed')
        limits[attempt]=budget['attempt_limits']
        total=totals.setdefault(attempt,dict(groups=0,native=0,samples=0,bytes=0))
        for key,amount in [('groups',1),('native',row['native_probes']),('samples',row['sampled_frames']),('bytes',row['primary_bytes'])]:
            total[key]=bounded_count(total[key]+amount)
        prefix=bounded_count(prefix+row['primary_bytes'])
        require(total['bytes']<=value and prefix<=value,'candidate_window_historical_primary_budget')
        limit=limits[attempt]
        require(total['groups']<=count(limit['maximum_groups']) and total['native']<=count(limit['maximum_native_probes'])
            and total['samples']<=count(limit['maximum_total_samples']),'candidate_window_cumulative_attempt_budget')
        if attempt==current:require(value==cap,'candidate_window_current_primary_cap')
    require((current not in blocks or block==current) and prefix<=cap,'candidate_window_current_retained_budget_or_order')


def _accepted(archive, rows, protocol):
    by_id={r['group_id']:r for r in archive['records']};audits={r['group_id']:r for r in rows};n=len(protocol['inputs'])
    references=[]
    for field,purpose in (('reference_group_ids','reference'),('final_group_ids','final')):
        ids=archive[field];require(type(ids) is list and len(ids)<=n and all(type(v) is str for v in ids)
            and len(set(ids))==len(ids),'candidate_window_accepted_inventory')
        previous=-1
        for position,identity in enumerate(ids):
            require(identity in by_id,'candidate_window_missing_accepted_group');record=by_id[identity];row=audits[identity]
            index=row['input_index']
            require(row['purpose']==purpose and row['consumed'] and row['measured'] and row['native_closure_recomputed']
                and record['training_requested_at_consume'] is True and index>previous,
                'candidate_window_unverified_accepted_group');previous=index
            if purpose=='reference':
                require(index==position,'candidate_window_reference_order');references.append(record)
    require(not set(archive['reference_group_ids'])&set(archive['final_group_ids']),'candidate_window_reference_final_overlap')
    finals=[by_id[i] for i in archive['final_group_ids']]
    if finals:
        require(len(references)==n,'candidate_window_final_without_complete_references')
        runs={r['logical_request']['run_id'] for r in finals};signatures={digest(r['candidate_binding']) for r in finals}
        revisions={(r['logical_request']['base_model_revision'],count(r['logical_request']['model_epoch'])) for r in finals}
        require(len(runs)==len(signatures)==len(revisions)==1 and all(r['attempt_id']==archive['current_attempt_id'] for r in finals),
                'candidate_window_final_generation_mixed')
        observed=[r['logical_request']['run_id'] for r in archive['records']
            if r['purpose']=='final' and r['attempt_id']==archive['current_attempt_id']]
        latest=max(observed,key=lambda v:int(v.rsplit('/',1)[1]))
        require(next(iter(runs))==latest,'candidate_window_final_generation_stale')
    if len(references)!=n:
        require(not references and all(r['purpose']=='reference' and r['window_proposal'] is None and not r['consumed']
            for r in archive['records']),'candidate_window_partial_reference_set_promoted')
        return []
    seeds=[reference_seed(r,archive['source_binding'],protocol) for r in references]
    for seed in seeds[1:]:
        for field in ('grid','initial_parameters','initial_capacitance'):_same(seed[field],seeds[0][field])
    require(len({r['measurement']['semantic_proof_id'] for r in references})==n
        and len({digest(r['candidate_binding']) for r in references})==1,'candidate_window_reference_family_mixed')
    return references


def audit_candidate_window_archive(document, configuration, *, runtime_plan=None, external_resolver=None):
    """Audit archived DATA; no bool/hash/wrapper becomes live authority."""
    try:
        keys(document,ARCHIVE_FIELDS,'candidate_window_archive_fields');_finite_json(document)
        require(document['kind']=='timelearner_composite_measurement_archive' and count(document['schema_version'])==2
            and document['method_id']==METHOD and document['artifact_document_sha256']==expected_artifact_document_id(document),
            'candidate_window_archive_schema_or_digest')
        archive=integral_number_view(document);configuration=integral_number_view(configuration);protocol=archive['protocol']
        common=validate_protocol(protocol,configuration)
        source=audit_source_binding(archive['source_binding'],archive['source_origin'],common)
        hash_id(archive['source_origin']);hash_id(archive['owner_family_binding']);_text(archive['current_attempt_id'])
        require(type(archive['records']) is list,'candidate_window_record_inventory')
        refs=[]
        for record in archive['records']:
            keys(record,RECORD2_FIELDS,'candidate_window_record2_fields')
            require(type(record['raw_trials']) is list,'candidate_window_raw_inventory')
            refs.extend(trial['primary_ref'] for trial in record['raw_trials'])
        primary=capture_primary_blobs(archive['primary_blobs'],refs,archive['maximum_total_primary_bytes'],external_resolver=external_resolver)
        rows=[];groups=set();trials=set();proofs=set()
        for record in archive['records']:
            row=_record(record,protocol,common,archive['source_binding'],archive['source_origin'],archive['owner_family_binding'],primary)
            trial=record['logical_request']['trial_id'];proof=None if record['measurement'] is None else record['measurement']['semantic_proof_id']
            require(record['group_id'] not in groups and trial not in trials and (proof is None or proof not in proofs),
                    'candidate_window_replayed_group_trial_or_proof')
            groups.add(record['group_id']);trials.add(trial)
            if proof is not None:hash_id(proof);proofs.add(proof)
            rows.append(row)
        _ledger(archive,rows);references=_accepted(archive,rows,protocol)
        if references:
            maximum=count(protocol['composite_measurement']['context_policy']['maximum_samples'])
            for record,row in zip(archive['records'],rows):
                if record['purpose']=='reference':continue
                raw=record['raw_trials'];declared=(count(raw[0]['actual_specification']['maximum_samples']) if raw
                    else count(record['window_proposal']['candidate']['declared_maximum_samples']))
                require(3<=declared<=maximum and all(count(r['actual_specification']['maximum_samples'])==declared for r in raw),
                        'candidate_window_declared_sample_budget')
                replay_proposal(record,protocol,archive['source_binding'],references,row['candidate_facts'],declared)
                row['proposal_recomputed']=True
        if runtime_plan is not None:
            require(type(runtime_plan) is dict and archive['current_attempt_id']==runtime_plan['run_id'],
                    'candidate_window_runtime_attempt_binding')
            validate_protocol(protocol,integral_number_view(runtime_plan))
            policy=runtime_plan['composite_measurement']
            _same(policy['candidate_window_policy'],protocol['composite_measurement']['candidate_window_policy'])
            require(count(policy['schema_version'])==2 and count(policy['maximum_total_primary_bytes'])==count(archive['maximum_total_primary_bytes']),
                    'candidate_window_runtime_policy_or_budget')
            for record in archive['records']:
                if record['attempt_id']!=archive['current_attempt_id']:continue
                _same(record['budgets']['attempt_limits'],{**policy['attempt_limits'],
                    'maximum_model_seconds':runtime_plan['maximum_model_seconds'],'maximum_wall_seconds':runtime_plan['maximum_wall_seconds']})
                for axis in ('model','wall'):
                    field='maximum_group_'+axis+'_seconds'
                    require(number(record['budgets'][field])<=number(policy[field]),'candidate_window_current_group_budget')
        counters=archive['counters'];keys(counters,{'attempt','archive'},'candidate_window_archive_counter_fields')
        totals=dict(groups=len(rows),**{k:sum(r[k] for r in rows) for k in ('native_probes','sampled_frames','primary_bytes')})
        current=[r for r in rows if r['attempt_id']==archive['current_attempt_id']]
        current_totals=dict(logical_groups=len(current),**{k:sum(r[k] for r in current) for k in ('native_probes','sampled_frames')})
        _same(counters['archive'],totals);_same(counters['attempt'],current_totals)
        for row in rows:row.pop('candidate_facts')
        return dict(reader_version=2,method_id=METHOD,source=source,groups=rows,reference_set_recomputed=bool(references),
            archive_counters_recomputed=True,attempt_membership_recomputed=True,retained_prefix_budgets_recomputed=True,
            current_runtime_budget_binding_checked=runtime_plan is not None,primary_files_checked=len(primary),
            primary_bytes=totals['primary_bytes'],artifact_document_sha256=archive['artifact_document_sha256'],
            native_execution_verified=False,live_authority_restored=False,training_certificate_verified=False,scientific_verdict=None)
    except EvidenceError:raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,UnicodeError,OverflowError,OSError,csv.Error) as error:
        raise EvidenceError('malformed_candidate_window_archive') from error
