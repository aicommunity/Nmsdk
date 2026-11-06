"""Declaration-only recovery checks; no synthetic waveform or certificate proof."""
from copy import deepcopy
import unittest

from ..candidate_recovery import (
    RECOVERY_MODE, RETRY_MODE, bind_recovery_policy,
    project_recovery_configuration, project_recovery_summary,
)
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, audit_training_summary, validate_configured_repeat_policy


def records(base=1):
    # These are deliberately partial declarations for the envelope/repeat
    # validators, not complete configurations accepted by the native codec.
    search = {"maximum_invalid_observations": 3}
    measured = {**search, "normalization": "synapse_count"}
    if base >= 2:
        search["n0_candidate_repeats"] = 2
        measured["n0_candidate_repeats"] = 2
    configuration = {"kind": "timelearner_native_cold_configuration", "schema_version": base,
                     "search": search, "model": {"normalization": "N0"}}
    summary = {"kind": "native_training_state_summary", "schema_version": base,
               "configuration": measured}
    return configuration, summary


def envelope(value):
    result = deepcopy(value)
    result.update(schema_version=5, base_schema_version=value["schema_version"],
                  invalid_measurement_recovery=RECOVERY_MODE)
    return result


class CandidateRecoveryDeclarationTest(unittest.TestCase):
    def test_each_base_projects_without_mutation_or_loss(self):
        for base in range(1, 5):
            for value, project in zip(records(base), (project_recovery_configuration, project_recovery_summary)):
                with self.subTest(base=base, kind=value["kind"]):
                    value["future_unknown_base_field"] = {"nested": [1, 2]}
                    original = deepcopy(value)
                    encoded = envelope(value)
                    before = deepcopy(encoded)
                    projected, mode = project(encoded)
                    self.assertEqual(mode, RECOVERY_MODE)
                    self.assertEqual(projected, original)
                    self.assertEqual(encoded, before)
                    self.assertNotEqual(canonical_model_sha256(encoded), canonical_model_sha256(projected))
                    projected["future_unknown_base_field"]["nested"].append(3)
                    self.assertEqual(encoded, before)

    def test_legacy_policy_is_explicitly_retry_and_copied(self):
        for base in range(1, 5):
            for value, project in zip(records(base), (project_recovery_configuration, project_recovery_summary)):
                projected, mode = project(value)
                self.assertEqual(mode, RETRY_MODE)
                self.assertEqual(projected, value)
                self.assertIsNot(projected, value)

    def test_unversioned_envelope_fields_are_rejected(self):
        for base in range(1, 5):
            for value, project in zip(records(base), (project_recovery_configuration, project_recovery_summary)):
                for key, field in (("base_schema_version", base), ("invalid_measurement_recovery", RECOVERY_MODE)):
                    changed = deepcopy(value);changed[key] = field
                    with self.assertRaisesRegex(EvidenceError, "unversioned_candidate_recovery"):
                        project(changed)

    def test_unknown_nested_missing_or_boolean_versions_are_rejected(self):
        for value, project in zip(records(), (project_recovery_configuration, project_recovery_summary)):
            for version in (None, True, 1.0, 0, 6, "5"):
                changed = envelope(value);changed["schema_version"] = version
                with self.subTest(version=version), self.assertRaises(EvidenceError):
                    project(changed)
            for base in (None, True, 1.0, 0, 5, "1"):
                changed = envelope(value);changed["base_schema_version"] = base
                with self.subTest(base=base), self.assertRaises(EvidenceError):
                    project(changed)
            for key in ("base_schema_version", "invalid_measurement_recovery"):
                changed = envelope(value);changed.pop(key)
                with self.assertRaises(EvidenceError):project(changed)

    def test_unknown_modes_and_invalid_allowances_are_rejected(self):
        for value, project, field in zip(records(),
                (project_recovery_configuration, project_recovery_summary), ("search", "configuration")):
            for mode in (None, True, RETRY_MODE, "advance", ""):
                changed = envelope(value);changed["invalid_measurement_recovery"] = mode
                with self.assertRaises(EvidenceError):project(changed)
            for allowance in (None, True, 0, -1, 1.5, float("nan"), float("inf"), 2**53, "3"):
                changed = envelope(value);changed[field]["maximum_invalid_observations"] = allowance
                with self.subTest(allowance=allowance), self.assertRaises(EvidenceError):project(changed)
            changed = envelope(value);changed[field].pop("maximum_invalid_observations")
            with self.assertRaises(EvidenceError):project(changed)

    def test_binding_rejects_one_sided_policy_base_or_allowance_change(self):
        config, summary = records()
        for declared, measured in ((envelope(config), summary), (config, envelope(summary)),
                                   (envelope(config), envelope(records(2)[1]))):
            with self.assertRaisesRegex(EvidenceError, "configuration_summary_recovery_schema_mismatch"):
                bind_recovery_policy(declared, measured)
        declared, measured = envelope(config), envelope(summary)
        measured["configuration"]["maximum_invalid_observations"] += 1
        with self.assertRaisesRegex(EvidenceError, "configuration_summary_recovery_allowance_mismatch"):
            bind_recovery_policy(declared, measured)

    def test_existing_repeat_validator_uses_bound_base_without_changing_source(self):
        for base in (1, 2):
            for wrapped in (False, True):
                values = records(base)
                if wrapped:values = tuple(map(envelope, values))
                before = deepcopy(values)
                self.assertEqual(validate_configured_repeat_policy(*values), base)
                self.assertEqual(values, before)
        config, summary = map(envelope, records(2))
        summary["configuration"]["n0_candidate_repeats"] = 3
        with self.assertRaisesRegex(EvidenceError, "configuration_summary_repeat_policy_mismatch"):
            validate_configured_repeat_policy(config, summary)

    def test_envelope_acceptance_cannot_certify_training(self):
        for base in range(1, 5):
            summary = envelope(records(base)[1])
            with self.assertRaisesRegex(EvidenceError, "candidate_recovery_primary_audit_not_implemented"):
                audit_training_summary(summary, {}, "pulse0")


if __name__ == "__main__":
    unittest.main()
