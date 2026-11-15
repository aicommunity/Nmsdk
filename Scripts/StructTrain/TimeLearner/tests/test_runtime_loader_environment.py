"""Pinned native environment application; strict runner guard remains intact."""
import os
import unittest
from unittest.mock import patch

from ..native_evidence import EvidenceError
from ..runtime import applied_loader_environment


class RuntimeLoaderEnvironmentTest(unittest.TestCase):
    def test_declared_values_replace_parent_values_and_are_restored(self):
        inherited = dict(LD_LIBRARY_PATH='/old/lib', QT_PLUGIN_PATH='/old/plugins', QT_QPA_PLATFORM='parent')
        declared = dict(LD_LIBRARY_PATH='/runtime/lib', QT_PLUGIN_PATH='/runtime/plugins', QT_QPA_PLATFORM='offscreen')
        with patch.dict(os.environ, inherited):
            with applied_loader_environment({'loader_environment': declared}):
                self.assertEqual({key: os.environ.get(key) for key in declared}, declared)
            self.assertEqual({key: os.environ.get(key) for key in inherited}, inherited)

    def test_absent_manifest_keys_are_unset_and_parent_presence_is_restored(self):
        with patch.dict(os.environ, {'QT_QPA_PLATFORM': 'parent', 'TIMELEARNER_TEST_KEEP': 'same'}):
            previous = {key: os.environ.get(key) for key in ('LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM')}
            with applied_loader_environment({'loader_environment': {}}):
                self.assertTrue(all(key not in os.environ for key in previous))
                self.assertEqual(os.environ['TIMELEARNER_TEST_KEEP'], 'same')
            self.assertEqual({key: os.environ.get(key) for key in previous}, previous)

    def test_exception_restores_values_and_absence(self):
        with patch.dict(os.environ):
            os.environ.pop('QT_QPA_PLATFORM', None)
            with self.assertRaisesRegex(RuntimeError, 'original failure'):
                with applied_loader_environment({'loader_environment': {'QT_QPA_PLATFORM': 'offscreen'}}):
                    self.assertEqual(os.environ['QT_QPA_PLATFORM'], 'offscreen')
                    raise RuntimeError('original failure')
            self.assertNotIn('QT_QPA_PLATFORM', os.environ)

    def test_arbitrary_keys_types_and_nul_are_rejected_before_mutation(self):
        for environment in ({'PATH': '/not-authorized'}, {'QT_QPA_PLATFORM': None},
                            {'QT_QPA_PLATFORM': 'bad\0value'}, []):
            with self.subTest(environment=environment):
                previous = dict(os.environ)
                with self.assertRaises(EvidenceError):
                    with applied_loader_environment({'loader_environment': environment}):
                        self.fail('invalid environment entered')
                self.assertEqual(dict(os.environ), previous)
