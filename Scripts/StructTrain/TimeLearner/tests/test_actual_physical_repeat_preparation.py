"""Preparation against an actual completed eight-trial Windows DATA source.

No native process is launched by this suite. A subsequent full native repeat
and production response comparison remain required for runtime acceptance.
"""
from copy import deepcopy
import os
from pathlib import Path
import unittest
import uuid

from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load
from Scripts.StructTrain.TimeLearner.prepared_physical_repeat import _binding, _closed_evaluation, prepare
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256 as sha
from Scripts.StructTrain.TimeLearner.runtime import file_record


class ActualPhysicalRepeatPreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('TIMELEARNER_PHYSICAL_REPEAT_SOURCE_CONTROLS')
        root = os.environ.get('TIMELEARNER_PHYSICAL_REPEAT_PYTHON_ROOT')
        if os.name != 'nt' or not source or not root:
            raise unittest.SkipTest('requires an actual closed Windows physical evaluation and pinned actor')
        cls.actor = Path(__file__).resolve().parents[4]
        cls.source = Path(source)
        cls.source_record = _closed_evaluation(cls.source)
        cls.declaration = dict(kind='timelearner_physical_repeat_preparation', schema_version=1,
            source_controls=str(cls.source), run_id='physical-repeat-metadata-'+uuid.uuid4().hex,
            python_source=str(cls.actor), python_root=root)

    def test_actual_source_has_full_frozen_graph_and_all_labelled_responses(self):
        source = self.source_record
        self.assertEqual(len(source['job']['trials']), 8)
        self.assertEqual(sum(t['label'] == 'target' for t in source['job']['trials']), 1)
        self.assertEqual(source['model']['model_revision'], source['metrics']['model_revision'])
        self.assertTrue(source['metrics']['data_only'])
        self.assertGreater(len(source['model']['neuron']['class_definitions']), 0)
        self.assertEqual(source['job']['source_model_data'], source['model'])

    def test_prepare_copies_exact_model_and_preserves_every_physical_trial_condition(self):
        controls = prepare(self.declaration)
        binding = _binding(controls)
        spec = load(controls/'specification.json')
        inputs = Path(spec['inputs'])
        model = load(inputs/'model.json')
        envelope = load(inputs/'native-job-source.json')
        job = dict(envelope['job'], source_model_data=model)
        original = self.source_record['job']
        self.assertEqual(model, self.source_record['model'])
        self.assertEqual(file_record(inputs/'model.json')['sha256'],
                         file_record(self.source_record['model_path'])['sha256'])
        physical_trials = lambda v: [{k:x for k,x in t.items() if k not in ('run_id','trial_id')}
                                      for t in v['trials']]
        self.assertEqual(physical_trials(job), physical_trials(original))
        self.assertEqual(job['criterion'], original['criterion'])
        self.assertEqual(job['maximum_model_ticks'], original['maximum_model_ticks'])
        self.assertEqual(job['sha256'], sha({k:v for k,v in job.items() if k != 'sha256'}))
        self.assertNotEqual([t['trial_id'] for t in job['trials']], [t['trial_id'] for t in original['trials']])
        self.assertFalse(binding['training_certificate_transferred'])
        self.assertFalse(Path(spec['output']).exists())
        self.assertTrue(all(file_record(Path(p)) == r for p,r in binding['source_records'].items()))
        # Repeat preparation never creates an executable native result.
        self.assertFalse((Path(spec['output'])/'repeat-terminal.json').exists())

    def test_extra_threshold_factor_is_rejected_before_preparation(self):
        declaration = dict(self.declaration, threshold=1.0)
        with self.assertRaisesRegex(EvidenceError, 'physical_repeat_preparation_schema'):
            prepare(declaration)

    def test_reset_policy_cannot_be_changed_through_repeat_interface(self):
        declaration = dict(self.declaration, reset_policy='preserve_neuron_dynamics')
        with self.assertRaisesRegex(EvidenceError, 'physical_repeat_preparation_schema'):
            prepare(declaration)

    def test_unknown_schema_is_not_a_compatibility_fallback(self):
        declaration = dict(self.declaration, schema_version=2)
        with self.assertRaisesRegex(EvidenceError, 'physical_repeat_preparation_schema'):
            prepare(declaration)

    def test_missing_source_is_rejected_without_model_substitution(self):
        declaration = deepcopy(self.declaration)
        declaration['source_controls'] = str(self.source.parent/'does-not-exist-physical-repeat-source')
        with self.assertRaises(FileNotFoundError):
            prepare(declaration)


if __name__ == '__main__':
    unittest.main()
