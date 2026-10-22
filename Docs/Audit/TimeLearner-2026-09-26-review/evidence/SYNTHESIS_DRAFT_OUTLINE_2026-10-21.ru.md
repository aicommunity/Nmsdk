# SYNTHESIS — черновое оглавление (не финал)

**Статус:** OUTLINE ONLY. Документ **`SYNTHESIS_FINAL` по полной 13-волновой матрице** запрещён: после RERUN только **3/13** волн с `launch.exit=0` ([`G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`](G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md)). Разрешён путь **`SYNTHESIS_PARTIAL`** по политике [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md) (метрики только exit-clean + `failure_class` для остальных). Этот файл фиксирует структуру сводки.

---

## 0. Область и SHA

Коротко: baseline root/Bin/PulseLib на дату финала; какие cold-arm включены (G1 S1, без смешения с E2 S0/S2 в одной таблице без колонки Arm). Ссылка на [`00_RULES.md`](../plans/AGENT_PLAN_2026-10-20/00_RULES.md) и иерархию [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md).

## 1. Ворота кампании (checklist)

- A0 provenance; A1 контроли; A3 runtime wiring; B2 inputs; C1 kernels; C2_MATCH; E2 R8 EQUIVALENT ([`E2_R8_SYNTHESIS_2026-10-21.ru.md`](E2_R8_SYNTHESIS_2026-10-21.ru.md)).
- G1: отбор 13 волн / 32 case; RERUN **закрыт**; exit audit **3/13** clean ([`G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`](G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md)); PARTIAL policy принята.
- Открытый TECH_DEBT: [`TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md) (обновление 2026-10-21).

## 2. Trainer×Mode — системные выводы

Развёрнутые абзацы (не только таблица):

- **Classic×N0:** W01 Need=0 + silent Test (DEBT); эквивалентность E2.
- **Classic×N1:** CL-N1 stall на W02 (L=54 44 1 1, not_converged) — все arms E2; bisect D1 частично ([`D1_PARTIAL_2026-10-20.ru.md`](D1_PARTIAL_2026-10-20.ru.md)).
- **Branch×N0/N1:** W04/W10 — converged vs fires/quality; остров nextseg/preinh vs gen/preinh silent.

## 3. Таблица результатов (шаблон)

Группировка: Trainer×Mode → Span → NeuronModel → строки Mod; колонки PostTune ON/OFF (если применимо), Host, RUN_ID, SHA, **Train**, **Test**, `training_convergence`, `fires`, `separation_quality`, margin/residue (когда появятся C++ поля S0).

Источник строк G1: `G1_selected_2026-10-21.tsv` + extract TSV (после exit-clean).

## 4. C2 vs Console (G1)

Сопоставление [`G1_predictions_2026-10-21.tsv`](G1_predictions_2026-10-21.tsv) с фактом; каждое расхождение — отдельный подпункт (feasible=false, oracle vs silent, quality_fail при gate_ok).

## 5. Точечные фиксы F1–F8 (R8 context)

Краткая narrative по закрытым cold (F2/F3/F4/F6) и OPEN F5 ([`F5_GAMMA_COLD_2026-10-21.ru.md`](F5_GAMMA_COLD_2026-10-21.ru.md)); без зачёта silent Test как PASS.

## 6. Controller v2 и этап 5–6

Ссылка на DRAFT [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md); решение «432 v1 vs v2» — после G1.

## 7. Риски и следующий цикл

Disk/offload policy на `.17`; ложный SERIES_DONE; приоритет silent-Test vs F5 vs G1 rerun.

---

*При публикации финала переименовать в `SYNTHESIS_FINAL_2026-10-XX.ru.md` и удалить или пометить superseded этот OUTLINE.*
