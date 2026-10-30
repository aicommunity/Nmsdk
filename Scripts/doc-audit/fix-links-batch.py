#!/usr/bin/env python3
"""One-shot batch fixes for known broken documentation links."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_in_tree(base: Path, mapping: dict[str, str], glob: str = "**/*.md") -> int:
    count = 0
    for md in base.rglob(glob.replace("**/", "")) if "**" not in glob else base.rglob("*.md"):
        if not md.is_file():
            continue
        text = md.read_text(encoding="utf-8")
        new = text
        for old, new_val in mapping.items():
            new = new.replace(old, new_val)
        if new != text:
            md.write_text(new, encoding="utf-8")
            count += 1
    return count


def fix_file(path: Path, replacements: list[tuple[str, str]]) -> bool:
    text = path.read_text(encoding="utf-8")
    new = text
    for old, new_val in replacements:
        new = new.replace(old, new_val)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0

    # Root Docs
    n += fix_file(
        ROOT / "Docs/Glossary.md",
        [("(Libraries/Terminology-Glossary.md)", "(../Libraries/Terminology-Glossary.md)")],
    )
    n += fix_file(
        ROOT / "Docs/Libraries/Rdk-HardwareLib.md",
        [
            (
                "](../Libraries/Rdk-HardwareLib/Firmware/README.md)",
                "](../../Libraries/Rdk-HardwareLib/Firmware/README.md)",
            )
        ],
    )
    n += fix_file(
        ROOT / "Docs/Submodules/Rdk-Index.md",
        [
            ("[FAQ](FAQ.md)", "[FAQ](../../Rdk/Docs/FAQ.md)"),
            ("[Getting-Started.md](Getting-Started.md)", "[Getting-Started.md](../Getting-Started.md)"),
            ("[Examples/](Examples/)", "[Examples](../../Rdk/Docs/Examples/)"),
        ],
    )
    n += fix_file(
        ROOT / "Docs/Testing/ConfigValidation-Tests.md",
        [
            (
                "`Tests/Integration/ConfigValidation/README.md`",
                "`Tests/Integration/ConfigValidation/README.md`",
            ),
            (
                "](../Tests/Integration/ConfigValidation/README.md)",
                "](../../Tests/Integration/ConfigValidation/README.md)",
            ),
            (
                "](../Development-Guides/Config-Validation.md)",
                "](../Development-Guides/Config-Validation.md)",
            ),
        ],
    )

    # Navigation-Map placeholders -> plain text
    nav = ROOT / "Docs/Submodules/Navigation-Map.md"
    nav_text = nav.read_text(encoding="utf-8")
    nav_new = nav_text
    nav_new = nav_new.replace(
        "[Документация библиотеки](../../Libraries/<LibName>/Docs/README.md)",
        "документация библиотеки `Libraries/<LibName>/Docs/README.md`",
    )
    nav_new = nav_new.replace(
        "[Каталог компонентов](../../Libraries/<LibName>/Docs/Component-Catalog.md)",
        "каталог `Libraries/<LibName>/Docs/Component-Catalog.md`",
    )
    nav_new = nav_new.replace(
        "[Документация компонента](../../Libraries/<LibName>/Docs/Components/<Component>.md)",
        "страница `Libraries/<LibName>/Docs/Components/<Component>.md`",
    )
    nav_new = nav_new.replace(
        "[Library Documentation](../../Libraries/<LibName>/Docs/README.md)",
        "library docs at `Libraries/<LibName>/Docs/README.md`",
    )
    nav_new = nav_new.replace(
        "[Component Catalog](../../Libraries/<LibName>/Docs/Component-Catalog.md)",
        "catalog `Libraries/<LibName>/Docs/Component-Catalog.md`",
    )
    nav_new = nav_new.replace(
        "[Component Documentation](../../Libraries/<LibName>/Docs/Components/<Component>.md)",
        "component page `Libraries/<LibName>/Docs/Components/<Component>.md`",
    )
    if nav_new != nav_text:
        nav.write_text(nav_new, encoding="utf-8")
        n += 1

    # Tests INDEX Bin path
    n += fix_file(
        ROOT / "Tests/Integration/ConfigValidation/INDEX.md",
        [
            (
                "](../../../../Bin/Configs/TestValidation/README.md)",
                "](../../../Bin/Configs/TestValidation/SUMMARY.md)",
            )
        ],
    )

    # PulseLib cross-component renames
    pulse_map = {
        "](NConstGenerator.md)": "](NCGenerator.md)",
        "](NPulseLifeNeuron.md)": "](NPLifeNeuron.md)",
        "](NLTZone.md)": "](NPLTZone.md)",
        "](NContinuesLTZone.md)": "](NPLTZone.md)",
        "](NPNewSynNeuronMembrane.md)": "](NPNewNeuronMembrane.md)",
        "](NPulseChannelClassic.md)": "](NPulseChannel.md)",
        "](NPulseHebbLifeSynapse.md)": "](NPHebbLifeSynapse.md)",
        "](NPulseDelay.md)": "](NPDelay.md)",
        "](NSynapseTrainer.md)": "](NNeuronTrainer.md)",
        # Only Documentation-Status at Docs/ root (handled per-file below)
        "](../../Bin/Docs/Literature-References.md)": "](../../../Bin/Docs/Literature-References.md)",
        "[Getting-Started.md](Getting-Started.md)": "[README.md](README.md)",
    }
    n += replace_in_tree(ROOT / "Libraries/Nmsdk-PulseLib/Docs", pulse_map)

    # MotionControlLib
    n += fix_file(
        ROOT / "Libraries/Nmsdk-MotionControlLib/Docs/Literature-References.md",
        [
            (
                "](../../Bin/Docs/Literature-References.md)",
                "](../../../Bin/Docs/Literature-References.md)",
            )
        ],
    )

    # BasicLib / HardwareLib Documentation-Status
    for lib in ("Rdk-BasicLib", "Rdk-HardwareLib"):
        n += fix_file(
            ROOT / f"Libraries/{lib}/Docs/Documentation-Status.md",
            [("](../Component-Catalog.md)", "](Component-Catalog.md)")],
        )

    # HardwareLib ArduinoBoard Bin paths (4 levels to root)
    n += fix_file(
        ROOT / "Libraries/Rdk-HardwareLib/Docs/Components/ArduinoBoard.md",
        [
            (
                "](../../../Bin/Configs/SpikeSamples/Hardware/01-ArduinoBoard/README.md)",
                "](../../../../Bin/Configs/SpikeSamples/Hardware/01-ArduinoBoard/README.md)",
            ),
            (
                "](../../../Bin/Docs/SpikeSamples/Overview.md)",
                "](../../../../Bin/Docs/SpikeSamples/Overview.md)",
            ),
        ],
    )

    # Rdk submodule cross-links to root Docs
    rdk_fixes = [
        (ROOT / "Rdk/Docs/Architecture/Overview.md", [
            ("](../../Docs/Submodules/", "](../../../Docs/Submodules/"),
        ]),
        (ROOT / "Rdk/Docs/Architecture/Graphics-Architecture.md", [
            ("](../../Docs/GUI/", "](../../../Docs/GUI/"),
            ("](../../Rdk/Docs/Graphics-Detailed.md)", "](../Graphics-Detailed.md)"),
        ]),
        (ROOT / "Rdk/Docs/Architecture/System-Platform-Abstraction.md", [
            ("](../../Docs/Build-And-Deploy/", "](../../../Docs/Build-And-Deploy/"),
            ("](../Build-And-Deploy/", "](../../../Docs/Build-And-Deploy/"),
        ]),
        (ROOT / "Rdk/Docs/Diagrams/README.md", [
            ("](../../Architecture/Overview.md)", "](../Architecture/Overview.md)"),
        ]),
        (ROOT / "Rdk/Docs/Guides/Component-Development.md", [
            ("](../../Rdk/Docs/Diagrams/Property-System.md)", "](../Diagrams/Property-System.md)"),
            ("](../Performance-And-Testing/Testing-Strategy.md)", "](../../../Docs/Performance-And-Testing/Testing-Strategy.md)"),
            ("](../Components-And-Configuration/Component-System.md)", "](../../../Docs/Components-And-Configuration/Component-System.md)"),
            ("](../Rdk-Core/Engine-Architecture.md)", "](../../../Docs/Rdk-Core/Engine-Architecture.md)"),
        ]),
        (ROOT / "Rdk/Docs/Guides/Project-Management.md", [
            ("](../../Bin/Docs/Configs-Structure.md)", "](../../../Bin/Docs/Configs-Structure.md)"),
            ("](../Rdk-Core/Application-Architecture.md)", "](../../../Docs/Rdk-Core/Application-Architecture.md)"),
            ("](../Components-And-Configuration/Component-System.md)", "](../../../Docs/Components-And-Configuration/Component-System.md)"),
        ]),
    ]
    for path, reps in rdk_fixes:
        if fix_file(path, reps):
            n += 1

    # CvBasicLib gap: TBinarizationSimpleAdaptiveThreshold
    bg = ROOT / "Libraries/Rdk-CvBasicLib/Docs/Components/BackgroundBinarizationLabeling.md"
    bg_text = bg.read_text(encoding="utf-8")
    if "TBinarizationSimpleAdaptiveThreshold" not in bg_text:
        insert = (
            "\nКонфигурационный алиас `TBinarizationSimpleAdaptiveThreshold` соответствует "
            "`UBABinarizationSimpleAdaptiveThreshold` (адаптивный порог).\n"
        )
        marker = "`UBABinarizationSimpleAdaptiveThreshold` добавляет адаптивный порог"
        if marker in bg_text:
            bg.write_text(bg_text.replace(marker, insert.strip() + "\n\n" + marker), encoding="utf-8")
            n += 1

    cat = ROOT / "Libraries/Rdk-CvBasicLib/Docs/Component-Catalog.md"
    cat_text = cat.read_text(encoding="utf-8")
    if "`TBinarizationSimpleAdaptiveThreshold`" not in cat_text:
        cat.write_text(
            cat_text.replace(
                "`TBinarizationSimple`",
                "`TBinarizationSimple`, `TBinarizationSimpleAdaptiveThreshold`",
                1,
            ),
            encoding="utf-8",
        )
        n += 1

    print(f"Updated {n} files")


if __name__ == "__main__":
    main()
