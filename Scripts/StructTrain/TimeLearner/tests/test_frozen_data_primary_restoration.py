"""Restore and reanalyze the closed DATA replay, order and unseen-foil corpus.

The archive is resolved through the external store. All native artifacts are
read from the disposable restored tree, not from the original run directories.
Byte recovery and portable evidence do not attest a new execution or learning.
"""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..external_archive import locate, resolve
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest, validate_job
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle
from ..recognition_metrics import load_physical_model_data_evaluation
from ..runtime import file_record


class FrozenDataPrimaryRestorationTest(unittest.TestCase):
    def test_complete_bytes_and_all_three_production_evaluations_restore(self):
        package = Path(os.environ['TIMELEARNER_FROZEN_DATA_PRIMARY_PUBLICATION'])
        metadata = locate(package/'bundle.json')
        bundle = load(metadata)
        reference = load(package/'primary.tar.xz.archive.json')
        archive = resolve(reference)
        before = file_record(archive)
        self.assertEqual(bundle['archive_sha256'],
            'be73dea9fd14ddc88caa2514f632e4c4f8d8d5c6149aec6254738e20aabb7838')
        self.assertEqual(bundle['archive_sha256'], reference['sha256'])
        self.assertEqual(bundle['expanded_bytes'], 317451632)
        self.assertEqual(bundle['archive_bytes'], 2383552)
        self.assertEqual(len(bundle['members']), 199)
        expected = (
            ('s11-branch-recognition-data-replay-m40-a1', 8, (1, 1, 0, 6)),
            ('s11-branch-DATA-frozen-order-m40-a1/run', 56, (7, 7, 0, 42)),
            ('s11-branch-frozen-new-foils-m40-a1/run', 27, (1, 1, 0, 25)),
        )
        rows = []
        with tempfile.TemporaryDirectory(prefix='frozen-data-primary-restore-',
                                         dir=os.environ['TMPDIR']) as temporary:
            root = Path(temporary); local = root/'package'; local.mkdir()
            (local/'bundle.json').write_bytes(metadata.read_bytes())
            (local/'primary.tar.xz.archive.json').write_text(json.dumps(reference), encoding='utf-8')
            restored = root/'restored'
            # Collection retains glog aliases as regular identical members.
            # The explicit native analysis adapter verifies every member first,
            # then omits only redundant aliases from this disposable view.
            # Original archives and recorded process identities stay unchanged.
            receipt = restore_native_bundle(local/'bundle.json', restored, compatibility=ALIAS_ADAPTER)
            self.assertEqual(receipt['archive_members_verified'], 199)
            self.assertEqual(receipt['retained_regular_files'], 196)
            self.assertEqual(len(receipt['omitted_redundant_aliases']), 3)
            self.assertFalse(receipt['source_archive_modified'])
            self.assertFalse(receipt['native_execution_attested'])
            for relative, count, counts in expected:
                run = restored/relative
                audit = audit_run_manifest(run/'run-manifest.json')
                self.assertTrue(audit['run_evidence_consistent'])
                metrics = load(run/'run-manifest.json')['analysis']['metrics']
                self.assertEqual(metrics['validity'], 'valid')
                self.assertTrue(metrics['data_only'])
                self.assertEqual(metrics['model_revision'],
                    '0fe43bddd70414e903ec41e68eb3433d9b85feaa5799448e2af7793ed8c5ff9f')
                self.assertEqual(tuple(metrics['pooled_counts'][key] for key in ('TP','FP','FN','TN')), counts)
                spec, observations = load_physical_model_data_evaluation(run/'native/evaluation.json')
                self.assertEqual(len(spec['trials']), count)
                self.assertEqual(len(observations), count)
                self.assertTrue(all(o['valid'] and o['complete'] and not o['censored'] for o in observations))
                self.assertTrue(all(len(o['samples']) == 4001 for o in observations))
                job = load(run/'input/job.json')
                source_case = (job['source_model_data'],)
                validate_job('physical-model-evaluate', job, source_case)
                for index in (0, len(job['trials'])-1):
                    for policy in ('preserve_neuron_dynamics', 'unknown_reset_policy'):
                        with self.subTest(run=relative,index=index,policy=policy):
                            changed = copy.deepcopy(job)
                            changed['trials'][index]['reset_policy'] = policy
                            changed.pop('sha256')
                            changed['sha256'] = canonical_model_sha256(changed)
                            with self.assertRaisesRegex(EvidenceError, 'pipeline_reset_policy_not_yet_verified'):
                                validate_job('physical-model-evaluate', changed, source_case)
                rows.append(dict(relative=relative, trials=count, counts=metrics['pooled_counts'],
                                 production_manifest_audited=True, complete_observations_checked=True,
                                 unsupported_reset_preflight_rejected=True))
        self.assertEqual(file_record(archive), before)
        proof = dict(kind='timelearner_frozen_data_primary_restoration_proof',schema_version=1,
            archive_reference=reference,source_archive=before,restoration=receipt,
            evaluations=rows,all_original_member_bytes_verified=True,
            disposable_recovery_cache_removed=True,new_native_execution=False,scientific_verdict=None)
        (Path(os.environ['TMPDIR'])/'frozen-data-primary-restoration-proof.json').write_text(
            json.dumps(proof,indent=2,allow_nan=False)+'\n',encoding='utf-8')
