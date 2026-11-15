"""Read-only paired evidence for the declared rejected-window length coverage study.

A passing test validates the comparison and readable raw plots. It is never a
training certificate or a successful classifier.
"""
import hashlib
import os
from pathlib import Path
import unittest

from ..composite_package_evidence import audit_composite_package
from ..composite_primary import filesystem_primary_resolver
from ..composite_training_temporal import render
from ..native_calibration_worker import _write
from ..native_evidence import load, require


class N0RecoveryCoverageTrainingReportTest(unittest.TestCase):
    def test_same_pre_rejection_measurements_and_actual_wide_candidates(self):
        controls = Path(os.environ['TIMELEARNER_N0_COVERAGE_REPORT_CONTROLS']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration) == {'before', 'after'}, 'n0_coverage_report_controls')
        roots = {role: Path(path).resolve(strict=True) for role, path in declaration.items()}
        packages, summaries, bindings = {}, {}, {}
        for role, root in roots.items():
            paths = [root/name for name in ('train_stopped_state.json', 'train_learned_state.json')
                     if (root/name).is_file()]
            require(len(paths) == 1, 'n0_coverage_report_package_inventory')
            path = paths[0]
            summary = path.with_name(path.name.replace('_state.', '_summary.'))
            packages[role], summaries[role] = load(path), load(summary)
            bindings[role] = dict(package_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                  summary_sha256=hashlib.sha256(summary.read_bytes()).hexdigest())
        before, after = (summaries[role] for role in ('before', 'after'))
        self.assertEqual(packages['before']['configuration'], packages['after']['configuration'])
        for field in ('capture_revision', 'source_origin', 'owner_family_binding'):
            self.assertEqual(before[field], after[field])
        self.assertEqual(before['outcome'], 'invalid_observation')
        self.assertIsNone(before['certificate'])
        old_candidates, new_candidates = before['candidates'], after['candidates']
        self.assertEqual(len(old_candidates), 13)
        self.assertGreaterEqual(len(new_candidates), len(old_candidates))
        fields = ('input_index', 'full_parameters', 'parameters', 'amplitude_residual',
                  'timing_low', 'timing_high', 'within_amplitude', 'within_timing')
        for left, right in zip(old_candidates, new_candidates):
            self.assertEqual({k: left[k] for k in fields}, {k: right[k] for k in fields})
        events = {role: [d['event'] for d in s['recovery_ledger']['deliveries']]
                  for role, s in summaries.items()}
        self.assertEqual([e['transition']['full_parameters'][1]['length']
                          for e in events['before']], [28, 29, 30, 31, 32])
        self.assertGreaterEqual(len(events['after']), 1)
        self.assertEqual(events['after'][0]['transition']['full_parameters'],
                         events['before'][0]['transition']['full_parameters'])
        far_groups = [c['measurement_group_id'] for c in new_candidates
                      if c['input_index'] == 1 and c['parameters']['length'] == 100]
        far_groups += [e['group_id'] for e in events['after']
                       if e['transition']['candidate_input_index'] == 1 and
                       e['transition']['full_parameters'][1]['length'] == 100]
        self.assertTrue(far_groups)
        records = packages['after']['measurement_archive']['records']
        ordinals = {r['group_id']: i for i, r in enumerate(records, 1)}
        selected = [new_candidates[12]['measurement_group_id'], events['after'][0]['group_id'],
                    far_groups[0], events['after'][-1]['group_id']]
        # Bind every plot to an actually archived group, never an invented wave.
        selected = list(dict.fromkeys(ordinals[g] for g in selected))
        output = Path(os.environ['TMPDIR'])/'n0-recovery-coverage-training-gallery'
        report = render(roots['after'], output, selected, native_window_zooms=True,
                        allow_incomplete_groups=True)
        before_audit = audit_composite_package(packages['before'], before,
                            external_resolver=filesystem_primary_resolver(roots['before']))
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertFalse(report['visual_acceptance_complete'])
        self.assertIsNone(report['scientific_verdict'])
        from PIL import Image
        for figure in report['figures']:
            if figure['view'].endswith('-native'):
                self.assertGreaterEqual(figure['minimum_native_tick_pixels'], 8.)
            with Image.open(output/figure['files'][0]) as image:
                self.assertGreaterEqual(image.width, 2800)
                self.assertGreaterEqual(image.height, 2800)
        facts = {}
        for role, summary in summaries.items():
            candidates = summary['candidates']
            transitions = [e['transition'] for e in events[role]]
            facts[role] = dict(outcome=summary['outcome'], reason=summary['reason'],
                certificate=summary['certificate'], scalar_measurements=len(candidates),
                scalar_input_indices=sorted({c['input_index'] for c in candidates}),
                rejected_transitions=transitions, terminal_parameters=summary['actual_parameters'],
                terminal_has_consumed_scalar=any(c['full_parameters']==summary['actual_parameters']
                                                 for c in candidates),
                jointly_ready_candidates=sum(c['within_timing'] and c['within_amplitude']
                                              for c in candidates))
        _write(output/'comparison.json', dict(kind='timelearner_n0_rejected_length_coverage_comparison',
            schema_version=1, same_complete_configuration=True, unchanged_scalar_prefix=13,
            before_audit=before_audit, after_audit=report['package_audit'], bindings=bindings,
            facts=facts, selected_groups=selected, classification_assessed=False,
            scientific_verdict=None))
