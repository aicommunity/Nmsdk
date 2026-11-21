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


def prepare(controls, destination, inputs, output, run_id):
    controls = Path(controls).resolve(strict=True)
    prior = json.loads((controls/'specification.json').read_bytes())
    sys.path.insert(0, prior['python_source'])
    sys.dont_write_bytecode = True
    from Scripts.StructTrain.TimeLearner.runtime import file_record
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.job_source_transport import make_envelope
    native = Path(prior['output'])/'native'
    process = json.loads((Path(prior['output'])/'process-result.json').read_bytes())
    require(process['all_processes_closed'], 'physical_export_source_process_live')
    execution = json.loads((native/'execution.json').read_bytes())
    require(execution['execution'] == 'completed' and execution['sha256'] ==
            sha({k:v for k,v in execution.items() if k != 'sha256'}), 'physical_export_source_execution')
    source_path = native/'model.json'
    before = file_record(source_path)
    records = {r['path']:r for r in execution['artifacts']}
    require(records['model.json'] == dict(path='model.json', bytes=before['size'], sha256=before['sha256']),
            'physical_export_source_bytes_changed')
    source = json.loads(source_path.read_bytes())
    require(source['kind'] == 'timelearner_diagnostic_threshold_candidate' and
            source['model_revision'] == execution['model_revision'] and
            source['sha256'] == sha({k:v for k,v in source.items() if k != 'sha256'}),
            'physical_export_requires_explicit_diagnostic_recognition_candidate')
    job = dict(kind='timelearner_native_physical_model_export_job', schema_version=1,
               implementation_id=source['implementation_id'], source_state=source)
    job['sha256'] = sha(job)
    inputs = Path(inputs).absolute()
    output = Path(output).absolute()
    destination = Path(destination).resolve(strict=True)
    require(not inputs.exists() and not output.exists(), 'physical_export_fresh_paths_required')
    inputs.mkdir(parents=True)
    os.link(source_path, inputs/'recognition-source.json')
    envelope = make_envelope(job, inputs/'recognition-source.json', inputs)
    _write(inputs/'native-job-source.json', envelope)
    (destination/'worker.py').write_bytes(Path(__file__).read_bytes())
    (destination/'runtime.json').write_bytes((controls/'runtime.json').read_bytes())
    spec = dict(kind='timelearner_prepared_physical_export', schema_version=1,
        job_id=output.name, execution_root=prior['execution_root'], python_source=prior['python_source'],
        sdk_source=prior['sdk_source'], inputs=str(inputs), output=str(output),
        worker_sha256=file_record(destination/'worker.py')['sha256'],
        input_inventory={p.name:dict(bytes=p.stat().st_size,sha256=file_record(p)['sha256']) for p in inputs.iterdir()},
        source_package_sha256=source['sha256'], source_model_revision=source['model_revision'],
        resolved_job_sha256=job['sha256'], memory_bytes=8*1024**3, maximum_wall_seconds=3600,
        disk=dict(minimum_free_bytes=512*1024**2, maximum_output_bytes=256*1024**2))
    _write(destination/'specification.json', spec)
    _write(destination/'proposal.json', dict(kind='complete_recognition_physical_export_preparation',
        source_execution_sha256=execution['sha256'], source_model_revision=source['model_revision'],
        source_package_sha256=source['sha256'], original_process_execution=process['execution'],
        original_runtime_provenance=process['runtime_provenance'], source_history_preserved=True,
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
    from Scripts.StructTrain.TimeLearner.contained_runner import execute
    from Scripts.StructTrain.TimeLearner.contained_process import inspect
    from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
    from Scripts.StructTrain.TimeLearner.native_cli import inspect_native_cli
    from Scripts.StructTrain.TimeLearner.physical_model_data_evidence import audit_physical_model_data
    from Scripts.StructTrain.TimeLearner.native_pipeline_worker import _artifact_records
    require(os.name == 'posix' and spec['kind'] == 'timelearner_prepared_physical_export' and
            spec['schema_version'] == 1, 'physical_export_worker_scope')
    inputs = Path(spec['inputs']).resolve(strict=True)
    output = Path(spec['output']).absolute()
    base = Path(spec['execution_root']).resolve(strict=True)
    require(base in (Path('/home/user/timelearner-refactor'),Path('/media/user/Data/TimeLearnerRefactor')) and
            output.is_relative_to(base/'readbacks') and inputs.is_relative_to(base/'readbacks') and
            not output.exists(), 'physical_export_paths')
    output.mkdir()
    def inventory():
        require(all(p.is_file() and not p.is_symlink() for p in inputs.iterdir()), 'physical_export_input_alias')
        return {p.name:dict(bytes=p.stat().st_size,sha256=file_record(p)['sha256']) for p in inputs.iterdir()}
    registry = lease = None
    try:
        require(inventory() == spec['input_inventory'] and
                file_record(Path(__file__))['sha256'] == spec['worker_sha256'], 'physical_export_input_changed')
        runtime = json.loads((controls/'runtime.json').read_bytes())
        require(source_closure(Path(spec['sdk_source'])) == runtime['source_closure'], 'physical_export_sdk_changed')
        _write(output/'cli.json', inspect_native_cli(runtime,['physical-model-export'],require_file_source=True))
        disk = spec['disk']
        require(shutil.disk_usage(base).free >= sum(disk.values()), 'physical_export_disk_admission')
        registry = Reservations.open_existing(base/'resource-reservations.sqlite3')
        lease = registry.reserve(spec['job_id'], [dict(path=str(p),access=a) for p,a in
            ((inputs,'read'),(controls,'read'),(Path(spec['sdk_source']),'read'),
             (Path(runtime['executable']['path']).parent,'read'),(output,'write'))],
            ttl_seconds=4200, demands=dict(slots=1,memory_bytes=9*1024**3,disk_bytes=disk['maximum_output_bytes']))
        import time
        from Scripts.StructTrain.TimeLearner.owned_python_job import _allocated_output_bytes
        last=[0.]
        def monitor(state):
            if time.monotonic()-last[0] < 1:return
            last[0]=time.monotonic()
            registry.heartbeat(lease['token'],ttl_seconds=4200)
            require(shutil.disk_usage(base).free >= disk['minimum_free_bytes'], 'physical_export_disk_floor')
            require(_allocated_output_bytes(output) <= disk['maximum_output_bytes'], 'physical_export_output_budget')
        arguments=['--app-ini',runtime['app_ini']['path'],'--timelearner-physical-model-export',
                   str(inputs/'native-job-source.json'),'--timelearner-output',str(output/'native')]
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
                execution['kind']=='timelearner_native_physical_model_export_execution' and
                execution['execution']=='completed' and execution['job_sha256']==spec['resolved_job_sha256'] and
                execution['physical_roundtrip_verified'] and not execution['source_evidence_included'] and
                not execution['training_certificate_transferred'] and not execution['controller_checkpoint_created'],
                'physical_export_native_evidence_changed')
        require(_artifact_records(native,execution)=={'model.json','input-projection.json'},'physical_export_artifacts')
        model=json.loads((native/'model.json').read_bytes())
        projection=json.loads((native/'input-projection.json').read_bytes())
        require(projection['sha256']==sha({k:v for k,v in projection.items() if k!='sha256'}) and
                projection['job_sha256']==spec['resolved_job_sha256'] and
                model['sha256']==execution['model_sha256'] and model['model_revision']==spec['source_model_revision'] and
                model['source_boundary']['sha256']==spec['source_package_sha256'] and
                execution['source_boundary']==projection['source_boundary']==model['source_boundary'],
                'physical_export_boundary_changed')
        audit=audit_physical_model_data(model,frozen=True)
        require(inventory()==spec['input_inventory'] and
                source_closure(Path(spec['sdk_source']))==runtime['source_closure'], 'physical_export_inputs_changed_after')
        _write(output/'terminal.json',dict(native_process_completed=True,physical_roundtrip_verified=True,
            portable_model_audit=audit,model_revision=model['model_revision'],model_sha256=model['sha256'],
            source_package_sha256=spec['source_package_sha256'],source_evidence_included=False,
            training_certificate_transferred=False,original_execution_reclassified=False,scientific_verdict=None))
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
    parser.add_argument('--controls',required=True)
    for name in ('destination','inputs','output','run-id'):parser.add_argument('--'+name)
    args=parser.parse_args()
    if any((args.destination,args.inputs,args.output,args.run_id)):
        if not all((args.destination,args.inputs,args.output,args.run_id)):parser.error('all preparation paths required')
        prepare(args.controls,args.destination,args.inputs,args.output,args.run_id)
    else:run(args.controls)


if __name__=='__main__':main()
