"""The real reservation parser must admit a shared tool/SDK source tree."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from Scripts.StructTrain.TimeLearner import linux_count_training as training
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
from Scripts.StructTrain.TimeLearner.resource_reservations import _resources, ReservationError


class LinuxCountTrainingResourcesTest(unittest.TestCase):
    def test_shared_source_is_one_read_and_outputs_stay_exclusive(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            source = root/'source'; source.mkdir()
            plan = dict(sdk=source, runtime=dict(executable=dict(path=str(root/'runtime/console'))),
                        controls=root/'controls', output=root/'output', directory=root/'controller')
            with patch.object(training, 'SOURCE', source):
                rows = training._reservation_resources(plan)
            parsed = _resources(rows)
            self.assertEqual(len(parsed), 5)
            self.assertEqual([r['access'] for r in parsed if r['canonical_path'] == str(source)], ['read'])
            self.assertEqual({r['canonical_path'] for r in parsed if r['access'] == 'write'},
                             {str(plan['output']), str(plan['directory'])})
            # The registry's general duplicate guard must remain strict.
            with self.assertRaisesRegex(ReservationError, 'duplicate_reservation_resource'):
                _resources(rows+[rows[0]])

    def test_conflicting_output_cannot_be_silently_folded_into_source(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            source = root/'source'; source.mkdir()
            plan = dict(sdk=source, runtime=dict(executable=dict(path=str(root/'runtime/console'))),
                        controls=root/'controls', output=source, directory=root/'controller')
            with patch.object(training, 'SOURCE', source):
                with self.assertRaisesRegex(EvidenceError, 'count_linux_resource_access_collision'):
                    training._reservation_resources(plan)


if __name__ == '__main__':
    unittest.main()
