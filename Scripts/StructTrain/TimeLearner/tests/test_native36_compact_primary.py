"""Full SDK36 corpus DATA replay; no fresh native/scientific authority.

Reuse the ten-conversion/twenty-trial and Console8 production-reader checks.
Legacy native32 classes keep their original 'case' archive layout and scope.
"""
import hashlib
import json
import math

from ..candidate_window_package_evidence import audit_candidate_window_recovery_package
from ..composite_primary import filesystem_primary_resolver
from ..native_evidence import EvidenceError, load, require
from ..native_gate import audit_junit
from . import test_recovery_recognition7_native as shared
from . import test_native32_compact_primary as native32


ROOT_COMMIT = '448b153f2fea3486ff40f3a626b8f1110b9e3ee2'
PULSE_COMMIT = '7b524b8d6c760c5ecfeea432b14b5f9d5045987d'
ARCHIVE_SHA = '605799a29ce070450904d3dbb1712f435cc6735c8211d940c21255912e860f83'
# Exact selected IDs from the independently committed SDK36 cohort declaration.
EXPECTED_IDS_SHA = 'baf50113bcc9a5632b877995a53c191eeecb05bf53bdcc7ae8eaa9972750a6c1'
EXPORT_CASES = ('ClassicStoppedSameBytesAndIndependentReplay', 'BranchStoppedSameBytesAndIndependentReplay',
                'ClassicCompletedSameBytesAndIndependentReplay', 'BranchCompletedSameBytesAndIndependentReplay')


