"""One cold native Train with a fixed uniform storage profile.

An explicit paired declaration changes only the immutable physics profile and
its class. Search tolerances/budgets are inherited; larger cable domain is
common to both cases. Valid negative outcomes are retained, never classified.
"""
from copy import deepcopy
import os
from pathlib import Path
from .candidate_window_package_evidence import audit_candidate_window_recovery_package
from .collector_provenance import frozen_digest
from .composite_primary import filesystem_primary_resolver
from .condition import CONDITION_ROLES, ConditionSpec, artifact
from .contained_process import inspect
from .model_identity import canonical_model_sha256 as digest
from .n1_protocol_robustness import _signed
from .native_calibration_worker import _write
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest, run_job, validate_job
from .native_process_policy import policy_for_reservation
from .process_runner import verify_runtime
from .resource_reservations import Reservations
from .stock_candidate_window_study import training_execution_limits
from .uniform_profile_physics import audit_uniform_profile


def declare_case(original, archive, variant):
    require(variant in (0,3), 'uniform_study_unknown_profile')
    c=original['configuration']
    require(c['schema_version']==8 and c['model']['branch'] is True and
            c['model']['normalization']=='N1' and len(c['model']['inputs'])==4 and
            c['model']['neuron_class']=='NSPNeuronGen' and c['model']['maximum_cable_length']==100,
            'uniform_study_original_not_cold_branch_N1')
    require(all(i==dict(attachment=1,synapses=1,resistance=86e6) for i in c['model']['inputs']) and
            c['search']['tolerances']==dict(amplitude_absolute=1e-5,amplitude_relative=0.,sync=.02),
            'uniform_study_original_protocol_changed')
    result=deepcopy(original);q=result['configuration']
    q['run_id']='Branch-uniform-profile'+str(variant)+'-cold-N1-L256'
    q['model']['neuron_class']='TLNativeFast'+str(variant)+'F2000_Neuron'
    q['model']['maximum_cable_length']=256
    for bound in q['search']['bounds'][:-1]:
        require(bound['maximum_length']==100,'uniform_study_original_length_bound_changed')
        bound['maximum_length']=256
    require(q['search']['bounds'][-1]==c['search']['bounds'][-1] and
            q['search']['bounds'][-1]['maximum_length']==1, 'uniform_study_anchor_changed')
    result['profile_archives']=[deepcopy(archive)]
    result=_signed({k:v for k,v in result.items() if k!='sha256'})
    validate_job('preflight',result);validate_job('train',result)
    return result


def _condition(job,initial,runtime):
    c=deepcopy(job['configuration']);c.pop('run_id')
    code={k:v['head'] for k,v in runtime['source_closure'].items()}
    payloads=dict(
        algorithm=dict(id='native-candidate-window-recovery-uniform-profile-pair-v1',
                       native_code=code,executable_sha256=runtime['executable']['sha256']),
        model_spec=c['model'],
        storage_profiles=dict(neuron_class=c['model']['neuron_class'],effective_model=initial['model']),
        initial_state=dict(cold=True,model_revision=initial['sha256']),training_plan=c,
        input_data=dict(target_isi=c['model']['initial_isi'],sample_id=c['sample_id']),
        presentation_protocol={k:c[k] for k in ('duration','windows','peak_selection','stimulus_profile')},
        calibration_spec=dict(performed=False),
        evaluation_spec=dict(performed=False,classification_assessed=False),
        execution_policy=dict(maximum_model_ticks=job['maximum_model_ticks'],
                              maximum_wall_seconds=c['maximum_wall_seconds']),
        randomness_spec=dict(declared_random_factors=[],cold_runs_per_condition=1))
    artifacts={role:artifact(role,payloads[role]) for role in CONDITION_ROLES}
    condition=ConditionSpec(controller_version=2,amplitude_goal='captured_per_input',
                           **{role:a['sha256'] for role,a in artifacts.items()})
    condition.resolve({a['sha256']:a for a in artifacts.values()})
    return dict(condition=condition.to_object(),artifacts=artifacts)


