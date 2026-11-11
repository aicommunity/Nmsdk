"""Controlled portable witnesses; numerical checks run on workers only."""
from copy import deepcopy
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from .test_matched_omission_evidence import fixture as legacy_fixture, branch_fixture
from ..matched_omission_portable import (ATTESTATION, CANONICAL_ENCODING, KIND, MAXIMUM, METHOD,
    audit_portable_matched_evidence, audit_portable_matched_file)
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError


def fixture(*, shared=False, branch=False, input_id=None):
    old, primary = branch_fixture() if branch else legacy_fixture(shared=shared)
    source = [.1, .5]; source_hash = canonical_model_sha256(source)
    first = old['packets'][0]; actual = first['observation']['specification']; prepared = first['prepared']
    spec = dict(schema_version=1, run_id=actual['run_id'], group_id=old['group_id'], sample_id=actual['sample_id'],
        protocol_revision=prepared['protocol_revision'], pattern_hash=source_hash,
        input_id=prepared['input_id'] if input_id is None else input_id,
        base_model_revision=prepared['base_model_revision'], effective_model_revision=prepared['effective_model_revision'],
        reset_binding=old['reset_binding'], model_instance_binding=old['model_instance_binding'],
        model_epoch=prepared['model_epoch'], assigned_input=old['assigned_input'], channel=old['assigned_channel'],
        routing=prepared['routing'], stimulus_ids=['pulse0','pulse1'], physical_channel_paths=old['physical_channel_paths'],
        stimulus_profile=deepcopy(actual['stimulus_profile']), duration=1.2, minimum_amplitude=.5)
    policy = dict(old['policy'], schema_version=1, maximum_samples=13, maximum_total_samples=52, maximum_native_probes=4)
    records = []
    for index, (packet, trace) in enumerate(zip(old['packets'], old['traces'])):
        mask = trace['presented_ordinals']; omitted = None if index in (0,3) else index-1
        presented = source if omitted is None else [.6] if omitted == 0 else [.1]
        pattern = canonical_model_sha256(presented)
        packet['prepared']['input_id'] = spec['input_id']
        for s in (packet['requested_specification'], packet['observation']['specification']):
            s['pattern_hash'] = pattern; s['stimulus_subset']['source_training_pattern_hash'] = source_hash
        name = trace['path']
        records.append(dict(role='full_before' if index == 0 else 'full_after' if index == 3 else 'omit',
            omitted_input=omitted, presented_ordinals=mask, planned_presented_isi=presented,
            applied_presented_isi=list(presented), presented_pattern_sha256=pattern, relative_path=name,
            bytes=len(primary[name]), sha256=trace['sha256'], native_evidence=packet,
            binding=dict(group_id=old['group_id'], source_pattern_hash=source_hash, reset_binding=old['reset_binding'],
                model_instance_binding=old['model_instance_binding'], current_base_revision=spec['base_model_revision'],
                native_completed=True, full_mask_restored=True, physical_channel_paths=spec['physical_channel_paths'])))
    maxima = deepcopy(old['maxima'])
    for peak in maxima:
        peak.update(comparison_first_sample=max(0,peak['first_sample']-1),
                    comparison_last_sample=min(12,peak['last_sample']+1))
    selected = old['selected_full_maximum']
    measured = None if selected is None else {key:maxima[selected][key] for key in MAXIMUM.split()}
    document = dict(schema_version=1, kind=KIND, method=METHOD, complete_group=True, diagnostic_only=True,
        training_certificate_eligible=False, scientific_verdict=None, specification=spec, policy=policy,
        source=dict(planned_isi=source, applied_isi=list(source), planned_sha256=source_hash, applied_sha256=source_hash,
                    canonical_encoding=CANONICAL_ENCODING),
        time_budget=dict(maximum_model_seconds=10., maximum_wall_seconds=60., elapsed_model_seconds=None,
                         elapsed_wall_seconds=None, enforcement_verified=False), traces=records,
        assignment=dict(validity=old['assignment_validity'], reasons=old['assignment_reasons'], maxima=maxima,
                        selected_full_maximum=selected, measured_maximum=measured),
        attestation={key:False for key in ATTESTATION.split()})
    return document, primary


def rehash(record, primary, raw):
    primary[record['relative_path']] = raw
    record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


