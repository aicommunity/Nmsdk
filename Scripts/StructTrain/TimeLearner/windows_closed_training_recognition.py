"""Continue a closed, audited Windows Train through DATA and actual recognition.

The maintained module owns preparation and waits for exact predecessors. It
never restarts Train, treats a process exit as convergence, or scores a template.
Primary publication to M40 remains separate from preparing a lossless bundle.
"""
import argparse
from copy import deepcopy
import ctypes
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import sys
import time
import traceback

from .native_evidence import load, require
from .runtime import file_record

BASE = Path('C:/Projects/TimeLearnerWorker')
SOURCE = Path(__file__).resolve().parents[3]
MODULE = 'Scripts.StructTrain.TimeLearner.windows_closed_training_recognition'
GIB = 1024**3
FIELDS = {'kind','schema_version','job_id','python_root','source_case','source_job',
          'source_full_audit','runtime_manifest','stimulus_source','predecessors',
          'expected_job_sha256','maximum_wait_seconds','maximum_whole_seconds',
          'preparation_wall_seconds','native_evaluation_wall_seconds'}


def _hex(value, size):
    return type(value) is str and len(value) == size and all(c in '0123456789abcdef' for c in value)


def _windows_path(value):
    return (type(value) is str and PureWindowsPath(value).is_absolute() and
            '..' not in PureWindowsPath(value).parts and
            PureWindowsPath(value).is_relative_to(PureWindowsPath('C:/Projects/TimeLearnerWorker')))


def validate_request(q):
    require(type(q) is dict and set(q) == FIELDS and
            q['kind'] == 'timelearner_windows_closed_training_recognition' and
            type(q['schema_version']) is int and q['schema_version'] == 1,
            'closed_training_request_schema')
    require(type(q['job_id']) is str and 1 <= len(q['job_id']) <= 60 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in q['job_id']) and
            _hex(q['python_root'],40) and _hex(q['expected_job_sha256'],64),
            'closed_training_request_identity')
    for key in ('source_case','source_job','source_full_audit','runtime_manifest','stimulus_source'):
        r=q[key]
        require(type(r) is dict and set(r)=={'path','sha256','size'} and
                _windows_path(r['path']) and _hex(r['sha256'],64) and
                type(r['size']) is int and 0 < r['size'] <= 4*GIB,
                'closed_training_request_record:'+key)
    require(type(q['predecessors']) is list and len(q['predecessors']) == 2,
            'closed_training_two_exact_predecessors')
    paths=[]
    for pred in q['predecessors']:
        require(type(pred) is dict and set(pred)=={'request','owner'},'closed_training_predecessor_schema')
        r=pred['request'];owner=pred['owner']
        require(type(r) is dict and set(r)=={'path','sha256','size'} and
                _windows_path(r['path']) and PureWindowsPath(r['path']).name=='request.json' and
                _hex(r['sha256'],64) and type(r['size']) is int and r['size']>0,
                'closed_training_predecessor_request')
        require(type(owner) is dict and set(owner)=={'pid','executable','creation_filetime'} and
                type(owner['pid']) is int and owner['pid']>0 and
                type(owner['creation_filetime']) is str and owner['creation_filetime'].isdigit() and
                int(owner['creation_filetime'])>0 and type(owner['executable']) is str and
                PureWindowsPath(owner['executable']).is_absolute(), 'closed_training_predecessor_owner')
        paths.append(PureWindowsPath(r['path']))
    require(len(set(paths))==2,'closed_training_duplicate_predecessor')
    for key in ('maximum_wait_seconds','maximum_whole_seconds','preparation_wall_seconds',
                'native_evaluation_wall_seconds'):
        require(type(q[key]) is int and q[key]>0,'closed_training_integer_budget:'+key)
    require(q['maximum_wait_seconds']<=86400 and q['preparation_wall_seconds']<=7200 and
            q['native_evaluation_wall_seconds']<=36000 and
            q['maximum_wait_seconds']+q['preparation_wall_seconds']+
            2*q['native_evaluation_wall_seconds']+10800 <= q['maximum_whole_seconds'] <= 172800,
            'closed_training_whole_budget')
    return q


