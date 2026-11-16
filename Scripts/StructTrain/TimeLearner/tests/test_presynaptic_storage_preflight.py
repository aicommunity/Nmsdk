"""Real native stock/PSI image readback with rehashed negative controls."""
from copy import deepcopy
import os
from pathlib import Path
import struct
import unittest
from unittest.mock import patch

from ..model_identity import canonical_model_sha256
from ..contained_process import inspect
from ..native_evidence import load
from ..native_process_policy import policy_for_reservation
from ..presynaptic_storage_study import compare_stock_and_psi, preflight
from ..resource_reservations import Reservations


class PresynapticStoragePreflightTest(unittest.TestCase):
    def test_actual_images_change_only_declared_PSI_fields(self):
        controls = Path(os.environ["TIMELEARNER_PSI_STORAGE_CONTROLS"]).resolve(strict=True)
        root = Path(os.environ["TMPDIR"])/"presynaptic-storage-preflight"
        root.mkdir(exist_ok=False)
        output = root/"native"
        controller = load(controls/"declaration.json")["controller"]
        owner = inspect(controller)
        self.assertEqual(owner["execution"], "running")
        self.assertEqual(owner["binding"]["initial_main_pid"], os.getpid())
        memory, tasks = 2*1024**3, 64
        registry = Reservations(root/"leases.sqlite3", managed_units=True,
            capacity=dict(slots=1, memory_bytes=owner["memory_max"]+2*memory,
                          disk_bytes=4*1024**3, tasks=owner["tasks_max"]+2*tasks))
        lease = registry.reserve("native-presynaptic-storage-preflight",
            [dict(path=str(output), access="write")], ttl_seconds=1800,
            demands=dict(slots=1, memory_bytes=owner["memory_max"]+memory,
                         disk_bytes=2*1024**3, tasks=owner["tasks_max"]+tasks),
            controller_directory=controller)
        try:
            policy = policy_for_reservation(registry, lease["token"], memory_bytes=memory, tasks=tasks)
            with patch.dict(os.environ, load(controls/"runtime.json")["loader_environment"]):
                result = preflight(controls/"prepared", controls/"runtime.json", output,
                                   process_policy=policy)
        finally:
            registry.release(lease["token"], note="Both exact native preflight groups closed; no Train claim.")
        self.assertTrue(result["factor"]["all_other_effective_model_fields_equal"])
        self.assertEqual(len(result["factor"]["synapse_paths"]), 4)
        self.assertFalse(result["factor"]["native_model_calculation"])
        stock = load(output/"stock/native/initial-state.json")["identity"]
        psi = load(output/"psi/native/initial-state.json")["identity"]
        for field, value in (("Capacity", 2e-9), ("InhibitionCoeff", 1.)):
            bad = deepcopy(psi)
            suffix = ".ExcChannel" if field == "Capacity" else ".ExcSynapse1"
            node = next(n for n in bad["model"]["nodes"] if n["path"] == "$.Soma1"+suffix)
            node["parameters"][field]["data"]["value"] = struct.pack(">d", value).hex()
            bad["sha256"] = canonical_model_sha256(bad["model"])
            with self.assertRaisesRegex(ValueError, "psi_study_undeclared_effective_difference"):
                compare_stock_and_psi(stock, bad)
        bad = deepcopy(psi)
        bad["model"]["bindings"].pop()
        bad["sha256"] = canonical_model_sha256(bad["model"])
        with self.assertRaisesRegex(ValueError, "psi_study_undeclared_effective_difference"):
            compare_stock_and_psi(stock, bad)
