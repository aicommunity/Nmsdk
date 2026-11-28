"""Project terminal summary9 without relabelling its historical measurements.

The caller must retain the full production primary audit. Wire projection alone
attests neither execution nor training. A restored graph may have the same
semantic revision as an earlier measurement and a different model epoch.
"""
from copy import deepcopy

from .composite_source_evidence import keys
from .native_evidence import count, require
from .terminal_package_evidence import SUMMARY_FIELDS, EVENT_FIELDS, EVENT_OPTIONAL, _digest
from .training_search_report import _parameters, _project_summary


def project_terminal_search_summary(summary, model):
    keys(summary, SUMMARY_FIELDS, 'search_report_terminal_summary_fields')
    _digest(summary)
    require(summary['kind'] == 'native_training_state_summary' and
            type(summary['schema_version']) is int and summary['schema_version'] == 9 and
            summary['state'] == 'finished' and summary['closed_boundary'] is True and
            summary['controller_checkpoint'] is False and summary['restored_live_authority'] is False,
            'search_report_terminal_summary_not_closed')
    history = summary['historical_summary']
    historical = _project_summary(history, model)
    require(summary['outcome'] == historical['outcome'] and summary['reason'] == historical['reason'],
            'search_report_terminal_training_outcome_changed')
    transcript_epoch = count(summary['transcript_model_epoch'])
    actual_epoch = count(summary['model_epoch'])
    require(transcript_epoch == count(history['model_epoch']) and actual_epoch >= transcript_epoch,
            'search_report_terminal_transcript_epoch')
    size = historical['input_count']
    actual = _parameters(summary['parameters'], size)
    event, journal = summary['terminal_event'], summary['terminal_journal']
    require(type(journal) is list and len(journal) <= 4096, 'search_report_terminal_journal')
    for entry in journal:
        keys(entry, EVENT_FIELDS | (EVENT_OPTIONAL & set(entry)), 'search_report_terminal_event_fields')
        _digest(entry)
    if event is not None:
        require(journal and event == journal[-1] and
                event['kind'] == 'timelearner_native_terminal_selection_event' and
                type(event['schema_version']) is int and event['schema_version'] == 2 and
                event['session_attempt'] == summary['session_attempt'] and
                event['stopped_outcome'] == summary['outcome'] and event['stopped_reason'] == summary['reason'],
                'search_report_terminal_current_event')
        require(event['search_terminal_epoch'] == transcript_epoch and
                event['search_terminal_revision'] == historical['actual_model_revision'] and
                event['search_terminal_parameters'] == historical['actual_parameters'] and
                event['actual_model_epoch'] == actual_epoch,
                'search_report_terminal_search_binding')
        require(event.get('actual_model_revision', summary['actual_model_revision']) == summary['actual_model_revision'] and
                event.get('actual_parameters', actual) == actual,
                'search_report_terminal_actual_binding')
        require(event['portable_export_supported'] is True and event['certificate'] is None and
                event['fresh_all_input_verification'] is False and
                event['historical_measurements_rebound_to_actual_epoch'] is False,
                'search_report_terminal_measurement_rebound')
    else:
        require(actual_epoch == transcript_epoch and actual == historical['actual_parameters'] and
                summary['actual_model_revision'] == historical['actual_model_revision'],
                'search_report_terminal_unexplained_model_change')
    measurements = historical['recorded_candidate_measurements']
    matches = [deepcopy(value) for value in measurements if
               value['model_revision'] == summary['actual_model_revision'] and value['full_parameters'] == actual]
    fresh_matches = [value['trial_id'] for value in matches if value['model_epoch'] == actual_epoch]
    # The complete historical projection stays nested with its own final graph,
    # candidates, domains and recovery ledger. Its last parameters are not the
    # graph restored by the subsequent terminal transaction.
    return dict(kind='timelearner_terminal_search_summary_projection', schema_version=1,
        topology=historical['topology'], normalization=historical['normalization'],
        input_count=size, anchor_index=historical['anchor_index'],
        outcome=summary['outcome'], reason=summary['reason'],
        actual_model_revision=summary['actual_model_revision'], actual_model_epoch=actual_epoch,
        actual_parameters=actual, transcript_model_epoch=transcript_epoch,
        terminal_event=deepcopy(event),
        historical_search=historical,
        historical_candidates_matching_actual_physics=(matches if historical['candidate_history_retained'] else None),
        matching_candidate_trial_ids_at_actual_epoch=(fresh_matches if historical['candidate_history_retained'] else None),
        historical_final_verification_group_ids=deepcopy(historical['final_verification_group_ids']),
        producer_reported_fresh_all_input_verification=(None if event is None else event['fresh_all_input_verification']),
        historical_measurements_rebound_to_actual_epoch=False,
        full_primary_audit_inferred=False, native_execution_attested=False,
        training_or_final_verification_verdict=None, scientific_verdict=None)
