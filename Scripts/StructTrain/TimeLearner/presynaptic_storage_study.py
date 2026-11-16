"""Matched stock/PSI storage-image control, before any expensive cold Train.

Use the existing native image chain. No live parameter overlays, new physics,
threshold tuning or training certificate is introduced by this preflight.
"""
from copy import deepcopy
import argparse
from pathlib import Path
import re
import struct

from .model_identity import canonical_model_sha256
from .contained_process import inspect
from .native_calibration_worker import _write
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest, run_job, validate_job
from .native_process_policy import validate_policy
from .n1_protocol_robustness import _signed
from .process_runner import verify_runtime
from .runtime import file_record
from .stock_phasea_preflight import audit_stock_profile


CLASSES = {"stock": "NSPNeuronGen", "psi": "NSPNeuronGenPreinh2_5"}


def _declaration(original, run_label):
    return dict(kind="timelearner_matched_presynaptic_storage_control", schema_version=1,
        run_label=run_label, original_job_sha256=original["sha256"],
        cases={role: role+".json" for role in CLASSES},
        factor="native stock image versus native PSI k=2.5 image",
        all_other_job_fields_equal=True, scientific_verdict=None)


def make_cases(original, run_label):
    require(type(run_label) is str and
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", run_label),
            "psi_study_run_label")
    validate_job("train", original)
    c = original["configuration"]
    m = c["model"]
    require(c["schema_version"] == 8 and m["branch"] is True and
            m["normalization"] == "N1" and m["frequency_hz"] == 2000 and
            m["neuron_class"] == "TLNativeFast0F2000_Neuron" and
            m["initial_threshold"] == 100. and m["initial_isi"] == [.01, .08, .16, .24] and
            m["inputs"] == [dict(attachment=1, synapses=1, resistance=86e6)]*4 and
            m["inhibition"] == [] and
            c["search"]["tolerances"] == dict(amplitude_absolute=1e-5,
                                               amplitude_relative=0., sync=.02),
            "psi_study_requires_declared_stock_cold_N4_N1")
    result = {}
    for role, image in CLASSES.items():
        job = deepcopy(original)
        job["configuration"]["run_id"] = "Branch-PSI-storage/"+run_label+"/"+role
        job["configuration"]["model"]["neuron_class"] = image
        # Both named images already belong to CreateClassSamples. The stock
        # image is measured again; alias equivalence to a prior run is not assumed.
        job["profile_archives"] = []
        job = _signed({k: v for k, v in job.items() if k != "sha256"})
        validate_job("preflight", job)
        validate_job("train", job)
        result[role] = job
    return result


def prepare(original_path, output, *, run_label):
    original_path, output = Path(original_path).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not original_path.is_relative_to(output),
            "psi_study_prepare_output_exists_or_overlap")
    original = load(original_path)
    cases = make_cases(original, run_label)
    output.mkdir(parents=True)
    (output/"original.json").write_bytes(original_path.read_bytes())
    for role, job in cases.items():
        _write(output/(role+".json"), job)
    record = _declaration(original, run_label)
    _write(output/"declaration.json", record)
    return record


def _differences(left, right, prefix="model"):
    if type(left) is not type(right):
        return [prefix]
    if type(left) is dict:
        if set(left) != set(right):
            return [prefix+".keys"]
        return [p for k in sorted(left) for p in _differences(left[k], right[k], prefix+"."+k)]
    if type(left) is list:
        if len(left) != len(right):
            return [prefix+".length"]
        return [p for i, (a, b) in enumerate(zip(left, right))
                for p in _differences(a, b, prefix+"["+str(i)+"]")]
    return [] if left == right else [prefix]


