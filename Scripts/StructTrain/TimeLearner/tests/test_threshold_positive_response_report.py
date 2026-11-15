"""Companion positive scale for the actual fixed-threshold observations."""
import os
from pathlib import Path
import unittest
from ..native_calibration_worker import _write
from ..native_evidence import load
from ..plotting import padded_limits, render_soma
from ..recognition_metrics import load_diagnostic_evaluation

class ThresholdPositiveResponseReportTest(unittest.TestCase):
    def test_all_patterns_and_channels_keep_native_samples_with_explicit_clipping(self):
        from PIL import Image
        source = Path(os.environ['TIMELEARNER_THRESHOLD_COMPLETED_STUDY']).resolve(strict=True)
        result = load(source/'result.json')
        self.assertTrue(result['baseline_waveforms_equal'])
        self.assertFalse(result['training_completed'])
        _, observations = load_diagnostic_evaluation(source/'runs/candidate/native/evaluation.json')
        self.assertEqual(len(observations),8)
        channels = len(observations[0]['samples'][0]['soma'])
        self.assertTrue(all(len(s['soma']) == channels for o in observations for s in o['samples']))
        output = Path(os.environ['TMPDIR'])/'fixed-threshold-positive-response-gallery'
        output.mkdir()
        threshold = result['proposal']['threshold']
        limits = [padded_limits([0.]+[s['soma'][c] for o in observations
                   for s in o['samples'] if s['soma'][c] >= 0.]) for c in range(channels)]
        lt_limits = padded_limits([0.,threshold]+[s['lt_potential'] for o in observations
                    for s in o['samples'] if s['lt_potential'] >= 0.])
        figures = []
        for index, observation in enumerate(observations):
            for channel in range(channels+1):
                lt = channel == channels
                label = '$.LTZone.Potential' if lt else f'$.Soma{channel+1}.SumPotential'
                projected = ({**observation, 'samples': [{**s, 'soma':[s['lt_potential']]}
                             for s in observation['samples']]} if lt else observation)
                folder = output/(f'trial-{index:04d}-lt-decision' if lt else
                                 f'trial-{index:04d}-soma-{channel+1:03d}')
                folder.mkdir()
                bounds = lt_limits if lt else limits[channel]
                views = render_soma(projected,0 if lt else channel,label,bounds,folder,
                    reference_level=threshold if lt else None, include_native_tiles=False,
                    potential_axis_label=("LT decision potential [model units; SI unverified]" if lt
                        else "Soma SumPotential [model units; SI unverified]"),
                    context_label='Positive-response Y detail; negative reset clipped; see full-range overview')
                self.assertTrue(all(v['time_view'] == 'overview' and not v['downsampling'] for v in views))
                for view in views:
                    with Image.open(folder/view['files'][0]) as image:
                        self.assertEqual(image.size,(1920,960))
                figures.append(dict(sample_id=observation['sample_id'],channel=label,
                    folder=folder.name,y_limits=bounds,negative_samples_outside_view=sum(
                        (s['lt_potential'] if lt else s['soma'][channel]) < bounds[0]
                        for s in observation['samples']),views=views))
        self.assertEqual(len(figures),8*(channels+1))
        _write(output/'manifest.json',dict(kind='native_threshold_positive_response_visual_companion',
            schema_version=1,figures=figures,native_samples_changed=False,
            negative_reset_clipping_explicit=True,full_range_report_required=True,
            native_time_tiles_in_original_report=True,visual_acceptance_complete=False,
            new_model_execution=False,classification_recomputed=False,scientific_verdict=None))
