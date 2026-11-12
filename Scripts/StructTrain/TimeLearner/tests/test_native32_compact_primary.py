"""Full native32 Git archives: original IDs, publication DATA and frozen trials.

These are reader checks, not fresh native execution or scientific admission.
The six recognition checks are inherited without copying their algorithms.
"""
from ..candidate_window_recovery_execution_evidence import audit_candidate_window_recovery_execution
from ..native_evidence import load, require
from ..native_gate import audit_junit
from . import test_recovery_recognition7_native as shared


class Native32BundleChecks:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bundle = load(cls.bundle_root/'bundle.json')
        origin = load(cls.bundle_root/'ORIGIN.json')
        require(bundle['archive_sha256'] == cls.archive_sha256 and len(bundle['members']) == 2735,
                'native32_original_archive_scope')
        require(origin['native_cases_passed'] == 32 and origin[cls.origin_trial_count_field] == 20 and
                origin['native_source_commit'] == '8362d58f4d6576a0c8b0cc7633270976dff1df7b' and
                origin['pulse_commit'] == '1110808f4ad1f67538dadc6fe1d3f097e00c0630' and
                origin['scientific_verdict'] is None, 'native32_original_source_scope')

    def test_original_32_junit_ids_and_every_artifact_rule(self):
        original = self.restored/'case'
        terminal = load(original/'terminal.json')
        self.assertTrue(terminal['job_validation_passed'])
        self.assertTrue(terminal['cohort_assertions_passed'])
        self.assertEqual(terminal['audited_completed_cpp_cases'], 32)
        self.assertEqual(terminal['completed_leaf_gates'], 32)
        observed = []
        specifications = sorted(original.glob('*/specification.json'))
        self.assertEqual(len(specifications), 32)
        for path in specifications:
            spec = load(path)
            inventory = audit_junit(path.parent/'native.xml', spec['expected_test_ids'])
            self.assertEqual(inventory['assertion_status'], 'passed')
            runtime = load(path.parent/'runtime.json')
            self.assertEqual(runtime['source_closure']['root']['head'],
                '8362d58f4d6576a0c8b0cc7633270976dff1df7b')
            observed.extend(spec['expected_test_ids'])
        self.assertEqual(len(observed), 32)
        self.assertEqual(len(set(observed)), 32)
        self.assertEqual(sum(x.startswith('NativeCompositeBuildBoundary/') for x in observed), 4)
        self.assertEqual(sum(x.startswith('NativeRecoveryConsoleArtifact/') for x in observed), 7)
        self.assertEqual(sum(x.startswith('NativeCandidateWindowConsoleArtifact/') for x in observed), 11)
        self.assertEqual(sum(x.startswith('NativeRecoveryRecognition7/') for x in observed), 10)
        members = load(self.bundle_root/'bundle.json')['members']
        aliases = {'NeuroModeler.'+s for s in ('INFO', 'WARNING', 'ERROR', 'FATAL')}
        materialized_aliases = [n for n in members if n.rsplit('/', 1)[-1] in aliases]
        self.assertEqual(len(materialized_aliases), 32)
        for name in materialized_aliases:
            parent, alias = name.rsplit('/', 1)
            severity = alias.rsplit('.', 1)[-1]
            targets = [n for n in members if n.rsplit('/', 1)[0] == parent and
                       '.log.'+severity+'.' in n.rsplit('/', 1)[-1] and members[n] == members[name]]
            self.assertTrue(targets, name)
        for rule in load(original/'job.json')['artifacts']:
            # Original log links were materialized as regular bytes. They do
            # not increase the regular-file count of the original rule.
            paths = [p for p in original.glob(rule['glob']) if p.is_file() and
                     p.name not in aliases]
            self.assertTrue(all(p.relative_to(self.restored).as_posix() in members for p in paths))
            self.assertGreaterEqual(len(paths), rule['minimum'])
            if rule['maximum'] is not None:
                self.assertLessEqual(len(paths), rule['maximum'])

    def test_actual_console_publications_bind_source7_and_execution5(self):
        checked = 0
        for ordinal in range(1, 5):
            paths = list((self.restored/'case'/f'console-{ordinal:03d}').glob(
                'native-composite/package7/*/*/source-package.json'))
            self.assertEqual(len(paths), 1)
            directory = paths[0].parent
            package = load(paths[0])
            # Same production reader used by inherited recognition checks.
            from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
            from ..composite_primary import filesystem_primary_resolver
            audit_candidate_window_recovery_package(package, load(directory/'source-summary.json'),
                external_resolver=filesystem_primary_resolver(directory))
            exported = directory/'console-artifacts'
            names = {p.relative_to(exported).as_posix() for p in exported.rglob('*') if p.is_file()}
            for base in (1, 2):
                execution = load(exported/f'wrapper-base{base}.json')
                result = audit_candidate_window_recovery_execution(execution, exported, names,
                    mode='train', base_version=base, package=package)
                self.assertTrue(result['recovery_ledger_present'])
                self.assertFalse(result['native_execution_verified'])
                self.assertIsNone(result['evaluation_verdict'])
                checked += 1
        self.assertEqual(checked, 8)


class ElderNative32Test(Native32BundleChecks, shared.RecoveryRecognition7NativeTest):
    fixture_environment = 'TIMELEARNER_NATIVE32_ELDER_BUNDLE'
    origin_trial_count_field = 'full_pattern_trials'
    archive_sha256 = 'ecd6a2570e4cdbac1aaac6c1f0d6e604cfc13f38032188732434fbbe46b8e42a'


class M40Native32Test(Native32BundleChecks, shared.RecoveryRecognition7NativeTest):
    fixture_environment = 'TIMELEARNER_NATIVE32_M40_BUNDLE'
    origin_trial_count_field = 'recognition_full_pattern_trials'
    archive_sha256 = '3e17d8a92a7ede6e0d23be7b21a82749ffc5564d7756c08e957641db6b857d36'
