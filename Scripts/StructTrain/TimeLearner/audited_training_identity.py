"""Resolve a compact reader's job identity from bound original Train evidence.

The sole missing-field adapter is the recorded Branch Count24 schema1 reader.
This checks metadata identity; the caller still owns full-primary auditing,
file-byte checks, closed groups and native DATA import. No source is rewritten.
"""
from .native_calibration_worker import _digest
from .native_evidence import require
from pathlib import PurePosixPath


LEGACY_BRANCH_KIND = 'timelearner_actual_Branch_Count24_closed_training_readback'
LEGACY_BRANCH_FIELDS = {'kind', 'schema_version', 'source_package', 'source_summary',
    'training_outcome', 'completed_boundary', 'terminal', 'historical', 'candidate_count',
    'classification_performed', 'scientific_verdict'}


def _legacy_record(value, name):
    require(type(value) is dict and set(value) == {'path', 'size', 'sha256'} and
            type(value['path']) is str and type(value['size']) is int and value['size'] > 0 and
            type(value['sha256']) is str and len(value['sha256']) == 64 and
            all(c in '0123456789abcdef' for c in value['sha256']),
            'audited_Train_legacy_branch_source_record_changed')
    path = PurePosixPath(value['path'])
    require(path.is_absolute() and '..' not in path.parts and '\\' not in value['path'] and path.name == name,
            'audited_Train_legacy_branch_source_record_changed')
    return path


def compact_job_identity(compact, job, execution, proof, expected_job_sha256):
    """Return an explicit derived identity, without inferring completion or quality."""
    require(all(type(v) is dict for v in (compact, job, execution, proof)),
            'audited_Train_identity_documents_required')
    _digest(job)
    _digest(execution)
    require(type(expected_job_sha256) is str and len(expected_job_sha256) == 64 and
            all(c in '0123456789abcdef' for c in expected_job_sha256) and
            job.get('kind') == 'timelearner_native_training_job' and
            execution.get('kind') == 'timelearner_native_training_execution' and
            execution.get('job_sha256') == job['sha256'] == expected_job_sha256,
            'audited_Train_original_job_changed')
    if 'job_sha256' in compact:
        require(compact['job_sha256'] == expected_job_sha256,
                'audited_Train_compact_job_changed')
        adapter = 'compact_declared_job_sha256'
    else:
        require(set(compact) == LEGACY_BRANCH_FIELDS and
                compact['kind'] == LEGACY_BRANCH_KIND and
                type(compact['schema_version']) is int and compact['schema_version'] == 1,
                'audited_Train_unknown_missing_job_identity_schema')
        package = _legacy_record(compact['source_package'], 'train_stopped_state.json')
        summary = _legacy_record(compact['source_summary'], 'train_stopped_summary.json')
        require(package.parent == summary.parent and
                type(compact['candidate_count']) is int and compact['candidate_count'] >= 0 and
                type(compact['terminal']) is dict and type(compact['historical']) is dict,
                'audited_Train_legacy_branch_scope_changed')
        require(job.get('owner_class') == 'NNeuronTimeLearnerBranch' and
                job.get('configuration', {}).get('model', {}).get('branch') is True and
                execution.get('attempt_id') == job.get('configuration', {}).get('run_id') and
                execution.get('package_path') == 'train_stopped_state.json' and
                execution.get('completed_boundary') is False and compact['completed_boundary'] is False and
                proof.get('completed_boundary') is False and
                compact['training_outcome'] == execution.get('training_outcome') == proof.get('training_outcome') and
                compact['classification_performed'] is False and compact['scientific_verdict'] is None,
                'audited_Train_legacy_branch_scope_changed')
        audited = proof.get('training_audit')
        require(type(audited) is dict and audited.get('package_digest_verified') is True and
                audited.get('model_revision') == execution.get('model_revision') and
                audited.get('training_outcome') == execution.get('training_outcome'),
                'audited_Train_legacy_branch_primary_audit_changed')
        adapter = 'legacy_branch_count24_v1_original_native_job_execution'
    return dict(kind='timelearner_audited_compact_job_identity', schema_version=1,
        adapter=adapter, job_sha256=expected_job_sha256,
        native_execution_sha256=execution['sha256'],
        original_compact_modified=False, training_completion_inferred=False,
        native_import_verified=False, scientific_verdict=None)
