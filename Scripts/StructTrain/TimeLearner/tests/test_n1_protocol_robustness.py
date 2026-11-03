"""Actual frozen N1 protocol data, strict completeness and identity regressions."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..condition import ConditionSpec
from ..native_evidence import EvidenceError, load
from ..n1_protocol_robustness import THRESHOLDS, _condition, _signed, _write, audit_study


class N1ProtocolRobustnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.environ.get('TIMELEARNER_N1_PROTOCOL_STUDY_DIR')
        if not path:
            raise unittest.SkipTest('requires complete native N1 order/reset/quiet-tail study')
        cls.root = Path(path)
        cls.design = load(cls.root/'design.json')

    def test_every_actual_condition_and_full_observation_set_is_recomputed(self):
        result = audit_study(self.root)
        self.assertEqual(result['validity'], 'valid')
        self.assertEqual(result['search_trials'], 528)
        self.assertEqual(len([r for r in result['rows'] if r['phase'] == 'study']), 8)
        self.assertFalse(result['threshold_retuning'])
        self.assertFalse(result['independent_patterns'])
        self.assertEqual(result['independent_trainings'], 0)
        self.assertIsNone(result['scientific_verdict'])

    def test_predeclared_thresholds_do_not_depend_on_new_responses(self):
        for row in self.design['rows']:
            job = load(self.root/'jobs'/f"{row['name']}.json")
            self.assertEqual(job['thresholds'], [THRESHOLDS[row['topology']]])
            self.assertEqual(job['maximum_candidates'], 1)
            self.assertEqual(len(job['trials']), row['expected_trials'])

    def test_condition_identity_excludes_attempt_and_deployment_paths_but_sees_the_protocol(self):
        row = next(r for r in self.design['rows'] if r['phase'] == 'study')
        job = load(self.root/'jobs'/f"{row['name']}.json")
        runtime = load(self.root/'runtime.json')
        candidate = load(self.root/'runs'/row['name']/'native/transaction.json')['candidates'][0]['candidate']
        first, _ = _condition(job['source_recognition'], candidate, job['trials'], runtime)
        moved = deepcopy(runtime);moved['executable']['path'] = '/different/deployment/NeuroModelerConsole'
        trials = deepcopy(job['trials'])
        for i, q in enumerate(trials):q.update(run_id='another-attempt', trial_id='another-trial-'+str(i))
        second, _ = _condition(job['source_recognition'], candidate, trials, moved)
        self.assertEqual(first, second)
        trials[0]['duration'] *= 2
        changed, _ = _condition(job['source_recognition'], candidate, trials, moved)
        self.assertNotEqual(ConditionSpec.loads(json.dumps(first)).fingerprint,
                            ConditionSpec.loads(json.dumps(changed)).fingerprint)

    def test_rehashed_missing_condition_cannot_keep_a_complete_study_claim(self):
        with tempfile.TemporaryDirectory(dir=self.root.parent) as directory:
            root = Path(directory)
            design = deepcopy(self.design);design['rows'].pop()
            _write(root/'design.json', _signed(design))
            shutil.copyfile(self.root/'index.json', root/'index.json')
            with self.assertRaisesRegex(EvidenceError, 'n1_study_incomplete_conditions'):
                audit_study(root)

    def test_rehashed_producer_counts_cannot_override_native_observations(self):
        before = (self.root/'index.json').read_bytes()
        with tempfile.TemporaryDirectory(dir=self.root.parent) as directory:
            root = Path(directory)/'copy'
            # Same-filesystem hardlinks avoid duplicating raw traces. Replace
            # the edited file's inode before writing; originals stay untouched.
            shutil.copytree(self.root, root, copy_function=os.link)
            changed = load(root/'index.json')
            changed['records'][0]['counts']['FP'] += 1
            (root/'index.json').unlink()
            _write(root/'index.json', _signed(changed))
            with self.assertRaisesRegex(EvidenceError, 'n1_study_producer_metrics_disagree'):
                audit_study(root)
        self.assertEqual((self.root/'index.json').read_bytes(), before)