class Native36CompactPrimaryTest(shared.RecoveryRecognition7NativeTest):
    fixture_environment = 'TIMELEARNER_NATIVE36_BUNDLE'
    archive_prefix = 'native'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bundle = load(cls.bundle_root/'bundle.json');origin = load(cls.bundle_root/'ORIGIN.json')
        require(bundle['archive_sha256'] == ARCHIVE_SHA and len(bundle['members']) == 3063 and
            bundle['expanded_bytes'] == 885620703, 'native36_exact_primary_scope')
        require(origin['native_root'] == ROOT_COMMIT and origin['native_pulselib'] == PULSE_COMMIT and
            origin['scientific_verdict'] is None and origin['independent_semantic_replay_accepted'] is False,
            'native36_original_source_and_producer_scope')

    test_actual_console_publications_bind_source7_and_execution5 = (
        native32.Native32BundleChecks.test_actual_console_publications_bind_source7_and_execution5)

    def test_exact_original_36_ids_and_all_artifact_rules(self):
        original = self.restored/'native';terminal = load(original/'terminal.json')
        self.assertTrue(terminal['job_validation_passed']);self.assertTrue(terminal['cohort_assertions_passed'])
        self.assertEqual(terminal['actual_audited_assertion_passed_cpp_cases'], 36)
        self.assertEqual(terminal['completed_leaf_gates'], 36)
        self.assertEqual(terminal['heartbeat_errors'], []);self.assertEqual(terminal['final_capture_errors'], [])
        observed = []
        specifications = sorted(original.glob('*/specification.json'));self.assertEqual(len(specifications), 36)
        for path in specifications:
            spec = load(path);inventory = audit_junit(path.parent/'native.xml', spec['expected_test_ids'])
            self.assertEqual(inventory['assertion_status'], 'passed')
            runtime = load(path.parent/'runtime.json');closure = runtime['source_closure']
            self.assertEqual(closure['root']['head'], ROOT_COMMIT)
            self.assertEqual(closure['Libraries/Nmsdk-PulseLib']['head'], PULSE_COMMIT)
            observed.extend(spec['expected_test_ids'])
        self.assertEqual(len(observed), len(set(observed)));self.assertEqual(len(observed), 36)
        digest = hashlib.sha256(json.dumps(sorted(observed), separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(digest, EXPECTED_IDS_SHA)
        members = load(self.bundle_root/'bundle.json')['members']
        aliases = {'NeuroModeler.'+s for s in ('INFO', 'WARNING', 'ERROR', 'FATAL')}
        self.assertEqual(sum(n.rsplit('/', 1)[-1] in aliases for n in members), 36)
        for rule in load(original/'job.json')['artifacts']:
            paths = [p for p in original.glob(rule['glob']) if p.is_file() and p.name not in aliases]
            self.assertTrue(all(p.relative_to(self.restored).as_posix() in members for p in paths))
            self.assertGreaterEqual(len(paths), rule['minimum'])
            if rule['maximum'] is not None:self.assertLessEqual(len(paths), rule['maximum'])

    def test_original_37_closures_and_immutable_sources_remain_data_only(self):
        original, controller = self.restored/'native', self.restored/'controller'
        result = load(controller/'supervisor-result.json')
        self.assertTrue(result['outer_closed']);self.assertEqual(result['record_errors'], []);self.assertIsNone(result['reason'])
        self.assertEqual(len(result['children_closed']), 36);self.assertIsNone(result['scientific_verdict'])
        self.assertTrue(all(r['closure']['all_processes_closed'] for r in result['children_closed']))
        outer = load(controller/'outer-closure.json');self.assertTrue(outer['all_processes_closed'])
        bound = list(self.restored.rglob('owned-unit.json'));self.assertEqual(len(bound), 37)
        leases = load(controller/'reservation-final.json')
        self.assertEqual(len(leases), 1);self.assertEqual(leases[0]['state'], 'released')
        outcome = load(controller/'original-outcome.json')
        self.assertEqual(outcome['kernel_before_stop']['state']['ExecMainStatus'], '0')
        self.assertEqual(outcome['kernel_before_stop']['state']['Result'], 'success')
        for before, after in [('source-closure.json', 'source-closure-after.json'),
            ('source-hashes-before-build.json', 'source-hashes-after.json'),
            ('current-runtime-before.json', 'current-runtime-after.json'),
            ('protected-files-before.json', 'protected-files-after.json')]:
            self.assertEqual((original/before).read_bytes(), (original/after).read_bytes())
        self.assertFalse(self.restoration['native_execution_attested'])

    def export_directory(self, ordinal):
        return self.restored/f'native/validated-{ordinal:03d}/native-composite/package7/NativeValidatedArchiveExport/{EXPORT_CASES[ordinal-1]}'

    def test_four_real_validated_exports_and_boundary_responses(self):
        for ordinal, name in enumerate(EXPORT_CASES, 1):
            with self.subTest(case=name):
                directory = self.export_directory(ordinal)
                package, summary = load(directory/'source-package.json'), load(directory/'source-summary.json')
                audit_candidate_window_recovery_package(package, summary,
                    external_resolver=filesystem_primary_resolver(directory))
                self.assertEqual(package['schema_version'], 7);self.assertEqual(summary['schema_version'], 8)
                self.assertEqual(summary['recovery_ledger'], package['recovery_ledger'])
                self.assertEqual(package['kind'], 'timelearner_stopped_state' if ordinal <= 2 else 'timelearner_completed_state')
                response = load(directory/'source-response.json')
                self.assertEqual(response['kind'], 'native_boundary_response_fixture')
                self.assertEqual(response['routing'], 'native_burst_active_input0')
                self.assertIsNone(response['scientific_verdict'])
                rows = response['relative_time_stimulus_potentials'];self.assertTrue(rows)
                self.assertGreaterEqual(len(rows[0]), 3)
                self.assertTrue(all(len(r) == len(rows[0]) and all(math.isfinite(v) for v in r) for r in rows))
                self.assertEqual(rows[0][0], 0.)
                self.assertTrue(all(a[0] < b[0] for a, b in zip(rows, rows[1:])))
                self.assertTrue(any(r[1] > 0 for r in rows))

    def test_corrupted_retained_export_primary_is_not_hidden_by_embedded_data(self):
        directory = self.export_directory(1)
        package, summary = load(directory/'source-package.json'), load(directory/'source-summary.json')
        path = next(iter(sorted((directory/'composite-measurements').glob('group-*/*.csv'))))
        original = path.read_bytes()
        try:
            path.write_bytes(original+b'corrupted\n')
            with self.assertRaises((EvidenceError, ValueError)):
                audit_candidate_window_recovery_package(package, summary,
                    external_resolver=filesystem_primary_resolver(directory))
        finally:
            path.write_bytes(original)
