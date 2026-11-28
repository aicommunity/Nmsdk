"""Real Windows process lifetimes, including a retained terminated handle."""
import os
import subprocess
import sys
import unittest

from Scripts.StructTrain.TimeLearner.windows_stopped_recognition_study import _kernel, live


@unittest.skipUnless(os.name == 'nt', 'requires actual Windows kernel handles')
class WindowsProcessIdentityLifetimeTest(unittest.TestCase):
    def setUp(self):
        self.api, self.kernel = _kernel()
        self.child = subprocess.Popen([sys.executable, '-B', '-c', 'import time;time.sleep(30)'],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW)
        self.handle = self.kernel.OpenProcess(0x101000, False, self.child.pid)
        self.assertTrue(self.handle)
        self.owner = dict(pid=self.child.pid, **self.api.identity(self.handle))

    def tearDown(self):
        if self.child.poll() is None:
            self.child.terminate()
        self.child.wait(timeout=10)
        self.api.close(self.handle)

    def test_running_exact_identity_is_live(self):
        self.assertTrue(live(self.api, self.kernel, self.owner))

    def test_same_pid_with_different_birth_is_not_the_owned_process(self):
        changed = dict(self.owner, creation_filetime=str(int(self.owner['creation_filetime'])+1))
        self.assertFalse(live(self.api, self.kernel, changed))
        self.assertTrue(live(self.api, self.kernel, self.owner))

    def test_exited_process_with_retained_kernel_handle_is_closed(self):
        self.child.terminate();self.child.wait(timeout=10)
        self.assertFalse(self.api.running(self.handle))
        self.assertFalse(live(self.api, self.kernel, self.owner))

    def test_exit_between_running_check_and_identity_query_is_closed(self):
        test = self
        class ExitAtIdentity:
            def running(self, handle):
                return test.api.running(handle)
            def identity(self, handle):
                # Force the real child to exit at this observation boundary.
                # No fake PID, extracted implementation or replacement OS
                # lifetime is used. A dead image query can fail with WinError31.
                test.child.terminate();test.child.wait(timeout=10)
                return test.api.identity(handle)
        self.assertFalse(live(ExitAtIdentity(), self.kernel, self.owner))

    def test_live_process_identity_error_must_propagate(self):
        test = self
        class IdentityError:
            def running(self, handle):
                return test.api.running(handle)
            def identity(self, handle):
                raise PermissionError(31, 'injected live-process image query failure')
        with self.assertRaises(PermissionError):
            live(IdentityError(), self.kernel, self.owner)
        self.assertTrue(live(self.api, self.kernel, self.owner))
