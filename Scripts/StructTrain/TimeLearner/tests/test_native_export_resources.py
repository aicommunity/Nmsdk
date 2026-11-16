"""Reject invalid native budgets before creating a long training attempt."""
import unittest
from ..native_evidence import EvidenceError
from ..uniform_profile_study import native_resource_demands


class NativeExportResourcesTest(unittest.TestCase):
    def test_native_limit_is_independent_of_controller_limit(self):
        controller=dict(memory_max=8*1024**3,tasks_max=32)
        low=native_resource_demands(controller,4*1024**3,64)
        high=native_resource_demands(controller,12*1024**3,128)
        self.assertEqual(low['memory_bytes'],12*1024**3)
        self.assertEqual(high['memory_bytes'],20*1024**3)
        self.assertEqual(high['tasks'],160)
        self.assertEqual(controller,dict(memory_max=8*1024**3,tasks_max=32))

    def test_invalid_unbounded_or_overflowing_budget_is_rejected(self):
        bounded=dict(memory_max=8*1024**3,tasks_max=32)
        for memory,tasks in [(True,64),(0,64),(-1,64),(4.5,64),(2**63,64),
                             (1024,False),(1024,0),(1024,1.5),(1024,2**63)]:
            with self.subTest(memory=memory,tasks=tasks), self.assertRaises(EvidenceError):
                native_resource_demands(bounded,memory,tasks)
        for controller in ({},dict(memory_max=None,tasks_max=32),
                           dict(memory_max=1024,tasks_max=0),
                           dict(memory_max=2**63-1,tasks_max=32)):
            with self.subTest(controller=controller), self.assertRaises(EvidenceError):
                native_resource_demands(controller,1024,64)
