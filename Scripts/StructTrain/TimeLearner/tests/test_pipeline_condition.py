"""Condition binding against exact published coordinator declarations, no model oracle."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from ..condition import ConditionSpec
from ..managed_pipeline import _append, _created_payload, _scan, _write, audit_pipeline, signed
from ..native_evidence import EvidenceError, parse_json_bytes
from ..pipeline_condition import audit_binding, build_binding
from ..runtime import digest_json, runtime_content_identity


class PipelineConditionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = Path(__file__).parent/"fixtures/pipeline_condition"
        source = json.loads((folder/"source.json").read_text())
        cls.records = {}
        for row in source["members"]:
            compressed = (folder/row["path"]).read_bytes()
            if hashlib.sha256(compressed).hexdigest() != row["gzip_sha256"]:
                raise RuntimeError("fixture compressed primary changed")
            raw = gzip.decompress(compressed)
            if len(raw) != row["raw_bytes"] or hashlib.sha256(raw).hexdigest() != row["raw_sha256"]:
                raise RuntimeError("fixture original primary changed")
            cls.records[row["path"]] = parse_json_bytes(raw)
        if len(cls.records) != 5:
            raise RuntimeError("requires all four actual declarations and original runtime")

    def spec(self, name="Classic-v1"):
        spec = deepcopy(self.records[name+".json.gz"])
        spec["schema_version"] = 2
        return spec

    def runtime(self):
        return deepcopy(self.records["runtime.json.gz"])

    def binding(self, spec=None, runtime=None):
        return build_binding(self.spec() if spec is None else spec,
                             self.runtime() if runtime is None else runtime)

    def sign_train(self, spec):
        spec["phases"][0]["job"] = signed(spec["phases"][0]["job"])
        return spec

    def test_four_actual_declarations_resolve_all_condition_roles(self):
        for name in ("Classic-v1", "Classic-v2", "Branch-v1", "Branch-v2"):
            spec = self.spec(name);binding = self.binding(spec)
            condition = ConditionSpec.loads(json.dumps(binding["condition"]))
            self.assertEqual(condition.fingerprint, binding["condition_fingerprint"])
            self.assertEqual(len(condition.resolve(binding["artifacts"])), 11)
            self.assertEqual(audit_binding(binding, spec, self.runtime()), condition.fingerprint)

    def test_attempt_run_and_trial_renaming_preserves_scientific_identity(self):
        original = self.binding();spec = self.spec();spec["attempt_id"] = "another-attempt"
        def rename(value):
            if type(value) is dict:
                for key, child in value.items():
                    if key in ("run_id", "trial_id"): value[key] = "renamed-"+child
                    else: rename(child)
            elif type(value) is list:
                for child in value: rename(child)
        rename(spec);changed = self.binding(self.sign_train(spec))
        self.assertEqual(changed["condition_fingerprint"], original["condition_fingerprint"])
        self.assertNotEqual(changed["pipeline_specification_sha256"], original["pipeline_specification_sha256"])
        self.assertIn("/phases/0/job/configuration/run_id", changed["omitted_metadata_paths"])

    def test_coordinator_envelope_version_is_not_a_mathematical_factor(self):
        spec = self.spec();new = self.binding(spec);spec["schema_version"] = 1
        self.assertEqual(new["condition_fingerprint"], self.binding(spec)["condition_fingerprint"])

    def test_relocating_identical_runtime_preserves_condition(self):
        original = self.binding();runtime = self.runtime()
        for record in [runtime["executable"], runtime["app_ini"], runtime["compiler"], *runtime["resolved_libraries"]]:
            record["path"] = "/another/deployment/"+Path(record["path"]).name
        self.assertEqual(original["condition_fingerprint"], self.binding(runtime=runtime)["condition_fingerprint"])

    def test_actual_binary_content_is_part_of_algorithm_identity(self):
        original = self.binding();runtime = self.runtime();runtime["executable"]["sha256"] = "0"*64
        runtime["runtime_identity"] = runtime_content_identity(runtime)
        runtime["runtime_fingerprint"] = digest_json(runtime["runtime_identity"])
        self.assertNotEqual(original["condition_fingerprint"], self.binding(runtime=runtime)["condition_fingerprint"])

    def test_runtime_digest_cannot_mask_changed_content(self):
        runtime = self.runtime();runtime["executable"]["sha256"] = "0"*64
        with self.assertRaisesRegex(EvidenceError, "runtime_identity_changed"):
            self.binding(runtime=runtime)

    def test_physics_tolerance_and_probe_parameters_change_identity(self):
        baseline = self.binding()["condition_fingerprint"]
        def resistance(job): job["configuration"]["model"]["inputs"][0]["resistance"] *= 1.1
        def tolerance(job): job["configuration"]["search"]["tolerances"]["sync"] += .001
        def stimulus(job): job["configuration"]["stimulus_profile"]["amplitude"] *= 1.1
        for change in (resistance, tolerance, stimulus):
            with self.subTest(change=change.__name__):
                spec = self.spec();change(spec["phases"][0]["job"])
                self.assertNotEqual(baseline, self.binding(self.sign_train(spec))["condition_fingerprint"])

    def test_calibration_evaluation_order_and_phase_budget_change_identity(self):
        baseline = self.binding()["condition_fingerprint"]
        for mode in ("grid", "order", "budget"):
            spec = self.spec()
            if mode == "grid":
                phase = next(p for p in spec["phases"] if p["operation"] == "calibrate")
                phase["job"]["thresholds"] = [t*1.01 for t in phase["job"]["thresholds"]]
            elif mode == "order":
                trials = spec["phases"][-1]["job"]["trials"]
                # This real corpus is target/foil/foil/target. Reversal only
                # renames trial IDs; require an actual stimulus-order change.
                trials.reverse()
                self.assertEqual(baseline, self.binding(spec)["condition_fingerprint"])
                trials.append(trials.pop(0))
            else: spec["phases"][0]["wall_seconds"] -= 1
            self.assertNotEqual(baseline, self.binding(spec)["condition_fingerprint"], mode)

    def test_rehashed_arbitrary_condition_artifact_cannot_replace_declaration(self):
        spec = self.spec();runtime = self.runtime();binding = self.binding(spec, runtime)
        for key in ("condition_fingerprint", "pipeline_specification_sha256"):
            damaged = deepcopy(binding);damaged[key] = "0"*64
            with self.assertRaisesRegex(EvidenceError, "condition_binding_changed"):
                audit_binding(damaged, spec, runtime)
        damaged = deepcopy(binding);damaged["artifacts"].clear()
        with self.assertRaisesRegex(EvidenceError, "condition_binding_changed"):
            audit_binding(damaged, spec, runtime)

    def test_new_journal_requires_binding_and_rejects_missing_or_corrupt_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);spec = self.spec();runtime = self.runtime()
            _write(root/"runtime.json", runtime)
            with self.assertRaises(OSError): _created_payload(root, spec, runtime["runtime_fingerprint"])
            _write(root/"condition-binding.json", self.binding(spec, runtime))
            payload = _created_payload(root, spec, runtime["runtime_fingerprint"])
            self.assertEqual(payload["condition_fingerprint"], self.binding()["condition_fingerprint"])
            events = [];_append(root, events, "created", None, payload)
            self.assertEqual(_scan(root, spec, events, runtime["runtime_fingerprint"]), ([], None, None))
            binding = self.binding();binding["declaration_only"] = False
            (root/"condition-binding.json").write_text(json.dumps(binding))
            with self.assertRaisesRegex(EvidenceError, "condition_binding_changed"):
                _scan(root, spec, events, runtime["runtime_fingerprint"])

    def test_legacy_and_new_audits_never_invent_effective_model_attestation(self):
        for schema in (1, 2):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory);spec = self.spec();spec["schema_version"] = schema;runtime = self.runtime()
                _write(root/"specification.json", spec);_write(root/"runtime.json", runtime)
                if schema == 2: _write(root/"condition-binding.json", self.binding(spec, runtime))
                _append(root, [], "created", None, _created_payload(root, spec, runtime["runtime_fingerprint"]))
                audit = audit_pipeline(root)
                self.assertFalse(audit["condition_identity_attested"])
                self.assertIsNone(audit["scientific_verdict"])
                self.assertFalse(audit["pipeline_complete"])
                self.assertEqual("condition_fingerprint" in audit, schema == 2)

    def test_binding_is_declarative_and_does_not_attest_execution_or_random_replicates(self):
        binding = self.binding()
        self.assertTrue(binding["declaration_only"])
        self.assertFalse(binding["effective_model_verified"])
        self.assertFalse(binding["native_execution_verified"])
        self.assertIsNone(binding["scientific_verdict"])
        condition = ConditionSpec.loads(json.dumps(binding["condition"]))
        self.assertFalse(condition.resolve(binding["artifacts"])["randomness_spec"]["independent_seed_replicates_attested"])
