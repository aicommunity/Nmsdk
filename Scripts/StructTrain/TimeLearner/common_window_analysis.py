"""Compare a common native prefix without censoring the full trial verdict.

The public entry point reaudits completed diagnostic runs. Full-window counts
remain authoritative; prefix/tail events and waveform differences are additional
descriptive evidence, never a new training or recognition certificate.
"""
import argparse
import json
from pathlib import Path, PurePosixPath

from .collector_provenance import _frozen, _json
from .native_evidence import equal, number, require
from .native_pipeline_worker import audit_run_manifest


def _tick(time, observation):
    frequency = number(observation['frequency_hz'])
    require(frequency > 0, 'common_window_frequency')
    begin = number(observation['begin'])
    offset = number((number(time)-begin)*frequency)
    tick = round(offset)
    require(tick >= 0 and equal(time, begin+tick/frequency),
            'common_window_event_off_native_grid')
    return tick


def _prefix(observation, seconds):
    require(observation['schema_version'] == 2 and observation['armed'] is True and
            observation['complete'] is True and observation['valid'] is True and
            observation['censored'] is False, 'common_window_incomplete_observation')
    frequency = number(observation['frequency_hz'])
    require(frequency > 0, 'common_window_frequency')
    ticks = round(number(seconds*frequency))
    require(ticks >= 1 and equal(seconds, ticks/frequency), 'common_window_off_native_grid')
    require(number(observation['end']) >= number(observation['begin']) and
            (observation['end'] >= observation['begin']+seconds or
             equal(observation['end'], observation['begin']+seconds)),
            'common_window_not_covered')
    samples = observation['samples']
    require(len(samples) >= ticks+1, 'common_window_missing_prefix_samples')
    waveform = []
    dimension = None
    for index, sample in enumerate(samples[:ticks+1]):
        require(_tick(sample['time'], observation) == index, 'common_window_sample_grid')
        soma = [number(value) for value in sample['soma']]
        require(bool(soma) and (dimension is None or len(soma) == dimension),
                'common_window_soma_dimension')
        dimension = len(soma)
        waveform.append([number(sample[key]) for key in ('lt_potential','lt_output','stimulus')]+soma)
    stimuli = [_tick(time, observation) for time in observation['stimulus_times']]
    spikes = [_tick(time, observation) for time in observation['spike_times']]
    require(observation['spike_count'] == len(spikes), 'common_window_spike_count')
    final_tick = _tick(observation['end'], observation)
    require(all(tick <= final_tick for tick in stimuli+spikes) and
            all(a < b for a,b in zip(stimuli,stimuli[1:])) and
            all(a <= b for a,b in zip(spikes,spikes[1:])), 'common_window_event_order_or_range')
    return dict(ticks=ticks,frequency_hz=frequency,waveform=waveform,soma_channels=dimension,
        stimulus_ticks=stimuli,prefix_spike_ticks=[t for t in spikes if t <= ticks],
        tail_spike_ticks=[t for t in spikes if t > ticks],
        early_spike_ticks=[t for t in spikes if stimuli and t < stimuli[-1]],
        observed_final_tick=final_tick)


