"""Actual Windows DATA replay with production audits and source waveforms.

Linux uses native_pipeline_worker directly. This explicitly scoped Windows
worker retains the owned Job/runtime evidence and calls the same native audit
and scorer. It never manufactures a training or calibration certificate.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import traceback


def _write(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)
        stream.write('\n')


def prepare(declaration):
    """Prepare DATA replay after closed, independently audited source trials.

    This replaces the former case-specific preparer. It reuses the complete
    physical export without decoding the large training history again.
    """
    fields={'kind','schema_version','source_controls','export_controls','source_audit',
        'destination','inputs','output','run_id','python_source','python_root'}
    if (type(declaration) is not dict or set(declaration)!=fields or
            declaration['kind']!='timelearner_physical_replay_preparation' or
            type(declaration['schema_version']) is not int or declaration['schema_version']!=1):
        raise ValueError('physical_replay_preparation_schema')
    actor=Path(declaration['python_source']).resolve(strict=True)
    sys.path.insert(0,str(actor));sys.dont_write_bytecode=True
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.runtime import file_record,runtime_content_identity,digest_json
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.native_pipeline_worker import validate_job,_artifact_records
    controls=Path(declaration['source_controls']).resolve(strict=True)
    exported=Path(declaration['export_controls']).resolve(strict=True)
    previous=json.loads((controls/'specification.json').read_bytes())
    export_spec=json.loads((exported/'specification.json').read_bytes())
    source=Path(previous['output']).resolve(strict=True)/'native'
    export_output=Path(export_spec['output']).resolve(strict=True)
    audit_path=Path(declaration['source_audit']).resolve(strict=True)
    audit=json.loads(audit_path.read_bytes());metrics=audit['native_evidence']['metrics']
    require(audit['kind']=='timelearner_prepared_diagnostic_independent_audit' and
            audit['complete_source_history_audited'] and audit['all_input_bytes_unchanged'] and
            audit['native_evidence']['frozen_model_verified'] and metrics['validity']=='valid' and
            len(metrics['trials'])==8 and Path(audit['output']).resolve(strict=True)==source.parent,
            'physical_replay_preparation_requires_complete_source_audit')
    require(Path(export_spec['sdk_source']).resolve(strict=True)==Path(previous['sdk_source']).resolve(strict=True),
            'physical_replay_preparation_sdk_mismatch')
    terminal=json.loads((export_output/'terminal.json').read_bytes())
    process=json.loads((export_output/'process-result.json').read_bytes())
    require(terminal['native_process_completed'] and terminal['physical_roundtrip_verified'] and
            process['execution']=='completed' and process['all_processes_closed'] and
            process['runtime_provenance']=='loaded_files_captured','physical_replay_export_not_closed')
    model_path=export_output/'native/model.json';model_before=file_record(model_path)
    model=json.loads(model_path.read_bytes())
    execution=json.loads((source/'execution.json').read_bytes())
    require(execution['sha256']==sha({k:v for k,v in execution.items() if k!='sha256'}),
            'physical_replay_preparation_source_execution_digest')
    _artifact_records(source,execution)
    require(model['sha256']==terminal['model_sha256'] and
            model['model_revision']==terminal['model_revision']==execution['model_revision']==metrics['model_revision'] and
            model['source_boundary']['sha256']==execution['model_sha256'],
            'physical_replay_preparation_export_source_mismatch')
    source_request=Path(previous['inputs']).resolve(strict=True)/'native-job-source.json'
    envelope=json.loads(source_request.read_bytes())
    require(envelope['kind']=='timelearner_checked_file_source_job' and envelope['schema_version']==1 and
            envelope['sha256']==sha({k:v for k,v in envelope.items() if k!='sha256'}) and
            envelope['source']['field']=='source_stopped' and envelope['job']['sha256']==
            execution['job_sha256']==audit['resolved_job_sha256'],
            'physical_replay_preparation_source_request_mismatch')
    original=envelope['job'];run_id=declaration['run_id']
    require(type(run_id) is str and bool(run_id),'physical_replay_preparation_run_id')
    job={k:v for k,v in original.items() if k not in
         ('sha256','source_stopped','conversion_spec','diagnostic_threshold')}
    job.update(kind='timelearner_native_physical_model_evaluation_job',schema_version=1,
        source_model_data=model,run_id=run_id,trials=[dict(t,run_id=run_id,
        trial_id=run_id+'/trial-'+str(i)) for i,t in enumerate(original['trials'])])
    job['sha256']=sha(job);validate_job('physical-model-evaluate',job,(model,))
    destination=Path(declaration['destination']).resolve(strict=True)
    inputs=Path(declaration['inputs']).absolute();output=Path(declaration['output']).absolute()
    base=Path('C:/Projects/TimeLearnerWorker').resolve(strict=True)
    require(os.name=='nt' and destination.is_relative_to(base/'controls') and
            inputs.is_relative_to(base/'jobs') and output.is_relative_to(base/'jobs') and
            not inputs.exists() and not output.exists() and inputs!=output,
            'physical_replay_preparation_fresh_worker_paths')
    inputs.mkdir(parents=True);os.link(model_path,inputs/'model.json');_write(inputs/'job.json',job)
    (destination/'worker.py').write_bytes((actor/'Scripts/StructTrain/TimeLearner/prepared_physical_replay.py').read_bytes())
    runtime=json.loads((exported/'runtime.json').read_bytes())
    backend=file_record(actor/'Scripts/StructTrain/TimeLearner/windows_process.py')
    require(backend['sha256']==runtime['windows_backend']['sha256'],
            'physical_replay_preparation_backend_implementation_changed')
    runtime['windows_backend']=backend;runtime['runtime_identity']=runtime_content_identity(runtime)
    runtime['runtime_fingerprint']=digest_json(runtime['runtime_identity']);_write(destination/'runtime.json',runtime)
    spec=dict(kind='timelearner_prepared_physical_replay',schema_version=1,python_source=str(actor),
        worker_root=declaration['python_root'],sdk_source=previous['sdk_source'],inputs=str(inputs),output=str(output),
        worker_sha256=file_record(destination/'worker.py')['sha256'],source_native=str(source),
        source_inventory={n:file_record(source/n) for n in ['execution.json',*[f'trial-{i}.json' for i in range(8)]]},
        source_request=file_record(source_request),source_audit=file_record(audit_path),
        source_model_revision=model['model_revision'],resolved_job_sha256=job['sha256'],
        input_inventory={p.name:dict(bytes=p.stat().st_size,sha256=file_record(p)['sha256']) for p in inputs.iterdir()},
        memory_bytes=2*1024**3,maximum_wall_seconds=3600,minimum_free_bytes=2*1024**3,
        maximum_output_bytes=512*1024**2,training_completed=False,scientific_verdict=None)
    _write(destination/'specification.json',spec)
    require(file_record(model_path)==model_before,'physical_replay_preparation_export_changed')
    result=dict(kind='timelearner_prepared_physical_replay_inputs',schema_version=1,
        source_model_revision=model['model_revision'],source_model_data_sha256=model['sha256'],
        source_audit=spec['source_audit'],source_request=spec['source_request'],native_trials=8,
        source_model_not_changed=True,native_execution_started=False,scientific_verdict=None)
    _write(destination/'proposal.json',result);return result


def run(controls):
    controls=Path(controls).resolve(strict=True)
    spec=json.loads((controls/'specification.json').read_bytes())
    sys.path.insert(0,spec['python_source']);sys.dont_write_bytecode=True
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.runtime import file_record,source_closure
    from Scripts.StructTrain.TimeLearner.native_cli import inspect_native_cli
    from Scripts.StructTrain.TimeLearner.native_pipeline_worker import validate_job,audit_execution
    from Scripts.StructTrain.TimeLearner.trial_response_comparison import trial_response_comparison
    from Scripts.StructTrain.TimeLearner.native_gate import _environment
    from Scripts.StructTrain.TimeLearner.windows_process import execute
    require(os.name=='nt' and spec['kind']=='timelearner_prepared_physical_replay' and
            spec['schema_version']==1,'physical_replay_worker_scope')
    base=Path('C:/Projects/TimeLearnerWorker').resolve(strict=True)
    inputs=Path(spec['inputs']).resolve(strict=True);output=Path(spec['output']).absolute()
    source=Path(spec['source_native']).resolve(strict=True)
    require(inputs.is_relative_to(base/'jobs') and output.is_relative_to(base/'jobs') and
            source.is_relative_to(base/'jobs') and not output.exists(),'physical_replay_paths')
    def inventory(directory):
        rows={}
        for p in directory.iterdir():
            require(p.is_file() and not p.is_symlink() and not p.is_junction(),'physical_replay_input_alias')
            f=file_record(p);rows[p.name]=dict(bytes=f['size'],sha256=f['sha256'])
        return rows
    output.mkdir()
    try:
        require(inventory(inputs)==spec['input_inventory'] and
                file_record(Path(__file__))['sha256']==spec['worker_sha256'],'physical_replay_input_changed')
        source_records={n:file_record(source/n) for n in spec['source_inventory']}
        require(source_records==spec['source_inventory'],'physical_replay_source_observation_changed')
        audit_path=Path(spec['source_audit']['path'])
        require(file_record(audit_path)==spec['source_audit'],'physical_replay_source_audit_changed')
        prior=json.loads(audit_path.read_bytes());prior_metrics=prior['native_evidence']['metrics']
        require(prior['complete_source_history_audited'] and prior['all_input_bytes_unchanged'] and
                prior['native_evidence']['frozen_model_verified'] and prior_metrics['validity']=='valid',
                'physical_replay_source_not_audited')
        model=json.loads((inputs/'model.json').read_bytes());job=json.loads((inputs/'job.json').read_bytes())
        execution=json.loads((source/'execution.json').read_bytes())
        require(model['model_revision']==spec['source_model_revision']==execution['model_revision']==
                prior_metrics['model_revision'] and model['source_boundary']['sha256']==execution['model_sha256'],
                'physical_replay_source_boundary_changed')
        validate_job('physical-model-evaluate',job,(model,))
        require(len(job['trials'])==8 and job['source_model_data']==model and
                job['sha256']==spec['resolved_job_sha256'],'physical_replay_eight_trial_scope')
        request_path=Path(spec['source_request']['path'])
        require(file_record(request_path)==spec['source_request'],'physical_replay_source_request_changed')
        original=json.loads(request_path.read_bytes())['job']
        require(original['sha256']==prior['resolved_job_sha256']==execution['job_sha256'] and
                job['criterion']==original['criterion'] and job['coverage_policy']==original['coverage_policy'] and
                [{k:v for k,v in t.items() if k not in ('run_id','trial_id')} for t in job['trials']]==
                [{k:v for k,v in t.items() if k not in ('run_id','trial_id')} for t in original['trials']],
                'physical_replay_protocol_changed')
        old={}
        for n in spec['source_inventory']:
            if n.startswith('trial-'):
                observation=json.loads((source/n).read_bytes())
                require(observation['sample_id'] not in old,'physical_replay_source_sample_duplicate')
                old[observation['sample_id']]=observation
        require(len(old)==8 and {t['sample_id'] for t in job['trials']}==set(old),
                'physical_replay_source_trial_set_changed')
        runtime=json.loads((controls/'runtime.json').read_bytes());sdk=Path(spec['sdk_source'])
        require(source_closure(sdk)==runtime['source_closure'],'physical_replay_sdk_changed')
        _write(output/'cli.json',inspect_native_cli(runtime,['physical-model-evaluate'],
            require_file_source=True,evidence_output=output))
        last=[0.]
        def monitor(state):
            if time.monotonic()-last[0]<1:return
            last[0]=time.monotonic();import shutil
            require(shutil.disk_usage(output).free>=spec['minimum_free_bytes'],'physical_replay_disk_floor')
            total=0
            for p in output.rglob('*'):
                try:
                    if p.is_file():total+=p.stat().st_size
                except FileNotFoundError:pass
            require(total<=spec['maximum_output_bytes'],'physical_replay_output_budget')
        args=['--app-ini',runtime['app_ini']['path'],'--timelearner-physical-model-evaluate',
              str(inputs/'job.json'),'--timelearner-output',str(output/'native')]
        with _environment({k:runtime['loader_environment'].get(k)
                           for k in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}):
            process=execute(runtime,args,Path(runtime['executable']['path']).parent,output/'process',
                memory_bytes=spec['memory_bytes'],maximum_processes=64,
                maximum_wall_seconds=spec['maximum_wall_seconds'],lock_file=base/'locks/worker.lock',
                cooperative_capture=True,monitor=monitor)
        _write(output/'process-result.json',process)
        require(process['execution']=='completed' and process['all_processes_closed'] and
                process['runtime_provenance']=='loaded_files_captured','physical_replay_native_incomplete')
        audited=audit_execution('physical-model-evaluate',output/'native',job,(model,))
        _write(output/'audit.json',audited)
        metrics=audited['metrics']
        require(audited['frozen_model_verified'] and metrics['validity']=='valid' and metrics['data_only'] and
                len(metrics['trials'])==8 and metrics['effective_threshold']==prior_metrics['effective_threshold'],
                'physical_replay_native_audit_invalid')
        rows=[]
        with trial_response_comparison(model,physical_data=True) as compare:
            for index,trial in enumerate(job['trials']):
                observed=json.loads((output/'native'/f'trial-{index}.json').read_bytes())
                expected=old[observed['sample_id']]
                comparison=compare(expected,observed)
                rows.append(dict(trial_id=observed['trial_id'],sample_id=observed['sample_id'],
                    samples=len(observed['samples']),spike_count=observed['spike_count'],
                    maximum_absolute_sample_difference=comparison['maximum_absolute_sample_difference'],
                    waveform_difference_reason=next(iter(comparison['difference_reasons']),None),
                    waveform_preserved=comparison['waveforms_equal_within_declared_tolerance'],
                    stimulus_and_spike_events_preserved=comparison['stimulus_and_spike_events_equal'],
                    response_comparison=comparison))
        require(inventory(inputs)==spec['input_inventory'] and source_closure(sdk)==runtime['source_closure'] and
                {n:file_record(source/n) for n in source_records}==source_records and
                file_record(audit_path)==spec['source_audit'] and
                file_record(request_path)==spec['source_request'],'physical_replay_source_changed_after_execution')
        preserved=all(r['waveform_preserved'] and r['stimulus_and_spike_events_preserved'] for r in rows)
        _write(output/'terminal.json',dict(kind='timelearner_actual_windows_physical_replay',schema_version=1,
            execution='completed',validity='valid',model_revision=model['model_revision'],
            source_model_data_sha256=model['sha256'],threshold=metrics['effective_threshold'],
            counts=metrics['pooled_counts'],rows=rows,all_eight_waveforms_and_events_preserved=preserved,
            transfer_valid=preserved,training_certificate_transferred=False,controller_checkpoint_restored=False,
            training_completed=False,independently_heldout_evaluation=False,scientific_verdict=None))
    except BaseException as e:
        _write(output/'exception.json',dict(reason=str(e),traceback=traceback.format_exc(),scientific_verdict=None))
        raise


def main():
    p=argparse.ArgumentParser()
    modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--controls');modes.add_argument('--prepare-specification')
    args=p.parse_args()
    if args.prepare_specification:
        print(json.dumps(prepare(json.loads(Path(args.prepare_specification).read_bytes())),allow_nan=False))
    else:run(args.controls)


if __name__=='__main__':main()
