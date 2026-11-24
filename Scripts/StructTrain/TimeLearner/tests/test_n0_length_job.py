"""Production factor declarations using an actual cold N0 job, not a mock."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..n0_length_policy import declare_n0_length_job, FIELD
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import validate_job
from ..prepared_count_training import factor_control_job


class N0LengthJobTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(os.environ['TIMELEARNER_N0_LENGTH_SOURCE_JOB']).resolve(strict=True)
        cls.raw = cls.path.read_bytes()
        cls.original = load(cls.path)

    def test_only_the_declared_factor_and_attempt_identity_change(self):
        for allowance in (0, 4):
            with self.subTest(allowance=allowance):
                actual = declare_n0_length_job(self.original, 'length-factor', allowance)
                search = actual['configuration']['search']
                if allowance:
                    self.assertEqual(search[FIELD], allowance)
                else:
                    self.assertNotIn(FIELD, search)
                restored = deepcopy(actual)
                restored['configuration']['run_id'] = self.original['configuration']['run_id']
                restored['configuration']['search'].pop(FIELD, None)
                restored['sha256'] = self.original['sha256']
                self.assertEqual(restored, self.original)
                for mode in ('train', 'preflight'):
                    self.assertEqual(validate_job(mode, actual)['job_sha256'], actual['sha256'])

    def test_source_and_explicitly_selected_factor_are_immutable(self):
        before = deepcopy(self.original)
        positive = declare_n0_length_job(self.original, 'length-four', 4)
        saved = deepcopy(positive)
        legacy = declare_n0_length_job(positive, 'length-zero', 0)
        self.assertEqual(positive, saved)
        self.assertNotIn(FIELD, legacy['configuration']['search'])
        self.assertEqual(self.original, before)
        self.assertEqual(self.path.read_bytes(), self.raw)

    def test_invalid_factor_and_attempt_identity_are_rejected(self):
        excessive = self.original['configuration']['search']['maximum_candidates_per_input']+1
        for value in (True, 1.5, -1, None, excessive):
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                declare_n0_length_job(self.original, 'invalid-factor', value)
        for run_id in ('', ' ', 1, None, True):
            with self.subTest(run_id=run_id), self.assertRaises(EvidenceError):
                declare_n0_length_job(self.original, run_id, 4)

    def test_existing_positive_graph_control_keeps_the_declared_length_factor(self):
        actual = declare_n0_length_job(self.original, 'length-factor-control', 4)
        control = factor_control_job(actual)
        validate_job('preflight', control)
        self.assertEqual(control['configuration']['search'][FIELD], 4)
        self.assertEqual(actual['configuration']['model'], self.original['configuration']['model'])
        self.assertNotEqual(control['configuration']['model'], actual['configuration']['model'])

    def test_source_corruption_cannot_be_resigned_by_the_factor_builder(self):
        damaged = deepcopy(self.original)
        damaged['configuration']['maximum_wall_seconds'] += 1
        with self.assertRaises(EvidenceError):
            declare_n0_length_job(damaged, 'damaged-source', 4)


if __name__ == '__main__':
    unittest.main()
