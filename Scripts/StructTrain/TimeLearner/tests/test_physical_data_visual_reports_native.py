"""Actual closed Console DATA traces, original primary and strict role checks."""
import copy
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..recognition_metrics import load_physical_model_data_evaluation, score_physical_model_data_evaluation
from ..reports import render_physical_data_evaluation


class PhysicalDataVisualReportsNativeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ['TIMELEARNER_PHYSICAL_DATA_CONSOLE_PRIMARY']).resolve(strict=True)
        cls.cases = [cls.root/'original-console-a4/classic/native',
                     cls.root/'recovered-console-a5/branch/native']
        for path in cls.cases:
            assert (path/'evaluation.json').is_file() and (path/'model.json').is_file()

    def test_actual_both_topologies_preserve_primary_metrics_and_readable_views(self):
        from PIL import Image
        total = 0
        temporary = Path(os.environ['TMPDIR'])/'physical-data-visual-report-native'
        temporary.mkdir(exist_ok=False)
        for i, native in enumerate(self.cases):
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in native.iterdir() if p.is_file()}
            source = native/'evaluation.json';model = native/'model.json'
            spec, observations = load_physical_model_data_evaluation(source)
            expected = score_physical_model_data_evaluation(spec, observations, load(model))
            self.assertEqual(expected['validity'], 'valid')
            self.assertEqual(len(observations), 2)
            output = Path(temporary)/('case-'+str(i))
            result = render_physical_data_evaluation(source, model, output)
            manifest = load(output/'manifest.json')
            self.assertTrue(result['data_only'])
            self.assertFalse(manifest['visual_acceptance_complete'])
            self.assertEqual(manifest['purpose'], 'physical_model_data_evaluation_diagnostic')
            self.assertEqual(manifest['source_boundary'], load(model)['source_boundary'])
            self.assertIsNone(result['evaluation_verdict'])
            for key in ('source_training_evidence_checked', 'training_certificate_transferred',
                        'calibration_confirmed', 'native_import_verified', 'controller_checkpoint_restored'):
                self.assertFalse(manifest[key])
            self.assertEqual(result['lt_decision_trial_pairs'], 2)
            channels = 1 if load(model)['configuration']['model']['branch'] else 2
            self.assertEqual(result['trial_soma_pairs'], 2*channels);total += result['trial_soma_pairs']
            for figure in manifest['figures']:
                self.assertTrue(figure['views'])
                for view in figure['views']:
                    self.assertFalse(view['downsampling'])
                    if view['minimum_native_tick_pixels_on_zoom'] is not None:
                        self.assertGreaterEqual(view['minimum_native_tick_pixels_on_zoom'], 8)
                    with Image.open(output/view['files'][0]) as image:
                        self.assertGreaterEqual(image.width, 1800)
            copied_spec, copied_observations = load_physical_model_data_evaluation(output/'primary/evaluation.json')
            self.assertEqual(copied_observations, observations)
            self.assertEqual(load(output/'primary/model.json'), load(model))
            replay = score_physical_model_data_evaluation(copied_spec, copied_observations, load(output/'primary/model.json'))
            self.assertEqual(replay, expected)
            for name, digest in load(output/'SHA256SUMS.json').items():
                self.assertEqual(hashlib.sha256((output/name).read_bytes()).hexdigest(), digest)
            self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in native.iterdir() if p.is_file()})
        self.assertEqual(total, 6)

    def test_unknown_evaluation_schema_does_not_create_report(self):
        from ..__main__ import main
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as temporary:
            native = self.cases[0];spec = load(native/'evaluation.json');spec['schema_version'] = 99
            source = Path(temporary)/'unknown.json';source.write_text(json.dumps(spec)+'\n', encoding='utf-8')
            output = Path(temporary)/'report'
            with self.assertRaisesRegex(EvidenceError, 'unknown_evaluation_spec'):
                render_physical_data_evaluation(source, native/'model.json', output)
            self.assertFalse(output.exists())
            captured = io.StringIO()
            with contextlib.redirect_stderr(captured):
                code = main(['report', str(source), '--format', 'physical-model-evaluation',
                             '--model', str(native/'model.json'), '--output', str(output)])
            self.assertEqual(code, 2)
            self.assertIn('unknown_evaluation_spec', json.loads(captured.getvalue())['reason'])
            self.assertFalse(output.exists())

    def test_self_signed_unknown_source_boundary_does_not_create_report(self):
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as temporary:
            native = Path(temporary)/'native';shutil.copytree(self.cases[0], native)
            model = load(native/'model.json');model['source_boundary']['schema_version'] = 99
            model['sha256'] = canonical_model_sha256({k: v for k, v in model.items() if k != 'sha256'})
            (native/'model.json').write_text(json.dumps(model)+'\n', encoding='utf-8')
            spec = load(native/'evaluation.json');spec['source_boundary'] = copy.deepcopy(model['source_boundary'])
            (native/'evaluation.json').write_text(json.dumps(spec)+'\n', encoding='utf-8')
            output = Path(temporary)/'report'
            with self.assertRaises(EvidenceError):
                render_physical_data_evaluation(native/'evaluation.json', native/'model.json', output)
            self.assertFalse(output.exists())
