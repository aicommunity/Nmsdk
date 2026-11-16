"""Hash a retained native model with the actual newly built PulseLib codec."""
import os
from pathlib import Path
import unittest

from ..collector_provenance import frozen_digest
from ..contained_process import inspect
from ..contained_runner import execute
from ..native_evidence import load
from ..native_gate import audit_junit
from ..resource_reservations import Reservations
from ..runtime import applied_loader_environment


class LargeCanonicalPackageTest(unittest.TestCase):
    def test_actual_317MB_package_keeps_preexisting_semantic_digest(self):
        controls=Path(os.environ['TIMELEARNER_LARGE_CANONICAL_CONTROLS'])
        declaration=load(controls/'declaration.json');runtime=load(controls/'runtime.json')
        live=inspect(declaration['controller'])
        self.assertEqual(live['binding']['initial_main_pid'],os.getpid())
        self.assertFalse(live['all_processes_closed'])
        source=Path(os.environ['TIMELEARNER_LARGE_CANONICAL_SOURCE'])/'model.json'
        self.assertEqual(str(source),declaration['source_path'])
        before=frozen_digest(source,512*1024**2)
        self.assertEqual(before['bytes'],317475838)
        self.assertEqual(before['sha256'],declaration['source_sha256'])
        self.assertEqual(runtime['source_closure']['root']['head'],declaration['sdk_root'])
        output=Path(os.environ['TMPDIR'])/'large-canonical';output.mkdir()
        memory=4*1024**3;tasks=64
        registry=Reservations(output/'leases.sqlite3',managed_units=True,
            capacity=dict(slots=1,memory_bytes=live['memory_max']+memory,
                          tasks=live['tasks_max']+tasks,disk_bytes=128*1024**2))
        lease=registry.reserve('actual-large-canonical-package',
            [dict(path=str(source),access='read'),dict(path=str(output),access='write'),
             dict(path=str(Path(runtime['executable']['path']).parent),access='read')],
            demands=dict(slots=1,memory_bytes=live['memory_max']+memory,
                         tasks=live['tasks_max']+tasks,disk_bytes=128*1024**2),
            controller_directory=declaration['controller'],ttl_seconds=1800)
        previous=os.environ.get('TIMELEARNER_CANONICAL_PACKAGE')
        try:
            os.environ['TIMELEARNER_CANONICAL_PACKAGE']=str(source)
            with applied_loader_environment(runtime):
                result=execute(runtime,[
                    '--gtest_filter=CanonicalModelHashRecorded.PreservesActualLargeTrainingPackageDigest',
                    '--gtest_output=xml:'+str(output/'native.xml')],
                    Path(runtime['executable']['path']).parent,output/'process',900.,
                    memory_bytes=memory,tasks=tasks,cooperative_capture=True,
                    managed_reservation=(registry,lease['token']))
            self.assertEqual(result['execution'],'completed')
            self.assertTrue(inspect(output/'process/contained')['all_processes_closed'])
            self.assertEqual(load(output/'process/contained/request.json')[
                'environment']['TIMELEARNER_CANONICAL_PACKAGE'],str(source))
            inventory=audit_junit(output/'native.xml',[
                'CanonicalModelHashRecorded/PreservesActualLargeTrainingPackageDigest'])
            self.assertEqual(inventory['assertion_status'],'passed')
        finally:
            if previous is None:os.environ.pop('TIMELEARNER_CANONICAL_PACKAGE',None)
            else:os.environ['TIMELEARNER_CANONICAL_PACKAGE']=previous
            registry.release(lease['token'],note='Actual large model hash control; full training export still requires its own acceptance.')
        self.assertEqual(frozen_digest(source,512*1024**2),before)
