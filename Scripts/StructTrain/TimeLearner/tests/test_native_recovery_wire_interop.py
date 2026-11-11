"""Replay actual C++ cold8/runtime3 documents with independent Python readers.

These are immutable DATA fixtures from the accepted Linux C2 run, not an
executor, service ledger, checkpoint, or scientific classification result.
Run this suite on the experiment workers.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import unittest

from ..candidate_window_contract import configuration_view, validate_protocol
from ..candidate_window_runtime_plan import (
    audit_candidate_window_runtime_plan, audit_candidate_window_runtime_recovery_plan,
)
from ..native_evidence import EvidenceError


class NativeRecoveryWireInteropTest(unittest.TestCase):
    def documents(self, topology):
        root = Path(os.environ['TIMELEARNER_NATIVE_RECOVERY_WIRE_FIXTURE'])
        manifest = json.loads((root/'manifest.json').read_bytes())
        self.assertEqual(manifest['root_commit'], '5643f8319e081b1cf4647965854709d35dc44df7')
        self.assertEqual(manifest['pulse_commit'], '0fb035a221d6da2b2e883bf767a20a35318d3154')
        self.assertIsNone(manifest['scientific_verdict'])
        result = {}
        for name in ('initial-configuration', 'runtime-plan', 'protocol',
                     'legacy-configuration', 'legacy-runtime-plan'):
            relative = topology+'/'+name+'.json'
            raw = (root/relative).read_bytes()
            self.assertEqual(len(raw), manifest['files'][relative]['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest['files'][relative]['sha256'])
            result[name] = json.loads(raw)
        return result

    def recovery(self, topology):
        documents = self.documents(topology)
        original = deepcopy(documents)
        configuration, protocol, runtime = (documents[n] for n in ('initial-configuration', 'protocol', 'runtime-plan'))
        self.assertEqual(configuration['schema_version'], 8)
        self.assertEqual(runtime['schema_version'], 3)
        validate_protocol(protocol, configuration)
        self.assertEqual(configuration_view(configuration)['schema_version'], 6)
        result = audit_candidate_window_runtime_recovery_plan(runtime, configuration, protocol)
        self.assertTrue(result['runtime_plan_validated'])
        for key in ('live_authority_restored', 'native_execution_verified', 'training_certificate_verified'):
            self.assertFalse(result[key])
        self.assertIsNone(result['scientific_verdict'])
        self.assertEqual(documents, original)

    def legacy(self, topology):
        documents = self.documents(topology)
        configuration, protocol, runtime = (documents[n] for n in ('legacy-configuration', 'protocol', 'legacy-runtime-plan'))
        self.assertEqual(configuration['schema_version'], 7)
        self.assertEqual(runtime['schema_version'], 2)
        validate_protocol(protocol, configuration)
        self.assertTrue(audit_candidate_window_runtime_plan(runtime, configuration, protocol)['runtime_plan_validated'])
        with self.assertRaises(EvidenceError):
            audit_candidate_window_runtime_recovery_plan(runtime, configuration, protocol)

    def downgrade(self, topology):
        documents = self.documents(topology)
        configuration, protocol, runtime = (documents[n] for n in ('initial-configuration', 'protocol', 'runtime-plan'))
        with self.assertRaises(EvidenceError):
            audit_candidate_window_runtime_plan(runtime, configuration, protocol)
        changed = deepcopy(runtime)
        changed['schema_version'] = 2
        with self.assertRaises(EvidenceError):
            audit_candidate_window_runtime_plan(changed, configuration, protocol)
        changed = deepcopy(configuration)
        changed['schema_version'] = 7
        with self.assertRaises(EvidenceError):
            validate_protocol(protocol, changed)

    def test_classic_native_recovery_documents(self): self.recovery('classic')
    def test_branch_native_recovery_documents(self): self.recovery('branch')
    def test_classic_native_legacy_documents(self): self.legacy('classic')
    def test_branch_native_legacy_documents(self): self.legacy('branch')
    def test_classic_native_documents_cannot_be_downgraded(self): self.downgrade('classic')
    def test_branch_native_documents_cannot_be_downgraded(self): self.downgrade('branch')
