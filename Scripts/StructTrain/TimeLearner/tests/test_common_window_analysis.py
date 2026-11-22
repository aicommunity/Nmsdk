"""Secondary prefix analysis must never hide late full-window false responses."""
from copy import deepcopy
import unittest

from ..common_window_analysis import _compare
from ..native_evidence import EvidenceError


def evaluation(duration=2, begin=0, frequency=2, soma_channels=1):
    observations = []
    trials = []
    for sample,label in [('target','target'),('foil','foil')]:
        trial_id = 'trial-'+sample
        trials.append(dict(sample_id=sample,label=label,pattern_hash=sample+'-hash',
                           trial_id=trial_id,reset_policy='reset_per_trial'))
        observations.append(dict(schema_version=2,armed=True,complete=True,valid=True,censored=False,
            frequency_hz=frequency,begin=begin,end=begin+duration,
            sample_id=sample,label=label,pattern_hash=sample+'-hash',trial_id=trial_id,
            reset_policy='reset_per_trial',spike_count=1 if label=='target' else 0,
            spike_times=[begin+.5] if label=='target' else [],
            stimulus_times=[begin+.5,begin+1.],
            samples=[dict(time=begin+i/frequency,lt_potential=0.,lt_output=0.,stimulus=0.,
                          soma=[float(i)]*soma_channels) for i in range(int(duration*frequency)+1)]))
    return dict(spec=dict(source_stopped_sha256='fixed-source',trials=trials),observations=observations,
        metrics=dict(model_revision='fixed-model',effective_threshold=.1,
                     pooled_counts=dict(TP=1,FP=0,FN=0,TN=1)))


class CommonWindowAnalysisTest(unittest.TestCase):
    def test_late_false_positive_retains_original_full_window_counts(self):
        baseline = evaluation()
        longer = evaluation(4)
        longer['observations'][1].update(spike_count=1,spike_times=[2.5])
        longer['metrics']['pooled_counts']=dict(TP=1,FP=1,FN=0,TN=0)
        result = _compare(dict(baseline=baseline,longer=longer),2.)
        self.assertEqual(result['full_window_counts']['longer']['FP'],1)
        self.assertIsNone(result['scientific_verdict'])
        self.assertNotIn('prefix_counts',result)
        foil = next(row for row in result['comparisons'][0]['trials'] if row['label']=='foil')
        self.assertTrue(foil['prefix_numeric_samples_equal'])
        self.assertEqual(foil['compared']['prefix_spike_ticks'],[])
        self.assertEqual(foil['compared']['tail_spike_ticks'],[5])

    def test_absolute_clock_and_row_permutation_do_not_change_prefix_alignment(self):
        longer = evaluation(4,begin=100.)
        longer['observations'].reverse();longer['spec']['trials'].reverse()
        result = _compare(dict(baseline=evaluation(),longer=longer),2.)
        self.assertTrue(all(row['prefix_numeric_samples_equal'] and row['prefix_spike_ticks_equal'] and
                            row['stimulus_ticks_equal'] for row in result['comparisons'][0]['trials']))
        target = next(row for row in result['comparisons'][0]['trials'] if row['label']=='target')
        self.assertEqual(target['compared']['early_spike_ticks'],[1])

    def test_changes_on_seventh_soma_are_not_discarded(self):
        left = evaluation(soma_channels=7);right = evaluation(4,soma_channels=7)
        right['observations'][0]['samples'][2]['soma'][6] += .25
        result = _compare(dict(left=left,right=right),2.)
        target = next(row for row in result['comparisons'][0]['trials'] if row['label']=='target')
        self.assertFalse(target['prefix_numeric_samples_equal'])
        self.assertEqual(target['maximum_absolute_difference']['soma'],[0.]*6+[.25])

    def test_censored_or_short_record_cannot_be_a_common_window(self):
        for change,reason in [(dict(censored=True),'incomplete_observation'),
                              (dict(complete=False),'incomplete_observation'),
                              (dict(end=1.),'not_covered')]:
            other=evaluation(4);other['observations'][0].update(change)
            with self.subTest(change=change),self.assertRaisesRegex(EvidenceError,reason):
                _compare(dict(base=evaluation(),other=other),2.)

    def test_frozen_model_threshold_and_source_must_match(self):
        for field in ('model_revision','effective_threshold','source_stopped_sha256'):
            other=evaluation(4)
            if field=='source_stopped_sha256':other['spec'][field]='different'
            elif field=='model_revision':other['metrics'][field]='different'
            else:other['metrics'][field]=.2
            with self.subTest(field=field),self.assertRaisesRegex(EvidenceError,'frozen_model_or_threshold'):
                _compare(dict(base=evaluation(),other=other),2.)

    def test_missing_duplicate_and_changed_pattern_are_refused(self):
        for change in ('missing','duplicate','hash'):
            other=evaluation(4)
            if change=='missing':other['observations'].pop()
            elif change=='duplicate':other['observations'].append(deepcopy(other['observations'][0]))
            else:other['spec']['trials'][0]['pattern_hash']='foreign-pattern'
            with self.subTest(change=change),self.assertRaises(EvidenceError):
                _compare(dict(base=evaluation(),other=other),2.)

    def test_nonfinite_channel_and_inconsistent_event_count_are_refused(self):
        for change in ('NaN','count','off-grid','sample-gap'):
            other=evaluation(4)
            if change=='NaN':other['observations'][0]['samples'][1]['lt_potential']=float('nan')
            elif change=='count':other['observations'][0]['spike_count']=7
            elif change=='off-grid':other['observations'][0]['spike_times']=[.75]
            else:other['observations'][0]['samples'].pop(1)
            with self.subTest(change=change),self.assertRaises(EvidenceError):
                _compare(dict(base=evaluation(),other=other),2.)

    def test_other_native_grid_or_channel_shape_is_refused(self):
        for other in (evaluation(4,frequency=4),evaluation(4,soma_channels=2)):
            with self.assertRaisesRegex(EvidenceError,'incompatible_native_grid_or_shape'):
                _compare(dict(base=evaluation(),other=other),2.)

    def test_fractional_tick_nonfinite_and_bool_window_are_refused(self):
        for seconds in (.75,0.,float('nan'),True):
            with self.subTest(seconds=seconds),self.assertRaises(EvidenceError):
                _compare(dict(base=evaluation(),other=evaluation(4)),seconds)
