"""Resolve historical Classic report paths without editing archived records."""
from os.path import abspath
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "Reports/StructTrainClassic"
PLANS = REPORTS / "_work/plans"
OFFICE_REPORTS = {".docx", ".xlsx", ".md"}
PLAN_FILES = {
    "GraphComparisonPlan.xlsx",
    "LegacyModelCheckPlan.docx",
    "TrainingReproducibilityPlan.docx",
    "DiscrepancyDiagnosisPlan.docx",
}


def report_path(path, *, root=ROOT):
    """Map a path recorded before the report move to its current location."""
    path = Path(abspath(root / Path(path)))
    reports = root / "Reports/StructTrainClassic"
    if not path.is_relative_to(reports):
        return path

    relative = path.relative_to(reports)
    if not relative.parts or relative.parts[0] == "_work":
        return path
    if path.name in PLAN_FILES and (relative.parts[0] == "outputs" or len(relative.parts) == 1):
        return reports / "_work/plans" / path.name
    if path.suffix.casefold() in OFFICE_REPORTS:
        if relative.parts[0] == "outputs":
            return reports / path.name
        if len(relative.parts) == 1:
            return path
    if relative == Path(".gitattributes"):
        return path
    return reports / "_work" / relative


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python report_paths.py <recorded path>")
    print(report_path(sys.argv[1]))
