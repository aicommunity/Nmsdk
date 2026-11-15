"""Real cold Train, plus positive readback of every live full-domain proposal."""
import os
from pathlib import Path

from ..native_evidence import load
from . import test_stock_candidate_recovery_train as shared


class StockObservationDomainTrainTest(shared.StockCandidateRecoveryTrainTest):
    expected_plan_version = 3

    def train_case(self, case):
        super().train_case(case)
        controls = Path(os.environ['TIMELEARNER_STOCK_COLD8_TRAIN_CONTROLS'])
        spec = load(controls/'declaration.json');folder = Path(spec['output'])/case
        result = load(folder/'index.json');package = load(folder/result['package_path'])
        rows = package['configuration']['composite_measurement']['candidate_window_policy']['inputs']
        measured_candidates = 0
        for record in package['measurement_archive']['records']:
            method = record['method_specification'];frame = method['candidate_frame']
            if frame is None:
                continue  # Initial reference capture retains its original windows.
            row = rows[method['assigned_input']]
            self.assertEqual(frame['first_frame'], 0)
            self.assertEqual(frame['first_frame'], row['hard_first_frame'])
            self.assertEqual(frame['last_frame'], row['hard_last_frame'])
            measured_candidates += 1
        self.assertGreater(measured_candidates, 0)
