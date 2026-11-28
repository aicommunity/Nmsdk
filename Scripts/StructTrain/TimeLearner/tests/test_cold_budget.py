"""Declared search coverage and factor preservation; no native training claim."""
from copy import deepcopy
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from ..cold_budget import coverage,prepare_single_sweep,main
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError
from ..native_pipeline_worker import validate_job
from .test_candidate_window_training_job import cold7,job


def template(branch=False,base=1,normalization='N0'):
    payload=job(cold7(base,branch=branch,n=4))
    payload['configuration']['composite_measurement']['attempt_limits'].update(
        maximum_groups=512,maximum_native_probes=4096,maximum_total_samples=10000000)
    payload['configuration']['model']['normalization']=normalization
    payload.pop('sha256');payload['sha256']=sha(payload)
    return payload


class ColdBudgetTest(unittest.TestCase):
    def test_one_complete_sweep_changes_only_declared_budget_and_run_identity(self):
        for branch in (False,True):
          for normalization in ('N0','N1'):
            original=template(branch,normalization=normalization);before=deepcopy(original)
            prepared,report=prepare_single_sweep(original,run_id='planned-complete-sweep',
                candidates_per_input=24,maximum_probes=160,maximum_model_seconds=1000.)
            self.assertEqual(original,before)
            self.assertEqual(validate_job('train',prepared)['job_sha256'],prepared['sha256'])
            self.assertEqual(prepared['configuration']['model'],before['configuration']['model'])
            expected=deepcopy(before);expected.pop('sha256')
            expected['configuration'].update(run_id='planned-complete-sweep',maximum_model_seconds=1000.)
            expected['configuration']['search'].update(maximum_candidates_per_input=24,
                maximum_probes=160,maximum_sweeps=1)
            expected['maximum_model_ticks']=2000000
            self.assertEqual({k:v for k,v in prepared.items() if k!='sha256'},expected)
            self.assertEqual(report['candidate_pair_probes'],144)
            self.assertEqual(report['best_restoration_probes'],6)
            self.assertEqual(report['final_all_input_probes'],4)
            self.assertEqual(report['valid_search_probe_upper_bound_per_sweep'],154)
            self.assertTrue(report['all_declared_sweeps_fit'])
            self.assertFalse(report['convergence_verified'])

    def test_four_requested_sweeps_do_not_hide_global_budget_shortage(self):
        payload=template();payload['configuration']['search'].update(
            maximum_candidates_per_input=16,maximum_probes=128,maximum_sweeps=4)
        payload.pop('sha256');payload['sha256']=sha(payload);report=coverage(payload)
        self.assertEqual(report['valid_search_probe_upper_bound_per_sweep'],106)
        self.assertEqual(report['valid_search_probe_upper_bound_all_declared_sweeps'],424)
        self.assertTrue(report['first_sweep_fits']);self.assertFalse(report['all_declared_sweeps_fit'])

    def test_n0_repetitions_are_charged_before_local_commit_and_restore(self):
        prepared,report=prepare_single_sweep(template(base=2),run_id='repeat-control',
            candidates_per_input=24,maximum_probes=320,maximum_model_seconds=1000.)
        self.assertEqual(report['candidate_repetitions'],2)
        self.assertEqual(report['valid_search_probe_upper_bound_per_sweep'],304)
        self.assertEqual(prepared['configuration']['search']['n0_candidate_repeats'],2)

    def test_terminal9_keeps_composite_cost_and_funds_completion_without_extra_search(self):
        for branch in (False,True):
          for normalization in ('N0','N1'):
            original=template(branch,normalization=normalization);terminal=deepcopy(original)
            c=terminal['configuration'];c.update(terminal_base_schema_version=c['schema_version'],schema_version=9,
                terminal_selection=dict(schema_version=1,maximum_wall_seconds=30.))
            terminal.pop('sha256');terminal['sha256']=sha(terminal);before=deepcopy(terminal)
            kwargs=dict(run_id='same-search-budget',candidates_per_input=24,maximum_probes=160,maximum_model_seconds=1000.)
            baseline,old=prepare_single_sweep(original,**kwargs)
            prepared,new=prepare_single_sweep(terminal,**kwargs)
            self.assertEqual(terminal,before)
            for field in ('native_probes_per_valid_group','composite_capacity','declared_window_model_seconds',
                          'valid_search_probe_upper_bound_per_sweep'):
                self.assertEqual(new[field],old[field])
            self.assertEqual(new['native_probes_per_valid_group'],6)
            self.assertEqual(prepared['configuration']['search'],baseline['configuration']['search'])
            self.assertEqual(prepared['configuration']['model'],baseline['configuration']['model'])
            self.assertEqual(prepared['configuration']['maximum_model_seconds'],1000.)
            self.assertEqual(prepared['maximum_model_ticks'],baseline['maximum_model_ticks']+2)
            self.assertTrue(new['terminal_completion']['completion_ticks_funded'])
            self.assertFalse(new['terminal_completion']['extra_search_time_allowed'])
            underfunded=deepcopy(prepared);underfunded['maximum_model_ticks']-=2
            underfunded.pop('sha256');underfunded['sha256']=sha(underfunded)
            self.assertFalse(coverage(underfunded)['terminal_completion']['completion_ticks_funded'])

    def test_insufficient_logical_native_or_window_budgets_are_not_silently_enlarged(self):
        kwargs=dict(run_id='planned',candidates_per_input=24,maximum_probes=160,maximum_model_seconds=1000.)
        with self.assertRaisesRegex(EvidenceError,'search_budget_underfunded'):
            prepare_single_sweep(template(),**{**kwargs,'maximum_probes':153})
        limited=template();limited['configuration']['composite_measurement']['attempt_limits'].update(
            maximum_groups=32,maximum_native_probes=128,maximum_total_samples=32000)
        limited.pop('sha256');limited['sha256']=sha(limited);before=deepcopy(limited)
        with self.assertRaisesRegex(EvidenceError,'native_capacity_underfunded'):
            prepare_single_sweep(limited,**kwargs)
        self.assertEqual(limited,before)
        with self.assertRaisesRegex(EvidenceError,'model_windows_underfunded'):
            prepare_single_sweep(template(),**{**kwargs,'maximum_model_seconds':1.})

    def test_invalid_numeric_parameters_cannot_create_a_signed_job(self):
        kwargs=dict(run_id='planned',candidates_per_input=24,maximum_probes=160,maximum_model_seconds=1000.)
        for change in (dict(candidates_per_input=True),dict(maximum_probes=0),dict(run_id=''),
                       dict(maximum_model_seconds=float('nan')),dict(maximum_model_seconds=True)):
            with self.subTest(change=change),self.assertRaises(EvidenceError):
                prepare_single_sweep(template(),**{**kwargs,**change})

    def test_cli_creates_source_bound_job_without_overwriting_or_starting_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'template.json';raw=json.dumps(template(True,normalization='N1')).encode()
            source.write_bytes(raw);output=root/'prepared'
            args=['--template',str(source),'--run-id','branch-complete',
                '--candidates-per-input','24','--maximum-probes','160',
                '--model-seconds','1000','--output',str(output)]
            with redirect_stdout(io.StringIO()):main(args)
            self.assertEqual(source.read_bytes(),raw)
            declaration=json.loads((output/'declaration.json').read_bytes())
            self.assertEqual(declaration['template']['sha256'],hashlib.sha256(raw).hexdigest())
            self.assertFalse(declaration['started'])
            self.assertEqual(declaration['budget_coverage']['valid_search_probe_upper_bound_per_sweep'],154)
            before=(output/'job.json').read_bytes()
            with self.assertRaisesRegex(EvidenceError,'output_exists'):main(args)
            self.assertEqual((output/'job.json').read_bytes(),before)
            args[args.index('160')]='1';args[-1]=str(root/'refused')
            with self.assertRaises(EvidenceError):main(args)
            self.assertFalse((root/'refused').exists())
