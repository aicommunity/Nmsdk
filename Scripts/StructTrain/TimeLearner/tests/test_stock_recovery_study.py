"""Preregistration controls using actual stock declarations and native runtime."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_recovery import RECOVERY_MODE
from ..condition import ConditionSpec
from ..native_evidence import EvidenceError, load
from ..n1_protocol_robustness import _signed, _write
from ..stock_recovery_study import prepare, audit_design, recovery_job, _normalized, _condition


class StockRecoveryDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('TIMELEARNER_STOCK_RECOVERY_TEMPLATES')
        runtime = os.environ.get('TIMELEARNER_STOCK_RECOVERY_RUNTIME')
        if not source or not runtime:
            raise unittest.SkipTest('requires actual four stock templates and immutable native runtime')
        cls.source, cls.runtime = Path(source), Path(runtime)
        cls.code = load(cls.source/'code-identity.json')

    def prepared(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)/'study'
        design = prepare(self.source, self.runtime, self.code, root)
        return root, design

    def test_all_eight_conditions_are_frozen_without_starting_training(self):
        root, design = self.prepared()
        self.assertEqual(audit_design(root), design)
        self.assertEqual(len(design['rows']), 8)
        self.assertFalse((root/'runs').exists())
        self.assertFalse(design['classification_assessed'])
        self.assertIsNone(design['scientific_verdict'])

    def test_pairs_preserve_every_other_factor_and_original_template(self):
        root, design = self.prepared()
        for row in design['rows']:
            source = load(root/'source'/(row['source_name']+'.json'))
            before = deepcopy(source)
            retry = recovery_job(source, 'retry', 'retry_same_candidate')
            advance = recovery_job(source, 'advance', RECOVERY_MODE)
            self.assertEqual(source, before)
            self.assertEqual(_normalized(retry), _normalized(advance))
            self.assertEqual(retry['configuration']['search']['maximum_invalid_observations'], 32)
            self.assertEqual(source['configuration']['search']['maximum_invalid_observations'], 0)

    def test_rehashed_missing_condition_is_rejected(self):
        root, design = self.prepared()
        design['rows'].pop();_write(root/'design.json', _signed(design))
        with self.assertRaisesRegex(EvidenceError, 'stock_recovery_incomplete_matrix'):
            audit_design(root)

    def test_rehashed_budget_drift_is_rejected(self):
        for field, value in (('maximum_invalid_observations', 33), ('maximum_sweeps', 5)):
            root, design = self.prepared();row = design['rows'][0]
            path = root/'jobs'/(row['name']+'.json');job = load(path)
            job['configuration']['search'][field] = value;job = _signed(job)
            _write(path, job);row['job_sha256'] = job['sha256']
            _write(root/'design.json', _signed(design))
            with self.assertRaisesRegex(EvidenceError, 'stock_recovery_other_factors_changed'):
                audit_design(root)

    def test_recovery_policy_changes_condition_but_deployment_path_does_not(self):
        root, design = self.prepared();row = design['rows'][0]
        template = load(root/'source'/(row['source_name']+'.json'))
        expected = load(root/'expected'/(row['name']+'.json'));runtime = load(self.runtime)
        retry = recovery_job(template, 'attempt-a', 'retry_same_candidate')
        advance = recovery_job(template, 'attempt-b', RECOVERY_MODE)
        def fingerprint(job, manifest):
            evidence = _condition(job, expected, self.code, manifest)
            return ConditionSpec.loads(json.dumps(evidence['condition'])).fingerprint
        self.assertNotEqual(fingerprint(retry, runtime), fingerprint(advance, runtime))
        moved = deepcopy(runtime);moved['executable']['path'] = '/other/NeuroModelerConsole'
        retry['configuration']['run_id'] = 'another-attempt'
        self.assertEqual(fingerprint(retry, runtime), fingerprint(retry, moved))

    def test_unknown_policy_and_already_modified_template_are_rejected(self):
        root, design = self.prepared()
        template = load(root/'source'/(design['rows'][0]['source_name']+'.json'))
        with self.assertRaisesRegex(EvidenceError, 'stock_recovery_unknown_policy'):
            recovery_job(template, 'attempt', 'silently-ignore')
        modified = recovery_job(template, 'attempt', RECOVERY_MODE)
        with self.assertRaisesRegex(EvidenceError, 'stock_recovery_requires_original_base1_template'):
            recovery_job(modified, 'another', RECOVERY_MODE)
