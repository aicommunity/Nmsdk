"""Report-channel contracts: absent legacy data and corrupt native scalars."""
from pathlib import Path
import tempfile
import unittest

from ..lt_decision_reports import render_lt_decisions
from ..native_evidence import EvidenceError


class LTDecisionReportContractTest(unittest.TestCase):
    def spec(self):
        return dict(model_revision='f'*64,
                    trials=[dict(trial_id='target-by-id', presentation_index=0)])

    def test_legacy_soma_is_not_substituted_for_unrecorded_lt(self):
        observation = dict(trial_id='target-by-id', schema_version=1,
                           samples=[dict(soma=[99., 98., 97., 96., 95.])])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = render_lt_decisions(self.spec(), [observation], None, output)
            self.assertFalse(result['all_declared_trials_rendered'])
            self.assertEqual(result['trials'], [])
            self.assertEqual(result['unavailable_trials'], [dict(
                trial_id='target-by-id', reason='legacy_lt_channel_not_recorded')])
            self.assertEqual(list(output.iterdir()), [])
            self.assertIsNone(result['scientific_verdict'])

    def test_corrupt_native_lt_is_refused_before_any_figure(self):
        for sample in (dict(soma=[1.]), dict(soma=[1.], lt_potential=float('nan')),
                       dict(soma=[1.], lt_potential=float('inf'))):
            observation = dict(trial_id='target-by-id', schema_version=2,
                threshold_potential_source=dict(path='$.LTZone.Potential'), samples=[sample])
            with self.subTest(sample=sample), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with self.assertRaises(EvidenceError):
                    render_lt_decisions(self.spec(), [observation], 100., output)
                self.assertEqual(list(output.iterdir()), [])

    def test_duplicate_ids_do_not_create_duplicate_or_relabelled_panels(self):
        observation = dict(trial_id='target-by-id', schema_version=1, samples=[dict(soma=[1.])])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with self.assertRaisesRegex(EvidenceError, 'lt_plot_duplicate_observation'):
                render_lt_decisions(self.spec(), [observation, observation], None, output)
            self.assertEqual(list(output.iterdir()), [])
