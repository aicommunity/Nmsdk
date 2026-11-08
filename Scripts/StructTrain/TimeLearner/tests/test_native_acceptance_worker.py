"""Metadata-only worker regressions; no compilation, numerical or model run."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from .. import native_acceptance_worker as subject
from .. import native_preparation


def declarations():
    # Complete declaration DATA for validation, not a claim of a Git checkout,
    # compilation, physical model or kernel execution in this unit fixture.
    arguments = ["--job", "/workspace/job.json"]
    source_root, pulse = 'a'*40, 'b'*40
    ids = ["Suite/First", "Suite/Second"]
    source_path = "Tests/actual.cpp"
    inventory = {"kind":"timelearner_git_case_inventory", "schema_version":1,
                 "root_commit":source_root, "source_closure":{
                     "root":{"head":source_root,"status":""},
                     "Libraries/Nmsdk-PulseLib":{"head":pulse,"status":"","recorded_gitlink":pulse}},
                 "files":{source_path:{"commit":source_root,"path":source_path,"git_blob":'c'*40,
                     "bytes":42,"sha256":'d'*64,"dialect":"literal-test-metadata",
                     "suites":None,"ids":ids,"recognized_ids":ids,"outside_declared_scope":[]}},
                 "documents":[],"ids":ids,"count":2,"compiled_inventory_verified":False,
                 "test_success_attested":False,"scientific_verdict":None}
    current = {"runplan":[{"name":"leaf", "expected_ids":["Suite/First", "Suite/Second"],
                           "wall_seconds":60}],
               "counts":{"selected_cases":2, "leaf_gates":1},
               "root":source_root,"pulse":pulse,"partitions":[{"name":"selected","ids":ids,"count":2}],
               "inventory":{"root":source_root,"total":2,"unique":2,
                            "files":{source_path:{"sha256":'d'*64,"count":2,"ids":ids}}}}
    prep = {"kind":"timelearner_native_preparation", "schema_version":2,
            "execution":{"mode":"repo_module",
                         "module":"Scripts.StructTrain.TimeLearner.native_acceptance_worker",
                         "arguments":arguments,"source":{"commit":source_root,
                             "path":"Scripts/StructTrain/TimeLearner/native_acceptance_worker.py",
                             "git_blob":'e'*40,"bytes":123,"sha256":'f'*64}},
            "module_source_bytes_verified_at_preparation":True,"loaded_module_bytes_verified":False,
            "compiled_inventory_verified":False, "kernel_closure_attested":False,
            "test_success_attested":False, "scientific_verdict":None,
            "current":current,"current_claims":copy.deepcopy(current),"source_inventory":inventory,
            "prior_bindings":[],"historical":None}
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
    def test_cache_profile_cannot_accept_prefixes_extra_flags_or_duplicate_key(self):
        flags = 'CMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING=-O1 -g1 -fsanitize=address -fno-omit-frame-pointer'
        empty = 'CMAKE_CXX_FLAGS:STRING='
        subject.validate_cache_profile('// comment\n'+flags+'\n'+empty+'\n', [flags, empty])
        for changed in (flags+' -ffast-math', flags.replace('-O1', '-O3'),
                        flags+'\n'+flags.replace(':STRING=', ':UNINITIALIZED=')):
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, 'changed_cached_build_profile'):
                subject.validate_cache_profile(changed+'\n'+empty, [flags, empty])
        with self.assertRaisesRegex(ValueError, 'complete_cache_entry_required'):
            subject.validate_cache_profile(flags, ['-fsanitize=address'])

    def test_canonical_selection_and_invocation_are_actual_data(self):
        job, prep, arguments = declarations()
        self.assertEqual(subject.validate_job(job, prep, arguments), ["Suite/First", "Suite/Second"])
        with self.assertRaisesRegex(ValueError, "invocation_mismatch"):
            subject.validate_job(job, prep, arguments+["unexpected"])

    def test_stale_hash_and_preparation_pass_claim_cannot_be_used(self):
        job, prep, arguments = declarations()
        prep["current"]["counts"]["selected_cases"] = 3
        with self.assertRaisesRegex(ValueError, "content_changed"):
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
        for field, value in (("limits", True), ("artifact", "../foreign/*.json"), ("extra", None), ("cache", [])):
            job, prep, arguments = declarations()
            if field == "limits":
                job["limits"]["leaf_tasks"] = value
            elif field == "artifact":
                job["artifacts"][0]["glob"] = value
            elif field == "cache":
                job["build"]["required_cache_tokens"] = value
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

    def test_rehashed_inconsistent_preparation_fields_are_rejected(self):
        for fault in ('root', 'nested_source_sha', 'unknown_id', 'execution', 'loaded_module'):
            job, prep, arguments = declarations()
            if fault == 'root':
                prep['current']['inventory']['root'] = '5'*40
                prep['current_claims']['inventory']['root'] = '5'*40
            elif fault == 'nested_source_sha':
                prep['current']['inventory']['files']['Tests/actual.cpp']['sha256'] = '0'*64
                prep['current_claims'] = copy.deepcopy(prep['current'])
            elif fault == 'unknown_id':
                prep['current']['runplan'][0]['expected_ids'][0] = 'Suite/Unknown'
                prep['current_claims'] = copy.deepcopy(prep['current'])
            elif fault == 'execution':
                prep['execution']['source']['git_blob'] = 'invalid'
            else:
                prep['loaded_module_bytes_verified'] = True
            prep['sha256'] = subject._digest({k:v for k,v in prep.items() if k != 'sha256'})
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                subject.validate_job(job, prep, arguments)

    def test_runtime_drift_and_unreadable_protected_path_do_not_suppress_other_captures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = object.__new__(subject.Worker)
            worker.out = root; worker.source = root/'source'; worker.runtime = root/'runtime'
            worker.paths = {'resources':root/'resources'}
            closure = {'Bin':{'recorded_gitlink':'a'*40}}
            worker.api = (SimpleNamespace(source_closure=lambda _:copy.deepcopy(closure)),)
            worker.source_files = lambda:({'actual':'unchanged'}, {})
            worker.git = lambda *args:('a'*40).encode()
            def inventory(path):
                if path == root/'unreadable':
                    raise OSError('capture-failed')
                return {'actual':'changed'} if path == worker.runtime else {'actual':'unchanged'}
            worker.inventory = inventory
            errors = worker.final_captures({'actual':'original'},
                {str(root/'unreadable'):{},str(root/'keeper'):{'actual':'unchanged'}},
                {'actual':'unchanged'}, closure)
            self.assertEqual([e['capture'] for e in errors], ['current_runtime','protected:'+str(root/'unreadable')])
            for name in ('source-hashes-after.json','source-closure-after.json','resource-closure-after.json'):
                self.assertTrue((root/name).is_file(), name)
            self.assertIn(str(root/'keeper'), json.loads((root/'protected-files-after.json').read_bytes()))

    def test_identical_materialized_bytes_do_not_hide_changed_source_or_resource_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = object.__new__(subject.Worker)
            worker.out = root; worker.source = root/'source'; worker.paths = {'resources':root/'resources'}
            worker.api = (SimpleNamespace(source_closure=lambda _:{'root':{'head':'changed'}}),)
            worker.git = lambda *args:b'changed'
            worker.source_files = lambda:({'bytes':'identical'}, {})
            errors = worker.final_captures(None, {}, {'bytes':'identical'},
                {'root':{'head':'original'},'Bin':{'recorded_gitlink':'a'*40}})
            self.assertEqual([e['capture'] for e in errors], ['source_closure','resource_closure'])
            self.assertTrue((root/'source-hashes-after.json').is_file())


if __name__ == "__main__":
    unittest.main()
