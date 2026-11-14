"""Read-only native plots of all eight patterns and each target position."""
import os
from pathlib import Path
import unittest

from ..native_calibration_worker import _write
from ..native_evidence import load
from ..native_pipeline_worker import audit_run_manifest
from ..plotting import padded_limits, render_soma
from ..recognition_metrics import load_diagnostic_evaluation
from ..runtime import file_record


class FixedOrderTemporalReportTest(unittest.TestCase):
    def test_native_inputs_and_responses_with_full_and_positive_scales(self):
        from PIL import Image
        source = Path(os.environ['TIMELEARNER_FIXED_ORDER_COMPLETED']).resolve(strict=True)
        before = {name: file_record(source/name)
                  for name in ('result.json', 'run/run-manifest.json')}
        result = load(source/'result.json')
        self.assertEqual(result['kind'], 'actual_fixed_threshold_order_matrix_result')
        self.assertTrue(result['first_rotation_waveforms_equal'])
        self.assertTrue(result['frozen_model_bytes_equal'])
        self.assertFalse(result['training_completed'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertTrue(audit_run_manifest(source/'run/run-manifest.json')['run_evidence_consistent'])
        _, observations = load_diagnostic_evaluation(source/'run/native/evaluation.json')
        self.assertEqual(len(observations), 64)
        self.assertTrue(all(o['valid'] and o['complete'] for o in observations))
        targets = [i for i, o in enumerate(observations) if o['label'] == 'target']
        self.assertEqual(len(targets), 8)
        self.assertEqual(sorted(i % 8 for i in targets), list(range(8)))
        selected = sorted(set(range(8)) | set(targets))
        self.assertEqual(len(selected), 15)
        channels = len(observations[0]['samples'][0]['soma'])
        self.assertEqual(channels, 4)
        threshold = result['threshold']
        output = Path(os.environ['TMPDIR'])/'fixed-order-temporal-gallery'
        output.mkdir()
        figures = []
        for channel in range(channels + 1):
            lt = channel == channels
            label = '$.LTZone.Potential' if lt else f'$.Soma{channel+1}.SumPotential'
            all_values = [s['lt_potential'] if lt else s['soma'][channel]
                          for o in observations for s in o['samples']]
            full_limits = padded_limits(all_values + ([threshold] if lt else []))
            positive_limits = padded_limits([0.] + ([threshold] if lt else []) +
                                            [v for v in all_values if v >= 0.])
            for index in selected:
                original = observations[index]
                projected = ({**original, 'samples': [{**s, 'soma': [s['lt_potential']]}
                              for s in original['samples']]} if lt else dict(original))
                # Test display uses the maximum of the whole observed response.
                # This is never an assigned-impulse measurement or new verdict.
                soma_channel = 0 if lt else channel
                maximum = max(range(len(projected['samples'])),
                              key=lambda i: projected['samples'][i]['soma'][soma_channel])
                if 0 < maximum < len(projected['samples']) - 1:
                    projected['diagnostic_peak_indices'] = [maximum]
                for scale, limits in [('full', full_limits), ('positive', positive_limits)]:
                    suffix = 'lt-decision' if lt else f'soma-{channel+1:03d}'
                    folder = output/f'trial-{index:04d}-{suffix}-{scale}'
                    folder.mkdir()
                    views = render_soma(projected, soma_channel, label, limits, folder,
                        reference_level=threshold if lt else None, include_native_tiles=False,
                        potential_axis_label=('LT decision potential [model units; SI unverified]' if lt
                            else 'Soma SumPotential [model units; SI unverified]'),
                        context_label=('Positive Y detail; negative reset clipped; see full range' if
                                       scale == 'positive' else 'Full range including negative reset'))
                    self.assertTrue(all(not v['downsampling'] for v in views))
                    for view in views:
                        with Image.open(folder/view['files'][0]) as image:
                            self.assertEqual(image.size, (1920, 960))
                        if view['time_view'] != 'overview':
                            self.assertGreaterEqual(view['minimum_native_tick_pixels_on_zoom'], 8.)
                    figures.append(dict(presentation_index=index, rotation=index//8,
                        position=index%8, sample_id=original['sample_id'], trial_id=original['trial_id'],
                        label=original['label'], channel=label, scale=scale, folder=folder.name,
                        global_response_maximum_sample_index=maximum, views=views))
        self.assertEqual(len(figures), 15*5*2)
        self.assertEqual(before, {name: file_record(source/name) for name in before})
        _write(output/'analysis.json', result['metrics'])
        _write(output/'manifest.json', dict(kind='fixed_order_native_temporal_report',
            schema_version=1, observed_trials=64, plotted_trials=selected, figures=figures,
            scope='all eight patterns in rotation0 and target in each of eight positions',
            shared_scales_computed_over_all_64_trials=True, native_samples_changed=False,
            peak_assignment_changed=False, negative_reset_clipping_explicit=True,
            complete_full_time_views=True, native_peak_details_when_local_scale_needed=True,
            uniform_native_time_tiles=False, new_model_execution=False,
            threshold_selected=False, training_completed=False, scientific_verdict=None,
            visual_acceptance_complete=False))
