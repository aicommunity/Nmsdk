"""Independent server restoration of the complete recorded Console2 archive.

No model is run and no execution/scientific attestation is invented by restore.
The fixture must be supplied through a declared, hashed validation suite.
"""
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_package
from ..collector_provenance import frozen_digest
from ..composite_primary import filesystem_primary_resolver
from ..native_evidence import load, require
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle


class Console2CompactPrimaryTest(unittest.TestCase):
    def test_complete_archive_restores_and_reaudits_actual_trained_models(self):
        value = os.environ.get('TIMELEARNER_CONSOLE2_COMPACT_PRIMARY')
        require(value is not None, 'console2_compact_primary_fixture_required')
        source = Path(value).resolve(strict=True)
        files = sorted(p for p in source.iterdir() if p.is_file())
        self.assertEqual({p.name for p in files}, {'bundle.json', 'primary.tar.xz',
            'collection-proof.json', 'collection-controller.json',
            'collection-closure.json', 'collection-terminal.json'})
        before = {p.name: frozen_digest(p, 16*1024**2) for p in files}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_sha256'],
            'ab29a831b9a9d879f0c06a5361656adaae44ee8b11caef7304000ccc869f0511')
        self.assertEqual(len(bundle['members']), 1201)
        self.assertEqual(bundle['expanded_bytes'], 884530384)
        self.assertEqual(bundle['archive_bytes'], 6227976)
        with tempfile.TemporaryDirectory(prefix='console2-independent-restore-') as temporary:
            restored = Path(temporary)/'restored'
            receipt = restore_native_bundle(source/'bundle.json', restored,
                compatibility=ALIAS_ADAPTER)
            self.assertEqual(receipt['archive_members_verified'], 1201)
            self.assertEqual(receipt['retained_regular_files'], 1185)
            self.assertEqual(len(receipt['omitted_redundant_aliases']), 16)
            self.assertFalse(receipt['source_archive_modified'])
            self.assertFalse(receipt['native_execution_attested'])
            root = restored/'original-console2-job'
            original = load(root/'controller-result.json')
            self.assertEqual(original['execution'], 'completed')
            self.assertEqual(original['returncode'], 0)
            self.assertTrue(load(root/'worker/terminal.json')['operation_passed'])
            audits = {}
            for name in ('Classic-window-N0', 'Branch-window-N0'):
                directory = root/'worker/native-cold7'/name/'runs/train/native'
                package = load(directory/'train_learned_state.json')
                audit = audit_candidate_window_package(package,
                    external_resolver=filesystem_primary_resolver(directory))
                self.assertTrue(audit['exact'])
                self.assertTrue(audit['certificate_consistent'])
                audits[name] = audit
            # Persist only the small independent reader receipt. Every restored
            # primary byte was checked by the production streaming reader;
            # the expanded temporary cache can then be removed normally.
            proof = dict(restoration=receipt, restored_model_audits=audits,
                original_execution_record=original,
                independent_restoration=True, new_model_execution=False,
                scientific_verdict=None)
            destination = Path(os.environ['TMPDIR'])/'console2-independent-restoration.json'
            with destination.open('x', encoding='utf-8') as stream:
                json.dump(proof, stream, indent=2, allow_nan=False)
                stream.write('\n')
        after = {p.name: frozen_digest(p, 16*1024**2) for p in files}
        self.assertEqual(before, after)
