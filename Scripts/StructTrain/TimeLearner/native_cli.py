"""Bounded read-only Console CLI check before a native job is allowed to start.

Runtime integrity alone does not distinguish the Console from a GoogleTest
binary built from the same tree. Help is an existing pre-engine parser path;
this check is an advertised-interface gate, not scientific execution proof.
"""
import hashlib
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time

from .native_evidence import require
from .process_runner import verify_runtime

OPERATIONS = frozenset(('train', 'export', 'evaluate', 'diagnostic-evaluate',
                        'preflight', 'probe', 'calibrate', 'posttune'))
MAX_HELP_BYTES = 128 * 1024
MAX_HELP_SECONDS = 5.


def inspect_native_cli(runtime, operations):
    require(type(operations) in (list, tuple) and bool(operations) and
            all(type(x) is str and x in OPERATIONS for x in operations),
            'native_cli_unknown_operation')
    requested = sorted(set(operations))
    executable = verify_runtime(runtime)
    environment = dict(os.environ)
    for key in ('LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM'):
        if key in runtime['loader_environment']:
            environment[key] = runtime['loader_environment'][key]
        else:
            environment.pop(key, None)
    # A mistaken GoogleTest target must list/help without executing test bodies.
    environment.update(GTEST_FILTER='-*', GTEST_LIST_TESTS='1',
                       GTEST_REPEAT='1', GTEST_SHUFFLE='0')
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='timelearner-cli-interface-') as directory:
        with (Path(directory)/'help.log').open('w+b') as stream:
            process = subprocess.Popen([str(executable), '--help'], cwd=directory,
                stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                env=environment, start_new_session=True)
            pidfd = None
            try:
                pidfd = os.pidfd_open(process.pid)
                while process.poll() is None:
                    require(stream.seek(0, 2) <= MAX_HELP_BYTES, 'native_cli_help_output_limit')
                    require(time.monotonic()-started < MAX_HELP_SECONDS, 'native_cli_help_timeout')
                    time.sleep(.01)
                require(stream.seek(0, 2) <= MAX_HELP_BYTES, 'native_cli_help_output_limit')
                stream.seek(0);raw = stream.read(MAX_HELP_BYTES+1)
                require(process.returncode == 0, 'native_cli_help_failed')
            finally:
                if process.poll() is None:
                    # The live owned leader cannot have been reused while its
                    # pidfd is retained. Stop its own process group, never names.
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=2)
                if pidfd is not None:
                    os.close(pidfd)
    verify_runtime(runtime)
    text = raw.decode('utf-8', errors='strict')
    required = ['--app-ini', '--timelearner-output',
                *('--timelearner-'+operation for operation in requested)]
    present = {flag: bool(re.search(r'(?m)^\s*'+re.escape(flag)+r'(?:\s|,|=|$)', text))
               for flag in required}
    require(all(present.values()), 'native_cli_missing_advertised_operation')
    return {'kind': 'timelearner_native_cli_interface', 'schema_version': 1,
            'runtime_fingerprint': runtime['runtime_fingerprint'],
            'executable_sha256': runtime['executable']['sha256'],
            'operations': requested, 'arguments': ['--help'],
            'advertised_options': present, 'help_text': text,
            'help_sha256': hashlib.sha256(raw).hexdigest(),
            'returncode': process.returncode, 'wall_seconds': time.monotonic()-started,
            'native_job_executed': False, 'scientific_verdict': None}
