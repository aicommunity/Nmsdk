"""Replay actual N4 recovery rejections, without changing their Train outcome."""
import json
import os
from pathlib import Path
import unittest

from ..candidate_window_diagnostic_replay import replay
from ..native_evidence import load, require


class CandidateRecoveryDiagnosticReplayNativeTest(unittest.TestCase):
    def test_real_Branch_N4_recovery_windows_and_full_traces_keep_stopped_state(self):
        native = Path(os.environ['TIMELEARNER_RECOVERY_N4_STOPPED_NATIVE']).resolve(strict=True)
        package = load(native/'train_stopped_state.json')
        summary = load(native/'train_stopped_summary.json')
        require(package['schema_version'] == 7 and summary['schema_version'] == 8 and
            package['configuration']['schema_version'] == 8 and
            package['configuration']['model']['branch'] is True and
            len(package['configuration']['model']['inputs']) == 4 and
            summary['outcome'] == 'invalid_observation', 'recovery_replay_real_N4_scope')
        records = package['measurement_archive']['records']
        deliveries = summary['recovery_ledger']['deliveries']
        rejected_ids = {d['event']['group_id'] for d in deliveries}
        rejected = [i for i,r in enumerate(records, 1) if r['group_id'] in rejected_ids]
        self.assertEqual(len(deliveries), 5)
        self.assertEqual(len(rejected), 5)
        self.assertEqual([d['event']['transition']['disposition'] for d in deliveries],
            ['cursor_advanced']*4+['invalid_budget_stop'])
        assigned = records[rejected[0]-1]['method_specification']['assigned_input']
        preceding = [i for i,r in enumerate(records, 1) if i < rejected[0] and
            r['method_specification']['assigned_input'] == assigned and
            r['selection']['geometry']['validity'] == 'valid']
        require(preceding, 'recovery_replay_preceding_assigned_control_missing')
        result = replay(native, [max(preceding), *rejected])
        self.assertEqual(result['original_training_outcome'], 'invalid_observation')
        self.assertEqual(result['package_audit']['package_schema_version'], 7)
        self.assertTrue(result['posthoc_windows'])
        self.assertFalse(result['original_state_rewritten'])
        self.assertFalse(result['new_model_execution'])
        self.assertFalse(result['training_certificate_eligible'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertEqual(result['groups'][0]['windows'][0]['geometry']['validity'], 'valid')
        for group in result['groups'][1:]:
            self.assertEqual(group['windows'][0]['geometry']['validity'], 'missing')
            self.assertIn(group['windows'][1]['geometry']['validity'],
                ('valid', 'missing', 'ambiguous', 'clipped', 'nonrepeatable'))
        # A full-window answer remains a post-hoc diagnostic, even if valid.
        output = Path(os.environ['TMPDIR'])/'recovery-N4-diagnostic-replay.json'
        with output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, allow_nan=False);stream.write('\n')
