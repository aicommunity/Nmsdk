"""Recover the complete closed Elder count campaign on another host.

This acceptance consumes the immutable published primary, not the original
worker directories. It proves full byte recovery and readable observations;
the earlier runtime/training/recognition audits keep their original scope.
"""
import collections
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest

from ..external_archive import locate, resolve
from ..native_evidence import load
from ..portable_primary import RETAIN_ALIASES, restore_native_bundle
from ..recognition_metrics import load_diagnostic_evaluation
from ..runtime import file_record


class ClassicCountPrimaryRestorationTest(unittest.TestCase):
    def test_complete_Elder_primary_and_all_recorded_recognition_trials_restore(self):
        package = Path(os.environ['TIMELEARNER_CLASSIC_COUNT_FULL_PRIMARY'])
        publication = load(package/'publication.json')
        self.assertEqual(publication['kind'], 'timelearner_stopped_classic_full_primary_archive')
        self.assertEqual(publication['original_training_job'], 'classic-measured-count-m4-elder-k1')
        self.assertEqual(publication['source_Train_outcome'], 'budget_exhausted')
        self.assertFalse(publication['training_completed'])
        bundle_path = locate(package/'bundle.json')
        bundle = load(bundle_path)
        reference = load(package/'primary.tar.xz.archive.json')
        self.assertEqual(reference, publication['archive'])
        self.assertEqual(bundle['archive_sha256'], reference['sha256'])
        self.assertEqual(reference['sha256'],
                         '615cf8153358500a0646bc8ddbecbd91097ed32d7a76e478167a5a0298194ad0')
        self.assertEqual(len(bundle['members']), 5129)
        self.assertEqual(bundle['expanded_bytes'], 12970896542)
        self.assertEqual(bundle['archive_bytes'], 125624684)
        archive = resolve(reference)
        before = file_record(archive)
        expected_prefixes = {
            'original-Train': 1666, 'original-Train-controls': 8,
            'full-Train-audit': 42, 'full-Train-audit-controls': 12,
            'recognition-study': 137, 'recognition-controls': 17,
            'baseline-run': 40, 'threshold-run': 40,
            'baseline-inputs': 1578, 'threshold-inputs': 1578,
            'native-runtime': 11,
        }
        self.assertEqual(dict(collections.Counter(n.split('/')[0] for n in bundle['members'])),
                         expected_prefixes)
        trials = []
        with tempfile.TemporaryDirectory(prefix='classic-full-primary-',
                                         dir=os.environ['TMPDIR']) as temporary:
            restored = Path(temporary)/'restored'
            receipt = restore_native_bundle(bundle_path, restored, compatibility=RETAIN_ALIASES)
            self.assertEqual(receipt['archive_members_verified'], 5129)
            self.assertEqual(receipt['retained_regular_files'], 5129)
            self.assertFalse(receipt['source_archive_modified'])
            self.assertFalse(receipt['native_execution_attested'])
            self.assertEqual(receipt['omitted_redundant_aliases'], [])
            actual = {p.relative_to(restored).as_posix(): p
                      for p in restored.rglob('*') if p.is_file()}
            self.assertEqual(set(actual), set(bundle['members']))
            self.assertTrue(all(not p.is_symlink() for p in actual.values()))
            self.assertTrue(all(actual[n].stat().st_size == r['bytes']
                                for n, r in bundle['members'].items()))
            execution = load(restored/'original-Train/train/native/execution.json')
            self.assertEqual(execution['training_outcome'], 'budget_exhausted')
            self.assertFalse(execution['completed_boundary'])
            native = restored/'original-Train/train/native'
            # EvidenceWriter finalizes a closed stopped Train by renaming the
            # live raw-trial files. Checking the transient name would reject a
            # completely recovered original archive after all bytes matched.
            expected_trials = {'train_stopped_trial_'+str(i)+suffix
                               for i in range(1, 497) for suffix in ('.json', '.csv')}
            self.assertEqual({p.name for p in native.glob('train_stopped_trial_*')},
                             expected_trials)
            self.assertEqual(list(native.glob('raw-trial-*')), [])
            for role in ('baseline-run', 'threshold-run'):
                spec, observations = load_diagnostic_evaluation(restored/role/'native/evaluation.json')
                self.assertEqual(len(spec['trials']), 8)
                self.assertEqual(len(observations), 8)
                self.assertEqual(len({row['trial_id'] for row in spec['trials']}), 8)
                self.assertTrue(all(o['valid'] and o['complete'] and not o['censored']
                                    for o in observations))
                self.assertTrue(all(len(o['samples']) == 4001 for o in observations))
                trials.append(dict(role=role, trials=8, samples_per_trial=4001,
                                   model_revision=spec['model_revision'],
                                   complete_observations_read_from_restored_tree=True))
            self.assertEqual(load(restored/'recognition-study/terminal.json')['actual_threshold_counts'],
                             publication['actual_threshold_counts'])
        self.assertEqual(file_record(archive), before)
        proof = dict(kind='timelearner_complete_Elder_count_primary_recovery', schema_version=1,
            recovery_host=socket.gethostname(), original_host='Elder',
            archive_reference=reference, source_archive=before, restoration=receipt,
            expanded_bytes=bundle['expanded_bytes'], recovered_prefixes=expected_prefixes,
            recognition_observations=trials, every_original_member_verified=True,
            independently_recovered_from_external_archive=True,
            disposable_expanded_cache_removed=True,
            original_Train_outcome='budget_exhausted', original_outcome_unchanged=True,
            new_full_training_or_recognition_audit_performed=False,
            new_native_execution=False, scientific_verdict=None)
        output = Path(os.environ['TMPDIR'])/'classic-full-primary-recovery-proof.json'
        self.assertFalse(output.exists())
        output.write_text(json.dumps(proof, indent=2, allow_nan=False)+'\n', encoding='utf-8')
