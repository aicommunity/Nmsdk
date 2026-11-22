"""Execution6 binds historical primary and the actual terminal model separately.

The common package/scorer readers retain responsibility for mathematical proof.
These checks bind its published files and counters; they grant no live authority.
"""
from pathlib import Path
import hashlib

from .composite_configuration import METHOD
from .composite_primary import filesystem_primary_resolver, primary_path
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import count, load, require
from .response_domain_evidence import _same
from .terminal_configuration import split_terminal_configuration

EXTRA_FIELDS = {'base_schema_version', 'model_semantic_hash', 'terminal_selection',
                'terminal_boundary', 'source_measurements', 'native_execution_counts'}
BOUNDARY_FIELDS = {'package_sha256', 'actual_model_revision', 'actual_model_epoch',
                   'historical_package_sha256', 'historical_model_revision', 'historical_model_epoch',
                   'terminal_event_sha256', 'terminal_journal_sha256'}
SOURCE_FIELDS = {'protocol_schema_version', 'measurement_method', 'measurement_archive', 'source_origin',
                 'attempt_counters', 'archive_counters', 'recovery_ledger_sha256', 'recovery_delivery_count'}


def audit_terminal_execution(execution, directory, names, *, mode, job, package=None):
    _, policy = split_terminal_configuration(job['configuration'])
    require(policy is not None and count(execution['schema_version']) == 6
            and count(execution['base_schema_version']) == 1 and job['schema_version'] == 1,
            'terminal_execution_configuration_version')
    _same(execution['terminal_selection'], policy)
    _same(execution['model_semantic_hash'], execution['model_revision'])
    raw = execution['native_execution_counts']
    keys(raw, {'native_trials', 'sampled_frames'}, 'terminal_execution_counter_fields')
    for value in raw.values():
        count(value)
    if package is None:
        require(execution['terminal_boundary'] is None and execution['source_measurements'] is None,
                'terminal_execution_invented_source_before_capture')
        if mode == 'preflight':
            require(raw == {'native_trials': 0, 'sampled_frames': 0}, 'terminal_preflight_has_native_trials')
        return dict(owned_archive_present=False, native_execution_verified=False, evaluation_verdict=None)

    require(mode == 'train' and count(package['schema_version']) == 8, 'terminal_execution_package_schema')
    _same(package['terminal_policy'], policy)
    _same(package['model_revision'], execution['model_revision'])
    history = package['historical_state']; event = package['terminal_event']
    boundary = execution['terminal_boundary']; keys(boundary, BOUNDARY_FIELDS, 'terminal_execution_boundary_fields')
    expected = dict(package_sha256=package['sha256'], actual_model_revision=package['model_revision'],
        actual_model_epoch=package['model_epoch'], historical_package_sha256=history['sha256'],
        historical_model_revision=history['model_revision'], historical_model_epoch=history['model_epoch'],
        terminal_event_sha256=None if event is None else event['sha256'],
        terminal_journal_sha256=digest({'entries': package['terminal_journal']}))
    _same(boundary, expected)
    source = execution['source_measurements']; keys(source, SOURCE_FIELDS, 'terminal_execution_source_fields')
    _same(source['protocol_schema_version'], history['protocol']['schema_version'])
    if count(history['schema_version']) not in (5, 6, 7):
        require(all(source[key] is None for key in SOURCE_FIELDS-{'protocol_schema_version'}),
                'terminal_plain_execution_has_composite_accounting')
        return dict(owned_archive_present=False, actual_and_historical_model_bound=True,
                    native_execution_verified=False, evaluation_verdict=None)

    archive = history['measurement_archive']
    _same(source['measurement_method'], METHOD); _same(source['source_origin'], archive['source_origin'])
    _same(source['attempt_counters'], archive['counters']['attempt'])
    _same(source['archive_counters'], archive['counters']['archive'])
    require(count(raw['native_trials']) >= count(source['attempt_counters']['native_probes'])
            and count(raw['sampled_frames']) >= count(source['attempt_counters']['sampled_frames']),
            'terminal_execution_counter_scope')
    descriptor = source['measurement_archive']; keys(descriptor, {'path', 'bytes', 'sha256'},
                                                    'terminal_execution_archive_descriptor')
    name = primary_path(descriptor['path']); require(name in names, 'terminal_execution_archive_unpublished')
    resolver = filesystem_primary_resolver(directory); data = resolver(name)
    require(len(data) == count(descriptor['bytes']) and hashlib.sha256(data).hexdigest() == descriptor['sha256'],
            'terminal_execution_archive_bytes_changed')
    _same(load(Path(directory)/name), archive)
    for index, group in enumerate(archive['records'], 1):
        sidecar = f'composite-measurements/group-{index:06d}.json'
        require(sidecar in names, 'terminal_execution_group_sidecar_missing')
        _same(load(Path(directory)/sidecar), group)
        for trial in group['raw_trials']:
            require(trial['primary_ref']['relative_path'] in names, 'terminal_execution_primary_unpublished')
    if count(history['schema_version']) == 7:
        ledger = history['recovery_ledger']
        require(source['recovery_ledger_sha256'] == ledger['sha256']
                and count(source['recovery_delivery_count']) == len(ledger['deliveries']),
                'terminal_execution_recovery_ledger_binding')
    else:
        require(source['recovery_ledger_sha256'] is None and source['recovery_delivery_count'] is None,
                'terminal_execution_invented_recovery_ledger')
    return dict(owned_archive_present=True, actual_and_historical_model_bound=True,
                native_execution_verified=False, evaluation_verdict=None)


def audit_terminal_start_failure(execution, directory, names, job):
    require(execution['execution'] == 'training_start_failed' and execution['completed_boundary'] is False
            and execution['package_path'] is None and execution['package_sha256'] is None
            and execution['attempt_id'] == job['configuration']['run_id'], 'terminal_start_failure_scope')
    require('training-start-failure.json' in names and not ({'train_learned_state.json', 'train_stopped_state.json',
            'train_learned_summary.json', 'train_stopped_summary.json'} & names), 'terminal_start_failure_has_package')
    failure = load(Path(directory)/'training-start-failure.json')
    keys(failure, {'kind', 'schema_version', 'outcome', 'reason', 'model_revision', 'dynamic_checkpoint',
        'source_origin', 'measurement_archive', 'certificate', 'contains_evaluation_verdict', 'sha256'},
        'terminal_start_failure_fields')
    from .stopped_evidence import OUTCOMES
    require(failure['sha256'] == digest({k:v for k,v in failure.items() if k != 'sha256'})
            and failure['kind'] == 'timelearner_native_training_start_failure' and count(failure['schema_version']) == 1
            and failure['outcome'] in OUTCOMES and failure['outcome'] == execution['training_outcome']
            and type(failure['reason']) is str and bool(failure['reason'])
            and failure['model_revision'] == execution['model_revision'] and failure['dynamic_checkpoint'] is False
            and all(failure[k] is None for k in ('source_origin', 'measurement_archive', 'certificate'))
            and failure['contains_evaluation_verdict'] is False, 'terminal_start_failure_binding')
    audit_terminal_execution(execution, directory, names, mode='train', job=job)
    return dict(training_start_failure=failure, completed_boundary=False, training_outcome=failure['outcome'],
                owned_source_captured=False, native_execution_verified=False, evaluation_verdict=None)
