"""Independent restoration of the two recorded stock N4 Train outcomes.

Archive integrity and replayed model DATA do not restore execution authority,
convergence, classification, or the unfinished Classic observation window.
"""
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


ARCHIVES = {
    'Classic': ('827fc90141885e32206574030219bcfeb84cee3e8b603ab58b060c4d33fef32f', 1519),
    'Branch': ('d8a1399de22e556ad22bed5d45a08efbdb1aa6890b9107b6d26812cd304e6964', 2628),
}
FILES = {'bundle.json', 'primary.tar.xz', 'collection-proof.json',
         'collection-controller.json', 'collection-closure.json', 'collection-terminal.json'}


class StockTrainCompactPrimaryTest(unittest.TestCase):
    def _verify(self, topology):
        fixture = os.environ.get('TIMELEARNER_STOCK_TRAIN_COMPACT_PRIMARY')
        require(fixture is not None, 'stock_train_compact_primary_required')
        source = Path(fixture).resolve(strict=True)/topology
        self.assertEqual({p.name for p in source.iterdir()}, FILES)
        before = {n: frozen_digest(source/n, 64*1024**2) for n in FILES}
        bundle = load(source/'bundle.json')
        archive_sha, members = ARCHIVES[topology]
        self.assertEqual(bundle['archive_sha256'], archive_sha)
        self.assertEqual(len(bundle['members']), members)
        self.assertTrue(load(source/'collection-terminal.json')['operation_passed'])
        collection = load(source/'collection-proof.json')
        for stage in ('before', 'after'):
            self.assertEqual(len(collection[stage]), 3)
            self.assertTrue(all(r['observation']['all_processes_closed'] for r in collection[stage]))
        with tempfile.TemporaryDirectory(prefix='stock-train-independent-') as temporary:
            restored_root = Path(temporary)/'restored'
            restored = restore_native_bundle(source/'bundle.json', restored_root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restored['archive_members_verified'], members)
            self.assertEqual(len(restored['omitted_redundant_aliases']), 2)
            self.assertEqual(restored['retained_regular_files'], members-2)
            self.assertFalse(restored['native_execution_attested'])
            original = restored_root/'stock-cold7-original'
            controller = load(original/'controller-result.json')
            operation = load(original/'worker/terminal.json')
            work = original/'worker/native-stock-cold7'
            run = work/(topology+'-stock-cold7-N1')
            outcome = load(run/'index.json')
            process = load(run/'runs/train/process/result.json')
            native = run/'runs/train/native'
            self.assertFalse(outcome['classification_assessed'])
            self.assertIsNone(outcome['scientific_verdict'])
            if topology == 'Classic':
                self.assertFalse(operation['operation_passed'])
                self.assertEqual(controller['execution'], 'process_error')
                self.assertEqual(process['execution'], 'timeout')
                self.assertEqual(outcome['execution'], 'timeout')
                self.assertEqual(outcome['validity'], 'unverified_execution')
                self.assertIsNone(outcome['package_audit'])
                self.assertIsNone(outcome['package_path'])
                self.assertFalse((native/'train_learned_state.json').exists())
                self.assertFalse((native/'train_stopped_state.json').exists())
                packets = {p.stem for p in native.glob('raw-trial-*.json')}
                traces = {p.stem for p in native.glob('raw-trial-*.csv')}
                self.assertEqual(len(packets), 702)
                self.assertEqual(len(traces), 703)
                self.assertLess(packets, traces)
                detail = dict(raw_packets=702, raw_traces=703,
                    orphan_trace_ids=sorted(traces-packets), final_observation_complete=False,
                    package_available=False, raw_trace_semantics_reaudited=False)
            else:
                self.assertTrue(operation['operation_passed'])
                self.assertEqual(controller['execution'], 'completed')
                self.assertEqual(process['execution'], 'completed')
                self.assertEqual(outcome['validity'], 'valid')
                package = load(native/'train_stopped_state.json')
                summary = load(native/'train_stopped_summary.json')
                audit = audit_candidate_window_package(package, summary=summary,
                    external_resolver=filesystem_primary_resolver(native))
                self.assertEqual(audit['training_outcome'], 'budget_exhausted')
                self.assertEqual(package['reason'], 'maximum_probes_exhausted')
                self.assertIsNone(audit['exact'])
                self.assertFalse(audit['certificate_consistent'])
                self.assertFalse(audit['live_authority_restored'])
                self.assertEqual(audit['logical_groups'], 132)
                self.assertEqual(audit['native_probes'], 792)
                self.assertEqual(audit['sampled_frames'], 2851992)
                initial = load(work/'prepared/initial/Branch-stock-cold7-N1.json')
                physics = audit_final_stock(initial, package['neuron']['graph']['identity'])
                trace = native/'composite-measurements/group-000001/full-after.csv'
                self.assertTrue(trace.is_file())
                with trace.open('ab') as stream:
                    stream.write(b'corrupted,NaN\n')
                with self.assertRaises(EvidenceError):
                    audit_candidate_window_package(package, summary=summary,
                        external_resolver=filesystem_primary_resolver(native))
                detail = dict(model_revision=audit['model_revision'], training_outcome=audit['training_outcome'],
                    reason=package['reason'], logical_groups=audit['logical_groups'],
                    native_probes=audit['native_probes'], sampled_frames=audit['sampled_frames'],
                    primary_bytes=audit['primary_bytes'], exact=None, certificate_consistent=False,
                    physical_audit=physics, corrupt_actual_primary_rejected=True)
            proof = dict(topology=topology, restoration=restored, recorded_outcome=outcome,
                original_controller_execution=controller['execution'], data_checks=detail,
                independent_restoration=True, original_execution_replaced=False,
                new_model_execution=False, scientific_verdict=None)
            receipt = Path(os.environ['TMPDIR'])/('stock-train-'+topology.lower()+'-independent-restoration.json')
            with receipt.open('x', encoding='utf-8') as stream:
                json.dump(proof, stream, indent=2, allow_nan=False)
                stream.write('\n')
        self.assertEqual(before, {n: frozen_digest(source/n, 64*1024**2) for n in FILES})

    def test_classic_archive_preserves_timeout_and_unfinished_observation_without_model(self):
        self._verify('Classic')

    def test_branch_archive_replays_all_groups_stopped_model_and_rejects_corrupt_primary(self):
        self._verify('Branch')
