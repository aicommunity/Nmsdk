#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for adding missing structural components to Model_*.xml.

It analyses Parameters_*.xml to determine neuron structure and adds
missing components (LTZone, Soma, Dendrite, Generators) to Model_*.xml.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re

# Add Scripts directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class StructureComponentFixer:
    """Fix missing structural components in configurations."""

    def __init__(self, configs_dir: str = "Bin/Configs", reports_dir: str = "Reports"):
        self.configs_dir = Path(configs_dir)
        self.reports_dir = Path(reports_dir)
        self.validation_report = self.reports_dir / "ConfigValidation-Detailed-Report.md"
        self.fixes_applied = []

    def find_configs_with_missing_components(self) -> List[str]:
        """Find configurations with missing structural components listed in the validation report."""
        if not self.validation_report.exists():
            print(f"Validation report not found: {self.validation_report}")
            return []

        content = self.validation_report.read_text(encoding='utf-8')
        problematic_configs = set()
        current_config = None

        # Structural components to search for
        structural_keywords = ['LTZone', 'Soma1', 'Soma2', 'Dendrite1_', 'PosGenerator', 'NegGenerator']

        for line in content.split('\n'):
            if line.startswith('### '):
                current_config = line[4:].strip()
            if any(keyword in line for keyword in structural_keywords):
                if current_config:
                    problematic_configs.add(current_config)

        return list(problematic_configs)

    def parse_parameters(self, params_path: Path) -> Dict:
        """Parse Parameters_*.xml and extract structural information."""
        params = {
            'StructureBuildMode': 0,
            'NumSomaMembraneParts': 1,
            'NumDendriteMembraneParts': 0,
            'NumDendriteMembranePartsVec': [],
            'LTZoneClassName': 'NPLTZone',
            'ExcGeneratorClassName': 'NPNeuronPosCGenerator',
            'InhGeneratorClassName': 'NPNeuronNegCGenerator',
            'MembraneClassName': 'NPMembrane',
        }

        try:
            tree = ET.parse(params_path)
            root = tree.getroot()

            # Recursive parameter search
            def find_param(elem, name):
                for child in elem.iter():
                    if name in child.tag or (child.text and name in str(child.text)):
                        if child.text:
                            return child.text.strip()
                        return child.get('value', '')
                return None

            # Extract parameters
            for param_name in params.keys():
                value = find_param(root, param_name)
                if value:
                    try:
                        if 'Vec' in param_name:
                            # Vector value — parse as list
                            params[param_name] = [int(x.strip()) for x in value.split(',') if x.strip()]
                        elif param_name.endswith('ClassName'):
                            params[param_name] = value
                        else:
                            params[param_name] = int(value)
                    except:
                        pass
        except Exception as e:
            print(f"  ⚠️  Error parsing Parameters: {e}")
            # Try to recover via regex
            try:
                content = params_path.read_text(encoding='utf-8', errors='ignore')
                for param_name in params.keys():
                    if 'Vec' in param_name:
                        match = re.search(rf'<{param_name}[^>]*>([^<]+)</{param_name}>', content)
                        if match:
                            try:
                                params[param_name] = [int(x.strip()) for x in match.group(1).split(',') if x.strip()]
                            except:
                                pass
                    else:
                        match = re.search(rf'<{param_name}[^>]*>([^<]+)</{param_name}>', content)
                        if match:
                            value = match.group(1).strip()
                            if param_name.endswith('ClassName'):
                                params[param_name] = value
                            else:
                                try:
                                    params[param_name] = int(value)
                                except:
                                    pass
            except:
                pass

        return params

    def get_existing_components(self, model_path: Path) -> Set[str]:
        """Return a set of existing component names from Model_*.xml."""
        components = set()

        if not model_path.exists():
            return components

        try:
            tree = ET.parse(model_path)
            root = tree.getroot()
            model = root.find("Model")
            if model is not None:
                comps_elem = model.find("Components")
                if comps_elem is not None:
                    for comp in comps_elem:
                        components.add(comp.tag)
        except:
            pass

        return components

    def create_component_xml(self, comp_name: str, comp_class: str, comp_type: str) -> ET.Element:
        """Create an XML element for a component."""
        comp_elem = ET.Element(comp_name)
        comp_elem.set("Class", comp_class)

        # Add coordinates depending on the component type
        if comp_type == "LTZone":
            comp_elem.set("X", "27.3")
            comp_elem.set("Y", "4.67")
        elif comp_type == "PosGenerator":
            comp_elem.set("X", "4")
            comp_elem.set("Y", "2")
        elif comp_type == "NegGenerator":
            comp_elem.set("X", "4")
            comp_elem.set("Y", "7.3")
        elif comp_type.startswith("Soma"):
            comp_elem.set("X", "10")
            comp_elem.set("Y", "5")
        elif comp_type.startswith("Dendrite"):
            comp_elem.set("X", "15")
            comp_elem.set("Y", "5")

        return comp_elem

    def add_missing_components(self, model_path: Path, params: Dict, existing: Set[str]) -> bool:
        """Add missing components to Model_*.xml."""
        if params['StructureBuildMode'] == 0:
            # Automatic structure building is disabled — skip
            return False

        modified = False

        try:
            # Load or create Model
            if model_path.exists():
                tree = ET.parse(model_path)
                root = tree.getroot()
            else:
                root = ET.Element("Save")
                tree = ET.ElementTree(root)

            # Find or create Model element
            model = root.find("Model")
            if model is None:
                model = ET.SubElement(root, "Model")

            # Find or create Components element
            components = model.find("Components")
            if components is None:
                components = ET.SubElement(model, "Components")

            # Add LTZone
            if "LTZone" not in existing:
                ltzone_elem = self.create_component_xml("LTZone", params['LTZoneClassName'], "LTZone")
                components.append(ltzone_elem)
                modified = True
                print("    ✅ Added LTZone")

            # Add generators
            if params.get('ExcGeneratorClassName') and "PosGenerator" not in existing:
                pos_gen_elem = self.create_component_xml("PosGenerator", params['ExcGeneratorClassName'], "PosGenerator")
                components.append(pos_gen_elem)
                modified = True
                print("    ✅ Added PosGenerator")

            if params.get('InhGeneratorClassName') and "NegGenerator" not in existing:
                neg_gen_elem = self.create_component_xml("NegGenerator", params['InhGeneratorClassName'], "NegGenerator")
                components.append(neg_gen_elem)
                modified = True
                print("    ✅ Added NegGenerator")

            # Add Soma components
            num_soma = params.get('NumSomaMembraneParts', 1)
            for i in range(1, num_soma + 1):
                soma_name = f"Soma{i}"
                if soma_name not in existing:
                    soma_elem = self.create_component_xml(soma_name, params['MembraneClassName'], f"Soma{i}")
                    components.append(soma_elem)
                    modified = True
                    print(f"    ✅ Added {soma_name}")

            # Add Dendrite components
            if params.get('NumDendriteMembranePartsVec'):
                # Mode 2 — individual length for each soma
                for soma_idx, dendrite_length in enumerate(params['NumDendriteMembranePartsVec'], 1):
                    for dendrite_idx in range(1, dendrite_length + 1):
                        dendrite_name = f"Dendrite{soma_idx}_{dendrite_idx}"
                        if dendrite_name not in existing:
                            dendrite_elem = self.create_component_xml(dendrite_name, params['MembraneClassName'], f"Dendrite{soma_idx}_{dendrite_idx}")
                            components.append(dendrite_elem)
                            modified = True
                            print(f"    ✅ Added {dendrite_name}")
            elif params.get('NumDendriteMembraneParts', 0) > 0:
                # Mode 1 — same length for all soma
                dendrite_length = params['NumDendriteMembraneParts']
                for soma_idx in range(1, num_soma + 1):
                    for dendrite_idx in range(1, dendrite_length + 1):
                        dendrite_name = f"Dendrite{soma_idx}_{dendrite_idx}"
                        if dendrite_name not in existing:
                            dendrite_elem = self.create_component_xml(dendrite_name, params['MembraneClassName'], f"Dendrite{soma_idx}_{dendrite_idx}")
                            components.append(dendrite_elem)
                            modified = True
                            print(f"    ✅ Added {dendrite_name}")

            if modified:
                # Format and save
                ET.indent(tree, space="  ")
                model_path.parent.mkdir(parents=True, exist_ok=True)
                tree.write(model_path, encoding='utf-8', xml_declaration=True)
                print(f"  ✅ Updated: {model_path}")

            return modified

        except Exception as e:
            print(f"  ❌ Error while adding components: {e}")
            return False

    def fix_config(self, config_rel_path: str) -> bool:
        """Fix a single configuration."""
        config_dir = self.configs_dir / config_rel_path
        project_ini = config_dir / "project.ini"

        if not project_ini.exists():
            print(f"  ⚠️  project.ini not found: {project_ini}")
            return False

        print(f"\nProcessing: {config_rel_path}")

        # Locate Parameters and Model files
        try:
            content = project_ini.read_text(encoding='utf-8', errors='ignore')
            params_match = re.search(r'<ParametersFileName>([^<]+)</ParametersFileName>', content)
            model_match = re.search(r'<ModelFileName>([^<]+)</ModelFileName>', content)

            if not params_match or not model_match:
                print(f"  ⚠️  ParametersFileName or ModelFileName not found")
                return False

            params_file = config_dir / params_match.group(1).strip()
            model_file = config_dir / model_match.group(1).strip()

            if not params_file.exists():
                print(f"  ⚠️  Parameters file not found: {params_file}")
                return False

            # Parse parameters
            params = self.parse_parameters(params_file)

            if params['StructureBuildMode'] == 0:
                print("  ℹ️  StructureBuildMode=0, automatic structure building is disabled")
                return False

            # Get existing components
            existing = self.get_existing_components(model_file)

            # Add missing components
            modified = self.add_missing_components(model_file, params, existing)

            if modified:
                self.fixes_applied.append(config_rel_path)

            return modified

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def run(self):
        """Run fixing for all problematic configurations."""
        print("Searching for configurations with missing structural components...")
        problematic_configs = self.find_configs_with_missing_components()

        if not problematic_configs:
            print("No problematic configurations found.")
            return

        print(f"Found problematic configurations: {len(problematic_configs)}")
        print("Processing all configurations...")

        for config_path in problematic_configs:
            if self.fix_config(config_path):
                self.fixes_applied.append(config_path)

        print(f"\n{'='*60}")
        print(f"Fixed configurations: {len(self.fixes_applied)}")

        if self.fixes_applied:
            print("\nFixed configurations list:")
            for config in self.fixes_applied:
                print(f"  - {config}")

if __name__ == "__main__":
    fixer = StructureComponentFixer()
    fixer.run()
