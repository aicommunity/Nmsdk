"""Actual terminal8 DATA imports and native source/destination waveform pairs.

The corpus is produced by the existing configured8 and actual-restoration8
native cases, not by changing schema labels on historical fixtures.
"""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError, load, number
from ..physical_model_data_evidence import audit_physical_model_data


def signed(value):
    value['sha256'] = digest({k: v for k, v in value.items() if k != 'sha256'})
    return value


class NativeTerminalPhysicalDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ['TIMELEARNER_NATIVE_TERMINAL_CONFIGURATION9']).resolve(strict=True)
        cls.rows = []
        for topology in ('classic', 'branch'):
            for method in ('fixed4', 'window5'):
                for normalization in ('N0', 'N1'):
                    for completed in (False, True):
                        name = (f'configured9-{topology}-terminal-{method}-{normalization}-completed'
                                if completed else f'{topology}-terminal-actual-{method}-{normalization}')
                        folder = root/name
                        cls.rows.append((name, completed, load(folder/'terminal-state8.json'),
                                         load(folder/'terminal-physical-data.json')))

    def test_actual_source8_graph_and_data_roles_are_preserved(self):
        for name, completed, source, fixture in self.rows:
            with self.subTest(case=name):
                self.assertEqual(source['schema_version'], 8)
                self.assertEqual(fixture['source_sha256'], source['sha256'])
                self.assertEqual(source['kind'], 'timelearner_completed_state' if completed else 'timelearner_stopped_state')
                data = fixture['physical_model_data']
                report = audit_physical_model_data(data)
                self.assertEqual(data['source_boundary']['schema_version'], 8)
                self.assertEqual(data['source_boundary']['sha256'], source['sha256'])
                self.assertEqual(data['model_revision'], source['model_revision'])
                self.assertEqual(data['parameters'], source['trained_inputs'])
                self.assertEqual(data['neuron']['graph']['identity'], source['neuron']['graph']['identity'])
                if not completed:
                    self.assertNotEqual(data['model_revision'], source['historical_state']['model_revision'])
                for key in ('source_training_evidence_checked', 'native_import_verified',
                            'training_certificate_transferred', 'calibration_confirmed'):
                    self.assertFalse(report[key])
                self.assertIsNone(data['certificate']);self.assertIsNone(report['evaluation_verdict'])
                self.assertEqual(fixture['destination_controller_epoch'], 0)
                self.assertEqual(fixture['destination_controller_state'], 'idle')
                self.assertEqual(fixture['frozen_destination_controller_state'], 'idle')
                self.assertTrue(fixture['frozen_destination_has_data'])
                self.assertFalse(fixture['frozen_destination_certificate_present'])
                self.assertFalse(fixture['training_certificate_transferred'])
                for key in ('historical_state', 'measurement_archive', 'terminal_journal', 'search_history', 'source_solo'):
                    self.assertNotIn(key, data)

    def test_recompute_native_waveform_residual_from_every_recorded_sample(self):
        for name, _, _, fixture in self.rows:
            with self.subTest(case=name):
                rows = fixture['response_rows'];self.assertGreater(len(rows), 100)
                self.assertEqual(fixture['response_columns'],
                    ['native_absolute_time', 'actual_input', 'source_potentials', 'data_potentials'])
                largest = excursion = 0.;previous = None
                initial = rows[0][2]
                for time, stimulus, source, data in rows:
                    time = number(time);number(stimulus)
                    if previous is not None:self.assertGreater(time, previous)
                    previous = time
                    self.assertEqual(len(source), len(data));self.assertEqual(len(source), len(initial))
                    for index, (a, b) in enumerate(zip(source, data)):
                        a, b = number(a), number(b)
                        largest = max(largest, abs(a-b));excursion = max(excursion, abs(a-initial[index]))
                self.assertEqual(largest, fixture['maximum_sample_difference'])
                self.assertEqual(excursion, fixture['source_response_excursion'])
                self.assertLessEqual(largest, 1e-12);self.assertGreater(excursion, 1e-6)
                for field in ('source_probe', 'data_probe'):
                    observation = fixture[field]['observation']
                    self.assertTrue(observation['complete']);self.assertEqual(observation['sample_count'], len(rows))

    def test_frozen_data_is_self_contained_and_unknown_references_stay_rejected(self):
        from ..native_pipeline_worker import _load_source_case, _snapshot_source
        for name, _, source, fixture in self.rows:
            with self.subTest(case=name):
                data = fixture['recognition_model_data'];recognition = fixture['recognition_source']
                report = audit_physical_model_data(data, frozen=True)
                self.assertEqual(data['source_boundary']['sha256'], recognition['sha256'])
                self.assertEqual(data['source_solo_revision'], source['model_revision'])
                self.assertEqual(data['parameters'], recognition['recognition_inputs'])
                self.assertFalse(report['source_training_evidence_checked'])
                self.assertFalse(report['training_certificate_transferred'])
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory);path = root/'model.json'
                    path.write_text(json.dumps(data, allow_nan=False), encoding='utf-8')
                    copied = _snapshot_source(path, root/'snapshot', physical_data=True)
                    self.assertEqual([p.name for p in copied.parent.iterdir()], ['model.json'])
                    self.assertEqual(_load_source_case('physical-model-evaluate', copied)[0], data)
                for model, version in ((fixture['physical_model_data'], 9), (data, 8)):
                    changed = copy.deepcopy(model);changed['source_boundary']['schema_version'] = version
                    with self.assertRaises(EvidenceError):audit_physical_model_data(signed(changed))
