"""Production public preflight with actual Console and schema3 ownership."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import unittest

from ..__main__ import main
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest
from ..native_process_policy import policy_for_reservation
from ..resource_reservations import Reservations
from ..native_calibration_worker import _artifact_files, _record, _signed


class ManagedNativePreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        descriptor = os.environ.get("TIMELEARNER_MANAGED_NATIVE_PREFLIGHT")
        if not descriptor:
            raise unittest.SkipTest("requires immutable Console runtime and two declared cold jobs")
        cls.spec = load(Path(descriptor))
        if set(cls.spec) != {"runtime", "jobs", "controller", "output"} or set(cls.spec["jobs"]) != {"Classic-N0", "Branch-N1"}:
            raise RuntimeError("incomplete managed native preflight declaration")
        cls.root = Path(cls.spec["output"])
        cls.root.mkdir(parents=True, exist_ok=False)

    def case(self, name):
        root = self.root/name
        root.mkdir()
        output = root/"run"
        capacity = {"slots": 1, "memory_bytes": 6*1024**3, "disk_bytes": 512*1024**2, "tasks": 512}
        demands = {"slots": 1, "memory_bytes": 4*1024**3+256*1024**2, "disk_bytes": 256*1024**2, "tasks": 256}
        registry = Reservations(root/"leases.sqlite3", capacity=capacity, managed_units=True)
        lease = registry.reserve("native-preflight-"+name, [{"path": str(output), "access": "write"}],
            demands=demands, controller_directory=self.spec["controller"], ttl_seconds=300)
        policy = policy_for_reservation(registry, lease["token"], memory_bytes=4*1024**3, tasks=64)
        policy_path = root/"policy.json"
        policy_path.write_text(json.dumps(policy))
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["preflight", self.spec["jobs"][name], "--runtime-manifest", self.spec["runtime"],
                         "--wall-seconds", "120", "--process-policy", str(policy_path), "--output", str(output)])
        (root/"cli-stdout.log").write_text(stdout.getvalue())
        self.assertEqual(code, 0, stdout.getvalue())
        result = load(output/"run-manifest.json")
        self.assertEqual(result["schema_version"], 4)
        self.assertEqual(result["execution"], "completed")
        self.assertEqual(result["validity"], "valid")
        native = load(output/"native/execution.json")
        self.assertEqual(native["model_ticks"], 0)
        self.assertFalse(native["training_started"])
        self.assertTrue(audit_run_manifest(output/"run-manifest.json")["run_evidence_consistent"])
        context = load(output/"process/reservation-context.json")
        self.assertEqual(context["lease"]["token"], lease["token"])
        self.assertEqual(context["intent"]["state"], "bound")
        self.assertEqual(context["intent"]["intent"]["unit"], load(output/"process/contained/owned-unit.json")["unit"])
        self.assertEqual(registry.inspect()["leases"][0]["state"], "held")
        registry.release(lease["token"], note="Native preflight returned with full managed-unit closure.")
        self.assertEqual(registry.inspect()["leases"][0]["state"], "released")
        clone = root/"rehashed-corruption"
        shutil.copytree(output, clone, symlinks=True)
        altered = load(clone/"process/reservation-context.json")
        altered["lease"]["token"] = "00000000-0000-4000-8000-000000000000"
        (clone/"process/reservation-context.json").write_text(json.dumps(altered))
        manifest = load(clone/"run-manifest.json")
        manifest["artifacts"] = [_record(p, clone) for p in _artifact_files(clone) if p != clone/"run-manifest.json"]
        manifest.pop("sha256")
        (clone/"run-manifest.json").write_text(json.dumps(_signed(manifest)))
        with self.assertRaisesRegex(EvidenceError, "native_resource_lease_changed"):
            audit_run_manifest(clone/"run-manifest.json")

    def test_classic_public_preflight_owns_actual_registered_unit(self):
        self.case("Classic-N0")

    def test_branch_public_preflight_owns_actual_registered_unit(self):
        self.case("Branch-N1")
