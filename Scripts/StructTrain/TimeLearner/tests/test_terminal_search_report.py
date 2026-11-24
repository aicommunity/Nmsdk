"""A restored earlier graph must not inherit the last search geometry or epoch."""
from copy import deepcopy
import unittest

from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from ..terminal_search_report import project_terminal_search_summary
from .test_training_search_report import fixture


def terminal_fixture():
    history, model = fixture()
    history['model_epoch'] = 33
    history['actual_parameters'][0]['length'] = 202
    history['final_group_ids'] = ['historical-final/0', 'historical-final/1']
    actual = deepcopy(history['actual_parameters']); actual[0]['length'] = 200
    row = history['candidates'][0]
    row.update(model_revision='c'*64, model_epoch=32, full_parameters=deepcopy(actual),
               parameters=deepcopy(actual[0]))
    event = dict(kind='timelearner_native_terminal_selection_event', schema_version=2,
        stopped_outcome='budget_exhausted', stopped_reason='wall', session_attempt=1,
        portable_export_supported=True, fresh_all_input_verification=False, certificate=None,
        search_terminal_epoch=33, search_terminal_revision=history['actual_model_revision'],
        search_terminal_parameters=deepcopy(history['actual_parameters']), selected=None,
        edit_budget={}, selected_probe_packets=[], status='restored', reason='', native_transactions=1,
        wall_seconds=1., actual_model_epoch=34, historical_measurements_rebound_to_actual_epoch=False,
        actual_model_revision='c'*64, actual_parameters=deepcopy(actual))
    event['sha256'] = digest(event)
    summary = dict(kind='native_training_state_summary', schema_version=9, state='finished',
        outcome='budget_exhausted', reason='wall', actual_model_revision='c'*64, model_epoch=34,
        transcript_model_epoch=33, parameters=actual, session_attempt=1, certificate=None,
        terminal_policy=dict(schema_version=1, maximum_wall_seconds=30.), terminal_event=event,
        terminal_journal=[deepcopy(event)], closed_boundary=True, controller_checkpoint=False,
        restored_live_authority=False, historical_summary=history)
    summary['sha256'] = digest(summary)
    return summary, model


def resign(summary):
    event = summary['terminal_event']
    event['sha256'] = digest({k:v for k,v in event.items() if k != 'sha256'})
    summary['terminal_journal'][-1] = deepcopy(event)
    summary['sha256'] = digest({k:v for k,v in summary.items() if k != 'sha256'})


class TerminalSearchReportTest(unittest.TestCase):
    def test_restored_parameters_and_transcript_parameters_remain_distinct(self):
        summary, model = terminal_fixture(); before = deepcopy(summary)
        report = project_terminal_search_summary(summary, model)
        self.assertEqual(report['actual_parameters'][0]['length'], 200)
        self.assertEqual(report['historical_search']['actual_parameters'][0]['length'], 202)
        self.assertEqual(summary, before)

    def test_semantic_match_from_earlier_epoch_is_not_rebound(self):
        summary, model = terminal_fixture(); report = project_terminal_search_summary(summary, model)
        self.assertEqual(len(report['historical_candidates_matching_actual_physics']), 1)
        self.assertEqual(report['matching_candidate_trial_ids_at_actual_epoch'], [])
        self.assertFalse(report['historical_measurements_rebound_to_actual_epoch'])
        self.assertIsNone(report['training_or_final_verification_verdict'])

    def test_false_fresh_flag_does_not_erase_historical_final_measurements(self):
        summary, model = terminal_fixture(); report = project_terminal_search_summary(summary, model)
        self.assertFalse(report['producer_reported_fresh_all_input_verification'])
        self.assertEqual(report['historical_final_verification_group_ids'],
                         ['historical-final/0', 'historical-final/1'])

    def test_changed_summary_digest_is_rejected(self):
        summary, model = terminal_fixture(); summary['parameters'][0]['length'] = 201
        with self.assertRaises(EvidenceError): project_terminal_search_summary(summary, model)

    def test_resigned_wrong_actual_parameters_are_rejected(self):
        summary, model = terminal_fixture(); summary['terminal_event']['actual_parameters'][0]['length'] = 201
        resign(summary)
        with self.assertRaises(EvidenceError): project_terminal_search_summary(summary, model)

    def test_resigned_wrong_transcript_epoch_is_rejected(self):
        summary, model = terminal_fixture(); summary['terminal_event']['search_terminal_epoch'] = 32
        resign(summary)
        with self.assertRaises(EvidenceError): project_terminal_search_summary(summary, model)

    def test_missing_current_event_in_journal_is_rejected(self):
        summary, model = terminal_fixture(); summary['terminal_journal'] = []
        summary['sha256'] = digest({k:v for k,v in summary.items() if k != 'sha256'})
        with self.assertRaises(EvidenceError): project_terminal_search_summary(summary, model)

    def test_resigned_fresh_certificate_claim_is_rejected(self):
        summary, model = terminal_fixture(); summary['terminal_event']['fresh_all_input_verification'] = True
        resign(summary)
        with self.assertRaises(EvidenceError): project_terminal_search_summary(summary, model)


if __name__ == '__main__':
    unittest.main()
