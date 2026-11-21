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
                maximum_wall_seconds=spec['maximum_wall_seconds'],lock_file=controls/'native-replay.lock',
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
    p=argparse.ArgumentParser();p.add_argument('--controls',required=True)
    run(p.parse_args().controls)


if __name__=='__main__':main()
