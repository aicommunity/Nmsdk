"""Production declarations and real CLI ModelSpec1/2 transfer evidence."""
import copy
import json
import os
import shutil
from pathlib import Path
import tempfile
import unittest

from ..model_spec_transport import prepare, requests, BASELINE
from ..native_calibration_worker import _signed, audit_run_manifest as audit_calibration
from ..native_pipeline_worker import audit_run_manifest
from ..native_evidence import load, EvidenceError
from ..learned_evidence import audit_learned_state, load_case
from ..calibrated_evidence import audit_calibrated_state
from ..recognition_metrics import load_evaluation


class ModelSpecTransportPreparationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_MODEL_SPEC_TRANSPORT_REPOSITORY')
        if not value:
            raise unittest.SkipTest('requires Git repository containing pinned positive N1 primaries')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)/'prepared'
        cls.plan = prepare(Path(value), cls.root)

    def test_only_model_wire_version_and_explicit_threshold_change(self):
        self.assertEqual(self.plan['baseline_commit'], BASELINE)
        self.assertEqual(len(self.plan['conditions']), 4)
        for row in self.plan['conditions']:
            original = load(self.root/'baseline/corpus'/row['baseline_name']/'input/job.json')
            job = load(self.root/'jobs'/(row['name']+'-train.json'))
            if row['model_spec_version'] == 2:
                restored = copy.deepcopy(job)
                self.assertEqual(restored['configuration']['model'].pop('initial_threshold'), 1.)
                restored['configuration']['model']['schema_version'] = 1
                restored.pop('sha256');restored = _signed(restored)
                self.assertEqual(restored, original)
            else:
                self.assertEqual(job, original)

    def test_actual_pinned_source_is_exact_with_original_tolerances(self):
        for row in self.plan['conditions']:
            case = load_case(self.root/'baseline/corpus'/row['baseline_name']/'native/train_learned_state.json')
            self.assertTrue(audit_learned_state(*case)['exact'])
            self.assertEqual(case[0]['configuration']['search']['tolerances'],
                             {'amplitude_absolute': 1e-5, 'amplitude_relative': 0, 'sync': .02})
            self.assertEqual(case[0]['configuration']['model']['initial_isi'], [.01, .03])
            self.assertTrue(any(n['path'] == '$.LTMembrane' for n in
                                case[0]['neuron']['graph']['identity']['model']['nodes']))

    def test_frozen_target_in_both_positions_uses_complete_predeclared_windows(self):
        trials = requests('declared', frozen=True)
        self.assertEqual([q['label'] for q in trials], ['target', 'foil', 'foil', 'target'])
        self.assertEqual(len({q['trial_id'] for q in trials}), 4)
        for q in trials:
            self.assertGreater(q['duration'], sum(q['pattern_isi']))
            self.assertGreater(q['maximum_samples'], q['duration']*2000+1)
            self.assertEqual(q['reset_policy'], 'reset_per_trial')

    def test_historical_adapter_preserves_original_claims_and_default_stays_strict(self):
        row = self.plan['conditions'][0]
        original = self.root/'baseline/corpus'/row['baseline_name']
        with self.assertRaisesRegex(EvidenceError, 'pipeline_run_analysis_changed'):
            audit_run_manifest(original/'run-manifest.json')
        accepted = audit_run_manifest(original/'run-manifest.json', historical_analysis='learned-v2-no-capacitance')
        self.assertEqual(accepted['historical_analysis_adapter'], 'learned-v2-no-capacitance')
        destination = Path(self.tmp.name)/'damaged'
        shutil.copytree(original, destination)
        path = destination/'run-manifest.json';saved = load(path)
        for key, value in [('exact', False), ('primary_trials', 0), ('auditor_version', 99)]:
            changed = copy.deepcopy(saved);changed['analysis']['training_audit'][key] = value
            changed.pop('sha256');path.write_text(json.dumps(_signed(changed)), encoding='utf-8')
            with self.subTest(field=key), self.assertRaises(EvidenceError):
                audit_run_manifest(path, historical_analysis='learned-v2-no-capacitance')


class ModelSpecTransportRunTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_MODEL_SPEC_TRANSPORT_RUN')
        prepared = os.environ.get('TIMELEARNER_MODEL_SPEC_TRANSPORT_PREPARED')
        if not value or not prepared:
            raise unittest.SkipTest('requires four actual Train/export/calibrate/fresh evaluation chains')
        cls.root, cls.prepared = Path(value), Path(prepared)
        cls.index = load(cls.root/'index.json')
        if len(cls.index['conditions']) != 4:
            raise RuntimeError('incomplete ModelSpec1/2 actual operation matrix')

    def test_all_sources_really_train_exact_from_the_pinned_same_physical_model(self):
        for row in self.index['conditions']:
            folder = self.root/'runs'/(row['name']+'-train')
            self.assertTrue(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'])
            self.assertTrue(audit_learned_state(*load_case(folder/'native/train_learned_state.json'))['exact'])
            before = load(folder/'native/initial-state.json')
            original = load(self.prepared/'baseline/corpus'/row['baseline_name']/'native/initial-state.json')
            self.assertEqual(before['identity'], original['identity'])
            self.assertEqual(before['parameters'], original['parameters'])
            job = load(folder/'input/job.json')
            self.assertEqual(job, load(self.prepared/'jobs'/(row['name']+'-train.json')))

    def test_every_candidate_and_fresh_confirmation_have_native_provenance(self):
        for row in self.index['conditions']:
            folder = self.root/'runs'/(row['name']+'-calibrate')
            self.assertTrue(audit_calibration(folder/'run-manifest.json')['run_evidence_consistent'])
            self.assertEqual(row['calibration_status'], 'calibrated')
            package = load(folder/'native/model.json')
            case = load_case(self.root/'runs'/(row['name']+'-train')/'native/train_learned_state.json')
            self.assertTrue(audit_calibrated_state(package, case)['calibrated'])
            self.assertNotEqual(package['threshold'], 1.)

    def test_fresh_console_import_preserves_full_calibrated_package_and_records_all_windows(self):
        for row in self.index['conditions']:
            folder = self.root/'runs'/(row['name']+'-frozen')
            self.assertTrue(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'])
            package = load(self.root/'runs'/(row['name']+'-calibrate')/'native/model.json')
            self.assertEqual(load(folder/'native/model.json'), package)
            self.assertEqual(load(folder/'native/model-after.json'), package)
            _, observations = load_evaluation(folder/'native/evaluation.json')
            self.assertEqual(len(observations), 4)
            self.assertEqual([o['label'] for o in observations], ['target', 'foil', 'foil', 'target'])
            self.assertTrue(all(o['valid'] and o['complete'] and not o['censored'] for o in observations))
            manifest = load(folder/'run-manifest.json')
            self.assertEqual(manifest['execution'], 'completed')

    def test_schema1_and_schema2_have_the_same_measured_solo_and_calibrated_physics(self):
        for top in ('Classic', 'Branch'):
            solos = [load(self.root/'runs'/(top+'-v'+str(v)+'-train')/'native/train_learned_state.json')
                     for v in (1, 2)]
            self.assertEqual(solos[0]['model_revision'], solos[1]['model_revision'])
            self.assertEqual(solos[0]['trained_inputs'], solos[1]['trained_inputs'])
            self.assertEqual(solos[0]['neuron']['graph'], solos[1]['neuron']['graph'])
            calibrated = [load(self.root/'runs'/(top+'-v'+str(v)+'-calibrate')/'native/model.json')
                          for v in (1, 2)]
            self.assertEqual(calibrated[0]['threshold'], calibrated[1]['threshold'])
            self.assertEqual(calibrated[0]['model_revision'], calibrated[1]['model_revision'])
            self.assertEqual(calibrated[0]['neuron']['graph'], calibrated[1]['neuron']['graph'])


if __name__ == '__main__':
    unittest.main()
