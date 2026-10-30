"""Linux process integration: actual binaries, pidfds, cancellation and timeout."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
import unittest

from ..native_evidence import EvidenceError
from ..process_runner import execute, inspect_attempt, verify_runtime
from ..runtime import file_record, digest_json, runtime_content_identity, resolved_libraries


class OwnedProcessTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.ini=self.root/"app.ini";self.ini.write_text("actual process integration fixture\n")

    def manifest(self, name="sleep.rs2", binary="/bin/sleep"):
        executable=self.root/name;shutil.copy2(Path(binary).resolve(),executable)
        manifest={"schema_version":2,"source_closure":{"fixture":"actual system binary; no neural model"},
                  "executable":file_record(executable),"app_ini":file_record(self.ini),
                  "compiler":file_record(Path("/bin/true")),"build_flags":{},
                  "resolved_libraries":resolved_libraries(executable),"loaded_process_files":None,
                  "loader_environment":{k:os.environ[k] for k in ("LD_LIBRARY_PATH","QT_PLUGIN_PATH","QT_QPA_PLATFORM") if k in os.environ}}
        manifest["runtime_identity"]=runtime_content_identity(manifest)
        manifest["runtime_fingerprint"]=digest_json(manifest["runtime_identity"])
        return manifest

    def test_suffix_executable_and_live_identity_readback(self):
        manifest=self.manifest();output=self.root/"attempt"
        seen=[]
        def observe():
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                if (output/"loaded-files.json").exists():
                    seen.append(inspect_attempt(output));return
                time.sleep(.01)
        thread=threading.Thread(target=observe);thread.start()
        result=execute(manifest,["1"],self.root,output,3)
        thread.join()
        self.assertEqual(result["execution"],"completed",result)
        self.assertEqual(result["runtime_provenance"],"loaded_files_captured")
        self.assertEqual(seen[0]["execution"],"running")
        owned=json.loads((output/"owned-process.json").read_text())
        self.assertTrue(owned["executable"].endswith("sleep.rs2"))
        self.assertEqual(inspect_attempt(output),result)
        self.assertIsNone(result["model_time"])
        self.assertIsNone(result["scientific_verdict"])

    def test_timeout_does_not_signal_unrelated_process(self):
        manifest=self.manifest();unrelated=subprocess.Popen(["/bin/sleep","10"])
        try:
            result=execute(manifest,["10"],self.root,self.root/"timeout",.15)
            self.assertEqual(result["execution"],"timeout",result)
            self.assertIsNone(unrelated.poll())
            self.assertLess(result["wall_seconds"],3)
        finally:
            unrelated.terminate();unrelated.wait()

    def test_cancellation_request_stops_only_owned_process(self):
        manifest=self.manifest();output=self.root/"cancelled"
        def cancel():
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                if (output/"owned-process.json").exists():
                    (output/"cancel.request").write_text("requested by test\n");return
                time.sleep(.01)
        thread=threading.Thread(target=cancel);thread.start()
        result=execute(manifest,["10"],self.root,output,3);thread.join()
        self.assertEqual(result["execution"],"interrupted",result)
        self.assertIsNotNone(result["returncode"])

    def test_nonzero_exit_and_log_capture(self):
        manifest=self.manifest("console.e05b","/bin/sh")
        result=execute(manifest,["-c","printf actual_stdout; printf actual_stderr >&2; exit 7"],
                       self.root,self.root/"nonzero",3)
        self.assertEqual(result["execution"],"process_error")
        self.assertEqual(result["returncode"],7)
        self.assertEqual((self.root/"nonzero/stdout.log").read_text(),"actual_stdout")
        self.assertEqual((self.root/"nonzero/stderr.log").read_text(),"actual_stderr")

    def test_changed_runtime_and_reused_attempt_are_rejected(self):
        manifest=self.manifest();self.ini.write_text("changed conditions")
        with self.assertRaises(EvidenceError):verify_runtime(manifest)
        manifest=self.manifest("sleep.rs1")
        execute(manifest,[".01"],self.root,self.root/"once",3)
        with self.assertRaises(FileExistsError):execute(manifest,[".01"],self.root,self.root/"once",3)

    def test_unknown_or_stale_attempt_never_becomes_completed(self):
        output=self.root/"stale";output.mkdir()
        self.assertEqual(inspect_attempt(output)["execution"],"unknown")
        (output/"owned-process.json").write_text(json.dumps({"pid":os.getpid(),"boot_id":"wrong-boot"}))
        self.assertEqual(inspect_attempt(output)["reason"],"worker_boot_changed")

    def test_sigkill_escalation_for_owned_term_resistant_binary(self):
        manifest=self.manifest("console.rs2","/bin/sh")
        result=execute(manifest,["-c","trap '' TERM; while :; do :; done"],self.root,
                       self.root/"resistant",.2,terminate_grace_seconds=.05)
        self.assertEqual(result["execution"],"timeout",result)
        self.assertEqual(result["returncode"],-9)
