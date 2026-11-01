#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for automatic analysis and fixing of problems with missing components
in Nmsdk configuration files.

It analyses the validation report and suggests fixes for configurations
that contain errors.
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Add Scripts directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ConfigFixer:
    """Fix configurations with missing components based on the validation report."""

    def __init__(self, configs_dir: str = "Bin/Configs", reports_dir: str = "Reports"):
        self.configs_dir = Path(configs_dir)
        self.reports_dir = Path(reports_dir)
        self.validation_report = self.reports_dir / "ConfigValidation-Detailed-Report.md"

        # Mapping from problematic components to their types and parameters
        self.component_fixes = {
            'LTZone': {
                'type': 'LTZone',
                'param': 'LTZoneClassName',
                'default_class': 'NPLTZone',
                'build_mode': [1, 2]
            },
            'Receptor': {
                'type': 'Receptor',
                'param': 'ReceptorClassName',
                'default_class': 'NReceptor',
                'build_mode': [1, 2]
            },
            'Soma1': {
                'type': 'Soma',
                'param': 'NumSomaMembraneParts',
                'default_value': 1,
                'build_mode': [1, 2]
            },
            'Soma2': {
                'type': 'Soma',
                'param': 'NumSomaMembraneParts',
                'default_value': 2,
                'build_mode': [1, 2]
            },
            'Dendrite1_1': {
                'type': 'Dendrite',
                'param': 'NumDendriteMembraneParts',
                'default_value': 1,
                'build_mode': [1, 2]
            },
            'Dendrite1_2': {
                'type': 'Dendrite',
                'param': 'NumDendriteMembraneParts',
                'default_value': 2,
                'build_mode': [1, 2]
            },
            'NegGenerator': {
                'type': 'Generator',
                'param': 'InhGeneratorClassName',
                'default_class': 'NPNeuronNegCGenerator',
                'build_mode': [1, 2]
            },
            'PosGenerator': {
                'type': 'Generator',
                'param': 'ExcGeneratorClassName',
                'default_class': 'NPNeuronPosCGenerator',
                'build_mode': [1, 2]
            },
            'LTMembrane': {
                'type': 'LTMembrane',
                'param': 'LTMembraneClassName',
                'default_class': 'NPMembrane',
                'build_mode': [1, 2]
            }
        }

    def parse_validation_report(self) -> Dict[str, Dict]:
        """Parse the validation report and extract error information."""
        if not self.validation_report.exists():
            print(f"Validation report not found: {self.validation_report}")
            return {}

        configs_errors = {}
        current_config = None

        with open(self.validation_report, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i]

            # Find configuration header
            if line.startswith('### '):
                config_path = line[4:].strip()
                if config_path.endswith("/project.ini"):
                    current_config = config_path
                    configs_errors[current_config] = {
                        'missing_components': [],
                        'missing_classes': [],
                        'invalid_links': []
                    }

            # Find section with non-existent components
            if current_config and "Несуществующие компоненты" in line:
                i += 1
                while i < len(lines) and not lines[i].startswith("####"):
                    comp_line = lines[i]
                    # Support both Russian and English bullet formats
                    match_ru = re.search(r"Компонент.*`(\w+)`.*не существует", comp_line)
                    match_en = re.search(r"Component.*`(\w+)`.*does not exist", comp_line)
                    if match_ru:
                        component_name = match_ru.group(1)
                        configs_errors[current_config]["missing_components"].append(component_name)
                    elif match_en:
                        component_name = match_en.group(1)
                        configs_errors[current_config]["missing_components"].append(component_name)
                    i += 1
                continue

            # Find section with non-existent component classes
            if current_config and "Несуществующие классы компонентов" in line:
                i += 1
                while i < len(lines) and not lines[i].startswith("####"):
                    comp_line = lines[i]
                    # Support both Russian and English bullet formats
                    match_ru = re.search(r"Компонент.*`(\w+)`.*Класс.*`(\w+)`", comp_line)
                    match_en = re.search(
                        r"Component.*`(\w+)`.*Class.*`(\w+)`", comp_line
                    )
                    if match_ru or match_en:
                        m = match_ru or match_en
                        component_name = m.group(1)
                        class_name = m.group(2)
                        configs_errors[current_config]["missing_classes"].append(
                            {
                                "component": component_name,
                                "class": class_name,
                            }
                        )
                    i += 1
                continue

            i += 1

        return configs_errors

    def find_xml_files(self, config_path: str) -> Tuple[Optional[Path], Optional[Path]]:
        """Find Parameters and Model XML files for a configuration."""
        # Extract configuration directory path
        if config_path.endswith("/project.ini"):
            config_dir = Path(config_path[:-11])  # Strip '/project.ini'
        else:
            config_dir = Path(config_path)

        full_config_dir = self.configs_dir / config_dir

        parameters_file = None
        model_file = None

        # Look for Parameters_00.xml or Parameters.xml
        for pattern in ["Parameters_00.xml", "Parameters.xml", "parameters.xml"]:
            candidate = full_config_dir / pattern
            if candidate.exists():
                parameters_file = candidate
                break

        # Look for Model_00.xml or model.xml
        for pattern in ["Model_00.xml", "Model.xml", "model.xml"]:
            candidate = full_config_dir / pattern
            if candidate.exists():
                model_file = candidate
                break

        return parameters_file, model_file

    def fix_component_issues(self, config_path: str, errors: Dict) -> List[str]:
        """Fix component issues for a single configuration."""
        fixes_applied = []

        parameters_file, model_file = self.find_xml_files(config_path)

        if not parameters_file:
            return fixes_applied

        # Create backup before modifications
        backup_file = None
        try:
            backup_file = self._create_backup(parameters_file)
        except Exception as e:
            print(
                f"Warning: failed to create backup {parameters_file}: {e}"
            )
            return fixes_applied  # Do not continue without backup

        try:
            tree = ET.parse(parameters_file)
            root = tree.getroot()

            # In Nmsdk XML the tag is an instance name and the type is stored in the Class attribute.
            # Therefore we filter by component.get(\"Class\"), not by component.tag.
            allowed_component_classes = {
                'NPulseNeuron',
                'NAfferentNeuron',
                'NSimpleAfferentNeuron',
                'NSAfferentNeuron',
                'NSPNeuronGen',
                'PHebbNeuron',
                'PNeuron',
            }

            for component in root.iter():
                component_class = component.get('Class', '')
                if component_class in allowed_component_classes:
                    component_instance = component.tag

                    # Check StructureBuildMode
                    structure_build_mode = None
                    params_elem = component.find('Parameters')
                    if params_elem is not None:
                        mode_param = params_elem.find('StructureBuildMode')
                        if mode_param is not None and mode_param.text is not None:
                            try:
                                structure_build_mode = int(mode_param.text)
                            except Exception:
                                structure_build_mode = None

                    # If StructureBuildMode == 0 but there are missing components, set the correct mode
                    if structure_build_mode == 0:
                        # Determine which components are missing for this neuron type
                        missing_for_this = self._get_missing_for_component_type(
                            component_class, errors.get('missing_components', [])
                        )

                        if missing_for_this:
                            # Set StructureBuildMode = 2 (simple structure) or 1 (classic)
                            # Create Parameters element if it does not exist
                            if params_elem is None:
                                params_elem = ET.SubElement(component, 'Parameters')

                            if params_elem.find("StructureBuildMode") is None:
                                # Add StructureBuildMode
                                mode_elem = ET.SubElement(
                                    params_elem, "StructureBuildMode"
                                )
                                mode_elem.set("Type", "i")
                                mode_elem.set("PType", "257")
                                mode_elem.set("IoType", "17")
                                mode_elem.text = "2"  # Simple structure

                                fixes_applied.append(
                                    "StructureBuildMode=2 set for "
                                    f"{component_instance} (Class={component_class}, "
                                    f"was 0, missing components: {', '.join(missing_for_this)})"
                                )

                    # Fix parameters for missing components
                    # Use component_class determined above
                    for missing_comp in errors.get('missing_components', []):
                        if missing_comp in self.component_fixes:
                            fix_info = self.component_fixes[missing_comp]

                            # Check whether this component is required for the neuron type
                            if self._component_needed_for_type(component_class, missing_comp):
                                # Set parameters
                                if params_elem is None:
                                    params_elem = ET.SubElement(component, "Parameters")

                                # Set parameter if it is missing
                                param_elem = params_elem.find(fix_info["param"])
                                if param_elem is None:
                                    param_elem = ET.SubElement(
                                        params_elem, fix_info["param"]
                                    )
                                    param_elem.set(
                                        "Type",
                                        "std::string"
                                        if "ClassName" in fix_info["param"]
                                        else "i",
                                    )
                                    param_elem.set("PType", "257")
                                    if "ClassName" in fix_info["param"]:
                                        param_elem.text = fix_info.get(
                                            "default_class", ""
                                        )
                                    else:
                                        param_elem.text = str(
                                            fix_info.get("default_value", 1)
                                        )

                                    fixes_applied.append(
                                        f"{fix_info['param']}={param_elem.text} set "
                                        f"for {component_instance} (Class={component_class}, "
                                        f"missing component {missing_comp})"
                                    )

            # Save changes only when there are fixes
            if fixes_applied:
                # Check integrity before saving
                elements_before = len(list(root.iter()))

                # Save without pretty-printing to preserve comments
                tree.write(parameters_file, encoding='utf-8', xml_declaration=True)

                # Check integrity after saving
                tree_check = ET.parse(parameters_file)
                elements_after = len(list(tree_check.getroot().iter()))

                if elements_after < elements_before * 0.95:  # More than 5% elements lost
                    print(
                        "  ⚠️ WARNING: Elements lost while saving Parameters XML!"
                    )
                    print(f"     Before: {elements_before}, after: {elements_after}")
                    print("     Restoring from backup...")
                    if backup_file and backup_file.exists():
                        import shutil
                        shutil.copy2(backup_file, parameters_file)
                        print("     ✅ File restored from backup")
                        fixes_applied = []  # Roll back recorded fixes
                else:
                    print(
                        f"  Changes saved to {parameters_file} (elements: {elements_after})"
                    )

        except Exception as e:
            print(f"Error while processing {parameters_file}: {e}")
            # Restore from backup on error
            if backup_file and backup_file.exists():
                try:
                    import shutil
                    shutil.copy2(backup_file, parameters_file)
                    print("  File restored from backup")
                except Exception as restore_error:
                    print(
                        "  CRITICAL ERROR: failed to restore file from backup: "
                        f"{restore_error}"
                    )
            fixes_applied = []  # Clear fixes list on error

        finally:
            # Backups are NOT removed automatically; they are kept for manual rollback and investigation.
            pass

        # Process Model_*.xml if it exists
        if model_file and model_file.exists():
            model_fixes = self.fix_model_issues(model_file, parameters_file, errors)
            fixes_applied.extend(model_fixes)

        return fixes_applied

    def _get_missing_for_component_type(self, component_class: str, missing_components: List[str]) -> List[str]:
        """Determine which missing components belong to a given neuron type."""
        # Simple heuristic: Soma, Dendrite, LTZone, Generators belong to NPulseNeuron;
        # Receptor and LTZone belong to NAfferentNeuron, etc.
        neuron_types = {
            'NPulseNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane'],
            'NAfferentNeuron': ['Receptor', 'LTZone'],
            'NSimpleAfferentNeuron': ['Receptor', 'LTZone'],
            'NSAfferentNeuron': ['Receptor', 'LTZone'],
            'NSPNeuronGen': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator'],
            'PHebbNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane'],
            'PNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane']
        }

        relevant = []
        for missing in missing_components:
            for comp_type in neuron_types.get(component_class, []):
                if comp_type in missing or missing.startswith(comp_type):
                    relevant.append(missing)
                    break

        return relevant

    def _component_needed_for_type(self, component_class: str, component_name: str) -> bool:
        """Check whether a component is required for a given neuron type."""
        neuron_components = {
            'NPulseNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane'],
            'NAfferentNeuron': ['Receptor', 'LTZone'],
            'NSimpleAfferentNeuron': ['Receptor', 'LTZone'],
            'NSAfferentNeuron': ['Receptor', 'LTZone'],
            'NSPNeuronGen': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator'],
            'PHebbNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane'],
            'PNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane']
        }

        for comp_type in neuron_components.get(component_class, []):
            if comp_type in component_name or component_name.startswith(comp_type):
                return True

        return False

    def _extract_components_from_parameters(self, parameters_file: Path) -> Dict[str, Dict]:
        """Extract all components from Parameters_*.xml with their classes and parent paths."""
        components_map = {}  # component_name -> {'class': ..., 'parent_paths': [...]}

        try:
            tree = ET.parse(parameters_file)
            root = tree.getroot()

            def extract_recursive(elem, parent_path: List[str]):
                """Recursively collect components and their paths to parent containers."""
                # Skip service elements at the top level
                if elem.tag in ["SaveProperties", "Model"]:
                    for child in elem:
                        extract_recursive(child, parent_path)
                    return

                # If this is Components, process child components
                if elem.tag == "Components":
                    for child in elem:
                        extract_recursive(child, parent_path)
                    return

                # If this is Parameters, skip (not a component)
                if elem.tag == "Parameters":
                    return

                # If this is a component (has Class attribute)
                component_class = elem.get("Class", "")
                if component_class:
                    component_name = elem.tag

                    # Store component with path to parent container
                    if component_name not in components_map:
                        components_map[component_name] = {
                            "class": component_class,
                            "parent_paths": [],
                        }
                    # Store path to parent Components (without the component itself)
                    components_map[component_name]["parent_paths"].append(parent_path.copy())

                # Recurse into children (including nested Components)
                for child in elem:
                    if child.tag == "Components":
                        # For Components children, update path by adding current component
                        extract_recursive(child, parent_path + [elem.tag])
                    else:
                        # For other elements pass the current path unchanged
                        extract_recursive(child, parent_path)

            # Start from the root Model
            model_elem = root.find("Model")
            if model_elem is not None:
                model_components = model_elem.find("Components")
                if model_components is not None:
                    extract_recursive(model_components, [])

        except Exception as e:
            print(
                f"  Warning: failed to extract components from {parameters_file}: {e}"
            )
            import traceback
            traceback.print_exc()

        return components_map

    def _find_component_in_model(self, model_root, component_name: str, parent_path: List[str] = None) -> Optional[ET.Element]:
        """Find a component in Model by its name and parent path."""
        if parent_path is None:
            parent_path = []

        # Look in root Components
        model_components = model_root.find("Components")
        if model_components is None:
            return None

        # If path is empty, search directly in root Components
        if not parent_path:
            for comp in model_components:
                if comp.tag == component_name:
                    return comp
            return None

        # Traverse the path (e.g. Model.Components.Neuron1.Components.Dendrite1_1)
        current = model_components
        for path_elem in parent_path:
            found = None
            for child in current:
                if child.tag == path_elem:
                    found = child
                    break
            if found is None:
                return None
            # Go to the next-level Components
            current = found.find("Components")
            if current is None:
                return None

        # Search for the component on the current level
        for comp in current:
            if comp.tag == component_name:
                return comp

        return None

    def fix_model_issues(self, model_file: Path, parameters_file: Path, errors: Dict) -> List[str]:
        """Fix component issues in Model_*.xml by adding missing components from Parameters_*.xml."""
        fixes_applied = []

        if not parameters_file.exists():
            return fixes_applied

        # Create Model backup before modifications
        backup_file = None
        try:
            backup_file = self._create_backup(model_file)
        except Exception as e:
            print(
                f"  Warning: failed to create backup {model_file}: {e}"
            )
            return fixes_applied

        try:
            # Parse Model
            model_tree = ET.parse(model_file)
            model_root = model_tree.getroot()

            # Extract components from Parameters
            params_components = self._extract_components_from_parameters(parameters_file)

            # Count elements before modifications
            elements_before = len(list(model_root.iter()))

            # Find root Components element in Model
            model_components_elem = model_root.find("Components")
            if model_components_elem is None:
                # If Components is absent, create it
                model_components_elem = ET.SubElement(model_root, "Components")

            # Create a map of existing components in Model for fast lookup
            # Key: (component_name, parent_path_str) -> element
            existing_components = {}

            def map_existing_recursive(elem, parent_path: List[str]):
                """Recursively build the map of existing components."""
                if elem.tag == "Components":
                    for child in elem:
                        component_name = child.tag
                        component_class = child.get("Class", "")
                        if component_class:  # Only components with Class
                            parent_path_str = ".".join(parent_path) if parent_path else "root"
                            key = (component_name, parent_path_str)
                            existing_components[key] = child
                            # Recurse into nested Components
                            child_components = child.find("Components")
                            if child_components is not None:
                                map_existing_recursive(child_components, parent_path + [component_name])

            map_existing_recursive(model_components_elem, [])

            # Add missing components from Parameters into Model
            for comp_name, comp_info in params_components.items():
                comp_class = comp_info['class']

                # Skip service elements
                if comp_name in ["SaveProperties", "Model", "Parameters", "Components", "Links"]:
                    continue

                if not comp_class:
                    continue  # Skip elements without a class

                # Check whether the component already exists in Model
                found_in_model = False
                for parent_path in comp_info['parent_paths']:
                    parent_path_str = ".".join(parent_path) if parent_path else "root"
                    key = (comp_name, parent_path_str)
                    if key in existing_components:
                        found_in_model = True
                        break

                # If the component is not present in Model, add it
                if not found_in_model:
                    # Determine parent container where the component should be added
                    parent_elem = model_components_elem

                    # If we have parent path information, try to locate the parent
                    if comp_info['parent_paths']:
                        parent_path = comp_info["parent_paths"][0]  # Use first known path

                        # Traverse to the parent component along the path
                        current = model_components_elem
                        for parent_name in parent_path:
                            found_parent = None
                            for child in current:
                                if child.tag == parent_name:
                                    found_parent = child
                                    break
                            if found_parent is None:
                                # Parent not found, fall back to root Components
                                break
                            # Step into parent's Components
                            parent_components = found_parent.find("Components")
                            if parent_components is None:
                                # Create Components for parent if missing
                                parent_components = ET.SubElement(found_parent, "Components")
                            current = parent_components
                            parent_elem = current

                    # Ensure the component does not already exist in this container
                    already_exists = False
                    for child in parent_elem:
                        if child.tag == comp_name and child.get("Class", "") == comp_class:
                            already_exists = True
                            break

                    if not already_exists:
                        # Create component
                        new_comp = ET.SubElement(parent_elem, comp_name)
                        new_comp.set("Class", comp_class)

                        # Add minimal structure
                        ET.SubElement(new_comp, "Parameters")
                        ET.SubElement(new_comp, "Components")

                        parent_desc = (
                            ".".join(comp_info["parent_paths"][0])
                            if comp_info["parent_paths"]
                            else "root"
                        )
                        fixes_applied.append(
                            f"Component {comp_name} created in {model_file.name} "
                            f"(Class={comp_class}, parent={parent_desc}, was missing in Model)"
                        )

            # Save changes only when there are fixes
            if fixes_applied:
                # Check integrity before saving
                elements_before_save = len(list(model_root.iter()))

                # Save without pretty-printing
                model_tree.write(model_file, encoding='utf-8', xml_declaration=True)

                # Check integrity after saving
                model_check_tree = ET.parse(model_file)
                elements_after = len(list(model_check_tree.getroot().iter()))

                if elements_after < elements_before_save * 0.95:  # More than 5% elements lost
                    print(
                        "  ⚠️ WARNING: Elements lost while saving Model XML!"
                    )
                    print(f"     Before: {elements_before_save}, after: {elements_after}")
                    print("     Restoring Model from backup...")
                    if backup_file and backup_file.exists():
                        import shutil
                        shutil.copy2(backup_file, model_file)
                        print("     ✅ Model file restored from backup")
                        fixes_applied = []  # Roll back recorded fixes
                else:
                    print(
                        f"  Changes saved to {model_file} (elements: {elements_after})"
                    )

        except Exception as e:
            print(f"  Error while processing {model_file}: {e}")
            import traceback
            traceback.print_exc()
            # Restore Model from backup on error
            if backup_file and backup_file.exists():
                try:
                    import shutil
                    shutil.copy2(backup_file, model_file)
                    print("  Model file restored from backup")
                except Exception as restore_error:
                    print(
                        "  CRITICAL ERROR: failed to restore Model from backup: "
                        f"{restore_error}"
                    )
            fixes_applied = []  # Clear fixes list on error

        finally:
            # Backups are NOT removed automatically
            pass

        return fixes_applied

    def _create_backup(self, file_path: Path) -> Path:
        """Create a backup copy of a file before modification."""
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = file_path.with_suffix(file_path.suffix + f'.backup.{stamp}')
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path

    def generate_fix_report(self, fixes: Dict[str, List[str]]) -> str:
        """Generate a human-readable report with all fixes applied."""
        report = "# Configuration fix report\n\n"
        report += f"**Created at:** {self._get_current_date()}\n\n"

        total_fixed = sum(len(f) for f in fixes.values())
        report += f"**Total configurations fixed:** {len(fixes)}\n"
        report += f"**Total fixes applied:** {total_fixed}\n\n"

        report += "## Fix details\n\n"

        for config_path, config_fixes in sorted(fixes.items()):
            if config_fixes:
                report += f"### {config_path}\n\n"
                for fix in config_fixes:
                    report += f"- {fix}\n"
                report += "\n"

        return report

    def _get_current_date(self) -> str:
        """Return current date-time as DD.MM.YYYY HH:MM."""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y %H:%M")

    def run(self, dry_run: bool = False) -> Dict[str, List[str]]:
        """Run the configuration fix workflow."""
        print("Analysing validation report...")
        configs_errors = self.parse_validation_report()

        if not configs_errors:
            print("No configurations with errors found in validation report.")
            return {}

        print(f"Found {len(configs_errors)} configurations with errors.")

        fixes_applied = {}

        for config_path, errors in configs_errors.items():
            if errors.get('missing_components') or errors.get('missing_classes'):
                print(f"\nProcessing: {config_path}")

                if not dry_run:
                    fixes = self.fix_component_issues(config_path, errors)
                    if fixes:
                        fixes_applied[config_path] = fixes
                        print(f"  Fixes applied: {len(fixes)}")
                else:
                    # In dry-run mode just show what would be changed
                    print(
                        f"  Would fix: {len(errors.get('missing_components', []))} missing components"
                    )

        if not dry_run and fixes_applied:
            # Save fix report
            report = self.generate_fix_report(fixes_applied)
            report_file = self.reports_dir / "ConfigFixes-Report.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\nFix report saved to: {report_file}")

        return fixes_applied


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix problems with missing components in configurations."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode (no changes are written).",
    )
    parser.add_argument(
        "--configs-dir",
        default="Bin/Configs",
        help="Directory with configurations (default: Bin/Configs)",
    )
    parser.add_argument(
        "--reports-dir",
        default="Reports",
        help="Directory with reports (default: Reports)",
    )

    args = parser.parse_args()

    fixer = ConfigFixer(
        configs_dir=args.configs_dir,
        reports_dir=args.reports_dir,
    )

    fixes = fixer.run(dry_run=args.dry_run)

    if args.dry_run:
        print(
            "\nDry-run completed. Run again without --dry-run to apply fixes."
        )
    else:
        print(f"\nFixes applied for {len(fixes)} configurations.")


if __name__ == '__main__':
    main()
