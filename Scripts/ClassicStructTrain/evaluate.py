#!/usr/bin/env python3
"""Compare replay measurements with archived observations and audit coverage."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from html import escape
import json
import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_paths import report_path
REPO = Path(__file__).resolve().parents[2]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def expected_cases(manifest, suite, repeat=1):
    ids = manifest["selected_ids"]
    if suite in ("smoke", "cold", "structures"):
        selected = [22] if suite == "smoke" else ids if suite == "cold" else range(1, 151)
        return [f"{kind}-{i}" for kind in ("learner", "trainer") for i in selected]
    if suite == "warm":
        return [f"transition-{i}" for i in range(91)]
    if suite == "recognition":
        return [f"{kind}-{i}" for kind in ("learner", "trainer") for i in ids] + [
            f"{v['kind']}-{v['id']}-frozen-{v['variant_index']}" for v in manifest["recognition_models"] if repeat == 1]
    if suite == "modes":
        return [x["case"] for x in manifest["mode_cases"]]
    if suite == "diagnostics":
        return ["observer-noninterference", "mode-change-iteration-clock", "recreate-subject", "save-reload-trained-model"]
    if suite == "two_examples":
        horizons = {"baseline51": 0, "baseline61": 0, "midpoint": 0, "2_2": 13, "3_4": 7,
                    "0_1": 18, "0_1_4_subset": 13, "0_1_4_full": 13}
        return [f"{scheme}-epoch-{epoch}" for scheme, last in horizons.items() for epoch in range(last+1)] + ["0_1_2_4_ambiguous"]
    raise ValueError(f"Unknown suite {suite}")


def compare_vectors(record, references):
    complete = [r for r in references if r.get("dendrites") is not None and r.get("synapses") is not None]
    if any(record.get("dendrites") == r["dendrites"] and record.get("synapses") == r["synapses"] for r in complete):
        return "match"
    if complete:
        return "difference"
    return "source_gap"


def structural_references(record, evidence):
    suite, ident, kind = record["suite"], record.get("id"), record.get("kind")
    if record.get("frozen_archive_structure"):
        return [record["reference"]]
    if suite in ("cold", "structures", "recognition"):
        key = "structural" if suite == "structures" else "cold"
        return [r for r in evidence.get(key, []) if r["id"] == ident and r["kind"] == kind]
    if suite == "warm":
        if "transition_index" not in record:
            return []
        index = record["transition_index"]
        return ([r for r in evidence["cold"] if r["repeat"] == record["repeat"] and r["id"] == ident and r["kind"] == "learner"]
                if index == 0 else [r for r in evidence["warm"] if r["repeat"] == record["repeat"] and int(r["case"].split(".")[-1]) == index])
    return []


def recognition_diagnostics(record, evidence):
    refs = [r for r in evidence.get("recognition", []) if r["id"] == record.get("id") and r["kind"] == record.get("kind")]
    if record.get("frozen_archive_structure"):
        refs = [r for r in refs if r["variant"] == record["reference"]["recognition_variant"]]
    answers = record.get("answers", [])
    mismatch = min((sum(a != b for a, b in zip(answers, r["answers"])) for r in refs), default=None) if len(answers) == 150 else None
    return {"answer_mismatches_min": mismatch, "answer_exact_match": mismatch == 0 if mismatch is not None else None,
            "role": "secondary_diagnostic_not_structure_acceptance"}


def structure_details(record, evidence):
    frozen = record.get("frozen_archive_structure", False)
    native = record["suite"] in ("cold", "structures", "warm", "recognition", "two_examples") and not frozen
    has_vectors = record.get("dendrites") is not None and record.get("synapses") is not None
    readback = record.get("structure_readback", {})
    valid = readback.get("consistent") is not False and readback.get("all_initialized") is not False
    stage = ("reference_reconstruction" if frozen else
             ("final_trained" if valid else "invalid_physical_graph") if native and has_vectors and record.get("status") == "completed" else
             "intermediate_at_stop" if native and has_vectors else "unavailable" if native else "control")
    refs = structural_references(record, evidence)
    comparison = compare_vectors(record, refs)
    return {"primary_structure_case": native and record.get("status") != "source_gap", "structure_stage": stage,
            "final_structure_match": comparison == "match" if stage == "final_trained" and valid and comparison != "source_gap" else None,
            "reconstructed_setup_match": comparison == "match" and valid if frozen else None,
            "reference_structures": [{k: r.get(k) for k in ("dendrites", "synapses", "source", "source_row")} for r in refs],
            "iteration_counts_reference": sorted({r["iterations"] for r in refs if r.get("iterations") is not None}),
            "physical_bounds_pass": record.get("physical_bounds_pass")}


def compare(record, evidence):
    status = record.get("status")
    if status == "source_gap":
        return "source_gap", record.get("reason", "Historical implementation is not recoverable")
    if status not in ("completed", "recorded"):
        return "incomplete", record.get("reason", status or "No native completion status")
    suite, ident, kind = record["suite"], record.get("id"), record.get("kind")
    if suite in ("cold", "structures"):
        references = structural_references(record, evidence)
        classification = compare_vectors(record, references)
        if (record.get("structure_readback", {}).get("consistent") is False
                or record.get("structure_readback", {}).get("all_initialized") is False):
            return "incomplete", "Reported structure is inconsistent with the physical graph or is uninitialized"
        return classification, "Structural comparison against recorded variants; missing cells stay missing"
    if suite == "warm":
        references = structural_references(record, evidence)
        classification = compare_vectors(record, references)
        if (record.get("structure_readback", {}).get("consistent") is False
                or record.get("structure_readback", {}).get("all_initialized") is False):
            return "incomplete", "Retrained physical structure is inconsistent or uninitialized"
        return classification, "The saved 91-pattern sequence is used without resetting its structure between patterns"
    if suite == "recognition":
        if (record.get("structure_readback", {}).get("all_initialized") is False
                or record.get("structure_readback", {}).get("consistent") is False
                or record.get("structure_unchanged") is False):
            return "incomplete", "Recognition structure is uninitialized or changed while recognizing"
        if len(record.get("answers", [])) != 150:
            return "incomplete", "Recognition did not produce exactly 150 answers"
        if record.get("frozen_archive_structure"):
            return "recorded", "Recognition on a supplied archived structure; answer differences are secondary diagnostics"
        return compare_vectors(record, structural_references(record, evidence)), "Final trained structure is the primary criterion; recognition answers are secondary"
    if suite == "modes":
        failed = [k for k in ("threshold_matches_requested_mode", "recognition_structure_unchanged") if record.get(k) is False]
        return ("difference", "Failed transition checks: "+", ".join(failed)) if failed else ("recorded", "Transition trace is retained with the original protocol row")
    if suite == "diagnostics":
        failed = [k for k in ("same_structure", "same_need_to_train", "start_matches_transition", "same_structure_after_recreation") if record.get(k) is False]
        if record.get("structure_readback", {}).get("consistent") is False:
            failed.append("structure_readback.consistent")
        return ("difference", "Failed lifecycle checks: "+", ".join(failed)) if failed else ("match", "Native lifecycle and observer controls")
    if suite == "two_examples":
        return "recorded", "Epoch structure, answers and standard metrics are preserved for source-specific comparison"
    return "recorded", "Native measurement"


def metrics(answers, classes, target):
    if len(answers) != len(classes) or any(a not in (0, 1) for a in answers):
        raise ValueError("Expected one binary answer per input")
    tp = sum(a == 1 and c == target for a, c in zip(answers, classes))
    fp = sum(a == 1 and c != target for a, c in zip(answers, classes))
    fn = sum(a == 0 and c == target for a, c in zip(answers, classes))
    tn = sum(a == 0 and c != target for a, c in zip(answers, classes))
    n = len(answers)
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "precision": tp/(tp+fp) if tp+fp else None, "recall": tp/(tp+fn) if tp+fn else None,
            "accuracy": (tp+tn)/n if n else None,
            "balanced_accuracy": .5*(tp/(tp+fn)+tn/(tn+fp)) if tp+fn and tn+fp else None,
            "empirical_risk": (fp+fn)/n if n else None}


def evaluate(run_dir):
    manifest = read_json(REPO / "Bin/Configs/StructTrainClassic/Prepared/manifest.json")
    evidence = read_json(REPO / "Reports/StructTrainClassic/_work/archive-evidence.json")
    rows, processes, coverage_errors = [], [], []
    repeat_signatures = defaultdict(list)
    for process_file in sorted(run_dir.glob("*/process.json")):
        process = read_json(process_file)
        processes.append(process)
        result_file = process_file.parent / "results.jsonl"
        records = []
        if result_file.exists():
            for line_number, line in enumerate(result_file.read_text(encoding="utf-8").splitlines(), 1):
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as ex:
                    coverage_errors.append(f"{process_file.parent.name}: malformed result line {line_number}")
                    rows.append({"suite": process["suite"], "case": f"malformed-result-line-{line_number}", "repeat": process["repeat"],
                                 "classification": "incomplete", "reason": str(ex)})
        seen = set()
        for record in records:
            identity = record["case"]
            if record["suite"] in ("cold", "structures", "warm") and record.get("status") != "not_run_precondition":
                signature = {k: record.get(k) for k in ("status", "dendrites", "synapses", "iterations")}
                repeat_signatures[(record["suite"], identity)].append({"repeat": record["repeat"], "signature": signature})
            classification, reason = compare(record, evidence)
            if identity in seen:
                classification, reason = "incomplete", "Duplicate result identity"
                coverage_errors.append(f"{process_file.parent.name}: duplicate {identity}")
            seen.add(identity)
            if "answers" in record:
                if record["suite"] == "recognition":
                    classes = [x["class"] for x in manifest["dataset"]]
                    control = metrics(record["answers"], classes, (record["id"]-1)//50+1)
                    for k, expected in control.items():
                        actual = record.get(k)
                        if expected is None and actual is not None or expected is not None and (actual is None or not math.isclose(actual, expected, abs_tol=1e-12)):
                            classification, reason = "incomplete", f"Independent metric calculation disagrees for {k}"
            rows.append({"suite": record["suite"], "case": identity, "repeat": record["repeat"], "classification": classification,
                         "native_status": record.get("status"), "reason": reason, "id": record.get("id"), "kind": record.get("kind"),
                         "iterations": record.get("iterations"), "dendrites": record.get("dendrites"), "synapses": record.get("synapses"),
                         "frozen_archive_structure": record.get("frozen_archive_structure", False),
                         **structure_details(record, evidence),
                         **(recognition_diagnostics(record, evidence) if record["suite"] == "recognition" and "answers" in record else {}),
                         "source": str(result_file.relative_to(run_dir))})
        expected = expected_cases(manifest, process["suite"], process["repeat"])
        if "--only-id" in process["command"]:
            only_id = int(process["command"][process["command"].index("--only-id")+1])
            expected = [k for k in expected if k.endswith(f"-{only_id}") or f"-{only_id}-frozen-" in k]
        for missing in sorted(set(expected)-seen):
            coverage_errors.append(f"{process_file.parent.name}: missing {missing}")
            rows.append({"suite": process["suite"], "case": missing, "repeat": process["repeat"], "classification": "incomplete",
                         "primary_structure_case": process["suite"] in ("cold", "structures", "warm", "recognition", "two_examples"),
                         "structure_stage": "unavailable",
                         "reason": "No native result; process status="+process["status"], "source": str(process_file.relative_to(run_dir))})
    totals = Counter(r["classification"] for r in rows)
    per_suite = {s: dict(Counter(r["classification"] for r in rows if r["suite"] == s)) for s in sorted({r["suite"] for r in rows})}
    run_file = run_dir / "run.json"
    run_finished = run_file.is_file()
    if run_finished and len(read_json(run_file)["jobs"]) != len(processes):
        coverage_errors.append("Supervisor job count does not match recorded process directories")
    repeated = {k: v for k, v in repeat_signatures.items() if len(v) > 1}
    disagreements = [{"suite": k[0], "case": k[1], "repeats": values} for k, values in repeated.items()
                     if any(v["signature"] != values[0]["signature"] for v in values[1:])]
    primary = [r for r in rows if r.get("primary_structure_case")]
    frozen = [r for r in rows if r.get("frozen_archive_structure")]
    structural_summary = {"native_cases": len(primary),
                          "stages": dict(Counter(r.get("structure_stage", "unavailable") for r in primary)),
                          "final_structures_available": sum(r.get("structure_stage") == "final_trained" for r in primary),
                          "final_matches": sum(r.get("final_structure_match") is True for r in primary),
                          "final_differences": sum(r.get("final_structure_match") is False for r in primary),
                          "reconstructed_archive_models": len(frozen),
                          "reconstructed_setups_verified": sum(r.get("reconstructed_setup_match") is True for r in frozen)}
    summary = {"counts": dict(totals), "per_suite": per_suite, "processes": processes, "cases": rows,
               "native_processes_completed": all(p["status"] == "completed" for p in processes),
               "supervisor_finished": run_finished,
               "all_expected_cases_recorded": run_finished and bool(processes) and not coverage_errors,
               "coverage_errors": coverage_errors,
               "native_status_counts": dict(Counter(r.get("native_status", "missing") for r in rows)),
               "all_experiments_completed": bool(rows) and totals["incomplete"] == 0,
               "all_results_match": bool(primary) and all(r.get("final_structure_match") is True for r in primary),
               "primary_acceptance_criteria": ["final trained dendrite lengths", "final trained synapse counts", "consistent initialized physical graph"],
               "structure_summary": structural_summary,
               "recognition_diagnostics": {"cases": sum(r.get("answer_exact_match") is not None for r in rows),
                                           "cases_with_answer_differences": sum(r.get("answer_exact_match") is False for r in rows),
                                           "role": "secondary; does not change structural acceptance"},
               "repeat_consistency": {"groups_compared": len(repeated), "disagreements": disagreements,
                                      "criteria": ["status", "dendrites", "synapses", "iterations"]},
               "limitations": manifest["known_source_gaps"]}
    (run_dir / "evaluation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    cols = ["suite", "case", "repeat", "classification", "native_status", "frozen_archive_structure", "id", "kind",
            "structure_stage", "final_structure_match", "reconstructed_setup_match", "dendrites", "synapses", "reference_structures",
            "iterations", "iteration_counts_reference", "physical_bounds_pass", "answer_mismatches_min", "answer_exact_match", "reason", "source"]
    with (run_dir / "comparison.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: json.dumps(r.get(k), ensure_ascii=False) if isinstance(r.get(k), (list, dict)) else r.get(k) for k in cols})
    structure_cols = [k for k in cols if k not in ("answer_mismatches_min", "answer_exact_match")]
    with (run_dir / "structure-comparison.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=structure_cols)
        writer.writeheader()
        for r in primary + frozen:
            writer.writerow({k: json.dumps(r.get(k), ensure_ascii=False) if isinstance(r.get(k), (list, dict)) else r.get(k) for k in structure_cols})
    table = "".join("<tr><td>"+escape(s)+"</td><td>"+escape(json.dumps(c, ensure_ascii=False))+"</td></tr>" for s, c in per_suite.items())
    limitations = "".join("<li>"+escape(s)+"</li>" for s in summary["limitations"])
    training_note = ("<strong>Обучение на закреплённой версии заблокировано:</strong> динамически добавленные синапсы остаются неинициализированными."
                     if summary["native_status_counts"].get("uninitialized_dynamic_structure") else
                     "Причины незавершённых опытов перечислены в полной таблице сравнения.")
    structural_conclusion = ("Финальные обученные структуры не получены. Совпадение или расхождение итоговой структуры с архивом пока не установлено."
                             if not structural_summary["final_structures_available"] else
                             f"Финальных обученных структур: {structural_summary['final_structures_available']}; совпадений: {structural_summary['final_matches']}; расхождений: {structural_summary['final_differences']}.")
    html = f'''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Повторение классических экспериментов структурного обучения</title>
<style>body{{font:17px/1.55 system-ui;max-width:1050px;margin:45px auto;padding:0 25px;color:#17202a}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #bbb;text-align:left;padding:12px}}code{{overflow-wrap:anywhere}}h1{{font-size:30px}}</style>
<h1>Повторение классических экспериментов структурного обучения</h1>
<p>Ветка autoPreset. Алгоритмы PulseLib используются без изменений; последовательностями управляет внешний стенд.</p>
<h2>Основной критерий — итоговая обученная структура</h2>
<p>Сравниваются длины дендритов и число синапсов после завершения обучения, с проверкой физического графа.
Число итераций, сигналы и ответы распознавания сохраняются как дополнительные измерения.</p>
<p><strong>{structural_conclusion}</strong></p>
<p>Промежуточных структур в момент остановки: {structural_summary['stages'].get('intermediate_at_stop', 0)}.
Их значения приведены рядом с архивными вариантами в <a href="structure-comparison.csv">таблице структур</a>.
Столбец <code>structure_stage</code> явно отделяет промежуточное состояние от финального.</p>
<p>{training_note}
Стенд проверяет физические компоненты и останавливает такой опыт со статусом <code>uninitialized_dynamic_structure</code>.
Зависимые опыты получают <code>not_run_precondition</code>. Независимый запуск штатного NeuroModelerConsole подтвердил рост счётчиков без завершения обучения.</p>
<p>Отдельные записи <code>frozen_archive_structure=true</code> — дополнительная проверка распознавания на реконструированных статических структурах.
Они не подтверждают повторение обучения. Такие структуры собраны и полностью инициализированы до распознавания; добавленные синапсы явно активированы.
Проверено восстановленных структур: {structural_summary['reconstructed_setups_verified']} из {structural_summary['reconstructed_archive_models']}.
Исторический код не позволяет установить дату и причину удаления DataFromFile: первый доступный коммит класса от 10.10.2023 уже не содержит этого свойства.</p>
<h2>Учёт всех случаев, включая контрольные проверки</h2>
<p>Результаты: <strong>{escape(json.dumps(dict(totals), ensure_ascii=False))}</strong>.</p>
<p>Всего записей: {len(rows)}; процессов: {len(processes)}; все процессы завершились штатно:
<strong>{'да' if summary['native_processes_completed'] else 'нет'}</strong>.</p>
<p>Повторяемость статуса, структуры и числа итераций: сопоставлено {len(repeated)} групп;
расхождения между повторами — {len(disagreements)}. Это проверка воспроизводимости измерений, включая неуспешные попытки.</p>
<p>Все ожидаемые случаи записаны: <strong>{'да' if summary['all_expected_cases_recorded'] else 'нет'}</strong>.
Все эксперименты завершены: <strong>{'да' if summary['all_experiments_completed'] else 'нет'}</strong>.
Статусы <code>match</code> контрольных проверок не означают успешного повторения обучения.</p>
<table><tr><th>Серия</th><th>Результаты сопоставления</th></tr>{table}</table>
<h2>Данные для проверки</h2><p><a href="comparison.csv">Полная таблица сравнения</a> · <a href="evaluation.json">Подробные результаты и команды</a></p>
<p><a href="integrity-audit.json">Проверка целостности и Release</a> ·
<a href="../preparation/pulse-integration-tests.json">Результаты восьми интеграционных тестов</a></p>
<p><a href="figures/frozen-recognition.png">Распознавание на архивных структурах</a> ·
<a href="figures/failed-native-control.png">Незавершённый контрольный запуск</a> ·
<a href="../protocol.txt">Протокол и ограничения повторения</a></p>
<p>Accuracy = (TP+TN)/N; balanced accuracy = (TPR+TNR)/2; эмпирический риск = (FP+FN)/N.
Историческое «(TP%+TN%)/2» сопоставляется со сбалансированной точностью.
Различия бинарных ответов на 150 входов — дополнительная диагностика; они не определяют соответствие итоговой структуры.
Число различающихся ответов сохранено в столбце <code>answer_mismatches_min</code>.</p>
<h2>Границы исторических данных</h2><ul>{limitations}</ul>
<p>match означает совпадение по проверяемым критериям; difference — измеренное расхождение; recorded — сохранённую трассу;
source_gap — недостаточность архивного эталона; incomplete — незавершённый или отсутствующий результат.
Завершение процесса само по себе не считается успешным экспериментом.</p>
<p>Основной репозиторий: <code>{manifest['root_sha']}</code><br>PulseLib: <code>{manifest['pulselib_sha']}</code></p></html>'''
    (run_dir / "report.html").write_text(html, encoding="utf-8")
    print(json.dumps({"counts": dict(totals), "all_expected_cases_recorded": summary["all_expected_cases_recorded"], "report": str(run_dir / "report.html")}, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    evaluate(report_path(args.run.resolve()))
