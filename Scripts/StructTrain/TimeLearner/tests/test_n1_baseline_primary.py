"""Worker-only independent replay of the complete native N1 baseline probes."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..stock_cold_primary import audit_result


class N1BaselinePrimaryTest(unittest.TestCase):
    def test_all_eight_original_probes_restore_and_missing_trace_is_rejected(self):
        source = Path(os.environ['TIMELEARNER_N1_BASELINE_PRIMARY']).resolve(strict=True)
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_bytes'], 133872)
        self.assertEqual(bundle['archive_sha256'],
                         '85342b1a6f98ec7a856feafcd0cee8f1282917c0eccea5e4d9237a85777b9266')
        self.assertEqual(len(bundle['members']), 342)
        original_digest = hashlib.sha256((source/'primary.tar.xz').read_bytes()).hexdigest()
        self.assertEqual(original_digest, bundle['archive_sha256'])
        with tempfile.TemporaryDirectory(prefix='n1-baseline-independent-') as temporary:
            root = Path(temporary)/'restored'
            restored = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restored['archive_members_verified'], 342)
            self.assertEqual(len(restored['omitted_redundant_aliases']), 8)
            self.assertFalse(restored['native_execution_attested'])
            case = root/'case'
            self.assertEqual(load(case/'request.json')['job_id'], 's11-n1-before-cold4-probes8-elder-a1')
            self.assertEqual(load(case/'controller-result.json')['execution'], 'completed')
            self.assertTrue(load(case/'worker/terminal.json')['operation_passed'])
            self.assertTrue(load(case/'closure-and-reservation.json')['closure']['all_processes_closed'])
            data = case/'worker/native-stock-cold4/result'
            result = audit_result(data)
            self.assertEqual(result['complete_probes'], 8)
            self.assertEqual({r['topology'] for r in result['rows']}, {'Classic', 'Branch'})
            for row in result['rows']:
                self.assertFalse(row['physical']['lt_membrane'])
                self.assertEqual(row['physical']['initial_threshold'], 100.)
            trace = data/'runs/Classic-cold-stock-input0/native/probe_trial_1.csv'
            trace.unlink()
            with self.assertRaises((EvidenceError, OSError)):
                audit_result(data)
        self.assertEqual(hashlib.sha256((source/'primary.tar.xz').read_bytes()).hexdigest(), original_digest)
