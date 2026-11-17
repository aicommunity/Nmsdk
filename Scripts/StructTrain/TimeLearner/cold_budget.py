"""Explicit cold single-sweep declarations; no model execution or physics edits.

Counts follow BoundedTrainingSession and FinalVerificationSession. Valid native
observations are an assumption of this estimate, never a claim of convergence.
"""
from copy import deepcopy
import math

from .composite_configuration import project_training_configuration
from .model_identity import canonical_model_sha256
from .native_evidence import number, require
from .native_pipeline_worker import validate_job


def coverage(job):
    validate_job('train', job)
    raw=job['configuration'];view=project_training_configuration(raw)
    search=view['search'];n=len(view['model']['inputs']);adjustable=max(0,n-1)
    repeats=search.get('n0_candidate_repeats',1)
    # A candidate uses a fresh anchor/input pair for every required repetition.
    # At local exhaustion, the current implementation also probes restored best.
    candidates=2*repeats*adjustable*search['maximum_candidates_per_input']
    restoration=2*repeats*adjustable
    # FinalVerificationSession collects every input once, including its anchor;
    # it does not request a separate anchor for each final input.
    final=n;per_sweep=candidates+restoration+final
    composite=raw.get('schema_version') in (6,7,8)
    waves=n+2 if composite else 1
    groups=n+per_sweep
    secondary={}
    if composite:
        limits=raw['composite_measurement']['attempt_limits']
        secondary=dict(required_groups=groups,required_native_probes=groups*waves,
            required_maximum_samples=groups*waves*raw['maximum_samples'],
            groups_fit=limits['maximum_groups']>=groups,
            native_probes_fit=limits['maximum_native_probes']>=groups*waves,
            samples_fit=limits['maximum_total_samples']>=groups*waves*raw['maximum_samples'])
    return dict(kind='timelearner_declared_sweep_budget_coverage',schema_version=1,
        inputs=n,adjustable_inputs=adjustable,candidate_repetitions=repeats,
        candidate_pair_probes=candidates,best_restoration_probes=restoration,
        final_all_input_probes=final,valid_search_probe_upper_bound_per_sweep=per_sweep,
        valid_search_probe_upper_bound_all_declared_sweeps=per_sweep*search['maximum_sweeps'],
        declared_search_probes=search['maximum_probes'],
        first_sweep_fits=search['maximum_probes']>=per_sweep,
        all_declared_sweeps_fit=search['maximum_probes']>=per_sweep*search['maximum_sweeps'],
        reference_capture_probes_separate=True,native_probes_per_valid_group=waves,
        composite_capacity=secondary,
        declared_window_model_seconds=groups*waves*raw['duration'],
        assumptions=['valid complete measurements; no recovery/retry allowance included',
            'legal edits; no additional wall/model-time overhead inferred',
            'local candidate exhaustion may occur earlier than the configured cap'],
        execution_verified=False,convergence_verified=False,scientific_verdict=None)


def prepare_single_sweep(job, *, run_id, candidates_per_input, maximum_probes,
                         maximum_model_seconds):
    """Keep physical/measurement declarations intact; re-sign explicit budgets.

    This mandatory C-trim-Off control retains every storage profile, numerical
    tolerance, window, source amplitude and topology. It cannot resume a state.
    Secondary native limits must already fund the declared valid sweep; they
    are never silently enlarged or treated as a runtime guarantee.
    """
    validate_job('train',job)
    require(type(run_id) is str and bool(run_id) and
            all(type(v) is int and v>0 for v in (candidates_per_input,maximum_probes)),
            'single_sweep_explicit_budget')
    seconds=number(maximum_model_seconds);require(seconds>0,'single_sweep_model_seconds')
    require(job['configuration'].get('schema_version') in (6,7,8),
            'single_sweep_requires_declared_composite_cold_job')
    require(job['optional_modes']==dict(sync_capacitance_trim=0,post_train_tuning=False,
                                       auto_calibrate_threshold=False),
            'single_sweep_control_requires_optional_modes_off')
    changed=deepcopy(job);config=changed['configuration'];config['run_id']=run_id
    config['search'].update(maximum_candidates_per_input=candidates_per_input,
        maximum_probes=maximum_probes,maximum_sweeps=1)
    config['maximum_model_seconds']=seconds
    ticks=number(seconds*number(config['model']['frequency_hz']))
    require(0<ticks<=2**53-1,'single_sweep_model_tick_bound')
    changed['maximum_model_ticks']=math.ceil(ticks)
    changed.pop('sha256');changed['sha256']=canonical_model_sha256(changed)
    report=coverage(changed)
    require(report['first_sweep_fits'],'single_sweep_search_budget_underfunded')
    require(all(report['composite_capacity'][key] for key in
                ('groups_fit','native_probes_fit','samples_fit')),
            'single_sweep_native_capacity_underfunded')
    require(seconds>=report['declared_window_model_seconds'],
            'single_sweep_model_windows_underfunded')
    return changed,report


def main(argv=None):
    import argparse
    import json
    from pathlib import Path
    from .collector_provenance import _frozen
    from .native_evidence import parse_json_bytes
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template',required=True,type=Path)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--candidates-per-input',required=True,type=int)
    parser.add_argument('--maximum-probes',required=True,type=int)
    parser.add_argument('--model-seconds',required=True,type=float)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(argv)
    raw,record=_frozen(args.template.resolve(strict=True),64*1024**2)
    original=parse_json_bytes(raw)
    prepared,report=prepare_single_sweep(original,run_id=args.run_id,
        candidates_per_input=args.candidates_per_input,maximum_probes=args.maximum_probes,
        maximum_model_seconds=args.model_seconds)
    output=args.output.resolve();require(not output.exists(),'single_sweep_output_exists')
    output.mkdir(parents=True,exist_ok=False)
    declaration=dict(kind='timelearner_single_sweep_cold_declaration',schema_version=1,
        template=record,template_job_sha256=original['sha256'],job_sha256=prepared['sha256'],
        changed_fields=['configuration.run_id','configuration.search.maximum_candidates_per_input',
            'configuration.search.maximum_probes','configuration.search.maximum_sweeps',
            'configuration.maximum_model_seconds','maximum_model_ticks'],
        physical_model_and_tolerances_unchanged=True,cold=True,started=False,
        budget_coverage=report,scientific_verdict=None)
    for name,value in (('job.json',prepared),('declaration.json',declaration)):
        with (output/name).open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps(dict(output=str(output),job_sha256=prepared['sha256'],started=False)))


if __name__=='__main__':main()
