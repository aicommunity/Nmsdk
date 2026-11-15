"""Execution4 artifact/producer joins, distinct from native process attestation."""
from .composite_execution_evidence import _audit_execution, _audit_start_failure
from .native_evidence import count, require


def audit_candidate_window_execution(execution, directory, names, *, mode, base_version, package=None):
    if package is not None:
        require(count(package['schema_version']) == 6 and count(package['protocol']['schema_version']) == 5
                and count(package['measurement_archive']['schema_version']) == 2,
                'candidate_window_execution_version_tuple')
    return _audit_execution(execution, directory, names, mode=mode, base_version=base_version,
                            package=package, execution_version=4, package_version=6)


def audit_candidate_window_start_failure(execution, directory, names, job):
    return _audit_start_failure(execution, directory, names, job, execution_version=4, configuration_version=7)
