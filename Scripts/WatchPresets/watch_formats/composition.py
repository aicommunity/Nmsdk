"""Neuron composition and role families for Watch preset inheritance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def default_composition() -> Dict[str, Any]:
    """Hand-authored map derived from NPulseLibrary UploadClass + BuildStructure.

    Neuron parents only expose stable always-present slots (LTZone).
    Variable structure (SomaN, Dendrite*, synapses, channels) is NOT inherited
    onto the neuron root — select those instances directly when needed.
    """
    membrane_classic = [
        {"slot": "ExcChannel", "childClass": "NPExcChannel"},
        {"slot": "InhChannel", "childClass": "NPInhChannel"},
        {"slot": "ExcSynapse1", "childClass": "NPSynapse"},
        {"slot": "InhSynapse1", "childClass": "NPSynapse"},
    ]
    membrane_bio = [
        {"slot": "ExcChannel", "childClass": "NPExcChannelBio"},
        {"slot": "InhChannel", "childClass": "NPInhChannelBio"},
        {"slot": "ExcSynapse1", "childClass": "NPSynapseBio"},
        {"slot": "InhSynapse1", "childClass": "NPSynapseBio"},
    ]
    membrane_bio2 = [
        {"slot": "ExcChannel", "childClass": "NPExcChannelBio2"},
        {"slot": "InhChannel", "childClass": "NPInhChannelBio2"},
        {"slot": "ExcSynapse1", "childClass": "NPSynapseBio2"},
        {"slot": "InhSynapse1", "childClass": "NPSynapseBio2"},
    ]

    # Stable slot only: LTZone is always built for these neuron templates.
    parents = {
        "NPNeuron": [{"slot": "LTZone", "childClass": "NPLTZone"}],
        "NPulseNeuronIaF": [{"slot": "LTZone", "childClass": "NPulseLTZoneIaF"}],
        "NPulseNeuronCable": [{"slot": "LTZone", "childClass": "NPulseLTZoneCable"}],
        "NPulseNeuronCableMulti": [{"slot": "LTZone", "childClass": "NPulseLTZoneCable"}],
        "NSPNeuron": [{"slot": "LTZone", "childClass": "NPLTZone"}],
        "NSPNeuronGen": [{"slot": "LTZone", "childClass": "NPulseLTZoneThreshold"}],
        "NSPNeuronBio": [{"slot": "LTZone", "childClass": "NPulseLTZoneThresholdBio"}],
        "NSPNeuronBio2": [{"slot": "LTZone", "childClass": "NPulseLTZoneThresholdBio2"}],
        "NNewSPNeuron": [{"slot": "LTZone", "childClass": "NPLTZone"}],
    }

    return {
        "schemaVersion": 1,
        "parents": parents,
        # When the selected instance IS a membrane, channels/synapses on that
        # instance are still useful (one membrane → few children).
        "membraneChildren": {
            "NPMembrane": membrane_classic,
            "NPNeuronMembrane": membrane_classic,
            "NPMembraneBio": membrane_bio,
            "NPMembraneBio2": membrane_bio2,
        },
        # Families: leaf roles with interchangeable properties only.
        # Do NOT group whole neurons (identical SomaSumPotential spam).
        "families": {
            "ltzone": [
                "NPLTZone",
                "NPulseLTZoneIaF",
                "NPulseLTZoneCable",
                "NPulseLTZoneThreshold",
                "NPulseLTZoneThresholdBio",
                "NPulseLTZoneThresholdBio2",
                "NPSimpleLTZone",
                "NCLTZone",
                "NCSimpleLTZone",
            ],
            "synapse": [
                "NPSynapse",
                "NPSynapseBio",
                "NPSynapseBio2",
                "NPHebbSynapse",
            ],
            "exc_channel": [
                "NPExcChannel",
                "NPExcChannelBio",
                "NPExcChannelBio2",
                "NPChannel",
                "NPSynNeuronChannel",
            ],
            "inh_channel": [
                "NPInhChannel",
                "NPInhChannelBio",
                "NPInhChannelBio2",
            ],
            "generator": [
                "NPGenerator",
                "NPulseGeneratorTransit",
                "NPulseGeneratorMulti",
                "NCGenerator",
            ],
        },
    }


def write_composition_json(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(default_composition(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_composition(path: Path) -> Dict[str, Any]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return default_composition()


def series_signature(preset: Dict[str, Any]) -> str:
    keys = []
    for s in preset.get("series") or []:
        keys.append(
            f"{s.get('path') or ''}|{s.get('property') or ''}|"
            f"{s.get('jx', 0)}|{s.get('jy', 0)}"
        )
    return ";".join(sorted(keys))


def preset_has_wildcard(preset: Dict[str, Any]) -> bool:
    for s in preset.get("series") or []:
        if "*" in (s.get("path") or "") or "*" in (s.get("property") or ""):
            return True
        if "*" in (preset.get("title") or "") or "*" in (preset.get("id") or ""):
            return True
    return False


def is_variable_neuron_path(path: str) -> bool:
    """Paths that should not appear as neuron-root presets.

    Stable: empty (root props), LTZone, Soma1 (first soma is always built).
    Variable: Dendrite*, Soma2+, synapses, channels.
    """
    if not path:
        return False
    if "*" in path:
        return True
    if path == "LTZone" or path.startswith("LTZone."):
        return False
    if path == "Soma1" or path.startswith("Soma1."):
        # Soma1 itself OK for curated multi (spikes+soma); nested channel/synapse under Soma1 not
        rest = path[5:].lstrip(".")
        if not rest:
            return False
        if rest in ("ExcChannel", "InhChannel") or rest.startswith("ExcSynapse") or rest.startswith(
            "InhSynapse"
        ):
            return True
        return True  # any deeper under Soma1 treated as variable for neuron-root list
    p = path.split(".")[0]
    if p.startswith("Dendrite"):
        return True
    if p.startswith("Soma") and p[4:].isdigit():
        return True
    if "ExcSynapse" in path or "InhSynapse" in path:
        return True
    if path.endswith("ExcChannel") or path.endswith("InhChannel"):
        return True
    return False


def expand_presets_for_class(
    class_name: str,
    by_class: Dict[str, List[Dict[str, Any]]],
    composition: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Pure-Python mirror of runtime expand (for tests / promote checks)."""
    composition = composition or default_composition()
    out: List[Dict[str, Any]] = []
    seen_ids = set()
    seen_sigs = set()

    def add(preset: Dict[str, Any], new_id: Optional[str] = None) -> None:
        p = dict(preset)
        if new_id:
            p = {**p, "id": new_id}
        if preset_has_wildcard(p):
            return
        # Drop variable structure when listing for any class that uses parent map
        # (neuron roots); still allow empty-path root props.
        for s in p.get("series") or []:
            if is_variable_neuron_path(s.get("path") or ""):
                if class_name in composition.get("parents", {}):
                    return
        pid = p.get("id", "")
        if pid in seen_ids:
            return
        sig = series_signature(p)
        if not sig or sig in seen_sigs:
            return
        seen_ids.add(pid)
        seen_sigs.add(sig)
        out.append(p)

    for p in by_class.get(class_name, []):
        add(p)

    for slot_info in composition.get("parents", {}).get(class_name, []):
        slot = slot_info["slot"]
        child = slot_info["childClass"]
        for p in by_class.get(child, []):
            series = []
            for s in p.get("series", []):
                path = s.get("path") or ""
                new_path = slot if not path else f"{slot}.{path}"
                series.append({**s, "path": new_path})
            add(
                {**p, "series": series, "sourceClass": child, "viaSlot": slot},
                new_id=f"inherited:{slot}:{p.get('id', '')}",
            )

    for slot_info in composition.get("membraneChildren", {}).get(class_name, []):
        slot = slot_info["slot"]
        child = slot_info["childClass"]
        for p in by_class.get(child, []):
            series = []
            for s in p.get("series", []):
                path = s.get("path") or ""
                new_path = slot if not path else f"{slot}.{path}"
                series.append({**s, "path": new_path})
            add(
                {**p, "series": series, "sourceClass": child, "viaSlot": slot},
                new_id=f"inherited:{slot}:{p.get('id', '')}",
            )

    family_of = None
    for _fname, members in composition.get("families", {}).items():
        if class_name in members:
            family_of = members
            break
    if family_of:
        for sib in family_of:
            if sib == class_name:
                continue
            for p in by_class.get(sib, []):
                add(
                    {**p, "sourceClass": sib, "viaFamily": True},
                    new_id=f"family:{sib}:{p.get('id', '')}",
                )

    return out
