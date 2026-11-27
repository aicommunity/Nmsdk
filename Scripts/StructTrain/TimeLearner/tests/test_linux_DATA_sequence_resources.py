"""Shared reader/SDK admission and the real reservation writer exclusion."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import linux_physical_recognition_sequence as sequence
from ..native_evidence import EvidenceError
from ..resource_reservations import Reservations, ReservationError, _resources


class LinuxDATASequenceResources(unittest.TestCase):
    def layout(self, root):
        sdk = root/'sdk'; sdk.mkdir()
        p = dict(sdk=sdk, controls=root/'controls', output=root/'phases')
        outputs = {phase: root/phase for phase in sequence.PHASES}
        runtime = dict(executable=dict(path=str(root/'runtime/NeuroModelerConsole')))
        return p, outputs, runtime

    def test_shared_sdk_is_accepted_without_losing_distinct_tool_readers(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve(); p, outputs, runtime = self.layout(root)
            training = dict(operation='train', execution_root=str(root), sdk_source=str(p['sdk']))
            self.assertEqual(sequence.training_sdk_source(training, root), p['sdk'])
            for source, expected in ((p['sdk'], 7), (root/'tool', 8)):
                with patch.object(sequence, 'SOURCE', source):
                    rows = sequence.evaluation_resources(p, 'confirmation', outputs, runtime)
                parsed = _resources(rows)
                self.assertEqual(len(parsed), expected)
                self.assertEqual({r['canonical_path'] for r in parsed if r['access'] == 'write'},
                                 {str(p['output']), str(outputs['confirmation'])})
                self.assertEqual(sum(r['canonical_path'] == str(p['sdk']) for r in parsed), 1)

    def test_scope_rejects_relative_outside_missing_and_aliased_sdk(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve(); p, _, _ = self.layout(root)
            (root/'parent').mkdir()
            for path in ('sdk', str(root.parent), str(root/'missing'), str(root/'parent/../sdk')):
                training = dict(operation='train', execution_root=str(root), sdk_source=path)
                with self.subTest(path=path), self.assertRaisesRegex(EvidenceError,
                        'linux_DATA_sequence_native_training_scope'):
                    sequence.training_sdk_source(training, root)

    def test_source_output_collision_is_not_promoted_to_write(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve(); p, outputs, runtime = self.layout(root)
            outputs['baseline'] = p['sdk']
            with patch.object(sequence, 'SOURCE', p['sdk']), self.assertRaisesRegex(
                    ReservationError, 'reservation_resource_access_collision'):
                sequence.evaluation_resources(p, 'baseline', outputs, runtime)

    def test_shared_read_lease_blocks_competing_writer_in_real_ledger(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve(); p, outputs, runtime = self.layout(root)
            with patch.object(sequence, 'SOURCE', p['sdk']):
                rows = sequence.evaluation_resources(p, 'baseline', outputs, runtime)
            ledger = Reservations(root/'leases.sqlite3', capacity=dict(slots=2, memory_bytes=1024, disk_bytes=1024))
            lease = ledger.reserve('DATA-read', rows, demands=dict(slots=1, memory_bytes=1, disk_bytes=1))
            try:
                with self.assertRaisesRegex(ReservationError, 'reservation_resource_conflict'):
                    ledger.reserve('competing-build', [dict(path=str(p['sdk']), access='write')],
                        demands=dict(slots=1, memory_bytes=1, disk_bytes=1))
                ledger.validate_paths(lease['token'])
            finally:
                ledger.release(lease['token'], note='Shared DATA reader test closed.')


if __name__ == '__main__':
    unittest.main()
