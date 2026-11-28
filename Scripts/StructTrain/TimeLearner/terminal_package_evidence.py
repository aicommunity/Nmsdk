"""Audit package8 actual model separately from its historical measurement proof.

This DATA audit grants neither native import nor execution authority. A stopped
measured selection is not an all-input certificate or a recognition verdict.
"""
import copy

from .capacitance_evidence import _images, audit_capacitance_state
from .composite_source_evidence import audit_identity, audit_snapshot, keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, audit_probe, count, number, require
from .response_domain_evidence import _finite_json, _same
from .training_capacitance_witness import validate_graph_input_parameters

FIELDS = set(('kind schema_version dynamic_checkpoint state_kind implementation_id controller_version '
    'calculate_mode structure_build_mode configuration protocol trained_inputs model_revision model_epoch '
    'session_attempt training_outcome reason certificate historical_state terminal_policy terminal_event '
    'terminal_journal dataset neuron capacitance_state sha256').split())
SUMMARY_FIELDS = set(('kind schema_version state outcome reason actual_model_revision model_epoch '
    'transcript_model_epoch parameters session_attempt certificate terminal_policy terminal_event terminal_journal '
    'closed_boundary controller_checkpoint restored_live_authority historical_summary sha256').split())
EVENT_FIELDS = set(('kind schema_version stopped_outcome stopped_reason session_attempt portable_export_supported '
    'fresh_all_input_verification certificate search_terminal_epoch search_terminal_revision search_terminal_parameters '
    'selected edit_budget selected_probe_packets status reason native_transactions wall_seconds actual_model_epoch '
    'historical_measurements_rebound_to_actual_epoch sha256').split())
EVENT_OPTIONAL = set(('source_neuron_identity source_dataset_identity source_capacitance_state '
    'rollback_attempted rollback_succeeded actual_model_revision actual_parameters').split())


def _digest(value):
    require(type(value) is dict and value.get('sha256') == digest({k:v for k,v in value.items() if k!='sha256'}),
            'terminal_digest_mismatch')


def _policy(value):
    if value is None:
        return
    from .terminal_configuration import validate_terminal_policy
    validate_terminal_policy(value)


def _summary(summary, package):
    keys(summary, SUMMARY_FIELDS, 'terminal_summary_fields')
    _digest(summary)
    require(summary['kind']=='native_training_state_summary' and count(summary['schema_version'])==9
            and summary['state']=='finished' and summary['closed_boundary'] is True
            and summary['controller_checkpoint'] is False and summary['restored_live_authority'] is False,
            'terminal_summary_not_closed_DATA')
    for field, target in [('outcome','training_outcome'),('reason','reason'),('actual_model_revision','model_revision'),
                          ('model_epoch','model_epoch'),('parameters','trained_inputs'),('session_attempt','session_attempt'),
                          ('certificate','certificate'),('terminal_policy','terminal_policy'),
                          ('terminal_event','terminal_event'),('terminal_journal','terminal_journal')]:
        _same(summary[field],package[target])
    _same(summary['transcript_model_epoch'],package['historical_state']['model_epoch'])
    require(type(summary['historical_summary']) is dict, 'terminal_historical_summary_missing')
    return summary['historical_summary']


def _source(package, historical_summary, packets, traces, external_resolver):
    historical=package['historical_state'];version=count(historical['schema_version'])
    require(1<=version<=7, 'terminal_recursive_historical_state')
    for field in ('kind','state_kind','implementation_id','controller_version','calculate_mode','structure_build_mode',
                  'configuration','protocol','session_attempt','training_outcome','certificate'):
        _same(package[field],historical[field])
    require(type(package['reason']) is str,'terminal_package_reason')
    if 'reason' in historical:_same(package['reason'],historical['reason'])
    if version in (5,6,7):
        from .composite_package_evidence import audit_composite_package
        require(not packets and not traces, 'terminal_composite_legacy_primary_overlay')
        return audit_composite_package(historical,historical_summary,external_resolver=external_resolver)
    require(historical_summary is not None, 'terminal_plain_historical_summary_required')
    from .stopped_evidence import audit_stopped_state
    from .learned_evidence import audit_learned_state
    # Warm attempts retain earlier transition evidence separately. Pass exactly
    # the original attempt's primary to the existing reader, without fabricating
    # a summary, silently dropping a required trial or rebinding an epoch.
    ids=_plain_source_ids(historical,historical_summary,packets)
    require(ids<=set(packets) and ids<=set(traces), 'terminal_historical_primary_missing')
    reader=audit_stopped_state if historical['kind']=='timelearner_stopped_state' else audit_learned_state
    return reader(historical,historical_summary,{k:packets[k] for k in ids},{k:traces[k] for k in ids})


