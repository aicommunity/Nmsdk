"""Runtime2 and whole archive2 joining controls; synthetic DATA, not native.

No mocks in the whole dispatcher/CLI controls. Run only on workers. The
artificial source fixture cannot demonstrate Rdk execution or service ownership.
"""
import base64
import contextlib
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from ..__main__ import main
from ..candidate_window_runtime_plan import audit_candidate_window_runtime_plan
from ..candidate_window_archive_evidence import audit_candidate_window_archive
from ..candidate_window_contract import recipe_content, instance_content, expected_measurement_id
from ..composite_measurement_evidence import audit_composite_measurement_archive
from ..composite_measurement_contract import expected_artifact_document_id
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from .synthetic_candidate_archive2 import fixture, source_data, runtime2


def invoke(*args):
    output,error=io.StringIO(),io.StringIO()
    with contextlib.redirect_stdout(output),contextlib.redirect_stderr(error):code=main(['analyze',*map(str,args)])
    return code,output.getvalue(),error.getvalue()


def write_case(root,archive,config,runtime,primary):
    (root/'composite-measurements').mkdir(parents=True)
    for name,value in [('initial-configuration.json',config),('runtime-plan.json',runtime),('composite-measurements/index.json',archive)]:
        (root/name).write_text(json.dumps(value,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    for name,raw in primary.items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)


def resign(archive):
    """Rehash public claims only; this is deliberately not semantic validation."""
    for record in archive['records']:
        record['candidate_witness_id']=digest(record['candidate_binding'])
        proposal=record['window_proposal']
        if proposal is not None:
            proposal['candidate_binding']=record['candidate_witness_id']
            # The caller may intentionally keep a FOREIGN reference proof to
            # test that a self-consistent public hash is not seed authority.
            proposal['window_recipe_id']=digest(recipe_content(proposal));proposal['measurement_instance_id']=digest(instance_content(proposal))
        if record['measurement'] is not None:record['measurement']['semantic_proof_id']=expected_measurement_id(record,archive['protocol'])
    archive['artifact_document_sha256']=expected_artifact_document_id(archive)


class CandidateWindowRuntime2DeclarationTest(unittest.TestCase):
    def make(self):
        config,p,source,binding=source_data();return runtime2(config,p,binding['model_identity']['sha256']),config,p

    def test_real_runtime_shape_binds_full_protocol_and_is_not_cold7(self):
        plan,config,p=self.make();result=audit_candidate_window_runtime_plan(plan,config,p)
        self.assertEqual(result['runtime_plan_schema_version'],2);self.assertFalse(result['current_search_derived_from_cold_configuration'])
        self.assertFalse(result['live_authority_restored']);self.assertFalse(result['training_certificate_verified'])

    def test_warm_current_model_epoch_search_tolerances_and_caps_may_differ_initial_cold(self):
        plan,config,p=self.make();plan.update(run_id='later/session/2',initial_model_revision='9'*64,initial_model_epoch=7)
        plan['search'].update(maximum_probes=32,n0_candidate_repeats=2);plan['search']['tolerances']['sync']=.04
        plan['composite_measurement']['maximum_total_primary_bytes']*=2
        self.assertEqual(audit_candidate_window_runtime_plan(plan,config,p)['run_id'],'later/session/2')
        self.assertEqual(config['search']['tolerances']['sync'],.02)

    def test_runtime_normalization_is_not_silently_copied_from_initial_model(self):
        plan,config,p=self.make();plan['search']['normalization']='N1'
        self.assertEqual(audit_candidate_window_runtime_plan(plan,config,p)['normalization'],'N1')
        plan['search']['n0_candidate_repeats']=2
        with self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,config,p)

    def test_cold7_clone_runtime1_and_scope_marker_are_not_runtime2(self):
        plan,config,p=self.make()
        old=deepcopy(plan);old.pop('protocol_binding');old['schema_version']=1
        for bad in (config,old,dict(runtime_plan2_exported=False)):
            with self.subTest(keys=list(bad)),self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(bad,config,p)

    def test_wrong_protocol_or_candidate_policy_binding_rejects(self):
        plan,config,p=self.make();plan['protocol_binding']='0'*64
        with self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,config,p)
        plan,config,p=self.make();plan['composite_measurement']['candidate_window_policy']['inputs'][0]['base_left_guard_frames']+=1
        with self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,config,p)

    def test_unknown_fields_and_boolean_fractional_or_nonfinite_numbers_fail(self):
        for field,value in [('schema_version',True),('initial_model_epoch',.5),('maximum_reference_probes','2'),
            ('maximum_wall_seconds',float('inf')),('record_capacitance_history',0),('future',1)]:
            plan,config,p=self.make();plan[field]=value
            with self.subTest(field=field),self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,config,p)

    def test_search_bounds_and_tolerances_remain_strict_typed_declarations(self):
        for field,value in [('maximum_length',2**31),('minimum_synapses',True),('maximum_synapses',129),('minimum_resistance',0.)]:
            plan,config,p=self.make();plan['search']['bounds'][0][field]=value
            with self.subTest(field=field),self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,config,p)
        plan,config,p=self.make();plan['search']['tolerances']['sync']=-.02
        with self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,config,p)

    def test_reference_raw_sample_and_group_time_budgets_bind_actual_plan(self):
        for change in ('refs','raw','samples','group'):
            plan,config,p=self.make()
            if change=='refs':plan['maximum_reference_probes']=1
            elif change=='raw':plan['composite_measurement']['attempt_limits']['maximum_native_probes']=3
            elif change=='samples':plan['composite_measurement']['attempt_limits']['maximum_total_samples']=51
            else:plan['composite_measurement']['maximum_group_wall_seconds']=1001.
            with self.subTest(change=change),self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,config,p)

    def test_C_search_declaration_preserves_false_record_flag_without_inventing_C0(self):
        plan,config,p=self.make();plan['search']['capacitance_search']=dict(enumeration='round_robin_absolute_C0_v1',
            minimum_scale=.9,maximum_scale=1.1,subdivision_depth=1,maximum_contexts=4,maximum_membranes=8,maximum_cursor_elements=8192)
        result=audit_candidate_window_runtime_plan(plan,config,p)
        self.assertFalse(plan['record_capacitance_history']);self.assertFalse(result['native_execution_verified'])
        plan['search']['capacitance_search']['maximum_cursor_elements']=1
        with self.assertRaisesRegex(EvidenceError,'C_cursor_budget'):audit_candidate_window_runtime_plan(plan,config,p)

    def test_C_region_and_context_count_limits_are_checked(self):
        plan,config,p=self.make();plan['search']['capacitance_search']=dict(enumeration='round_robin_absolute_C0_v1',
            minimum_scale=.9,maximum_scale=1.1,subdivision_depth=1,maximum_contexts=4,maximum_membranes=1,maximum_cursor_elements=8192)
        with self.assertRaisesRegex(EvidenceError,'C_region_budget'):audit_candidate_window_runtime_plan(plan,config,p)
        plan['search']['capacitance_search']['maximum_membranes']=8;plan['search']['capacitance_search']['maximum_contexts']=5
        with self.assertRaises(EvidenceError):audit_candidate_window_runtime_plan(plan,config,p)
        # The shared owner counts ONE baseline plus seed inventory, whose
        # current==unit==minimum==maximum values deduplicate to ONE seed.
        # Length inventory is capped by maximum_candidates_per_input:
        # min(4,8)=4 lengths +128 counts=132; two contexts need 264 slots.
        self.assertEqual(plan['search']['maximum_candidates_per_input'],4)
        self.assertEqual(tuple(plan['search']['bounds'][0][k] for k in
            ('minimum_length','maximum_length','minimum_synapses','maximum_synapses')),(1,8,1,128))
        policy=plan['search']['capacitance_search'];policy.update(minimum_scale=1.,maximum_scale=1.,maximum_contexts=4,maximum_cursor_elements=264)
        audit_candidate_window_runtime_plan(plan,config,p)
        policy['maximum_cursor_elements']=263
        with self.assertRaisesRegex(EvidenceError,'C_cursor_budget'):audit_candidate_window_runtime_plan(plan,config,p)


