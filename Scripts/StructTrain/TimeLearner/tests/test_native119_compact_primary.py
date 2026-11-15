"""Restore a complete native119 archive and replay its declared data checks.

Original execution claims remain recorded evidence. Restoration launches no
native model and cannot supply fresh execution authority for the other host.
"""
import os
from pathlib import Path
import tempfile
import unittest
import json

from ..candidate_window_package_evidence import audit_candidate_window_package
from ..collector_provenance import frozen_digest
from ..composite_primary import filesystem_primary_resolver
from ..native_evidence import load, require
from ..native_gate import audit_junit
from ..portable_primary import restore_native_bundle


ARCHIVES = {
    '0404e830a1a00c00f2397e9094c2953dcdef71ebffb603ef4ce500b8d9df7850': 'Elder',
    'f9196adc86ed760dcc0b1fe85c96500ac052f57f885a379f4fe797cee47d0902': 'M40',
}


class Native119CompactPrimaryTest(unittest.TestCase):
    def test_complete_restore_replays_all_junit_rules_and_original_model_states(self):
        value = os.environ.get('TIMELEARNER_NATIVE119_COMPACT_PRIMARY')
        require(value is not None, 'native119_compact_primary_required')
        source = Path(value).resolve(strict=True)
        names = {'bundle.json', 'primary.tar.xz', 'collection-proof.json',
            'collection-controller.json', 'collection-closure.json', 'collection-terminal.json'}
        self.assertEqual({p.name for p in source.iterdir() if p.is_file()}, names)
        before = {n: frozen_digest(source/n, 32*1024**2) for n in names}
        bundle = load(source/'bundle.json')
        self.assertIn(bundle['archive_sha256'], ARCHIVES)
        self.assertEqual(len(bundle['members']), 4868)
        self.assertTrue(load(source/'collection-terminal.json')['operation_passed'])
        collection = load(source/'collection-proof.json')
        for stage in ('before', 'after'):
            self.assertEqual(len(collection[stage]), 44)
            self.assertTrue(all(r['observation']['all_processes_closed'] for r in collection[stage]))
        with tempfile.TemporaryDirectory(prefix='native119-independent-restore-') as temporary:
            destination = Path(temporary)/'restored'
            # These aliases belong to raw C++ test logs, not the special legacy
            # pipeline alias namespace. Preserve all as regular archive bytes.
            restored = restore_native_bundle(source/'bundle.json', destination)
            self.assertEqual(restored['archive_members_verified'], 4868)
            self.assertEqual(restored['retained_regular_files'], 4868)
            self.assertFalse(restored['native_execution_attested'])
            aliases = 0
            for root in collection['manifest']['roots']:
                for name, link in root['links'].items():
                    path = Path(root['prefix'])/name
                    target = path.parent/link['link_text']
                    self.assertEqual(bundle['members'][path.as_posix()], bundle['members'][target.as_posix()])
                    aliases += 1
            self.assertEqual(aliases, 42)
            original = destination/'native119-original'
            terminal = load(original/'terminal.json')
            self.assertTrue(terminal['job_validation_passed'])
            self.assertTrue(terminal['cohort_assertions_passed'])
            self.assertEqual(terminal['audited_completed_cpp_cases'], 119)
            self.assertEqual(terminal['completed_leaf_gates'], 43)
            observed = []
            specs = sorted(original.glob('*/specification.json'))
            self.assertEqual(len(specs), 43)
            for path in specs:
                spec = load(path)
                inventory = audit_junit(path.parent/'native.xml', spec['expected_test_ids'])
                self.assertEqual(inventory['assertion_status'], 'passed')
                runtime = load(path.parent/'runtime.json')
                self.assertEqual(runtime['source_closure']['root']['head'],
                    '22e9714bbe66d29a661bb6829e1c992f24fc1362')
                observed.extend(spec['expected_test_ids'])
            self.assertEqual(len(observed), 119)
            self.assertEqual(len(set(observed)), 119)
            rules = load(original/'job.json')['artifacts']
            self.assertEqual(len(rules), 310)
            source_namespace = next(r for r in collection['manifest']['roots']
                if r['prefix'] == 'native119-original')
            for rule in rules:
                # Materialized log aliases were links in the original tree;
                # do not change an original regular-file count by restoration.
                count = len([p for p in original.glob(rule['glob'])
                    if p.relative_to(original).as_posix() in source_namespace['files']])
                self.assertGreaterEqual(count, rule['minimum'])
                if rule['maximum'] is not None:
                    self.assertLessEqual(count, rule['maximum'])
            corpus = original/'native-package6-29/native-composite'
            audits = {}
            cases = ['package6-classic/source-'+str(i) for i in range(7)] + [
                'package6-branch/source-'+str(i) for i in range(4)] + [
                'package6-classic/imported-warm', 'package6-branch/asymmetric-imported-warm']
            for case in cases:
                directory = corpus/case
                paths = [p for p in (directory/'train_learned_state.json', directory/'train_stopped_state.json') if p.is_file()]
                self.assertEqual(len(paths), 1)
                audits[case] = audit_candidate_window_package(load(paths[0]),
                    external_resolver=filesystem_primary_resolver(directory))
            for case in ('package6-classic/source-0', 'package6-branch/source-0'):
                self.assertTrue(audits[case]['exact'])
                self.assertTrue(audits[case]['certificate_consistent'])
            self.assertIsNone(audits['package6-classic/source-5']['exact'])
            self.assertFalse(audits['package6-classic/source-5']['mathematical_exact'])
            self.assertIsNone(audits['package6-classic/source-6']['exact'])
            self.assertTrue(audits['package6-classic/source-6']['mathematical_exact'])
            for topology in ('classic', 'branch'):
                self.assertFalse(audits['package6-'+topology+'/source-2']['certificate_consistent'])
            proof = dict(restoration=restored, source_worker=ARCHIVES[bundle['archive_sha256']],
                junit_cases=len(observed), leaf_gates=len(specs), artifact_rules=len(rules),
                preserved_log_aliases=aliases, actual_package_audits=audits,
                new_native_execution=False, scientific_verdict=None)
            with (Path(os.environ['TMPDIR'])/'native119-independent-restoration.json').open('x', encoding='utf-8') as stream:
                json.dump(proof, stream, indent=2, allow_nan=False);stream.write('\n')
        self.assertEqual(before, {n: frozen_digest(source/n, 32*1024**2) for n in names})
