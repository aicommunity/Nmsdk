"""Bind recovery-event DATA to independently replayed complete native groups.

This checks a supplied event set, not completeness of a service ledger or a
training certificate. Missing controller actions and unrecorded generic errors
cannot be reconstructed from these measurement groups alone.
"""
from .candidate_recovery_history import _FIELDS as TRANSITION_FIELDS
from .candidate_window_archive_evidence import audit_candidate_window_archive
from .candidate_window_contract import (bounded_count, capacitance, hash_id,
    parameters, expected_rejected_group_content_id)
from .candidate_window_runtime_plan import audit_candidate_window_runtime_recovery_plan
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, number, require
from .response_domain_evidence import _same, _text

EVENT_FIELDS=set(('kind schema_version transition group_id rejected_content_id source_origin '
    'owner_scope candidate_witness_id issued_probes applied_edits accepted_composite_observations event_id').split())


def validate_candidate_window_recovery_event(event):
    """Validate the wire shape; a self-consistent content hash is not admission."""
    try:
        keys(event,EVENT_FIELDS,'candidate_window_recovery_event_fields')
        require(event['kind']=='timelearner_candidate_window_recovery_event' and
                bounded_count(event['schema_version'])==1,'candidate_window_recovery_event_version')
        hash_id(event['event_id'])
        require(event['event_id']==digest({k:v for k,v in event.items() if k!='event_id'}),
                'candidate_window_recovery_event_digest')
        for field in ('rejected_content_id','source_origin','candidate_witness_id'):hash_id(event[field])
        for field in ('group_id','owner_scope'):_text(event[field])
        transition=event['transition'];keys(transition,TRANSITION_FIELDS,'candidate_window_recovery_transition_fields')
        for field in ('run_id','trial_id','base_model_revision','effective_model_revision'):_text(transition[field])
        require(type(transition['reason_after']) is str,'candidate_window_recovery_reason_type')
        for field in ('action_serial','input_index','candidate_input_index','sweep','model_epoch','invalid_before','invalid_after'):
            bounded_count(transition[field])
        require(transition['action_serial']>0 and transition['invalid_after']==transition['invalid_before']+1,
                'candidate_window_recovery_invalid_increment')
        values=parameters(transition['full_parameters'])
        require(all(v['synapses']<=128 for v in values) and
                transition['input_index']<len(values) and transition['candidate_input_index']<len(values),
                'candidate_window_recovery_parameter_dimensions')
        capacitance(transition['capacitance'])
        require(transition['validity'] in ('missing','ambiguous') and transition['phase'] in ('anchor','input'),
                'candidate_window_recovery_measurement_kind')
        status={'cursor_advanced':'searching','invalid_budget_stop':'invalid_observation','restored_best_stop':'search_unresolved'}
        require(transition['disposition'] in status and transition['status_after']==status[transition['disposition']],
                'candidate_window_recovery_outcome')
        probes=bounded_count(event['issued_probes'],positive=True);bounded_count(event['applied_edits'])
        require(bounded_count(event['accepted_composite_observations'])<=probes,
                'candidate_window_recovery_accepted_counter')
        return transition
    except EvidenceError:raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,OverflowError) as error:
        raise EvidenceError('malformed_candidate_window_recovery_event') from error


