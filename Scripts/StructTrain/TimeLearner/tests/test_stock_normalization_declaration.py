"""N0 is a separate declared condition; declaration checks are not native proof."""
from copy import deepcopy
import unittest

from ..native_evidence import EvidenceError
from ..n1_protocol_robustness import _signed
from ..stock_candidate_window_study import (
    ALGORITHMS, normalization_declaration, observation_domain_declaration, recovery_declaration,
)
from .test_stock_candidate_recovery_declaration import source_job
from .test_stock_observation_domain_declaration import origins


def original(branch=False):
    job = source_job(branch)
    for i, (p, b) in enumerate(zip(job['configuration']['model']['inputs'], job['configuration']['search']['bounds'])):
        b['minimum_synapses'] = b['maximum_synapses'] = 1
        if i == 3:
            b['minimum_length'] = b['maximum_length'] = p['attachment']
    return observation_domain_declaration(recovery_declaration(_signed(job), 'cold-N1'), origins())


class StockNormalizationDeclarationTest(unittest.TestCase):
    def test_only_declared_actuator_bounds_mode_and_condition_labels_change(self):
        for branch in (False, True):
            source = original(branch);before = deepcopy(source)
            result = normalization_declaration(source, 'cold-N0')
            self.assertEqual(source, before)
            expected = deepcopy(source)
            expected['implementation_id'] = ALGORITHMS[4]
            c = expected['configuration']
            c.update(run_id='cold-N0', protocol_revision=ALGORITHMS[4])
            c['model']['normalization'] = 'N0'
            for i, (p, b) in enumerate(zip(c['model']['inputs'], c['search']['bounds'])):
                b.update(minimum_resistance=p['resistance'], maximum_resistance=p['resistance'],
                    minimum_synapses=1, maximum_synapses=1 if i == 3 else 128)
            self.assertEqual(result, _signed(expected))
            self.assertNotEqual(source['sha256'], result['sha256'])
            self.assertEqual(result['configuration']['search']['tolerances'], c['search']['tolerances'])

    def test_retains_heterogeneous_initial_resistances_without_global_intersection(self):
        source = original()
        for i, (p, b) in enumerate(zip(source['configuration']['model']['inputs'], source['configuration']['search']['bounds'])):
            p['resistance'] = 10.+i
            b['minimum_resistance'] = 1.;b['maximum_resistance'] = 100.
        result = normalization_declaration(_signed(source), 'N0')
        for i, b in enumerate(result['configuration']['search']['bounds']):
            self.assertEqual((b['minimum_resistance'], b['maximum_resistance']), (10.+i, 10.+i))

    def test_rejects_repeated_conversion_stale_digest_nonfull_window_and_moving_anchor(self):
        good = original()
        for bad in ('N0', 'digest', 'window', 'anchor', 'Ns', 'tolerance'):
            source = deepcopy(good);c = source['configuration']
            if bad == 'N0':c['model']['normalization'] = 'N0'
            elif bad == 'window':c['composite_measurement']['candidate_window_policy']['inputs'][0]['delay_frames_per_segment'] = 1
            elif bad == 'anchor':c['search']['bounds'][3]['maximum_length'] += 1
            elif bad == 'Ns':c['search']['bounds'][0]['maximum_synapses'] = 128
            elif bad == 'tolerance':c['search']['tolerances']['sync'] = .2
            if bad != 'digest':source = _signed(source)
            else:c['run_id'] += '/changed'
            with self.subTest(bad=bad), self.assertRaises(EvidenceError):
                normalization_declaration(source, 'N0')
