"""Corrupt real native previews; never substitute a synthetic physical graph."""
import copy
import os
import struct
import unittest
from pathlib import Path

from Scripts.StructTrain.TimeLearner.domain_evidence import audit_resistance_domain
from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError, load


class DomainEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_DOMAIN_EVIDENCE_DIR")
        if not directory:
            raise unittest.SkipTest("requires native physical-preview artifacts")
        d = Path(directory)
        cls.records = []
        for pattern in ("*_domain_preview.json", "*_fixed_domain.json", "*_scaled_domain.json"):
            cls.records.extend(load(path) for path in sorted(d.glob(pattern)))
        if len(cls.records) < 6:
            raise RuntimeError("requires actual Classic/Branch previews and fixed/scaled inhibition")
        for path in sorted(d.glob("*_summary.json")):
            cls.records.extend(load(path).get("resistance_domains", []))
        cls.sample = next(record for record in cls.records if record["status"] == "available" and record["channels"])

    def reject(self, edit, *, resign=False):
        record = copy.deepcopy(self.sample)
        edit(record)
        if resign:
            record["preview_model_revision"] = canonical_model_sha256(record["preview_model"])
        with self.assertRaises(EvidenceError):
            audit_resistance_domain(record)

    def test_actual_native_physics(self):
        for record in self.records:
            with self.subTest(revision=record["preview_model_revision"]):
                result = audit_resistance_domain(record)
                self.assertEqual(result["physics_verified"], record["status"] == "available")
                self.assertIsNone(result["evaluation_verdict"])

    def test_changed_coefficient(self):
        self.reject(lambda r: r["channels"][0].__setitem__("variable_coefficient", r["channels"][0]["variable_coefficient"] * 2))

    def test_changed_small_fixed_conductance(self):
        self.reject(lambda r: r["channels"][0].__setitem__("fixed_conductance", 1e-20))

    def test_changed_child_physics_with_consistent_digest(self):
        def edit(r):
            path = "$." + r["channels"][0]["path"]
            node = next(n for n in r["preview_model"]["nodes"] if n["path"] == path)
            data = node["parameters"]["Capacity"]["data"]
            value = struct.unpack(">d", bytes.fromhex(data["value"]))[0]
            data["value"] = struct.pack(">d", value * 2).hex()
        self.reject(edit, resign=True)

    def test_changed_connection_with_consistent_digest(self):
        def edit(r):
            target = "$." + r["channels"][0]["path"] + ":SynapticInputs"
            r["preview_model"]["bindings"] = [b for b in r["preview_model"]["bindings"] if b["target"] != target]
        self.reject(edit, resign=True)

    def test_missing_channel(self):
        self.reject(lambda r: r["channels"].pop())

    def test_missing_control(self):
        self.reject(lambda r: r["controls"].clear())

    def test_changed_lock(self):
        self.reject(lambda r: r.__setitem__("locked_by_shared_bank", not r["locked_by_shared_bank"]))

    def test_changed_endpoint(self):
        self.reject(lambda r: r.__setitem__("minimum_resistance", r["minimum_resistance"] * .5))

    def test_nonfinite(self):
        self.reject(lambda r: r["channels"][0].__setitem__("variable_coefficient", float("nan")))

    def test_unknown_schema(self):
        self.reject(lambda r: r.__setitem__("schema_version", 99))

    def test_changed_identity(self):
        self.reject(lambda r: r.__setitem__("preview_model_revision", "corrupt"))

    def test_connected_physics(self):
        def edit(r):
            path = "$." + r["channels"][0]["path"]
            node = next(n for n in r["preview_model"]["nodes"] if n["path"] == path)
            node["parameters"]["Capacity"]["binding"] = True
        self.reject(edit, resign=True)

    def test_unavailable_is_not_verified(self):
        record = copy.deepcopy(self.sample)
        record["status"] = "unavailable"
        self.assertFalse(audit_resistance_domain(record)["physics_verified"])

    def test_legacy_requires_explicit_adapter(self):
        record = copy.deepcopy(self.sample)
        record["schema_version"] = 1
        with self.assertRaises(EvidenceError):
            audit_resistance_domain(record)
        self.assertFalse(audit_resistance_domain(record, allow_legacy=True)["physics_verified"])