def compare_stock_and_psi(stock, psi):
    for identity in (stock, psi):
        require(identity["valid"] is True and identity["diagnostics"] == [] and
                identity["sha256"] == canonical_model_sha256(identity["model"]),
                "psi_study_invalid_effective_identity")
    baseline = audit_stock_profile(stock, branch=True)
    require(baseline["initial_threshold"] == 100., "psi_study_threshold_changed")
    expected = deepcopy(stock["model"])
    images = {"NSPNeuronGen": CLASSES["psi"],
              "NPMembraneBio": "NPMembraneBioPreinh2_5",
              "NPSynapseBio": "NPSynapseBioPreinh2_5"}
    synapses = []
    for node in expected["nodes"]:
        source_class = node["class"]
        node["class"] = images.get(source_class, source_class)
        if source_class == "NSPNeuronGen":
            p = node["parameters"]["MembraneClassName"]
            require(p["data"] == dict(type="utf8", value="NPMembraneBio") and
                    node["parameters"]["UseElementDefaults"]["data"] ==
                    dict(type="boolean", value=False), "psi_study_root_not_storage_owned")
            p["data"]["value"] = images["NPMembraneBio"]
        elif source_class == "NPMembraneBio":
            p = node["parameters"]["SynapseClassName"]
            require(p["data"] == dict(type="utf8", value="NPSynapseBio"),
                    "psi_study_unexpected_body_synapse_image")
            p["data"]["value"] = images["NPSynapseBio"]
        elif source_class == "NPSynapseBio":
            node["parameters"]["UsePresynapticInhibition"]["data"]["value"] = True
            node["parameters"]["InhibitionCoeff"]["data"]["value"] = struct.pack(">d", 2.5).hex()
            synapses.append(node["path"])
    require(synapses and expected["nodes"][0]["path"] == "$", "psi_study_synapses_missing")
    differences = _differences(expected, psi["model"])
    require(not differences, "psi_study_undeclared_effective_difference:"+",".join(differences[:20]))
    return dict(kind="timelearner_native_presynaptic_storage_factor", schema_version=1,
        stock_model_revision=stock["sha256"], psi_model_revision=psi["sha256"],
        all_other_effective_model_fields_equal=True,
        changed_physics=["UsePresynapticInhibition=false->true", "InhibitionCoeff=0->2.5"],
        synapse_paths=synapses, channel_feedback_LT_physics_preserved=True, lt_membrane=False,
        native_model_calculation=False, training_started=False, scientific_verdict=None)


def preflight(prepared, runtime_path, output, *, process_policy):
    prepared, runtime_path = Path(prepared).resolve(strict=True), Path(runtime_path).resolve(strict=True)
    output = Path(output).resolve()
    require(not output.exists() and not prepared.is_relative_to(output) and
            not output.is_relative_to(prepared), "psi_study_preflight_output_exists_or_overlap")
    declaration = load(prepared/"declaration.json")
    original = load(prepared/"original.json")
    require(type(declaration.get("schema_version")) is int and
            type(declaration.get("all_other_job_fields_equal")) is bool and
            declaration == _declaration(original, declaration.get("run_label")),
            "psi_study_prepared_schema")
    cases = make_cases(original, declaration["run_label"])
    require(all(load(prepared/(role+".json")) == job for role, job in cases.items()),
            "psi_study_prepared_case_changed")
    runtime = load(runtime_path)
    verify_runtime(runtime)
    policy = validate_policy(process_policy, 180.)
    require(policy is not None and policy["schema_version"] == 2,
            "psi_study_owned_reservation_required")
    inputs = [prepared/name for name in ("declaration.json", "original.json", "stock.json", "psi.json")]
    inputs.append(runtime_path)
    before = [file_record(p) for p in inputs]
    output.mkdir(parents=True)
    identities, audits = {}, {}
    for role in CLASSES:
        folder = output/role
        result = run_job("preflight", prepared/(role+".json"), None, runtime_path, folder, 180.,
                         process_policy=policy)
        require(result["execution"] == "completed" and result["validity"] == "valid",
                "psi_study_native_preflight_rejected:"+role)
        require(inspect(folder/"process/contained")["all_processes_closed"],
                "psi_study_preflight_group_live:"+role)
        audits[role] = audit_run_manifest(folder/"run-manifest.json")
        initial = load(folder/"native/initial-state.json")
        require(initial["training_started"] is False, "psi_study_preflight_started_training")
        identities[role] = initial["identity"]
    factor = compare_stock_and_psi(identities["stock"], identities["psi"])
    require(before == [file_record(p) for p in inputs], "psi_study_input_changed")
    record = dict(kind="timelearner_matched_presynaptic_storage_preflight", schema_version=1,
        factor=factor, run_audits=audits, cold_train_not_performed=True,
        case_job_sha256={role: job["sha256"] for role, job in cases.items()},
        waveform_effect_not_yet_verified=True, scientific_verdict=None)
    _write(output/"index.json", record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("original", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--run-label", required=True)
    p = commands.add_parser("preflight")
    p.add_argument("prepared", type=Path)
    p.add_argument("runtime", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--process-policy", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.action == "prepare":
        prepare(args.original, args.output, run_label=args.run_label)
    else:
        preflight(args.prepared, args.runtime, args.output,
                  process_policy=load(args.process_policy))


if __name__ == "__main__":
    main()
