"""Readable Soma and full/positive LT scales from already checked frozen data."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..n1_protocol_robustness import _write
from ..plotting import padded_limits, render_soma
from ..recognition_metrics import load_diagnostic_evaluation


class N0LengthPositiveReportTest(unittest.TestCase):
    def test_all_low_threshold_patterns_keep_original_values_and_explicit_scale_limits(self):
        from PIL import Image

        controls = Path(os.environ['TIMELEARNER_N0_LENGTH_POSITIVE_CONTROLS']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        self.assertEqual(set(declaration), {'source_gallery'})
        source = Path(declaration['source_gallery']).resolve(strict=True)
        output = Path(os.environ['TMPDIR'])/'n0-length-positive-companions'
        output.mkdir(exist_ok=False)
        all_rows = []
        for name in ['baseline-fixed00117', 'candidate-fixed00117']:
            case = source/name
            sums = load(case/'SHA256SUMS.json')
            spec = load(case/'primary/evaluation.json')
            paths = ['primary/evaluation.json', 'analysis.json', 'manifest.json']
            paths += ['primary/'+t['observation'] for t in spec['trials']]
            before = {p: hashlib.sha256((case/p).read_bytes()).hexdigest() for p in paths}
            self.assertTrue(all(sums[p] == h for p, h in before.items()))
            _, observations = load_diagnostic_evaluation(case/'primary/evaluation.json')
            metrics = load(case/'analysis.json')
            self.assertEqual(metrics['validity'], 'valid')
            self.assertEqual(metrics['effective_threshold'], .0117)
            self.assertTrue(metrics['diagnostic_only'])
            self.assertFalse(metrics['training_completed'])
            self.assertIsNone(metrics['evaluation_verdict'])
            self.assertEqual(len(observations), 8)
            self.assertEqual({o['sample_id'] for o in observations}, {t['sample_id'] for t in metrics['trials']})
            self.assertTrue(all(o['complete'] and o['spike_count'] == len(o['spike_times']) for o in observations))
            self.assertTrue(all(len(s['soma']) == 1 for o in observations for s in o['samples']))
            soma_positive = padded_limits([0.]+[s['soma'][0] for o in observations
                                               for s in o['samples'] if s['soma'][0] >= 0.])
            lt_positive = padded_limits([0., .0117]+[s['lt_potential'] for o in observations
                                                    for s in o['samples'] if s['lt_potential'] >= 0.])
            lt_full = padded_limits([s['lt_potential'] for o in observations for s in o['samples']])
            self.assertLess(lt_full[0], lt_positive[0])
            folder = output/name
            folder.mkdir()
            figures = []
            for index, observation in enumerate(observations):
                for view, bounds in [('soma-positive', soma_positive), ('lt-full', lt_full), ('lt-positive', lt_positive)]:
                    is_lt = view.startswith('lt-')
                    clipped = view != 'lt-full'
                    projected = ({**observation, 'samples': [{**s, 'soma': [s['lt_potential']]}
                                 for s in observation['samples']]} if is_lt else observation)
                    label = '$.LTZone.Potential' if is_lt else '$.Soma1.SumPotential'
                    target = folder/(f'trial-{index:04d}-'+view)
                    target.mkdir()
                    views = render_soma(projected, 0, label, bounds, target,
                        reference_level=.0117 if is_lt else None, include_native_tiles=False,
                        potential_axis_label=label+' [native units; SI unverified]',
                        context_label=('Positive Y detail; negative reset clipped; full range retained separately'
                            if clipped else 'Full LT decision-potential range; negative reset retained'))
                    outside = sum(s['soma'][0] < bounds[0] for s in projected['samples'])
                    if not clipped:
                        self.assertEqual(outside, 0)
                    for rendered in views:
                        self.assertFalse(rendered['downsampling'])
                        with Image.open(target/rendered['files'][0]) as image:
                            self.assertEqual(image.size, (1920, 960))
                    figures.append(dict(sample_id=observation['sample_id'], label=observation['label'],
                        channel=label, view=view, folder=target.name, y_limits=bounds,
                        negative_reset_clipping_explicit=clipped, samples_outside_view=outside,
                        original_sample_count=len(observation['samples']), views=views))
            self.assertEqual(len(figures), 24)
            self.assertEqual(before, {p: hashlib.sha256((case/p).read_bytes()).hexdigest() for p in paths})
            _write(folder/'manifest.json', dict(kind='n0_length_response_scale_companions', schema_version=1,
                source_hashes=before, source_full_range_report=str(case/'index.html'), figures=figures,
                native_samples_changed=False, original_native_time_tiles_retained=True,
                new_model_execution=False, classification_recomputed=False,
                visual_acceptance_complete=False, scientific_verdict=None))
            all_rows.append(dict(run=name, figures=len(figures), samples_unchanged=True))
        _write(output/'index.json', dict(rows=all_rows, trials=16, figure_groups=48,
            scientific_verdict=None, visual_acceptance_complete=False))
