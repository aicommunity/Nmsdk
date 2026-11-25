"""Declare an M=4 third-pulse diagnostic on an unchanged physical model.

The first, second and last input times stay fixed. The original target is a
repeated control. This diagnostic is not an independently held-out class.
"""
from copy import deepcopy
import math

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import equal, number, require


PROTOCOL = 'fixed_first_second_last_varied_third_v1'
THIRD_TICKS = (240, 320, 400, 480, 560, 640, 720, 800)


def declare_job(original, run_id):
    from .native_pipeline_worker import validate_job
    require(type(run_id) is str and bool(run_id), 'third_pulse_run_identity')
    model = original['source_model_data']; originals = original['trials']
    require(len(originals) == 8 and len({t['pattern_hash'] for t in originals}) == 8 and
            len({t['sample_id'] for t in originals}) == 8 and
            all(t['label'] in ('target', 'foil') and t['pattern_hash'] == sha(t['pattern_isi'])
                for t in originals), 'third_pulse_original_matrix')
    targets = [t for t in originals if t['label'] == 'target']
    require(len(targets) == 1, 'third_pulse_unique_target')
    target = targets[0]; frequency = number(model['configuration']['model']['frequency_hz'])
    require(frequency == 2000 and target['pattern_isi'] == [.01, .08, .16, .24] ==
            model['configuration']['model']['initial_isi'] and
            target['reset_policy'] == 'reset_per_trial' and target['record_threshold_potential'] is True and
            equal(number(target['duration']), 2.), 'third_pulse_requires_declared_M4_clock_and_window')
    job = deepcopy(original); job.pop('sha256'); job['run_id'] = run_id; job['trials'] = []
    for tick in THIRD_TICKS:
        control = tick == 480
        pattern = list(target['pattern_isi']) if control else [.01, .08, (tick-160)/2000, (960-tick)/2000]
        sample = target['sample_id'] if control else 'third-pulse-tick-'+str(tick)
        require(control or sample not in {t['sample_id'] for t in originals}, 'third_pulse_sample_collision')
        job['trials'].append(dict(deepcopy(target), run_id=run_id, trial_id=run_id+'/tick-'+str(tick),
            sample_id=sample, label='target' if control else 'foil', pattern_isi=pattern, pattern_hash=sha(pattern)))
    job['maximum_model_ticks'] = sum(math.ceil(t['duration']*frequency)+4 for t in job['trials'])
    job['sha256'] = sha(job)
    validate_job('physical-model-evaluate', job, (model,))
    design = dict(protocol_id=PROTOCOL, pulse_count=4, first_input_delay_ticks=20,
        second_from_first_ticks=160, last_from_first_ticks=960, third_from_first_ticks=list(THIRD_TICKS),
        target_third_from_first_ticks=480, observation_ticks=4000, reset_policy='reset_per_trial',
        target_position=THIRD_TICKS.index(480), target_control_trials=1, new_foil_trials=7,
        label_rule='exact_original_target_hash_is_target; all_other_declared_patterns_are_foil',
        selection_scope='posthoc_mechanism_diagnostic; not_independent_holdout',
        training_performed=False, calibration_performed=False, scientific_verdict=None)
    return job, design
