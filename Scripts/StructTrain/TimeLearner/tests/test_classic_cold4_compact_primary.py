"""Independent byte-exact restoration and analysis of the actual Classic cold4 Train."""
import os
from pathlib import Path
import tempfile
import unittest

from ..collector_provenance import frozen_digest
from ..native_calibration_worker import _write
from ..native_evidence import EvidenceError, load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..training_search_report import analyze_search_history


class ClassicCold4CompactPrimaryTest(unittest.TestCase):
    def test_restored_original_train_keeps_recovery_history_and_rejects_changed_csv(self):
        source = Path(os.environ['TIMELEARNER_CLASSIC_COLD4_PRIMARY']).resolve(strict=True)
        self.assertEqual({p.name for p in source.iterdir()}, {'bundle.json', 'primary.tar.xz'})
        before = {p.name: frozen_digest(p, 128*1024**2) for p in source.iterdir()}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_bytes'], 29285000)
        self.assertEqual(bundle['archive_sha256'],
                         'dd633d3743f082fdb524bb07ec6c0c92197a1eb1ffb3fa2b784316cc146fdd4e')
        self.assertEqual(len(bundle['members']), 910)
        with tempfile.TemporaryDirectory(prefix='classic-cold4-primary-', dir=os.environ['TMPDIR']) as temporary:
            root = Path(temporary)/'restored'
            restoration = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restoration['archive_members_verified'], 910)
            self.assertEqual(restoration['retained_regular_files'], 908)
            self.assertEqual(len(restoration['omitted_redundant_aliases']), 2)
            self.assertFalse(restoration['native_execution_attested'])
            manifests = [root/name for name in bundle['members']
                         if name.endswith('/runs/train/run-manifest.json')]
            self.assertEqual(len(manifests), 1)
            original_request = load(manifests[0].parent/'process/request.json')
            original_native = Path(original_request['arguments'][5])
            self.assertTrue(original_native.is_absolute())
            self.assertFalse(original_native.exists(), 'independent replay must not see original M40 output')
            report = analyze_search_history(manifests[0])
            self.assertEqual(report['schema_version'], 2)
            self.assertEqual(report['outcome'], 'invalid_observation')
            self.assertEqual((report['topology'], report['normalization'], report['input_count']), ('Classic', 'N1', 4))
            self.assertFalse(any(p['within_timing'] and p['within_amplitude']
                                 for p in report['recorded_candidate_measurements']))
            self.assertEqual(report['source_summary']['sha256'],
                             '19642e90bcbf66a1440833c97fadd41ffac245086a5718bfa86bb303bceacbef')
            rows = report['recorded_recovery_deliveries']
            transitions = [r['event']['transition'] for r in rows]
            self.assertEqual([t['trial_id'].split('/')[-1] for t in transitions], ['18','26','58','66','74'])
            self.assertEqual([[p['length'] for p in t['full_parameters']] for t in transitions],
                             [[54,1,1,1], [52,1,1,1], [50,1,1,1], [48,1,1,1], [45,1,1,1]])
            self.assertEqual([t['disposition'] for t in transitions], ['cursor_advanced']*4+['invalid_budget_stop'])
            self.assertEqual([t['invalid_after'] for t in transitions], [1,2,3,4,5])
            self.assertEqual(len(report['recorded_candidate_measurements']), 14)
            self.assertEqual(report['final_verification_group_ids'], [])
            self.assertFalse(report['attempt_total_independently_recounted'])
            self.assertIsNone(report['scientific_verdict'])
            manifest = load(manifests[0])
            csv = next(r['path'] for r in manifest['artifacts'] if r['path'].endswith('.csv'))
            with (manifests[0].parent/csv).open('ab') as stream:
                stream.write(b'corrupt,extracted,primary\n')
            with self.assertRaisesRegex(EvidenceError, 'pipeline_run_artifact_changed'):
                analyze_search_history(manifests[0])
        self.assertEqual(before, {p.name: frozen_digest(p, 128*1024**2) for p in source.iterdir()})
        _write(Path(os.environ['TMPDIR'])/'classic-cold4-primary-replay.json', dict(
            restoration=restoration, search_report=report, corrupted_extracted_csv_rejected=True,
            original_archive_changed=False, original_m40_paths_available=False,
            new_model_execution=False, scientific_verdict=None))
