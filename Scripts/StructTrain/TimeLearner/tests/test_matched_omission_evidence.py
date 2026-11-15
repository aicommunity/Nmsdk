"""Controlled primary fixtures for the independent reader; run on workers."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import matched_omission_evidence as reader
from ..matched_omission_evidence import (METHOD, audit_matched_omission_evidence,
                                        audit_matched_omission_file, diagnose_declared_window)
from ..native_evidence import EvidenceError, count, number


def fixture(shared=False, partial=False):
    policy = dict(comparison_radius_ticks=1, time_comparison_tolerance=1e-12, baseline_absolute=0.,
                  repeatability_absolute=0., repeatability_relative=0., influence_absolute=.1, influence_relative=0.)
    profile = dict(generator_class='NPulseGeneratorTransit', amplitude=1., pulse_length=.1, frequency_hz=10.,
                   frequency_deviation=0., use_transit_signal=False, use_pattern_output=False)
    full = [0.,0.,1.,3.,1.,0.,0.,0.,4. if shared else 2.,0.,0.,0.,0.]
    missing_zero = [0.,0.,0.,0.,0.,0.,0.,0.,2.,0.,0.,0.,0.]
    missing_one = [0.,0.,1.,3.,1.,0.,0.,0.,2. if shared else 0.,0.,0.,0.,0.]
    masks = [[0,1],[1],[0],[0,1]]; signals = [full, missing_zero, missing_one, full]
    packets, records, primary = [], [], {}
    for index, (mask, signal) in enumerate(zip(masks, signals)):
        start = float(2*index); times = [start+i/10 for i in range(13)]
        subset = dict(purpose='stimulus_subset_characterization', source_training_pattern_hash='pattern',
                      physical_input_count=2, source_ordinals=mask)
        spec = dict(time_frame='absolute_model_time', schema_version=6, run_id='run', trial_id='group/native/'+str(index),
                    sample_id='sample', pattern_hash='pattern' if len(mask)==2 else 'mask'+str(index),
                    effective_model_revision='model', begin=start, end=start+1.2, maximum_sample_gap=.1,
                    minimum_amplitude=.5, maximum_samples=13, record_spikes=False, baseline=[2.,2.], windows=[],
                    expected_stimulus_ids=['pulse'+str(i) for i in mask], stimulus_profile=deepcopy(profile),
                    wave_assignment='window_only', peak_selection='isolated_window', stimulus_subset=subset)
        requested = dict(deepcopy(spec), time_frame='relative_to_trial_start', begin=0., end=1.2,
                         baseline=[], effective_model_revision='')
        events = [dict(id='pulse'+str(i), time=times[[1,6][i]], relative_to_trial_start=times[[1,6][i]]-start) for i in mask]
        observation = dict(schema_version=6, specification=spec, complete=True, valid=True, end_reason='window_closed',
                           reasons=[], sample_count=13, stimuli=events, peaks=[], burst_assignments=[], spikes=[],
                           spike_count=None, first_stimulus_time=events[0]['time'])
        prepared = dict(routing='classic_burst', input_id='input0', protocol_revision='protocol',
                        base_model_revision='model', effective_model_revision='model', model_epoch=0, selected_input_index=None)
        packets.append(dict(kind='timelearner_native_probe_evidence', evidence_schema_version=2, native_status='completed',
                            current_base_revision='model', reasons=[], requires_fresh_verification=False,
                            requested_specification=requested, prepared=prepared, observation=observation))
        name = 'native-'+str(index)+'.csv'
        lines = ['time,stimulus,soma0,soma1']
        for frame, (time, value) in enumerate(zip(times, signal)):
            stimulus = 1 if frame in [[1,6][i] for i in mask] else 0
            lines.append(','.join(format(v,'.17g') for v in [time,stimulus,2.+value,2.]))
        raw = ('\n'.join(lines)+'\n').encode(); primary[name] = raw
        records.append(dict(path=name, presented_ordinals=mask, sha256=hashlib.sha256(raw).hexdigest()))
    maxima = [dict(first_sample=3,last_sample=3,amplitude=3.,raw_potential=5.,time=.3,plateau_end=.3,
                   supported_inputs=[0], influence_by_input=['supported','not_supported'], unknown=False,
                   clipped=False,precedes_assigned_stimulus=False),
              dict(first_sample=8,last_sample=8,amplitude=4. if shared else 2.,raw_potential=6. if shared else 4.,
                   time=.8,plateau_end=.8,supported_inputs=[0,1] if shared else [1],
                   influence_by_input=['supported' if shared else 'not_supported','supported'],unknown=False,
                   clipped=False,precedes_assigned_stimulus=False)]
    group = dict(schema_version=1,kind='native_matched_omission_fixture',method=METHOD,group_id='group',native_probes=4,
                 packets=packets,traces=records,reason='omission_group_closed',assignment_validity='ambiguous' if shared else 'valid',
                 training_certificate_eligible=False,scientific_verdict=None,source_pattern_sha256='pattern',reset_binding='reset',
                 model_instance_binding='instance',physical_channel_paths=['Neuron.Soma1','Neuron.Soma2'],
                 assigned_input=0,assigned_channel=0,policy=policy,
                 assignment_reasons=['highest_assigned_maximum_has_shared_or_unknown_support'] if shared else [],
                 maxima=maxima,selected_full_maximum=None if shared else 0)
    if partial:
        group.update(native_probes=1,packets=packets[:1],traces=records[:1],reason='omission_group_external_stop',
                     assignment_validity='not_available',assignment_reasons=[],maxima=[],selected_full_maximum=None)
        primary = {records[0]['path']:primary[records[0]['path']]}
    return group, primary


def branch_fixture():
    """Same measurements on the one physical Branch soma, assigned to input1."""
    group, primary = fixture()
    group.update(physical_channel_paths=['Neuron.Soma1'], assigned_input=1, assigned_channel=0,
                 selected_full_maximum=1)
    group['maxima'][0]['precedes_assigned_stimulus'] = True
    for packet, record in zip(group['packets'], group['traces']):
        packet['prepared'].update(routing='branch_solo_burst', input_id='input1', selected_input_index=1)
        packet['observation']['specification']['baseline'] = [2.]
        name = record['path']
        raw = ('\n'.join(line.rsplit(',', 1)[0] for line in primary[name].decode().splitlines())+'\n').encode()
        primary[name] = raw; record['sha256'] = hashlib.sha256(raw).hexdigest()
    return group, primary


class MatchedOmissionEvidenceTest(unittest.TestCase):
    def rejected(self, group, primary):
        with self.assertRaises(EvidenceError): audit_matched_omission_evidence(group, primary)

    def test_exclusive_assigned_peak_recomputed_without_certification(self):
        group, primary = fixture(); result = audit_matched_omission_evidence(group, primary)
        self.assertEqual(result['assignment_validity'], 'valid'); self.assertTrue(result['assignment_recomputed'])
        for key in ['training_certificate_eligible','causal_origin_verified','native_execution_verified',
                    'total_budget_declarations_available','reset_instance_ownership_independently_verified']:
            self.assertFalse(result[key])

    def test_larger_shared_late_peak_blocks_global_support_method(self):
        group, primary = fixture(shared=True); result = audit_matched_omission_evidence(group, primary)
        self.assertEqual(result['assignment_validity'],'ambiguous')
        diagnostic = diagnose_declared_window(group,result,.1,.5)
        self.assertEqual(diagnostic['in_window_exclusive_assigned_maxima'],[0])
        self.assertEqual(diagnostic['possibly_assigned_shared_maxima_outside'],[1])
        self.assertFalse(diagnostic['criterion_changed']); self.assertFalse(diagnostic['training_certificate_eligible'])

    def test_partial_stop_checks_first_trace_without_inventing_assignment(self):
        group, primary = fixture(partial=True); result = audit_matched_omission_evidence(group, primary)
        self.assertFalse(result['complete_group']); self.assertFalse(result['assignment_recomputed'])
        group['assignment_validity']='valid'; self.rejected(group,primary)

    def test_tampered_selected_peak_or_support_is_rejected(self):
        for mutation in ('selected_full_maximum','support','validity'):
            group, primary = fixture()
            if mutation=='selected_full_maximum':group[mutation]=1
            elif mutation=='support':group['maxima'][0]['supported_inputs']=[1]
            else:group['assignment_validity']='ambiguous'
            self.rejected(group,primary)

    def test_missing_duplicate_or_extra_trace_is_rejected(self):
        group, primary = fixture(); del primary['native-1.csv']; self.rejected(group,primary)
        group, primary = fixture(); group['traces'][1]['path']='native-0.csv'; self.rejected(group,primary)
        group, primary = fixture(); primary['unused.csv']=b''; self.rejected(group,primary)

    def test_unknown_schema_or_fields_are_rejected(self):
        group, primary = fixture(); group['schema_version']=2; self.rejected(group,primary)
        group, primary = fixture(); group['policy']['silent_fallback']=True; self.rejected(group,primary)

    def test_schema_ids_require_json_integers_instead_of_numeric_equality(self):
        paths = [('schema_version',), ('packets',0,'evidence_schema_version'),
                 ('packets',0,'observation','schema_version'),
                 ('packets',0,'observation','specification','schema_version'),
                 ('packets',0,'requested_specification','schema_version')]
        for path in paths:
            for boolean in (False, True):
                with self.subTest(path=path, boolean=boolean):
                    group, primary = fixture(); node = group
                    for key in path[:-1]: node = node[key]
                    node[path[-1]] = True if boolean else float(node[path[-1]])
                    self.rejected(group, primary)

    def test_assigned_indices_are_rejected_before_entering_measurement_math(self):
        for field in ('assigned_input', 'assigned_channel'):
            for value in (0., False):
                with self.subTest(field=field, value=value):
                    group, primary = fixture(); group[field] = value
                    with patch.object(reader, '_recompute', side_effect=AssertionError('untyped index reached replay')):
                        self.rejected(group, primary)

    def test_native_dimensions_and_policy_radius_require_json_integers(self):
        paths = [('native_probes',), ('policy','comparison_radius_ticks'),
                 ('packets',0,'prepared','model_epoch'), ('packets',0,'observation','sample_count'),
                 ('packets',0,'observation','specification','maximum_samples'),
                 ('packets',0,'requested_specification','maximum_samples'),
                 ('packets',0,'observation','specification','stimulus_subset','physical_input_count'),
                 ('packets',0,'requested_specification','stimulus_subset','physical_input_count')]
        for path in paths:
            with self.subTest(path=path):
                group, primary = fixture(); node = group
                for key in path[:-1]: node = node[key]
                node[path[-1]] = float(node[path[-1]])
                self.rejected(group, primary)

    def test_branch_selector_is_an_integer_identity_not_boolean_true_or_float_one(self):
        group, primary = branch_fixture()
        self.assertEqual(audit_matched_omission_evidence(group, primary)['assignment_validity'], 'valid')
        for value in (True, 1.):
            with self.subTest(value=value):
                group, primary = branch_fixture()
                for packet in group['packets']: packet['prepared']['selected_input_index'] = value
                self.rejected(group, primary)

    def test_manifest_and_requested_source_ordinals_are_strict_integer_ids(self):
        for path in [('traces',0,'presented_ordinals'),
                     ('packets',0,'requested_specification','stimulus_subset','source_ordinals'),
                     ('packets',0,'observation','specification','stimulus_subset','source_ordinals')]:
            with self.subTest(path=path):
                group, primary = fixture(); node = group
                for key in path: node = node[key]
                node[0] = float(node[0]); self.rejected(group, primary)

    def test_recorded_maximum_and_support_indices_are_strict_bounded_integers(self):
        paths = [('selected_full_maximum',), ('maxima',0,'first_sample'),
                 ('maxima',0,'last_sample'), ('maxima',0,'supported_inputs',0)]
        for path in paths:
            with self.subTest(path=path):
                group, primary = fixture(); node = group
                for key in path[:-1]: node = node[key]
                node[path[-1]] = float(node[path[-1]]); self.rejected(group, primary)
        group, primary = fixture(); group['maxima'][0]['last_sample'] = 13; self.rejected(group, primary)
        group, primary = fixture(); group['maxima'][0]['supported_inputs'] = [2]; self.rejected(group, primary)

    def test_absurd_branch_input_count_is_bounded_by_full_mask_before_any_large_range(self):
        group, primary = branch_fixture()
        for packet in group['packets']:
            for spec in (packet['observation']['specification'], packet['requested_specification']):
                spec['stimulus_subset']['physical_input_count'] = 2**53-1
        # This test must fail safely if the inventory guard regresses: never
        # actually attempt list(range(2**53-1)) on a worker.
        def bounded_range(*args):
            stop = args[0] if len(args) == 1 else args[1]
            if abs(stop) > 64: raise AssertionError('unbounded dimension reached range')
            return range(*args)
        with patch.object(reader, 'range', bounded_range, create=True):
            self.rejected(group, primary)

    def test_shared_numeric_contract_still_accepts_integral_float_measurements(self):
        self.assertEqual(count(1.), 1); self.assertEqual(number(.25), .25)
        with self.assertRaises(EvidenceError): number(True)
        group, primary = fixture(); group['policy']['influence_relative'] = 0.
        self.assertTrue(audit_matched_omission_evidence(group, primary)['assignment_recomputed'])

    def test_declared_window_adapter_rejects_an_untyped_assigned_index(self):
        group, primary = fixture(); receipt = audit_matched_omission_evidence(group, primary)
        group['assigned_input'] = 0.
        with self.assertRaises(EvidenceError): diagnose_declared_window(group, receipt, .1, .5)

    def test_changed_model_epoch_or_trial_is_rejected(self):
        for field,value in [('base_model_revision','other'),('model_epoch',1)]:
            group, primary = fixture(); group['packets'][1]['prepared'][field]=value; self.rejected(group,primary)
        group, primary = fixture(); group['packets'][1]['observation']['specification']['trial_id']='duplicate'; self.rejected(group,primary)

    def test_nonfinite_or_modified_primary_is_rejected_even_if_rehashed(self):
        for token in (b'NaN',b'inf',b'1e309'):
            group, primary = fixture(); primary['native-0.csv'] = primary['native-0.csv'].replace(b'0,0,2,2',token+b',0,2,2',1)
            group['traces'][0]['sha256']=hashlib.sha256(primary['native-0.csv']).hexdigest(); self.rejected(group,primary)
        group, primary = fixture(); primary['native-0.csv']+=b'0,0,0,0\n'; self.rejected(group,primary)

    def test_baseline_source_and_retained_timestamp_changes_are_rejected(self):
        for field,value in [('baseline',[3.,2.]),('stimulus_profile',None)]:
            group, primary = fixture(); group['packets'][1]['observation']['specification'][field]=value; self.rejected(group,primary)
        group, primary = fixture(); group['packets'][1]['observation']['stimuli'][0]['time']+=.1; self.rejected(group,primary)

    def test_unknown_waveform_and_false_completion_are_rejected(self):
        group, primary = fixture(); group['packets'][1]['observation']['complete']=False; self.rejected(group,primary)
        group, primary = fixture(); primary['native-1.csv']=primary['native-1.csv'].replace(b',1,2,2',b',0,2,2',1)
        group['traces'][1]['sha256']=hashlib.sha256(primary['native-1.csv']).hexdigest(); self.rejected(group,primary)

    def test_file_adapter_refuses_parent_paths_and_malformed_records(self):
        with tempfile.TemporaryDirectory() as temp:
            group, primary = fixture(); path=Path(temp)/'group.json'
            for name,raw in primary.items():(path.parent/name).write_bytes(raw)
            path.write_text(json.dumps(group),encoding='utf-8'); self.assertTrue(audit_matched_omission_file(path)['complete_group'])
            group['traces'][0]['path']='../escape.csv'; path.write_text(json.dumps(group),encoding='utf-8')
            with self.assertRaises(EvidenceError):audit_matched_omission_file(path)
            group['traces']=[None]; path.write_text(json.dumps(group),encoding='utf-8')
            with self.assertRaises(EvidenceError):audit_matched_omission_file(path)