def _plain_source_ids(historical, summary, packets):
    if historical['kind']=='timelearner_stopped_state':
        return {p['requested_specification']['trial_id'] for p in
                historical['observed_packets']+historical['reference_packets']+historical['final_packets']}
    embedded=historical['reference_packets']+historical['final_packets']
    ids={p['requested_specification']['trial_id'] for p in embedded}
    run=summary['configuration']['run_id']
    require(type(run) is str and bool(run),'terminal_historical_run_missing')
    # Namespace selects original current-attempt raw trials, including rejected
    # candidates. Their completeness is checked by the existing summary reader.
    ids.update(trial for trial,p in packets.items() if p['requested_specification']['run_id']==run or
               p['requested_specification']['run_id'].startswith(run+'/'))
    return ids


def _historical_capacitance(historical):
    # Original plain schema1 has no C0 field. This is a known wire contract,
    # not a recovered physical baseline or permission to omit newer evidence.
    if count(historical['schema_version']) == 1:
        require('capacitance_state' not in historical, 'terminal_unversioned_legacy_C0')
        return None
    require('capacitance_state' in historical, 'terminal_historical_C0_field_missing')
    return historical['capacitance_state']


def _physical(package):
    historical=package['historical_state'];archive=package['neuron'];old=historical['neuron']
    require(archive.get('kind')=='timelearner_model_archive' and count(archive['schema_version'])==2,
            'terminal_physical_archive_schema')
    _digest(archive);audit_snapshot(archive['graph']);identity=archive['graph']['identity'];audit_identity(identity)
    _same(identity['sha256'],package['model_revision'])
    _same(_images(archive['class_definitions']),_images(old['class_definitions']))
    validate_graph_input_parameters(package['configuration']['model'],identity,package['trained_inputs'])
    audit_snapshot(package['dataset'],dataset=True)
    _same(package['dataset']['identity'],historical['dataset']['identity'])
    expected=copy.deepcopy(old['metadata'])
    paths=[row['cached_ltzone'] for row in identity['model']['caches'] if row.get('cached_ltzone')]
    require(paths, 'terminal_ltzone_missing')
    from .recognition_evidence import _physical as physical_number
    nodes={node['path']:node for node in identity['model']['nodes']}
    expected['calibration']['ltzone_path']=paths[0]
    expected['calibration']['threshold']=physical_number(nodes[paths[0]],'Threshold')
    event=package['terminal_event'];journal=package['terminal_journal']
    expected['terminal_event_sha256']=event['sha256'] if event is not None else None
    expected['terminal_journal_sha256']=digest({'entries':journal})
    _same(archive['metadata'],expected)
    state=package['capacitance_state'];previous=_historical_capacitance(historical)
    require((state is None)==(previous is None), 'terminal_C0_lost_or_invented')
    if state is None:
        return None
    result=audit_capacitance_state(state,state['baseline']['model_spec'],identity,archive['class_definitions'])
    for field in ('model_spec','model_revision','capture_model','storage_images_sha256'):
        _same(state['baseline'][field],previous['baseline'][field])
    _same(state['maximum_relative_change'],previous['maximum_relative_change'])
    return result