class PortableMatchedOmissionTest(unittest.TestCase):
    def rejected(self, document, primary):
        with self.assertRaises(EvidenceError): audit_portable_matched_evidence(document, primary)

    def test_complete_classic_witness_recomputed_without_certificate(self):
        document, primary = fixture(); result = audit_portable_matched_evidence(document, primary)
        self.assertEqual(result['assignment_validity'],'valid'); self.assertEqual(result['primary_traces_checked'],4)
        self.assertEqual(result['total_samples_checked'],52)
        self.assertTrue(result['planned_applied_isi_hashes_recomputed']); self.assertTrue(result['sample_probe_budgets_verified'])
        self.assertFalse(result['training_certificate_eligible']); self.assertFalse(result['time_budget_enforcement_independently_verified'])

    def test_branch_input_one_and_nonconventional_input_id_are_bound(self):
        document, primary = fixture(branch=True, input_id='trained-path-right')
        result = audit_portable_matched_evidence(document,primary)
        self.assertEqual(result['selected_full_maximum'],1)
        self.assertFalse(result['actual_event_schedule_derived_from_planned_isi'])

    def test_larger_shared_peak_remains_ambiguous(self):
        document, primary = fixture(shared=True); result = audit_portable_matched_evidence(document,primary)
        self.assertEqual(result['assignment_validity'],'ambiguous'); self.assertIsNone(result['measured_maximum'])

    def test_unknown_schema_kind_and_fields_fail_closed(self):
        for key,value in [('schema_version',2),('kind','native_matched_omission_fixture'),('method','other'),('unknown',0)]:
            document, primary = fixture(); document[key] = value; self.rejected(document,primary)

    def test_changed_planned_or_applied_source_and_hash_is_rejected(self):
        for field in ('planned_isi','applied_isi','planned_sha256','applied_sha256','canonical_encoding'):
            document, primary = fixture(); document['source'][field] = [.2,.4] if field.endswith('_isi') else 'other'
            self.rejected(document,primary)

    def test_presented_isi_or_hash_cannot_be_substituted(self):
        for field in ('planned_presented_isi','applied_presented_isi','presented_pattern_sha256'):
            document, primary = fixture(); document['traces'][1][field] = [.1] if field.endswith('_isi') else 'other'
            self.rejected(document,primary)

    def test_missing_duplicate_reordered_or_extra_primary_is_rejected(self):
        document, primary = fixture(); document['traces'].pop(); self.rejected(document,primary)
        document, primary = fixture(); document['traces'][1]['relative_path'] = document['traces'][0]['relative_path']; self.rejected(document,primary)
        document, primary = fixture(); document['traces'][1:3] = reversed(document['traces'][1:3]); self.rejected(document,primary)
        document, primary = fixture(); primary['extra.csv'] = b''; self.rejected(document,primary)

    def test_each_sample_total_sample_and_native_probe_budget_is_checked(self):
        for key,value in [('maximum_samples',12),('maximum_total_samples',51),('maximum_native_probes',3)]:
            document, primary = fixture(); document['policy'][key] = value; self.rejected(document,primary)

    def test_actual_trial_chronology_must_not_overlap(self):
        document, primary = fixture(); record = document['traces'][1]; packet = record['native_evidence']
        begin = document['traces'][0]['native_evidence']['observation']['specification']['end']
        spec = packet['observation']['specification']; spec.update(begin=begin,end=begin+1.2)
        event = packet['observation']['stimuli'][0]; event.update(time=begin+.6,relative_to_trial_start=(begin+.6)-begin)
        packet['observation']['first_stimulus_time'] = event['time']
        rows = list(csv.reader(io.StringIO(primary[record['relative_path']].decode())))
        for frame,row in enumerate(rows[1:]):row[0] = format(begin+frame/10,'.17g')
        raw = ('\n'.join(','.join(row) for row in rows)+'\n').encode(); rehash(record,primary,raw)
        with self.assertRaisesRegex(EvidenceError,'portable_native_trials_overlap_or_reorder'):
            audit_portable_matched_evidence(document,primary)

    def test_observed_model_span_cannot_exceed_declared_budget(self):
        document, primary = fixture(); document['time_budget']['maximum_model_seconds'] = 7.
        self.rejected(document,primary)

    def test_elapsed_time_or_native_attestations_cannot_be_invented(self):
        for field in ('elapsed_model_seconds','elapsed_wall_seconds','enforcement_verified'):
            document, primary = fixture(); document['time_budget'][field] = True if field == 'enforcement_verified' else 1.
            self.rejected(document,primary)
        for field in ATTESTATION.split():
            document, primary = fixture(); document['attestation'][field] = True; self.rejected(document,primary)

    def test_boolean_and_float_identities_are_not_integer_indices(self):
        for value in (True,0.):
            document, primary = fixture(); document['specification']['assigned_input'] = value; self.rejected(document,primary)
        document, primary = fixture(); document['schema_version'] = True; self.rejected(document,primary)
        document, primary = fixture(); document['policy']['maximum_samples'] = 13.; self.rejected(document,primary)

    def test_comparison_range_support_and_selected_maximum_are_recomputed(self):
        for field in ('comparison_first_sample','supported_inputs','amplitude'):
            document, primary = fixture(); document['assignment']['maxima'][0][field] = [1] if field == 'supported_inputs' else 0
            self.rejected(document,primary)
        document, primary = fixture(); document['assignment']['measured_maximum']['time'] = .4; self.rejected(document,primary)

    def test_changed_model_epoch_selector_or_native_event_is_rejected(self):
        for field,value in [('model_epoch',1),('base_model_revision','other'),('selected_input_index',0)]:
            document, primary = fixture(); document['traces'][1]['native_evidence']['prepared'][field] = value
            self.rejected(document,primary)
        document, primary = fixture(); document['traces'][1]['native_evidence']['observation']['stimuli'][0]['time'] += .1
        self.rejected(document,primary)

    def test_declared_profile_cannot_alias_boolean_and_numeric_values(self):
        document, primary = fixture(); document['specification']['stimulus_profile']['frequency_deviation'] = False
        self.rejected(document,primary)
        document, primary = fixture(); document['specification']['stimulus_profile']['use_pattern_output'] = 0
        self.rejected(document,primary)

    def test_native_completion_and_full_mask_restoration_are_required(self):
        for field in ('native_completed','full_mask_restored'):
            document, primary = fixture(); document['traces'][1]['binding'][field] = False; self.rejected(document,primary)
        document, primary = fixture(); document['complete_group'] = False; self.rejected(document,primary)

    def test_primary_must_match_canonical_csv_even_after_rehash(self):
        document, primary = fixture(); record = document['traces'][0]
        raw = primary[record['relative_path']].replace(b'0,0,2,2',b'0.0,0,2,2',1); rehash(record,primary,raw)
        self.rejected(document,primary)

    def test_nonfinite_source_or_primary_cannot_be_hidden(self):
        document, primary = fixture(); document['source']['planned_isi'][0] = float('nan'); self.rejected(document,primary)
        document, primary = fixture(); record = document['traces'][0]
        raw = primary[record['relative_path']].replace(b'0,0,2,2',b'0,0,NaN,2',1); rehash(record,primary,raw)
        self.rejected(document,primary)

    def test_file_reader_rejects_missing_escaping_and_duplicate_key_primary(self):
        with tempfile.TemporaryDirectory() as folder:
            document, primary = fixture(); path = Path(folder)/'evidence.json'
            for name,raw in primary.items():(path.parent/name).write_bytes(raw)
            path.write_text(json.dumps(document)); self.assertTrue(audit_portable_matched_file(path)['complete_group'])
            document['traces'][0]['relative_path'] = '../escape.csv'; path.write_text(json.dumps(document))
            with self.assertRaises(EvidenceError):audit_portable_matched_file(path)
            document, primary = fixture(); raw = json.dumps(document).replace('"schema_version": 1','"schema_version": 1, "schema_version": 1',1)
            path.write_text(raw)
            with self.assertRaises(EvidenceError):audit_portable_matched_file(path)

    def test_verdict_and_training_eligibility_never_follow_process_success(self):
        for field,value in [('diagnostic_only',False),('training_certificate_eligible',True),('scientific_verdict','PASS')]:
            document, primary = fixture(); document[field] = value; self.rejected(document,primary)

    def test_complete_missing_response_remains_a_negative_operational_outcome(self):
        document, primary = fixture()
        for record in document['traces']:
            rows = list(csv.reader(io.StringIO(primary[record['relative_path']].decode())))
            for row in rows[1:]:row[2:] = ['2']*(len(row)-2)
            rehash(record,primary,('\n'.join(','.join(row) for row in rows)+'\n').encode())
        document['assignment'].update(validity='missing',reasons=['no_exclusive_assigned_full_maximum'],
                                      maxima=[],selected_full_maximum=None,measured_maximum=None)
        result = audit_portable_matched_evidence(document,primary)
        self.assertEqual(result['assignment_validity'],'missing'); self.assertFalse(result['training_certificate_eligible'])

    def test_complete_clipped_response_does_not_become_a_valid_peak(self):
        document, primary = fixture()
        for index in (0,2,3):
            record=document['traces'][index];rows=list(csv.reader(io.StringIO(primary[record['relative_path']].decode())))
            rows[-1][2]='10';rehash(record,primary,('\n'.join(','.join(row) for row in rows)+'\n').encode())
        a = document['assignment'];a.update(validity='clipped',reasons=['possibly_assigned_maximum_is_clipped'],
                                           selected_full_maximum=None,measured_maximum=None)
        a['maxima'].append(dict(first_sample=12,last_sample=12,amplitude=8.,raw_potential=10.,time=1.2,plateau_end=1.2,
            comparison_first_sample=11,comparison_last_sample=12,supported_inputs=[0],
            influence_by_input=['supported','not_supported'],unknown=False,precedes_assigned_stimulus=False,clipped=True))
        result=audit_portable_matched_evidence(document,primary)
        self.assertEqual(result['assignment_validity'],'clipped');self.assertFalse(result['training_certificate_eligible'])

    def test_complete_nonrepeatable_group_retains_its_failure(self):
        document, primary = fixture();record=document['traces'][3]
        rows=list(csv.reader(io.StringIO(primary[record['relative_path']].decode())))
        rows[4][2]='5.5';rehash(record,primary,('\n'.join(','.join(row) for row in rows)+'\n').encode())
        document['assignment'].update(validity='non_repeatable',reasons=['full_response_not_repeatable'],
                                      maxima=[],selected_full_maximum=None,measured_maximum=None)
        result=audit_portable_matched_evidence(document,primary)
        self.assertEqual(result['assignment_validity'],'non_repeatable');self.assertFalse(result['training_certificate_eligible'])
