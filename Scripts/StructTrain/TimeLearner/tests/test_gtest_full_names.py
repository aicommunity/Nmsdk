"""Server checks against the saved compiled SDK listing and real native JUnit.

Mutated XML tests reader identity only; it is never native execution evidence.
"""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

from .. import gtest_full_names as subject
from ..native_evidence import EvidenceError
from ..native_gate import audit_junit, supported_specification, artifact_directories_valid


class ActualCompiledGTestNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = os.environ.get('TIMELEARNER_FULL_GTEST_FIXTURE')
        if not fixture:
            raise unittest.SkipTest('requires saved actual SDK listing and completed native gate')
        cls.fixture = Path(fixture)
        cls.listing = (cls.fixture/'compiled-test-inventory.log').read_text()
        cls.crosscheck = json.loads((cls.fixture/'compiled-inventory-crosscheck.json').read_text())
        cls.names = subject.parse_listing(cls.listing)
        cls.original_xml = (cls.fixture/'native.xml').read_bytes()
        cls.legacy = json.loads((cls.fixture/'specification.json').read_text())

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='gtest-names-')
        self.addCleanup(directory.cleanup)
        self.xml = Path(directory.name)/'native.xml'
        self.xml.write_bytes(self.original_xml)

    def test_saved_listing_exactly_matches_all_compiled_ids(self):
        self.assertTrue(self.crosscheck['accepted'])
        old = [n.replace('.', '/', 1) for n in self.names]
        # Explicit adapter: the historical worker retained one space before
        # GetParam comments. Current selectors still reject all whitespace.
        historical = self.crosscheck['compiled']
        self.assertTrue(all(n == n.rstrip() or (n.endswith(' ') and not n.endswith('  '))
                            for n in historical))
        self.assertEqual(set(old), {n.rstrip() for n in historical})
        self.assertEqual(len(old), len(historical))
        self.assertGreater(len(old), len(self.crosscheck['expected']))

    def test_parameterized_suite_and_case_slashes_survive_filter(self):
        names = [n for n in self.names if '/' in n.split('.')[0] and '/' in n.split('.')[1]]
        self.assertTrue(names)
        self.assertEqual(subject.filter_argument(names), '--gtest_filter='+':'.join(names))
        self.assertIn('TopologiesAndRates/NativeTimingProperties.'
                      'RejectNonfiniteWithoutChangingPreviousValue/0', names)

    def test_partition_covers_every_actual_case_once_in_original_order(self):
        for maximum in (1, 7, 32, 256):
            leaves = subject.partition(self.names, maximum)
            self.assertEqual([n for leaf in leaves for n in leaf], self.names)
            self.assertTrue(all(1 <= len(leaf) <= maximum for leaf in leaves))
            for leaf in leaves:
                self.assertLessEqual(len(subject.filter_argument(leaf).encode()), subject.MAXIMUM_FILTER_BYTES)

    def test_argument_bytes_are_bounded_independently_of_case_count(self):
        names = ['Suite.'+'Case'+'x'*1000+str(i) for i in range(200)]
        with self.assertRaisesRegex(EvidenceError, 'filter_argument_budget'):
            subject.filter_argument(names)
        leaves = subject.partition(names, 256)
        self.assertGreater(len(leaves), 1)
        self.assertEqual([n for leaf in leaves for n in leaf], names)

    def test_filter_operators_and_ambiguous_separators_are_rejected(self):
        for name in ('Suite.Case*', 'Suite.Case:Other.Case', 'Suite.-Case',
                     'Suite.Case?', 'Suite.Case.Other', 'Suite/Case', 'Suite..Case',
                     'Suite.Case\0', 'Suite.Case\n', '.Case', 'Suite.'):
            with self.subTest(name=name), self.assertRaises(EvidenceError):
                subject.filter_argument([name])
        with self.assertRaisesRegex(EvidenceError, 'duplicate'):
            subject.filter_argument([self.names[0], self.names[0]])

    def test_unknown_or_incomplete_listing_cannot_silently_drop_lines(self):
        for text in ('Suite.\n', 'Suite.\nOther.\n  Case\n', '  Case\n',
                     'Suite.\n  Case\nSuite.\n  Other\n',
                     self.listing+'unexpected console message\n',
                     self.listing+'  Case*\n'):
            with self.subTest(text=text[-100:]), self.assertRaises(EvidenceError):
                subject.parse_listing(text)

    def test_listing_comments_are_metadata_instead_of_filter_syntax(self):
        self.assertEqual(subject.parse_listing('Types/Suite/0.  # TypeParam = int\n'
            '  Case/0  # GetParam() = (false, 2000)\n'), ['Types/Suite/0.Case/0'])

    def test_partition_rejects_invalid_or_boolean_limits(self):
        for count in (True, 0, -1, 257, 3.0):
            with self.assertRaises(EvidenceError):
                subject.partition(self.names, count)

    def test_real_unparameterized_junit_has_identical_legacy_and_full_name_outcome(self):
        expected = [c.get('classname')+'.'+c.get('name') for c in ET.fromstring(self.original_xml).iter('testcase')]
        before = audit_junit(self.xml, self.legacy['expected_test_ids'])
        after = audit_junit(self.xml, expected, full_names=True)
        self.assertEqual(before, after)
        self.assertEqual(after, audit_junit(self.xml, list(reversed(expected)), full_names=True))

    def parameterized_reader_control(self):
        # Names are intentionally mutated reader controls, not measured cases.
        tree = ET.fromstring(self.original_xml)
        names = []
        for index, case in enumerate(tree.iter('testcase')):
            suite, name = 'Fixture/TypedSuite/'+str(index % 2), 'Case/'+str(index)
            case.set('classname', suite)
            case.set('name', name)
            names.append(subject.full_name(suite, name))
        ET.ElementTree(tree).write(self.xml, encoding='utf-8')
        return tree, names

    def test_parameterized_junit_matches_separate_classname_and_name_exactly(self):
        _, names = self.parameterized_reader_control()
        self.assertEqual(audit_junit(self.xml, names, full_names=True)['assertion_status'], 'passed')
        with self.assertRaises(EvidenceError):
            audit_junit(self.xml, [n.replace('/', '.') for n in names], full_names=True)

    def test_parameterized_junit_missing_duplicate_skipped_and_bad_counts_fail(self):
        for mutation in ('missing', 'duplicate', 'skipped', 'counts'):
            tree, names = self.parameterized_reader_control()
            cases = list(tree.iter('testcase'))
            if mutation == 'missing': cases[0].set('name', 'Other/0')
            elif mutation == 'duplicate':
                for key in ('name', 'classname'): cases[1].set(key, cases[0].get(key))
            elif mutation == 'skipped': ET.SubElement(cases[0], 'skipped')
            else: tree.set('tests', str(len(names)+1))
            ET.ElementTree(tree).write(self.xml, encoding='utf-8')
            with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                audit_junit(self.xml, names, full_names=True)

    def test_schema6_requires_explicit_inputs_capture_and_integer_process_limits(self):
        spec = dict(self.legacy, schema_version=6, data_inputs=[], artifact_directories={}, cooperative_runtime_capture=True)
        spec['process_limits'] = dict(memory_bytes=4*1024**3, tasks=32)
        self.assertTrue(supported_specification(spec))
        for key in ('data_inputs', 'artifact_directories', 'cooperative_runtime_capture', 'process_limits'):
            missing = dict(spec); del missing[key]
            self.assertFalse(supported_specification(missing))
        for change in (dict(data_inputs=None), dict(data_inputs=[{}]),
                       dict(cooperative_runtime_capture=False), dict(unknown=True),
                       dict(schema_version=True), dict(schema_version=7)):
            self.assertFalse(supported_specification(dict(spec, **change)))
        for key in ('memory_bytes', 'tasks'):
            for value in (True, 0, -1, 1.0):
                changed = copy.deepcopy(spec); changed['process_limits'][key] = value
                self.assertFalse(supported_specification(changed))

    def test_schema5_still_requires_nonempty_inputs_and_old_ids_remain_unchanged(self):
        spec = dict(self.legacy, schema_version=5, data_inputs=[], cooperative_runtime_capture=True)
        spec['process_limits'] = dict(memory_bytes=4*1024**3, tasks=32)
        self.assertFalse(supported_specification(spec))
        self.assertTrue(supported_specification(self.legacy))
        expected = self.legacy['expected_test_ids']
        self.assertTrue(all(n.count('/') == 1 and '.' not in n for n in expected))

    def test_artifact_outputs_are_declared_owned_directories_instead_of_arbitrary_environment(self):
        self.assertTrue(artifact_directories_valid({}))
        self.assertTrue(artifact_directories_valid(dict(TIMELEARNER_PROFILE_TEST_DIR='profiles',
                                                        TL_HOT_READOUT_DIR='hot-reset')))
        for value in (None, [], {'PATH':'bin'}, {'TIMELEARNER_COMPAT_CHILD':'yes'},
                      {'TIMELEARNER_PROFILE_TEST_DIR':'../outside'},
                      {'TIMELEARNER_PROFILE_TEST_DIR':'/absolute'},
                      {'TIMELEARNER_PROFILE_TEST_DIR':'nested/path'},
                      {'TIMELEARNER_PROFILE_TEST_DIR':'same', 'TL_HOT_READOUT_DIR':'same'}):
            self.assertFalse(artifact_directories_valid(value))


if __name__ == '__main__':
    unittest.main()
