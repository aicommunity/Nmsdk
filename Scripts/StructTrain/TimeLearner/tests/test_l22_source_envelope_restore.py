"""Large actual N4 publication roundtrip; readers use restored files only."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from ..composite_package_evidence import audit_composite_package
from ..composite_primary import filesystem_primary_resolver
from ..native_calibration_worker import _write
from ..native_characterization import audit_execution
from ..native_evidence import load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle


class L22SourceEnvelopeRestoreTest(unittest.TestCase):
    def test_actual_large_package_before_original_source_and_five_probe_audits(self):
        package = Path(os.environ['TIMELEARNER_L22_ENVELOPE_PACKAGE']).resolve(strict=True)
        index = load(package/'bundle.json')
        self.assertEqual(len(index['recipes']), 15)
        self.assertEqual(index['literal_fallbacks'], {})
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'restored'
            restored = restore_native_bundle(package/'bundle.json', output, compatibility=ALIAS_ADAPTER)
            self.assertTrue(restored['all_primary_bytes_verified'])
            self.assertEqual(restored['reconstructed_job_files'], 15)
            source = output/'source'
            raw = (source/'train_stopped_state.json').read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                '8b36876b486741d68cabbd47222a221dce9973e5db8473480c360035469ccca7')
            state = load(source/'train_stopped_state.json')
            source_audit = audit_composite_package(state, load(source/'train_stopped_summary.json'),
                external_resolver=filesystem_primary_resolver(source))
            self.assertEqual(source_audit['training_outcome'], 'budget_exhausted')
            study = output/'study/worker/tmp/l22-burst-resistance-study'
            result = load(study/'result.json')
            self.assertEqual(result['source_revision'], state['model_revision'])
            self.assertTrue(result['declared_grid_completed'])
            cases = []
            for name in ('replay', 'matched', 'resistance-1', 'resistance-2', 'resistance-3'):
                audit = audit_execution(study/'runs'/name/'native')
                self.assertEqual(audit['execution'], 'completed')
                self.assertTrue(audit['primary_evidence_checked'])
                cases.append(name)
            _write(Path(os.environ['TMPDIR'])/'L22-envelope-restore-proof.json',
                dict(kind='l22_source_envelope_restore', schema_version=1, restored=restored,
                    source_audit=source_audit, primary_audits=cases,
                    original_members=len(index['members']),
                    package_bytes=sum(p.stat().st_size for p in package.rglob('*') if p.is_file()),
                    original_manifests_rewritten=False, native_execution_attested=False,
                    scientific_verdict=None))
