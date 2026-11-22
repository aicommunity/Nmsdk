"""Prepare eight full diagnostic trials after a completed primary Train audit.

Reuse the complete immutable source namespace. Decode its package once and
reference it in the resolved job without copying its large history tree.
The existing prepared_diagnostic executor performs the native run afterwards.
"""
import argparse
import json
import os
from pathlib import Path

from .job_source_transport import make_envelope
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import load, require
from .prepared_diagnostic import inventory
from .runtime import digest_json, file_record, runtime_content_identity


def _write(path, value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')


def prepare(declaration):
    expected={'kind','schema_version','source_native','source_proof','source_audit','template_envelope',
              'native_runtime','sdk_source','destination','inputs','output','run_id','python_source'}
    require(type(declaration) is dict and set(declaration)==expected and
            declaration['kind']=='timelearner_stopped_baseline_preparation' and
            type(declaration['schema_version']) is int and declaration['schema_version']==1,
            'stopped_baseline_preparation_schema')
    native=Path(declaration['source_native']).resolve(strict=True)
    destination=Path(declaration['destination']).resolve(strict=True)
    inputs=Path(declaration['inputs']).absolute();output=Path(declaration['output']).absolute()
    require(not inputs.exists() and not output.exists() and
            not inputs.is_relative_to(native) and not native.is_relative_to(inputs),
            'stopped_baseline_fresh_separate_paths')
    proof_path=Path(declaration['source_proof']).resolve(strict=True)
    audit_path=Path(declaration['source_audit']).resolve(strict=True)
    proof=load(proof_path);audit=load(audit_path)
    require(proof['kind']=='timelearner_closed_matched_count_training_audit' and
            Path(proof['native']).resolve(strict=True)==native and
            proof['source_package_full_decodes']==1 and proof['original_outcome_unchanged'] is True and
            proof['full_primary_audit']['completed_boundary'] is False and
            proof['full_primary_audit']['training_outcome']=='budget_exhausted' and
            audit==proof['full_primary_audit']['training_audit'] and
            audit['package_digest_verified'] is True and audit['training_outcome']=='budget_exhausted',
            'stopped_baseline_requires_complete_original_primary_audit')
    source=native/'train_stopped_state.json';before=file_record(source)
    require(before==proof['source_package'],'stopped_baseline_audited_package_bytes_changed')
    package=load(source)
    require(package['kind']=='timelearner_stopped_state' and package['state_kind']=='diagnostic' and
            package['certificate'] is None and package['training_outcome']=='budget_exhausted' and
            package['model_revision']==audit['model_revision'],'stopped_baseline_source_kind_or_model')
    model=package['configuration']['model']
    require(model['frequency_hz']==2000 and len(model['initial_isi'])==4,
            'stopped_baseline_verified_clock_and_dimension_required')
    donor=load(Path(declaration['template_envelope']))
    require(donor['kind']=='timelearner_checked_file_source_job' and donor['schema_version']==1 and
            donor['sha256']==sha({k:v for k,v in donor.items() if k!='sha256'}),
            'stopped_baseline_template_envelope')
    criterion=dict(id='post_anchor_target_whole_window_foil_v1',anchor='onset',begin_offset=0.,
                   end_offset=None,reject_target_outside_window=True)
    template=donor['job'];trials=template['trials'];run_id=declaration['run_id']
    require(type(run_id) is str and bool(run_id) and template['criterion']==criterion and
            len(trials)==len({t['sample_id'] for t in trials})==len({t['pattern_hash'] for t in trials})==8 and
            sum(t['label']=='target' for t in trials)==1 and sum(t['label']=='foil' for t in trials)==7 and
            next(t['pattern_isi'] for t in trials if t['label']=='target')==model['initial_isi'] and
            all(t['pattern_hash']==sha(t['pattern_isi']) and t['duration']==2 and
                t['maximum_samples']==4005 and t['reset_policy']=='reset_per_trial' and
                t['record_threshold_potential'] is True for t in trials),
            'stopped_baseline_complete_original_matrix_required')
    job=dict(kind='timelearner_native_diagnostic_evaluation_job',schema_version=1,
        owner_class='NNeuronTimeLearnerBranch' if model['branch'] else 'NNeuronTimeLearner',
        implementation_id=package['implementation_id'],source_stopped=package,
        conversion_spec=dict(schema_version=1,mode='identity',resistance_bounds=[]),
        maximum_model_ticks=8*4004,run_id=run_id,coverage_policy='per_trial_windows',criterion=criterion,
        trials=[dict(t,run_id=run_id,trial_id=run_id+'/trial-'+str(i)) for i,t in enumerate(trials)])
    job['sha256']=sha(job)
    # This is a binding to an already completed full audit, not permission to
    # omit history. The ordinary native codec still checks the complete source.
    inputs.mkdir(parents=True);staged=inputs/'source';staged.mkdir()
    for path in native.rglob('*'):
        require(not path.is_symlink() and not getattr(path,'is_junction',lambda:False)(),
                'stopped_baseline_source_alias')
        target=staged/path.relative_to(native)
        if path.is_dir():target.mkdir(parents=True,exist_ok=True)
        else:
            require(path.is_file(),'stopped_baseline_nonregular_source')
            target.parent.mkdir(parents=True,exist_ok=True);os.link(path,target)
    envelope=make_envelope(job,staged/source.name,inputs)
    _write(inputs/'native-job-source.json',envelope)
    python_source=Path(declaration['python_source']).resolve(strict=True)
    worker=python_source/'Scripts/StructTrain/TimeLearner/prepared_diagnostic.py'
    (destination/'worker.py').write_bytes(worker.read_bytes())
    runtime=load(Path(declaration['native_runtime']))
    if os.name=='nt':
        backend=file_record(python_source/'Scripts/StructTrain/TimeLearner/windows_process.py')
        runtime['windows_backend']=backend
        runtime['build_flags']=dict(runtime['build_flags'],windows_backend_sha256=backend['sha256'])
        runtime['runtime_identity']=runtime_content_identity(runtime)
        runtime['runtime_fingerprint']=digest_json(runtime['runtime_identity'])
    _write(destination/'runtime.json',runtime)
    spec=dict(kind='timelearner_prepared_diagnostic',schema_version=1,job_id=output.name,
        execution_root=str(inputs.parent.parent),python_source=str(python_source),sdk_source=declaration['sdk_source'],
        inputs=str(inputs),output=str(output),worker_sha256=file_record(destination/'worker.py')['sha256'],
        input_inventory=inventory(inputs,file_record),resolved_job_sha256=job['sha256'],
        source_package_sha256=package['sha256'],source_model_revision=package['model_revision'],
        source_audit=dict(path=str(audit_path),sha256=file_record(audit_path)['sha256']),
        memory_bytes=16*1024**3,maximum_wall_seconds=7200,
        disk=dict(minimum_free_bytes=4*1024**3,maximum_output_bytes=24*1024**3),
        lock_file=str(inputs.parent.parent/'locks/worker.lock'))
    _write(destination/'specification.json',spec)
    require(file_record(source)==before and file_record(staged/source.name)['sha256']==before['sha256'],
            'stopped_baseline_source_changed_during_preparation')
    result=dict(kind='timelearner_stopped_baseline_preparation_result',schema_version=1,
        source_model_revision=package['model_revision'],source_package_sha256=package['sha256'],
        source_proof=file_record(proof_path),source_audit=spec['source_audit'],resolved_job_sha256=job['sha256'],
        staged_files=len(spec['input_inventory']),complete_source_namespace_preserved=True,
        source_decoded_once_without_history_copy=True,original_outcome='budget_exhausted',
        initial_threshold=model['initial_threshold'],trials=8,inputs=str(inputs),output=str(output),
        native_execution_started=False,scientific_verdict=None)
    _write(destination/'proposal.json',result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('declaration',type=Path)
    args=parser.parse_args();print(json.dumps(prepare(load(args.declaration)),allow_nan=False))


if __name__=='__main__':main()
