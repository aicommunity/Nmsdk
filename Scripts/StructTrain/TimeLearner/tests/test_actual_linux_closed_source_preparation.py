"""Admission against the actual closed sequential Train, without a new model run."""
from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest

from ..linux_physical_recognition_sequence import (
    FIELDS, PROJECTED_FIELDS, context, evaluation_limits, guard, original_projection_source)
from ..native_evidence import EvidenceError


class ActualLinuxClosedSourcePreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = os.environ.get('TIMELEARNER_LINUX_CLOSED_SOURCE_REQUEST')
        if sys.platform != 'linux' or not name:
            raise unittest.SkipTest('requires the real closed M40 sequential Train and contained receipts')
        cls.plan = context(Path(name))

    def test_real_closed_groups_and_full_primary_audit_bind_the_actual_stopped_package(self):
        source = original_projection_source(self.plan)
        self.assertEqual(source['execution']['model_revision'],
            '8a8b447f4ecb17f7e9140aa5504f5dedea523ce4e6d802b4a032dc7cd3d44412')
        self.assertEqual(source['execution']['training_outcome'], 'budget_exhausted')
        self.assertIs(source['execution']['completed_boundary'], False)
        self.assertEqual(source['package']['size'], 1185881421)
        self.assertEqual(source['package']['sha256'],
            '9881c643cd9c70db739a2c6f1801bf58751f6f00fcb8d8f9785547b331ff21de')
        self.assertIs(source['terminal']['native_import_verified'], False)

    def test_unrelated_job_cannot_borrow_the_valid_primary_audit(self):
        p = deepcopy(self.plan); p['q']['expected_job_sha256'] = '0'*64
        with self.assertRaisesRegex(EvidenceError, 'original_primary_source_mismatch'):
            original_projection_source(p)

    def test_different_contained_identity_cannot_borrow_the_closed_group(self):
        for role in ('train', 'audit'):
            p = deepcopy(self.plan); p['q']['source_contained_groups'][role]['binding_sha256'] = '0'*64
            with self.subTest(role=role), self.assertRaisesRegex(EvidenceError, 'original_group_not_closed'):
                original_projection_source(p)

    def test_changed_original_audit_receipt_is_rejected_before_preparation(self):
        p = deepcopy(self.plan); p['q']['source_audit_terminal']['sha256'] = '0'*64
        with self.assertRaisesRegex(EvidenceError, 'original_audit_changed'):
            guard(p)

    def test_schema3_requires_explicit_closed_source_bindings_and_integer_native_budget(self):
        q = self.plan['q']; self.assertEqual(set(q), PROJECTED_FIELDS)
        self.assertEqual(evaluation_limits(q), dict(native_wall_seconds=5400,
            python_phase_wall_seconds=5800, reservation_ttl_seconds=6000))
        for key in ('source_audit_terminal','source_contained_groups','predecessor_owner'):
            changed = deepcopy(q); changed.pop(key)
            with self.subTest(key=key), self.assertRaisesRegex(EvidenceError, 'request_schema'):
                evaluation_limits(changed)
        for value in (True, 5400., 0, 36001):
            changed = deepcopy(q); changed['native_evaluation_wall_seconds'] = value
            with self.subTest(value=value), self.assertRaisesRegex(EvidenceError, 'evaluation_wall_budget'):
                evaluation_limits(changed)

    def test_projection_protocol_cannot_silently_use_legacy_owner_fields_or_tune_the_threshold(self):
        for key, value in (('source_audit_controls', '/unrelated'), ('source_audit_owner', {}),
                           ('threshold', .01), ('expected_counts', {'TP':1,'TN':7})):
            q = deepcopy(self.plan['q']); q[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(EvidenceError, 'request_schema'):
                evaluation_limits(q)
        self.assertNotEqual(FIELDS, PROJECTED_FIELDS)


if __name__ == '__main__':
    unittest.main()
