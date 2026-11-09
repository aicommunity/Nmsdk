"""Explicit summary7 consistency over independently audited package6 DATA."""
from .composite_summary_evidence import _audit_summary
from .native_evidence import count, require


def audit_candidate_window_summary(document, package, archive_audit):
    require(count(package['schema_version']) == 6 and count(package['protocol']['schema_version']) == 5
            and count(package['runtime_plan']['schema_version']) == 2
            and count(package['measurement_archive']['schema_version']) == 2,
            'candidate_window_summary_version_tuple')
    result = _audit_summary(document, package, archive_audit, schema_version=7)
    return {**result, 'summary_schema_version': 7, 'terminal_provenance_verified': False}
