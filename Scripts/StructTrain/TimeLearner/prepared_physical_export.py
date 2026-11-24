"""Export complete physical DATA from an explicit recognition boundary.

Preparation retains the full source package in a checked file. Native import
validates it before exporting DATA; no stopped/solo package is relabelled.
The resulting DATA carries no training or calibration certificate.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys


def _write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def prepare_conversion(plan_path):
    """Bind an explicit DATA1 -> DATA2 operation to an immutable native SDK.

    The original source boundary remains diagnostic/solo when applicable.
    Neither an uncompleted Train nor supplied reference data acquires proof.
    """
    return _prepare_physical_edit(plan_path,threshold_candidate=False)


def prepare_threshold(plan_path):
    """Create one native uncalibrated threshold candidate from base recognition DATA."""
    return _prepare_physical_edit(plan_path,threshold_candidate=True)


def _prepare_physical_edit(plan_path,*,threshold_candidate):
    from Scripts.StructTrain.TimeLearner.runtime import file_record, source_closure
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.native_evidence import require,number
    from Scripts.StructTrain.TimeLearner.physical_model_data_evidence import audit_physical_model_data
    from Scripts.StructTrain.TimeLearner.job_source_transport import make_envelope
    from Scripts.StructTrain.TimeLearner.process_runner import verify_runtime
    plan_path=Path(plan_path).resolve(strict=True)
    plan=json.loads(plan_path.read_bytes())
    require(set(plan)=={'kind','schema_version','source_data','runtime_manifest','sdk_source',
            'python_source','controls','inputs','output','job_id'} |
            ({'threshold'} if threshold_candidate else {'conversion_spec','reference_amplitudes'}) and
            plan['kind']==('timelearner_prepared_physical_threshold_plan' if threshold_candidate else
                          'timelearner_prepared_physical_conversion_plan') and
            type(plan['schema_version']) is int and plan['schema_version']==1,
            'physical_conversion_preparation_scope')
    source_path=Path(plan['source_data']['path']).resolve(strict=True)
    runtime_path=Path(plan['runtime_manifest']['path']).resolve(strict=True)
    require(file_record(source_path)==plan['source_data'] and
            file_record(runtime_path)==plan['runtime_manifest'],'physical_conversion_plan_input_changed')
    source=json.loads(source_path.read_bytes())
    audit_physical_model_data(source,frozen=threshold_candidate)
    if threshold_candidate:
        number(plan['threshold'])
        require(source['schema_version']==2 or source['schema_version']==1 and source['source_boundary']['kind'] in
                ('timelearner_recognition_state','timelearner_diagnostic_recognition_state'),
                'physical_threshold_requires_base_recognition_data')
    else:
        require(source['schema_version']==1 and source['source_boundary']['kind'] in
                ('timelearner_completed_state','timelearner_stopped_state'), 'physical_conversion_requires_original_solo_DATA1')
    base=Path('C:/Projects/TimeLearnerWorker') if os.name=='nt' else Path(plan['output']).parent.parent
    allowed=(Path('C:/Projects/TimeLearnerWorker'),) if os.name=='nt' else (
        Path('/home/user/timelearner-refactor'),Path('/media/user/Data/TimeLearnerRefactor'))
    area=base/('jobs' if os.name=='nt' else 'readbacks')
    controls=Path(plan['controls']);inputs=Path(plan['inputs']);output=Path(plan['output'])
    require(base in allowed and base.resolve(strict=True)==base and
            controls.parent==base/('controls' if os.name=='nt' else 'requests') and
            inputs.parent==output.parent==area and output.name==plan['job_id'] and
            len({controls,inputs,output})==3 and all(p.is_absolute() and not p.exists() and not p.is_symlink()
            for p in (controls,inputs,output)), 'physical_conversion_fresh_paths_required')
    for parent in (controls.parent,area):
        require(parent.resolve(strict=True)==parent,'physical_conversion_parent_alias')
    python_source=Path(plan['python_source']).resolve(strict=True)
    sdk_source=Path(plan['sdk_source']).resolve(strict=True)
    require(file_record(python_source/'Scripts/StructTrain/TimeLearner/prepared_physical_export.py')==
            file_record(Path(__file__)), 'physical_conversion_worker_source_mismatch')
    runtime=json.loads(runtime_path.read_bytes())
    require(source_closure(sdk_source)==runtime['source_closure'],'physical_conversion_sdk_changed')
    verify_runtime(runtime)
    controls.mkdir();inputs.mkdir()
    carrier=inputs/('recognition-physical-data.json' if threshold_candidate else 'solo-physical-data.json')
    # A private copy prevents mutations through a hard-linked source alias.
    shutil.copyfile(source_path,carrier)
    require(file_record(source_path)==plan['source_data'] and
            file_record(carrier)['sha256']==plan['source_data']['sha256'], 'physical_conversion_source_changed')
    edit_fields=({'threshold':plan['threshold']} if threshold_candidate else
        dict(conversion_spec=plan['conversion_spec'],reference_amplitudes=plan['reference_amplitudes']))
    job=dict(kind=('timelearner_native_physical_threshold_candidate_job' if threshold_candidate else
        'timelearner_native_physical_model_conversion_job'),schema_version=1,
        implementation_id=source['implementation_id'],source_model_data=source,**edit_fields)
    job['sha256']=sha(job)
    _write(inputs/'native-job-source.json',make_envelope(job,carrier,inputs))
    (controls/'worker.py').write_bytes(Path(__file__).read_bytes())
    _write(controls/'runtime.json',runtime)
    _write(controls/'specification.json',dict(kind=('timelearner_prepared_physical_threshold' if threshold_candidate else
        'timelearner_prepared_physical_conversion'),schema_version=1,
        job_id=plan['job_id'],execution_root=str(base),python_source=str(python_source),sdk_source=str(sdk_source),
        inputs=str(inputs),output=str(output),worker_sha256=file_record(controls/'worker.py')['sha256'],
        input_inventory={p.name:dict(bytes=p.stat().st_size,sha256=file_record(p)['sha256']) for p in inputs.iterdir()},
        source_model_revision=source['model_revision'],source_package_sha256=source['source_boundary']['sha256'],
        source_model_data_sha256=source['sha256'],**edit_fields,resolved_job_sha256=job['sha256'],
        memory_bytes=8*1024**3,maximum_wall_seconds=3600,lock_file=str(base/'locks/worker.lock'),
        disk=dict(minimum_free_bytes=512*1024**2,maximum_output_bytes=256*1024**2)))
    _write(controls/'proposal.json',dict(kind=('physical_DATA_threshold_candidate_preparation' if threshold_candidate else
        'physical_DATA1_recognition_conversion_preparation'),
        preparation_plan=file_record(plan_path),source_model_data=plan['source_data'],
        source_boundary=source['source_boundary'],runtime_manifest=plan['runtime_manifest'],
        training_completed=False,training_certificate_transferred=False,calibration_confirmed=False,
        original_execution_reclassified=False,scientific_verdict=None))
    require(file_record(source_path)==plan['source_data'] and file_record(runtime_path)==plan['runtime_manifest'],
            'physical_conversion_plan_changed_during_preparation')


def prepare(controls, destination, inputs, output, run_id, python_source=None):
    controls = Path(controls).resolve(strict=True)
    prior = json.loads((controls/'specification.json').read_bytes())
    python_source = str(Path(python_source or prior['python_source']).resolve(strict=True))
    sys.path.insert(0, python_source)
    sys.dont_write_bytecode = True
    from Scripts.StructTrain.TimeLearner.runtime import file_record, runtime_content_identity, digest_json
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.job_source_transport import make_envelope,MAXIMUM_SOURCE_BYTES
    native = Path(prior['output'])/'native'
    process = json.loads((Path(prior['output'])/'process-result.json').read_bytes())
    require(process['all_processes_closed'], 'physical_export_source_process_live')
    execution = json.loads((native/'execution.json').read_bytes())
    require(execution['kind'] == 'timelearner_native_diagnostic_evaluation_execution' and
            execution['execution'] == 'completed' and execution['sha256'] ==
            sha({k:v for k,v in execution.items() if k != 'sha256'}), 'physical_export_source_execution')
    source_path = native/'model.json'
    before = file_record(source_path)
    records = {r['path']:r for r in execution['artifacts']}
    require(records['model.json'] == dict(path='model.json', bytes=before['size'], sha256=before['sha256']),
            'physical_export_source_bytes_changed')
    inputs = Path(inputs).absolute()
    output = Path(output).absolute()
    destination = Path(destination).resolve(strict=True)
    base = Path('C:/Projects/TimeLearnerWorker') if os.name == 'nt' else Path(prior['execution_root'])
    area = base/('jobs' if os.name == 'nt' else 'readbacks')
    require(base.resolve(strict=True) == base and inputs.is_relative_to(area) and
            output.is_relative_to(area) and not inputs.is_symlink() and not output.is_symlink(),
            'physical_export_preparation_paths')
    require(not inputs.exists() and not output.exists(), 'physical_export_fresh_paths_required')
    inputs.mkdir(parents=True)
    carrier = inputs/'recognition-source.json'
    if before['size'] > MAXIMUM_SOURCE_BYTES:
        from Scripts.StructTrain.TimeLearner.json_transport import compact_json_transport
        transport = compact_json_transport(source_path,carrier,expected_bytes=before['size'],
            expected_sha256=before['sha256'],maximum_output_bytes=MAXIMUM_SOURCE_BYTES)
        _write(destination/'source-transport.json',transport)
    else:
        os.link(source_path,carrier)
    source = json.loads(carrier.read_bytes())
    require(source['kind'] == 'timelearner_diagnostic_threshold_candidate' and
            source['model_revision'] == execution['model_revision'] and source['sha256'] == execution['model_sha256'] and
            source['sha256'] == sha({k:v for k,v in source.items() if k != 'sha256'}),
            'physical_export_requires_explicit_diagnostic_recognition_candidate')
    job = dict(kind='timelearner_native_physical_model_export_job', schema_version=1,
               implementation_id=source['implementation_id'], source_state=source)
    job['sha256'] = sha(job)
    envelope = make_envelope(job,carrier,inputs)
    _write(inputs/'native-job-source.json', envelope)
    (destination/'worker.py').write_bytes(Path(__file__).read_bytes())
    runtime = json.loads((controls/'runtime.json').read_bytes())
    prior_backend = runtime.get('windows_backend')
    if os.name == 'nt':
        # The native SDK remains immutable. Bind a fresh manifest to the exact
        # runner module from this explicitly selected Python source checkout.
        runtime['windows_backend'] = file_record(Path(python_source)/'Scripts/StructTrain/TimeLearner/windows_process.py')
        runtime['build_flags'] = dict(runtime['build_flags'],
            windows_backend_sha256=runtime['windows_backend']['sha256'])
        runtime['runtime_identity'] = runtime_content_identity(runtime)
        runtime['runtime_fingerprint'] = digest_json(runtime['runtime_identity'])
    _write(destination/'runtime.json',runtime)
    spec = dict(kind='timelearner_prepared_physical_export', schema_version=1,
        job_id=output.name, execution_root=str(base), python_source=python_source,
        sdk_source=prior['sdk_source'], inputs=str(inputs), output=str(output),
        worker_sha256=file_record(destination/'worker.py')['sha256'],
        input_inventory={p.name:dict(bytes=p.stat().st_size,sha256=file_record(p)['sha256']) for p in inputs.iterdir()},
        source_package_sha256=source['sha256'], source_model_revision=source['model_revision'],
        resolved_job_sha256=job['sha256'], memory_bytes=8*1024**3, maximum_wall_seconds=3600,
        lock_file=str(base/'locks/worker.lock'),
        disk=dict(minimum_free_bytes=512*1024**2, maximum_output_bytes=256*1024**2))
    _write(destination/'specification.json', spec)
    _write(destination/'proposal.json', dict(kind='complete_recognition_physical_export_preparation',
        source_execution_sha256=execution['sha256'], source_model_revision=source['model_revision'],
        source_package_sha256=source['sha256'], original_process_execution=process['execution'],
        original_runtime_provenance=process['runtime_provenance'], source_history_preserved=True,
        previous_windows_backend=prior_backend, effective_windows_backend=runtime.get('windows_backend'),
        original_execution_reclassified=False, run_id=run_id, training_completed=False, scientific_verdict=None))
    require(file_record(source_path) == before, 'physical_export_source_changed_during_preparation')


def run(controls):
    controls = Path(controls).resolve(strict=True)
    spec = json.loads((controls/'specification.json').read_bytes())
    sys.path.insert(0, spec['python_source'])
    sys.dont_write_bytecode = True
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.runtime import file_record, source_closure, applied_loader_environment
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.native_cli import inspect_native_cli
    from Scripts.StructTrain.TimeLearner.physical_model_data_evidence import audit_physical_model_data
    from Scripts.StructTrain.TimeLearner.native_pipeline_worker import _artifact_records
    conversion=spec['kind']=='timelearner_prepared_physical_conversion'
    threshold_candidate=spec['kind']=='timelearner_prepared_physical_threshold'
    require(os.name in ('posix','nt') and spec['kind'] in ('timelearner_prepared_physical_export',
            'timelearner_prepared_physical_conversion','timelearner_prepared_physical_threshold') and
            spec['schema_version'] == 1, 'physical_export_worker_scope')
    inputs = Path(spec['inputs']).resolve(strict=True)
    output = Path(spec['output']).absolute()
    base = Path(spec['execution_root']).resolve(strict=True)
    allowed = (Path('C:/Projects/TimeLearnerWorker'),) if os.name=='nt' else (
        Path('/home/user/timelearner-refactor'),Path('/media/user/Data/TimeLearnerRefactor'))
    area = base/('jobs' if os.name=='nt' else 'readbacks')
    require(base in allowed and output.is_relative_to(area) and inputs.is_relative_to(area) and
            not output.exists(), 'physical_export_paths')
    shared_lock=base/'locks/worker.lock'
    require(Path(spec.get('lock_file',str(shared_lock)))==shared_lock,
            'physical_export_shared_worker_lock_scope')
    output.mkdir()
    def inventory():
        require(all(p.is_file() and not p.is_symlink() and not getattr(p,'is_junction',lambda:False)()
                    for p in inputs.iterdir()), 'physical_export_input_alias')
        return {p.name:dict(bytes=p.stat().st_size,sha256=file_record(p)['sha256']) for p in inputs.iterdir()}
    registry = lease = None
    try:
        require(inventory() == spec['input_inventory'] and
                file_record(Path(__file__))['sha256'] == spec['worker_sha256'], 'physical_export_input_changed')
        runtime = json.loads((controls/'runtime.json').read_bytes())
        require(source_closure(Path(spec['sdk_source'])) == runtime['source_closure'], 'physical_export_sdk_changed')
        cli=inspect_native_cli(runtime,['physical-model-export'],require_file_source=True,evidence_output=output)
        _write(output/'cli.json',cli)
        require(not threshold_candidate or 'physical-data-threshold-v1' in cli['help_text'],
                'physical_threshold_native_capability_missing')
        disk = spec['disk']
        require(shutil.disk_usage(base).free >= sum(disk.values()), 'physical_export_disk_admission')
        if os.name != 'nt':
            from Scripts.StructTrain.TimeLearner.contained_runner import execute
            from Scripts.StructTrain.TimeLearner.contained_process import inspect
            from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
            registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
            lease = registry.reserve(spec['job_id'], [dict(path=str(p),access=a) for p,a in
                ((inputs,'read'),(controls,'read'),(Path(spec['sdk_source']),'read'),
                 (Path(runtime['executable']['path']).parent,'read'),(output,'write'))],
                ttl_seconds=4200, demands=dict(slots=1,memory_bytes=9*1024**3,disk_bytes=disk['maximum_output_bytes']))
        import time
        if os.name == 'nt':
            def output_bytes():
                total=0
                for p in output.rglob('*'):
                    try:
                        require(not p.is_symlink() and not p.is_junction(),'physical_export_output_alias')
                        if p.is_file():total+=p.stat().st_size
                    except FileNotFoundError:
                        pass  # The native writer atomically renames temporary files.
                return total
        else:
            from Scripts.StructTrain.TimeLearner.owned_python_job import _allocated_output_bytes
            def output_bytes():return _allocated_output_bytes(output)
        last=[0.]
        def monitor(state):
            if time.monotonic()-last[0] < 1:return
            last[0]=time.monotonic()
            if registry is not None:registry.heartbeat(lease['token'],ttl_seconds=4200)
            require(shutil.disk_usage(base).free >= disk['minimum_free_bytes'], 'physical_export_disk_floor')
            require(output_bytes() <= disk['maximum_output_bytes'], 'physical_export_output_budget')
        arguments=['--app-ini',runtime['app_ini']['path'],'--timelearner-physical-model-export',
                   str(inputs/'native-job-source.json'),'--timelearner-output',str(output/'native')]
        if os.name == 'nt':
            from Scripts.StructTrain.TimeLearner.windows_process import execute
            from Scripts.StructTrain.TimeLearner.native_gate import _environment
            with _environment({k:runtime['loader_environment'].get(k)
                               for k in ('PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM')}):
                result=execute(runtime,arguments,Path(runtime['executable']['path']).parent,output/'process',
                    memory_bytes=spec['memory_bytes'],maximum_processes=64,
                    maximum_wall_seconds=spec['maximum_wall_seconds'],lock_file=shared_lock,
                    cooperative_capture=True,monitor=monitor)
        else:
            with applied_loader_environment(runtime):
                result=execute(runtime,arguments,Path(runtime['executable']['path']).parent,output/'process',
                    spec['maximum_wall_seconds'],memory_bytes=spec['memory_bytes'],tasks=128,
                    cooperative_capture=True,monitor=monitor)
        _write(output/'process-result.json',result)
        require(result['execution']=='completed' and result['all_processes_closed'] and
                result['runtime_provenance']=='loaded_files_captured', 'physical_export_native_incomplete')
        native=output/'native'
        execution=json.loads((native/'execution.json').read_bytes())
        require(execution['sha256']==sha({k:v for k,v in execution.items() if k!='sha256'}) and
                execution['kind']==('timelearner_native_physical_threshold_candidate_execution' if threshold_candidate else
                                   'timelearner_native_physical_model_conversion_execution' if conversion else
                                   'timelearner_native_physical_model_export_execution') and
                execution['execution']=='completed' and execution['job_sha256']==spec['resolved_job_sha256'] and
                execution['physical_roundtrip_verified'] and not execution['source_evidence_included'] and
                not execution['training_certificate_transferred'] and not execution['controller_checkpoint_created'],
                'physical_export_native_evidence_changed')
        require(_artifact_records(native,execution)=={'model.json','input-projection.json'},'physical_export_artifacts')
        model=json.loads((native/'model.json').read_bytes())
        projection=json.loads((native/'input-projection.json').read_bytes())
        require(projection['sha256']==sha({k:v for k,v in projection.items() if k!='sha256'}) and
                projection['job_sha256']==spec['resolved_job_sha256'] and
                model['sha256']==execution['model_sha256'] and
                (model['source_recognition_data']['model_revision'] if threshold_candidate else
                 model['source_solo_revision'] if conversion else model['model_revision'])==spec['source_model_revision'] and
                model['source_boundary']['sha256']==spec['source_package_sha256'] and
                execution['source_boundary']==projection['source_boundary']==model['source_boundary'],
                'physical_export_boundary_changed')
        if conversion:
            require(model['schema_version']==2 and execution['source_model_data_sha256']==
                    projection['source_model_data_sha256']==model['source_model_data']['sha256']==
                    spec['source_model_data_sha256'] and model['conversion_spec']==projection['conversion_spec']==
                    spec['conversion_spec'] and model['reference_amplitudes']==projection['reference_amplitudes']==
                    spec['reference_amplitudes'] and execution['calibration_confirmed'] is False,
                    'physical_conversion_operation_changed')
        if threshold_candidate:
            require(model['schema_version']==3 and execution['source_model_data_sha256']==
                    projection['source_model_data_sha256']==model['source_recognition_data']['sha256']==
                    spec['source_model_data_sha256'] and model['threshold']==projection['threshold']==spec['threshold'] and
                    execution['calibration_confirmed'] is False,'physical_threshold_operation_changed')
        audit=audit_physical_model_data(model,frozen=True)
        require(inventory()==spec['input_inventory'] and
                source_closure(Path(spec['sdk_source']))==runtime['source_closure'], 'physical_export_inputs_changed_after')
        _write(output/'terminal.json',dict(native_process_completed=True,physical_roundtrip_verified=True,
            portable_model_audit=audit,model_revision=model['model_revision'],model_sha256=model['sha256'],
            source_package_sha256=spec['source_package_sha256'],source_evidence_included=False,
            explicit_conversion=conversion,explicit_threshold_candidate=threshold_candidate,training_certificate_transferred=False,
            calibration_confirmed=False,original_execution_reclassified=False,scientific_verdict=None))
    except BaseException as error:
        import traceback
        _write(output/'exception.json',dict(reason=str(error),traceback=traceback.format_exc(),scientific_verdict=None))
        raise
    finally:
        if lease is not None and (not (output/'process/contained/request.json').exists() or
                                 inspect(output/'process/contained')['all_processes_closed']):
            registry.release(lease['token'],note='Physical recognition DATA export closed; no training or calibration authority transferred')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--controls')
    parser.add_argument('--conversion-plan')
    parser.add_argument('--threshold-plan')
    for name in ('destination','inputs','output','run-id'):parser.add_argument('--'+name)
    parser.add_argument('--python-source')
    args=parser.parse_args()
    if args.conversion_plan or args.threshold_plan:
        if args.conversion_plan and args.threshold_plan:parser.error('select one physical edit plan')
        if any((args.controls,args.destination,args.inputs,args.output,args.run_id,args.python_source)):
            parser.error('physical edit plan cannot be combined with other modes')
        (prepare_threshold if args.threshold_plan else prepare_conversion)(args.threshold_plan or args.conversion_plan)
        return
    if not args.controls:parser.error('--controls required for export preparation or execution')
    if any((args.destination,args.inputs,args.output,args.run_id)):
        if not all((args.destination,args.inputs,args.output,args.run_id)):parser.error('all preparation paths required')
        prepare(args.controls,args.destination,args.inputs,args.output,args.run_id,args.python_source)
    else:
        if args.python_source:parser.error('--python-source applies only to preparation')
        run(args.controls)


if __name__=='__main__':main()
