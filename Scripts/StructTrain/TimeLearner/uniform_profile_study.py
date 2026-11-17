"""One cold native Train with a fixed uniform storage profile.

An explicit paired declaration changes only the immutable physics profile and
its class. Search tolerances/budgets are inherited; larger cable domain is
common to both cases. Valid negative outcomes are retained, never classified.
"""
from copy import deepcopy
import argparse
import math
import os
import re
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
from .uniform_profile_physics import audit_uniform_profile, require_fixed_capacitance_policy


def rebase_full_observation_window(configuration, reference_frames):
    """Encode the same full recorded domain around this profile's own seed.

    Coordinates are data, not an imported amplitude reference or a certificate.
    Native Train must capture and validate its references again.
    """
    policy = configuration['composite_measurement']['candidate_window_policy']
    n = len(configuration['model']['inputs'])
    require(type(reference_frames) is list and n > 0 and
            len(reference_frames) == len(policy['inputs']) == n,
            'uniform_study_reference_window_dimensions')
    for p, frames in zip(policy['inputs'], reference_frames):
        require(type(frames) is dict and
                set(frames) == {'first_frame', 'last_frame', 'frame_count'} and
                all(type(v) is int for v in frames.values()) and
                0 < frames['first_frame'] <= frames['last_frame'] < frames['frame_count']-1 and
                p['hard_first_frame'] == 0 and
                p['hard_last_frame'] == frames['frame_count']-1 and
                p['maximum_window_frames'] == frames['frame_count'] and
                all(p[k] == 0 for k in ('delay_frames_per_segment', 'length_guard_frames',
                    'synapse_count_guard_frames', 'resistance_change_guard_frames',
                    'capacitance_change_guard_frames')),
                'uniform_study_not_full_observation_recipe')
        p['base_left_guard_frames'] = frames['first_frame']
        p['base_right_guard_frames'] = p['hard_last_frame']-frames['last_frame']


def declare_case(original, archive, variant, reference_frames=None, *, run_label=None):
    require(variant in (0,3), 'uniform_study_unknown_profile')
    c=original['configuration']
    require_fixed_capacitance_policy(c)
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
    if reference_frames is not None:
        require(type(reference_frames) is list and len(reference_frames) == 4,
                'uniform_study_reference_window_dimensions')
        require(all(type(f) is dict and f.get('frame_count') == 3601 for f in reference_frames),
                'uniform_study_not_full_observation_recipe')
        rebase_full_observation_window(q, reference_frames)
        q['run_id']+='/measured-window-rebased'
    if run_label is not None:
        require(type(run_label) is str and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_label),
                'uniform_study_invalid_run_label')
        q['run_id']+='/'+run_label
    result['profile_archives']=[deepcopy(archive)]
    result=_signed({k:v for k,v in result.items() if k!='sha256'})
    validate_job('preflight',result);validate_job('train',result)
    return result


def _condition(job,initial,runtime,*,native_memory_bytes=4*1024**3,native_tasks=64):
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
                              maximum_wall_seconds=c['maximum_wall_seconds'],
                              native_memory_bytes=native_memory_bytes,native_tasks=native_tasks),
        randomness_spec=dict(declared_random_factors=[],cold_runs_per_condition=1))
    artifacts={role:artifact(role,payloads[role]) for role in CONDITION_ROLES}
    condition=ConditionSpec(controller_version=2,amplitude_goal='captured_per_input',
                           **{role:a['sha256'] for role,a in artifacts.items()})
    condition.resolve({a['sha256']:a for a in artifacts.values()})
    return dict(condition=condition.to_object(),artifacts=artifacts)


def native_resource_demands(controller, memory_bytes, tasks):
    """Charge the live controller and its sibling native unit explicitly.

    This is the local managed-family budget, not evidence of free host RAM or
    a replacement for admission by the outer worker's global scheduler.
    """
    require(type(memory_bytes) is int and 0 < memory_bytes < 2**63 and
            type(tasks) is int and 0 < tasks < 2**63,
            'uniform_study_invalid_native_resources')
    require(type(controller.get('memory_max')) is int and controller['memory_max'] > 0 and
            type(controller.get('tasks_max')) is int and controller['tasks_max'] > 0,
            'uniform_study_unbounded_controller_resources')
    result=dict(slots=1,memory_bytes=controller['memory_max']+memory_bytes,
                disk_bytes=4*1024**3,tasks=controller['tasks_max']+tasks)
    require(all(0 < value < 2**63 for value in result.values()),
            'uniform_study_combined_resource_overflow')
    return result


