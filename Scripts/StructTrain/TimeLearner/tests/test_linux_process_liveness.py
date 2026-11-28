"""Actual unreaped Linux children exercise the production identity predicate."""
import os
import sys
import time
import unittest

from ..owned_native_job import _identity, _same_process


@unittest.skipUnless(sys.platform == 'linux', 'actual Linux /proc and waitid required')
class LinuxProcessLiveness(unittest.TestCase):
    def test_unreaped_child_is_dead_without_reaping_or_assuming_success(self):
        read_fd, write_fd = os.pipe()
        child = os.fork()
        if child == 0:
            os.close(write_fd)
            os.read(read_fd, 1)
            os._exit(23)
        os.close(read_fd)
        try:
            identity = _identity(child)
            self.assertTrue(_same_process(identity))
            self.assertFalse(_same_process(dict(identity, start_ticks=str(int(identity['start_ticks'])+1))))
            os.close(write_fd)
            write_fd = None
            deadline = time.monotonic()+5
            while True:
                observed = os.waitid(os.P_PID, child, os.WEXITED | os.WNOWAIT | os.WNOHANG)
                if observed is not None:
                    break
                self.assertLess(time.monotonic(), deadline, 'real child did not exit')
                time.sleep(.01)
            self.assertEqual(observed.si_status, 23)
            self.assertEqual(_identity(child), identity)
            self.assertFalse(_same_process(identity))
            # The predicate must not reap somebody else's child or reinterpret
            # its nonzero exit as success; exact ownership/closure gates follow.
            self.assertEqual(os.waitid(os.P_PID, child, os.WEXITED | os.WNOWAIT).si_status, 23)
        finally:
            if write_fd is not None:
                os.close(write_fd)
            os.waitpid(child, 0)
        self.assertFalse(_same_process(identity))
