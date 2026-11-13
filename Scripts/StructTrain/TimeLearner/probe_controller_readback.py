"""Idle controller DATA readback, separate from a finished training summary."""
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import count, number, require


def audit_idle_composite_controller(summary, source):
    fields = {'kind', 'schema_version', 'state', 'certificate', 'reference_probes', 'search_present',
        'session_attempt', 'model_epoch', 'protocol_sha256', 'source_binding_sha256',
        'initial_configuration_sha256', 'record_signatures_sha256', 'recovery_deliveries_sha256',
        'recovery_delivery_log_intact', 'reference_rows', 'reference_group_ids', 'final_group_ids',
        'groups', 'native_probes', 'sampled_frames', 'primary_bytes'}
    require(type(summary) is dict and set(summary) == fields and
            summary['kind'] == 'native_probe_idle_controller_readback' and
            type(summary['schema_version']) is int and summary['schema_version'] == 1 and
            source['schema_version'] in (5, 6, 7), 'probe_idle_readback_schema')
    require(summary['state'] == 'idle' and summary['certificate'] is None and
            summary['search_present'] is False and count(summary['reference_probes']) == 0,
            'probe_idle_readback_started_training')
    archive = source['measurement_archive'];records = archive['records']
    signatures = [dict(group_id=r['group_id'], attempt_id=r['attempt_id'], consumed=r['consumed'],
        semantic_proof_id=(r['measurement'] or {}).get('semantic_proof_id', '')) for r in records]
    deliveries = source.get('recovery_ledger', {}).get('deliveries', [])
    require(count(summary['session_attempt']) == count(source['session_attempt']) and
            count(summary['model_epoch']) == count(source['model_epoch']) and
            summary['protocol_sha256'] == sha(source['protocol']) and
            summary['source_binding_sha256'] == sha(archive['source_binding']) and
            summary['initial_configuration_sha256'] == sha(source['configuration']) and
            summary['record_signatures_sha256'] == sha(signatures) and
            summary['recovery_deliveries_sha256'] == sha(deliveries) and
            summary['recovery_delivery_log_intact'] is True and
            summary['reference_group_ids'] == archive['reference_group_ids'] and
            summary['final_group_ids'] == [v for v in archive['final_group_ids'] if v],
            'probe_idle_retained_history_changed')
    counters = archive['counters']
    for key, value in (('groups', counters['attempt']['logical_groups']),
                       ('native_probes', counters['attempt']['native_probes']),
                       ('sampled_frames', counters['attempt']['sampled_frames']),
                       ('primary_bytes', counters['archive']['primary_bytes'])):
        require(count(summary[key]) == count(value), 'probe_idle_counter_changed')
    reference_records = {r['group_id']: r for r in records}
    expected = {}
    if source['reference_complete']:
        for group in archive['reference_group_ids']:
            record = reference_records[group];measurement = record['measurement']
            key = record['logical_request']['input_id']
            require(key not in expected, 'probe_idle_duplicate_reference')
            expected[key] = dict(input_id=key, raw_potential=number(measurement['raw_potential']),
                                group_id=group, semantic_proof_id=measurement['semantic_proof_id'])
    rows = summary['reference_rows']
    require(type(rows) is list and len(rows) == len(expected) and
            all(type(r) is dict and set(r) == {'input_id', 'raw_potential', 'group_id', 'semantic_proof_id'}
                for r in rows) and len({r['input_id'] for r in rows}) == len(rows),
            'probe_idle_reference_inventory')
    for row in rows:
        number(row['raw_potential'])
        require(row['input_id'] in expected and row == expected[row['input_id']],
                'probe_idle_reference_changed')
    return dict(idle_readback_checked=True, finished_training_boundary_claimed=False,
                controller_checkpoint=False, scientific_verdict=None)
