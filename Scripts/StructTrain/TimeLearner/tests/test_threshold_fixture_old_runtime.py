"""Measure existing completed-training fixture failures on an older SDK."""
import os
from pathlib import Path
import unittest

from ..native_calibration_worker import _write
from ..native_evidence import load
from ..native_gate import run_native_gate


class ThresholdFixtureOldRuntimeTest(unittest.TestCase):
    def test_original_sdk_preconditions_are_measured_without_assuming_pass_or_failure(self):
        controls = Path(os.environ['TIMELEARNER_OLD_THRESHOLD_GATE'])
        output = Path(os.environ['TMPDIR'])/'old-threshold-fixture-two'
        result = run_native_gate(controls/'gate.json', output)
        self.assertEqual(result['validity'], 'valid')
        self.assertEqual(result['inventory']['observed'], 2)
        _write(Path(os.environ['TMPDIR'])/'old-threshold-fixture-result.json', result)
        # Assertion failures are the subject of this control, not a passing
        # production suite. Preserve the original XML/stdout and failed IDs.