def _compare(evaluations, common_seconds):
    seconds = number(common_seconds)
    require(seconds > 0 and 2 <= len(evaluations) <= 4, 'common_window_design')
    base_name = next(iter(evaluations))
    baseline = evaluations[base_name]
    base_metrics = baseline['metrics']
    inventories = {}
    projected = {}
    for name, evaluation in evaluations.items():
        spec, observations, metrics = (evaluation[k] for k in ('spec','observations','metrics'))
        require(metrics['model_revision'] == base_metrics['model_revision'] and
                number(metrics['effective_threshold']) == number(base_metrics['effective_threshold']) and
                spec['source_stopped_sha256'] == baseline['spec']['source_stopped_sha256'],
                'common_window_frozen_model_or_threshold_changed')
        expected = {row['sample_id']: row for row in spec['trials']}
        require(len(expected) == len(spec['trials']), 'common_window_duplicate_sample')
        actual = {row['sample_id']: row for row in observations}
        require(len(actual) == len(observations) and set(actual) == set(expected),
                'common_window_missing_or_duplicate_trial')
        inventory = {sample:(row['label'],row['pattern_hash']) for sample,row in expected.items()}
        require(all(row[0] in ('target','foil') for row in inventory.values()) and
                sum(row[0] == 'target' for row in inventory.values()) == 1 and len(inventory) >= 2,
                'common_window_labels')
        require(not inventories or inventory == inventories[base_name], 'common_window_pattern_set_changed')
        inventories[name] = inventory
        projected[name] = {}
        for sample, observation in actual.items():
            require((observation['label'],observation['pattern_hash']) == inventory[sample] and
                    observation['trial_id'] == expected[sample]['trial_id'] and
                    observation['reset_policy'] == expected[sample]['reset_policy'],
                    'common_window_trial_metadata_changed')
            projected[name][sample] = _prefix(observation,seconds)
    comparisons = []
    for name in evaluations:
        if name == base_name:
            continue
        trials = []
        for sample in sorted(inventories[base_name]):
            left,right = projected[base_name][sample],projected[name][sample]
            require(left['frequency_hz'] == right['frequency_hz'] and
                    left['ticks'] == right['ticks'] and left['soma_channels'] == right['soma_channels'],
                    'common_window_incompatible_native_grid_or_shape')
            differences = [0.]*(3+left['soma_channels'])
            for a,b in zip(left['waveform'],right['waveform']):
                for index,(av,bv) in enumerate(zip(a,b)):
                    differences[index] = max(differences[index],number(abs(av-bv)))
            trials.append(dict(sample_id=sample,label=inventories[base_name][sample][0],
                pattern_hash=inventories[base_name][sample][1],
                compared_samples=left['ticks']+1,frequency_hz=left['frequency_hz'],
                prefix_numeric_samples_equal=all(value == 0 for value in differences),
                maximum_absolute_difference=dict(lt_potential=differences[0],lt_output=differences[1],
                    stimulus=differences[2],soma=differences[3:]),
                stimulus_ticks_equal=left['stimulus_ticks'] == right['stimulus_ticks'],
                prefix_spike_ticks_equal=left['prefix_spike_ticks'] == right['prefix_spike_ticks'],
                baseline={k:v for k,v in left.items() if k != 'waveform'},
                compared={k:v for k,v in right.items() if k != 'waveform'}))
        comparisons.append(dict(baseline=base_name,compared=name,trials=trials))
    return dict(kind='timelearner_common_window_diagnostic_comparison',schema_version=1,
        common_seconds=seconds,common_anchor='native_trial_begin',
        model_revision=base_metrics['model_revision'],threshold=base_metrics['effective_threshold'],
        full_window_counts={name:row['metrics']['pooled_counts'] for name,row in evaluations.items()},
        full_window_counts_preserved=True,comparisons=comparisons,
        prefix_is_secondary_description=True,tail_events_retained=True,
        training_completed=False,independent_evaluation=False,scientific_verdict=None)


def compare_diagnostic_runs(manifests, common_seconds):
    """Reaudit complete real runs, then compare each pattern to the first run."""
    require(type(manifests) is dict and 2 <= len(manifests) <= 4 and
            all(type(name) is str and name for name in manifests), 'common_window_design')
    require(number(common_seconds) > 0, 'common_window_design')
    evaluations = {}
    provenance = {}
    for name,path in manifests.items():
        path = Path(path).resolve(strict=True)
        raw,before = _frozen(path,16*1024**2)
        manifest = _json(raw)
        audit = audit_run_manifest(path)
        require(audit['run_evidence_consistent'] and manifest['operation'] == 'diagnostic-evaluate' and
                manifest['execution'] == 'completed' and manifest['validity'] == 'valid',
                'common_window_requires_audited_completed_diagnostic')
        metrics = manifest['analysis']['metrics']
        require(metrics['validity'] == 'valid' and metrics['diagnostic_only'] is True and
                metrics['training_completed'] is False and metrics['evaluation_verdict'] is None,
                'common_window_diagnostic_role_changed')
        root = path.parent
        records = {row['path']:row for row in manifest['artifacts']}
        def bound(relative):
            parts = PurePosixPath(relative)
            require(not parts.is_absolute() and '..' not in parts.parts and
                    '\\' not in relative and ':' not in relative and relative in records,
                    'common_window_primary_path')
            raw,observed = _frozen(root/relative,16*1024**2)
            require(all(observed[k] == records[relative][k] for k in ('bytes','sha256')),
                    'common_window_primary_changed')
            return _json(raw)
        spec = bound('native/evaluation.json')
        observations = [bound('native/'+row['observation']) for row in spec['trials']]
        _,after = _frozen(path,16*1024**2)
        require(before == after, 'common_window_manifest_changed')
        evaluations[name] = dict(spec=spec,observations=observations,metrics=metrics)
        provenance[name] = dict(manifest=before,runtime_fingerprint=manifest['runtime_fingerprint'],
                               run_evidence_consistent=True)
    return dict(_compare(evaluations,common_seconds),source_runs=provenance)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',action='append',required=True,metavar='NAME=PATH')
    parser.add_argument('--common-seconds',type=float,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args(argv)
    manifests = {}
    for value in args.manifest:
        name,separator,path = value.partition('=')
        require(separator and name and path and name not in manifests,'common_window_manifest_argument')
        manifests[name] = Path(path)
    output = args.output.resolve()
    require(not output.exists() and all(not output.is_relative_to(p.resolve(strict=True).parent)
            for p in manifests.values()), 'common_window_new_external_output_required')
    result = compare_diagnostic_runs(manifests,args.common_seconds)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')


if __name__ == '__main__':
    main()
