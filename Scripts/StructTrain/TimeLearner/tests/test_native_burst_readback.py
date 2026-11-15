"""Wire-declaration controls; these do not stand in for native model probes."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from .test_composite_configuration import configuration
from ..native_calibration_worker import _signed
from ..native_characterization import expected_import_parameters, subset_presented_isi, validate_job
from ..native_evidence import EvidenceError


def declaration(branch=False, n=4):
    c = configuration(branch=branch, n=n)
    c['model']['normalization'] = 'N1'
    source = _signed(dict(kind='timelearner_stopped_state', state_kind='diagnostic', certificate=None,
        controller_version=2, implementation_id='declaration-only', configuration=c,
        trained_inputs=[dict(length=1, synapses=1, resistance=1.) for _ in range(n)]))
    return _signed(dict(kind='timelearner_native_probe_job', schema_version=7,
        owner_class='NNeuronTimeLearner'+('Branch' if branch else ''), implementation_id='declaration-only',
        model=deepcopy(c['model']), profile_archives=[], stimulus_profile=deepcopy(c['stimulus_profile']),
        source_stopped=source, resistance_intervention=[dict(input_index=0, resistance=1.)],
        channel_diagnostics=True,
        presentation=dict(kind='native_burst_readback', source_ordinals=list(range(n))),
        probe=dict(run_id='readback', trial_id='readback/1', sample_id='target', protocol_revision='raw-v1',
            input_index=0, duration=.1, maximum_sample_gap=.0005, minimum_amplitude=1e-6,
            maximum_samples=201, record_spikes=False, peak_selection='none', window=None),
        maximum_model_ticks=408, maximum_wall_seconds=30.))


class NativeBurstReadbackDeclarationTest(unittest.TestCase):
    def test_full_burst_and_time_matched_noop_control_are_declared_without_peak(self):
        for branch, n in ((False, 1), (False, 7), (True, 4)):
            job = declaration(branch, n)
            self.assertFalse(validate_job(job)['training_started'])
            self.assertEqual(subset_presented_isi(job), job['model']['initial_isi'])
            self.assertEqual(expected_import_parameters(job), job['source_stopped']['trained_inputs'])

    def test_changed_resistance_preserves_source_and_changes_only_declared_input(self):
        job = declaration();original = deepcopy(job['source_stopped'])
        job.pop('sha256');job['resistance_intervention'][0]['resistance'] = .5
        validate_job(_signed(job));parameters = expected_import_parameters(job)
        self.assertEqual([p['resistance'] for p in parameters], [.5, 1., 1., 1.])
        self.assertEqual(job['source_stopped'], original)

    def test_omission_reordering_and_duplicate_source_impulses_are_forbidden(self):
        for indices in ([0, 1, 2], [1, 0, 2, 3], [0, 0, 2, 3], [0, 1, 2, 4], [False, 1, 2, 3]):
            job = declaration();job.pop('sha256');job['presentation']['source_ordinals'] = indices
            with self.subTest(indices=indices), self.assertRaises(EvidenceError):validate_job(_signed(job))

    def test_window_peak_stimulus_change_and_reserved_schema_cannot_enter_raw_readback(self):
        for change in ('window', 'peak', 'source', 'schema'):
            job = declaration();job.pop('sha256')
            if change == 'window':job['probe']['window'] = dict(begin=0., end=.1)
            elif change == 'peak':job['probe']['peak_selection'] = 'assigned_burst_wave'
            elif change == 'source':job['stimulus_profile']['amplitude'] = 2.
            else:job['schema_version'] = 8
            with self.subTest(change=change), self.assertRaises(EvidenceError):validate_job(_signed(job))

    def test_previous_subset_schema_still_forbids_resistance_intervention(self):
        job = declaration();job.pop('sha256');job['schema_version'] = 6
        job['presentation']['kind'] = 'stimulus_subset_characterization'
        with self.assertRaisesRegex(EvidenceError, 'subset_source_or_intervention_changed'):
            validate_job(_signed(job))

    def test_shared_branch_bank_cannot_receive_inconsistent_resistances(self):
        job = declaration(True);job.pop('sha256');job['resistance_intervention'][0]['resistance'] = .5
        with self.assertRaisesRegex(EvidenceError, 'shared_bank_intervention_inconsistent'):
            validate_job(_signed(job))

    def test_n0_raw_replay_is_allowed_but_rs_intervention_requires_n1(self):
        job = declaration();job.pop('sha256');job['model']['normalization'] = 'N0'
        source = job['source_stopped'];source.pop('sha256')
        source['configuration']['model']['normalization'] = 'N0'
        job['source_stopped'] = _signed(source)
        with self.assertRaisesRegex(EvidenceError, 'burst_readback_rs_requires_n1'):
            validate_job(_signed(job))
        job['resistance_intervention'] = []
        self.assertFalse(validate_job(_signed(job))['training_started'])

    def test_schema7_exit2_requests_audit_instead_of_becoming_a_success(self):
        from ..native_pipeline_worker import _structured_training_exit, audit_execution
        job = declaration();process = dict(execution='process_error', returncode=2)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertFalse(_structured_training_exit('probe', job, process, root))
            (root/'execution.json').write_text('{}', encoding='utf-8')
            self.assertTrue(_structured_training_exit('probe', job, process, root))
            # The routing decision is not evidence: absent native job/data
            # still fails the actual production execution auditor.
            with self.assertRaises((EvidenceError, OSError)):
                audit_execution('probe', root, job)
            self.assertFalse(_structured_training_exit('probe', {**job, 'schema_version': 8}, process, root))
