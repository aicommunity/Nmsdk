"""Read actual signed-threshold models, stock-image contracts and native traces."""
import copy
import os
from pathlib import Path
import unittest

from .test_threshold_proposal_evidence import measurement
from ..learned_evidence import load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..threshold_candidate_evidence import audit_threshold_candidate
from ..threshold_proposal_evidence import audit_threshold_proposal


def signed(value):
    value.pop("sha256", None);value["sha256"] = sha(value)
    return value


class ThresholdContractEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("TIMELEARNER_THRESHOLD_CONTRACT_DIR")
        if not value:
            raise unittest.SkipTest("requires actual stock-image and signed-candidate controls")
        cls.root = Path(value)
        cls.signed = sorted(cls.root.glob("*_numeric_domain_*_candidate.json"))
        cls.legacy = sorted(cls.root.glob("*_legacy_v1_candidate.json"))
        bases = {path.name.removesuffix("_legacy_v1_candidate.json") for path in cls.legacy}
        expected = {base+"_numeric_domain_"+domain+"_candidate.json"
                    for base in bases for domain in ("zero", "negative")}
        negative_zero = {base+"_numeric_domain_negative_zero_candidate.json" for base in bases}
        actual = {path.name for path in cls.signed}
        # Historical snapshots have eight files. New snapshots must carry all
        # four persisted negative-zero controls; a partial extension is invalid.
        if len(cls.legacy) != 4 or len(bases) != 4 or actual not in (expected, expected | negative_zero):
            raise RuntimeError("requires complete Classic/Branch x legacy/dispersed signed-domain controls")

    def test_zero_and_negative_candidates_preserve_every_other_parameter(self):
        for path in self.signed:
            package = load(path)
            base = path.name.split("_numeric_domain_", 1)[0]
            result = audit_threshold_candidate(package, load_case(self.root/(base+"_learned_state.json")))
            self.assertEqual(package["candidate_record"]["algorithm"], "explicit-native-threshold-v2")
            self.assertEqual(result["threshold"], 0. if "_zero_" in path.name else -1.)
            self.assertFalse(result["calibrated"])
            if "_negative_zero_" in path.name:
                positive_zero = load(path.with_name(base+"_numeric_domain_zero_candidate.json"))
                self.assertEqual(package["model_revision"], positive_zero["model_revision"])

    def test_legacy_positive_only_records_still_match_native_archives(self):
        for path in self.legacy:
            package = load(path);base = path.name.removesuffix("_legacy_v1_candidate.json")
            result = audit_threshold_candidate(package, load_case(self.root/(base+"_learned_state.json")))
            self.assertEqual(package["candidate_record"]["algorithm"], "explicit-native-threshold-v1")
            self.assertTrue(result["threshold_derivation_verified"])

    def test_negative_candidate_cannot_be_relabelled_as_legacy_v1(self):
        path = next(path for path in self.signed if path.name.endswith("_numeric_domain_negative_candidate.json"))
        package = load(path);base = path.name.split("_numeric_domain_", 1)[0]
        record = package["candidate_record"];record["algorithm"] = "explicit-native-threshold-v1"
        package["neuron"]["metadata"]["calibration"]["candidate_record"] = copy.deepcopy(record)
        signed(package["neuron"]);signed(package)
        with self.assertRaisesRegex(EvidenceError, "invalid_threshold_candidate_value"):
            audit_threshold_candidate(package, load_case(self.root/(base+"_learned_state.json")))

    def test_signed_bounds_are_independently_derived_from_actual_frames(self):
        paths = sorted(self.root.glob("*_signed_bounds_threshold_proposal.json"))
        self.assertEqual(len(paths), 2)
        for path in paths:
            base = path.name.removesuffix("_signed_bounds_threshold_proposal.json")
            high = load(self.root/(base+"_candidate_high_recognition_candidate.json"))
            m = measurement(self.root, base, "candidate_high", high)
            result = audit_threshold_proposal(load(path), m["evaluation_spec"], m["observations"], high,
                load_case(self.root/(base+"_learned_state.json")), minimum_threshold=-.1, maximum_threshold=1.)
            self.assertTrue(result["proposal_math_verified"])
            self.assertEqual(load(path)["algorithm"], "nonspiking-native-ltz-bracket-v2")

    def test_registered_images_keep_their_actual_signed_defaults_and_roles(self):
        contract = load(self.root/"native_threshold_storage_contract.json")
        images = {row["image"]: row for row in contract["images"]}
        self.assertEqual(len(images), 10)
        for image in ("NPulseLTZoneIaF", "NPulseLTZoneCable"):
            self.assertEqual(images[image]["threshold"], -.055)
            self.assertIs(images[image]["scalar_spike_threshold_supported"], True)
        self.assertIs(images["NPulseLTZoneIzhikevich"]["scalar_spike_threshold_supported"], True)
        for image in ("NPSimpleLTZone", "NCLTZone", "NCSimpleLTZone"):
            self.assertIs(images[image]["scalar_spike_threshold_supported"], False)
        self.assertIs(contract["calibrated"], False)

    def test_real_native_scheduler_observes_negative_voltage_crossing(self):
        trace = load(self.root/"native_signed_threshold_control.json")
        self.assertEqual(trace["image"], "NPulseLTZoneIaF")
        self.assertEqual(trace["threshold"], -.055)
        self.assertEqual([f["input"] for f in trace["frames"]], [-.07, -.05, -.071])
        self.assertEqual([f["decision_potential"] for f in trace["frames"]], [-.07, -.05, -.071])
        self.assertEqual([f["spike_count"] for f in trace["frames"]], [0, 1, 1])
        self.assertEqual(trace["frames"][0]["lt_output"], 0.)
        self.assertGreater(trace["frames"][1]["lt_output"], 0.)
        self.assertEqual(trace["frames"][2]["lt_output"], 0.)
        self.assertIs(trace["calibrated"], False)
