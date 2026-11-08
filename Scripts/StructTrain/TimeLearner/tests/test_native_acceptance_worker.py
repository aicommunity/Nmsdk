"""Metadata-only worker regressions; no compilation, numerical or model run."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import native_acceptance_worker as subject


def declarations():
    arguments = ["--job", "/workspace/job.json"]
    current = {"runplan":[{"name":"leaf", "expected_ids":["Suite/First", "Suite/Second"],
                           "wall_seconds":60}],
               "counts":{"selected_cases":2, "leaf_gates":1},
               "inventory":{"files":{"Tests/actual.cpp":{}}}}
    prep = {"kind":"timelearner_native_preparation", "schema_version":2,
            "execution":{"mode":"repo_module",
                         "module":"Scripts.StructTrain.TimeLearner.native_acceptance_worker",
                         "arguments":arguments},
            "compiled_inventory_verified":False, "kernel_closure_attested":False,
            "test_success_attested":False, "scientific_verdict":None,
            "current":current, "source_inventory":{"files":{"Tests/actual.cpp":{}}}}
    prep["sha256"] = subject._digest(prep)
    job = {"kind":"timelearner_native_acceptance_job", "schema_version":1,
           "workspace":"/workspace", "preparation":"/workspace/preparation.json",
           "paths":{k:"/workspace/"+k for k in
                    ("source", "build", "runtime", "output", "resources", "framework")},
           "build":{"type":"Release", "parallel":1, "wall_seconds":120,
                    "required_cache_tokens":["CMAKE_BUILD_TYPE:STRING=Release"]},
           "limits":{"whole_wall_seconds":240, "leaf_memory_bytes":128*1024**2,
                     "leaf_tasks":32, "physical_free_floor_bytes":512*1024**2,
                     "reservation_memory_bytes":256*1024**2, "reservation_disk_bytes":128*1024**2},
           "asan_options":None, "protected_runtimes":[],
           "artifacts":[{"glob":"leaf/export/*.json", "minimum":1, "maximum":None}]}
    return job, prep, arguments


class NativeAcceptanceWorkerTest(unittest.TestCase):
    def test_canonical_selection_and_invocation_are_actual_data(self):
        job, prep, arguments = declarations()
        self.assertEqual(subject.validate_job(job, prep, arguments), ["Suite/First", "Suite/Second"])
        with self.assertRaisesRegex(ValueError, "invocation_mismatch"):
            subject.validate_job(job, prep, arguments+["unexpected"])

    def test_stale_hash_and_preparation_pass_claim_cannot_be_used(self):
        job, prep, arguments = declarations()
        prep["current"]["counts"]["selected_cases"] = 3
        with self.assertRaisesRegex(ValueError, "preparation_identity"):
            subject.validate_job(job, prep, arguments)
        prep["test_success_attested"] = True
        prep["sha256"] = subject._digest({k:v for k,v in prep.items() if k != "sha256"})
        with self.assertRaisesRegex(ValueError, "outside_scope"):
            subject.validate_job(job, prep, arguments)

    def test_duplicate_missing_count_or_reused_leaf_is_rejected(self):
        for mode in ("duplicate_case", "missing_count", "reused_leaf"):
            job, prep, arguments = declarations()
            current = prep["current"]
            if mode == "duplicate_case":
                current["runplan"][0]["expected_ids"] = ["Suite/First", "Suite/First"]
            elif mode == "missing_count":
                current["counts"]["selected_cases"] = 3
            else:
                current["runplan"].append({"name":"leaf", "expected_ids":["Suite/Third"], "wall_seconds":30})
                current["counts"] = {"selected_cases":3, "leaf_gates":2}
            prep["sha256"] = subject._digest({k:v for k,v in prep.items() if k != "sha256"})
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                subject.validate_job(job, prep, arguments)

    def test_boolean_budgets_and_escaping_artifact_paths_are_rejected(self):
        for field, value in (("limits", True), ("artifact", "../foreign/*.json"), ("extra", None)):
            job, prep, arguments = declarations()
            if field == "limits":
                job["limits"]["leaf_tasks"] = value
            elif field == "artifact":
                job["artifacts"][0]["glob"] = value
            else:
                job["undeclared"] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                subject.validate_job(job, prep, arguments)

    def test_partial_failed_and_skipped_junit_never_fills_expected_cases(self):
        raw = ('<testsuites><testsuite name="Suite">'
               '<testcase classname="Suite" name="First" status="run" result="completed"/>'
               '<testcase classname="Suite" name="Second" status="run" result="completed"><failure/></testcase>'
               '<testcase classname="Suite" name="Third" status="notrun" result="suppressed"/>'
               '</testsuite></testsuites>')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"native.xml"; path.write_text(raw)
            self.assertEqual(subject.observed_junit(path),
                             (["Suite/First", "Suite/Second"], ["Suite/Second"], ["Suite/Third"]))
            path.write_text('<testsuites/>')
            self.assertEqual(subject.observed_junit(path), ([], [], []))

    def test_duplicate_junit_case_is_not_two_observations(self):
        case = '<testcase classname="Suite" name="First" status="run" result="completed"/>'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"native.xml"; path.write_text('<testsuites>'+case+case+'</testsuites>')
            with self.assertRaisesRegex(ValueError, "duplicate_JUnit_case"):
                subject.observed_junit(path)

    def test_json_rejects_duplicate_nonfinite_and_aliased_job(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"job.json"
            for raw in ('{"a":1,"a":2}', '{"a":NaN}'):
                path.write_text(raw)
                with self.subTest(raw=raw), self.assertRaises(ValueError):
                    subject._json(path)
            path.write_text('{}')
            alias = path.with_name("alias.json")
            alias.symlink_to(path)
            with self.assertRaisesRegex(ValueError, "job_file_alias"):
                subject._json(alias)

    def test_runtime_inventory_keeps_symlink_text_and_excludes_git_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'.git').mkdir(); (root/'.git/lock').write_text('mutable')
            (root/'binary').write_bytes(b'actual bytes'); (root/'link').symlink_to('binary')
            worker = object.__new__(subject.Worker)
            first = worker.inventory(root)
            (root/'.git/lock').write_text('changed metadata')
            self.assertEqual(first, worker.inventory(root))
            self.assertEqual(first['link'], {'kind':'symlink', 'text':'binary'})
            (root/'binary').write_bytes(b'changed actual bytes')
            self.assertNotEqual(first, worker.inventory(root))

    def test_protected_output_is_rejected_before_creating_any_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            job, prep, arguments = declarations()
            job['workspace'] = str(root)
            job['paths'] = {k:str(root/k) for k in job['paths']}
            protected = root/'historical'; protected.mkdir()
            output = protected/'new-output'
            job['paths']['output'] = str(output)
            job['protected_runtimes'] = [str(protected)]
            module = root/'source/Scripts/StructTrain/TimeLearner/native_acceptance_worker.py'
            with patch.object(subject, '__file__', str(module)), \
                 self.assertRaisesRegex(ValueError, 'protected_write_path_overlap'):
                subject.Worker(job, prep, arguments)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
