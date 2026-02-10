#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check and fix mismatches between expected component classes
from Parameters_*.xml and actual classes in Model_*.xml.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import re

class ComponentClassFixer:
    """Fix mismatches between component classes in Parameters and Model XML."""

    def __init__(self, configs_dir: str = "Bin/Configs", reports_dir: str = "Reports"):
        self.configs_dir = Path(configs_dir)
        self.reports_dir = Path(reports_dir)
        self.validation_report = self.reports_dir / "ConfigValidation-Detailed-Report.md"
        self.fixes_applied = []

    def get_expected_classes(self, params_file: Path) -> dict:
        """Extract expected component classes from Parameters XML."""
        expected = {}

        try:
            content = params_file.read_text(encoding="utf-8", errors="ignore")

            # Mapping from component types to parameter names
            component_params = {
                'LTZone': 'LTZoneClassName',
                'PosGenerator': 'ExcGeneratorClassName',
                'NegGenerator': 'InhGeneratorClassName',
                'Soma': 'MembraneClassName',      # For all Soma*
                'Dendrite': 'MembraneClassName',  # For all Dendrite*
                'LTMembrane': 'LTMembraneClassName',  # LTMembrane component
                'Receptor': 'ReceptorClassName',      # Receptor component
            }

            for comp_type, param_name in component_params.items():
                pattern = rf'<{re.escape(param_name)}[^>]*>([^<]+)</{re.escape(param_name)}>'
                match = re.search(pattern, content)
                if match:
                    expected[comp_type] = match.group(1).strip()
        except Exception as e:
            print(f"  ⚠️  Error reading Parameters: {e}")

        return expected

    def fix_model_classes(
        self, model_file: Path, expected_classes: dict, missing_components: list
    ) -> bool:
        """Fix component classes in Model and add missing components."""
        modified = False

        try:
            # Load Model
            if model_file.exists():
                tree = ET.parse(model_file)
                root = tree.getroot()
            else:
                root = ET.Element("Save")
                tree = ET.ElementTree(root)

            model = root.find("Model")
            if model is None:
                model = ET.SubElement(root, "Model")

            components = model.find("Components")
            if components is None:
                components = ET.SubElement(model, "Components")

            # Check and fix existing components
            for comp in list(components):
                comp_name = comp.tag
                comp_class = comp.get("Class", "")

                # Determine expected class
                expected_class = None
                if comp_name == "LTZone" and "LTZone" in expected_classes:
                    expected_class = expected_classes["LTZone"]
                elif comp_name == "PosGenerator" and "PosGenerator" in expected_classes:
                    expected_class = expected_classes["PosGenerator"]
                elif comp_name == "NegGenerator" and "NegGenerator" in expected_classes:
                    expected_class = expected_classes["NegGenerator"]
                elif comp_name.startswith("Soma") and "Soma" in expected_classes:
                    expected_class = expected_classes["Soma"]
                elif comp_name.startswith("Dendrite") and "Dendrite" in expected_classes:
                    expected_class = expected_classes["Dendrite"]
                elif comp_name == "LTMembrane" and "LTMembrane" in expected_classes:
                    expected_class = expected_classes["LTMembrane"]
                elif comp_name == "Receptor" and "Receptor" in expected_classes:
                    expected_class = expected_classes["Receptor"]

                    if expected_class and comp_class != expected_class:
                        comp.set("Class", expected_class)
                        modified = True
                        print(
                            f"    ✅ Fixed class {comp_name}: {comp_class} -> {expected_class}"
                        )

            # Add missing components
            for comp_name in missing_components:
                if components.find(comp_name) is None:
                    expected_class = None
                    if comp_name == "LTZone" and "LTZone" in expected_classes:
                        expected_class = expected_classes["LTZone"]
                    elif comp_name == "PosGenerator" and "PosGenerator" in expected_classes:
                        expected_class = expected_classes["PosGenerator"]
                    elif comp_name == "NegGenerator" and "NegGenerator" in expected_classes:
                        expected_class = expected_classes["NegGenerator"]
                    elif comp_name.startswith("Soma") and "Soma" in expected_classes:
                        expected_class = expected_classes["Soma"]
                    elif comp_name.startswith("Dendrite") and "Dendrite" in expected_classes:
                        expected_class = expected_classes["Dendrite"]
                    elif comp_name == "LTMembrane" and "LTMembrane" in expected_classes:
                        expected_class = expected_classes["LTMembrane"]
                    elif comp_name == "Receptor" and "Receptor" in expected_classes:
                        expected_class = expected_classes["Receptor"]

                    if expected_class:
                        comp_elem = ET.Element(comp_name)
                        comp_elem.set("Class", expected_class)
                        components.append(comp_elem)
                        modified = True
                        print(
                            f"    ✅ Added component {comp_name} with class {expected_class}"
                        )

            if modified:
                ET.indent(tree, space="  ")
                model_file.parent.mkdir(parents=True, exist_ok=True)
                tree.write(model_file, encoding="utf-8", xml_declaration=True)
                print(f"  ✅ Updated: {model_file}")

            return modified

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def fix_config(self, config_path: str, missing_components: list) -> bool:
        """Fix a single configuration."""
        # Strip trailing "/project.ini" if present
        if config_path.endswith("/project.ini") or config_path.endswith("\\project.ini"):
            config_path = config_path.rsplit("/", 1)[0].rsplit("\\", 1)[0]

        config_dir = self.configs_dir / config_path

        # Locate files
        project_ini = config_dir / "project.ini"
        if not project_ini.exists():
            return False

        try:
            project_content = project_ini.read_text(encoding="utf-8", errors="ignore")

            # Find Parameters and Model file names
            params_match = re.search(
                r"<ParametersFileName>([^<]+)</ParametersFileName>", project_content
            )
            model_match = re.search(
                r"<ModelFileName>([^<]+)</ModelFileName>", project_content
            )

            if not params_match or not model_match:
                return False

            params_file = config_dir / params_match.group(1).strip()
            model_file = config_dir / model_match.group(1).strip()

            if not params_file.exists():
                return False

            print(f"\nProcessing: {config_path}")

            # Get expected classes
            expected_classes = self.get_expected_classes(params_file)
            if not expected_classes:
                print("  ⚠️  No class parameters found in Parameters")
                return False

            # Fix Model
            return self.fix_model_classes(model_file, expected_classes, missing_components)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def run(self):
        """Run fixes for all configurations that have problems in the report."""
        # Find configurations with problems from the report
        if not self.validation_report.exists():
            print("Validation report not found")
            return

        content = self.validation_report.read_text(encoding="utf-8")

        # Parse report to find configurations with missing components
        configs_with_missing = defaultdict(list)
        current_config = None
        current_section = None

        for line in content.split("\n"):
            if line.startswith("### "):
                current_config = line[4:].strip()
                current_section = None
                continue
            if line.startswith("#### "):
                current_section = line[5:].strip()
                continue

            if current_section == "Несуществующие компоненты":
                # Support both Russian and English bullet formats in the report
                match_ru = re.search(r"\*\*Компонент:\*\*\s+`([^`]+)`", line)
                match_en = re.search(r"\*\*Component:\*\*\s+`([^`]+)`", line)
                m = match_ru or match_en
                if m:
                    component = m.group(1)
                    configs_with_missing[current_config].append(component)

        print(
            f"Found configurations with component class problems: {len(configs_with_missing)}"
        )

        # Process all configurations (not only the first few)
        for config_path, missing_comps in configs_with_missing.items():
            if self.fix_config(config_path, missing_comps):
                self.fixes_applied.append(config_path)

        print(f"\nConfigurations fixed: {len(self.fixes_applied)}")

if __name__ == "__main__":
    fixer = ComponentClassFixer()
    fixer.run()
