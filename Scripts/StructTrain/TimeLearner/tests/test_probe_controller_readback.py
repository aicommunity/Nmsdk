"""DATA contract controls; no model, live authority or training proof is faked."""
from copy import deepcopy
import unittest
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError
from ..probe_controller_readback import audit_idle_composite_controller


def data():
    record = dict(group_id='reference/0', attempt_id='a1', consumed=True,
        measurement=dict(raw_potential=.01, semantic_proof_id='proof'), logical_request=dict(input_id='input0'))
    archive = dict(source_binding=dict(initial_epoch=0), records=[record], reference_group_ids=['reference/0'],
        final_group_ids=[], counters=dict(attempt=dict(logical_groups=1, native_probes=3, sampled_frames=30),
                                         archive=dict(primary_bytes=1000)))
    source = dict(schema_version=7, session_attempt=1, model_epoch=2, protocol=dict(schema_version=5),
        configuration=dict(schema_version=8), measurement_archive=archive, reference_complete=True,
        recovery_ledger=dict(deliveries=[]))
    summary = dict(kind='native_probe_idle_controller_readback', schema_version=1, state='idle', certificate=None,
        reference_probes=0, search_present=False, session_attempt=1, model_epoch=2,
        protocol_sha256=sha(source['protocol']), source_binding_sha256=sha(archive['source_binding']),
        initial_configuration_sha256=sha(source['configuration']),
        record_signatures_sha256=sha([dict(group_id='reference/0', attempt_id='a1', consumed=True, semantic_proof_id='proof')]),
        recovery_deliveries_sha256=sha([]), recovery_delivery_log_intact=True,
        reference_group_ids=['reference/0'], final_group_ids=[], groups=1, native_probes=3, sampled_frames=30,
        primary_bytes=1000, reference_rows=[dict(input_id='input0', raw_potential=.01,
                                               group_id='reference/0', semantic_proof_id='proof')])
    return summary, source


class ProbeControllerReadbackTest(unittest.TestCase):
    def test_idle_readback_does_not_require_legacy_packets_or_finished_summary(self):
        summary, source = data();before = deepcopy((summary, source))
        result = audit_idle_composite_controller(summary, source)
        self.assertFalse(result['finished_training_boundary_claimed'])
        self.assertFalse(result['controller_checkpoint']);self.assertEqual((summary, source), before)

    def test_changed_history_or_source_binding_is_rejected(self):
        for key in ('source_binding_sha256', 'initial_configuration_sha256', 'record_signatures_sha256',
                    'protocol_sha256', 'recovery_deliveries_sha256'):
            summary, source = data();summary[key] = '0'*64
            with self.subTest(key=key), self.assertRaises(EvidenceError):audit_idle_composite_controller(summary, source)

    def test_active_search_certificate_counter_and_epoch_changes_are_rejected(self):
        for key, value in (('state', 'finished'), ('search_present', True), ('certificate', {}),
                           ('reference_probes', 1), ('model_epoch', 3), ('native_probes', 4)):
            summary, source = data();summary[key] = value
            with self.subTest(key=key), self.assertRaises(EvidenceError):audit_idle_composite_controller(summary, source)

    def test_changed_reference_amplitude_and_duplicate_reference_are_rejected(self):
        for duplicate in (False, True):
            summary, source = data()
            if duplicate:summary['reference_rows'].append(deepcopy(summary['reference_rows'][0]))
            else:summary['reference_rows'][0]['raw_potential'] = .02
            with self.subTest(duplicate=duplicate), self.assertRaises(EvidenceError):audit_idle_composite_controller(summary, source)

    def test_incomplete_capture_cannot_invent_reference_rows(self):
        summary, source = data();source['reference_complete'] = False
        with self.assertRaises(EvidenceError):audit_idle_composite_controller(summary, source)
        summary['reference_rows'] = []
        self.assertTrue(audit_idle_composite_controller(summary, source)['idle_readback_checked'])