def _selected(event, package, source_audit, packets, traces, used):
    selected=event['selected'];protocol=package['protocol'];index=count(selected['input_index'])
    from .candidate_measurement_purpose import measurement_purpose_inventory
    measurement_purpose_inventory([selected])
    require(index<len(protocol['inputs']), 'terminal_selected_input')
    audit_identity(selected['neuron_identity']);audit_identity(selected['dataset_identity'])
    validate_graph_input_parameters(package['configuration']['model'],selected['neuron_identity'],selected['parameters'])
    revision=selected['neuron_identity']['sha256'];epoch=count(selected['model_epoch'])
    ids=[selected['trial_id'],selected['anchor_trial_id']]
    if count(protocol['schema_version'])==3:
        embedded=event['selected_probe_packets']
        require(type(embedded) is list and len(embedded)==2, 'terminal_selected_packets')
        for input_index,trial,packet in zip((index,len(protocol['inputs'])-1),ids,embedded):
            require(trial in packets and trial in traces, 'terminal_selected_primary_missing')
            _same(packet,packets[trial]);used.add(trial)
            audit=audit_probe(packet,traces[trial]);prepared=packet['prepared'];request=packet['requested_specification']
            require(audit['valid_observation'] is True and request['trial_id']==trial
                    and prepared['base_model_revision']==packet['current_base_revision']==revision
                    and count(prepared['model_epoch'])==epoch, 'terminal_selected_probe_binding')
            for field,target in [('sample_id','sample_id'),('pattern_hash','pattern_hash'),('expected_stimulus_ids','stimulus_ids')]:
                _same(request[field],protocol[target])
            peaks=packet['observation']['peaks']
            require(len(peaks)==1 and peaks[0]['input_id']==protocol['inputs'][input_index]['id'],
                    'terminal_selected_assigned_input')
    else:
        require(event['selected_probe_packets']==[], 'terminal_composite_unexpected_flat_packets')
        records={row['logical_request']['trial_id']:row for row in package['historical_state']['measurement_archive']['records']}
        require(len(records)==len(package['historical_state']['measurement_archive']['records']), 'terminal_composite_duplicate_trial')
        audited={row['group_id']:row for row in source_audit['composite_measurements']['groups']}
        for input_index,trial in zip((index,len(protocol['inputs'])-1),ids):
            require(trial in records, 'terminal_selected_composite_missing')
            row=records[trial];logical=row['logical_request'];proof=audited[row['group_id']]
            require(row['consumed'] is True and row['training_requested_at_consume'] is True
                    and proof['native_closure_recomputed'] and proof['geometry_recomputed'] and proof['measured'] and proof['consumed']
                    and count(logical['input_index'])==input_index and logical['base_model_revision']==revision
                    and count(logical['model_epoch'])==epoch, 'terminal_selected_composite_binding')
            _same(row['candidate_binding']['model_identity'],selected['neuron_identity'])


def _journal(package, source_audit, packets, traces):
    journal=package['terminal_journal'];current=package['terminal_event']
    require(type(journal) is list and len(journal)<=4096, 'terminal_journal_budget')
    session=epoch=0;seen=set();used=set()
    for event in journal:
        keys(event,EVENT_FIELDS | (EVENT_OPTIONAL & set(event)), 'terminal_event_fields');_digest(event)
        require(event['kind']=='timelearner_native_terminal_selection_event' and count(event['schema_version'])==2
                and event['portable_export_supported'] is True and event['fresh_all_input_verification'] is False
                and event['historical_measurements_rebound_to_actual_epoch'] is False and event['certificate'] is None,
                'terminal_event_claim')
        attempt=count(event['session_attempt']);before=count(event['search_terminal_epoch']);after=count(event['actual_model_epoch'])
        charge=count(event['native_transactions']);budget=event['edit_budget']
        used_edits=count(budget['search_applied_edits']);maximum=count(budget['maximum_edits'])
        require(session<attempt<=count(package['session_attempt']) and before>=epoch and after==before+charge
                and charge<=2 and used_edits<=maximum and charge<=maximum-used_edits
                and count(budget['reserved_transactions'])==2 and (not charge or maximum-used_edits>=2),
                'terminal_event_epoch_or_edit_charge')
        require(number(event['wall_seconds'])>=0 and number(budget['maximum_finalization_wall_seconds'])>0,
                'terminal_event_wall_budget')
        status=event['status'];require(status in {'restored','already_current','budget_exhausted','rejected','rolled_back','failed'},
                                     'terminal_event_status')
        require(status!='already_current' or charge==0,'terminal_noop_charged')
        require(status!='restored' or charge>0,'terminal_restore_not_charged')
        require(status!='rolled_back' or (charge==2 and event['rollback_attempted'] is True and event['rollback_succeeded'] is True),
                'terminal_rollback_claim')
        require(event['sha256'] not in seen,'terminal_duplicate_event')
        _selected(event,package,source_audit,packets,traces,used)
        session=attempt;epoch=after;seen.add(event['sha256'])
    if current is not None:
        require(journal and current==journal[-1] and count(current['session_attempt'])==count(package['session_attempt']),
                'terminal_current_event_missing_from_journal')
        require(package['terminal_policy'] is not None,'terminal_current_event_missing_policy')
        _same(current['edit_budget']['maximum_finalization_wall_seconds'],package['terminal_policy']['maximum_wall_seconds'])
    return used