def validate_source_metadata(q, case, job, proof, execution):
    """Bind the actual terminal graph and outcome, without loading its history."""
    from .model_identity import canonical_model_sha256 as sha
    require(case['kind']=='timelearner_count_candidate_limit_training' and
            case['job_file']==q['source_job'] and _windows_path(case['output']) and
            _windows_path(case['sdk_source']), 'closed_training_actual_case')
    require(job['sha256']==sha({k:v for k,v in job.items() if k!='sha256'})==
            q['expected_job_sha256']==proof['job_sha256']==execution['job_sha256'],
            'closed_training_actual_job')
    require(proof['process_closed'] is True and proof['original_outcome_unchanged'] is True and
            execution['kind']=='timelearner_native_training_execution' and execution['execution']=='completed' and
            execution['training_outcome']==proof['training_outcome'] and
            type(execution['completed_boundary']) is bool and
            execution['completed_boundary']==proof['completed_boundary'] and
            execution['model_revision']==proof['full_primary_audit']['training_audit']['model_revision'],
            'closed_training_actual_terminal_boundary')
    filename=execution['package_path']
    require(filename == ('train_learned_state.json' if execution['completed_boundary'] else 'train_stopped_state.json') and
            execution['sha256']==sha({k:v for k,v in execution.items() if k!='sha256'}),
            'closed_training_actual_execution')
    records=[r for r in execution['artifacts'] if r['path']==filename]
    require(len(records)==1 and type(records[0]['bytes']) is int and
            0<records[0]['bytes']<=4*GIB and _hex(records[0]['sha256'],64),
            'closed_training_actual_package_artifact')
    return dict(job_sha256=job['sha256'],model_revision=execution['model_revision'],
                training_outcome=execution['training_outcome'],completed_boundary=execution['completed_boundary'],
                package=deepcopy(records[0]))


def evaluation_job(q, source_job, model, stimulus, phase):
    from .model_identity import canonical_model_sha256 as sha
    from .native_pipeline_worker import validate_job
    from .physical_threshold_proposal import CRITERION
    rows=deepcopy(stimulus['job']['trials']);target=[r for r in rows if r['label']=='target']
    require(len(rows)==8 and len(target)==1 and len({r['sample_id']for r in rows})==8 and
            len({r['pattern_hash']for r in rows})==8 and
            stimulus['job']['criterion']==CRITERION and
            target[0]['pattern_isi']==source_job['configuration']['model']['initial_isi']==
            model['configuration']['model']['initial_isi'] and
            model['configuration']['model']['frequency_hz']==2000,
            'closed_training_actual_stimulus_protocol')
    name=q['job_id']+'-'+phase
    for i,row in enumerate(rows):
        require(row['duration']==2 and row['maximum_samples']==4005 and row['reset_policy']=='reset_per_trial' and
                row['record_threshold_potential'] is True and row['pattern_hash']==sha(row['pattern_isi']),
                'closed_training_complete_evaluation_window')
        row.update(run_id=name,trial_id=name+'/trial-'+str(i))
    job=dict(kind='timelearner_native_physical_model_evaluation_job',schema_version=1,
        owner_class=source_job['owner_class'],implementation_id=model['implementation_id'],
        maximum_model_ticks=32032,run_id=name,coverage_policy='per_trial_windows',criterion=deepcopy(CRITERION),
        trials=rows,source_model_data=model)
    job['sha256']=sha(job);validate_job('physical-model-evaluate',job,(model,))
    return job


