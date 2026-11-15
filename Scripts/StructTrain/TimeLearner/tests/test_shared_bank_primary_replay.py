"""Restore the complete actual Branch intervention before production DATA audit."""
import os
from pathlib import Path
import tempfile
import unittest

from ..native_calibration_worker import _write
from ..native_characterization import audit_execution
from ..native_evidence import load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..primary_recompression import _snapshot


class SharedBankPrimaryReplayTest(unittest.TestCase):
    def test_restore_every_original_byte_then_audit_all_three_native_runs(self):
        package = Path(os.environ['TIMELEARNER_SHARED_BANK_PRIMARY']).resolve(strict=True)
        before = _snapshot(package)
        index = load(package/'bundle.json')
        self.assertEqual(len(index['members']), 2090)
        self.assertEqual(len(index['recipes']), 9)
        self.assertEqual(index['literal_fallbacks'], {})
        audits = {}
        with tempfile.TemporaryDirectory(prefix='shared-bank-primary-', dir=os.environ['TMPDIR']) as temporary:
            root = Path(temporary)/'restored'
            restored = restore_native_bundle(package/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertTrue(restored['all_primary_bytes_verified'])
            self.assertEqual(restored['restored_files'], 2087)
            self.assertFalse(restored['run_manifests_rewritten'])
            self.assertFalse(restored['native_execution_attested'])
            result = load(root/'study/result.json')
            self.assertEqual(result['kind'], 'native_burst_resistance_study_result')
            self.assertEqual(result['physical_bank_owners'], [0, 1, 2])
            self.assertEqual(result['source_geometry'], [27, 27, 27, 1])
            self.assertEqual([r['name'] for r in result['rows']], ['replay', 'matched', 'resistance-1'])
            for row in result['rows']:
                self.assertTrue(row['observation_complete'])
                self.assertEqual(row['sample_count'], 3601)
                self.assertTrue(row['global_maxima_are_not_assigned_impulse_measurements'])
                audit = audit_execution(root/'study/runs'/row['name']/'native')
                self.assertTrue(audit['primary_evidence_checked'])
                self.assertEqual(audit['execution'], 'completed')
                audits[row['name']] = audit
        self.assertEqual(_snapshot(package), before)
        _write(Path(os.environ['TMPDIR'])/'shared-bank-primary-replay-proof.json', dict(
            restoration=restored, native_data_audits=audits, source_package_changed=False,
            new_native_execution=False, scientific_verdict=None))
