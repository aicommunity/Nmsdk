"""Read-only temporal report of the matched current-runtime N0 geometry pair."""
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_calibration_worker import _write
from ..native_evidence import load


class N0GeometryTrainingReportTest(unittest.TestCase):
    def test_shared_prefix_divergence_and_best_measured_groups(self):
        from PIL import Image
        roots = {role: Path(os.environ['TIMELEARNER_N0_GEOMETRY_'+role.upper()]).resolve(strict=True)
                 for role in ('before', 'after')}
        summaries = {role: load(root/'train_stopped_summary.json') for role, root in roots.items()}
        fields = ('input_index', 'full_parameters', 'parameters', 'amplitude_residual',
                  'timing_low', 'timing_high', 'within_amplitude', 'within_timing')
        before, after = (summaries[role]['candidates'] for role in ('before', 'after'))
        prefix = 0
        for left, right in zip(before, after):
            if any(left[field] != right[field] for field in fields):
                break
            prefix += 1
        self.assertEqual(prefix, 31)
        for field in ('capture_revision', 'source_origin', 'owner_family_binding'):
            self.assertEqual(summaries['before'][field], summaries['after'][field])
        for role, native in roots.items():
            summary = summaries[role]
            self.assertEqual(summary['outcome'], 'budget_exhausted')
            self.assertEqual(summary['reason'], 'native_training_time_budget_exhausted')
            self.assertIsNone(summary['certificate'])
            self.assertEqual(summary['final_group_ids'], [])
            candidates = summary['candidates']
            self.assertEqual(len(candidates), 36 if role == 'before' else 37)
            self.assertFalse(any(c['within_timing'] and c['within_amplitude'] for c in candidates))
            best = min((c for c in candidates if c['within_timing']),
                       key=lambda c: abs(c['amplitude_residual']))
            selected = [candidates[prefix-1], candidates[prefix], best]
            package = load(native/'train_stopped_state.json')
            self.assertIsNone(package['certificate'])
            records = package['measurement_archive']['records']
            groups = [next(i for i, r in enumerate(records, 1)
                           if r['group_id'] == c['measurement_group_id']) for c in selected]
            self.assertEqual(len(set(groups)), 3)
            output = Path(os.environ['TMPDIR'])/('N0-geometry-'+role+'-training-gallery')
            report = render(native, output, groups, native_window_zooms=True)
            self.assertEqual({f['channel'] for f in report['figures']}, {0})
            self.assertEqual(len(report['figures']), 12)
            self.assertFalse(report['downsampling'])
            self.assertFalse(report['training_certificate_eligible'])
            self.assertFalse(report['visual_acceptance_complete'])
            self.assertTrue(all(g['complete_group'] and len(g['recorded_trials']) == 6
                                and all(t['complete'] for t in g['recorded_trials'])
                                for g in report['groups']))
            for figure in report['figures']:
                if figure['view'].endswith('-native'):
                    self.assertGreaterEqual(figure['minimum_native_tick_pixels'], 8.)
                with Image.open(output/figure['files'][0]) as image:
                    self.assertGreaterEqual(image.width, 2800)
                    self.assertGreaterEqual(image.height, 2800)
            _write(output/'selection.json', dict(kind='matched_n0_geometry_training_selection',
                schema_version=1, role=role, exact_common_candidate_prefix=prefix,
                selected_candidates=selected, selected_groups=groups,
                terminal_parameters=summary['actual_parameters'], new_model_execution=False,
                classification_assessed=False, scientific_verdict=None))
