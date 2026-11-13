"""Independent byte-exact restoration and analysis of the actual Branch Train."""
import os
from pathlib import Path
import tempfile
import unittest

from ..collector_provenance import frozen_digest
from ..native_calibration_worker import _write
from ..native_evidence import EvidenceError, load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..training_search_report import analyze_search_history


class CoupledRecoveryCompactPrimaryTest(unittest.TestCase):
    def test_restored_original_train_keeps_recovery_history_and_rejects_changed_csv(self):
        source = Path(os.environ['TIMELEARNER_COUPLED_TRAIN_PRIMARY']).resolve(strict=True)
        self.assertEqual({p.name for p in source.iterdir()}, {'bundle.json', 'primary.tar.xz'})
        before = {p.name: frozen_digest(p, 128*1024**2) for p in source.iterdir()}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_bytes'], 24114712)
        self.assertEqual(bundle['archive_sha256'],
                         '03d94a94726a976e09abab7a643e807bac4081882f285a429949d8621ed50ce5')
        self.assertEqual(len(bundle['members']), 1214)
        with tempfile.TemporaryDirectory(prefix='coupled-train-primary-', dir=os.environ['TMPDIR']) as temporary:
            root = Path(temporary)/'restored'
            restoration = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restoration['archive_members_verified'], 1214)
            self.assertEqual(restoration['retained_regular_files'], 1212)
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
            self.assertEqual(report['source_summary']['sha256'],
                             '94f28cc3abf9d31bdcf70a2cec653e055b60533e89cae0a84f126b3b2163e060')
            rows = report['recorded_recovery_deliveries']
            transitions = [r['event']['transition'] for r in rows]
            self.assertEqual([t['trial_id'].split('/')[-1] for t in transitions], ['90','95','99','103','107'])
            self.assertEqual([[p['length'] for p in t['full_parameters']] for t in transitions],
                             [[28,28,27,1], [29,28,27,1], [29,29,27,1], [30,29,27,1], [28,27,27,1]])
            self.assertEqual([t['disposition'] for t in transitions], ['cursor_advanced']*4+['invalid_budget_stop'])
            self.assertEqual([t['invalid_after'] for t in transitions], [1,2,3,4,5])
            self.assertEqual(len(report['recorded_candidate_measurements']), 22)
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
        _write(Path(os.environ['TMPDIR'])/'coupled-train-primary-replay.json', dict(
            restoration=restoration, search_report=report, corrupted_extracted_csv_rejected=True,
            original_archive_changed=False, original_m40_paths_available=False,
            new_model_execution=False, scientific_verdict=None))
