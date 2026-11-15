"""Original large diagnostic model and observations: compact export and rescore."""
import json
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recorded_matrix_primary import create_primary, audit_primary


class DeclaredDiagnosticPrimaryTest(unittest.TestCase):
    def test_actual_closed_model_and_all_trials_rescore_from_selected_primary_bytes(self):
        source = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_PRIMARY'])
        controller = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_CONTROLLER'])
        runtime = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_RUNTIME'])/'runtime.json'
        request = load(controller/'request.json')
        cases = [row['name'] for row in request['cases']]
        originals = {name:load(source/name/'run-manifest.json') for name in cases}
        root = Path(os.environ['TMPDIR']);packed = root/'declared-compact-primary'
        bundle = create_primary(source, controller, runtime, packed,
            maximum_member_bytes=384*1024**2, deduplicate_content=True)
        self.assertEqual(bundle['schema_version'], 2)
        for name in cases:
            original = {row['path']:row for row in originals[name]['artifacts']}
            for path in ['native/model.json']+[f'native/trial-{i}.json' for i in range(8)]:
                self.assertEqual(bundle['members']['native/'+name+'/'+path],
                    {key:original[path][key] for key in ('bytes','sha256')})
        result = audit_primary(packed/'bundle.json', root/'declared-compact-restored',
                               maximum_member_bytes=384*1024**2)
        self.assertEqual(result['trials'], 8*len(cases))
        rows = {row['name']:row for row in result['models']}
        self.assertEqual(set(rows), set(cases))
        for name in cases:
            metrics = originals[name]['analysis']['metrics']
            self.assertEqual(rows[name]['model_revision'], metrics['model_revision'])
            self.assertEqual(rows[name]['training_outcome'], metrics['declared_training_outcome'])
            self.assertEqual(rows[name]['counts'], metrics['pooled_counts'])
        self.assertTrue(result['diagnostic_only'])
        self.assertFalse(result['complete_runtime_directory'])
        self.assertFalse(result['native_execution_attested'])
        self.assertIsNone(result['scientific_verdict'])
        (root/'declared-compact-readback.json').write_text(
            json.dumps(result,indent=2,allow_nan=False)+'\n', encoding='utf-8')
