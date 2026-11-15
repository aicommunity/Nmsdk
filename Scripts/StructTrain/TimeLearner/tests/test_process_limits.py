"""Early admission of real worker limits, before queue/lease/launch effects."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ..contained_process import start
from ..contained_runner import execute
from ..native_evidence import EvidenceError


class WorkerLimitPreflightTest(unittest.TestCase):
    def test_cli_accepts_one_day_and_rejects_36_hours_without_output_or_launch(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            def call(wall, path):
                return subprocess.run([sys.executable, '-m', 'Scripts.StructTrain.TimeLearner.process_limits',
                    '--memory-bytes', '4294967296', '--tasks', '128', '--wall-seconds', str(wall),
                    '--output', str(path)], cwd=Path(__file__).resolve().parents[4],
                    capture_output=True, text=True, timeout=30)
            accepted = root/'accepted.json';result = call(86400, accepted)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(accepted.read_text())
            self.assertEqual(data['limits'], {'memory_bytes': 4294967296, 'tasks': 128,
                                             'maximum_wall_seconds': 86400})
            self.assertFalse(data['worker_started']);self.assertFalse(data['resources_reserved'])
            self.assertIsNone(data['scientific_verdict'])
            rejected = root/'rejected.json';result = call(129600, rejected)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)['reason'], 'contained_limits_invalid')
            self.assertFalse(rejected.exists())
            original = accepted.read_bytes();result = call(86400, accepted)
            self.assertEqual(result.returncode, 2);self.assertEqual(accepted.read_bytes(), original)

    @unittest.skipUnless(sys.platform == 'linux', 'actual Linux worker entry points required')
    def test_actual_entry_points_reject_invalid_cap_before_manifest_reservation_or_output(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw);output = root/'not-created'
            # An opaque invalid reservation context would fail if touched.
            # Limit rejection must precede its construction and runtime reads.
            with self.assertRaisesRegex(EvidenceError, '^contained_limits_invalid$'):
                start({}, [], root, output, memory_bytes=4294967296, tasks=128,
                      maximum_wall_seconds=129600, managed_reservation=object())
            self.assertFalse(output.exists())
            with self.assertRaisesRegex(EvidenceError, '^invalid_contained_wall_budget$'):
                execute({}, [], root, output, 129600, memory_bytes=4294967296, tasks=128,
                        managed_reservation=object())
            self.assertFalse(output.exists())
