"""Run the declared 32 cadence/reset cases on an admitted frozen Windows SDK.

This is one part of the full mode matrix. It neither trains nor calibrates.
The seed is copied by the actual scheduled user into its own immutable Git
controls. Every case is prepared and audited by the production DATA runner.
"""
from pathlib import Path
import argparse
import ctypes
import gzip
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import traceback


def load(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def run(seed):
    seed = Path(seed).resolve(strict=True)
    q = load(seed/'request.json')
    assert os.name == 'nt' and q['kind'] == 'timelearner_windows_frozen_cadence_matrix'
    base, sdk = Path(q['worker_root']), Path(q['sdk'])
    out = Path(q['output'])
    assert base.resolve(strict=True) == base and sdk.is_relative_to(base)
    assert out.parent == base/'jobs' and not out.exists()
    out.mkdir()
    log = (out/'worker.log').open('x', encoding='utf-8', buffering=1)
    sys.stdout = sys.stderr = log
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(sdk))
    from Scripts.StructTrain.TimeLearner.runtime import file_record, source_closure
    from Scripts.StructTrain.TimeLearner.external_archive import resolve
    from Scripts.StructTrain.TimeLearner.prepared_physical_evaluation import prepare, run as evaluate
    from Scripts.StructTrain.TimeLearner.linux_frozen_physical_followups import CADENCE_PHASES, declared_job
    from Scripts.StructTrain.TimeLearner.frozen_physical_iti_study import condition
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.native_gate import _environment
    from Scripts.StructTrain.TimeLearner.trial_response_comparison import trial_response_comparison

    def git(directory, *args):
        result = subprocess.run(['git', '-C', str(directory), *args], capture_output=True,
                                timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        with (out/'git-commands.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(arguments=args, returncode=result.returncode,
                stderr=result.stderr.decode(errors='replace')))+'\n')
        assert result.returncode == 0, result.stderr.decode(errors='replace')
        return result.stdout.decode().strip()

    def freeze(directory, message):
        (directory/'.gitattributes').write_bytes(b'* -text\n')
        for args in [('init', '-b', 'codex/'+directory.name),
                     ('config', 'user.name', 'TimeLearner worker'),
                     ('config', 'user.email', 'timelearner@localhost'),
                     ('config', 'gc.auto', '0'), ('config', 'maintenance.auto', 'false'),
                     ('add', '.'), ('commit', '-qm', message)]:
            git(directory, *args)
        return git(directory, 'rev-parse', 'HEAD')

    try:
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.GetProcessTimes.argtypes = [ctypes.c_void_p]+[ctypes.POINTER(ctypes.c_ulonglong)]*4
        times = [ctypes.c_ulonglong() for _ in range(4)]
        assert kernel.GetProcessTimes(kernel.GetCurrentProcess(), *[ctypes.byref(v) for v in times])
        write(out/'owner.json', dict(pid=os.getpid(), creation_filetime=str(times[0].value),
                                    executable=sys.executable))
        assert shutil.disk_usage(base).free >= q['minimum_free_bytes']+q['maximum_new_bytes']
        prior = Path(q['prior_controller'])
        prior_terminal = load(prior/'terminal.json')
        assert prior_terminal['validity'] == 'valid' and prior_terminal['all_eight_waveforms_and_events_preserved']
        before = source_closure(sdk)
        assert before == load(prior/'source-after.json')
        write(out/'source-before.json', before)
        runtime_dir, gate = Path(q['runtime']), Path(q['closed_gate'])
        spec = importlib.util.spec_from_file_location('cadence_sdk_inventory',
            sdk/'Scripts/StructTrain/TimeLearner/workers/windows-vs2026/sdk-build.py')
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        with gzip.open(gate/'audit/runtime-files.json.gz', 'rb') as stream:
            inventory = json.load(stream)
        assert helper.inventory(runtime_dir) == inventory
        nas = Path(q['archive_root'])
        reference = load(resolve(q['reference_catalog'], nas))
        assert reference['model_revision'] == q['model_revision'] and reference['threshold'] == q['threshold']
        model_path = out/'source-model.json'
        shutil.copyfile(resolve(reference['model_data'], nas), model_path)
        assert file_record(model_path)['sha256'] == reference['model_data']['sha256']
        model = load(model_path)
        original = dict(reference['job_template'], source_model_data=model)
        original['sha256'] = sha(original)
        c = out/'frozen-controls'
        c.mkdir()
        for name in ['.gitattributes', 'worker.py', 'request.json', 'dispatch-command.txt']:
            shutil.copyfile(seed/name, c/name)
        shutil.copyfile(prior/'frozen-controls/runtime.json', c/'runtime.json')
        runtime = load(c/'runtime.json')
        assert runtime['source_closure'] == before
        phases = list(CADENCE_PHASES)
        assert len(phases) == len(set(phases)) == 32
        declarations = []
        if q['crossplatform_baseline_first']:
            baseline = dict(reference['job_template'])
            baseline['run_id'] = q['job_id']+'/baseline'
            baseline['trials'] = [dict(t, run_id=baseline['run_id'],
                trial_id=baseline['run_id']+'/trial-'+str(i)) for i, t in enumerate(baseline['trials'])]
            declarations.append(('baseline', baseline, dict(protocol_id='original_eight_crossplatform_control')))
        for phase in phases:
            job, design = declared_job(original, q['job_id']+'/'+phase, phase)
            binding = condition(job, design, runtime, threshold=q['threshold'])
            write(c/(phase+'-condition.json'), binding)
            declarations.append((phase, {k:v for k,v in job.items()
                if k not in ('source_model_data', 'sha256')}, design))
        for phase, job, design in declarations:
            plan = dict(kind='timelearner_prepared_physical_evaluation_plan', schema_version=3,
                worker_root=str(base), job_id=q['job_id']+'-'+phase, source_data=file_record(model_path),
                runtime_manifest=file_record(c/'runtime.json'), sdk_source=str(sdk),
                worker_origin=q['worker_origin'], job=job,
                execution_limits=dict(memory_bytes=8*1024**3, maximum_wall_seconds=14400))
            write(c/(phase+'-plan.json'), plan)
            write(c/(phase+'-design.json'), design)
        frozen_commit = freeze(c, 'Preregister all 32 frozen cadence reset cases before any native calculation')
        write(out/'declaration.json', dict(controls_commit=frozen_commit, cases=len(declarations),
            mode_matrix_subset='one fixed model; 8 rotations x 2 cadences x 2 reset policies',
            new_Train=False, threshold_selected=False, original_training_outcome_unchanged=True,
            full_mode_matrix_accepted=False))
        rows, paired = [], {}
        for phase, _, design in declarations:
            assert not (out/'cancel.request').exists(), 'matrix_cancel_requested'
            assert shutil.disk_usage(base).free >= q['minimum_free_bytes']+512*1024**2
            assert file_record(model_path)['sha256'] == reference['model_data']['sha256']
            write(out/(phase+'-started.json'), dict(phase=phase, started_wall_time=time.time()))
            invocation_started = False
            try:
                with _environment({k:runtime['loader_environment'].get(k)
                                   for k in ('PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM')}):
                    prepared = prepare(c/(phase+'-plan.json'))
                    commit = freeze(prepared, 'Freeze actual native controls for one declared cadence case')
                    invocation_started = True
                    evaluate(prepared, cancel_file=out/'cancel.request')
                result = Path(load(prepared/'specification.json')['output'])
                terminal = load(result/'terminal.json')
                assert terminal['validity'] == 'valid' and terminal['complete_observations'] == 8
                assert terminal['frozen_model_verified'] and terminal['native_execution_verified']
                assert terminal['model_revision'] == q['model_revision'] and terminal['threshold'] == q['threshold']
                control_comparison = None
                if phase == 'baseline':
                    observations = {load(resolve(v,nas))['sample_id']:load(resolve(v,nas))
                                    for v in reference['observations'].values()}
                    with trial_response_comparison(model, physical_data=True) as compare:
                        comparison_rows = [compare(observations[o['sample_id']],o)
                            for o in [load(result/'native'/f'trial-{i}.json')for i in range(8)]]
                    control_comparison = dict(rows=comparison_rows,
                        all_eight_waveforms_and_events_preserved=all(r['response_preserved']for r in comparison_rows))
                    write(out/'crossplatform-baseline-comparison.json',control_comparison)
                    assert control_comparison['all_eight_waveforms_and_events_preserved'], 'baseline_transport_changed'
                else:
                    key = phase.rsplit('-',1)[0]
                    first = result/'native/trial-0.json'
                    if phase.endswith('-reset'):
                        paired[key] = first
                    else:
                        with trial_response_comparison(model, physical_data=True) as compare:
                            control_comparison = compare(load(paired[key]),load(first))
                        assert control_comparison['response_preserved'], 'paired_initial_reset_response_changed'
                row = dict(phase=phase, execution='completed', validity='valid', counts=terminal['counts'],
                    result=str(result), controls_commit=commit, terminal=file_record(result/'terminal.json'),
                    design=design, first_trial_control_comparison=control_comparison, scientific_verdict=None)
            except BaseException as error:
                row = dict(phase=phase, execution='failed', validity='unaccepted', error=str(error),
                           traceback=traceback.format_exc(), design=design, scientific_verdict=None)
                write(out/(phase+'-failure.json'),row)
                rows.append(row)
                write(out/(phase+'-partial.json'),dict(rows=rows,remaining_phases=[p for p,_,_ in declarations[len(rows):]]))
                process_result = base/'jobs'/(q['job_id']+'-'+phase)/'process-result.json'
                safe_to_continue = not invocation_started or (process_result.exists() and
                    load(process_result).get('all_processes_closed') is True)
                # Keep failures separate and continue the other declared cases
                # once closure is proved. An unknown Job Object or a failed
                # cross-platform source control stops only this worker.
                if not safe_to_continue or str(error) == 'baseline_transport_changed':
                    raise
                continue
            rows.append(row)
            write(out/(phase+'-result.json'),row)
        assert source_closure(sdk) == before and helper.inventory(runtime_dir) == inventory
        assert file_record(model_path)['sha256'] == reference['model_data']['sha256']
        write(out/'source-after.json',before)
        completed=[r for r in rows if r['execution']=='completed' and r['validity']=='valid']
        write(out/'terminal.json',dict(execution='completed',validity='valid' if len(completed)==len(rows) else 'partial',rows=rows,
            actual_observations=len(completed)*8,completed_cadence_cases=sum(r['phase']!='baseline' for r in completed),new_Train=False,
            threshold_selected=False,model_revision=q['model_revision'],threshold=q['threshold'],
            full_primary_archival_pending=True,temporal_figures_pending=True,
            full_mode_matrix_accepted=False,scientific_verdict=None))
    except BaseException as error:
        write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc(),scientific_verdict=None))
        raise


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--controls',required=True)
    run(parser.parse_args().controls)


if __name__ == '__main__':
    main()
