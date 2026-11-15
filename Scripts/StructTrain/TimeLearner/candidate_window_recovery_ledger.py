"""Replay portable recovery delivery DATA against actual archive2 primary.

Retained attempts keep their original runtime3 declarations, including after a
warm retry under runtime2. This does not infer unrecorded controller actions,
restore execution authority or certify a training result.
"""
from .candidate_window_archive_evidence import audit_candidate_window_archive
from .candidate_window_contract import bounded_count, hash_id
from .candidate_window_recovery_events import (audit_candidate_window_recovery_events,
                                               validate_candidate_window_recovery_event)
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, require
from .response_domain_evidence import _same, _finite_json, _text

FIELDS=set(('kind schema_version source_origin owner_family_binding '
    'measurement_archive_document_id producer_log_intact '
    'independent_delivery_completeness_verified deliveries sha256').split())


def audit_candidate_window_recovery_ledger(ledger, archive, configuration, *, external_resolver=None):
    """Verify all supplied deliveries; an empty list never proves coverage."""
    try:
        keys(ledger,FIELDS,'candidate_window_recovery_ledger_fields');_finite_json(ledger)
        require(ledger['kind']=='timelearner_candidate_window_recovery_ledger' and
                bounded_count(ledger['schema_version'])==1 and
                ledger['producer_log_intact'] is True and
                ledger['independent_delivery_completeness_verified'] is False,
                'candidate_window_recovery_ledger_schema_or_claim')
        hash_id(ledger['sha256'])
        require(ledger['sha256']==digest({k:v for k,v in ledger.items() if k!='sha256'}),
                'candidate_window_recovery_ledger_digest')
        for field in ('source_origin','owner_family_binding'):
            hash_id(ledger[field]);_same(ledger[field],archive[field])
        hash_id(ledger['measurement_archive_document_id'])
        _same(ledger['measurement_archive_document_id'],archive['artifact_document_sha256'])
        require(type(ledger['deliveries']) is list and len(ledger['deliveries'])<=len(archive['records']),
                'candidate_window_recovery_ledger_inventory')
        # Even an empty ledger must replay its referenced primary archive.
        primary=audit_candidate_window_archive(archive,configuration,external_resolver=external_resolver)
        positions={r['group_id']:i for i,r in enumerate(archive['records'])}
        attempts={};seen_groups=set();seen_events=set();last=-1
        for row in ledger['deliveries']:
            keys(row,{'event','runtime_plan'},'candidate_window_recovery_delivery_fields')
            event=row['event'];transition=validate_candidate_window_recovery_event(event)
            group=event['group_id'];identifier=event['event_id']
            require(group in positions,'candidate_window_recovery_ledger_group_missing')
            require(group not in seen_groups and identifier not in seen_events and positions[group]>last,
                    'candidate_window_recovery_ledger_replay_or_order')
            seen_groups.add(group);seen_events.add(identifier);last=positions[group]
            run=transition['run_id'];_text(run)
            if run not in attempts:attempts[run]={'runtime':row['runtime_plan'],'events':[]}
            _same(row['runtime_plan'],attempts[run]['runtime'])
            attempts[run]['events'].append(event)
        results={}
        for run,attempt in attempts.items():
            results[run]=audit_candidate_window_recovery_events(attempt['events'],archive,configuration,
                attempt['runtime'],external_resolver=external_resolver,attempt_id=run)
        return dict(schema_version=1,ledger_digest_verified=True,deliveries_checked=len(ledger['deliveries']),
            attempts_checked=len(attempts),primary_files_checked=primary['primary_files_checked'],
            attempts=results,event_bindings_verified=True,service_ledger_completeness_verified=False,
            all_invalid_observations_independently_recounted=False,all_edits_independently_recounted=False,
            native_execution_verified=False,live_authority_restored=False,training_certificate_verified=False,
            scientific_verdict=None)
    except EvidenceError:raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,OverflowError) as error:
        raise EvidenceError('malformed_candidate_window_recovery_ledger') from error
