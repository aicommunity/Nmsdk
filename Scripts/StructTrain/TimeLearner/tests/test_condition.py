import copy
from dataclasses import replace
import hashlib
import json
import unittest
import uuid

from Scripts.StructTrain.TimeLearner.condition import (
    ARTIFACT_ROLES, CONDITION_ROLES, ConditionError, ConditionSpec, artifact,
    validate_artifact, parse, serialize, matrix_fingerprint, analysis_fingerprint, new_attempt_id,
)


def fixture():
    values = {role: artifact(role, {"fixture_role": role, "value": 1}) for role in CONDITION_ROLES}
    condition = ConditionSpec(controller_version=2, amplitude_goal="captured_per_input",
                              **{role: value["sha256"] for role, value in values.items()})
    return condition, {value["sha256"]: value for value in values.values()}


class ConditionIdentityTest(unittest.TestCase):
    def test_roundtrip_uses_all_content_references(self):
        condition, values = fixture()
        loaded = ConditionSpec.loads(json.dumps(json.loads(condition.dumps()), indent=3))
        self.assertEqual(loaded, condition)
        self.assertEqual(loaded.dumps(), condition.dumps())
        self.assertEqual(loaded.fingerprint, condition.fingerprint)
        resolved = loaded.resolve(values)
        self.assertEqual(set(resolved), set(CONDITION_ROLES))
        resolved["algorithm"]["value"] = 999
        self.assertEqual(loaded.resolve(values)["algorithm"]["value"], 1)

    def test_every_role_is_required(self):
        condition, values = fixture()
        for role in CONDITION_ROLES:
            with self.subTest(role=role):
                missing = copy.deepcopy(values)
                del missing[getattr(condition, role)]
                with self.assertRaises(ConditionError):
                    condition.resolve(missing)
                text = json.loads(condition.dumps())
                del text[role]
                with self.assertRaises(ConditionError):
                    ConditionSpec.loads(json.dumps(text))

    def test_unknown_schema_fields_bool_versions_and_goal_rejected(self):
        condition, _ = fixture()
        for field, value in (("schema_version", 2), ("controller_version", True),
                             ("schema_version", True), ("amplitude_goal", "shared_amplitude"),
                             ("executable_path", "/tmp/console")):
            text = json.loads(condition.dumps()); text[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ConditionError):
                ConditionSpec.loads(json.dumps(text))

    def test_duplicate_and_escaped_duplicate_keys_rejected(self):
        condition, _ = fixture()
        text = condition.dumps()[:-1] + ',"algorithm":"' + condition.algorithm + '"}'
        with self.assertRaisesRegex(ConditionError, "duplicate"):
            ConditionSpec.loads(text)
        with self.assertRaisesRegex(ConditionError, "duplicate"):
            parse(r'{"schema_version":1,"schema_\u0076ersion":1}')

    def test_corrupt_hash_payload_and_role_rejected(self):
        condition, values = fixture()
        values[condition.algorithm]["payload"]["value"] = 2
        with self.assertRaises(ConditionError):
            condition.resolve(values)
        record = artifact("model_spec", {"value": 1})
        with self.assertRaises(ConditionError):
            validate_artifact(record, "algorithm")
        with self.assertRaises(ConditionError):
            replace(condition, model_spec="0" * 63)

    def test_numeric_spelling_zero_and_key_order_have_one_identity(self):
        a = artifact("model_spec", {"z": -0.0, "a": 1.0, "v": [2.0, .125]})
        b = artifact("model_spec", {"v": [2, .125], "a": 1, "z": 0})
        self.assertEqual(serialize(a), serialize(b))
        self.assertEqual(a["sha256"], b["sha256"])
        self.assertNotEqual(artifact("model_spec", {"value": True})["sha256"],
                            artifact("model_spec", {"value": 1})["sha256"])

    def test_nonfinite_large_integer_invalid_strings_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), 2**53 + 1, b"raw"):
            with self.subTest(value=repr(value)), self.assertRaises(ConditionError):
                artifact("execution_policy", {"value": value})
        with self.assertRaises(ConditionError):
            parse('{"value":NaN}')
        with self.assertRaises(ConditionError):
            serialize({"value": chr(0xD800)})

    def test_execution_stall_limit_and_trial_order_change_condition(self):
        condition, _ = fixture()
        a = replace(condition, execution_policy=artifact("execution_policy", {"stall_autosave_n": 0})["sha256"])
        b = replace(condition, execution_policy=artifact("execution_policy", {"stall_autosave_n": 8})["sha256"])
        self.assertNotEqual(a.fingerprint, b.fingerprint)
        a = replace(condition, presentation_protocol=artifact("presentation_protocol", {"order": ["target", "foil"]})["sha256"])
        b = replace(condition, presentation_protocol=artifact("presentation_protocol", {"order": ["foil", "target"]})["sha256"])
        self.assertNotEqual(a.fingerprint, b.fingerprint)

    def test_other_case_changes_matrix_but_not_this_case(self):
        condition, _ = fixture()
        other = replace(condition, training_plan=artifact("training_plan", {"budget": 99})["sha256"])
        before = condition.fingerprint
        a = matrix_fingerprint([("a", condition), ("b", condition)])
        self.assertEqual(a, matrix_fingerprint([("b", condition), ("a", condition)]))
        self.assertNotEqual(a, matrix_fingerprint([("a", condition), ("b", other)]))
        self.assertEqual(condition.fingerprint, before)
        with self.assertRaises(ConditionError):
            matrix_fingerprint([("a", condition), ("a", other)])

    def test_scorer_changes_analysis_not_experiment_condition(self):
        condition, _ = fixture(); before = condition.fingerprint
        args = {key: hashlib.sha256(key.encode()).hexdigest()
                for key in ("model", "runtime", "observations", "scorer", "calibration_result")}
        original = analysis_fingerprint(condition, **args)
        args["scorer"] = "f" * 64
        self.assertNotEqual(original, analysis_fingerprint(condition, **args))
        self.assertEqual(condition.fingerprint, before)

    def test_attempt_ids_are_separate_from_condition(self):
        condition, _ = fixture(); before = condition.fingerprint
        ids = [new_attempt_id() for _ in range(8)]
        self.assertEqual(len(set(ids)), len(ids))
        self.assertTrue(all(uuid.UUID(value).version == 4 for value in ids))
        self.assertEqual(condition.fingerprint, before)

    def test_attempt_and_deployment_metadata_cannot_leak_into_condition_artifacts(self):
        for name in ("run_id", "RunId", "trial_id", "output_dir", "executable_path", "host"):
            with self.subTest(name=name), self.assertRaisesRegex(ConditionError, "provenance_field"):
                artifact("training_plan", {"nested": [{name: "attempt_or_path"}]})
        # Observation provenance belongs in a separate analysis artifact.
        value = artifact("observations", {"run_id": "attempt-a", "trial_id": "trial-1"})
        self.assertEqual(validate_artifact(value, "observations"), value)
