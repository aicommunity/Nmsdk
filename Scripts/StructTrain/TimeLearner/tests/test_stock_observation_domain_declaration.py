"""Recorded-domain recipe invariants. Declaration DATA, not model measurements."""
from copy import deepcopy
import unittest

from ..candidate_window_contract import GRID_TAGS, calculate_window
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from ..stock_candidate_window_study import observation_domain_declaration, recovery_declaration
from .test_stock_candidate_recovery_declaration import source_job


def origins():
    return [dict(input_index=i, assigned_peak_frame=49+40*i,
        assigned_plateau_last_frame=49+40*i, sample_count=201) for i in range(4)]


class StockObservationDomainDeclarationTest(unittest.TestCase):
    def test_preserves_physics_reference_windows_objective_and_search_budget(self):
        for branch in (False, True):
            old = recovery_declaration(source_job(branch), 'source');before = deepcopy(old)
            changed = observation_domain_declaration(old, origins())
            self.assertEqual(old, before)
            a,b = deepcopy(old),deepcopy(changed)
            for value in (a,b):
                value.pop('sha256');value['configuration'].pop('run_id')
                value['configuration']['composite_measurement']['candidate_window_policy'].pop('inputs')
            self.assertEqual(a,b)

    def test_full_domain_does_not_move_with_length_Ns_Rs_or_C_changes(self):
        changed = observation_domain_declaration(recovery_declaration(source_job(), 'source'), origins())
        config = changed['configuration'];model = config['model']
        before = [dict(length=p['attachment'],synapses=p['synapses'],resistance=p['resistance'])
            for p in model['inputs']]
        after = [dict(length=8 if i%2 else 1,synapses=128,resistance=.01 if i%2 else 100.)
            for i in range(4)]
        grid = dict(frequency_hz=model['frequency_hz'],source_origin='declaration-only',
            source_pattern_binding=digest(model['initial_isi']),
            source_profile_binding=digest(config['stimulus_profile']),**GRID_TAGS)
        c0 = dict(origin=digest('declared-C0'),maximum_relative_change=.1,
            membrane_scales={'Dendrite1_1':1.})
        c1 = deepcopy(c0);c1['membrane_scales']['Dendrite1_1'] = 1.1
        for i,origin in enumerate(origins()):
            seed = dict(input_index=i,first_frame=origin['assigned_peak_frame'],
                last_frame=origin['assigned_plateau_last_frame'],frame_count=201,grid=grid,
                initial_parameters=before,initial_capacitance=c0)
            candidate = dict(grid=grid,declared_maximum_samples=201,parameters=after,capacitance=c1)
            computed = calculate_window(config['composite_measurement']['candidate_window_policy'],seed,candidate)
            self.assertEqual((computed['first_frame'],computed['last_frame']),(0,200))
            self.assertEqual(computed['shift_frames'],0)
            self.assertEqual(computed['uncertainty_frames'],0)

    def test_bad_reference_inventory_or_domain_is_rejected(self):
        for change in ('dimension','duplicate','edge','oversized','fractional'):
            values = origins()
            if change == 'dimension':values.pop()
            elif change == 'duplicate':values[1]['input_index'] = 0
            elif change == 'edge':values[0]['assigned_peak_frame'] = 0
            elif change == 'oversized':values[0]['sample_count'] = 202
            else:values[0]['assigned_peak_frame'] = 49.5
            with self.subTest(change=change), self.assertRaises(EvidenceError):
                observation_domain_declaration(recovery_declaration(source_job(),'source'),values)

    def test_tampered_source_digest_cannot_be_rebound(self):
        job = recovery_declaration(source_job(), 'source');job['configuration']['run_id'] = 'tampered'
        with self.assertRaises(EvidenceError):observation_domain_declaration(job,origins())