def _actual(package):
    event=package['terminal_event'];history=package['historical_state']
    actual=package['neuron']['graph']['identity'];source=history['neuron']['graph']['identity']
    if event is None:
        for field in ('model_revision','model_epoch','trained_inputs'):_same(package[field],history[field])
        _same(package['capacitance_state'],_historical_capacitance(history))
        _same(actual,source)
    else:
        for field,target in [('search_terminal_revision','model_revision'),('search_terminal_epoch','model_epoch'),
                             ('search_terminal_parameters','trained_inputs'),('actual_model_epoch','model_epoch')]:
            _same(event[field],history[target] if field.startswith('search_') else package[target])
        if 'source_neuron_identity' in event:_same(event['source_neuron_identity'],source)
        if 'source_dataset_identity' in event:_same(event['source_dataset_identity'],history['dataset']['identity'])
        if 'source_capacitance_state' in event:_same(event['source_capacitance_state'],_historical_capacitance(history) or {})
        if event['status'] in ('restored','already_current'):
            selected=event['selected'];_same(actual,selected['neuron_identity'])
            _same(package['dataset']['identity'],selected['dataset_identity'])
            _same(package['trained_inputs'],selected['parameters']);_same(event['actual_model_revision'],package['model_revision'])
            _same(event['actual_parameters'],package['trained_inputs'])
            _same(package['capacitance_state'] or {},selected['capacitance_state'])
        else:
            _same(actual,source);_same(package['trained_inputs'],history['trained_inputs'])
            _same(package['capacitance_state'],_historical_capacitance(history))
    if package['certificate'] is not None:
        require(event is None,'terminal_transition_has_certificate')
        _same(package['model_revision'],history['model_revision']);_same(package['model_epoch'],history['model_epoch'])


def audit_terminal_package(document, summary, packets, traces, *, external_resolver=None):
    """Check complete source proof and actual boundary; never synthesize primary."""
    try:
        keys(document,FIELDS,'terminal_package_fields');_finite_json(document);_digest(document)
        require(count(document['schema_version'])==8 and document['dynamic_checkpoint'] is False,
                'terminal_package_schema')
        _policy(document['terminal_policy']);count(document['model_epoch'])
        require(count(document['session_attempt'])>0,'terminal_package_session')
        historical_summary=_summary(summary,document)
        source=_source(document,historical_summary,packets,traces,external_resolver)
        physical=_physical(document);extra=_journal(document,source,packets,traces);_actual(document)
        if count(document['protocol']['schema_version'])==3:
            history=document['historical_state']
            expected=extra | _plain_source_ids(history,historical_summary,packets)
            require(set(packets)==set(traces)==expected,'terminal_primary_trial_inventory')
        return dict(auditor_version=1,package_schema_version=8,package_digest_verified=True,
            model_revision=document['model_revision'],model_epoch=document['model_epoch'],
            transcript_model_epoch=document['historical_state']['model_epoch'],training_outcome=document['training_outcome'],
            certificate_consistent=source.get('certificate_consistent',False),exact=source.get('exact'),
            terminal_events=len(document['terminal_journal']),source_audit=source,capacitance_state=physical,
            native_import_verified=False,native_execution_verified=False,live_authority_restored=False,evaluation_verdict=None)
    except EvidenceError:raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,UnicodeError,OverflowError,OSError) as error:
        raise EvidenceError('malformed_terminal_package8') from error
