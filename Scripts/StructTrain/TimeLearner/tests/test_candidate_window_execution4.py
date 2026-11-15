"""Execution4 DATA scope controls; server-only, no native execution claim."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from ..candidate_window_execution_evidence import audit_candidate_window_execution
from ..composite_execution_evidence import audit_composite_execution
from ..composite_configuration import METHOD
from ..native_evidence import EvidenceError


def descriptor(*, preflight):
    return dict(schema_version=4,base_schema_version=1,measurement_method=METHOD,
        measurement_archive=None,source_origin=None,model_revision='initial-model',model_semantic_hash='initial-model',
        composite_counters=dict(attempt=dict(logical_groups=0,native_probes=0,sampled_frames=0) if preflight else None,
            archive=dict(groups=0,native_probes=0,sampled_frames=0,primary_bytes=0) if preflight else None,
            execution=dict(native_trials=0,sampled_frames=0)))


class CandidateWindowExecution4Test(unittest.TestCase):
    def test_preflight_known_zeros_are_not_execution_attestation(self):
        with tempfile.TemporaryDirectory() as folder:
            result=audit_candidate_window_execution(descriptor(preflight=True),Path(folder),set(),mode='preflight',base_version=1)
        self.assertFalse(result['owned_archive_present']);self.assertFalse(result['native_execution_verified'])

    def test_failed_start_requires_unknown_retained_counts(self):
        value=descriptor(preflight=False)
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(audit_candidate_window_execution(value,Path(folder),set(),mode='train',base_version=1)['owned_archive_present'])
            value['composite_counters']['attempt']=dict(logical_groups=0,native_probes=0,sampled_frames=0)
            with self.assertRaises(EvidenceError):
                audit_candidate_window_execution(value,Path(folder),set(),mode='train',base_version=1)

    def test_unknown_preflight_accounting_is_not_filled_with_zeros(self):
        value=descriptor(preflight=True);value['composite_counters']['archive']=None
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(EvidenceError):
            audit_candidate_window_execution(value,Path(folder),set(),mode='preflight',base_version=1)

    def test_version3_and_version4_are_distinct(self):
        old=descriptor(preflight=True);old['schema_version']=3
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)
            self.assertFalse(audit_composite_execution(old,path,set(),mode='preflight',base_version=1)['native_execution_verified'])
            with self.assertRaises(EvidenceError):audit_candidate_window_execution(old,path,set(),mode='preflight',base_version=1)
            with self.assertRaises(EvidenceError):audit_composite_execution(descriptor(preflight=True),path,set(),mode='preflight',base_version=1)

    def test_mixed_package_version_rejected_before_primary_read(self):
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(EvidenceError):
            audit_candidate_window_execution(descriptor(preflight=False),Path(folder),set(),mode='train',base_version=1,
                package=dict(schema_version=5,protocol=dict(schema_version=4),measurement_archive=dict(schema_version=1)))

    def test_preflight_actual_model_mismatch_is_not_ignored(self):
        value=deepcopy(descriptor(preflight=True));value['model_semantic_hash']='different-model'
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(EvidenceError):
            audit_candidate_window_execution(value,Path(folder),set(),mode='preflight',base_version=1)
