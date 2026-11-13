"""Independent DATA replay of the actual stopped Branch N4 full-domain Train."""
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..collector_provenance import frozen_digest
from ..composite_primary import filesystem_primary_resolver
from ..native_calibration_worker import _write
from ..native_evidence import EvidenceError, load
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..stock_threshold_study import audit_final_stock


class BranchFullDomainCompactPrimaryTest(unittest.TestCase):
    def test_actual_model_and_all_primary_groups_restore_without_original_worker(self):
        source = Path(os.environ['TIMELEARNER_BRANCH_FULL_DOMAIN_PRIMARY']).resolve(strict=True)
        self.assertEqual({p.name for p in source.iterdir()}, {'bundle.json', 'primary.tar.xz'})
        original = Path('/media/user/Data/TimeLearnerRefactor/readbacks/s07-branch-full-domain-cold4-m40-a1')
        self.assertFalse(original.exists(), 'Run on a separate worker without the original source directory')
        before = {p.name: frozen_digest(p, 128*1024**2) for p in source.iterdir()}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_sha256'],
                         '8e98f2f87ada41e331b7941b874b656d20c9f231e97cf76a8f0ba5965c8cee56')
        self.assertEqual(bundle['archive_bytes'], 44060132)
        self.assertEqual(len(bundle['members']), 2164)
        with tempfile.TemporaryDirectory(prefix='branch-full-domain-primary-') as temporary:
            root = Path(temporary)/'restored'
            restoration = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restoration['archive_members_verified'], 2164)
            self.assertEqual(restoration['retained_regular_files'], 2162)
            self.assertEqual(len(restoration['omitted_redundant_aliases']), 2)
            self.assertFalse(restoration['native_execution_attested'])
            train = root/'original-train'
            self.assertEqual(load(train/'controller-result.json')['execution'], 'completed')
            self.assertTrue(load(train/'worker/terminal.json')['operation_passed'])
            self.assertTrue(load(train/'closure-and-reservation.json')['closure']['all_processes_closed'])
            case = train/'worker/native-full-domain/Branch-stock-cold8-N1'
            native = case/'runs/train/native'
            package = load(native/'train_stopped_state.json')
            summary = load(native/'train_stopped_summary.json')
            audit = audit_candidate_window_recovery_package(package, summary,
                external_resolver=filesystem_primary_resolver(native))
            self.assertEqual(audit['model_revision'],
                'fea609e0651ccf779b58a9321e8d4008e984db768ce1167cdcc1406d1a03280d')
            self.assertEqual(audit['training_outcome'], 'budget_exhausted')
            self.assertEqual(audit['logical_groups'], 108)
            self.assertEqual(audit['native_probes'], 648)
            self.assertFalse(audit['certificate_consistent'])
            self.assertIsNone(audit['exact'])
            self.assertFalse(audit['live_authority_restored'])
            self.assertEqual([p['length'] for p in package['trained_inputs']], [27, 27, 27, 1])
            self.assertEqual(package['configuration']['search']['tolerances'],
                dict(amplitude_absolute=1e-5, amplitude_relative=0., sync=.02))
            self.assertEqual(len(summary['candidates']), 51)
            self.assertEqual(summary['rejections'], [])
            self.assertEqual(summary['final_group_ids'], [])
            initial = load(case/'runs/preflight/native/initial-state.json')['identity']
            physics = audit_final_stock(initial, package['neuron']['graph']['identity'])
            # Break the extracted external mirror, not the archive or live source.
            ref = package['measurement_archive']['records'][0]['raw_trials'][0]['primary_ref']['relative_path']
            with (native/ref).open('ab') as stream:
                stream.write(b'corrupt,external,primary\n')
            with self.assertRaises(EvidenceError):
                audit_candidate_window_recovery_package(package, summary,
                    external_resolver=filesystem_primary_resolver(native))
        self.assertEqual(before, {p.name: frozen_digest(p, 128*1024**2) for p in source.iterdir()})
        _write(Path(os.environ['TMPDIR'])/'branch-full-domain-independent-restoration.json',
            dict(restoration=restoration, package_audit=audit, physical_audit=physics,
                 original_archive_changed=False, corrupted_external_primary_rejected=True,
                 new_model_execution=False, scientific_verdict=None))
