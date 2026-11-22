"""An audited DATA baseline and unchanged source files for new frozen studies."""
from contextlib import contextmanager
from pathlib import Path

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest
from .recognition_metrics import load_physical_model_data_evaluation
from .runtime import file_record


@contextmanager
def frozen_physical_source(declaration):
    source = Path(declaration['source_manifest']).resolve(strict=True)
    comparison = Path(declaration['source_comparison']).resolve(strict=True)
    job_path = source.parent/'input/job.json'
    models = list((source.parent/'input/source').glob('*.json'))
    require(len(models) == 1, 'frozen_source_model_ambiguous')
    model_path = models[0]
    paths = [source, comparison, job_path, model_path]
    records = {str(p):file_record(p) for p in paths}
    require(records[str(source)]['sha256'] == declaration['source_manifest_sha256'] and
            records[str(comparison)]['sha256'] == declaration['source_comparison_sha256'],
            'frozen_source_declared_binding_changed')
    audit = audit_run_manifest(source); baseline = load(source); result = load(comparison)
    require(audit['run_evidence_consistent'] and baseline['operation'] == 'physical-model-evaluate' and
            baseline['execution'] == 'completed' and baseline['validity'] == 'valid',
            'frozen_source_requires_complete_audited_DATA_run')
    job = load(job_path); model = load(model_path); metrics = baseline['analysis']['metrics']
    require(job['kind'] == 'timelearner_native_physical_model_evaluation_job' and
            job['coverage_policy'] == 'per_trial_windows' and job['source_model_data'] == model and
            model['model_revision'] == declaration['model_revision'], 'frozen_source_model_or_protocol_changed')
    require(metrics['data_only'] and metrics['validity'] == 'valid' and
            metrics['model_revision'] == result['model_revision'] == model['model_revision'] and
            metrics['effective_threshold'] == declaration['threshold'] and
            result['source_model_data_sha256'] == model['sha256'] and
            result['counts'] == metrics['pooled_counts'] and result['all_eight_waveforms_and_events_preserved'],
            'frozen_source_roundtrip_or_metrics_changed')
    spec, observations = load_physical_model_data_evaluation(source.parent/'native/evaluation.json')
    require(len(job['trials']) == len(metrics['trials']) == len(observations) == 8 and
            spec['model_revision'] == model['model_revision'] and
            len({t['sample_id'] for t in job['trials']}) == 8 and
            sum(t['label'] == 'target' for t in job['trials']) == 1 and
            all(t['reset_policy'] == 'reset_per_trial' and t['record_threshold_potential'] is True
                for t in job['trials']), 'frozen_source_requires_eight_recorded_unique_trials')
    yield dict(job=job, model=model, metrics=metrics, observations=observations,
               model_path=model_path, records=records)
    require({str(p):file_record(p) for p in paths} == records and
            model['sha256'] == sha({k:v for k,v in model.items() if k != 'sha256'}),
            'frozen_source_changed_during_study')
