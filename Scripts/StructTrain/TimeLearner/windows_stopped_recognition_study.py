"""Continue an audited stopped Windows count Train with actual eight trials.

The source Train and its full-primary task must both close. Preparation and
audit use the existing bounded Windows backend; the small native controller
uses prepared_diagnostic, which owns the same host lock and bounded native
job itself. No current source/runtime is updated and no Train is restarted.
"""
import argparse
import ctypes as C
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

from .native_evidence import EvidenceError, load, require
from .runtime import file_record

SOURCE = Path(__file__).resolve().parents[3]
BASE = Path('C:/Projects/TimeLearnerWorker')
MODULE = 'Scripts.StructTrain.TimeLearner.windows_stopped_recognition_study'
GIB = 1024**3


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False);stream.write('\n')


def state(path, value):
    temporary=path.with_suffix('.pending');require(not temporary.exists(),'recognition_pending_state_collision')
    write(temporary,value);os.replace(temporary,path)


def context(request):
    request=Path(request).resolve(strict=True);spec=load(request)
    fields={'kind','schema_version','job_id','python_root','source_training_spec',
            'source_audit_spec','source_native_owner','source_audit_owner','template_envelope',
            'maximum_wait_seconds','maximum_phase_wall_seconds'}
    require(os.name=='nt' and type(spec) is dict and set(spec)==fields and
        spec['kind']=='timelearner_windows_stopped_recognition_study' and
        type(spec['schema_version']) is int and spec['schema_version']==1,
        'windows_recognition_request_schema')
    name=spec['job_id'];require(type(name) is str and 1<=len(name)<=90 and
        all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name), 'windows_recognition_job_id')
    require(BASE.resolve(strict=True)==BASE and SOURCE.is_relative_to(BASE) and
        request==BASE/'controls'/name/'request.json', 'windows_recognition_owned_paths')
    # Pin the isolated tool tree separately from the original native SDK.
    def git(*args):
        return subprocess.check_output(['git','-c','maintenance.auto=false','-c','gc.auto=0',
            '-C',str(SOURCE),*args],stderr=subprocess.PIPE,timeout=60,
            creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    require(type(spec['python_root']) is str and len(spec['python_root'])==40 and
        git('rev-parse','HEAD')==spec['python_root'] and not git('status','--porcelain',
            '--untracked-files=all','--ignore-submodules=all'), 'windows_recognition_actor_changed')
    require(type(spec['maximum_wait_seconds']) is int and 0<spec['maximum_wait_seconds']<=86400 and
        type(spec['maximum_phase_wall_seconds']) is int and
        9000<=spec['maximum_phase_wall_seconds']<=12000, 'windows_recognition_finite_limits')
    for key in ('source_training_spec','source_audit_spec','source_native_owner','source_audit_owner','template_envelope'):
        record=spec[key];p=Path(record['path'])
        require(p.is_relative_to(BASE) and p.resolve(strict=True)==p and not p.is_symlink() and
            not p.is_junction() and file_record(p)==record,'windows_recognition_bound_input_changed:'+key)
    training=load(Path(spec['source_training_spec']['path']))
    require(training['kind']=='timelearner_count_two_sweep_training','windows_recognition_two_sweep_source_required')
    source=Path(training['output']);native=source/'train/native';sdk=Path(training['sdk_source'])
    audit_spec=load(Path(spec['source_audit_spec']['path']));audit_controls=Path(spec['source_audit_spec']['path']).parent
    require(source.is_relative_to(BASE/'jobs') and sdk.is_relative_to(BASE) and
        audit_spec['source_job']==str(source) and audit_spec['module']==
        'Scripts.StructTrain.TimeLearner.tests.test_closed_doubled_count_training' and
        Path(spec['source_native_owner']['path'])==source/'train/process/owned-process.json' and
        Path(spec['source_audit_owner']['path'])==audit_controls/'queue-owner.json',
        'windows_recognition_exact_source_and_audit_roles')
    runtime=Path(spec['source_training_spec']['path']).parent/'runtime.json'
    return dict(spec=spec,request=request,request_record=file_record(request),controls=request.parent,
        output=BASE/'jobs'/name,source=source,native=native,sdk=sdk,runtime=runtime,
        runtime_record=file_record(runtime),audit_controls=audit_controls,
        audit_output=Path(audit_spec['output']),training_task='TimeLearner-'+source.name,
        audit_task='TimeLearner-'+audit_spec['name'])


def guard(plan):
    require(file_record(plan['request'])==plan['request_record'] and
        file_record(plan['runtime'])==plan['runtime_record'],'windows_recognition_request_or_runtime_changed')
    for key in ('source_training_spec','source_audit_spec','source_native_owner','source_audit_owner','template_envelope'):
        require(file_record(Path(plan['spec'][key]['path']))==plan['spec'][key],
            'windows_recognition_input_changed:'+key)


def phase_paths(plan,phase):
    role='threshold' if phase.startswith('threshold') else 'baseline'
    name=plan['spec']['job_id']+'-'+role
    return plan['controls']/role,BASE/'jobs'/name,BASE/'jobs'/(name+'-inputs')


def worker(request,phase):
    plan=context(request);guard(plan);control,output,inputs=phase_paths(plan,phase)
    if phase=='baseline-prepare':
        from .prepare_stopped_baseline import prepare
        control.mkdir();proof=plan['audit_output']/'tmp/two-sweep-count-training-audit.json'
        audit=control/'source-audit.json';write(audit,load(proof)['full_primary_audit']['training_audit'])
        declaration=dict(kind='timelearner_stopped_baseline_preparation',schema_version=1,
            source_native=str(plan['native']),source_proof=str(proof),source_audit=str(audit),
            template_envelope=plan['spec']['template_envelope']['path'],native_runtime=str(plan['runtime']),
            sdk_source=str(plan['sdk']),destination=str(control),inputs=str(inputs),output=str(output),
            run_id=plan['spec']['job_id']+'/baseline',python_source=str(SOURCE))
        write(control/'declaration.json',declaration);prepare(declaration)
    elif phase=='threshold-prepare':
        from .prepared_threshold import prepare
        control.mkdir()
        try:prepare(plan['controls']/'baseline',control,inputs,output,plan['spec']['job_id']+'/threshold')
        except EvidenceError as error:
            if str(error)!='threshold_no_target_preserving_gap':raise
            write(control/'nonseparable.json',dict(calibration='nonseparable',reason=str(error),
                protocol='historical_same_matrix',selected_threshold=None,scientific_verdict=None))
    elif phase in ('baseline-audit','threshold-audit'):
        from .audit_prepared_diagnostic import audit
        write(control/'independent-audit.json',audit(control))
    else:raise ValueError('unknown_windows_recognition_phase')
    guard(plan);write(plan['output']/phase/'worker-terminal.json',dict(completed=True,phase=phase,
        original_training_outcome_unchanged=True,training_convergence_inferred=False,scientific_verdict=None))


def task(name):
    require(all(c.isalnum() or c in '-_' for c in name),'windows_recognition_task_name')
    script="$s=New-Object -ComObject Schedule.Service;$s.Connect();$t=$s.GetFolder([string][char]92).GetTask('"+name+"');@{state=$t.State;last_result=$t.LastTaskResult;instances=$t.GetInstances(0).Count}|ConvertTo-Json -Compress"
    r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],
        capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=20,check=True)
    return json.loads(r.stdout.decode('utf-8-sig'))


