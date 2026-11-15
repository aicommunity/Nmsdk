"""Search reporting must not manufacture measured terminal-state coverage."""
import contextlib
from copy import deepcopy
import io
import hashlib
import json
import os
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch

from ..native_evidence import EvidenceError
from ..model_identity import canonical_model_sha256 as digest
from ..training_search_report import _project_summary, analyze_search_history


def fixture(size=2):
    parameters = [dict(length=1, synapses=1, resistance=86e6) for _ in range(size)]
    row = dict(trial_id='search/2', input_index=0, model_revision='a'*64,
        model_epoch=1, full_parameters=deepcopy(parameters), parameters=deepcopy(parameters[0]),
        timing_low=-.48, timing_high=-.48, amplitude_residual=0., within_timing=False,
        within_amplitude=True, parameter_change_cost=0., capacitance_witness_id='original-C')
    summary = dict(kind='native_training_state_summary', schema_version=8,
        search_history_retained=True, reference_complete=True, actual_model_revision='b'*64,
        actual_parameters=deepcopy(parameters), outcome='budget_exhausted', reason='budget',
        candidates=[row], resistance_domains=[], rejections=[], final_group_ids=[],
        search_probes=58, applied_edits=28,
        tolerances=dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
    model = dict(inputs=[{} for _ in range(size)], normalization='N1', branch=False)
    return summary, model


def recovery_ledger(summary):
    deliveries = []
    for ordinal in range(5):
        values = deepcopy(summary['actual_parameters'])
        values[0]['length'] = ordinal+1
        transition = dict(action_serial=ordinal+1, input_index=0, candidate_input_index=0,
            sweep=0, model_epoch=ordinal, invalid_before=ordinal, invalid_after=ordinal+1,
            run_id='attempt', trial_id='rejected/'+str(ordinal), base_model_revision='a'*64,
            effective_model_revision='b'*64, phase='input', validity='ambiguous',
            full_parameters=values, capacitance=None,
            disposition='invalid_budget_stop' if ordinal == 4 else 'cursor_advanced',
            status_after='invalid_observation' if ordinal == 4 else 'searching', reason_after='')
        event = dict(kind='timelearner_candidate_window_recovery_event', schema_version=1,
            transition=transition, group_id='group/'+str(ordinal), rejected_content_id='c'*64,
            source_origin='d'*64, owner_scope='owner', candidate_witness_id='e'*64,
            issued_probes=ordinal+1, applied_edits=ordinal, accepted_composite_observations=0)
        event['event_id'] = digest(event)
        # A wire-only fixture; full runtime/primary admission is checked by the
        # real-corpus CLI test, not inferred from this projection unit control.
        deliveries.append(dict(event=event, runtime_plan=dict(schema_version=3, run_id='attempt')))
    ledger = dict(kind='timelearner_candidate_window_recovery_ledger', schema_version=1,
        source_origin='d'*64, owner_family_binding='e'*64,
        measurement_archive_document_id='f'*64, producer_log_intact=True,
        independent_delivery_completeness_verified=False, deliveries=deliveries)
    ledger['sha256'] = digest(ledger)
    return ledger


class TrainingSearchReportTest(unittest.TestCase):
    def test_absent_recovery_ledger_is_unknown_not_zero_recoveries(self):
        summary, model = fixture()
        result = _project_summary(summary, model)
        self.assertIsNone(result['recorded_recovery_deliveries'])
        self.assertIsNone(result['recovery_ledger_provenance'])

    def test_empty_ledger_does_not_claim_independent_attempt_completeness(self):
        summary, model = fixture()
        ledger = recovery_ledger(summary);ledger['deliveries'] = []
        ledger['sha256'] = digest({k: v for k, v in ledger.items() if k != 'sha256'})
        summary['recovery_ledger'] = ledger
        result = _project_summary(summary, model)
        self.assertEqual(result['recorded_recovery_deliveries'], [])
        self.assertFalse(result['recovery_ledger_provenance']['independent_delivery_completeness_verified'])
        self.assertFalse(result['attempt_total_independently_recounted'])

    def test_different_rejected_geometries_runtime_plans_and_budget_stop_survive(self):
        summary, model = fixture()
        summary['recovery_ledger'] = recovery_ledger(summary)
        before = deepcopy(summary)
        result = _project_summary(summary, model)
        rows = result['recorded_recovery_deliveries']
        self.assertEqual(rows, summary['recovery_ledger']['deliveries'])
        self.assertEqual([r['event']['transition']['full_parameters'][0]['length'] for r in rows], [1,2,3,4,5])
        self.assertEqual(rows[-1]['event']['transition']['disposition'], 'invalid_budget_stop')
        self.assertEqual(len(result['recorded_candidate_measurements']), 1)
        self.assertIsNone(result['scientific_verdict'])
        rows[0]['event']['transition']['full_parameters'][0]['length'] = 99
        rows[0]['runtime_plan']['run_id'] = 'changed-copy'
        self.assertEqual(summary, before)

    def test_malformed_rehashed_or_duplicate_recovery_data_are_refused(self):
        for defect in ('schema', 'duplicate', 'dimension', 'nonfinite', 'counter', 'completeness'):
            summary, model = fixture()
            ledger = recovery_ledger(summary)
            event = ledger['deliveries'][0]['event']
            if defect == 'schema':ledger['schema_version'] = 2
            elif defect == 'duplicate':ledger['deliveries'].append(deepcopy(ledger['deliveries'][0]))
            elif defect == 'dimension':event['transition']['full_parameters'].pop()
            elif defect == 'counter':event['transition']['invalid_after'] = 99
            elif defect == 'completeness':ledger['independent_delivery_completeness_verified'] = True
            else:event['transition']['full_parameters'][0]['resistance'] = float('nan')
            if defect != 'nonfinite':
                event['event_id'] = digest({k: v for k, v in event.items() if k != 'event_id'})
                ledger['sha256'] = digest({k: v for k, v in ledger.items() if k != 'sha256'})
            summary['recovery_ledger'] = ledger
            with self.subTest(defect=defect), self.assertRaises(EvidenceError):
                _project_summary(summary, model)

    def test_cli_refuses_output_inside_original_run_before_any_audit(self):
        from ..__main__ import main
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary);source = root/'run-manifest.json';source.write_bytes(b'{}')
            output = root/'analysis.json'
            with patch('Scripts.StructTrain.TimeLearner.training_search_report.audit_run_manifest') as audit, \
                 contextlib.redirect_stderr(io.StringIO()):
                code = main(['analyze', str(source), '--format', 'native-search-history',
                             '--output', str(output)])
            self.assertEqual(code, 2)
            audit.assert_not_called()
            self.assertFalse(output.exists())

    def test_summary_changed_after_full_audit_cannot_be_projected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary);(root/'native').mkdir();(root/'input').mkdir()
            summary, model = fixture()
            files = {'native/train_stopped_summary.json': summary,
                'native/execution.json': dict(package_path='train_stopped_state.json',
                    model_revision=summary['actual_model_revision'], training_outcome='budget_exhausted'),
                'input/job.json': dict(configuration=dict(model=model))}
            records = []
            for name, value in files.items():
                raw = json.dumps(value).encode();(root/name).write_bytes(raw)
                records.append(dict(path=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
            manifest = root/'run-manifest.json'
            manifest.write_text(json.dumps(dict(operation='train', validity='valid', artifacts=records)))
            def audited_then_changed(_):
                (root/'native/train_stopped_summary.json').write_bytes(b'{}')
                return dict(run_evidence_consistent=True)
            # This unit control changes the file after the auditor boundary;
            # it does not stand in for the separate real-corpus CLI test.
            with patch('Scripts.StructTrain.TimeLearner.training_search_report.audit_run_manifest',
                       side_effect=audited_then_changed), \
                 self.assertRaisesRegex(EvidenceError, 'search_report_source_changed'):
                analyze_search_history(manifest)

    def test_parameters_alone_do_not_prove_actual_model_was_measured(self):
        summary, model = fixture()
        result = _project_summary(summary, model)
        self.assertEqual(result['actual_parameters'], summary['candidates'][0]['full_parameters'])
        self.assertFalse(result['actual_model_matched_in_candidate_history'])
        self.assertEqual(result['actual_model_candidate_trial_ids'], [])
        self.assertEqual(result['producer_reported_search_probes'], 58)
        self.assertEqual(len(result['recorded_candidate_measurements']), 1)
        self.assertFalse(result['attempt_total_independently_recounted'])
        self.assertIsNone(result['training_or_final_verification_verdict'])

    def test_exact_revision_and_parameters_match_is_not_a_certificate(self):
        summary, model = fixture()
        summary['actual_model_revision'] = 'a'*64
        result = _project_summary(summary, model)
        self.assertTrue(result['actual_model_matched_in_candidate_history'])
        self.assertEqual(result['actual_model_candidate_trial_ids'], ['search/2'])
        self.assertIsNone(result['scientific_verdict'])

    def test_unretained_history_is_unknown_instead_of_unmeasured(self):
        summary, model = fixture()
        summary.update(search_history_retained=False, candidates=[])
        result = _project_summary(summary, model)
        self.assertIsNone(result['actual_model_matched_in_candidate_history'])
        self.assertIsNone(result['actual_model_candidate_trial_ids'])

    def test_branch_n0_more_than_four_inputs_and_extra_candidate_fields_survive(self):
        summary, model = fixture(7)
        model.update(branch=True, normalization='N0')
        result = _project_summary(summary, model)
        self.assertEqual((result['topology'], result['normalization'], result['anchor_index']),
                         ('Branch', 'N0', 6))
        row = result['recorded_candidate_measurements'][0]
        self.assertEqual(row['capacitance_witness_id'], 'original-C')
        row['full_parameters'][0]['length'] = 99
        self.assertEqual(summary['candidates'][0]['full_parameters'][0]['length'], 1)

    def test_duplicate_trial_unknown_schema_and_nonfinite_residual_are_refused(self):
        for defect in ('duplicate', 'schema', 'nonfinite'):
            summary, model = fixture()
            if defect == 'duplicate':summary['candidates'].append(deepcopy(summary['candidates'][0]))
            elif defect == 'schema':summary['schema_version'] = 9
            else:summary['candidates'][0]['amplitude_residual'] = float('nan')
            with self.subTest(defect=defect), self.assertRaises(EvidenceError):
                _project_summary(summary, model)


class TrainingSearchReportActualTest(unittest.TestCase):
    def test_production_cli_reports_original_fifteen_measurements_not_terminal_L22_as_success(self):
        from ..__main__ import main
        manifest = Path(os.environ['TIMELEARNER_SEARCH_REPORT_PRIMARY'])/'run-manifest.json'
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['analyze', str(manifest), '--format', 'native-search-history'])
        self.assertEqual(code, 0)
        document = json.loads(output.getvalue());result = document['analysis']
        self.assertEqual(document['validity'], 'valid')
        self.assertEqual(result['actual_model_revision'],
            '3b8a160f2fe6f5ace6aa377f5d42117bcc922bcdd746358ca8d7c34fc67a6b1c')
        self.assertEqual(result['actual_parameters'][0]['length'], 22)
        points = result['recorded_candidate_measurements']
        self.assertEqual(len(points), 15)
        self.assertEqual([p['parameters']['length'] for p in points], [1, 1]+list(range(2, 15)))
        self.assertEqual(len(result['recorded_rejections']), 13)
        self.assertEqual(len(result['assessed_resistance_domains']), 28)
        self.assertEqual(result['producer_reported_search_probes'], 58)
        self.assertEqual(result['actual_model_candidate_trial_ids'], [])
        self.assertFalse(result['actual_model_matched_in_candidate_history'])
        self.assertTrue(all(not p['within_timing'] for p in points))
        self.assertEqual(result['final_verification_group_ids'], [])
        self.assertIsNone(document['evaluation_verdict'])
        self.assertIsNone(result['scientific_verdict'])
        (Path(os.environ['TMPDIR'])/'actual-training-search-report.json').write_text(
            json.dumps(document, indent=2, allow_nan=False)+'\n', encoding='utf-8')


class CoupledRecoverySearchReportActualTest(unittest.TestCase):
    def test_production_cli_keeps_five_distinct_failed_candidates_outside_measured_history(self):
        from ..__main__ import main
        manifest = Path(os.environ['TIMELEARNER_COUPLED_RECOVERY_REPORT_RUN'])/'run-manifest.json'
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['analyze', str(manifest), '--format', 'native-search-history'])
        self.assertEqual(code, 0)
        document = json.loads(output.getvalue());result = document['analysis']
        self.assertEqual(document['validity'], 'valid')
        self.assertEqual(result['schema_version'], 2)
        self.assertEqual(result['outcome'], 'invalid_observation')
        self.assertEqual(result['reason'], 'rejected_candidate_window:ambiguous')
        rows = result['recorded_recovery_deliveries']
        transitions = [row['event']['transition'] for row in rows]
        self.assertEqual([t['trial_id'].split('/')[-1] for t in transitions], ['90','95','99','103','107'])
        self.assertEqual([t['model_epoch'] for t in transitions], [21,22,23,24,25])
        self.assertEqual([[p['length'] for p in t['full_parameters']] for t in transitions],
                         [[28,28,27,1], [29,28,27,1], [29,29,27,1], [30,29,27,1], [28,27,27,1]])
        self.assertEqual([t['disposition'] for t in transitions], ['cursor_advanced']*4+['invalid_budget_stop'])
        self.assertTrue(all(t['phase'] == 'input' and t['input_index'] == 1 for t in transitions))
        self.assertTrue(all(row['runtime_plan']['search']['maximum_invalid_observations'] == 4 for row in rows))
        self.assertEqual(len(result['recorded_candidate_measurements']), 22)
        measured_trials = {row['trial_id'] for row in result['recorded_candidate_measurements']}
        self.assertFalse(measured_trials.intersection(t['trial_id'] for t in transitions))
        self.assertFalse(result['recovery_ledger_provenance']['independent_delivery_completeness_verified'])
        self.assertFalse(result['attempt_total_independently_recounted'])
        self.assertEqual(result['final_verification_group_ids'], [])
        self.assertIsNone(result['scientific_verdict'])
        self.assertIsNone(document['evaluation_verdict'])
        with (Path(os.environ['TMPDIR'])/'coupled-recovery-search-history.json').open('x', encoding='utf-8') as stream:
            json.dump(document, stream, indent=2, allow_nan=False);stream.write('\n')
