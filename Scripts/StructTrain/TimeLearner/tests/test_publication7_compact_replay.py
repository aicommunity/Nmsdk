"""Independent replay of all original publication7 files and wrapper semantics.

The original C++ cases use explicit wrapper arguments, not a Console process.
This reader never creates a neuron, recompiles code or promotes that scope.
"""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..candidate_window_recovery_execution_evidence import audit_candidate_window_recovery_execution
from ..collector_provenance import frozen_digest
from ..composite_primary import filesystem_primary_resolver
from ..model_identity import canonical_model_sha256 as digest
from ..native_calibration_worker import _write
from ..native_evidence import EvidenceError, load
from ..native_gate import audit_junit
from ..portable_primary import ALIAS_ADAPTER, restore_native_bundle


def signed(value):
    value['sha256'] = digest({k: v for k, v in value.items() if k != 'sha256'})
    return value


class Publication7CompactReplayTest(unittest.TestCase):
    def test_original_seven_case_corpus_and_both_wire_bases_replay_independently(self):
        source = Path(os.environ['TIMELEARNER_PUBLICATION7_PRIMARY']).resolve(strict=True)
        before = {name: frozen_digest(source/name, 4*1024**2)
                  for name in ('bundle.json', 'primary.tar.xz')}
        bundle = load(source/'bundle.json')
        self.assertEqual(bundle['archive_bytes'], 1827912)
        self.assertEqual(bundle['archive_sha256'],
                         'b2cb195ba2df4fdb6f6e72194cf4bffbeeddcdc6d57c5fc3c2b889fc0a35a296')
        self.assertEqual(len(bundle['members']), 498)
        cases = ('ClassicStoppedPublicationAndExecution5', 'BranchStoppedPublicationAndExecution5',
                 'ClassicCompletedPublicationAndExecution5', 'BranchCompletedPublicationAndExecution5')
        before_source = ('Preflight5KeepsNullLedgerAndKnownZeroCounters',
                         'BeforeSourceFailure5DoesNotInventLedger')
        foreign_case = 'RehashedForeignLedgerRejectedBeforeAnyPublication'
        expected = ['NativeRecoveryConsoleArtifact/'+name for name in (*cases, *before_source, foreign_case)]
        with tempfile.TemporaryDirectory(prefix='publication7-replay-', dir=os.environ['TMPDIR']) as temporary:
            root = Path(temporary)/'restored'
            restoration = restore_native_bundle(source/'bundle.json', root, compatibility=ALIAS_ADAPTER)
            self.assertEqual(restoration['archive_members_verified'], 498)
            self.assertEqual(restoration['retained_regular_files'], 497)
            self.assertEqual(len(restoration['omitted_redundant_aliases']), 1)
            self.assertFalse(restoration['native_execution_attested'])
            old_output = Path(load(root/'native/job.json')['paths']['output'])
            self.assertTrue(old_output.is_absolute())
            self.assertFalse(old_output.exists(), 'independent replay must not see the original Elder output')
            junit = audit_junit(root/'native/publication-receipt-seven/native.xml', expected)
            self.assertEqual(junit['assertion_status'], 'passed')
            corpus = root/'native/publication-receipt-seven/native-composite/package7/NativeRecoveryConsoleArtifact'
            self.assertEqual({p.name for p in corpus.iterdir() if p.is_dir()},
                             set((*cases, *before_source, foreign_case)))
            rows = []
            for name in cases:
                directory = corpus/name/'console-artifacts'
                completed = 'Completed' in name
                stem = 'learned' if completed else 'stopped'
                package = load(directory/f'train_{stem}_state.json')
                summary = load(directory/f'train_{stem}_summary.json')
                self.assertEqual(package, load(corpus/name/'source-package.json'))
                self.assertEqual(summary, load(corpus/name/'source-summary.json'))
                audit_candidate_window_recovery_package(package, summary,
                    external_resolver=filesystem_primary_resolver(directory))
                names = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
                scope = load(directory/'wrapper-scope.json')
                self.assertFalse(scope['actual_console_process_executed'])
                self.assertTrue(scope['execution_counters_are_test_arguments'])
                for base in (1, 2):
                    wire = load(directory/f'wrapper-base{base}.json')
                    audited = audit_candidate_window_recovery_execution(wire, directory, names,
                        mode='train', base_version=base, package=package)
                    self.assertTrue(audited['owned_archive_present'])
                    self.assertTrue(audited['recovery_ledger_present'])
                    self.assertFalse(audited['native_execution_verified'])
                rows.append(dict(case=name, package_sha256=package['sha256'],
                    groups=len(package['measurement_archive']['records']),
                    deliveries=len(package['recovery_ledger']['deliveries']), checked_bases=[1, 2]))
            for name in before_source:
                preflight = name.startswith('Preflight')
                for base in (1, 2):
                    wire = load(corpus/name/f'{"preflight" if preflight else "start-failure"}-base{base}.json')
                    audited = audit_candidate_window_recovery_execution(wire, corpus/name, set(),
                        mode='preflight' if preflight else 'train', base_version=base)
                    self.assertFalse(audited['owned_archive_present'])
                    self.assertFalse(audited['recovery_ledger_present'])
                    counters = wire['composite_counters']
                    if preflight:
                        self.assertEqual(counters['attempt'], dict(logical_groups=0, native_probes=0, sampled_frames=0))
                    else:
                        self.assertIsNone(counters['attempt'])
                        self.assertIsNone(counters['archive'])
            foreign_root = corpus/foreign_case
            foreign = load(foreign_root/'source-package.json')
            foreign_summary = load(foreign_root/'source-summary.json')
            audit_candidate_window_recovery_package(foreign, foreign_summary,
                external_resolver=filesystem_primary_resolver(foreign_root))
            changed = deepcopy(foreign)
            changed['recovery_ledger']['source_origin'] = '0'*64
            signed(changed['recovery_ledger'])
            changed['neuron']['metadata']['recovery_ledger_sha256'] = changed['recovery_ledger']['sha256']
            signed(changed['neuron']);signed(changed)
            # Do not let an unchanged summary digest mask the foreign-ledger
            # check: the package itself must fail without a supplied summary.
            with self.assertRaisesRegex(EvidenceError, 'domain_recomputed'):
                audit_candidate_window_recovery_package(changed,
                    external_resolver=filesystem_primary_resolver(foreign_root))
            case = corpus/cases[0]/'console-artifacts'
            package = load(case/'train_stopped_state.json')
            summary = load(case/'train_stopped_summary.json')
            reference = package['measurement_archive']['records'][0]['raw_trials'][0]['primary_ref']['relative_path']
            csv = case/reference
            original = csv.read_bytes();csv.write_bytes(original+b'corrupt,restored,primary\n')
            with self.assertRaises(EvidenceError):
                audit_candidate_window_recovery_package(package, summary,
                    external_resolver=filesystem_primary_resolver(case))
            csv.write_bytes(original)
        self.assertEqual(before, {name: frozen_digest(source/name, 4*1024**2)
                                 for name in ('bundle.json', 'primary.tar.xz')})
        _write(Path(os.environ['TMPDIR'])/'publication7-replay.json', dict(
            restoration=restoration, original_junit=junit, positive_cases=rows,
            before_source_bases_checked=4, foreign_ledger_rejected=True,
            corrupted_external_primary_rejected=True, original_archive_changed=False,
            original_elder_output_available=False, new_model_execution=False,
            actual_console_process_executed=False, scientific_verdict=None))