def _kernel():
    from .windows_process import _Windows
    api=_Windows();k=C.WinDLL('kernel32',use_last_error=True)
    k.GetCurrentProcess.restype=C.c_void_p;k.OpenProcess.argtypes=[C.c_ulong,C.c_int,C.c_ulong]
    k.OpenProcess.restype=C.c_void_p;k.CloseHandle.argtypes=[C.c_void_p]
    return api,k


def live(api,k,identity):
    h=k.OpenProcess(0x101000,False,identity['pid'])
    if not h:
        require(C.get_last_error() in (87,1168),'windows_recognition_process_observation_failed')
        return False
    try:
        # A terminated process can retain an open kernel handle while its
        # executable mapping is already unavailable (QueryFullProcessImageName
        # then reports WinError31). Check this handle's lifetime first, and
        # distinguish an exit during the identity query from a live-process
        # access failure. Never classify an unobservable live process as dead.
        if not api.running(h):return False
        try:
            actual=api.identity(h)
        except OSError:
            if not api.running(h):return False
            raise
        # A reused PID is a different process; never signal it or wait on it.
        return (actual['creation_filetime']==identity['creation_filetime'] and
                os.path.samefile(actual['executable'],identity['executable']) and api.running(h))
    finally:k.CloseHandle(h)


def controller_runtime(plan,phase):
    from .runtime import runtime_content_identity,digest_json
    runtime=load(plan['runtime']);backend=file_record(SOURCE/'Scripts/StructTrain/TimeLearner/windows_process.py')
    runtime.update(executable=file_record(Path(sys.executable)),app_ini=plan['request_record'],
        compiler=file_record(Path(sys.executable)),resolved_libraries=[],loaded_process_files=None,
        windows_backend=backend,build_flags=dict(runtime['build_flags'],role=phase,
            windows_backend_sha256=backend['sha256'],python_source_root=plan['spec']['python_root']))
    runtime['runtime_identity']=runtime_content_identity(runtime)
    runtime['runtime_fingerprint']=digest_json(runtime['runtime_identity'])
    return runtime


