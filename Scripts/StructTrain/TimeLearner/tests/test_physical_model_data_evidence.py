"""Production readers/scorer over real native DATA roundtrip outputs.

Mutations below test rejection/metric rules, never additional physical runs.
"""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError, load
from ..physical_model_data_evidence import audit_physical_model_data
from ..recognition_metrics import score_physical_model_data_evaluation, score_recognition_evaluation


def signed(document):
    document['sha256'] = digest({k: v for k, v in document.items() if k != 'sha256'})
    return document


class PhysicalModelDataEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get('TIMELEARNER_PHYSICAL_DATA_DIR')
        if not directory:
            raise unittest.SkipTest('requires native NativePhysicalModelData frozen outputs')
        cls.cases = []
        for topology in ('Classic', 'Branch'):
            root = Path(directory); stem = 'physical-data-frozen-' + topology
            model = load(root / (stem + '-model-data.json'))
            source = load(root / (stem + '-source.json'))
            observations = [load(root / (stem + '-' + label + '.json'))['physical_data']
                            for label in ('target', 'foil')]
            spec = dict(kind='timelearner_physical_model_data_evaluation_spec', schema_version=1,
                run_id=observations[0]['run_id'], model_revision=model['model_revision'], data_only=True,
                source_boundary=copy.deepcopy(model['source_boundary']), coverage_policy='per_trial_windows',
                criterion=dict(id='post_anchor_target_whole_window_foil_v1', anchor='onset', begin_offset=0.,
                    end_offset=None, reject_target_outside_window=True),
                trials=[dict(trial_id=o['trial_id'], sample_id=o['sample_id'], label=o['label'],
                    pattern_hash=o['pattern_hash'], reset_policy=o['reset_policy'], presentation_index=i,
                    duration=.4, observation='trial-' + str(i) + '.json') for i, o in enumerate(observations)])
            cls.cases.append((model, source, spec, observations))

    def test_real_native_data_and_full_observations_without_training_authority(self):
        for model, source, spec, observations in self.cases:
            audit = audit_physical_model_data(model, frozen=True)
            self.assertEqual(model['source_boundary']['sha256'], source['sha256'])
            self.assertEqual(audit['model_revision'], source['model_revision'])
            result = score_physical_model_data_evaluation(spec, observations, model)
            self.assertEqual(result['validity'], 'valid')
            counts = result['pooled_counts']
            self.assertEqual(counts['targets'], 1); self.assertEqual(counts['foils'], 1)
            self.assertEqual(counts['TP'], int(bool(observations[0]['spike_times'])))
            self.assertEqual(counts['FP'], int(bool(observations[1]['spike_times'])))
            self.assertTrue(result['data_only']); self.assertIsNone(result['training_completed'])
            self.assertIsNone(result['declared_training_outcome'])
            for key in ('source_training_evidence_checked', 'training_certificate_present',
                        'calibration_confirmed', 'native_execution_verified'):
                self.assertFalse(result[key])
            self.assertIsNone(result['evaluation_verdict'])

    def test_row_order_and_relocation_do_not_change_counts_or_identity(self):
        for model, _, spec, observations in self.cases:
            expected = score_physical_model_data_evaluation(spec, observations, model)
            moved = copy.deepcopy(spec); moved['trials'].reverse()
            for trial in moved['trials']: trial['observation'] = 'moved/' + trial['observation']
            self.assertEqual(score_physical_model_data_evaluation(moved, observations[::-1], model), expected)

    def test_missing_duplicate_nonfinite_and_wrong_label_cannot_score(self):
        for model, _, spec, observations in self.cases:
            for changed in (observations[:-1], observations + [observations[0]]):
                with self.assertRaises(EvidenceError): score_physical_model_data_evaluation(spec, changed, model)
            for field, value in (('label', 'target'), ('model_after', '0' * 64)):
                changed = copy.deepcopy(observations); changed[1][field] = value
                with self.assertRaises(EvidenceError): score_physical_model_data_evaluation(spec, changed, model)
            changed = copy.deepcopy(observations); changed[0]['samples'][1]['soma'][0] = float('nan')
            with self.assertRaises(EvidenceError): score_physical_model_data_evaluation(spec, changed, model)

    def test_censoring_forbids_pooled_counts(self):
        for model, _, spec, observations in self.cases:
            changed = copy.deepcopy(observations)
            changed[0].update(complete=False, censored=True, valid=False, reason='test_cancelled_at_closed_boundary')
            result = score_physical_model_data_evaluation(spec, changed, model)
            self.assertEqual(result['validity'], 'invalid'); self.assertIsNone(result['pooled_counts'])
            self.assertIsNone(result['evaluation_verdict'])

    def test_resigned_physics_and_false_proof_claims_are_rejected(self):
        for model, _, _, _ in self.cases:
            for field, value in (('data_only', False), ('dynamic_checkpoint', True), ('certificate', {})):
                changed = copy.deepcopy(model); changed[field] = value
                with self.assertRaises(EvidenceError): audit_physical_model_data(signed(changed), frozen=True)
            changed = copy.deepcopy(model); changed['parameters'][0]['resistance'] *= 1.25
            with self.assertRaises(EvidenceError): audit_physical_model_data(signed(changed), frozen=True)
            changed = copy.deepcopy(model); archive = changed['neuron']
            archive['metadata']['calibration']['threshold'] += 1.
            signed(archive)
            with self.assertRaises(EvidenceError): audit_physical_model_data(signed(changed), frozen=True)

    def test_old_proof_scoring_role_does_not_accept_physical_data(self):
        for model, _, spec, observations in self.cases:
            old = copy.deepcopy(spec); old.pop('data_only'); old.pop('source_boundary')
            old['kind'] = 'timelearner_recognition_evaluation_spec'
            with self.assertRaises(EvidenceError): score_recognition_evaluation(old, observations, model)

    def test_pipeline_uses_the_complete_data_source_without_history_siblings(self):
        from ..native_pipeline_worker import _load_source_case, _snapshot_source, validate_job
        for model, _, spec, observations in self.cases:
            requests = [{key: o[key] for key in ('run_id', 'trial_id', 'sample_id', 'label', 'pattern_hash',
                'pattern_isi', 'maximum_samples', 'reset_policy')} | dict(duration=.4, record_threshold_potential=True)
                for o in observations]
            job = signed(dict(kind='timelearner_native_physical_model_evaluation_job', schema_version=1,
                owner_class='NNeuronTimeLearner' + ('Branch' if model['configuration']['model']['branch'] else ''),
                implementation_id=model['implementation_id'], source_model_data=model, maximum_model_ticks=2000,
                run_id=spec['run_id'], coverage_policy=spec['coverage_policy'], criterion=spec['criterion'], trials=requests))
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory); path = root/'model.json'
                path.write_text(json.dumps(model, allow_nan=False), encoding='utf-8')
                copied = _snapshot_source(path, root/'snapshot', physical_data=True)
                self.assertEqual([p.name for p in copied.parent.iterdir()], ['model.json'])
                source_case = _load_source_case('physical-model-evaluate', copied)
                audit = validate_job('physical-model-evaluate', job, source_case)
                self.assertTrue(audit['data_only']); self.assertFalse(audit['source_training_evidence_checked'])
                changed = copy.deepcopy(job); changed['source_model_data']['parameters'][0]['length'] += 1
                with self.assertRaises(EvidenceError): validate_job('physical-model-evaluate', signed(changed), source_case)

    def test_public_analyze_cli_preserves_data_only_status(self):
        for model, _, spec, observations in self.cases:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name, value in [('model.json', model), ('evaluation.json', spec)] + [
                        ('trial-' + str(i) + '.json', o) for i, o in enumerate(observations)]:
                    (root/name).write_text(json.dumps(value, allow_nan=False), encoding='utf-8')
                result = subprocess.run([sys.executable, '-m', 'Scripts.StructTrain.TimeLearner', 'analyze',
                    str(root/'evaluation.json'), '--format', 'physical-model-evaluation', '--model', str(root/'model.json')],
                    capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
                response = json.loads(result.stdout)
                self.assertEqual(response['kind'], 'timelearner_analysis')
                self.assertEqual(response['schema_version'], 1)
                self.assertEqual(response['execution'], 'completed')
                self.assertEqual(response['validity'], 'valid')
                self.assertEqual(response['format'], 'physical-model-evaluation')
                self.assertIsNone(response['evaluation_verdict'])
                self.assertEqual(response['analysis'],
                                 score_physical_model_data_evaluation(spec, observations, model))
