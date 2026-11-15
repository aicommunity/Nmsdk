"""Execution5 binds supplied recovery DATA; no controller completeness claim."""
from .composite_execution_evidence import _audit_execution, _audit_start_failure
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import count, require


EXTRA_FIELDS = {'recovery_ledger_sha256', 'recovery_delivery_count'}


def _ledger_binding(execution, package):
    require(type(execution) is dict and EXTRA_FIELDS <= set(execution), 'recovery_execution_ledger_fields_missing')
    require(execution.get('sha256') == digest({k: v for k, v in execution.items() if k != 'sha256'}),
            'recovery_execution_digest')
    if package is None:
        require(execution['recovery_ledger_sha256'] is None and execution['recovery_delivery_count'] is None,
                'recovery_execution_invented_ledger_before_source')
        return {'recovery_ledger_present': False, 'native_execution_verified': False}
    require(count(package['schema_version']) == 7 and count(package['protocol']['schema_version']) == 5
            and count(package['measurement_archive']['schema_version']) == 2, 'recovery_execution_version_tuple')
    ledger = package['recovery_ledger']
    require(execution['recovery_ledger_sha256'] == ledger['sha256'] and
            count(execution['recovery_delivery_count']) == len(ledger['deliveries']), 'recovery_execution_ledger_binding')
    return {'recovery_ledger_present': True, 'supplied_recovery_deliveries': len(ledger['deliveries']),
            'service_ledger_completeness_verified': False, 'native_execution_verified': False}


def audit_candidate_window_recovery_execution(execution, directory, names, *, mode, base_version, package=None):
    binding = _ledger_binding(execution, package)
    result = _audit_execution(execution, directory, names, mode=mode, base_version=base_version,
                              package=package, execution_version=5, package_version=7)
    return {**result, **binding}


def audit_candidate_window_recovery_start_failure(execution, directory, names, job):
    _ledger_binding(execution, None)
    return _audit_start_failure(execution, directory, names, job, execution_version=5, configuration_version=8)