def native_controller(plan,phase,directory):
    """The checked small executor itself owns the global lock/native job.

    Wrapping it in a second lock-holding windows_process job would deadlock
    the nested executor. Record this controller's actual lifetime separately;
    its native child still gets the maintained backend's 16 GiB/7200s limits.
    """
    control,output,_=phase_paths(plan,phase);api,k=_kernel();start=time.monotonic()
    environment=dict(os.environ)
    for key in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM'):
        value=load(control/'runtime.json')['loader_environment'].get(key)
        if value is None:environment.pop(key,None)
        else:environment[key]=value
    def disk_guard():
        total=0
        if output.exists():
            for parent,_,names in os.walk(output):
                for name in names:
                    try:total+=(Path(parent)/name).stat().st_size
                    except FileNotFoundError:pass
        require(total<=16*GIB,'windows_recognition_native_output_budget')
        require(shutil.disk_usage(BASE).free>=8*GIB,'windows_recognition_disk_floor')
    with (directory/'stdout.log').open('xb') as stdout,(directory/'stderr.log').open('xb') as stderr:
        p=subprocess.Popen([sys.executable,'-B',str(control/'worker.py'),'--controls',str(control)],
            cwd=SOURCE,stdout=stdout,stderr=stderr,env=environment,creationflags=subprocess.CREATE_NO_WINDOW)
        h=k.OpenProcess(0x101000,False,p.pid);require(bool(h),'windows_recognition_controller_not_observable')
        try:identity=dict(pid=p.pid,**api.identity(h))
        finally:k.CloseHandle(h)
        write(directory/'controller-owner.json',identity)
        try:
            while p.poll() is None:
                guard(plan)
                require(not (plan['controls']/'cancel.request').exists(),'windows_recognition_cancelled')
                require(time.monotonic()-start<plan['spec']['maximum_phase_wall_seconds'],
                    'windows_recognition_native_controller_timeout')
                disk_guard()
                time.sleep(2)
        except BaseException:
            # Killing only this exact Popen owner closes its non-inherited
            # native Job handle (KILL_ON_JOB_CLOSE). Verify that child closure
            # before leaving; never start another phase after this failure.
            if p.poll() is None:p.terminate()
            p.wait(timeout=30)
            native_owner=output/'process/owned-process.json'
            if native_owner.exists():
                child=load(native_owner);deadline=time.monotonic()+30
                while live(api,k,child) and time.monotonic()<deadline:time.sleep(.2)
                require(not live(api,k,child),'windows_recognition_native_closure_unknown')
            raise
    disk_guard();result=load(output/'process-result.json')
    require(p.returncode==0 and result['execution']=='completed' and result['all_processes_closed'] and
        result['runtime_provenance']=='loaded_files_captured' and
        load(output/'terminal.json')['native_process_completed'], 'windows_recognition_native_incomplete')
    write(directory/'worker-terminal.json',dict(completed=True,phase=phase,controller_return_code=p.returncode,
        controller=identity,controller_memory_hard_limit=False,native_memory_hard_limit_bytes=16*GIB,
        native_maximum_wall_seconds=7200,all_native_processes_closed=True,scientific_verdict=None))


