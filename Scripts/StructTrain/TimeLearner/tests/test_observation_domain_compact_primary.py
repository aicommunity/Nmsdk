"""Restore actual full-domain N4 data; preserve failure and stopped outcomes.

Server-only DATA replay. No native execution, checkpoint authority or scientific
classification is inferred from a self-consistent saved model.
"""
from contextlib import contextmanager
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


class ObservationDomainCompactPrimaryTest(unittest.TestCase):
    @contextmanager
    def restored(self, role, expected_sha, expected_bytes, expected_members):
        source = Path(os.environ['TIMELEARNER_OBSERVATION_DOMAIN_'+role+'_PRIMARY']).resolve(strict=True)
        before = {p.name: frozen_digest(p, 128*1024**2)
                  for p in source.iterdir() if p.is_file()}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_sha256'], expected_sha)
        self.assertEqual(bundle['archive_bytes'], expected_bytes)
        self.assertEqual(len(bundle['members']), expected_members)
        origin = load(source/'ORIGIN.json')
        self.assertEqual(origin['archive_sha256'], expected_sha)
        self.assertEqual(origin['native_root'], '8362d58f4d6576a0c8b0cc7633270976dff1df7b')
        self.assertEqual(origin['native_pulselib'], '1110808f4ad1f67538dadc6fe1d3f097e00c0630')
        try:
            with tempfile.TemporaryDirectory(prefix='observation-domain-primary-') as temporary:
                root = Path(temporary)/'restored'
                restoration = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
                self.assertEqual(restoration['archive_members_verified'], expected_members)
                self.assertFalse(restoration['native_execution_attested'])
                yield root/'case', restoration
        finally:
            self.assertEqual(before, {p.name: frozen_digest(p, 128*1024**2)
                                      for p in source.iterdir() if p.is_file()})

    def audit_model(self, folder, outcome, groups, lengths, revision, deliveries):
        result = load(folder/'index.json')
        self.assertEqual((result['execution'], result['validity']), ('completed', 'valid'))
        self.assertFalse(result['classification_assessed'])
        self.assertIsNone(result['scientific_verdict'])
        native = folder/'runs/train/native'
        package = load(native/'train_stopped_state.json')
        summary = load(native/'train_stopped_summary.json')
        audit = audit_candidate_window_recovery_package(package, summary,
            external_resolver=filesystem_primary_resolver(native))
        self.assertEqual(audit['training_outcome'], outcome)
        self.assertEqual(audit['logical_groups'], groups)
        self.assertEqual(audit['native_probes'], groups*6)
        self.assertEqual(audit['model_revision'], revision)
        self.assertFalse(audit['certificate_consistent'])
        self.assertIsNone(audit['exact'])
        self.assertFalse(audit['live_authority_restored'])
        self.assertFalse(audit['native_execution_verified'])
        self.assertEqual([row['length'] for row in package['trained_inputs']], lengths)
        config = package['configuration']
        self.assertEqual(config['model']['normalization'], 'N1')
        self.assertEqual(config['search']['tolerances'],
            dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
        policy = config['composite_measurement']['candidate_window_policy']['inputs']
        candidates = 0
        for record in package['measurement_archive']['records']:
            method = record['method_specification']; frame = method['candidate_frame']
            if frame is None:
                continue  # Reference capture uses its original declared windows.
            row = policy[method['assigned_input']]
            self.assertEqual(frame['first_frame'], 0)
            self.assertEqual(frame['first_frame'], row['hard_first_frame'])
            self.assertEqual(frame['last_frame'], row['hard_last_frame'])
            candidates += 1
        self.assertGreater(candidates, 0)
        ledger = package['recovery_ledger']['deliveries']
        self.assertEqual([row['event']['transition']['disposition'] for row in ledger], deliveries)
        initial = load(folder/'runs/preflight/native/initial-state.json')['identity']
        physics = audit_final_stock(initial, package['neuron']['graph']['identity'])
        # Mutate only a temporary extracted copy. The external mirror must remain
        # authoritative even though the package also embeds the original bytes.
        primary = native/package['measurement_archive']['records'][-1]['raw_trials'][0]['primary_ref']['relative_path']
        with primary.open('ab') as stream:
            stream.write(b'corrupt,actual,primary\n')
        with self.assertRaises(EvidenceError):
            audit_candidate_window_recovery_package(package, summary,
                external_resolver=filesystem_primary_resolver(native))
        return dict(package_audit=audit, physical_audit=physics,
                    full_domain_candidates=candidates, corrupt_external_primary_rejected=True)

    def receipt(self, name, restoration, cases):
        value = dict(restoration=restoration, cases=cases, original_archive_changed=False,
                     new_native_execution=False, scientific_verdict=None)
        with (Path(os.environ['TMPDIR'])/name).open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, allow_nan=False);stream.write('\n')

    def test_combined_keeps_classic_ambiguity_and_branch_timeout(self):
        with self.restored('COMBINED',
                '22d409fd09a33ca038f289d0236c5bbc893f98f54afe88db4869c5a1bf2a8385',
                42246064, 2279) as (case, restoration):
            self.assertEqual(load(case/'controller-result.json')['execution'], 'process_error')
            self.assertFalse(load(case/'worker/terminal.json')['operation_passed'])
            validation = load(case/'worker/validation/result.json')
            self.assertEqual(validation['executed_tests'], 2)
            self.assertEqual(len(validation['failures']), 1)
            self.assertEqual(validation['errors'], [])
            work = case/'worker/native-full-domain'
            classic = self.audit_model(work/'Classic-stock-cold8-N1', 'invalid_observation',
                42, [45, 1, 1, 1],
                '35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263',
                ['cursor_advanced']*4+['invalid_budget_stop'])
            branch = work/'Branch-stock-cold8-N1'
            result = load(branch/'index.json')
            self.assertEqual((result['execution'], result['validity']), ('timeout', 'unverified_execution'))
            for field in ('package_path', 'package_audit', 'physical_audit', 'scientific_verdict'):
                self.assertIsNone(result[field])
            self.assertFalse(result['classification_assessed'])
            native = branch/'runs/train/native'
            self.assertFalse((native/'train_stopped_state.json').exists())
            self.assertFalse((native/'train_stopped_summary.json').exists())
            self.assertEqual(len(list(native.glob('**/*.csv'))), 652)
            self.receipt('observation-domain-combined-independent.json', restoration,
                dict(Classic=classic, Branch=dict(execution='timeout', validity='unverified_execution',
                     training_outcome=None, complete_model_available=False, retained_csv=652)))

    def test_branch_retry_keeps_valid_budget_exhausted_model(self):
        with self.restored('BRANCH',
                'd507026724bb0746bee41f2f75d5d042c289747377ca286217efcd267cde80d4',
                43079920, 2107) as (case, restoration):
            self.assertEqual(load(case/'controller-result.json')['execution'], 'completed')
            self.assertTrue(load(case/'worker/terminal.json')['operation_passed'])
            branch = self.audit_model(case/'worker/native-full-domain-branch/Branch-stock-cold8-N1',
                'budget_exhausted', 105, [27, 27, 26, 1],
                'efc6bacd25770cb3ccde41b952b2e09638296e401be88e2b6f5f7bd3548e9ecd', [])
            self.receipt('observation-domain-branch-independent.json', restoration, dict(Branch=branch))
