"""Byte binding and supplementary timing on actual preserved eight responses.

Only the original cases are recorded measurements. Deliberate header/file
mutations below are rule-test counterexamples, never new native evidence.
The bound audit assembled for each test is explicitly a test fixture; it is
not presented as a newly performed full model/history audit.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..prepared_report_inputs import capture_report_primary, load_report_inputs
from ..trial_response_timing import summarize_trial_timing, timing_html


class PreparedReportInputsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus=Path(os.environ['TIMELEARNER_BOUND_REPORT_CORPUS']).resolve(strict=True)
        provenance=load(cls.corpus/'fixture-provenance.json')
        if not provenance['derived_binding_is_rule_test_fixture_only'] or provenance['new_full_model_reaudit_performed']:
            raise RuntimeError('requires explicitly separated actual-data rule fixture')

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.native=self.root/'native'
        shutil.copytree(self.corpus/'native',self.native)
        self.audit=load(self.corpus/'original-audit.json')
        self.audit['report_primary_binding']=capture_report_primary(self.native)
        self.audit_path=self.root/'test-fixture-audit.json';self.write(self.audit_path,self.audit)

    def write(self,path,value):
        path.write_text(json.dumps(value,allow_nan=False)+'\n',encoding='utf-8')

    def inputs(self):return load_report_inputs(self.audit_path,native_directory=self.native)

    def test_exact_observations_and_declared_counts_are_preserved(self):
        data=self.inputs();before=deepcopy(data['metrics'])
        timing=summarize_trial_timing(data['spec'],data['observations'],data['metrics'])
        self.assertEqual(data['metrics'],before)
        self.assertEqual([timing['declared_counts'][k]for k in ('TP','FP','FN','TN')],[1,1,0,6])
        self.assertEqual(timing['target_trials_with_before_last_output'],[])
        self.assertFalse(timing['new_response_criterion']);self.assertIsNone(timing['scientific_verdict'])
        target=next(r for r in timing['trials']if r['label']=='target')
        false=next(r for r in timing['trials']if r['declared_classification']=='FP')
        self.assertAlmostEqual(target['spike_times_from_last_input'][0],.0035,places=12)
        self.assertAlmostEqual(false['spike_times_from_last_input'][0],.0015,places=12)

    def test_early_and_later_target_outputs_remain_separate_from_weak_TP(self):
        data=self.inputs();observations=deepcopy(data['observations']);metrics=deepcopy(data['metrics'])
        o=next(x for x in observations if x['label']=='target');row=next(x for x in metrics['trials']if x['trial_id']==o['trial_id'])
        early=o['stimulus_times'][0]+.005
        o['spike_times']=sorted([early,*o['spike_times']]);o['spike_count']+=1
        row['window_spikes']=sorted([early,*row['window_spikes']]);row['spike_count']+=1
        timing=summarize_trial_timing(data['spec'],observations,metrics)
        actual=next(x for x in timing['trials']if x['trial_id']==o['trial_id'])
        self.assertEqual(actual['declared_classification'],'TP')
        self.assertEqual(actual['before_last_input_count'],1)
        self.assertEqual(actual['at_or_after_last_input_count'],1)
        self.assertEqual(timing['target_trials_with_before_last_output'],[o['trial_id']])
        self.assertIsNone(actual['timing_verdict'])

    def test_event_exactly_at_last_input_uses_roundoff_only_without_new_tolerance(self):
        data=self.inputs();observations=deepcopy(data['observations']);metrics=deepcopy(data['metrics'])
        o=next(x for x in observations if x['label']=='target');row=next(x for x in metrics['trials']if x['trial_id']==o['trial_id'])
        o['spike_times']=[o['stimulus_times'][-1]];row['window_spikes']=list(o['spike_times'])
        timing=summarize_trial_timing(data['spec'],observations,metrics);actual=next(x for x in timing['trials']if x['label']=='target')
        self.assertEqual(actual['before_last_input_count'],0)
        self.assertEqual(actual['at_or_after_last_input_count'],1)
        self.assertEqual(actual['spike_times_from_last_input'],[0.])
        self.assertIsNone(actual['timing_verdict'])

    def test_row_permutation_keeps_supplement_and_Russian_table(self):
        data=self.inputs();expected=summarize_trial_timing(data['spec'],data['observations'],data['metrics'])
        spec=deepcopy(data['spec']);spec['trials'].reverse();metrics=deepcopy(data['metrics']);metrics['trials'].reverse()
        self.assertEqual(expected,summarize_trial_timing(spec,list(reversed(data['observations'])),metrics))
        text=timing_html(expected)
        self.assertIn('Отрицательное время',text);self.assertIn('Паттерн',text)
        self.assertEqual(text.count('<tr>'),9)

    def test_incomplete_and_duplicate_trial_sets_cannot_produce_summary(self):
        data=self.inputs()
        for observations in (data['observations'][:-1],data['observations']+[data['observations'][0]]):
            with self.subTest(count=len(observations)),self.assertRaises(EvidenceError):
                summarize_trial_timing(data['spec'],observations,data['metrics'])
        observations=deepcopy(data['observations']);observations[0]['complete']=False
        with self.assertRaisesRegex(EvidenceError,'requires_valid_complete_observation'):
            summarize_trial_timing(data['spec'],observations,data['metrics'])

    def test_nonfinite_and_wrong_spike_count_cannot_hide_in_timing(self):
        data=self.inputs()
        for edit in (lambda o:o['stimulus_times'].__setitem__(-1,float('nan')),
                     lambda o:o.update(spike_count=o['spike_count']+1)):
            observations=deepcopy(data['observations']);edit(observations[0])
            with self.assertRaises(EvidenceError):summarize_trial_timing(data['spec'],observations,data['metrics'])

    def test_rewritten_observation_and_resigned_execution_are_still_rejected(self):
        p=self.native/'trial-0.json';observation=load(p);observation['samples'][0]['soma'][0]+=.001;self.write(p,observation)
        execution=load(self.native/'execution.json');captured=capture_report_primary(self.native)
        for row in execution['artifacts']:
            if row['path']=='trial-0.json':row.update(captured['files']['trial-0.json'])
        execution['sha256']=sha({k:v for k,v in execution.items()if k!='sha256'})
        self.write(self.native/'execution.json',execution)
        with self.assertRaisesRegex(EvidenceError,'audited_primary_changed'):self.inputs()

    def test_unbound_legacy_audit_requires_explicit_full_reaudit(self):
        del self.audit['report_primary_binding'];self.write(self.audit_path,self.audit)
        with self.assertRaisesRegex(EvidenceError,'legacy_audit_requires_bound_reaudit'):self.inputs()

    def test_duplicate_native_artifacts_are_not_collapsed_by_dictionary(self):
        execution=load(self.native/'execution.json');execution['artifacts'].append(deepcopy(execution['artifacts'][0]))
        execution['sha256']=sha({k:v for k,v in execution.items()if k!='sha256'});self.write(self.native/'execution.json',execution)
        self.audit['report_primary_binding']=capture_report_primary(self.native);self.write(self.audit_path,self.audit)
        with self.assertRaisesRegex(EvidenceError,'duplicate_native_artifact'):self.inputs()

    def test_mismatched_audited_model_or_counts_are_not_reported(self):
        self.audit['native_evidence']['metrics']['model_revision']='a'*64;self.write(self.audit_path,self.audit)
        with self.assertRaisesRegex(EvidenceError,'incomplete_or_changed_metrics'):self.inputs()
        data=load(self.corpus/'original-audit.json');metrics=data['native_evidence']['metrics'];metrics['pooled_counts']['TP']+=1
        spec=load(self.native/'evaluation.json');observations=[load(self.native/f'trial-{i}.json')for i in range(8)]
        with self.assertRaisesRegex(EvidenceError,'declared_counts_changed'):summarize_trial_timing(spec,observations,metrics)

    def test_byte_identical_relocation_does_not_change_scientific_identity(self):
        first=self.inputs();other=self.root/'relocated-native';shutil.copytree(self.native,other)
        second=load_report_inputs(self.audit_path,native_directory=other)
        self.assertEqual(first['primary_binding']['files'],second['primary_binding']['files'])
        self.assertEqual(first['metrics'],second['metrics'])
        self.assertEqual(summarize_trial_timing(first['spec'],first['observations'],first['metrics']),
                         summarize_trial_timing(second['spec'],second['observations'],second['metrics']))


if __name__=='__main__':unittest.main()