def run(job_path,runtime_path,controller,expected_initial_path,output,*,finalization_seconds=300.):
    job_path=Path(job_path).resolve(strict=True);runtime_path=Path(runtime_path).resolve(strict=True)
    expected_initial_path=Path(expected_initial_path).resolve(strict=True);output=Path(output).resolve()
    require(not output.exists(),'uniform_study_result_exists')
    inputs=(job_path,runtime_path,expected_initial_path)
    require(not any(p.is_relative_to(output) for p in inputs),'uniform_study_output_overlaps_inputs')
    before={str(p):frozen_digest(p,256*1024**2) for p in inputs}
    job=load(job_path);validate_job('train',job);runtime=load(runtime_path);verify_runtime(runtime)
    c=job['configuration'];require(c['model']['normalization']=='N1' and c['model']['branch'] is True,
                                 'uniform_study_not_branch_N1')
    limits=training_execution_limits(c,finalization_seconds)
    state=inspect(controller)
    require(state['execution']=='running' and not state['all_processes_closed'] and
            state['binding']['initial_main_pid']==os.getpid(),'uniform_study_controller_not_owner')
    output.mkdir(parents=True);_write(output/'controller-limits-readback.json',state)
    _write(output/'execution-limits.json',limits)
    registry=Reservations(output/'leases.sqlite3',managed_units=True,
        capacity=dict(slots=1,memory_bytes=state['memory_max']+6*1024**3,disk_bytes=8*1024**3,tasks=512))
    lease=registry.reserve('uniform-profile-Branch-N1',[dict(path=str(output/'runs'),access='write')],
        demands=dict(slots=1,memory_bytes=state['memory_max']+4*1024**3,disk_bytes=4*1024**3,tasks=256),
        controller_directory=str(controller),ttl_seconds=7200)
    policy=policy_for_reservation(registry,lease['token'],memory_bytes=4*1024**3,tasks=64)
    preflight=run_job('preflight',job_path,None,runtime_path,output/'runs/preflight',180.,process_policy=policy)
    require(preflight['execution']=='completed' and preflight['validity']=='valid',
            'uniform_study_preflight_invalid')
    require(inspect(output/'runs/preflight/process/contained')['all_processes_closed'],
            'uniform_study_preflight_live')
    initial=load(output/'runs/preflight/native/initial-state.json')['identity']
    expected=load(expected_initial_path)['identity']
    initial_physics=audit_uniform_profile(expected,initial)
    require(initial_physics['membranes_checked']['initial']==initial_physics['membranes_checked']['final']==2,
            'uniform_study_not_cold_graph')
    condition=_condition(job,initial,runtime);_write(output/'condition.json',condition)
    result=run_job('train',job_path,None,runtime_path,output/'runs/train',
                   limits['process_maximum_wall_seconds'],process_policy=policy)
    require(inspect(output/'runs/train/process/contained')['all_processes_closed'],
            'uniform_study_train_group_live')
    package_audit=None;physical_audit=None;package_path=None
    if result['validity']=='valid':
        audit_run_manifest(output/'runs/train/run-manifest.json')
        root=output/'runs/train/native'
        packages=[p for p in (root/'train_learned_state.json',root/'train_stopped_state.json') if p.is_file()]
        require(len(packages)==1,'uniform_study_actual_terminal_package_required')
        package_path=packages[0];package=load(package_path)
        summary=load(package_path.with_name(package_path.name.replace('_state.json','_summary.json')))
        physical_audit=audit_uniform_profile(initial,package['neuron']['graph']['identity'])
        package_audit=audit_candidate_window_recovery_package(package,summary=summary,
                                     external_resolver=filesystem_primary_resolver(root))
    registry.release(lease['token'],note='Native groups closed; validity and convergence remain separate.')
    require(before=={str(p):frozen_digest(p,256*1024**2) for p in inputs},'uniform_study_input_changed')
    record=dict(kind='timelearner_uniform_profile_training_result',schema_version=1,
        execution=result['execution'],validity=result['validity'],initial_physics=initial_physics,
        package_audit=package_audit,physical_audit=physical_audit,
        package_path=None if package_path is None else package_path.relative_to(output).as_posix(),
        condition_fingerprint=digest(condition['condition']),classification_assessed=False,scientific_verdict=None)
    _write(output/'index.json',record)
    return record
