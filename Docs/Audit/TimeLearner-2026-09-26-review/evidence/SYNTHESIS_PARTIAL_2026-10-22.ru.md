# SYNTHESIS_PARTIAL — TimeLearner AGENT_PLAN (2026-10-22)

**Статус:** PARTIAL (не FINAL). Политика exit — [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md). Оглавление-черновик — [`SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md`](SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md). Группировка — [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md).

## 0. Область и SHA

Кампания AGENT_PLAN 2026-10-20 на ветке `timelearner_fix2`. Cold-arm, вошедшие в эту сводку: **E2 R8** (EQUIVALENT) и **G1 S1** (13 волн / 32 case, RERUN закрыт). Console sha256 `745d6061…`, PulseLib `6d746ac` (F5-флаг default off). Документ **не** смешивает S0/S2 E2-плечи с G1 S1 в одной доле PASS без колонки Arm.

## 1. Ворота кампании

| Ворота | Статус |
|--------|--------|
| A0 env / refresh / Console | OK; тег `tl-baseline-20261020` и DEBT-A0-ctest ещё open |
| A1 / A3 / B2 / C1 / C2_MATCH | закрыты или MATCH по evidence R/E1 |
| E1.0 cable vs Console soma-kernel | **PARTIAL** — [`E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md`](E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md) |
| E2 R8 | EQUIVALENT — [`E2_R8_SYNTHESIS_2026-10-21.ru.md`](E2_R8_SYNTHESIS_2026-10-21.ru.md) |
| G1 exit-clean полная матрица | **не** пройдена: **3/13** волн `launch.exit=0` после RERUN |
| TECH_DEBT P0 | silent-Test (H3 confirmed offline — [`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md)); CL-N1; S0 **partial**; G1-exit-gate **done** |

## 2. Trainer×Mode — системные выводы

**Classic×N0.** На Span 50 exit-clean волны **W01** (PostTune OFF) и **W33** (PostTune ON) стабильно сходятся Train (`converged_need0` / `converged_posttune_finalized`), но Test даёт **silent Acc=7/8, Цель=нет** на всех трёх rep ([`G1_S1_PARTIAL_METRICS_2026-10-22.ru.md`](G1_S1_PARTIAL_METRICS_2026-10-22.ru.md)). Offline mid-sweep на W01-15892 ([`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md)): при `candidate_mid≈0.00241` fires=`01000101` (Acc 4/8), при thr=1 — silent 7/8; **H3 подтверждена** (штатный путь маскирует soma-fire thr=1), сильный H1 (target_hit при candidate) **нет** (peak target &lt; candidate_mid). Span 100/480 (**W02**, **W31**) после RERUN — `launch_exit=1`.

**Classic×N1.** **W13** (HIST ltz50 gen) — единственная exit-clean N1-волна; та же silent 7/8 без цели. **W09** / **W12** / pack-волна **W37** после RERUN — `launch_exit=1`, доли PASS по ним в кампанию не входят. CL-N1 stall на длинных span (семейство W02 N1 в E2) остаётся открытым DEBT.

**Branch×N0 / Branch×N1.** Ни одна Branch-волна отбора не стала exit-clean после RERUN. **W04** — единственная с `launch_exit=2`; остальные Branch HIST / FastSpan (**W08**, **W10**, **W11**, **W48**) — `launch_exit=1`. Остров nextseg/preinh vs silent gen из более ранних boundary-map **не** перепроверен на exit-clean G1 S1 (нет clean Branch-волн).

## 3. Таблица результатов (PARTIAL)

Канон строк: [`G1_S1_PARTIAL_METRICS_2026-10-22.tsv`](G1_S1_PARTIAL_METRICS_2026-10-22.tsv). Кратко exit-clean (rep3):

| Trainer×Mode | Span | NeuronModel | Mod | PostTune | Case | Acc | Цель | Train | Test |
|--------------|------|-------------|-----|----------|------|-----|------|-------|------|
| Classic×N0 | 50 | AsymRm | gen | OFF | W01_CL50_N0_PSIoff | 7/8 | нет | `TimeLearnerMatrix/W01/inputs/…/Train` | `…/Test` |
| Classic×N1 | 50 | AsymRm | gen | OFF | W13_HIST_ltz50_gen | 7/8 | нет | `TimeLearnerMatrix/W13/inputs/…/Train` | `…/Test` |
| Classic×N0 | 50 | AsymRm | gen | ON | W33_CL50_N0_PSIoff_POST | 7/8 | нет | `TimeLearnerMatrix/W33/inputs/…/Train` | `…/Test` |