def evaluation_condition(q, job, runtime):
    from .condition import ConditionSpec,artifact
    from .physical_threshold_proposal import RULE
    from .runtime import runtime_content_identity
    model=job['source_model_data']
    payloads=dict(algorithm=dict(operation='physical-model-evaluate',implementation_id=job['implementation_id'],
        native_runtime_content=runtime_content_identity(runtime)),model_spec=model['configuration']['model'],
        storage_profiles=dict(effective_graph_sha256=model['model_revision']),
        initial_state=dict(source_training_job_sha256=q['expected_job_sha256'],frozen_model=model['model_revision']),
        training_plan=dict(new_training=False),input_data=dict(trials=[{k:v for k,v in r.items()
            if k not in ('run_id','trial_id')}for r in job['trials']]),
        presentation_protocol=dict(frequency_hz=2000,reset_policy='reset_per_trial',duration_seconds=2),
        calibration_spec=dict(protocol='historical_same_matrix',rule=RULE,original_threshold=100,
            one_candidate=True,actual_confirmation_required=True,
            effective_threshold=model['neuron']['metadata']['calibration']['threshold']),
        evaluation_spec=dict(criterion=job['criterion'],coverage_policy=job['coverage_policy']),
        execution_policy=dict(native_memory_bytes=8*GIB,native_wall_seconds=q['native_evaluation_wall_seconds'],
            automatic_retry=False),randomness_spec=dict(stochastic_source_declared=False))
    artifacts={k:artifact(k,v)for k,v in payloads.items()}
    condition=ConditionSpec(controller_version=2,amplitude_goal='captured_per_input',
        **{k:v['sha256']for k,v in artifacts.items()});condition.resolve({v['sha256']:v for v in artifacts.values()})
    require(ConditionSpec.loads(condition.dumps())==condition,'closed_training_condition_roundtrip')
    return dict(condition=condition.to_object(),fingerprint=condition.fingerprint,artifacts=artifacts,
                descriptor_integrity_only=True,scientific_verdict=None)


def _bound_record(r):
    p=Path(r['path']);require(p.resolve(strict=True)==p and not p.is_symlink() and not p.is_junction() and
                             file_record(p)==r,'closed_training_bound_file_changed')
    return p


def _context(request):
    from .owned_python_job import _source_snapshot
    request=Path(request).resolve(strict=True);q=validate_request(load(request))
    require(os.name=='nt' and request==BASE/'controls'/q['job_id']/'request.json' and
            SOURCE.is_relative_to(BASE) and BASE.resolve(strict=True)==BASE,'closed_training_owned_paths')
    _source_snapshot(SOURCE,q['python_root'])
    for key in ('source_case','source_job','source_full_audit','runtime_manifest','stimulus_source'):_bound_record(q[key])
    for pred in q['predecessors']:_bound_record(pred['request'])
    return q,request.parent


def _all_owned_closed(directory,api,kernel):
    from .windows_stopped_recognition_study import live
    return all(not live(api,kernel,load(p))for p in directory.rglob('owned-process.json'))


def _source_binding(q,api,kernel):
    case=load(Path(q['source_case']['path']));job=load(Path(q['source_job']['path']));proof=load(Path(q['source_full_audit']['path']))
    native=Path(case['output'])/'train/native';execution=load(native/'execution.json')
    result=validate_source_metadata(q,case,job,proof,execution)
    require(file_record(native/'execution.json')==proof['source_execution'] and
            _all_owned_closed(Path(case['output']),api,kernel),'closed_training_source_still_live_or_changed')
    package=native/result['package']['path'];actual=file_record(package)
    require(actual['size']==result['package']['bytes'] and actual['sha256']==result['package']['sha256'],
            'closed_training_package_bytes_changed')
    return dict(result,source_package=actual,source_execution=proof['source_execution'],
        source_full_audit=q['source_full_audit'],source_case=q['source_case'],
        original_output=case['output'],sdk_source=case['sdk_source'],scientific_verdict=None)