def run(job_path,runtime_path,controller,expected_initial_path,output,*,finalization_seconds=300.,
        native_memory_bytes=4*1024**3,native_tasks=64):
    job_path=Path(job_path).resolve(strict=True);runtime_path=Path(runtime_path).resolve(strict=True)
    expected_initial_path=Path(expected_initial_path).resolve(strict=True);output=Path(output).resolve()
    require(not output.exists(),'uniform_study_result_exists')
    inputs=(job_path,runtime_path,expected_initial_path)
    require(not any(p.is_relative_to(output) for p in inputs),'uniform_study_output_overlaps_inputs')
    before={str(p):frozen_digest(p,256*1024**2) for p in inputs}
    job=load(job_path);validate_job('train',job)
    require_fixed_capacitance_policy(job['configuration'])
    runtime=load(runtime_path);verify_runtime(runtime)
    c=job['configuration'];require(c['model']['normalization']=='N1' and c['model']['branch'] is True,
                                 'uniform_study_not_branch_N1')
    limits=training_execution_limits(c,finalization_seconds)
    state=inspect(controller)
    require(state['execution']=='running' and not state['all_processes_closed'] and
            state['binding']['initial_main_pid']==os.getpid(),'uniform_study_controller_not_owner')
    demands=native_resource_demands(state,native_memory_bytes,native_tasks)
    output.mkdir(parents=True);_write(output/'controller-limits-readback.json',state)
    _write(output/'execution-limits.json',dict(limits,native_memory_bytes=native_memory_bytes,
        native_tasks=native_tasks,managed_family_demands=demands))
    registry=Reservations(output/'leases.sqlite3',managed_units=True,
        capacity=demands)
    lease=registry.reserve('uniform-profile-Branch-N1',[dict(path=str(output/'runs'),access='write')],
        demands=demands,
        controller_directory=str(controller),ttl_seconds=7200)
    policy=policy_for_reservation(registry,lease['token'],memory_bytes=native_memory_bytes,tasks=native_tasks)
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
    condition=_condition(job,initial,runtime,native_memory_bytes=native_memory_bytes,
                         native_tasks=native_tasks);_write(output/'condition.json',condition)
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
        native_process_resources=dict(memory_bytes=native_memory_bytes,tasks=native_tasks),
        package_audit=package_audit,physical_audit=physical_audit,
        package_path=None if package_path is None else package_path.relative_to(output).as_posix(),
        condition_fingerprint=digest(condition['condition']),classification_assessed=False,scientific_verdict=None)
    _write(output/'index.json',record)
    return record


def reference_window_frames(native):
    """Audited characterization coordinates only; new Train recaptures references."""
    from .candidate_window_binding_evidence import reference_seed
    native=Path(native).resolve(strict=True)
    paths=[native/n for n in ('train_stopped_state.json','train_learned_state.json') if (native/n).is_file()]
    require(len(paths)==1,'uniform_study_reference_package_missing')
    p=load(paths[0]);summary=load(paths[0].with_name(paths[0].name.replace('_state.','_summary.')))
    audit=audit_candidate_window_recovery_package(p,summary=summary,
                                                external_resolver=filesystem_primary_resolver(native))
    require(p['reference_complete'] is True and p['configuration']['model']['branch'] is True and
            p['configuration']['model']['normalization']=='N1','uniform_study_reference_source_not_complete')
    source=p['measurement_archive']['source_binding']
    records=[r for r in p['measurement_archive']['records'] if r['purpose']=='reference']
    require(len(records)==4 and {r['logical_request']['input_index'] for r in records}==set(range(4)),
            'uniform_study_reference_inventory')
    records.sort(key=lambda r:r['logical_request']['input_index'])
    seeds=[reference_seed(r,source,p['protocol']) for r in records]
    frames=[{k:seed[k] for k in ('first_frame','last_frame','frame_count')} for seed in seeds]
    return dict(frames=frames,source_package_sha256=frozen_digest(paths[0],256*1024**2),
                source_origin=p['measurement_archive']['source_origin'],source_data_audited=True,
                references_imported_into_train=False,training_certificate_verified=False,scientific_verdict=None)