Остальные 29 case-строк TSV несут `failure_class=launch_exit_1|2` и Acc/Цель = `—`.

## 4. C2 vs Console (G1)

Полное сопоставление 32 case **отложено**. Для exit-clean тройки допустима точечная сверка с [`G1_predictions_2026-10-21.tsv`](G1_predictions_2026-10-21.tsv) / [`G1_vs_C2_2026-10-21.tsv`](G1_vs_C2_2026-10-21.tsv) без экстраполяции на non-exit волны. Расхождения oracle vs silent на W01/W13/W33 остаются в зоне DEBT detection/mid, не infra.

## 5. Точечные фиксы F1–F8

F2/F3/F4/F6 cold закрыты без регрессии Train на своих пилотах; **F5** — OPEN: paired γ=0 vs γ=1 на `W01_CL50_N1_PSIoff` ([`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md)) — оба плеча Need=0, **идентичный** silent 7/8, PASS **нет** (one-shot — [`F5_GAMMA_COLD_2026-10-21.ru.md`](F5_GAMMA_COLD_2026-10-21.ru.md)). F7 → F2.pref; F8 done. Silent Test **не** зачтён как PASS ни на одном фиксе.

## 6. Controller v2 и этап 5–6

Скелет DRAFT — [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md); обогащение входов 2026-10-22 (E1 δ/amp/N-sat, H3 default-off, H1-weak/H4 weakened/H2 inconclusive, D1 phase2 CLOSED first L₀≥54=`3cefd64`, open decisions candidate_mid/KeepDone/sep_margin, F1b docs-ready) — [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md). Решение «432 v1 vs v2» и V-gate этапов 4–6 **не** блокируются ожиданием 13/13 exit-clean, но **не** опираются на drv-only SERIES_DONE; F1b senior (`DEBT-F1b`) по-прежнему блокер физики быстрого EPSP до SPEC.

## 7. Риски и следующий цикл

1. Починить или явно жить с **DEBT-G1-exit-gate** в `run_series.sh` (читать значение `launch.exit`).
2. **F5** — paired W01 N1 выполнен; следующий шаг — другой case/span или mid-диагностика, не повтор W01 без гипотезы.
3. Алгоритм: H3 mid-policy **зафлажена и cold-verified** (`UseCandidateMidOnNonSeparableTest=1` → fires=`01000101`, [`MID_POLICY_H3_COLD_2026-10-22.ru.md`](MID_POLICY_H3_COLD_2026-10-22.ru.md)); default off сохраняет G1 silent. **H4 / sep_margin ослаблена** ([`SILENT_TEST_H4_MARGIN_2026-10-22.ru.md`](SILENT_TEST_H4_MARGIN_2026-10-22.ru.md)). **W13/W33 offline mid** реплицируют H1-weak/H3 при TipR 20M×3+86M — [`SILENT_TEST_W13_W33_MID_2026-10-22.ru.md`](SILENT_TEST_W13_W33_MID_2026-10-22.ru.md). **H2 KeepDone cold W33** — **inconclusive** ([`SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md`](SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md)). **H2 frozen TipR overlay W01** на `.17` (`H2.TipROverlay-17-20261022T090800Z`): flat / midband_20M / keep_snap × thr=1 и `candidate_mid` — все `fires=null`, diagnostic `rc=-6` (`EmitToGlog`) → H2 **still inconclusive**; долг **`DEBT-17-console-glog`**, не TipR physics — [`SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md`](SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md). Next overlay — local HEAD после D1 `3cefd64`, не повтор abort на `.17`. **D1 phase2 CLOSED:** lo=`5308aa5`(L₀=53) … hi=`3cefd64`(L₀=100≥54, MaxL escape); первый L₀≥54 = **`3cefd64`** — [`D1_BISECT_2026-10-22.ru.md`](D1_BISECT_2026-10-22.ru.md). **E1.0 / E1.1 / E1.1b** — без изменения статуса.
4. Не стартовать повторный RERUN тех же 10 волн на том же SHA.

---
*При достижении exit-clean большинства волн или смене отбора — опубликовать `SYNTHESIS_FINAL_*.ru.md` и пометить этот PARTIAL superseded.*
