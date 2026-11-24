"""Recalculate archival answers from original XLSX cells and text files."""
from collections import Counter
from pathlib import Path
import json
import math
import posixpath
import re
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import ROOT, WORK, PREVIOUS, OLD, load, save, sha, relative

ARCHIVE = ROOT / "Docs/ClassicStructTrainExperiments/Эксперименты"
RESEARCH = ARCHIVE / "Исследование"
SOURCE_NAMES = {
    "Схема 3 на 4": ("3 на 4", 0),
    "Схема 0 на 1": ("0 на 1", 1),
    "Схема 0 на 1(2)+4": ("0 на 1(2)+4", -1),
    "Схема 0 на 1+4 для 150 примеров": ("0 на 1+4 для 150 примеров", 0),
    "Схема 0 на 1+4(верн. синапсы)": ("0 на 1+4 (верное число синапсов)", 0),
}


def sheet_xml(archive, sheet):
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    node = next(row for row in workbook.findall(".//{*}sheet") if row.get("name") == sheet)
    relationship = node.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    targets = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    target = next(row.get("Target") for row in targets if row.get("Id") == relationship)
    member = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
    return ET.fromstring(archive.read(member))


def source_cells(path, sheet, with_text=False):
    with ZipFile(path) as archive:
        xml = sheet_xml(archive, sheet)
        shared = (["".join(node.itertext()) for node in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
                  if with_text else [])
        values = {}
        for cell in xml.findall(".//{*}sheetData/{*}row/{*}c"):
            kind, value = cell.get("t", "n"), cell.findtext("{*}v")
            if value is None:
                continue
            if kind == "n":
                values[cell.get("r")] = float(value)
            elif with_text and kind == "s":
                values[cell.get("r")] = shared[int(value)]
        return values


def summary_formulas(path, sheet):
    with ZipFile(path) as archive:
        formulas = {c.get("r"): c.find("{*}f") for c in sheet_xml(archive, sheet).findall(".//{*}c")
                    if c.find("{*}f") is not None}
    shared = {f.get("si"): f.text for f in formulas.values() if f.get("si") is not None and f.text}
    return {cell: (f.text or shared[f.get("si")], f.text is None) for cell, f in formulas.items()}


def audit_summaries(cells, formulas, column, state, ids, metrics):
    expected = []
    if len(ids) == 150:
        suffix = str(state + 1)
        tp, fp, fn, tn = (metrics[k] for k in ("TP", "FP", "FN", "TN"))
        expected = [(col + suffix, name, value, None) for col, name, value in (
            ("AC", "TP", tp), ("AD", "FP", fp), ("AE", "FN", fn), ("AF", "TN", tn),
            ("AG", "precision", tp/(tp+fp)), ("AH", "recall", tp/(tp+fn)), ("AI", "Q", fp+fn))]
    elif len(ids) == 30:
        expected = [(column + "32", "TP", metrics["TP"], (12, 21)),
                    (column + "33", "FP", metrics["FP"], (22, 31))]
    elif len(ids) == 10:
        expected = [(column + "12", "TP", metrics["TP"], (2, 11))]
    audited = []
    for cell, name, value, interval in expected:
        formula, shared = formulas.get(cell, (None, False))
        if interval:
            match = re.fullmatch(r"SUM\(([A-Z]+)(\d+):([A-Z]+)(\d+)\)", formula or "")
            assert match and match[1] == match[3] and (int(match[2]), int(match[4])) == interval, cell
            assert shared or match[1] == column, cell
            assert sum(cells[f"{column}{i}"] for i in range(interval[0], interval[1] + 1)) == value, cell
        assert math.isclose(cells[cell], value, rel_tol=1e-12, abs_tol=1e-12), (cell, name, value)
        audited.append({"cell": cell, "metric": name, "recalculated": value, "formula": formula,
                        "shared_formula": shared, "answer_rows": interval})
    return audited


def confusion(answers, ids, target):
    counts = Counter((a, (i - 1) // 50 + 1 == target) for a, i in zip(answers, ids, strict=True))
    return dict(TP=counts[1, True], FP=counts[1, False], FN=counts[0, True], TN=counts[0, False])


def read_output(path):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    structure = [int(token) for token in lines[0].split()[:10]]
    return structure, [int(value) for value in lines[1:] if value.strip()]


def run():
    for path, digest in load(PREVIOUS / "prior-evidence-lock.json").items():
        assert sha(ROOT / path) == digest, path
    for item in load(PREVIOUS / "delivery-manifest.json")["deliverables"]:
        assert sha(ROOT / item["path"]) == item["sha256"], item["path"]
    diagnostic = load(PREVIOUS / "report-data.json")
    book = ARCHIVE / "Тестирование/Распознавание/Распознавание.xlsx"
    cells = source_cells(book, "Sheet1")
    book_hash = sha(book)
    answer_rows = []
    for column in diagnostic["recognition"]:
        letter = column["source_range"].split("1:")[0]
        for identifier, (history, previous, trained) in enumerate(zip(
                column["historical_answers"], column["previous_answers"], column["new_answers"], strict=True), 1):
            cell = f"{letter}{identifier + 2}"
            assert cells[cell] == history, cell
            answer_rows.append({
                "source": relative(book), "sheet": "Sheet1", "cell": cell, "sha256": book_hash,
                "experiment": column["label"], "protocol": "150 continuous", "state": 1, "input_id": identifier,
                "historical": history, "previous": previous, "trained": trained,
                "previous_model": column["previous_structure"],
                "previous_log": column["previous_native_source"],
                "trained_log": column["new"]["runs"][0].get("inference_source"),
            })
    save(WORK / "archival-answers.json", answer_rows)

    book = RESEARCH / "Обучение нескольким примерам.xlsx"
    book_hash = sha(book)
    cache = {name: source_cells(book, name) for name in SOURCE_NAMES}
    formulas = {name: summary_formulas(book, name) for name in SOURCE_NAMES}
    references = load(OLD / "protocol-references.json")
    science = load(OLD / "scientific-comparison-data.json")
    structural_source = science["primary_source"]
    structural_book = ROOT / "Docs/ClassicStructTrainExperiments" / structural_source["relative"]
    assert sha(structural_book) == structural_source["sha256"]
    structural_cells = source_cells(structural_book, structural_source["sheet"], with_text=True)
    for row in structural_source["rows"]:
        columns = (list("GHIJK"), list("RSTUV")) if row["algorithm"] == "NT" else (
            list("LMNOP"), ["W", "X", "Y", "Z", "AA"])
        assert structural_cells[f"A{row['row']}"] == row["input_id"]
        for field, keys in zip(("dendrites", "original_synapses"), columns, strict=True):
            assert row[field] == [structural_cells.get(f"{key}{row['row']}") for key in keys], row["record"]
    state_rows, discrepancies = [], []
    for row in references:
        folder, offset = SOURCE_NAMES[row["sheet"]]
        filename = RESEARCH / folder / f'output_data{row["state"] + offset}.txt'
        structure, answers = read_output(filename)
        ids = row["input_ids"]
        col = row["source_range"].split("2:")[0]
        workbook_answers = [int(cache[row["sheet"]][f"{col}{i+2}"]) for i in range(len(ids))]
        actual = answers[:len(ids)]
        assert set(answers) <= {0, 1}
        assert structure == row["dendrites"] + row["synapses"], filename
        assert workbook_answers == actual == row["answers"], filename
        metrics = confusion(actual, ids, 2)
        if len(ids) == 150:
            published = science["epochs"][row["state"] - 1]["old"]
            assert metrics == {key: published[key] for key in metrics}
        state_rows.append({
            "source": relative(book), "sha256": book_hash, "sheet": row["sheet"],
            "range": row["source_range"], "state": row["state"], "file": relative(filename),
            "file_sha256": sha(filename), "graph_ds": structure, "metrics": metrics,
            "mapped_answers": len(ids), "unmapped_answer_lines": answers[len(ids):],
            "input_ids": ids, "answers": actual,
            "summary_audit": audit_summaries(cache[row["sheet"]], formulas[row["sheet"]], col,
                                             row["state"], ids, metrics),
            "job": row["job"],
        })
        if len(answers) != len(ids):
            discrepancies.append({
                "source": relative(filename), "status": "unmapped_extra_record",
                "lines": list(range(len(ids) + 2, len(answers) + 2)), "values": answers[len(ids):],
            })
    seen = {row["file"] for row in state_rows}
    unpaired = []
    for directory, _ in SOURCE_NAMES.values():
        for path in sorted((RESEARCH / directory).glob("output_data*.txt")):
            if relative(path) not in seen:
                _, data = read_output(path)
                unpaired.append({"file": relative(path), "sha256": sha(path), "answers": len(data)})
    duplicate_a = RESEARCH / "0 на 1/output_data1.txt"
    duplicate_b = duplicate_a.with_name("output_data2.txt")
    assert sha(duplicate_a) == sha(duplicate_b)
    variant_fields = ("id", "binary_sha256", "pulselib_sha", "rdk_sha",
                      "controller_sha256", "training_adapter_sha256")
    order_legacy = []
    for name in ("VB", "FO"):
        metadata = load(PREVIOUS / "variants" / f"{name}.json")
        order_legacy.append({field: metadata[field] for field in variant_fields})
    save(WORK / "source-audit.json", {
        "recognition_cells_verified": len(answer_rows), "protocols": state_rows,
        "structure": {**structural_source, "path": relative(structural_book)},
        "retained_order_variants": order_legacy,
        "unmapped_records": discrepancies, "unpaired_files": unpaired,
        "duplicate_single_iteration_files": [relative(duplicate_a), relative(duplicate_b)],
        "original_2022_callable_recognition_chain_recovered": False,
    })
    print(f"Verified {len(answer_rows)} source cells and {len(state_rows)} protocol states")


if __name__ == "__main__":
    run()