def prepare_cold(original_path, profile_path, reference_native, output, *, variant,
                 maximum_wall_seconds=None, maximum_group_wall_seconds=None, run_label=None):
    """Prepare a cold job using audited coordinates, without importing amplitudes."""
    require(type(variant) is int and variant in (0, 3), 'uniform_study_unknown_profile')
    if maximum_wall_seconds is not None:
        require(type(maximum_wall_seconds) in (int, float) and
                math.isfinite(maximum_wall_seconds) and maximum_wall_seconds > 0,
                'uniform_study_invalid_wall_budget')
    if maximum_group_wall_seconds is not None:
        require(type(maximum_group_wall_seconds) in (int, float) and
                math.isfinite(maximum_group_wall_seconds) and maximum_group_wall_seconds > 0,
                'uniform_study_invalid_group_wall_budget')
    original_path = Path(original_path).resolve(strict=True)
    profile_path = Path(profile_path).resolve(strict=True)
    reference_native = Path(reference_native).resolve(strict=True)
    output = Path(output).resolve()
    require(not output.exists(), 'uniform_study_preparation_exists')
    require(not output.is_relative_to(reference_native) and
            not reference_native.is_relative_to(output) and
            not any(p.is_relative_to(output) for p in (original_path, profile_path)),
            'uniform_study_preparation_overlaps_inputs')
    inputs = (original_path, profile_path)
    before = {str(p): frozen_digest(p, 256*1024**2) for p in inputs}
    original, archive = load(original_path), load(profile_path)
    validate_job('train', original)
    require_fixed_capacitance_policy(original['configuration'])
    if maximum_group_wall_seconds is not None:
        require(maximum_group_wall_seconds <= (maximum_wall_seconds if
                maximum_wall_seconds is not None else original['configuration']['maximum_wall_seconds']),
                'uniform_study_group_wall_exceeds_attempt')
    packages = [reference_native/name for name in
                ('train_stopped_state.json', 'train_learned_state.json')
                if (reference_native/name).is_file()]
    require(len(packages) == 1, 'uniform_study_reference_package_missing')
    package_before = frozen_digest(packages[0], 256*1024**2)
    source = load(packages[0])
    configuration = source.get('configuration', {})
    require(type(configuration) is dict and type(configuration.get('model')) is dict and
            configuration['model'].get('neuron_class') ==
            'TLNativeFast'+str(variant)+'F2000_Neuron',
            'uniform_study_reference_class_mismatch')
    require(configuration['model'].get('initial_isi') ==
            original['configuration']['model']['initial_isi'] and
            all(configuration.get(k) == original['configuration'][k] for k in
                ('duration', 'stimulus_profile', 'windows', 'peak_selection')),
            'uniform_study_reference_protocol_mismatch')
    characterization = reference_window_frames(reference_native)
    require(characterization['source_package_sha256'] == package_before,
            'uniform_study_reference_changed')
    changed = deepcopy(original)
    change = {}
    if maximum_wall_seconds is not None:
        old_wall = changed['configuration']['maximum_wall_seconds']
        changed['configuration']['maximum_wall_seconds'] = float(maximum_wall_seconds)
        change['maximum_wall_seconds'] = dict(before=old_wall, after=float(maximum_wall_seconds))
    if maximum_group_wall_seconds is not None:
        composite = changed['configuration']['composite_measurement']
        old_wall = composite['maximum_group_wall_seconds']
        composite['maximum_group_wall_seconds'] = float(maximum_group_wall_seconds)
        change['maximum_group_wall_seconds'] = dict(before=old_wall,
                                                    after=float(maximum_group_wall_seconds))
    if change:
        changed = _signed({k: v for k, v in changed.items() if k != 'sha256'})
    else:
        change = None
    job = declare_case(changed, archive, variant, characterization['frames'],
                       run_label=run_label)
    require(before == {str(p): frozen_digest(p, 256*1024**2) for p in inputs} and
            package_before == frozen_digest(packages[0], 256*1024**2),
            'uniform_study_preparation_input_changed')
    declaration = dict(variant=variant, run_label=run_label,
                       before_job_sha256=original['sha256'], budget_change=change,
                       reference_frames=characterization['frames'])
    receipt = dict(kind='timelearner_uniform_cold_preparation', schema_version=1,
                   original_job_sha256=original['sha256'], job_sha256=job['sha256'],
                   inputs=before, reference_package=package_before,
                   characterization=characterization, budget_change=change,
                   execution_performed=False, amplitude_references_imported=False,
                   learned_parameters_imported=False, classification_assessed=False,
                   scientific_verdict=None)
    output.mkdir(parents=True)
    (output/'original-before-budget.json').write_bytes(original_path.read_bytes())
    (output/'profile.json').write_bytes(profile_path.read_bytes())
    for name, value in (('original.json', changed), ('job.json', job),
                        ('declaration.json', declaration),
                        ('reference-characterization.json', characterization),
                        ('preparation.json', receipt)):
        _write(output/name, value)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare-cold', help='prepare an audited cold profile job')
    prepare.add_argument('original', type=Path)
    prepare.add_argument('profile', type=Path)
    prepare.add_argument('reference_native', type=Path)
    prepare.add_argument('output', type=Path)
    prepare.add_argument('--variant', type=int, choices=(0, 3), required=True)
    prepare.add_argument('--maximum-wall-seconds', type=float)
    prepare.add_argument('--maximum-group-wall-seconds', type=float,
        help='explicit per-composite-group wall limit; must fit within the attempt wall limit')
    prepare.add_argument('--run-label')
    args = parser.parse_args(argv)
    prepare_cold(args.original, args.profile, args.reference_native, args.output,
                 variant=args.variant, maximum_wall_seconds=args.maximum_wall_seconds,
                 maximum_group_wall_seconds=args.maximum_group_wall_seconds,
                 run_label=args.run_label)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
