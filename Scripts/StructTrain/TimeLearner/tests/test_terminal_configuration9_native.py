"""Read actual C++ cold codecs/owner ticks; never synthesize native evidence."""
import copy
import os
from pathlib import Path
import unittest

from ..composite_configuration import project_training_configuration
from ..learned_evidence import audit_learned_state
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError,load,require
from ..terminal_configuration import split_terminal_configuration,validate_terminal_policy


class NativeTerminalConfiguration9Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['TIMELEARNER_NATIVE_TERMINAL_CONFIGURATION9']).resolve(strict=True)
        cls.folders=[cls.root/(topology+'-terminal-configuration9')/('base-'+str(version))
                     for topology in ('classic','branch') for version in range(1,9)]
        require(set(cls.root.glob('*-terminal-configuration9/base-*'))==set(cls.folders),
                'terminal_configuration_native_population')

    def test_all_16_native_base_records_are_preserved(self):
        for folder in self.folders:
            with self.subTest(folder=folder.name):
                original=load(folder/'original.json');configured=load(folder/'configured9.json')
                saved=copy.deepcopy(configured);base,policy=split_terminal_configuration(configured)
                self.assertEqual(base,original);self.assertEqual(policy['maximum_wall_seconds'],3.5)
                self.assertEqual(configured,saved)
                self.assertEqual(project_training_configuration(configured),project_training_configuration(original))

    def test_invalid_or_unversioned_policy_cannot_be_ignored(self):
        original=load(self.folders[0]/'original.json');configured=load(self.folders[0]/'configured9.json')
        changed=copy.deepcopy(original);changed['terminal_selection']=configured['terminal_selection']
        with self.assertRaises(EvidenceError):project_training_configuration(changed)
        for value in (None,True,'3.5',0,-1,float('nan'),float('inf')):
            with self.subTest(value=value):
                policy=copy.deepcopy(configured['terminal_selection']);policy['maximum_wall_seconds']=value
                with self.assertRaises(EvidenceError):validate_terminal_policy(policy)
        for version in (None,True,'1',0,9):
            changed=copy.deepcopy(configured);changed['terminal_base_schema_version']=version
            with self.assertRaises(EvidenceError):project_training_configuration(changed)
        changed=copy.deepcopy(configured);changed['terminal_selection']['unknown_control']=True
        with self.assertRaises(EvidenceError):project_training_configuration(changed)

    def test_request_identity_retains_policy_while_math_view_is_unchanged(self):
        for folder in self.folders:
            original=load(folder/'original.json');configured=load(folder/'configured9.json')
            self.assertIsNone(split_terminal_configuration(original)[1])
            self.assertNotEqual(canonical_model_sha256(original),canonical_model_sha256(configured))
            changed=copy.deepcopy(configured);changed['terminal_selection']['maximum_wall_seconds']+=.125
            self.assertNotEqual(canonical_model_sha256(configured),canonical_model_sha256(changed))
            self.assertEqual(project_training_configuration(configured),project_training_configuration(changed))

    def test_all_8_configured_owner_entries_export_actual_DATA(self):
        expected={'NativeTerminalConfiguredEntry/'+topology+mode+normalization
                  for topology in ('Classic','Branch') for mode in ('Fixed','Window') for normalization in ('N0','N1')}
        paths=list(self.root.glob('configured9-*/configuration9-case.json'));seen=set()
        for path in paths:
            row=load(path);identity=row['test_id'];require(identity in expected and identity not in seen,'configured9_duplicate_case')
            require(row['kind']=='native_configured_terminal_case' and row['schema_version']==1,'configured9_descriptor')
            seen.add(identity)
            with self.subTest(case=identity):
                package=load(path.parent/row['package']);summary=load(path.parent/row['summary'])
                self.assertEqual(package['terminal_policy']['maximum_wall_seconds'],7.25)
                self.assertEqual(package['historical_state']['configuration']['schema_version'],9)
                self.assertIsNone(package['terminal_event']);self.assertEqual(package['terminal_journal'],[])
                report=audit_learned_state(package,summary,{},{})
                self.assertIsNone(report['evaluation_verdict']);self.assertFalse(report['live_authority_restored'])
        self.assertEqual(seen,expected)
