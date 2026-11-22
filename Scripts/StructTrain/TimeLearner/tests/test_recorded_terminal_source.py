"""Recorded-matrix transfer against real completed native terminal restorations."""
import copy
import os
from pathlib import Path
import unittest

from ..composite_primary import filesystem_primary_resolver
from ..native_evidence import EvidenceError,load,require
from ..recorded_diagnostic_matrix import audit_recorded_source,recorded_source_archive


class RecordedTerminalSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['TIMELEARNER_RECORDED_TERMINAL_SOURCES']).resolve(strict=True)
        cls.cases=[]
        for topology in ('classic','branch'):
            folder=cls.root/topology
            package=load(folder/'train_stopped_state.json');summary=load(folder/'train_stopped_summary.json')
            require(package['schema_version']==8 and package['terminal_event']['status']=='restored' and
                    package['model_revision']!=package['historical_state']['model_revision'],
                    'recorded_terminal_fixture_requires_actual_restore')
            cls.cases.append((folder,package,summary))

    def test_outer_actual_model_and_original_raw_epoch_are_separate(self):
        for folder,package,summary in self.cases:
            with self.subTest(topology=folder.name):
                audit=audit_recorded_source(package,summary,external_resolver=filesystem_primary_resolver(folder))
                self.assertEqual(audit['model_revision'],package['model_revision'])
                self.assertEqual(audit['package_schema_version'],8)
                self.assertIsNone(audit['evaluation_verdict'])
                self.assertIsNone(package['certificate'])
                self.assertEqual(recorded_source_archive(package),package['historical_state']['measurement_archive'])
                self.assertFalse(audit['native_import_verified'])

    def test_embedded_data_cannot_hide_a_damaged_external_trial(self):
        for folder,package,summary in self.cases:
            original=filesystem_primary_resolver(folder)
            ref=recorded_source_archive(package)['records'][0]['raw_trials'][0]['primary_ref']
            def corrupted(relative):
                raw=original(relative)
                return raw+b'corrupt' if relative==ref['relative_path'] else raw
            with self.subTest(topology=folder.name),self.assertRaises(EvidenceError):
                audit_recorded_source(package,summary,external_resolver=corrupted)

    def test_learned_or_unversioned_history_cannot_replace_diagnostic_source(self):
        for _,original,_ in self.cases:
            for mutation in ('learned','plain_history','recursive_history'):
                package=copy.deepcopy(original)
                if mutation=='learned':package['kind']='timelearner_learned_state'
                else:package['historical_state']['schema_version']=1 if mutation=='plain_history' else 8
                with self.subTest(mutation=mutation),self.assertRaises(EvidenceError):
                    recorded_source_archive(package)
