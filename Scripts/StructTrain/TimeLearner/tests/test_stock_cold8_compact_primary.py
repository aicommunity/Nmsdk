"""Independently restore both actual stopped N4 trains from Git primary data."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..collector_provenance import frozen_digest
from ..composite_primary import filesystem_primary_resolver
from ..native_evidence import EvidenceError, load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..stock_threshold_study import audit_final_stock


class StockCold8CompactPrimaryTest(unittest.TestCase):
    def test_restore_both_real_N4_trains_and_reject_changed_primary(self):
        source = Path(os.environ['TIMELEARNER_STOCK_COLD8_COMPACT_PRIMARY']).resolve(strict=True)
        before = {p.name: frozen_digest(p, 128*1024**2)
                  for p in source.iterdir() if p.is_file()}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_sha256'],
            'fbffa754e4f6ecf18941e5b0112dc67db025ff5dc818c636eacf561841328c7c')
        self.assertEqual(bundle['archive_bytes'], 24627936)
        outcomes = {}
        with tempfile.TemporaryDirectory(prefix='stock-cold8-primary-independent-') as temporary:
            root = Path(temporary)/'restored'
            restoration = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restoration['archive_members_verified'], len(bundle['members']))
            self.assertFalse(restoration['native_execution_attested'])
            original = root/'case'
            self.assertEqual(load(original/'controller-result.json')['execution'], 'completed')
            self.assertTrue(load(original/'worker/terminal.json')['operation_passed'])
            work = original/'worker/native-stock-cold8'
            for topology, groups, lengths in [('Classic', 24, [7, 1, 1, 1]),
                                               ('Branch', 28, [7, 7, 7, 1])]:
                with self.subTest(topology=topology):
                    case = topology+'-stock-cold8-N1'
                    result = load(work/case/'index.json')
                    self.assertEqual(result['validity'], 'valid')
                    self.assertFalse(result['classification_assessed'])
                    self.assertIsNone(result['scientific_verdict'])
                    native = work/case/'runs/train/native'
                    package = load(native/'train_stopped_state.json')
                    summary = load(native/'train_stopped_summary.json')
                    audit = audit_candidate_window_recovery_package(package, summary,
                        external_resolver=filesystem_primary_resolver(native))
                    self.assertEqual(audit['training_outcome'], 'invalid_observation')
                    self.assertEqual(audit['logical_groups'], groups)
                    self.assertEqual(audit['native_probes'], groups*6)
                    self.assertFalse(audit['certificate_consistent'])
                    self.assertIsNone(audit['exact'])
                    self.assertFalse(audit['live_authority_restored'])
                    self.assertEqual([row['length'] for row in package['trained_inputs']], lengths)
                    deliveries = package['recovery_ledger']['deliveries']
                    self.assertEqual([d['event']['transition']['disposition'] for d in deliveries],
                        ['cursor_advanced']*4+['invalid_budget_stop'])
                    initial = load(work/case/'runs/preflight/native/initial-state.json')['identity']
                    physics = audit_final_stock(initial, package['neuron']['graph']['identity'])
                    primary = native/package['measurement_archive']['records'][-1]['raw_trials'][0]['primary_ref']['relative_path']
                    with primary.open('ab') as stream:
                        stream.write(b'corrupt,actual,primary\n')
                    with self.assertRaises(EvidenceError):
                        audit_candidate_window_recovery_package(package, summary,
                            external_resolver=filesystem_primary_resolver(native))
                    outcomes[topology] = dict(package_audit=audit, physical_audit=physics,
                        corrupt_extracted_primary_rejected=True)
        self.assertEqual(before, {p.name: frozen_digest(p, 128*1024**2)
                                  for p in source.iterdir() if p.is_file()})
        receipt = dict(restoration=restoration, cases=outcomes,
            original_archive_changed=False, new_model_execution=False, scientific_verdict=None)
        with (Path(os.environ['TMPDIR'])/'stock-cold8-primary-independent-restoration.json').open('x', encoding='utf-8') as stream:
            json.dump(receipt, stream, indent=2, allow_nan=False);stream.write('\n')
