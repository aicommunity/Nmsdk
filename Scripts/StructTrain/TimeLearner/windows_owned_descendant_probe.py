"""Observe members of an owned --help Job without changing backend verdicts.

Only queries of the producer's named Job and member creation/image identities
are added. This diagnoses auxiliary launch failures, never calculates a model.
"""
from pathlib import Path
import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import traceback


def load(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def run(controls):
    seed = Path(controls).resolve(strict=True)
    q = load(seed/'request.json')
    assert os.name == 'nt' and q['kind'] == 'timelearner_owned_windows_descendant_diagnostic'
    out = Path(q['output'])
    assert out.parent == Path(q['worker_root'])/'jobs' and not out.exists()
    out.mkdir()
    log = (out/'worker.log').open('x', encoding='utf-8', buffering=1)
    sys.stdout = sys.stderr = log
    sys.dont_write_bytecode = True
    sdk = Path(q['sdk'])
    sys.path.insert(0, str(sdk))
    from Scripts.StructTrain.TimeLearner.windows_process import execute, _Windows
    from Scripts.StructTrain.TimeLearner.native_gate import _environment
    from Scripts.StructTrain.TimeLearner.runtime import source_closure, file_record
    kernel = ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.GetProcessTimes.argtypes=[ctypes.c_void_p]+[ctypes.POINTER(ctypes.c_ulonglong)]*4
    times=[ctypes.c_ulonglong()for _ in range(4)]
    assert kernel.GetProcessTimes(kernel.GetCurrentProcess(),*[ctypes.byref(v)for v in times])
    write(out/'owner.json',dict(pid=os.getpid(),creation_filetime=str(times[0].value),executable=sys.executable))
    try:
        runtime_path = Path(q['runtime_manifest'])
        runtime_record = file_record(runtime_path)
        runtime = load(runtime_path)
        before = source_closure(sdk)
        assert before == runtime['source_closure']
        assert shutil.disk_usage(out).free >= 2*1024**3
        c = out/'frozen-controls'
        c.mkdir()
        for name in ['.gitattributes','worker.py','request.json','dispatch-command.txt']:
            shutil.copyfile(seed/name,c/name)
        for args in [('init','-b','codex/'+c.parent.name),('config','user.name','TimeLearner worker'),
                     ('config','user.email','timelearner@localhost'),('config','gc.auto','0'),
                     ('config','maintenance.auto','false'),('add','.'),
                     ('commit','-qm','Freeze query-only observation of owned help-process descendants')]:
            result=subprocess.run(['git','-C',str(c),*args],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            assert result.returncode==0,result.stderr.decode(errors='replace')
        write(out/'source-before.json',before)
        results=[]
        for index in range(q['attempts']):
            assert not(out/'cancel.request').exists()
            directory=out/('attempt-'+str(index))
            stop=threading.Event()
            mappings=[]
            errors=[]
            def observe():
                api=_Windows()
                open_job=kernel.OpenJobObjectW
                open_job.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_wchar_p]
                open_job.restype=ctypes.c_void_p
                open_process=kernel.OpenProcess
                open_process.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
                open_process.restype=ctypes.c_void_p
                handle=None
                seen=set()
                try:
                    while not stop.wait(.005):
                        owner_path=directory/'owned-process.json'
                        if not owner_path.exists():continue
                        owner=load(owner_path)
                        if handle is None:
                            handle=open_job(4,False,owner['job_name'])
                            if not handle:
                                errors.append(dict(operation='OpenJobObjectW',error=ctypes.get_last_error()))
                                continue
                        for pid in api.pids(handle):
                            process=open_process(0x1000|0x100000,False,pid)
                            if not process:
                                errors.append(dict(operation='OpenProcess',pid=pid,error=ctypes.get_last_error()))
                                continue
                            try:
                                belongs=api.W.BOOL()
                                api.check(api.in_job(process,handle,ctypes.byref(belongs)))
                                if not belongs.value:
                                    errors.append(dict(pid=pid,reason='no_longer_in_owned_job'))
                                    continue
                                identity=api.identity(process)
                                key=(pid,identity['creation_filetime'])
                                if key in seen:continue
                                seen.add(key)
                                mappings.append(dict(pid=pid,**identity,owned_job=owner['job_name'],
                                    main_pid=owner['pid'],main_creation_filetime=owner['creation_filetime'],
                                    main_member=pid==owner['pid'],member_running=api.running(process),
                                    recorded_monotonic=time.monotonic()))
                            finally:
                                api.close(process)
                except BaseException as error:
                    errors.append(dict(operation='observe_owned_job',error=str(error)))
                finally:
                    if handle:api.close(handle)
            observer=threading.Thread(target=observe,daemon=True)
            observer.start()
            try:
                values={key:runtime['loader_environment'].get(key)for key in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}
                values.update(GTEST_FILTER='-*',GTEST_LIST_TESTS='1',GTEST_REPEAT='1',GTEST_SHUFFLE='0')
                with _environment(values):
                    result=execute(runtime,['--help'],Path(runtime['executable']['path']).parent,
                        directory,memory_bytes=1024**3,maximum_processes=16,maximum_wall_seconds=30,
                        lock_file=out/'probe.lock',cooperative_capture=False)
            finally:
                stop.set()
                observer.join(timeout=10)
                write(out/('attempt-'+str(index)+'-member-observations.json'),dict(members=mappings,errors=errors,
                    observer_changes='query-only extra Job handle and member inspection may change timing',
                    original_unobserved_launch_reclassified=False))
            assert not observer.is_alive() and result['all_processes_closed']
            remaining=result.get('descendants_at_main_exit',[])
            write(out/('attempt-'+str(index)+'-result.json'),result)
            results.append(dict(attempt=index,result=result,remaining_member_observations=[v for v in mappings if v['pid']in remaining],
                                observer_errors=errors,model_executed=False))
        assert file_record(runtime_path)==runtime_record and source_closure(sdk)==before
        write(out/'source-after.json',before)
        write(out/'terminal.json',dict(execution='completed',validity='diagnostic_only',rows=results,
            backend_verdicts_preserved=True,original_failed_attempt_not_reclassified=True,
            model_executed=False,new_Train=False,scientific_verdict=None))
    except BaseException as error:
        write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc(),scientific_verdict=None))
        raise


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--controls',required=True)
    run(parser.parse_args().controls)


if __name__=='__main__':
    main()
