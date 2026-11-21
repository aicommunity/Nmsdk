"""Prepare a same-matrix threshold probe from a complete native baseline.

Only one complete source tree is parsed. History and primary files stay intact;
hard links reuse immutable input bytes, not a reduced learned-state format.
Preparation does not claim a native result, calibration or training convergence.
"""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import sys


def prepare(controls, destination, inputs, output, run_id):
    controls = Path(controls).resolve(strict=True)
    previous = json.loads((controls/'specification.json').read_bytes())
    sys.path.insert(0, previous['python_source'])
    sys.dont_write_bytecode = True
    from Scripts.StructTrain.TimeLearner.native_evidence import require
    from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
    from Scripts.StructTrain.TimeLearner.runtime import file_record
    from Scripts.StructTrain.TimeLearner.job_source_transport import make_envelope
    from Scripts.StructTrain.TimeLearner.native_pipeline_worker import _artifact_records

    destination = Path(destination).resolve(strict=True)
    inputs = Path(inputs).absolute()
    output = Path(output).absolute()
    require(not inputs.exists() and not output.exists(), 'threshold_fresh_paths_required')
    baseline = Path(previous['output'])
    terminal = json.loads((baseline/'terminal.json').read_bytes())
    process = json.loads((baseline/'process-result.json').read_bytes())
    require(terminal['native_process_completed'] and process['execution'] == 'completed' and
            process['all_processes_closed'] and process['runtime_provenance'] == 'loaded_files_captured',
            'threshold_baseline_process_incomplete')
    native = baseline/'native'
    execution = json.loads((native/'execution.json').read_bytes())
    require(execution['execution'] == 'completed' and execution['sha256'] ==
            sha({k:v for k,v in execution.items() if k != 'sha256'}), 'threshold_execution_digest')
    _artifact_records(native, execution)  # Full byte/hash closure, including the large models/job.
    design = json.loads((native/'evaluation.json').read_bytes())
    require(design['criterion'] == dict(id='post_anchor_target_whole_window_foil_v1', anchor='onset',
        begin_offset=0., end_offset=None, reject_target_outside_window=True) and
        len(design['trials']) == 8 and design['model_revision'] == previous['source_model_revision'],
        'threshold_whole_pattern_baseline_required')
    rows = []
    for trial in design['trials']:
        value = json.loads((native/trial['observation']).read_bytes())
        require(value['schema_version'] == 2 and value['complete'] and value['valid'] and
            not value['censored'] and value['spike_count'] == 0 and value['spike_times'] == [] and
            value['reset_policy'] == 'reset_per_trial' and value['model_before'] == value['model_after'] ==
            design['model_revision'] and all(value[k] == trial[k] for k in
                ('trial_id','sample_id','label','pattern_hash')), 'threshold_baseline_observation')
        potentials = [s['lt_potential'] for s in value['samples']]
        require(potentials and all(type(v) in (int,float) and math.isfinite(v) for v in potentials),
                'threshold_nonfinite_potential')
        rows.append(dict(trial_id=trial['trial_id'], sample_id=trial['sample_id'], label=trial['label'],
                         lt_maximum=max(potentials)))
    targets = [r['lt_maximum'] for r in rows if r['label'] == 'target']
    foils = [r['lt_maximum'] for r in rows if r['label'] == 'foil']
    require(len({r['trial_id'] for r in rows}) == 8 and len(targets) == 1 and len(foils) == 7,
            'threshold_baseline_labels')
    below = [v for v in foils if v < targets[0]]
    require(below, 'threshold_no_target_preserving_gap')
    lower, upper = max(below), targets[0]
    threshold = lower+(upper-lower)/2
    require(lower < threshold < upper, 'threshold_midpoint_unresolvable')

    module_spec = importlib.util.spec_from_file_location('prepared_inventory', controls/'worker.py')
    worker = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(worker)
    old_inputs = Path(previous['inputs']).resolve(strict=True)
    require(worker.inventory(old_inputs, file_record) == previous['input_inventory'], 'threshold_old_input_changed')
    envelope = json.loads((old_inputs/'native-job-source.json').read_bytes())
    require(envelope['sha256'] == sha({k:v for k,v in envelope.items() if k != 'sha256'}) and
            envelope['job']['schema_version'] == 1 and envelope['job']['sha256'] == previous['resolved_job_sha256']
            and envelope['source']['field'] == 'source_stopped', 'threshold_source_envelope')
    source = old_inputs/envelope['source']['path']
    source_before = file_record(source)
    package = json.loads(source.read_bytes())
    require(source_before['sha256'] == envelope['source']['sha256'] and
            source_before['size'] == envelope['source']['bytes'] and
            package['sha256'] == envelope['source']['package_sha256'] == previous['source_package_sha256'],
            'threshold_complete_source_binding')
    original = {**envelope['job'], 'source_stopped':package}
    require(sha({k:v for k,v in original.items() if k != 'sha256'}) == previous['resolved_job_sha256'],
            'threshold_original_resolved_job_digest')
    job = {k:v for k,v in original.items() if k != 'sha256'}
    job.update(schema_version=2, diagnostic_threshold=threshold, run_id=run_id,
               trials=[{**t, 'run_id':run_id} for t in original['trials']])
    job['sha256'] = sha(job)

    inputs.mkdir(parents=True)
    # Reuse the complete source namespace. Every name and byte remains checked;
    # the unrelated full resolved job is not copied into the new input tree.
    source_root = Path(envelope['source']['path']).parts[0]
    for relative in previous['input_inventory']:
        if Path(relative).parts[0] != source_root:
            continue
        target = inputs/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(old_inputs/relative, target)
    new_envelope = make_envelope(job, inputs/envelope['source']['path'], inputs)

    def write(path, value):
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')

    write(inputs/'native-job-source.json', new_envelope)
    (destination/'worker.py').write_bytes((controls/'worker.py').read_bytes())
    (destination/'runtime.json').write_bytes((controls/'runtime.json').read_bytes())
    spec = {**previous, 'job_id':output.name, 'output':str(output), 'inputs':str(inputs),
            'input_inventory':worker.inventory(inputs, file_record), 'resolved_job_sha256':job['sha256'],
            'scope':'Same-matrix threshold confirmation on the actual stopped model; not independent Test or completed Train.'}
    write(destination/'specification.json', spec)
    proposal = dict(kind='prepared_same_matrix_threshold_proposal', schema_version=1, baseline=str(baseline),
        baseline_execution_sha256=execution['sha256'], source_model_revision=previous['source_model_revision'],
        source_package_sha256=package['sha256'], rows=rows, threshold=threshold,
        full_matrix_peak_margin=upper-max(foils),
        nonspiking_proxy=dict(TP=1,FN=0,FP=sum(v>=threshold for v in foils),TN=sum(v<threshold for v in foils)),
        rule='midpoint_of_target_maximum_and_highest_strictly_lower_foil_maximum',
        baseline_all_artifact_bytes_verified=True, original_resolved_job_digest_verified=True,
        source_inventory_unchanged=worker.inventory(old_inputs,file_record)==previous['input_inventory'],
        protocol='historical_same_matrix', actual_threshold_confirmation_required=True,
        complete_source_history_preserved=True, training_completed=False, scientific_verdict=None)
    require(proposal['source_inventory_unchanged'] and file_record(source) == source_before,
            'threshold_source_changed_during_preparation')
    write(destination/'proposal.json', proposal)
    return proposal


def main():
    parser = argparse.ArgumentParser()
    for name in ('controls','destination','inputs','output','run-id'):
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args()
    result = prepare(args.controls, args.destination, args.inputs, args.output, args.run_id)
    print(json.dumps(result, allow_nan=False))


if __name__ == '__main__':
    main()