def supervise(request):
    from .native_gate import _environment
    from .windows_process import execute
    plan=context(request);spec=plan['spec'];root=plan['output'];require(not root.exists(),'windows_recognition_output_exists');root.mkdir()
    api,k=_kernel();write(plan['controls']/'queue-owner.json',dict(pid=os.getpid(),**api.identity(k.GetCurrentProcess())))
    identities=[load(Path(spec[key]['path']))for key in ('source_native_owner','source_audit_owner')]
    try:
        start=time.monotonic()
        while True:
            guard(plan);require(time.monotonic()-start<spec['maximum_wait_seconds'],'windows_recognition_wait_timeout')
            require(not (plan['controls']/'cancel.request').exists(),'windows_recognition_wait_cancelled')
            running=[live(api,k,v)for v in identities]
            snapshots={}
            if not any(running):
                snapshots={role:task(plan[role+'_task'])for role in ('training','audit')}
                if all(v['state']==3 and v['instances']==0 for v in snapshots.values()):
                    require(all(v['last_result']==0 for v in snapshots.values()),'windows_recognition_original_task_failed')
                    audit=load(plan['audit_controls']/'terminal.json');process=load(plan['audit_controls']/'process-result.json')
                    validation=audit['validation']
                    require(audit['full_primary_audit_complete'] and process['execution']=='completed' and
                        process['all_processes_closed'] and process['runtime_provenance']=='loaded_files_captured' and
                        validation['assertion_status']=='passed' and validation['executed_tests']==1 and
                        not any(validation[x]for x in ('failures','errors','skipped')),
                        'windows_recognition_complete_primary_audit_required')
                    proof_path=plan['audit_output']/'tmp/two-sweep-count-training-audit.json';proof=load(proof_path)
                    require(proof['kind']=='timelearner_closed_doubled_count_training_audit',
                        'windows_recognition_exact_doubled_proof_required')
                    full=proof['full_primary_audit']
                    if full['completed_boundary'] is not False or full['training_outcome']!='budget_exhausted':
                        write(root/'terminal.json',dict(execution='not_dispatched',reason='different_completed_or_stopped_protocol_required',
                            actual_training_outcome=full['training_outcome'],completed_boundary=full['completed_boundary'],
                            original_Train_not_restarted=True,scientific_verdict=None));return
                    write(root/'original-primary-audit.json',dict(proof=file_record(proof_path),task_closure=snapshots,
                        validation=validation,source_groups_closed=True,original_outcome_unchanged=True));break
            state(plan['controls']/'queue-state.json',dict(reason='waiting_for_exact_two_sweep_Train_and_full_primary_task',
                observed_utc=datetime.now(timezone.utc).isoformat(),source_native_running=running[0],
                source_primary_running=running[1],elapsed_wait_seconds=time.monotonic()-start,
                no_Train_restarted=True,new_native_execution_started=False))
            time.sleep(15)
        for phase in ('baseline-prepare','baseline-native','baseline-audit','threshold-prepare','threshold-native','threshold-audit'):
            guard(plan);require(shutil.disk_usage(BASE).free>=24*GIB,'windows_recognition_phase_disk_admission')
            directory=root/phase;directory.mkdir();state(plan['controls']/'queue-state.json',dict(reason='running_'+phase,
                source_groups_closed=True,observed_utc=datetime.now(timezone.utc).isoformat()))
            if phase.endswith('native'):native_controller(plan,phase,directory)
            else:
                runtime=controller_runtime(plan,phase);write(directory/'runtime.json',runtime)
                with _environment({key:runtime['loader_environment'].get(key)for key in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}):
                    result=execute(runtime,['-B','-m',MODULE,'_phase',str(plan['request']),phase],SOURCE,
                        directory/'process',memory_bytes=16*GIB,maximum_processes=16,
                        maximum_wall_seconds=spec['maximum_phase_wall_seconds'],lock_file=BASE/'locks/worker.lock')
                write(directory/'process-result.json',result)
                require(result['execution']=='completed' and result['all_processes_closed'] and
                    load(directory/'worker-terminal.json')['completed'],'windows_recognition_phase_failed:'+phase)
            if phase=='threshold-prepare' and (plan['controls']/'threshold/nonseparable.json').exists():
                baseline=load(plan['controls']/'baseline/independent-audit.json')
                write(root/'terminal.json',dict(execution='completed',validity='valid',calibration='nonseparable',
                    baseline_counts=baseline['native_evidence']['metrics']['pooled_counts'],
                    actual_selected_threshold_replay_performed=False,training_completed=False,
                    independently_heldout_evaluation=False,scientific_verdict=None));return
        baseline=load(plan['controls']/'baseline/independent-audit.json');threshold=load(plan['controls']/'threshold/independent-audit.json')
        write(root/'terminal.json',dict(execution='completed',validity='valid',calibration='same_matrix_actual_replay',
            baseline_counts=baseline['native_evidence']['metrics']['pooled_counts'],
            actual_threshold_counts=threshold['native_evidence']['metrics']['pooled_counts'],
            threshold=load(plan['controls']/'threshold/proposal.json')['threshold'],
            original_Train_outcome='budget_exhausted',training_completed=False,
            source_proof_kind='timelearner_closed_doubled_count_training_audit',
            complete_source_history_audited=True,independently_heldout_evaluation=False,scientific_verdict=None))
    except BaseException as error:
        write(root/'exception.json',dict(reason=str(error),traceback=traceback.format_exc(),
            original_Train_not_restarted=True,scientific_verdict=None));raise


def main():
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=('supervise','_phase'));parser.add_argument('request');parser.add_argument('phase',nargs='?')
    args=parser.parse_args()
    if args.operation=='supervise':supervise(args.request)
    else:worker(args.request,args.phase)


if __name__=='__main__':main()
