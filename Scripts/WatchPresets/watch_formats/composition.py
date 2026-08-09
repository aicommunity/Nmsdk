"""Neuron composition and role families for Watch preset inheritance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def default_composition() -> Dict[str, Any]:
    """Hand-authored map derived from NPulseLibrary UploadClass + BuildStructure."""
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

    parents = {
        "NPNeuron": [
            {"slot": "LTZone", "childClass": "NPLTZone"},
            {"slot": "Soma1", "childClass": "NPMembrane"},
        ],
        "NPulseNeuronIaF": [
            {"slot": "LTZone", "childClass": "NPulseLTZoneIaF"},
            {"slot": "Soma1", "childClass": "NPulseMembraneIaF"},
        ],
        "NPulseNeuronCable": [
            {"slot": "LTZone", "childClass": "NPulseLTZoneCable"},
            {"slot": "Soma1", "childClass": "NPulseMembraneCable"},
        ],
        "NPulseNeuronCableMulti": [
            {"slot": "LTZone", "childClass": "NPulseLTZoneCable"},
            {"slot": "Soma1", "childClass": "NPulseMembraneCableMulti"},
        ],
        "NSPNeuron": [
            {"slot": "LTZone", "childClass": "NPLTZone"},
            {"slot": "Soma1", "childClass": "NPMembrane"},
            {"slot": "Dendrite1_1", "childClass": "NPMembrane"},
        ],
        "NSPNeuronGen": [
            {"slot": "LTZone", "childClass": "NPulseLTZoneThreshold"},
            {"slot": "Soma1", "childClass": "NPMembraneBio"},
            {"slot": "Dendrite1_1", "childClass": "NPMembraneBio"},
        ],
        "NSPNeuronBio": [
            {"slot": "LTZone", "childClass": "NPulseLTZoneThresholdBio"},
            {"slot": "Soma1", "childClass": "NPMembraneBio"},
            {"slot": "Dendrite1_1", "childClass": "NPMembraneBio"},
        ],
        "NSPNeuronBio2": [
            {"slot": "LTZone", "childClass": "NPulseLTZoneThresholdBio2"},
            {"slot": "Soma1", "childClass": "NPMembraneBio2"},
            {"slot": "Dendrite1_1", "childClass": "NPMembraneBio2"},
        ],
        "NNewSPNeuron": [
            {"slot": "LTZone", "childClass": "NPLTZone"},
            {"slot": "Soma1", "childClass": "NPMembrane"},
        ],
    }

    # Expand Favorites-style always-present nested slots on neuron parents
    for pname, slots in list(parents.items()):
        soma = next((s for s in slots if s["slot"] == "Soma1"), None)
        if not soma:
            continue
        mclass = soma["childClass"]
        if mclass == "NPMembrane":
            nested = membrane_classic
        elif mclass == "NPMembraneBio":
            nested = membrane_bio
        elif mclass == "NPMembraneBio2":
            nested = membrane_bio2
        else:
            nested = [
                {"slot": "ExcChannel", "childClass": "NPExcChannel"},
                {"slot": "InhChannel", "childClass": "NPInhChannel"},
            ]
        for n in nested:
            parents[pname].append(
                {"slot": f"Soma1.{n['slot']}", "childClass": n["childClass"]}
            )

    return {
        "schemaVersion": 1,
        "parents": parents,
        "membraneChildren": {
            "NPMembrane": membrane_classic,
            "NPNeuronMembrane": membrane_classic,
            "NPMembraneBio": membrane_bio,
            "NPMembraneBio2": membrane_bio2,
        },
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
            "membrane": [
                "NPMembrane",
                "NPMembraneBio",
                "NPMembraneBio2",
                "NPNeuronMembrane",
                "NPulseMembraneIaF",
                "NPulseMembraneCable",
                "NPulseMembraneCableMulti",
            ],
            "generator": [
                "NPGenerator",
                "NPulseGeneratorTransit",
                "NPulseGeneratorMulti",
                "NCGenerator",
            ],
            "sp_neuron": [
                "NSPNeuron",
                "NSPNeuronGen",
                "NSPNeuronBio",
                "NSPNeuronBio2",
                "NNewSPNeuron",
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


def expand_presets_for_class(
    class_name: str,
    by_class: Dict[str, List[Dict[str, Any]]],
    composition: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Pure-Python mirror of runtime expand (for tests / promote checks)."""
    composition = composition or default_composition()
    out: List[Dict[str, Any]] = []
    seen_ids = set()

    def add(preset: Dict[str, Any], new_id: Optional[str] = None) -> None:
        p = dict(preset)
        if new_id:
            p = {**p, "id": new_id}
        pid = p.get("id", "")
        if pid in seen_ids:
            return
        seen_ids.add(pid)
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

    # membrane one-level when selecting membrane class
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
    for fname, members in composition.get("families", {}).items():
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
