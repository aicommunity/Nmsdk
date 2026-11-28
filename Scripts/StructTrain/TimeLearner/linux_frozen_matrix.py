"""Execute the existing frozen cadence protocol against an audited DATA source.

The declaration is committed before calculation. Native execution, complete
observation audits and condition serialization stay in the production package.
"""
from pathlib import Path
import argparse
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
    c = Path(controls).resolve(strict=True)
    q = load(c/'request.json')
    assert sys.platform == 'linux' and q['kind'] == 'timelearner_linux_frozen_cadence_matrix'
    base, actor, out = Path(q['execution_root']), Path(q['actor']), Path(q['controller_output'])
    assert base == Path('/home/user/timelearner-refactor') and base.resolve(strict=True) == base
    assert c.parent == base/'requests' and out.parent == base/'readbacks' and not out.exists()
    out.mkdir()
    log = (out/'worker.log').open('x', buffering=1)
    sys.stdout = sys.stderr = log
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(actor))
    from Scripts.StructTrain.TimeLearner.runtime import file_record, source_closure
    from Scripts.StructTrain.TimeLearner.owned_python_job import _source_snapshot, _allocated_output_bytes
    from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
    from Scripts.StructTrain.TimeLearner.contained_process import inspect, stop
    from Scripts.StructTrain.TimeLearner.frozen_physical_source import frozen_physical_source
    from Scripts.StructTrain.TimeLearner.frozen_physical_iti_study import declare_job, condition, run_case
    from Scripts.StructTrain.TimeLearner.linux_frozen_physical_followups import CADENCE_PHASES
    from Scripts.StructTrain.TimeLearner.trial_response_comparison import trial_response_comparison

    registry = lease = None
    monitor_stop, monitor_errors = threading.Event(), []
    current_group = [None]
    monitor_thread = None
    try:
        write(out/'owner.json',dict(pid=os.getpid(), start_ticks=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19],
                                   boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()))
        before = _source_snapshot(actor,q['actor_commit'])
        write(out/'source-before.json',before)
        runtime_path = Path(q['runtime_manifest'])
        runtime = load(runtime_path)
        assert source_closure(Path(q['sdk_source'])) == runtime['source_closure']
        execution_phases = q.get('execution_phases', list(CADENCE_PHASES))
        assert type(execution_phases) is list and execution_phases
        assert len(set(execution_phases)) == len(execution_phases) and set(execution_phases) <= set(CADENCE_PHASES)
        registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
        capacity = registry.inspect()['capacity']
        assert capacity['memory_bytes'] >= 8*1024**3 and capacity['disk_bytes'] >= q['maximum_new_bytes'], 'matrix_declared_demand_exceeds_worker_capacity'
        assert shutil.disk_usage(base).free >= q['minimum_free_bytes']+q['maximum_new_bytes']
        write(out/'resource-admission.json',dict(capacity=capacity,minimum_free_bytes=q['minimum_free_bytes'],
            maximum_new_bytes=q['maximum_new_bytes'],declared_full_conditions=32,execution_phases=execution_phases))
        declaration = {k:q[k] for k in ['source_manifest','source_comparison','model_revision','threshold']}
        for key in ['source_manifest','source_comparison']:
            declaration[key+'_sha256'] = file_record(Path(q[key]))['sha256']
        write(c/'source-declaration.json',declaration)
        prepared = {}
        with frozen_physical_source(declaration) as source:
            for phase in CADENCE_PHASES:
                cadence, rotation, policy = phase.split('-')
                study = dict(rotation=int(rotation[1:]),cadence=cadence,
                             reset_policy='reset_per_trial' if policy=='reset' else 'preserve_neuron_dynamics')
                job, design = declare_job(source['job'],q['run_id']+'/'+phase,**study)
                binding = condition(job,design,runtime,threshold=q['threshold'])
                prepared[phase] = dict(study=study,condition_fingerprint=binding['condition_fingerprint'])
                write(c/(phase+'-design.json'),design)
                write(c/(phase+'-condition.json'),binding)
        assert len(prepared) == 32
        for args in [('add','.'),('commit','-qm','Freeze all32 cadence conditions before Calculate')]:
            subprocess.run(['git','-C',str(c),*args],check=True,capture_output=True)
        commit = subprocess.check_output(['git','-C',str(c),'rev-parse','HEAD']).decode().strip()
        write(out/'declaration.json',dict(controls_commit=commit,cases=len(execution_phases),declared_full_conditions=32,
            execution_phases=execution_phases,unexecuted_phases=[p for p in CADENCE_PHASES if p not in execution_phases],training_performed=False,
            threshold_selected=False,full_mode_matrix_accepted=False))
        registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
        assert shutil.disk_usage(base).free >= q['minimum_free_bytes']+q['maximum_new_bytes']
        lease = registry.reserve(q['run_id'],[dict(path=str(p),access=a)for p,a in
            [(actor,'read'),(Path(q['source_manifest']).parent,'read'),(Path(q['source_comparison']).parent,'read'),
             (Path(q['sdk_source']),'read'),(Path(runtime['executable']['path']).parent,'read'),(c,'read'),(out,'write')]],
            ttl_seconds=14400,
            demands=dict(slots=1,memory_bytes=8*1024**3,disk_bytes=q['maximum_new_bytes']))
        write(out/'reservation.json',lease)
        def monitor():
            while not monitor_stop.wait(10):
                try:
                    registry.heartbeat(lease['token'],ttl_seconds=14400)
                    assert shutil.disk_usage(base).free >= q['minimum_free_bytes'],'matrix_disk_floor'
                    assert _allocated_output_bytes(out) <= q['maximum_new_bytes'],'matrix_output_ceiling'
                    assert not(out/'cancel.request').exists(),'matrix_cancel_requested'
                except BaseException as error:
                    monitor_errors.append(str(error))
                    group = current_group[0]
                    if group is not None and (group/'request.json').exists() and not inspect(group)['all_processes_closed']:
                        stop(group)
                    return
        monitor_thread = threading.Thread(target=monitor,daemon=True)
        monitor_thread.start()
        rows, paired = [], {}
        started = time.monotonic()
        for phase in execution_phases:
            values = prepared[phase]
            assert not monitor_errors and time.monotonic()-started < q['maximum_matrix_wall_seconds']
            assert not(out/'cancel.request').exists()
            case = out/phase
            current_group[0] = case/'run/process/contained'
            write(out/(phase+'-started.json'),dict(phase=phase,started_wall_time=time.time()))
            try:
                result = run_case(declaration,runtime_path,case,run_id=q['run_id']+'/'+phase,
                    **values['study'],maximum_wall_seconds=7200,process_policy=dict(
                        kind='timelearner_native_process_policy',schema_version=1,backend='bound_cgroup',
                        memory_bytes=2*1024**3,tasks=128,cooperative_capture=True))
                assert result['condition_fingerprint'] == values['condition_fingerprint']
                key = phase.rsplit('-',1)[0]
                first = case/'run/native/trial-0.json'
                if phase.endswith('-reset'):
                    paired[key] = first
                elif key in paired:
                    with frozen_physical_source(declaration) as source:
                        with trial_response_comparison(source['model'],physical_data=True) as compare:
                            comparison = compare(load(paired[key]),load(first))
                    write(case/'first-trial-control.json',comparison)
                    assert comparison['response_preserved'],'paired_initial_reset_response_changed'
                row = dict(phase=phase,execution='completed',validity='valid',result=file_record(case/'terminal.json'),
                           counts=result['counts'],condition_fingerprint=result['condition_fingerprint'])
            except BaseException as error:
                row = dict(phase=phase,execution='failed',validity='unaccepted',error=str(error),traceback=traceback.format_exc())
                write(out/(phase+'-failure.json'),row)
                group = current_group[0]
                if monitor_errors or ((group/'request.json').exists() and not inspect(group)['all_processes_closed']):
                    raise
            rows.append(row)
            write(out/(phase+'-result.json'),row)
        assert not monitor_errors and _source_snapshot(actor,q['actor_commit']) == before
        write(out/'source-after.json',before)
        complete = [r for r in rows if r['validity']=='valid']
        write(out/'terminal.json',dict(execution='completed',validity='valid' if len(complete)==len(execution_phases) else 'partial',
            rows=rows,completed_cadence_cases=len(complete),accepted_observations=8*len(complete),
            declared_full_conditions=32,execution_phases=execution_phases,
            unexecuted_phases=[p for p in CADENCE_PHASES if p not in execution_phases],
            model_revision=q['model_revision'],threshold=q['threshold'],new_Train=False,threshold_selected=False,
            full_primary_archival_pending=True,temporal_figures_pending=True,full_mode_matrix_accepted=False,scientific_verdict=None))
    except BaseException as error:
        write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc(),monitor_errors=monitor_errors,scientific_verdict=None))
        raise
    finally:
        monitor_stop.set()
        if monitor_thread is not None:
            monitor_thread.join(timeout=15)
        group = current_group[0]
        if lease is not None and (group is None or not(group/'request.json').exists() or inspect(group)['all_processes_closed']):
            registry.release(lease['token'],note='All owned matrix phases closed; original training and calibration unchanged')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--controls',required=True)
    run(parser.parse_args().controls)


if __name__ == '__main__':
    main()
