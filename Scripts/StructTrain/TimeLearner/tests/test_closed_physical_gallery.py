"""Exercise production gallery preparation on an actual archived native run."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..closed_physical_gallery import prepare, validate_plan
from ..native_evidence import EvidenceError, load
from ..runtime import file_record


class ClosedPhysicalGalleryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = load(Path(os.environ['TIMELEARNER_CLOSED_GALLERY_SOURCE'])/'plan.json')
        cls.plan['cases'] = cls.plan['cases'][:1]

    def test_actual_complete_run_keeps_labels_events_and_primary_bindings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root/'plan.json'
            plan.write_text(json.dumps(self.plan))
            result = prepare(plan, root/'report')
            rows = load(root/'report/sources.json')['trials']
            self.assertEqual(result['observations'], 8)
            self.assertEqual([r['response'] for r in rows].count('TP'), 1)
            self.assertEqual([r['response'] for r in rows].count('FP'), 1)
            self.assertEqual([r['response'] for r in rows].count('TN'), 6)
            for row in rows:
                observation = load(root/'report'/row['observation']['path'])
                original = load(Path(self.plan['cases'][0]['native_directory'])/
                                ('trial-'+row['id'].rsplit('-', 1)[1]+'.json'))
                self.assertEqual(observation, original)
                self.assertEqual(row['sample_id'], observation['sample_id'])
                self.assertEqual(row['trial_id'], observation['trial_id'])
            self.assertFalse(result['native_experiment_started'])
            self.assertFalse(result['source_native_process_ownership_reattested'])
            self.assertFalse(result['figures_rendered'])

    def test_duplicate_case_ids_are_rejected(self):
        plan = deepcopy(self.plan)
        plan['cases'].append(deepcopy(plan['cases'][0]))
        with self.assertRaisesRegex(EvidenceError, 'duplicate_or_invalid_case_id'):
            validate_plan(plan)

    def test_unknown_schema_is_rejected(self):
        plan = deepcopy(self.plan)
        plan['schema_version'] = 2
        with self.assertRaisesRegex(EvidenceError, 'closed_gallery_plan_schema'):
            validate_plan(plan)

    def test_primary_member_digest_cannot_be_substituted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = deepcopy(self.plan)
            bundle = load(Path(plan['cases'][0]['bundle']['path']))
            key = plan['cases'][0]['primary_member_prefix']+'/trial-0.json'
            bundle['members'][key]['sha256'] = '0'*64
            changed = root/'bundle.json'
            changed.write_text(json.dumps(bundle))
            plan['cases'][0]['bundle'] = file_record(changed)
            path = root/'plan.json'
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(EvidenceError, 'closed_gallery_primary_member_changed:trial-0.json'):
                prepare(path, root/'report')

    def test_missing_real_observation_cannot_produce_a_gallery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = deepcopy(self.plan)
            native = root/'native'
            shutil.copytree(plan['cases'][0]['native_directory'], native)
            (native/'trial-7.json').unlink()
            plan['cases'][0]['native_directory'] = str(native)
            path = root/'plan.json'
            path.write_text(json.dumps(plan))
            with self.assertRaises((EvidenceError, FileNotFoundError)):
                prepare(path, root/'report')
