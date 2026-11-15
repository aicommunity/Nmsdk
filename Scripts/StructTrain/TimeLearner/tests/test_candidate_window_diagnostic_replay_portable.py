"""Restore the real Git primary and replay legacy6 using the current dispatcher."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_diagnostic_replay import replay
from ..collector_provenance import frozen_digest
from ..native_evidence import load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle


class CandidateWindowDiagnosticReplayPortableTest(unittest.TestCase):
    def test_actual_legacy6_git_primary_keeps_recorded_and_full_window_results(self):
        source = Path(os.environ['TIMELEARNER_DIAGNOSTIC_LEGACY6_BUNDLE']).resolve(strict=True)
        before = {p.name:frozen_digest(p, 128*1024**2) for p in source.iterdir() if p.is_file()}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_sha256'],
            'e541de403a9b9600f35a3d926599529d499110c3ae4e127e66acc52c9fc9e4d7')
        with tempfile.TemporaryDirectory(prefix='legacy6-diagnostic-primary-') as temporary:
            root = Path(temporary)/'restored'
            restoration = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restoration['archive_members_verified'], 463)
            native = root/'original-train/worker/native-stock-cold7/Classic-stock-cold7-N1/runs/train/native'
            self.assertEqual(load(native/'train_stopped_state.json')['schema_version'], 6)
            result = replay(native, [12, 14, 18])
            self.assertEqual(result['original_training_outcome'], 'invalid_observation')
            self.assertEqual(result['package_audit']['native_probes'], 108)
            self.assertEqual([g['windows'][0]['geometry']['validity'] for g in result['groups']],
                ['valid', 'missing', 'missing'])
            self.assertEqual([g['windows'][1]['geometry']['validity'] for g in result['groups']],
                ['valid', 'ambiguous', 'ambiguous'])
            self.assertFalse(result['new_model_execution'])
            self.assertFalse(result['original_state_rewritten'])
            self.assertFalse(result['training_certificate_eligible'])
            self.assertIsNone(result['scientific_verdict'])
        self.assertEqual(before,
            {p.name:frozen_digest(p, 128*1024**2) for p in source.iterdir() if p.is_file()})
        with (Path(os.environ['TMPDIR'])/'legacy6-diagnostic-replay.json').open('x', encoding='utf-8') as stream:
            json.dump(dict(restoration=restoration, replay=result), stream, indent=2, allow_nan=False)
            stream.write('\n')
