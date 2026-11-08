import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from Scripts.StructTrain.TimeLearner import declared_time_scales as subject
from Scripts.StructTrain.TimeLearner.config_document import ConfigDocument, TextEdit
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError


def project(*, global_frequency="1", default_frequency="1", individual="0", channel="00"):
    return (f'<Project><Channels><{channel}><ParametersFileName>Parameters_00.xml</ParametersFileName>'
            f'<GlobalTimeStep>{global_frequency}</GlobalTimeStep><DefaultTimeStep>{default_frequency}</DefaultTimeStep>'
            f'<UseIndTimeStepFlag>{individual}</UseIndTimeStepFlag></{channel}></Channels></Project>').encode()


def parameters(capacity="1", resistance="1", *, extra="", class_name="RegisteredStorageImage"):
    return (f'<SaveProperties><Soma Class="{class_name}"><Parameters><Capacity>{capacity}</Capacity>'
            f'<Resistance>{resistance}</Resistance>{extra}</Parameters></Soma></SaveProperties>').encode()


def mode(report):
    return report["parameter_blocks"][0]["modes"][0]


class DeclaredTimeScalesTest(unittest.TestCase):
    def test_registered_image_names_are_not_inferred_cpp_classes_or_physics(self):
        record = subject.audit_declared_pair(project(), parameters())
        self.assertEqual(mode(record)["q"], 1)
        self.assertEqual(record["parameter_blocks"][0]["registered_image_or_class_name"], "RegisteredStorageImage")
        self.assertEqual(record["applicability"]["physics"], "unknown")
        self.assertFalse(record["applicability"]["effective_model_attested"])
        self.assertFalse(record["applicability"]["storage_resolution_attested"])
        self.assertIsNone(record["integrator_stability_verdict"])
        self.assertIsNone(record["scientific_verdict"])

    def test_real_numeric_channel_dialect_bom_comments_and_attributes_survive(self):
        raw = b'\xef\xbb\xbf<?xml version="1.0"?>\r\n' + project().replace(b'<Channels>', b'<!-- <00>fake</00> --><Channels>')
        record = subject.audit_declared_pair(raw, parameters(class_name="Image&amp;Variant"))
        self.assertEqual(record["clock"]["project_channel_path"], ["Project", "Channels", "00"])
        self.assertEqual(record["parameter_blocks"][0]["registered_image_or_class_name"], "Image&Variant")
        self.assertEqual(record["inputs"]["project"]["sha256"], hashlib.sha256(raw).hexdigest())

    def test_attribute_view_is_read_only_without_changing_existing_text_edits(self):
        raw = parameters(class_name="Image&amp;Variant")
        document = ConfigDocument(raw)
        node = document.select(("SaveProperties", "Soma"))
        with self.assertRaises(TypeError):
            node.attributes["Class"] = "Other"
        self.assertEqual(document.edited([]), raw)
        changed = document.edited([TextEdit(("SaveProperties", "Soma", "Parameters", "Capacity"), "1", "2")])
        self.assertEqual(changed, raw.replace(b'<Capacity>1</Capacity>', b'<Capacity>2</Capacity>'))
        self.assertEqual(ConfigDocument(changed).root.children[0].attributes["Class"], "Image&Variant")

    def test_missing_project_never_silently_uses_2000(self):
        record = subject.audit_declared_pair(None, parameters())
        self.assertIsNone(record["clock"]["frequency_hz"])
        self.assertEqual(record["diagnostic_status"], "not_assessed")
        self.assertIsNone(mode(record)["q"])
        self.assertIn("project_document_missing", record["clock"]["issues"])

    def test_missing_clock_fields_and_flags_are_explicitly_unknown(self):
        for tag in [b'<GlobalTimeStep>1</GlobalTimeStep>', b'<UseIndTimeStepFlag>0</UseIndTimeStepFlag>']:
            with self.subTest(tag=tag):
                record = subject.audit_declared_pair(project().replace(tag, b''), parameters())
                self.assertIsNone(mode(record)["q"])
                self.assertTrue(record["clock"]["issues"])

    def test_zero_global_uses_only_explicit_positive_declared_default(self):
        record = subject.audit_declared_pair(project(global_frequency="0e0", default_frequency="4"), parameters())
        self.assertEqual(mode(record)["q"], 4)
        self.assertEqual(record["clock"]["basis"], "declared_project_DefaultTimeStep")
        missing = project(global_frequency="0").replace(b'<DefaultTimeStep>1</DefaultTimeStep>', b'')
        self.assertIsNone(mode(subject.audit_declared_pair(missing, parameters()))["q"])

    def test_individual_clock_is_unresolved_and_override_is_hypothetical(self):
        record = subject.audit_declared_pair(project(individual="1"), parameters())
        self.assertIsNone(mode(record)["q"])
        override = subject.audit_declared_pair(project(individual="1"), parameters(), explicit_frequency_hz=8)
        self.assertEqual(mode(override)["q"], 8)
        self.assertEqual(override["clock"]["basis"], "explicit_hypothetical_override")
        self.assertFalse(override["clock"]["effective_frequency_attested"])
        self.assertEqual(override["diagnostic_status"], "partially_assessed_conditionally")

    def test_duplicate_channel_binding_is_not_flattened_to_same_frequency(self):
        raw = project().replace(b'</Channels>', project(channel="01").split(b'<Channels>')[1].split(b'</Channels>')[0]+b'</Channels>')
        record = subject.audit_declared_pair(raw, parameters())
        self.assertIsNone(mode(record)["q"])
        self.assertTrue(record["clock"]["issues"])

    def test_other_parameters_filename_cannot_bind_a_project_clock(self):
        record = subject.audit_declared_pair(project(), parameters(), parameter_filename="Parameters_01.xml")
        self.assertIsNone(mode(record)["q"])

    def test_component_time_step_is_not_replaced_with_global_or_override(self):
        for override in [None, 4]:
            with self.subTest(override=override):
                record = subject.audit_declared_pair(project(), parameters(extra='<TimeStep>8</TimeStep>'),
                                                     explicit_frequency_hz=override)
                self.assertIsNone(mode(record)["q"])
                self.assertIn("component_TimeStep_requires_effective_resolution", record["parameter_blocks"][0]["issues"])

    def test_empty_and_no_rc_document_never_get_positive_classification(self):
        for raw in [b'<SaveProperties/>', b'<SaveProperties><Model><Parameters><Activity>1</Activity></Parameters></Model></SaveProperties>']:
            with self.subTest(raw=raw):
                record = subject.audit_declared_pair(project(), raw)
                self.assertEqual(record["diagnostic_status"], "not_assessed")
                self.assertEqual(record["summary"]["conditionally_assessed_modes"], 0)
                self.assertIn("no_declared_RC_parameter_blocks", record["issues"])

    def test_malformed_document_is_not_assessed_with_consistent_empty_summary(self):
        record = subject.audit_declared_pair(project(), b'<Root><Broken></Root>')
        self.assertEqual(record["diagnostic_status"], "not_assessed")
        self.assertEqual(record["summary"]["declared_modes"], 0)
        self.assertTrue(record["issues"])

    def test_invalid_capacity_tokens_are_retained_as_unresolved(self):
        for text in ["0", "-1", "nan", "inf", "1e999", "not-a-number", "1_000", "1 2"]:
            with self.subTest(text=text):
                record = subject.audit_declared_pair(project(), parameters(capacity=text))
                self.assertIsNone(mode(record)["q"])
                self.assertTrue(record["parameter_blocks"][0]["issues"])
                json.dumps(record, allow_nan=False)

    def test_invalid_resistance_is_not_omitted_beside_valid_mode(self):
        record = subject.audit_declared_pair(project(), parameters(resistance="nan", extra='<FBResistance>2</FBResistance>'))
        self.assertEqual(len(record["parameter_blocks"][0]["modes"]), 2)
        self.assertIsNone(record["parameter_blocks"][0]["modes"][0]["q"])
        self.assertEqual(record["parameter_blocks"][0]["modes"][1]["q"], 2)
        self.assertEqual(record["diagnostic_status"], "partially_assessed_conditionally")

    def test_missing_or_duplicate_capacity_does_not_borrow_another_block(self):
        for raw in [parameters().replace(b'<Capacity>1</Capacity>', b''),
                    parameters(extra='<Capacity>2</Capacity>')]:
            with self.subTest(raw=raw):
                record = subject.audit_declared_pair(project(), raw)
                self.assertIsNone(mode(record)["q"])

    def test_nonfinite_or_underflow_product_never_escapes_as_json_infinity(self):
        for c, r in [("1e200", "1e200"), ("1e-200", "1e-200")]:
            with self.subTest(c=c, r=r):
                record = subject.audit_declared_pair(project(), parameters(c, r))
                self.assertIsNone(mode(record)["q"])
                self.assertIn("time_scale_product_not_finite_positive", mode(record)["issues"])
                json.dumps(record, allow_nan=False)

    def test_nonfinite_inverse_is_not_stored_after_positive_subnormal_product(self):
        record = subject.audit_declared_pair(project(), parameters(resistance="1e-320"))
        self.assertIsNone(mode(record)["q"])
        self.assertIsNone(mode(record)["inverse_q"])
        self.assertIn("time_scale_inverse_not_finite_positive", mode(record)["issues"])

    def test_threshold_counts_and_bands_share_exact_versioned_policy(self):
        for q in [math.nextafter(.5, 0), .5, math.nextafter(.5, 1),
                  math.nextafter(1., 0), 1., math.nextafter(1., 2), 2., math.nextafter(2., 3)]:
            with self.subTest(q=q):
                record = subject.audit_declared_pair(project(), parameters(resistance=repr(q)))
                self.assertEqual(mode(record)["threshold_membership"], {str(t): q <= t for t in (.5, 1., 2.)})
                self.assertEqual(record["summary"]["conditional_q_counts"], {str(t): int(q <= t) for t in (.5, 1., 2.)})
                self.assertEqual(record["threshold_policy"]["relative_tolerance"], 0)

    def test_returned_threshold_metadata_cannot_mutate_future_policy(self):
        first = subject.audit_declared_pair(project(), parameters())
        first["threshold_policy"]["thresholds"].append(100)
        second = subject.audit_declared_pair(project(), parameters())
        self.assertEqual(second["threshold_policy"]["thresholds"], [.5, 1., 2.])

    def test_duplicate_component_names_keep_distinct_block_ordinals(self):
        soma = parameters().removeprefix(b'<SaveProperties>').removesuffix(b'</SaveProperties>')
        record = subject.audit_declared_pair(project(), b'<SaveProperties>'+soma+soma+b'</SaveProperties>')
        self.assertEqual([b["parameter_block_ordinal"] for b in record["parameter_blocks"]], [0, 1])

    def test_boolean_nonfinite_and_nonpositive_override_are_rejected(self):
        for value in [True, float('nan'), float('inf'), 0, -1]:
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                subject.audit_declared_pair(project(), parameters(), explicit_frequency_hz=value)

    def test_file_digest_is_of_parsed_snapshot_not_later_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);path = root/'Parameters_00.xml';raw = parameters();path.write_bytes(raw)
            (root/'Project.ini').write_bytes(project());original = subject._frozen
            def captured_then_replaced(p, limit):
                value = original(p, limit)
                if p == path:
                    path.write_bytes(parameters(capacity="2"))
                return value
            with patch.object(subject, '_frozen', side_effect=captured_then_replaced):
                record = subject.audit_case(path)
            self.assertEqual(mode(record)["q"], 1)
            self.assertEqual(record["inputs"]["parameters"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertNotEqual(record["inputs"]["parameters"]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_parameter_and_project_symlinks_never_supply_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);actual = root/'actual';actual.write_bytes(parameters());path = root/'Parameters_00.xml'
            path.symlink_to(actual)
            with self.assertRaises(EvidenceError):
                subject.audit_case(path)
            path.unlink();path.write_bytes(parameters());actual.write_bytes(project());(root/'Project.ini').symlink_to(actual)
            with self.assertRaises(EvidenceError):
                subject.audit_case(path)

    def test_size_budget_is_enforced_before_config_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'Parameters_00.xml';path.write_bytes(parameters())
            with patch.object(subject, 'MAXIMUM_FILE_BYTES', 1), self.assertRaises(EvidenceError):
                subject.audit_case(path)

    def test_matrix_discovery_retains_bad_case_without_losing_good_case(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, c in [('good', '1'), ('bad', '0')]:
                p = root/'W01/inputs'/name/'Train';p.mkdir(parents=True)
                (p/'Parameters_00.xml').write_bytes(parameters(capacity=c));(p/'Project.ini').write_bytes(project())
            record = subject.audit_config_tree(root, discovery='matrix')
            self.assertEqual(record['summary']['discovered_cases'], 2)
            self.assertEqual(record['summary']['not_assessed_cases'], 1)
            self.assertEqual(record['diagnostic_coverage'], 'incomplete')

    def test_tracked_tree_is_relocatable_and_ignores_untracked_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'relocated snapshot';root.mkdir();config = root/'arbitrary/Train';config.mkdir(parents=True)
            (config/'Parameters_00.xml').write_bytes(parameters());(config/'Project.ini').write_bytes(project())
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                            'commit', '--quiet', '-m', 'declared metadata fixture'], check=True)
            untracked = root/'untracked/Train';untracked.mkdir(parents=True)
            (untracked/'Parameters_00.xml').write_bytes(parameters())
            record = subject.audit_config_tree(root, discovery='tracked-tree')
            self.assertEqual(record['summary']['discovered_cases'], 1)
            self.assertEqual(record['cases'][0]['parameter_path'], 'arbitrary/Train/Parameters_00.xml')
            self.assertTrue(record['provenance']['Git_revision_is_not_worktree_hash'])

    def test_cli_writes_strict_diagnostic_and_never_overwrites_existing_output(self):
        from Scripts.StructTrain.TimeLearner.__main__ import main
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);case = root/'W01/inputs/case/Train';case.mkdir(parents=True)
            (case/'Parameters_00.xml').write_bytes(parameters());(case/'Project.ini').write_bytes(project())
            output = root/'report.json'
            args = ['audit-time-scales', '--config-root', str(root), '--discovery', 'matrix', '--output', str(output)]
            self.assertEqual(main(args), 0)
            raw = output.read_bytes();record = json.loads(raw)
            self.assertIsNone(record['integrator_stability_verdict'])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(args), 2)
            self.assertEqual(output.read_bytes(), raw)

    def test_tracked_subtree_metacharacters_are_literal_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ['configs[old]', 'configso']:
                folder = root/name/'Train';folder.mkdir(parents=True)
                (folder/'Parameters_00.xml').write_bytes(parameters());(folder/'Project.ini').write_bytes(project())
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                            'commit', '--quiet', '-m', 'literal subtree metadata'], check=True)
            record = subject.audit_config_tree(root/'configs[old]', discovery='tracked-tree')
            self.assertEqual(record['summary']['discovered_cases'], 1)
            self.assertEqual(record['cases'][0]['parameter_path'], 'Train/Parameters_00.xml')

    def test_cli_empty_discovery_is_nonzero_and_explicitly_not_assessed(self):
        from Scripts.StructTrain.TimeLearner.__main__ import main
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()) as stream:
            status = main(['audit-time-scales', '--config-root', directory, '--discovery', 'matrix'])
            record = json.loads(stream.getvalue())
            self.assertEqual(status, 2)
            self.assertEqual(record['diagnostic_coverage'], 'empty')
            self.assertIn('no_parameter_files_discovered', record['issues'])


if __name__ == '__main__':
    unittest.main()
