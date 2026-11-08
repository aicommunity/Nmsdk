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


def audit_initial_planning_configuration(package, job, initial):
    """Only actual initial input readback replaces creation input defaults."""
    expected = {**job['configuration'], 'run_id': job['configuration']['run_id'] + '/session/1'}
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
    require(package['runtime_plan']['run_id'] == expected['run_id'], 'composite_initial_runtime_attempt')
    source = package['measurement_archive']['source_binding']
    _same(source['initial_model'], initial['identity'])


def audit_composite_execution(execution, directory, names, *, mode, base_version, package=None):
    directory = Path(directory)
    require(count(execution['schema_version']) == 3 and count(execution['base_schema_version']) == base_version
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
    require(package is not None and package['schema_version'] == 5, 'composite_execution_package_missing')
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
