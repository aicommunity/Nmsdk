"""Independent restore/audit of the actual new N1 Classic diagnostic state."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_package
from ..collector_provenance import frozen_digest
from ..composite_primary import filesystem_primary_resolver
from ..native_evidence import EvidenceError, load, require
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..stock_threshold_study import audit_final_stock


class N1ClassicCompactPrimaryTest(unittest.TestCase):
    def test_restore_actual_failed_train_replay_graph_and_reject_corrupt_primary(self):
        value = os.environ.get('TIMELEARNER_N1_CLASSIC_COMPACT_PRIMARY')
        require(value is not None, 'n1_classic_compact_primary_fixture_required')
        source = Path(value).resolve(strict=True)
        names = {'bundle.json', 'primary.tar.xz', 'collection-proof.json',
                 'collection-controller.json', 'collection-closure.json', 'collection-terminal.json'}
        self.assertEqual({p.name for p in source.iterdir()}, names)
        before = {n: frozen_digest(source/n, 128*1024**2) for n in names}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_sha256'],
                         'e541de403a9b9600f35a3d926599529d499110c3ae4e127e66acc52c9fc9e4d7')
        self.assertEqual(len(bundle['members']), 463)
        self.assertEqual(bundle['archive_bytes'], 10194852)
        self.assertTrue(load(source/'collection-terminal.json')['operation_passed'])
        for observations in (load(source/'collection-proof.json')[k] for k in ('before', 'after')):
            self.assertEqual(len(observations), 3)
            self.assertTrue(all(r['observation']['all_processes_closed'] for r in observations))
        with tempfile.TemporaryDirectory(prefix='n1-classic-primary-independent-') as temporary:
            root = Path(temporary)/'restored'
            restoration = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restoration['archive_members_verified'], 463)
            self.assertEqual(restoration['retained_regular_files'], 461)
            self.assertEqual(len(restoration['omitted_redundant_aliases']), 2)
            self.assertFalse(restoration['native_execution_attested'])
            original = root/'original-train'
            self.assertEqual(load(original/'controller-result.json')['execution'], 'completed')
            self.assertTrue(load(original/'worker/terminal.json')['operation_passed'])
            work = original/'worker/native-stock-cold7'
            case = work/'Classic-stock-cold7-N1'
            outcome = load(case/'index.json')
            self.assertEqual(outcome['validity'], 'valid')
            self.assertFalse(outcome['classification_assessed'])
            native = case/'runs/train/native'
            package = load(native/'train_stopped_state.json')
            summary = load(native/'train_stopped_summary.json')
            audit = audit_candidate_window_package(package, summary,
                external_resolver=filesystem_primary_resolver(native))
            self.assertEqual(audit['training_outcome'], 'invalid_observation')
            self.assertEqual(package['reason'], 'composite_train_assignment_missing;omission_group_closed')
            self.assertEqual(audit['logical_groups'], 18)
            self.assertEqual(audit['native_probes'], 108)
            self.assertEqual(audit['sampled_frames'], 388908)
            self.assertFalse(audit['certificate_consistent'])
            self.assertIsNone(audit['exact'])
            self.assertFalse(audit['live_authority_restored'])
            self.assertEqual([p['length'] for p in package['trained_inputs']], [54, 1, 1, 1])
            initial = load(work/'prepared/initial/Classic-stock-cold7-N1.json')
            physics = audit_final_stock(initial, package['neuron']['graph']['identity'])
            trace = native/'composite-measurements/group-000018/full-before.csv'
            with trace.open('ab') as stream:
                stream.write(b'corrupt,actual,primary\n')
            with self.assertRaises(EvidenceError):
                audit_candidate_window_package(package, summary,
                    external_resolver=filesystem_primary_resolver(native))
        self.assertEqual(before, {n: frozen_digest(source/n, 128*1024**2) for n in names})
        receipt = dict(restoration=restoration, package_audit=audit, physical_audit=physics,
            corrupt_extracted_primary_rejected=True, original_archive_changed=False,
            new_model_execution=False, scientific_verdict=None)
        with (Path(os.environ['TMPDIR'])/'n1-classic-primary-independent-restoration.json').open('x', encoding='utf-8') as stream:
            json.dump(receipt, stream, indent=2, allow_nan=False); stream.write('\n')
