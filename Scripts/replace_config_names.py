#!/usr/bin/env python3
"""
Script to replace old component names (PosChannel/NegChannel) with new ones (InhChannel/ExcChannel)
in XML configuration files.

Replacement rules:
- PosChannel → InhChannel (Type=1, inhibitory channel)
- NegChannel → ExcChannel (Type=-1, excitatory channel)
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

# Replacement patterns
REPLACEMENTS = [
    # In component paths
    (r'\.PosChannel', '.InhChannel'),
    (r'\.NegChannel', '.ExcChannel'),
    (r'PosChannel\.', 'InhChannel.'),
    (r'NegChannel\.', 'ExcChannel.'),
    # In XML tags
    (r'<PosChannel', '<InhChannel'),
    (r'</PosChannel>', '</InhChannel>'),
    (r'<NegChannel', '<ExcChannel'),
    (r'</NegChannel>', '</ExcChannel>'),
    # In Name tag values (only when it is the whole value, not part of another word)
    (r'>PosChannel</Name>', '>InhChannel</Name>'),
    (r'>NegChannel</Name>', '>ExcChannel</Name>'),
]

def replace_in_file(file_path: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Replace old component names with new ones in a single file.

    Returns:
        Tuple[int, List[str]]: (number of replacements, list of changed lines)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try additional encodings
        try:
            with open(file_path, 'r', encoding='cp1251') as f:
                content = f.read()
        except:
            print(f"Warning: Cannot read {file_path}, skipping")
            return 0, []

    original_content = content
    changes = []
    total_replacements = 0

    # Perform replacements
    for pattern, replacement in REPLACEMENTS:
        matches = list(re.finditer(pattern, content))
        if matches:
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                changes.append(f"  Line {line_num}: {match.group()} → {replacement}")
            content = re.sub(pattern, replacement, content)
            total_replacements += len(matches)

    # Save changes if any
    if content != original_content and not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except:
            print(f"Error: Cannot write {file_path}")
            return 0, []

    return total_replacements, changes

def validate_xml(file_path: Path) -> bool:
    """Validate XML file."""
    try:
        ET.parse(file_path)
        return True
    except ET.ParseError as e:
        print(f"XML validation error in {file_path}: {e}")
        return False

def main():
    configs_dir = Path("Bin/Configs")
    if not configs_dir.exists():
        print(f"Error: Directory {configs_dir} not found")
        sys.exit(1)

    # Find all XML files
    xml_files = list(configs_dir.rglob('*.xml'))
    print(f"Found {len(xml_files)} XML files")

    # Statistics
    total_files_changed = 0
    total_replacements = 0
    files_with_errors = []

    # Process each file
    for xml_file in xml_files:
        replacements, changes = replace_in_file(xml_file, dry_run=False)

        if replacements > 0:
            total_files_changed += 1
            total_replacements += replacements

            # Validate XML
            if not validate_xml(xml_file):
                files_with_errors.append(str(xml_file))
                print(f"Warning: XML validation failed for {xml_file}")

    # Print summary
    print(f"\n=== Replacement Summary ===")
    print(f"Total XML files processed: {len(xml_files)}")
    print(f"Files changed: {total_files_changed}")
    print(f"Total replacements: {total_replacements}")

    if files_with_errors:
        print(f"\nWarning: {len(files_with_errors)} files have XML validation errors:")
        for f in files_with_errors[:10]:  # Show first 10
            print(f"  - {f}")
        if len(files_with_errors) > 10:
            print(f"  ... and {len(files_with_errors) - 10} more")
    else:
        print("\nAll files passed XML validation!")

if __name__ == '__main__':
    main()
