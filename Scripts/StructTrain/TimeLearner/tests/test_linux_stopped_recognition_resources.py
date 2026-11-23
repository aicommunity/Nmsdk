"""Reproduce the real shared SDK/tool reservation failure without a new Train."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import linux_stopped_recognition_study as study
from ..resource_reservations import Reservations, ReservationError, _resources, coalesce_resource_requests


class LinuxStoppedRecognitionResourcesTest(unittest.TestCase):
    def plan(self,root):
        source=root/'sdk';source.mkdir()
        return dict(sdk=source,paths=dict(source_train=root/'Train',source_audit_job=root/'audit',
            source_request=root/'original/request.json',template_envelope=root/'template/envelope.json'),
            controls=root/'controls',output=root/'phases')

    def test_shared_tool_and_sdk_fold_once_with_all_output_writes_retained(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name).resolve();plan=self.plan(root)
            with patch.object(study,'SOURCE',plan['sdk']):
                rows=study.reservation_resources(plan,root/'baseline',root/'inputs')
            parsed=_resources(rows)
            self.assertEqual(len(parsed),9)
            self.assertEqual([r['access']for r in parsed if r['canonical_path']==str(plan['sdk'])],['read'])
            self.assertEqual({r['canonical_path']for r in parsed if r['access']=='write'},
                {str(plan['controls']),str(plan['output']),str(root/'baseline'),str(root/'inputs')})
            with self.assertRaisesRegex(ReservationError,'duplicate_reservation_resource'):
                _resources(rows+[rows[0]])

    def test_distinct_tool_tree_is_not_lost(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name).resolve();plan=self.plan(root);tool=root/'tool';tool.mkdir()
            with patch.object(study,'SOURCE',tool):
                rows=study.reservation_resources(plan,root/'baseline',root/'inputs')
            parsed=_resources(rows)
            self.assertEqual(len(parsed),10)
            self.assertTrue({str(tool),str(plan['sdk'])}<={r['canonical_path']for r in parsed})

    def test_source_output_collision_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name).resolve();plan=self.plan(root)
            with patch.object(study,'SOURCE',plan['sdk']):
                with self.assertRaisesRegex(ReservationError,'reservation_resource_access_collision'):
                    study.reservation_resources(plan,plan['sdk'],root/'inputs')

    def test_canonical_alias_and_real_ledger_preserve_competing_writer_conflict(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name).resolve();source=root/'source';source.mkdir();(root/'alias-parent').mkdir()
            rows=coalesce_resource_requests([dict(path=str(source),access='read'),
                dict(path=str(root/'alias-parent/../source'),access='read')])
            self.assertEqual(len(rows),1)
            ledger=Reservations(root/'leases.sqlite3',capacity=dict(slots=2,memory_bytes=1024,disk_bytes=1024))
            lease=ledger.reserve('reader',rows,demands=dict(slots=1,memory_bytes=1,disk_bytes=1))
            try:
                with self.assertRaisesRegex(ReservationError,'reservation_resource_conflict'):
                    ledger.reserve('writer',[dict(path=str(source),access='write')],
                        demands=dict(slots=1,memory_bytes=1,disk_bytes=1))
            finally:
                ledger.release(lease['token'],note='Metadata-only test reader released.')
