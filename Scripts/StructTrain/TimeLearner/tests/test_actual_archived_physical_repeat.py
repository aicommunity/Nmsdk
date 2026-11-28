"""Production verification of two real archived Branch evaluations, no model run.

Inputs are complete immutable native primaries. Failure cases alter only private
copies of saved data; real source archives and recorded observations stay intact.
"""
from copy import deepcopy
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..archived_physical_evaluation import read_source
from ..native_evidence import EvidenceError, load
from ..prepared_physical_repeat import compare_closed


class ActualArchivedPhysicalRepeat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = os.environ.get('TIMELEARNER_ARCHIVED_REPEAT_FIXTURE')
        output = os.environ.get('TIMELEARNER_ARCHIVED_REPEAT_TEST_OUTPUT')
        if not fixture or not output:
            raise unittest.SkipTest('requires two real, complete archived evaluations and private output')
        cls.fixture = load(Path(fixture))
        cls.source = read_source(cls.fixture['source'])
        cls.observed = read_source(cls.fixture['observed'])
        cls.output = Path(output).resolve(strict=True)
        cls.binding = dict(source_records=cls.source['records'],
            model_revision=cls.source['model']['model_revision'], absolute_tolerance=1e-12,
            source_counts=cls.source['metrics']['pooled_counts'],
            threshold=cls.source['metrics']['effective_threshold'],
            training_certificate_transferred=False, calibration_confirmed=False)

    def test_all_eight_real_responses_preserved_without_relabelling_native_jobs(self):
        result = compare_closed(self.source, self.observed, self.binding)
        self.assertTrue(result['all_eight_waveforms_and_events_preserved'])
        self.assertEqual(result['compared_trials'], 8)
        self.assertEqual(len(result['comparisons']), 8)
        self.assertFalse(result['training_certificate_transferred'])
        self.assertFalse(result['calibration_confirmed'])
        self.assertNotEqual(self.source['job']['run_id'], self.observed['job']['run_id'])
        self.assertEqual(self.source['job']['kind'], self.observed['job']['kind'])

    def test_same_result_cannot_certify_its_own_repeat(self):
        with self.assertRaisesRegex(EvidenceError, 'physical_repeat_self_reference'):
            compare_closed(self.source, self.source, self.binding)

    def test_another_path_does_not_make_the_same_attempt_a_repeat(self):
        observed = dict(self.source, output=self.observed['output'])
        with self.assertRaisesRegex(EvidenceError, 'physical_repeat_same_attempt_identity'):
            compare_closed(self.source, observed, self.binding)

    def test_changed_reset_condition_is_not_a_repeat(self):
        observed = dict(self.observed, job=deepcopy(self.observed['job']))
        observed['job']['trials'][1]['reset_policy'] = 'preserve_neuron_dynamics'
        with self.assertRaisesRegex(EvidenceError, 'physical_repeat_protocol_changed'):
            compare_closed(self.source, observed, self.binding)

    def test_changed_threshold_is_not_a_repeat(self):
        observed = dict(self.observed, metrics=dict(self.observed['metrics'],
            effective_threshold=self.binding['threshold']*2))
        with self.assertRaisesRegex(EvidenceError, 'physical_repeat_model_or_threshold_changed'):
            compare_closed(self.source, observed, self.binding)

    def test_wrong_archive_digest_is_rejected_before_audit(self):
        declaration = deepcopy(self.fixture['source'])
        declaration['primary']['sha256'] = '0'*64
        with self.assertRaisesRegex(EvidenceError, 'archived_evaluation_bound_file_changed'):
            read_source(declaration)

    def _damaged_tree(self, remove):
        declaration = deepcopy(self.fixture['source'])
        with tempfile.TemporaryDirectory(prefix='archived-repeat-', dir=self.output) as temporary:
            work = Path(temporary).resolve(strict=True)
            self.assertTrue(work.is_relative_to(self.output))
            root = work/'restored'
            shutil.copytree(declaration['restored_root'], root)
            declaration['restored_root'] = str(root)
            path = root/declaration['native_prefix']/'trial-4.json'
            if remove:
                path.unlink()
            else:
                path.write_bytes(path.read_bytes()+b'\n')
            with self.assertRaisesRegex(EvidenceError, 'archived_evaluation_'+
                    ('missing_member' if remove else 'member_changed')):
                read_source(declaration)

    def test_missing_saved_trial_cannot_pass(self):
        self._damaged_tree(True)

    def test_changed_saved_trial_cannot_pass(self):
        self._damaged_tree(False)

    def test_boolean_schema_version_is_not_a_supported_version(self):
        with self.assertRaisesRegex(EvidenceError, 'archived_evaluation_source_schema'):
            read_source(dict(self.fixture['source'], schema_version=True))
