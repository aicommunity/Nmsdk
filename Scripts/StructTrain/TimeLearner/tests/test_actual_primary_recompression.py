"""Actual large primary package: compression and full production restoration."""
import os
from pathlib import Path
import tempfile
import unittest

from ..native_calibration_worker import _write
from ..native_evidence import load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..primary_recompression import recompress


class ActualPrimaryRecompressionTest(unittest.TestCase):
    def test_actual_envelopes_restore_all_original_bytes_after_container_recompression(self):
        source = Path(os.environ['TIMELEARNER_ENVELOPED_PRIMARY_TO_RECOMPRESS']).resolve(strict=True)
        root = Path(os.environ['TMPDIR'])
        output = root/'recompressed-threshold-primary'
        result = recompress(source, output)
        self.assertTrue(result['tar_stream_identical'])
        self.assertTrue(result['recipe_bytes_unchanged'])
        self.assertFalse(result['source_changed'])
        self.assertLess(result['archive_bytes'], 100*1024**2)
        before, after = load(source/'bundle.json'), load(output/'bundle.json')
        self.assertEqual(after['members'], before['members'])
        self.assertEqual(after['recipes'], before['recipes'])
        with tempfile.TemporaryDirectory(prefix='recompressed-primary-restore-', dir=root) as temporary:
            restored = restore_native_bundle(output/'bundle.json', Path(temporary)/'restored',
                                             compatibility=ALIAS_ADAPTER)
            self.assertTrue(restored['all_primary_bytes_verified'])
            self.assertFalse(restored['run_manifests_rewritten'])
            self.assertFalse(restored['native_execution_attested'])
        _write(root/'primary-recompression-proof.json', dict(recompression=result,
            restoration=restored, new_model_execution=False, scientific_verdict=None))
