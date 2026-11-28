"""Admit an actual stopped Train through its complete production evidence.

This is independent of the normalization variable and of the worker that ran
Train. It grants only permission to prepare a diagnostic evaluation, never a
convergence certificate or a classification result.
"""
from pathlib import Path

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import load, require
from .runtime import file_record


def closed_pipeline_source(manifest_path, native, audit):
    """Reaudit the full, unchanged primary run before preparing its stopped state.

    A small saved audit or a signed metadata document alone is insufficient.
    The production auditor checks all primary bytes, observations, cold model,
    terminal selection and owned-process/runtime evidence. The returned native
    package record binds the later, separate preparation decode to those bytes.
    """
    from .native_pipeline_worker import audit_run_manifest

    manifest_path = Path(manifest_path).resolve(strict=True)
    native = Path(native).resolve(strict=True)
    require(manifest_path == native.parent/'run-manifest.json' and native.name == 'native',
            'stopped_pipeline_actual_run_path')
    before = file_record(manifest_path)
    manifest = load(manifest_path)
    require(type(manifest) is dict and
            manifest.get('kind') == 'timelearner_native_pipeline_run_manifest' and
            type(manifest.get('schema_version')) is int and manifest['schema_version'] == 4 and
            manifest.get('sha256') == sha({k:v for k,v in manifest.items() if k != 'sha256'}) and
            manifest.get('operation') == 'train' and manifest.get('execution') == 'completed' and
            manifest.get('validity') == 'valid' and manifest.get('source_package_path') is None,
            'stopped_pipeline_closed_contained_cold_train_required')
    analysis = manifest.get('analysis')
    require(type(analysis) is dict and analysis.get('completed_boundary') is False and
            analysis.get('training_outcome') == 'budget_exhausted' and
            type(audit) is dict and audit.get('package_digest_verified') is True and
            audit.get('training_outcome') == 'budget_exhausted' and
            analysis.get('training_audit') == audit,
            'stopped_pipeline_complete_original_audit_required')
    execution_path = native/'execution.json'
    execution_record = file_record(execution_path)
    execution = load(execution_path)
    require(execution.get('sha256') == sha({k:v for k,v in execution.items() if k != 'sha256'}) and
            execution.get('kind') == 'timelearner_native_training_execution' and
            execution.get('execution') == 'completed' and
            execution.get('completed_boundary') is False and
            execution.get('training_outcome') == 'budget_exhausted' and
            execution.get('job_sha256') == manifest.get('job_sha256') and
            execution.get('model_revision') == audit.get('model_revision') and
            execution.get('package_path') == 'train_stopped_state.json',
            'stopped_pipeline_terminal_binding')
    packages = [r for r in execution.get('artifacts', [])
                if type(r) is dict and r.get('path') == 'train_stopped_state.json']
    require(len(packages) == 1 and type(packages[0].get('bytes')) is int and
            packages[0]['bytes'] > 0, 'stopped_pipeline_package_artifact')
    package_record = file_record(native/'train_stopped_state.json')
    require(package_record['size'] == packages[0]['bytes'] and
            package_record['sha256'] == packages[0].get('sha256'),
            'stopped_pipeline_package_bytes_changed')

    # Do not replace this with trusting manifest['analysis']. A checksum proves
    # binding to bytes; it cannot prove that their measurements were audited.
    evidence = audit_run_manifest(manifest_path)
    require(evidence.get('run_evidence_consistent') is True and evidence.get('operation') == 'train',
            'stopped_pipeline_full_primary_audit_required')
    require(file_record(manifest_path) == before and
            file_record(execution_path) == execution_record and
            file_record(native/'train_stopped_state.json') == package_record,
            'stopped_pipeline_source_changed_during_audit')
    return dict(proof_kind=manifest['kind'], source_manifest=before,
                consumed_job_sha256=manifest['job_sha256'],
                original_training_outcome='budget_exhausted',
                source_package=package_record, full_primary_reaudited=True,
                pipeline_evidence=evidence, training_completed=False,
                scientific_verdict=None)