class CandidateWindowWholeArchive2SyntheticTest(unittest.TestCase):
    def audit(self,archive,config,runtime,primary):
        return audit_composite_measurement_archive(archive,config,runtime_plan=runtime,external_resolver=primary)

    def test_unmocked_whole_archive2_dispatch_replays_refs_proposals_primary_and_runtime2(self):
        args=fixture();result=self.audit(*args)
        self.assertEqual(result['reader_version'],2);self.assertEqual(len(result['groups']),5)
        self.assertTrue(result['reference_set_recomputed']);self.assertTrue(result['current_runtime_plan']['runtime_plan_validated'])
        self.assertEqual(sum(r['measured'] for r in result['groups']),5)
        self.assertEqual(sum(r.get('proposal_recomputed',False) for r in result['groups']),3)
        self.assertTrue(all(r['native_closure_recomputed'] and r['geometry_recomputed'] for r in result['groups']))
        self.assertFalse(result['native_execution_verified']);self.assertFalse(result['live_authority_restored'])
        self.assertFalse(result['training_certificate_verified']);self.assertIsNone(result['scientific_verdict'])

    def test_unmocked_public_CLI_reads_original_documents_and_all_external_primary(self):
        archive,config,runtime,primary=fixture()
        with tempfile.TemporaryDirectory() as directory:
            case=Path(directory)/'synthetic-DATA-only';write_case(case,archive,config,runtime,primary)
            output=Path(directory)/'audit.json';code,text,error=invoke(case,'--format','native-composite-measurements','--output',output)
            self.assertEqual(code,0,error);self.assertFalse(text);report=json.loads(output.read_text(encoding='utf-8'))['analysis']
            self.assertEqual(report['archive_schema_version'],2);self.assertEqual(report['coverage']['measured_groups'],5)
            self.assertEqual(len(report['measurements']),5);self.assertFalse(report['training_certificate_verified'])

    def test_missing_runtime_original_is_not_filled_from_cold_or_index(self):
        archive,config,runtime,primary=fixture()
        with tempfile.TemporaryDirectory() as directory:
            case=Path(directory)/'synthetic-DATA-only';write_case(case,archive,config,runtime,primary);(case/'runtime-plan.json').unlink()
            code,text,error=invoke(case,'--format','native-composite-measurements')
            self.assertEqual(code,2);self.assertFalse(text);self.assertEqual(json.loads(error)['validity'],'invalid')

    def test_missing_or_changed_mirror_cannot_fall_back_to_embedded_primary(self):
        archive,config,runtime,primary=fixture();name=next(iter(primary))
        for missing in (True,False):
            changed=dict(primary)
            if missing:changed.pop(name)
            else:changed[name]+=b'corrupt'
            with self.subTest(missing=missing),self.assertRaises(EvidenceError):self.audit(archive,config,runtime,changed)

    def test_rehashed_foreign_reference_proof_does_not_mint_seed_authority(self):
        archive,config,runtime,primary=fixture();record=archive['records'][2]
        record['window_proposal']['reference_proof_id']='0'*64;resign(archive)
        with self.assertRaisesRegex(EvidenceError,'recomputed_value_changed'):self.audit(archive,config,runtime,primary)

    def test_rehashed_physical_Rs_claim_is_checked_against_full_graph(self):
        archive,config,runtime,primary=fixture()
        for record in archive['records']:record['candidate_binding']['physical_readback']['parameters'][0]['resistance']=9.
        resign(archive)
        with self.assertRaisesRegex(EvidenceError,'actual_bank_control_knob'):self.audit(archive,config,runtime,primary)

    def test_rehashed_changed_candidate_window_is_not_prediction_as_measurement(self):
        archive,config,runtime,primary=fixture();record=archive['records'][2];claim=record['window_proposal']
        for field in ('first_frame','last_frame'):
            claim['computation'][field]+=1;record['method_specification']['candidate_frame'][field]+=1
        resign(archive)
        with self.assertRaises(EvidenceError):self.audit(archive,config,runtime,primary)

    def test_warm_empty_attempt_retains_original_references_and_own_history_budgets(self):
        archive,config,runtime,primary=fixture();archive['current_attempt_id']='synthetic/session/2';archive['final_group_ids']=[]
        archive['counters']['attempt']=dict(logical_groups=0,native_probes=0,sampled_frames=0)
        archive['maximum_total_primary_bytes']=20000000
        runtime.update(run_id=archive['current_attempt_id'],initial_model_revision='9'*64,initial_model_epoch=7)
        runtime['search']['tolerances']['sync']=.04;runtime['composite_measurement']['maximum_total_primary_bytes']=20000000
        resign(archive);result=self.audit(archive,config,runtime,primary)
        self.assertEqual(result['current_runtime_plan']['run_id'],'synthetic/session/2');self.assertTrue(result['reference_set_recomputed'])
        self.assertEqual(archive['source_binding']['initial_epoch'],0);self.assertFalse(result['live_authority_restored'])

    def test_rehashed_historical_prefix_cap_cannot_hide_behind_higher_warm_cap(self):
        archive,config,runtime,primary=fixture();archive['current_attempt_id']='synthetic/session/2';archive['final_group_ids']=[]
        archive['counters']['attempt']=dict(logical_groups=0,native_probes=0,sampled_frames=0);archive['maximum_total_primary_bytes']=20000000
        runtime['run_id']=archive['current_attempt_id'];runtime['composite_measurement']['maximum_total_primary_bytes']=20000000
        cap=max(r['counters']['primary_bytes'] for r in archive['records'])+1
        for record in archive['records']:record['budgets']['maximum_total_primary_bytes']=cap
        resign(archive)
        with self.assertRaisesRegex(EvidenceError,'historical_primary_budget'):self.audit(archive,config,runtime,primary)

    def test_rehashed_raw_trace_changes_are_detected_independently_of_peak_metadata(self):
        archive,config,runtime,primary=fixture();record=archive['records'][0];trace=record['native_group']['traces'][0]
        name=trace['relative_path'];raw=primary[name].replace(b',5\n',b',6\n',1);self.assertNotEqual(raw,primary[name])
        primary[name]=raw;sha=hashlib.sha256(raw).hexdigest();trace.update(bytes=len(raw),sha256=sha)
        record['raw_trials'][0]['primary_ref'].update(bytes=len(raw),sha256=sha)
        refs={t['primary_ref']['sha256']:primary[t['primary_ref']['relative_path']] for r in archive['records'] for t in r['raw_trials']}
        archive['primary_blobs']={s:dict(bytes=len(b),base64=base64.b64encode(b).decode()) for s,b in refs.items()};resign(archive)
        with self.assertRaises(EvidenceError):self.audit(archive,config,runtime,primary)


if __name__=='__main__':unittest.main()
