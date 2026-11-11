"""Execution3 artifact closure and Train/package bindings, not process attestation."""
from pathlib import Path

from .composite_configuration import METHOD
from .composite_primary import filesystem_primary_resolver, primary_path
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import count, load, require
from .response_domain_evidence import _same

EXTRA_FIELDS = {'base_schema_version', 'measurement_method', 'measurement_archive',
                'model_semantic_hash', 'source_origin', 'composite_counters'}


def _audit_start_failure(execution, directory, names, job, *, execution_version, configuration_version):
    """A signed pre-source refusal is diagnostic data, never a model package."""
    require((execution_version,configuration_version) in ((3,6),(4,7)), 'unsupported_execution_configuration_pair')
    require(execution['schema_version'] == execution_version and execution['base_schema_version'] == 1
            and job['schema_version'] == 1 and job['configuration']['schema_version'] == configuration_version
            and execution['execution'] == 'training_start_failed'
            and execution['completed_boundary'] is False
            and execution['package_path'] is None and execution['package_sha256'] is None
            and execution['attempt_id'] == job['configuration']['run_id'],
            'composite_start_failure_scope')
    require('training-start-failure.json' in names and not ({'train_learned_state.json',
            'train_stopped_state.json', 'train_learned_summary.json', 'train_stopped_summary.json'} & names),
            'composite_start_failure_package_or_missing_receipt')
    failure = load(Path(directory)/'training-start-failure.json')
    keys(failure, {'kind', 'schema_version', 'outcome', 'reason', 'model_revision', 'dynamic_checkpoint',
        'source_origin', 'measurement_archive', 'certificate', 'contains_evaluation_verdict', 'sha256'},
        'composite_start_failure_fields')
    from .composite_measurement_contract import integral_number_view
    original = failure; failure = integral_number_view(failure)
    from .stopped_evidence import OUTCOMES
    require(original['sha256'] == digest({k:v for k,v in original.items() if k != 'sha256'})
            and failure['kind'] == 'timelearner_native_training_start_failure'
            and count(failure['schema_version']) == 1 and failure['outcome'] in OUTCOMES
            and failure['outcome'] == execution['training_outcome']
            and type(failure['reason']) is str and bool(failure['reason'])
            and failure['dynamic_checkpoint'] is False and failure['source_origin'] is None
            and failure['measurement_archive'] is None and failure['certificate'] is None
            and failure['contains_evaluation_verdict'] is False,
            'composite_start_failure_binding')
    revision = execution['model_revision']
    require(revision is None or type(revision) is str and len(revision) == 64
            and all(c in '0123456789abcdef' for c in revision), 'composite_start_failure_model_revision')
    require(failure['model_revision'] == execution['model_semantic_hash'] == revision,
            'composite_start_failure_model_binding')
    _audit_execution(execution, directory, names, mode='train', base_version=1,
                     execution_version=execution_version, package_version=configuration_version-1)
    return dict(training_start_failure=failure, completed_boundary=False,
        training_outcome=failure['outcome'], owned_source_captured=False,
        native_execution_verified=False, evaluation_verdict=None)


def audit_initial_planning_configuration(package, job, initial):
    """Only actual initial input readback replaces creation input defaults."""
    expected = dict(job['configuration'])
    actual_inputs = initial['parameters']
    require(len(actual_inputs) == len(expected['model']['inputs']), 'composite_initial_input_dimension')
    inputs = []
    for declared, actual in zip(expected['model']['inputs'], actual_inputs):
        require(actual['length'] == declared['attachment'] and actual['synapses'] == declared['synapses']
                and (declared['resistance'] is None or actual['resistance'] == declared['resistance']),
                'composite_initial_input_readback_changed')
        inputs.append({**declared, 'resistance': actual['resistance']})
    expected['model'] = {**expected['model'], 'inputs': inputs}
    _same(package['configuration'], expected)
    require(package['runtime_plan']['run_id'] == expected['run_id'] + '/session/1', 'composite_initial_runtime_attempt')
    source = package['measurement_archive']['source_binding']
    _same(source['initial_model'], initial['identity'])


