"""Controlled metadata/join negatives; no native producer acceptance.

Run on workers only. Artificial declarations below exercise narrow validators;
the separate native corpus suite must cover the actual complete DATA path.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from .. import candidate_window_certificate_evidence as certificate
from ..candidate_window_package_evidence import audit_candidate_window_package, _runtime_context
from ..composite_package_evidence import audit_composite_package
from ..learned_evidence import audit_learned_state, load_case as load_learned
from ..stopped_evidence import audit_stopped_state, load_case as load_stopped
from ..native_evidence import EvidenceError
from .synthetic_candidate_archive2 import fixture


class CandidateWindowPackage6MetadataTest(unittest.TestCase):
    def context(self):
        archive,configuration,plan,_=fixture()
        return dict(measurement_archive=archive,configuration=configuration,protocol=archive['protocol'],runtime_plan=plan,
                    model_revision=plan['initial_model_revision'],model_epoch=plan['initial_model_epoch'])

    def test_schema6_dispatch_rejects_missing_fields_through_its_own_contract(self):
        with self.assertRaisesRegex(EvidenceError,'candidate_window_package6_fields'):
            audit_composite_package(dict(schema_version=6))

    def test_schema5_and_schema6_direct_readers_are_not_wire_aliases(self):
        with self.assertRaises(EvidenceError):audit_candidate_window_package(dict(schema_version=5))
        with self.assertRaisesRegex(EvidenceError,'unknown_composite_package_fields'):
            audit_composite_package(dict(schema_version=5))

    def test_malformed_nonobject_uses_evidence_error(self):
        with self.assertRaises(EvidenceError):audit_composite_package([])

    def test_learned_dispatch_rejects_old_flat_primary_overlay(self):
        with self.assertRaisesRegex(EvidenceError,'composite_package_legacy_primary_overlay'):
            audit_learned_state(dict(schema_version=6,kind='timelearner_completed_state'),None,{'fake':{}},{})

    def test_stopped_dispatch_rejects_old_flat_primary_overlay(self):
        with self.assertRaisesRegex(EvidenceError,'composite_package_legacy_primary_overlay'):
            audit_stopped_state(dict(schema_version=6,kind='timelearner_stopped_state'),None,{'fake':{}},{})

    def test_selfcontained_file_loading_does_not_require_or_invent_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            for suffix,kind,loader in [('learned','timelearner_completed_state',load_learned),
                                        ('stopped','timelearner_stopped_state',load_stopped)]:
                path=Path(directory)/('train_'+suffix+'_state.json')
                document=dict(schema_version=6,kind=kind);path.write_text(json.dumps(document),encoding='utf-8')
                package,summary,packets,traces=loader(path)
                self.assertEqual(package,document);self.assertIsNone(summary)
                self.assertEqual((packets,traces),({},{}))

    def test_runtime_initial_model_joins_first_current_record(self):
        package=self.context();_runtime_context(package)
        package['runtime_plan']['initial_model_revision']='another-current-boundary'
        with self.assertRaisesRegex(EvidenceError,'candidate_window_package_runtime_initial_model'):
            _runtime_context(package)

    def test_empty_current_attempt_joins_actual_current_model_not_old_history(self):
        package=self.context();package['runtime_plan']['run_id']='new-empty-attempt'
        package['measurement_archive']['current_attempt_id']='new-empty-attempt';_runtime_context(package)
        package['model_epoch']=1
        with self.assertRaisesRegex(EvidenceError,'candidate_window_package_runtime_initial_model'):
            _runtime_context(package)

    def test_warm_runtime_tolerance_change_does_not_rewrite_initial_configuration(self):
        package=self.context();original=deepcopy(package['configuration'])
        package['runtime_plan']['search']['tolerances']['sync']=.03;_runtime_context(package)
        self.assertEqual(package['configuration'],original)

    def test_current_normalization_cannot_change_native_model_family(self):
        package=self.context();package['runtime_plan']['search']['normalization']='N1'
        package['runtime_plan']['search']['n0_candidate_repeats']=1
        with self.assertRaises(EvidenceError):_runtime_context(package)

    def test_final_decimal_id_has_no_fraction_boolean_sign_or_leading_zero(self):
        for value in (True,False,1,'','01','-1','1.0','9007199254740992'):
            with self.subTest(value=value),self.assertRaises(EvidenceError):certificate._serial(value)
        self.assertEqual(certificate._serial('0'),0)
        with self.assertRaises(EvidenceError):certificate._serial('0',positive=True)

    def test_incomplete_selected_allN_does_not_create_math_certificate(self):
        package=self.context();package['measurement_archive']['final_group_ids']=[]
        self.assertIsNone(certificate.replay_candidate_window_certificate(package,{}))

    def test_protocol4_cannot_enter_protocol5_residual_replay(self):
        package=self.context();package['protocol']['schema_version']=4
        with self.assertRaisesRegex(EvidenceError,'candidate_window_certificate_requires_protocol5_archive2'):
            certificate.replay_candidate_window_certificate(package,{})

    def test_arrival_uses_each_actual_origin_and_never_absolute_model_clock(self):
        record=dict(selection=dict(geometry=dict(measured_maximum=dict(raw_potential=2.,time=100.25,plateau_end=100.5))),
            native_group=dict(traces=[dict(native_evidence=dict(observation=dict(stimuli=[dict(time=100.)])))]),
            measurement=dict(raw_potential=2.,arrival=.25,plateau_end=.5,actual_origin_time=100.))
        protocol=dict(stimulus_ids=['pulse0'],origin_stimulus_id='pulse0')
        self.assertEqual(certificate._measurement(record,protocol),dict(raw_potential=2.,arrival=.25,plateau_end=.5))
        record['measurement']['arrival']=100.25
        with self.assertRaises(EvidenceError):certificate._measurement(record,protocol)
