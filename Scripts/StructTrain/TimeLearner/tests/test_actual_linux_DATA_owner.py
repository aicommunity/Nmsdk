"""Owner selection over archived native Classic/Branch physical models.

These declarations exercise the production job validator. A separate native
replay checks execution; these tests do not manufacture a learned model.
"""
from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest

from ..linux_physical_recognition_sequence import job_for
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job
from ..runtime import file_record


class ActualLinuxDATAOwner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = os.environ.get('TIMELEARNER_LINUX_DATA_OWNER_FIXTURES')
        if sys.platform != 'linux' or not fixture:
            raise unittest.SkipTest('requires the declared archived native Classic/Branch DATA fixtures')
        root = Path(fixture).resolve(strict=True)
        index = load(root/'index.json')
        if set(index['models']) != {'Classic', 'Branch'}:
            raise RuntimeError('both actual physical topologies are required')
        cls.request = load(root/'request.json')
        cls.models = {}
        for topology, record in index['models'].items():
            path = Path(record['path'])
            if file_record(path) != record:
                raise RuntimeError('actual DATA fixture changed: '+topology)
            cls.models[topology] = load(path)

    def generated(self, model, phase='baseline'):
        return job_for({'q': self.request}, phase, model)

    def test_both_native_topologies_generate_valid_jobs_without_changing_model(self):
        for topology, model in self.models.items():
            before = deepcopy(model)
            for phase in ('baseline', 'confirmation'):
                with self.subTest(topology=topology, phase=phase):
                    job = self.generated(model, phase)
                    expected = 'NNeuronTimeLearner'+('Branch' if topology == 'Branch' else '')
                    self.assertEqual(job['owner_class'], expected)
                    self.assertIs(job['source_model_data'], model)
                    admission = validate_job('physical-model-evaluate', job, (model,))
                    self.assertTrue(admission['data_only'])
                    self.assertFalse(admission['training_certificate_transferred'])
            self.assertEqual(model, before)

    def test_original_branch_payload_with_classic_owner_is_rejected(self):
        model = self.models['Branch']; job = self.generated(model)
        job['owner_class'] = 'NNeuronTimeLearner'
        job['sha256'] = sha({k:v for k,v in job.items() if k != 'sha256'})
        with self.assertRaisesRegex(EvidenceError, 'pipeline_owner_or_tick_budget_invalid'):
            validate_job('physical-model-evaluate', job, (model,))

    def test_classic_source_cannot_be_executed_by_branch_owner(self):
        model = self.models['Classic']; job = self.generated(model)
        job['owner_class'] = 'NNeuronTimeLearnerBranch'
        job['sha256'] = sha({k:v for k,v in job.items() if k != 'sha256'})
        with self.assertRaisesRegex(EvidenceError, 'pipeline_owner_or_tick_budget_invalid'):
            validate_job('physical-model-evaluate', job, (model,))

    def test_owner_selection_cannot_trust_resigned_topology_changes(self):
        for topology, model in self.models.items():
            for branch in (not model['configuration']['model']['branch'], 'false', 0, None):
                changed = deepcopy(model); changed['configuration']['model']['branch'] = branch
                changed['sha256'] = sha({k:v for k,v in changed.items() if k != 'sha256'})
                with self.subTest(topology=topology, branch=branch), self.assertRaises(EvidenceError):
                    self.generated(changed)


if __name__ == '__main__':
    unittest.main()