def primary_worker(request):
    """Bounded subprocess; no component calculation or template reconstruction."""
    from .physical_data_projection import project_file
    from .portable_primary import create_native_bundle
    from .windows_stopped_recognition_study import write
    q,c=_context(request);binding=load(c/'actual-source-binding.json');out=BASE/'jobs'/(q['job_id']+'-preparation')
    require(out.is_dir() and not any(out.iterdir()),'closed_training_fresh_preparation_output')
    files={}
    roots={'actual-training':Path(binding['original_output']),
           'source-case-controls':Path(q['source_case']['path']).parent,
           'original-audit-controls':Path(q['predecessors'][0]['request']['path']).parent}
    for role,where in roots.items():
        for p in where.rglob('*'):
            relative=p.relative_to(where)
            if '.git' in relative.parts or p.suffix.lower()=='.ps1':continue
            require(not p.is_symlink() and not p.is_junction(),'closed_training_archive_alias')
            if p.is_file():files[role+'/'+relative.as_posix()]=p
    for name in ('request.json','actual-source-binding.json','controls.bundle'):files['current-declaration/'+name]=c/name
    runtime=load(Path(q['runtime_manifest']['path']));exe=Path(runtime['executable']['path'])
    require(file_record(exe)==runtime['executable'],'closed_training_original_executable_changed')
    files['original-native-runtime/'+exe.name]=exe
    loaded=json.loads((Path(binding['original_output'])/'train/process/loaded-files.json').read_bytes())
    require(type(loaded) is list and bool(loaded),'closed_training_loaded_module_inventory_missing')
    for i,record in enumerate(loaded):
        path=Path(record['path']);actual=file_record(path)
        require(actual['sha256']==record['sha256'] and actual['size']==record['size'],
                'closed_training_recorded_module_bytes_unavailable')
        files['original-native-runtime/loaded/'+str(i).zfill(3)+'-'+path.name]=path
    write(out/'recorded-loaded-files.json',dict(files=loaded))
    files['recorded-loaded-files.json']=out/'recorded-loaded-files.json'
    require(len(files)<=30000 and sum(p.stat().st_size for p in files.values())<=16*GIB,
            'closed_training_primary_pack_admission')
    packed=create_native_bundle(files,out/'packed-primary',dictionary_bytes=32*1024**2,deduplicate_content=True)
    write(out/'primary-pack-result.json',dict(members=len(packed['members']),expanded_bytes=packed['expanded_bytes'],
        objects={n:file_record(out/'packed-primary'/n)for n in ('bundle.json','primary.tar.xz')},
        actual_recorded_loaded_module_bytes_archived=len(loaded),source_Train_outcome=binding['training_outcome'],
        source_completed_boundary=binding['completed_boundary'],external_M40_publication_pending=True,scientific_verdict=None))
    projection=project_file(Path(binding['source_package']['path']),out/'physical-model-DATA.json',
        expected_bytes=binding['source_package']['size'],expected_sha256=binding['source_package']['sha256'],
        maximum_source_bytes=4*GIB,maximum_output_bytes=128*1024**2)
    require(projection['model_revision']==binding['model_revision'],'closed_training_projection_graph_changed')
    write(out/'physical-projection.json',projection)
    write(out/'terminal.json',dict(execution='completed',validity='valid',source_model_revision=binding['model_revision'],
        source_package=binding['source_package'],no_native_calculation=True,scientific_verdict=None))