def audit_candidate_window_recovery_events(events, archive, configuration, runtime_plan, *, external_resolver=None,
                                           attempt_id=None):
    """Replay primary first; bind supplied ordered events without claiming coverage."""
    try:
        require(type(events) is list,'candidate_window_recovery_event_inventory')
        protocol=archive['protocol']
        runtime_audit=audit_candidate_window_runtime_recovery_plan(runtime_plan,configuration,protocol)
        primary_audit=audit_candidate_window_archive(archive,configuration,external_resolver=external_resolver)
        selected_attempt=archive['current_attempt_id'] if attempt_id is None else attempt_id
        _text(selected_attempt)
        require(selected_attempt==runtime_plan['run_id'] and
                (selected_attempt==archive['current_attempt_id'] or
                 any(r['attempt_id']==selected_attempt for r in archive['records'])),
                'candidate_window_recovery_runtime_attempt')
        common=runtime_plan['composite_measurement'];_same(archive['maximum_total_primary_bytes'],common['maximum_total_primary_bytes'])
        records=archive['records'];by_group={r['group_id']:(i,r) for i,r in enumerate(records)}
        for record in records:
            if record['attempt_id']!=runtime_plan['run_id']:continue
            _same(record['budgets']['attempt_limits'],{**common['attempt_limits'],
                'maximum_model_seconds':runtime_plan['maximum_model_seconds'],'maximum_wall_seconds':runtime_plan['maximum_wall_seconds']})
            for axis in ('model','wall'):
                field='maximum_group_'+axis+'_seconds'
                require(number(record['budgets'][field])<=number(common[field]),'candidate_window_recovery_group_budget')
        seen=set();last_position=-1;last_serial=last_invalid=last_probes=last_edits=last_accepted=0
        last_epoch=bounded_count(runtime_plan['initial_model_epoch']);search=runtime_plan['search']
        for event in events:
            t=validate_candidate_window_recovery_event(event)
            require(event['group_id'] in by_group,'candidate_window_recovery_group_missing')
            position,record=by_group[event['group_id']];logical=record['logical_request']
            identity=(event['group_id'],t['trial_id'],event['event_id'])
            require(all(value not in seen for value in identity) and position>last_position and
                    t['action_serial']>last_serial and t['model_epoch']>=last_epoch,
                    'candidate_window_recovery_replay_or_order')
            seen.update(identity)
            require(record['attempt_id']==runtime_plan['run_id'] and t['run_id']==logical['run_id']==runtime_plan['run_id'] and
                    record['consumed'] is False and record['training_requested_at_consume'] is True,
                    'candidate_window_recovery_delivery_state')
            _same(event['source_origin'],record['source_origin']);_same(event['owner_scope'],record['owner_family_binding'])
            _same(event['candidate_witness_id'],record['candidate_witness_id'])
            for field in ('trial_id','input_index','model_epoch','base_model_revision'):_same(t[field],logical[field])
            _same(t['effective_model_revision'],record['native_group']['specification']['effective_model_revision'])
            _same(t['full_parameters'],record['candidate_binding']['physical_readback']['parameters'])
            _same(t['capacitance'],record['candidate_binding']['physical_readback']['capacitance'])
            _same(event['rejected_content_id'],expected_rejected_group_content_id(record,protocol))
            _same(t['validity'],record['selection']['geometry']['validity'])
            require(t['trial_id']==runtime_plan['run_id']+'/search/'+str(bounded_count(t['action_serial'])),
                    'candidate_window_recovery_action_trial_binding')
            anchor=len(protocol['inputs'])-1
            require(t['candidate_input_index']<anchor and t['input_index']==(anchor if t['phase']=='anchor' else t['candidate_input_index']),
                    'candidate_window_recovery_input_assignment')
            for value,bound in zip(t['full_parameters'],search['bounds']):
                for field in ('length','synapses','resistance'):
                    require(number(bound['minimum_'+field])<=number(value[field])<=number(bound['maximum_'+field]),
                            'candidate_window_recovery_parameter_bounds')
            before,after=t['invalid_before'],t['invalid_after'];allowance=bounded_count(search['maximum_invalid_observations'])
            require(last_invalid<=before and after<=allowance+1,'candidate_window_recovery_invalid_budget')
            if t['disposition']=='invalid_budget_stop':require(before==allowance,'candidate_window_recovery_budget_stop')
            else:require(before<allowance,'candidate_window_recovery_advance_without_budget')
            if t['disposition']=='restored_best_stop':
                require(t['reason_after']=='restored_best_candidate_has_rejected_window','candidate_window_recovery_restored_best_reason')
            require(last_probes<=event['issued_probes']<=search['maximum_probes'] and
                    last_edits<=event['applied_edits']<=search['maximum_edits'] and
                    last_accepted<=event['accepted_composite_observations'], 'candidate_window_recovery_counter_order_or_budget')
            accepted=sum(r['purpose']=='search' and r['attempt_id']==runtime_plan['run_id'] and r['consumed'] for r in records[:position])
            _same(event['accepted_composite_observations'],accepted)
            last_position,last_serial,last_epoch=position,t['action_serial'],t['model_epoch']
            last_invalid,last_probes,last_edits,last_accepted=after,event['issued_probes'],event['applied_edits'],accepted
        return dict(events_checked=len(events),primary_files_checked=primary_audit['primary_files_checked'],
            runtime_plan=runtime_audit,event_bindings_verified=True,service_ledger_completeness_verified=False,
            all_invalid_observations_independently_recounted=False,all_edits_independently_recounted=False,
            native_execution_verified=False,live_authority_restored=False,training_certificate_verified=False,scientific_verdict=None)
    except EvidenceError:raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,OverflowError) as error:
        raise EvidenceError('malformed_candidate_window_recovery_events') from error
