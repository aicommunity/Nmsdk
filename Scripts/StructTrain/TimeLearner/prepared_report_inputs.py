"""Bind visual-report inputs to the bytes seen by the completed full audit.

Only the execution/design/eight observation subset used for drawing is read.
This does not replace the full model/history auditor or authenticate a file.
"""
from pathlib import Path

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import load, require
from .recognition_metrics import load_diagnostic_evaluation
from .runtime import file_record

NAMES=('execution.json','evaluation.json',*(f'trial-{i}.json'for i in range(8)))


def capture_report_primary(native):
    native=Path(native).resolve(strict=True);files={}
    for name in NAMES:
        path=native/name
        require(path.is_file() and not path.is_symlink() and
            not getattr(path,'is_junction',lambda:False)(),'prepared_report_primary_alias_or_missing')
        row=file_record(path);files[name]=dict(bytes=row['size'],sha256=row['sha256'])
    return dict(kind='timelearner_full_audit_report_primary_binding',schema_version=1,
                native_directory=str(native),files=files)


def load_report_inputs(audit_path, *, native_directory=None):
    audit_path=Path(audit_path).resolve(strict=True);audit=load(audit_path)
    require(audit['kind']=='timelearner_prepared_diagnostic_independent_audit' and
        audit['complete_source_history_audited'] is True and audit['all_input_bytes_unchanged'] is True and
        audit['native_evidence']['frozen_model_verified'] is True,'prepared_report_requires_complete_audit')
    binding=audit.get('report_primary_binding')
    require(type(binding) is dict and set(binding)=={'kind','schema_version','native_directory','files'} and
        binding['kind']=='timelearner_full_audit_report_primary_binding' and
        type(binding['schema_version']) is int and binding['schema_version']==1 and
        set(binding['files'])==set(NAMES),'prepared_report_legacy_audit_requires_bound_reaudit')
    native=Path(native_directory).resolve(strict=True) if native_directory is not None else Path(audit['output'])/'native'
    current=capture_report_primary(native)
    require(current['files']==binding['files'],'prepared_report_audited_primary_changed')
    execution=load(native/'execution.json')
    require(execution['sha256']==sha({k:v for k,v in execution.items()if k!='sha256'}) and
        execution['kind']=='timelearner_native_diagnostic_evaluation_execution' and
        type(execution['schema_version']) is int and execution['schema_version']==1 and
        execution['execution']=='completed' and execution['evaluation_verdict'] is None and
        execution['job_sha256']==audit['resolved_job_sha256'], 'prepared_report_execution_changed')
    records=execution['artifacts'];by_name={r['path']:r for r in records}
    require(len(by_name)==len(records),'prepared_report_duplicate_native_artifact')
    for name in NAMES[1:]:
        require(by_name[name]==dict(path=name,**binding['files'][name]),'prepared_report_primary_record_changed')
    spec,observations=load_diagnostic_evaluation(native/'evaluation.json');metrics=audit['native_evidence']['metrics']
    require(metrics['validity']=='valid' and not metrics['invalid_trial_ids'] and
        len(spec['trials'])==len(observations)==len(metrics['trials'])==8 and
        execution['expected_trials']==execution['observed_trials']==8 and
        execution['run_id']==spec['run_id']==metrics['run_id'] and
        execution['model_revision']==spec['model_revision']==metrics['model_revision'] and
        spec['criterion']==metrics['criterion'],'prepared_report_incomplete_or_changed_metrics')
    require(capture_report_primary(native)==current,'prepared_report_primary_changed_during_read')
    return dict(audit=audit,spec=spec,observations=observations,metrics=metrics,native=native,
                primary_binding=current,original_primary_binding=binding)