def supervise(request):
    from .owned_python_job import _source_snapshot
    from .windows_stopped_recognition_study import _kernel,live,write,state
    from .runtime import runtime_content_identity,digest_json
    from .windows_process import execute
    from .native_gate import _environment
    from .prepared_physical_export import prepare_conversion,prepare_threshold,run as physical_edit
    from . import prepared_physical_evaluation as evaluation
    from .prepared_physical_repeat import _closed_evaluation
    from .physical_threshold_proposal import propose_physical_same_matrix_threshold
    from .recognition_metrics import load_physical_model_data_evaluation
    from .trial_response_timing import summarize_trial_timing
    request=Path(request).resolve(strict=True)
    q,c=_context(request);api,kernel=_kernel();write(c/'owner.json',dict(pid=os.getpid(),**api.identity(kernel.GetCurrentProcess())))
    bound={str(request):file_record(Path(request))}
    for key in ('source_case','source_job','source_full_audit','runtime_manifest','stimulus_source'):bound[q[key]['path']]=q[key]
    for pred in q['predecessors']:bound[pred['request']['path']]=pred['request']
    begun=time.monotonic()
    def guard():
        require(time.monotonic()-begun<q['maximum_whole_seconds'] and not(c/'cancel.request').exists(),
                'closed_training_budget_or_cancel')
        require(all(file_record(Path(p))==r for p,r in bound.items()),'closed_training_source_changed')
    def capacity(minimum):
        started=time.monotonic()
        while True:
            guard();m=api.Memory();m.length=ctypes.sizeof(m);api.check(api.memory_status(ctypes.byref(m)))
            if m.available_physical>=minimum and shutil.disk_usage(BASE).free>=10*GIB:return
            require(time.monotonic()-started<q['maximum_wait_seconds'],'closed_training_capacity_wait_budget')
            state(c/'waiting.json',dict(phase='capacity',available_physical_bytes=m.available_physical));time.sleep(30)
    try:
        while True:
            guard();observed=[]
            for pred in q['predecessors']:
                parent=Path(pred['request']['path']).parent
                require(load(parent/'owner.json')==pred['owner'] and not(parent/'exception.json').exists(),
                        'closed_training_exact_predecessor_failed_or_replaced')
                alive=live(api,kernel,pred['owner']);observed.append(dict(owner=pred['owner'],live=alive))
                if not alive:
                    terminal=load(parent/'terminal.json')
                    require(terminal['execution']=='completed' and terminal['validity']=='valid',
                            'closed_training_predecessor_not_accepted')
            if all(not x['live']for x in observed):break
            require(time.monotonic()-begun<q['maximum_wait_seconds'],'closed_training_predecessor_wait_budget')
            state(c/'waiting.json',dict(phase='exact_predecessors',observed=observed,preparation_or_native_started=False));time.sleep(30)
        capacity(18*GIB);binding=_source_binding(q,api,kernel);write(c/'actual-source-binding.json',binding)
        original=load(Path(q['runtime_manifest']['path']));backend=file_record(SOURCE/'Scripts/StructTrain/TimeLearner/windows_process.py')
        require(backend['sha256']==original['windows_backend']['sha256'],'closed_training_backend_bytes_changed')
        runtime=deepcopy(original);runtime['windows_backend']=backend
        runtime['runtime_identity']=runtime_content_identity(runtime);runtime['runtime_fingerprint']=digest_json(runtime['runtime_identity'])
        require(runtime['runtime_fingerprint']==original['runtime_fingerprint'],'closed_training_runtime_content_changed')
        write(c/'native-runtime.json',runtime)
        preparation=BASE/'jobs'/(q['job_id']+'-preparation');require(not preparation.exists(),'closed_training_fresh_preparation');preparation.mkdir()
        helper=deepcopy(runtime);helper.update(executable=file_record(Path(sys.executable)),compiler=file_record(Path(sys.executable)),
            app_ini=file_record(Path(request)),resolved_libraries=[],loaded_process_files=None,
            build_flags=dict(runtime['build_flags'],role='complete_closed_primary_and_physical_DATA_projection',
                python_source_root=q['python_root'],windows_backend_sha256=backend['sha256']))
        helper['runtime_identity']=runtime_content_identity(helper);helper['runtime_fingerprint']=digest_json(helper['runtime_identity'])
        write(c/'preparation-runtime.json',helper)
        with _environment({n:helper['loader_environment'].get(n)for n in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}):
            process=execute(helper,['-B','-m',MODULE,'--primary-worker',str(request)],SOURCE,c/'preparation-process',
                memory_bytes=16*GIB,maximum_processes=16,maximum_wall_seconds=q['preparation_wall_seconds'],
                lock_file=BASE/'locks/worker.lock',cooperative_capture=False)
        write(c/'preparation-process-result.json',process)
        require(process['execution']=='completed' and process['all_processes_closed'] and
                process['runtime_provenance']=='loaded_files_captured' and
                load(preparation/'terminal.json')['validity']=='valid','closed_training_primary_projection_failed')
        source_job=load(Path(q['source_job']['path']));stimulus=load(Path(q['stimulus_source']['path']))
        def edit(source,phase,threshold=None):
            guard();capacity(10*GIB);name=q['job_id']+'-'+phase
            plan=dict(kind='timelearner_prepared_physical_'+('conversion'if threshold is None else 'threshold')+'_plan',
                schema_version=1,source_data=file_record(source),runtime_manifest=file_record(c/'native-runtime.json'),
                sdk_source=binding['sdk_source'],python_source=str(SOURCE),controls=str(BASE/'controls'/name),
                inputs=str(BASE/'jobs'/(name+'-inputs')),output=str(BASE/'jobs'/name),job_id=name)
            if threshold is None:plan.update(conversion_spec=dict(schema_version=1,mode='identity',resistance_bounds=[]),reference_amplitudes=[])
            else:plan['threshold']=threshold
            path=c/(phase+'-plan.json');write(path,plan)
            (prepare_conversion if threshold is None else prepare_threshold)(path);physical_edit(Path(plan['controls']))
            output=Path(plan['output']);terminal=load(output/'terminal.json')
            require(terminal['native_process_completed'] and terminal['physical_roundtrip_verified'] and
                    _all_owned_closed(output,api,kernel),'closed_training_native_edit_failed')
            return output/'native/model.json'
        def evaluate(source,phase):
            guard();capacity(10*GIB);model=load(source);job=evaluation_job(q,source_job,model,stimulus,phase)
            condition=evaluation_condition(q,job,runtime);write(c/(phase+'-condition.json'),condition)
            wire={k:v for k,v in job.items()if k not in ('source_model_data','sha256')}
            plan=dict(kind='timelearner_prepared_physical_evaluation_plan',schema_version=2,job_id=job['run_id'],
                source_data=file_record(source),runtime_manifest=file_record(c/'native-runtime.json'),
                sdk_source=binding['sdk_source'],worker_origin=dict(root_commit=q['python_root'],
                    path='Scripts/StructTrain/TimeLearner/prepared_physical_evaluation.py',
                    sha256=file_record(Path(evaluation.__file__))['sha256']),job=wire,
                execution_limits=dict(memory_bytes=8*GIB,maximum_wall_seconds=q['native_evaluation_wall_seconds']))
            path=c/(phase+'-plan.json');write(path,plan);controls=evaluation.prepare(path);evaluation.run(controls)
            verified=_closed_evaluation(controls);spec,obs=load_physical_model_data_evaluation(verified['output']/'native/evaluation.json')
            write(c/(phase+'-timing.json'),summarize_trial_timing(spec,obs,verified['metrics']))
            return verified
        data=edit(preparation/'physical-model-DATA.json','conversion');baseline=evaluate(data,'baseline')
        proposal=propose_physical_same_matrix_threshold(baseline['output']/'native',baseline['job'],baseline['model'])
        write(c/'threshold-proposal.json',proposal);actual=None
        if proposal['status']=='candidate':
            candidate=edit(data,'threshold',proposal['threshold']);actual=evaluate(candidate,'confirmation')
        guard();_source_snapshot(SOURCE,q['python_root'])
        write(c/'terminal.json',dict(kind='timelearner_closed_Train_actual_same_matrix_recognition',schema_version=1,
            execution='completed',validity='valid',source_Train_outcome=binding['training_outcome'],
            source_completed_boundary=binding['completed_boundary'],source_model_revision=binding['model_revision'],
            preparation=file_record(preparation/'primary-pack-result.json'),baseline=baseline['metrics']['pooled_counts'],
            calibration_proposal_status=proposal['status'],threshold=proposal['threshold'],
            actual_counts=None if actual is None else actual['metrics']['pooled_counts'],
            actual_model_revision=None if actual is None else actual['model']['model_revision'],
            working_example_criterion_met=False if actual is None else
                actual['metrics']['pooled_counts']['TP']>=1 and actual['metrics']['pooled_counts']['TN']>=2,
            actual_confirmation_complete=actual is not None,protocol='historical_same_matrix',independent_evaluation=False,
            full_external_primary_publication_pending=True,new_Train=False,training_certificate_transferred=False,
            calibration_certificate_transferred=False,scientific_verdict=None))
    except BaseException as error:
        write(c/'exception.json',dict(reason=str(error),traceback=traceback.format_exc(),
            no_automatic_Train_or_native_retry=True,scientific_verdict=None));raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--supervise',type=Path);group.add_argument('--primary-worker',type=Path)
    args=parser.parse_args()
    if args.supervise:supervise(args.supervise)
    else:primary_worker(args.primary_worker)
