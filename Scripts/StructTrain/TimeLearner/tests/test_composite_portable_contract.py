"""Wire/hash and nonpromotion controls; no synthetic native training PASS."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from ..composite_measurement_contract import (integral_number_view,
    expected_semantic_measurement_id, expected_artifact_document_id)
from ..composite_package_evidence import audit_composite_package
from ..composite_execution_evidence import audit_composite_execution
from ..learned_evidence import load_case, audit_learned_state
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from .test_composite_configuration import configuration, protocol


def hash_payload():
    """Hash-format fixture, deliberately not an admissible native record."""
    return dict(purpose='search', source_origin='source', candidate_witness_id='candidate', live_attempt_binding='lease',
        logical_request=dict(trial_id='run/trial'), group_id='group',
        budgets=dict(attempt_limits=dict(maximum_groups=8, maximum_native_probes=32, maximum_total_samples=1000,
            maximum_model_seconds=3., maximum_wall_seconds=10.), maximum_group_model_seconds=.5, maximum_group_wall_seconds=2.),
        native_group=dict(traces=[dict(native_evidence=dict(trial_id='raw'), sha256='0'*64, relative_path='old/a.csv')]),
        measurement=dict(actual_peak=dict(raw_potential=.1, time=.02, plateau_end=.02)))


class CompositePortableContractTest(unittest.TestCase):
    def test_retained_dataset_readback_must_match_isi_source_physics_and_dimensions(self):
        from ..composite_source_evidence import audit_dataset_source
        import struct
        config=configuration();profile=config['stimulus_profile'];isi=config['model']['initial_isi']
        def prop(kind, value, **extra): return dict(binding=False, data=dict(type=kind,value=value,**extra))
        nodes={'$':dict(**{'class':config['model']['dataset_class']},parameters=dict(
            MatrixData=prop('binary64_matrix',[[struct.pack('>d',v).hex()] for v in isi],rows='2',columns='1'),
            NumSamples=prop('signed_integer','1'),NumFeatures=prop('signed_integer','1'),MaxSpikesPerFeature=prop('signed_integer','2'))),
            '$.Generator1':dict(**{'class':profile['generator_class']},frequency_hz='2000',parameters={})}
        for name,key in [('Amplitude','amplitude'),('PulseLength','pulse_length'),('FrequencyDeviation','frequency_deviation')]:
            nodes['$.Generator1']['parameters'][name]=prop('binary64',struct.pack('>d',profile[key]).hex())
        for name,key in [('UseTransitSignal','use_transit_signal'),('UsePatternOutput','use_pattern_output')]:
            nodes['$.Generator1']['parameters'][name]=prop('boolean',profile[key])
        audit_dataset_source(nodes,config['model'],profile,isi)
        for node,name,field,value in [('$','MatrixData','rows','3'),('$','MatrixData','value',[['0000000000000000']]*2),
                ('$','NumFeatures','value','2'),('$.Generator1','Amplitude','value','0000000000000000'),
                ('$.Generator1','UseTransitSignal','value',True)]:
            bad=deepcopy(nodes);bad[node]['parameters'][name]['data'][field]=value
            with self.subTest(name=name,field=field),self.assertRaises(EvidenceError):
                audit_dataset_source(bad,config['model'],profile,isi)
        bad=deepcopy(nodes);bad['$.Generator1']['parameters']['Amplitude']['binding']=True
        with self.assertRaises(EvidenceError):audit_dataset_source(bad,config['model'],profile,isi)

    def test_purpose_namespaces_bind_logical_trial_epoch_group_and_attempt(self):
        from ..composite_measurement_contract import validate_logical_namespace
        for purpose,run,trial in [('search','run/session/2','run/session/2/search/3'),
                ('reference','run/session/2/capture/0','run/session/2/capture/0/1'),
                ('final','run/session/2/final/1','run/session/2/final/1/verify/4/2')]:
            record=dict(purpose=purpose,attempt_id='run/session/2',group_id=trial+'/composite/0',
                        logical_request=dict(run_id=run,trial_id=trial,model_epoch=4))
            validate_logical_namespace(record)
            for field in ('attempt_id','group_id'):
                bad=deepcopy(record);bad[field]+='x'
                with self.assertRaises(EvidenceError):validate_logical_namespace(bad)
            bad=deepcopy(record);bad['logical_request']['trial_id']+='x'
            with self.assertRaises(EvidenceError):validate_logical_namespace(bad)
        record['logical_request']['model_epoch']=3
        with self.assertRaises(EvidenceError):validate_logical_namespace(record)

    def test_private_numeric_view_preserves_semantics_and_does_not_mutate_input(self):
        original = dict(schema_version=1., indices=[0., 2.], bool_value=True, amplitude=.125)
        before = deepcopy(original); view = integral_number_view(original)
        self.assertEqual(original, before); self.assertEqual(digest(view), digest(original))
        self.assertIs(type(view['schema_version']), int); self.assertIs(view['bool_value'], True)

    def test_nonfinite_private_view_is_rejected_before_hashing(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=value), self.assertRaises((EvidenceError, ValueError)):
                integral_number_view(dict(value=value))

    def test_csv_path_rename_changes_document_identity_but_not_measurement_proof(self):
        spec = protocol(configuration()); record = hash_payload(); renamed = deepcopy(record)
        renamed['native_group']['traces'][0]['relative_path'] = 'new/а.csv'
        self.assertEqual(expected_semantic_measurement_id(record, spec), expected_semantic_measurement_id(renamed, spec))
        self.assertNotEqual(expected_artifact_document_id(record), expected_artifact_document_id(renamed))

    def test_measurement_identity_retains_attempt_and_actual_bytes(self):
        spec = protocol(configuration()); record = hash_payload(); original = expected_semantic_measurement_id(record, spec)
        for field in ('group_id', 'live_attempt_binding', 'source_origin', 'candidate_witness_id'):
            changed = deepcopy(record); changed[field] += '-changed'
            self.assertNotEqual(original, expected_semantic_measurement_id(changed, spec))
        changed = deepcopy(record); changed['native_group']['traces'][0]['sha256'] = '1'*64
        self.assertNotEqual(original, expected_semantic_measurement_id(changed, spec))

    def test_hash_payload_is_not_promoted_to_a_training_package(self):
        with self.assertRaises(EvidenceError): audit_composite_package(hash_payload())

    def test_schema_five_loader_never_uses_old_flat_trial_globs_or_invents_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root/'train_learned_state.json'
            path.write_text(json.dumps(dict(schema_version=5, kind='timelearner_completed_state')), encoding='utf-8')
            (root/'train_state_trial_1.json').write_text('corrupt legacy flat file', encoding='utf-8')
            case = load_case(path)
            self.assertIsNone(case[1]); self.assertEqual(case[2:], ({}, {}))
            with self.assertRaises(EvidenceError): audit_learned_state(*case)

    def test_schema_five_does_not_ignore_supplied_legacy_primary_overlay(self):
        with self.assertRaisesRegex(EvidenceError, 'legacy_primary_overlay'):
            audit_learned_state(dict(schema_version=5, kind='timelearner_completed_state'), None, {'x':{}}, {})

    def test_preflight_envelope_accepts_known_zero_callbacks_but_rejects_invented_archive(self):
        execution = dict(schema_version=3, base_schema_version=1, measurement_method='declared-window-basin-necessity-v1',
            measurement_archive=None, source_origin=None, model_semantic_hash='actual', model_revision='actual',
            composite_counters=dict(attempt=dict(logical_groups=0, native_probes=0, sampled_frames=0),
                archive=dict(groups=0, native_probes=0, sampled_frames=0, primary_bytes=0),
                execution=dict(native_trials=0, sampled_frames=0)))
        result = audit_composite_execution(execution, '.', set(), mode='preflight', base_version=1)
        self.assertFalse(result['owned_archive_present']); self.assertIsNone(result['evaluation_verdict'])
        numeric = deepcopy(execution); numeric['schema_version'] = 3.; numeric['base_schema_version'] = 1.
        self.assertEqual(result, audit_composite_execution(numeric, '.', set(), mode='preflight', base_version=1))
        numeric['schema_version'] = True
        with self.assertRaises(EvidenceError): audit_composite_execution(numeric, '.', set(), mode='preflight', base_version=1)
        execution['composite_counters']['execution']['native_trials'] = 1
        with self.assertRaises(EvidenceError): audit_composite_execution(execution, '.', set(), mode='preflight', base_version=1)

    def test_warm_boundary_request_binds_current_runtime_not_immutable_initial_run(self):
        from ..finalization_boundary_evidence import audit_boundary
        def signed(value): return {**value, 'sha256': digest(value)}
        parameters = dict(IsNeedToTrain=True, CalculateMode=1, ControllerVersion=2,
            CalibrateLTZThresholdFraction=.5, AutoCalibrateFixedLTZThreshold=False,
            EnablePostTrainTuning=False, EnablePostTrainMidThreshold=False)
        bindings = {key:dict(connected=False, external_data_source=False, sources=[]) for key in parameters}
        request = signed(dict(kind='native_training_request_intent', schema_version=1,
            controls=dict(parameters=parameters, bindings=bindings), run_id='warm/session/2', session_attempt=2,
            model_epoch=0, initial_model_revision='unattested-test-binding', protocol_revision='protocol',
            pattern_hash='pattern', started_model_time=0., dynamic_checkpoint=False, calibrated=False, evaluation_verdict=None))
        solo = signed(dict(kind='timelearner_stopped_state', schema_version=5, training_outcome='external_stop',
            certificate=None, session_attempt=2, configuration=dict(run_id='initial/session/1', model=dict(branch=False)),
            runtime_plan=dict(run_id='warm/session/2'), protocol=dict(revision='protocol', pattern_hash='pattern')))
        boundary = signed(dict(kind='timelearner_finalization_boundary', schema_version=2, source_solo=solo,
            dynamic_checkpoint=False, mid_probe_resume_supported=False, recognition_success=None,
            training_outcome='external_stop', diagnostic_only=True, controls=dict(parameters=parameters, bindings=bindings),
            training_request=request, phase_requests=dict(target_reference=False, post_tune=False,
                post_train_mid=False, legacy_parallel_peak=False)))
        result = audit_boundary(boundary)
        self.assertFalse(result['training_evidence_checked']); self.assertIsNone(result['scientific_verdict'])
        bad = deepcopy(boundary); bad['training_request']['run_id'] = 'initial/session/1'
        bad['training_request'] = signed({k:v for k,v in bad['training_request'].items() if k != 'sha256'})
        bad = signed({k:v for k,v in bad.items() if k != 'sha256'})
        with self.assertRaises(EvidenceError): audit_boundary(bad)

    def test_cold_initial_declaration_retains_original_run_while_runtime_owns_session(self):
        from ..composite_execution_evidence import audit_initial_planning_configuration
        config=configuration();config['model']['inputs'][0]['resistance']=None
        actual=[dict(length=1,synapses=1,resistance=2.),dict(length=1,synapses=1,resistance=1.)]
        initial=dict(parameters=actual,identity=dict(wire_fixture='not-native-attestation'))
        declaration=deepcopy(config);declaration['model']['inputs'][0]['resistance']=2.
        package=dict(configuration=declaration,runtime_plan=dict(run_id=config['run_id']+'/session/1'),
            measurement_archive=dict(source_binding=dict(initial_model=deepcopy(initial['identity']))))
        audit_initial_planning_configuration(package,dict(configuration=config),initial)
        for field in ('configuration','runtime_plan'):
            bad=deepcopy(package)
            bad[field]['run_id']=config['run_id']+'/session/1' if field=='configuration' else config['run_id']
            with self.subTest(field=field),self.assertRaises(EvidenceError):
                audit_initial_planning_configuration(bad,dict(configuration=config),initial)

    def test_start_failure_receipt_keeps_unknown_accounting_and_no_model_package(self):
        from ..composite_execution_evidence import audit_composite_start_failure
        # Wire-only refusal fixture; no trained graph or native execution claim.
        job=dict(schema_version=1,configuration=configuration())
        revision='1'*64
        execution=dict(schema_version=3,base_schema_version=1,measurement_method='declared-window-basin-necessity-v1',
            execution='training_start_failed',completed_boundary=False,package_path=None,package_sha256=None,
            attempt_id=job['configuration']['run_id'],training_outcome='invalid_model',model_revision=revision,
            model_semantic_hash=revision,measurement_archive=None,source_origin=None,
            composite_counters=dict(attempt=None,archive=None,execution=dict(native_trials=2,sampled_frames=20)))
        failure=dict(kind='timelearner_native_training_start_failure',schema_version=1,outcome='invalid_model',
            reason='wire-only-owned-start-refusal',model_revision=revision,dynamic_checkpoint=False,source_origin=None,
            measurement_archive=None,certificate=None,contains_evaluation_verdict=False)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'training-start-failure.json'
            def save(value):path.write_text(json.dumps({**value,'sha256':digest(value)}),encoding='utf-8')
            save(failure);names={'job.json','initial-state.json','training-start-failure.json'}
            audit=audit_composite_start_failure(execution,directory,names,job)
            self.assertFalse(audit['owned_source_captured']);self.assertFalse(audit['completed_boundary'])
            self.assertFalse(audit['native_execution_verified']);self.assertIsNone(audit['evaluation_verdict'])
            for field,value in [('certificate',{}),('outcome','exact'),('reason',''),('dynamic_checkpoint',True),
                    ('model_revision','2'*64),('contains_evaluation_verdict',True),('schema_version',True)]:
                save({**failure,field:value})
                with self.subTest(field=field),self.assertRaises(EvidenceError):
                    audit_composite_start_failure(execution,directory,names,job)
            save(failure)
            for field,value in [('package_path','train_stopped_state.json'),('completed_boundary',True),
                    ('base_schema_version',2),('model_semantic_hash','2'*64),('execution','completed')]:
                with self.subTest(field=field),self.assertRaises(EvidenceError):
                    audit_composite_start_failure({**execution,field:value},directory,names,job)
            bad=deepcopy(execution);bad['composite_counters']['attempt']={}
            with self.assertRaises(EvidenceError):audit_composite_start_failure(bad,directory,names,job)
            with self.assertRaises(EvidenceError):audit_composite_start_failure(execution,directory,names|{'train_stopped_state.json'},job)
            with self.assertRaises(EvidenceError):audit_composite_start_failure(execution,directory,names-{'training-start-failure.json'},job)
