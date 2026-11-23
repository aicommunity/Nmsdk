"""Predeclare new M=4 negative patterns with the target's total duration.

The realized integer-tick patterns are signed before evaluation. Selection
uses no waveform, score, learned parameter or threshold. A repeated original
target is a control, not an independently held-out positive class.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import equal, load, number, require

PROTOCOL = 'frozen_M4_matched_duration_negative_holdout_v1'
KIND = 'timelearner_frozen_duration_holdout_protocol'
SAMPLER = 'sha256_counter_pair_rejection_v1'
FIELDS = {'kind', 'schema_version', 'protocol_id', 'sampler', 'sampling_seed',
          'draw_limit', 'draws_used', 'frequency_hz', 'pulse_count', 'target_pattern_hash',
          'onset_ticks', 'total_interval_ticks', 'interval_tick_bounds',
          'excluded_pattern_hashes', 'foil_interval_ticks', 'target_position', 'sha256'}


def _integer(value, minimum, maximum, reason):
    require(type(value) is int and minimum <= value <= maximum, reason)
    return value


def _source(original):
    require(type(original) is dict, 'duration_holdout_source')
    rows = original['trials']; model = original['source_model_data']['configuration']['model']
    require(type(rows) is list and len(rows) == 8 and
            all(t['label'] in ('target', 'foil') and t['pattern_hash'] == sha(t['pattern_isi']) for t in rows) and
            len({t['pattern_hash'] for t in rows}) == 8, 'duration_holdout_source_matrix')
    targets = [t for t in rows if t['label'] == 'target']
    require(len(targets) == 1, 'duration_holdout_source_target')
    target = targets[0]; pattern = target['pattern_isi']; frequency = number(model['frequency_hz'])
    require(len(pattern) == 4 and pattern == model['initial_isi'] and frequency > 0 and
            frequency.is_integer() and all(number(v) > 0 for v in pattern), 'duration_holdout_requires_M4_native_target')
    ticks = [round(number(v)*frequency) for v in pattern]
    require(all(n > 0 and equal(v*frequency, n) for v, n in zip(pattern, ticks)) and
            target['reset_policy'] == 'reset_per_trial' and target['record_threshold_potential'] is True,
            'duration_holdout_source_clock_or_reset')
    excluded = {t['pattern_hash'] for t in rows}
    # This older grid is not a new holdout: it was already examined on the
    # working models. Odd native ticks cannot have had that half-tick grid.
    if all(n % 2 == 0 for n in ticks[1:]):
        from .frozen_physical_foil_study import declare_trials
        previous, _ = declare_trials(original, 'duration-holdout/excluded-old-grid')
        excluded.update(t['pattern_hash'] for t in previous)
    require(sum(pattern) < number(target['duration']), 'duration_holdout_source_window')
    return target, int(frequency), ticks, sorted(excluded)


def _sample(target, frequency, total, lower, upper, excluded, seed, count, limit):
    width = upper-lower+1; maximum = 1 << 64; ceiling = maximum-maximum % width
    rows, used = [], set()
    for draw in range(limit):
        raw = hashlib.sha256((PROTOCOL+'/'+str(seed)+'/'+str(draw)).encode('ascii')).digest()
        first, second = int.from_bytes(raw[:8], 'big'), int.from_bytes(raw[8:16], 'big')
        if first >= ceiling or second >= ceiling:
            continue
        a, b = lower+first % width, lower+second % width
        candidate = (a, b, total-a-b)
        if not lower <= candidate[2] <= upper or candidate in used:
            continue
        pattern = [target['pattern_isi'][0]]+[n/frequency for n in candidate]
        if sha(pattern) in excluded:
            continue
        rows.append(list(candidate)); used.add(candidate)
        if len(rows) == count:
            return rows, draw+1
    require(False, 'duration_holdout_candidate_budget_exhausted')


def make_protocol(original, *, seed, foil_count=7, target_position=5,
                  minimum_interval_ticks=60, maximum_interval_ticks=600, draw_limit=10000):
    target, frequency, ticks, excluded = _source(original)
    _integer(seed, 0, 2**63-1, 'duration_holdout_seed')
    _integer(foil_count, 1, 256, 'duration_holdout_foil_count')
    _integer(target_position, 0, foil_count, 'duration_holdout_target_position')
    _integer(draw_limit, 1, 100000, 'duration_holdout_draw_limit')
    _integer(minimum_interval_ticks, 1, 2**31-1, 'duration_holdout_interval_bounds')
    _integer(maximum_interval_ticks, minimum_interval_ticks, 2**31-1, 'duration_holdout_interval_bounds')
    total = sum(ticks[1:])
    require(3*minimum_interval_ticks <= total <= 3*maximum_interval_ticks,
            'duration_holdout_interval_bounds')
    rows, draws = _sample(target, frequency, total, minimum_interval_ticks,
                         maximum_interval_ticks, set(excluded), seed, foil_count, draw_limit)
    result = dict(kind=KIND, schema_version=1, protocol_id=PROTOCOL, sampler=SAMPLER,
        sampling_seed=seed, draw_limit=draw_limit, draws_used=draws, frequency_hz=frequency,
        pulse_count=4, target_pattern_hash=target['pattern_hash'], onset_ticks=ticks[0],
        total_interval_ticks=total, interval_tick_bounds=[minimum_interval_ticks, maximum_interval_ticks],
        excluded_pattern_hashes=excluded, foil_interval_ticks=rows, target_position=target_position)
    return dict(result, sha256=sha(result))


def validate_protocol(protocol, original):
    require(type(protocol) is dict and set(protocol) == FIELDS and protocol['kind'] == KIND and
            type(protocol['schema_version']) is int and protocol['schema_version'] == 1 and
            protocol['protocol_id'] == PROTOCOL and protocol['sampler'] == SAMPLER,
            'duration_holdout_protocol_schema')
    require(all(type(protocol[k]) is int for k in ('sampling_seed', 'draw_limit', 'draws_used',
                'frequency_hz', 'pulse_count', 'onset_ticks', 'total_interval_ticks', 'target_position')) and
            type(protocol['excluded_pattern_hashes']) is list and
            all(type(v) is str for v in protocol['excluded_pattern_hashes']),
            'duration_holdout_protocol_numeric_types')
    bounds = protocol['interval_tick_bounds']; rows = protocol['foil_interval_ticks']
    require(type(bounds) is list and len(bounds) == 2 and type(rows) is list and 1 <= len(rows) <= 256 and
            all(type(row) is list and len(row) == 3 and all(type(n) is int for n in row) for row in rows),
            'duration_holdout_protocol_ticks')
    expected = make_protocol(original, seed=protocol['sampling_seed'], foil_count=len(rows),
        target_position=protocol['target_position'], minimum_interval_ticks=bounds[0],
        maximum_interval_ticks=bounds[1], draw_limit=protocol['draw_limit'])
    require(protocol == expected, 'duration_holdout_protocol_changed_or_wrong_source')
    return protocol


def declare_trials(original, run_id, protocol):
    require(type(run_id) is str and bool(run_id), 'duration_holdout_run_identity')
    validate_protocol(protocol, original)
    target, frequency, _, _ = _source(original); trials = []
    for ticks in protocol['foil_interval_ticks']:
        pattern = [target['pattern_isi'][0]]+[n/frequency for n in ticks]
        sample = 'heldout-M4-ticks-'+'-'.join(map(str, ticks))
        trials.append(dict(deepcopy(target), run_id=run_id, trial_id=run_id+'/'+sample,
            sample_id=sample, label='foil', pattern_isi=pattern, pattern_hash=sha(pattern)))
    control = dict(deepcopy(target), run_id=run_id, trial_id=run_id+'/repeated-target')
    trials.insert(protocol['target_position'], control)
    require(len({t['sample_id'] for t in trials}) == len(trials) and
            len({t['pattern_hash'] for t in trials}) == len(trials), 'duration_holdout_duplicate_trial')
    design = dict(protocol_id=PROTOCOL, protocol_sha256=protocol['sha256'],
        pulses_per_pattern=4, native_frequency_hz=frequency,
        fixed_onset_isi=target['pattern_isi'][0], matched_total_interval_ticks=protocol['total_interval_ticks'],
        declared_foil_ticks=protocol['foil_interval_ticks'],
        excluded_calibration_and_previous_grid_hashes=protocol['excluded_pattern_hashes'],
        sampling=dict(algorithm=SAMPLER, seed=protocol['sampling_seed'], draws_used=protocol['draws_used']),
        target_position=protocol['target_position'], new_foil_trials=len(trials)-1, target_control_trials=1,
        label_rule='exact_original_target_hash_is_target; all_predeclared_new_hashes_are_foil',
        independence_scope='negative_patterns_only; original_positive_is_repeated_control',
        interpretation='fixed_duration_temporal_selectivity; no_new_positive_class_or_stochastic_replicates')
    return trials, design


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-job', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args(argv)
    protocol = make_protocol(load(args.source_job), seed=args.seed)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(protocol, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