def _audit_execution(execution, directory, names, *, mode, base_version, package=None,
                     execution_version, package_version):
    require((execution_version,package_version) in ((3,5),(4,6)), 'unsupported_execution_package_pair')
    from .composite_measurement_contract import integral_number_view
    execution = integral_number_view(execution)
    directory = Path(directory)
    require(count(execution['schema_version']) == execution_version and count(execution['base_schema_version']) == base_version
            and execution['measurement_method'] == METHOD, 'composite_execution_version_or_method')
    counters = execution['composite_counters']
    keys(counters, {'attempt', 'archive', 'execution'}, 'composite_execution_counter_fields')
    keys(counters['execution'], {'native_trials', 'sampled_frames'}, 'composite_execution_raw_counter_fields')
    for value in counters['execution'].values(): count(value)
    if execution['measurement_archive'] is None:
        require(execution['source_origin'] is None and package is None, 'composite_execution_missing_owned_archive')
        if mode == 'preflight':
            _same(counters, dict(attempt=dict(logical_groups=0, native_probes=0, sampled_frames=0),
                archive=dict(groups=0, native_probes=0, sampled_frames=0, primary_bytes=0),
                execution=dict(native_trials=0, sampled_frames=0)))
            _same(execution['model_semantic_hash'], execution['model_revision'])
        else:
            # A failed start may have actual callbacks but no captured source.
            # Unknown attempt/archive accounting must remain explicitly null.
            require(counters['attempt'] is None and counters['archive'] is None,
                    'composite_failed_start_invented_accounting')
        return dict(owned_archive_present=False, native_execution_verified=False, evaluation_verdict=None)
    require(package is not None and package['schema_version'] == package_version, 'composite_execution_package_missing')
    record = execution['measurement_archive']; keys(record, {'path', 'bytes', 'sha256'}, 'composite_execution_archive_record')
    name = primary_path(record['path']); require(name in names, 'composite_execution_archive_unpublished')
    raw = filesystem_primary_resolver(directory)(name)
    import hashlib
    require(len(raw) == count(record['bytes']) and hashlib.sha256(raw).hexdigest() == record['sha256'],
            'composite_execution_archive_bytes_changed')
    _same(load(directory/name), package['measurement_archive'])
    archive = package['measurement_archive']
    _same(counters['attempt'], archive['counters']['attempt']); _same(counters['archive'], archive['counters']['archive'])
    require(execution['model_semantic_hash'] == package['neuron']['graph']['identity']['sha256'] == package['model_revision']
            and execution['source_origin'] == archive['source_origin'], 'composite_execution_actual_model_or_source')
    require(counters['execution']['native_trials'] >= counters['attempt']['native_probes']
            and counters['execution']['sampled_frames'] >= counters['attempt']['sampled_frames'],
            'composite_execution_counter_scope')
    # The external files are an additional exact mirror of mandatory blobs.
    from .composite_package_evidence import audit_composite_package
    summary_name = 'train_learned_summary.json' if package['kind'] == 'timelearner_completed_state' else 'train_stopped_summary.json'
    require(summary_name in names, 'composite_execution_summary_missing')
    audited = audit_composite_package(package, load(directory/summary_name), external_resolver=filesystem_primary_resolver(directory))
    for index, group in enumerate(archive['records'], 1):
        sidecar = f'composite-measurements/group-{index:06d}.json'
        require(sidecar in names, 'composite_execution_group_sidecar_missing')
        _same(load(directory/sidecar), group)
        for trial in group['raw_trials']:
            require(trial['primary_ref']['relative_path'] in names, 'composite_execution_primary_unpublished')
    return dict(owned_archive_present=True, package_audit=audited, native_execution_verified=False, evaluation_verdict=None)


def audit_composite_start_failure(execution, directory, names, job):
    return _audit_start_failure(execution, directory, names, job, execution_version=3, configuration_version=6)


def audit_composite_execution(execution, directory, names, *, mode, base_version, package=None):
    return _audit_execution(execution, directory, names, mode=mode, base_version=base_version,
                            package=package, execution_version=3, package_version=5)
