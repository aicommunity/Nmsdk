# SYNTHESIS_PARTIAL — TimeLearner AGENT_PLAN (2026-10-22)

**Статус:** PARTIAL (не FINAL). **`SYNTHESIS_FINAL` заблокирован:** после G1 RERUN только **3/13** волн `launch.exit=0`; новый RERUN тех же волн **не** стартовать. Политика exit — [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md). Оглавление-черновик — [`SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md`](SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md). Группировка — [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md).

## 0. Область и SHA

Кампания AGENT_PLAN 2026-10-20 на ветке `timelearner_fix2`. Cold-arm, вошедшие в G1-сводку: **E2 R8** (EQUIVALENT) и **G1 S1** (13 волн / 32 case, RERUN закрыт). Документ **не** смешивает S0/S2 E2-плечи с G1 S1 в одной доле PASS без колонки Arm.

**Якоря docs-refresh (root `timelearner_fix2`, после G1 PARTIAL):**

| Цепочка | SHA / tip | Evidence |
|---------|-----------|----------|
| CL-N1 HEAD stage-2 ablations | `6245a0c09` | [`CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md`](CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md) — **6/6** `not_converged_at_stop` |
| CL-N1 next arm W3on (`3cefd64` hyp) | docs + cold `CLN1.W3on-…19730` | [`CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md`](CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md) — MaxL `100 58 1 1`, **not** converged |
| PulseLib F6/F7 diagnostic flags | tip `a532db7` | opt-in Classic UProperty; **defaults = historical** (off / tol×4) |
| E1.4 sep predictor | `e9a0808c8` | gate **6/6** PARTIAL |
| E1.5 fragility | `f9e83bf8c` | **FRAGILE** PARTIAL |
| E1.1d / E1.1e / E1.1f / E1.1g | `da88a998c` / `2adf0cd35` / `18ddd803a` / `ab3abc329` | proxy **intentional for SPEC** (offline + Console IR negative) |
| F3 Reset CODE + R8 A/B | CODE `e02f7bcaa` / A/B `0755c31ca` (PulseLib `3a599a7`) | default **off**; [`F3_R8_AB_2026-10-22.ru.md`](F3_R8_AB_2026-10-22.ru.md) — **`DEBT-F3-R8` done** |
| Controller DRAFT inputs | refresh post-W3on / E0 | [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md) — SPEC blocked |
| CL-N1 next hypothesis | docs-ready only | [`CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md`](CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md) — H1 Span≠480 / H2 `infeasible_len` |
| Bin E0 `--train-param` | tip `bf3e82ffe` | whitelist ResetNeuron / EnableRmaxLengthEscape на `timelearner_fix2` |

G1 cold Console sha256 эпохи S1 — `745d6061…` / PulseLib `6d746ac` (F5 default off); CL-N1 ablations / W3on — Console `f88d1852…` на PulseLib tip с F3+F6/F7 (см. evidence CL-N1).

## 1. Ворота кампании

| Ворота | Статус |
|--------|--------|
| A0 env / refresh / Console | OK; `DEBT-A0-ctest` **done** (87/87); тег `tl-baseline-20261020` ещё **не** резан |
| A1 / A3 / B2 / C1 / C2_MATCH | закрыты или MATCH по evidence R/E1 |
| E1.0 cable vs Console soma-kernel | **PARTIAL** — [`E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md`](E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md) |
| E1.1 / E1.1b / E1.1c timing+amp | **PARTIAL** scoped libraries |
| E1.1d NextSegInh/PSI | **PARTIAL** — [`E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.ru.md`](E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.ru.md) |
| E1.1e multi-pulse tip IR | **PARTIAL / negative** — proxy не retired — [`E1_1e_MULTIPULSE_IR_2026-10-22.ru.md`](E1_1e_MULTIPULSE_IR_2026-10-22.ru.md) |
| E1.1f 4-dendrite Pack-A | **PARTIAL / negative** — nextseg sep −0.01/−0.03 vs proxy +0.074 — [`E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.ru.md`](E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.ru.md) |
| E1.2 repeatability Reset vs no-Reset | **PARTIAL** — [`E1_2_REPEATABILITY_2026-10-22.ru.md`](E1_2_REPEATABILITY_2026-10-22.ru.md) |
| E1.4 separability predictor | **PARTIAL** gate **6/6** — [`E1_4_SEPARABILITY_PREDICTOR_2026-10-22.ru.md`](E1_4_SEPARABILITY_PREDICTOR_2026-10-22.ru.md) |
| E1.5 historical PASS fragility | **PARTIAL / FRAGILE** — [`E1_5_FRAGILITY_2026-10-22.ru.md`](E1_5_FRAGILITY_2026-10-22.ru.md) |
| E2 R8 | EQUIVALENT — [`E2_R8_SYNTHESIS_2026-10-21.ru.md`](E2_R8_SYNTHESIS_2026-10-21.ru.md) |
| G1 exit-clean полная матрица | **не** пройдена: **3/13** волн `launch.exit=0` после RERUN |
| CL-N1 HEAD ablations (§этап 2) | **6/6 stall** — DEBT-CL-N1 **open** — [`CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md`](CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md) |
| CL-N1 W3on Arm A | MaxL phenotype **да**, Need=0 **нет** — [`CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md`](CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md) |
| CL-N1 H1 Span100 baseline | Train **`converged_need0`** — TipR@Rmax stall **480-specific** — [`CL_N1_H1_SPAN100_2026-10-22.ru.md`](CL_N1_H1_SPAN100_2026-10-22.ru.md) |
| F3 ResetNeuronBeforeTrainBurst | **CODE** default off; cold R8 A/B **done** (`0755c31ca`) — BR PASS no regress; W01 silent 0≡1 |
| Controller v2 DRAFT inputs | notes refreshed; **не** SPEC — `DEBT-CTRL-V2-DRAFT` open |
| TECH_DEBT P0 | silent-Test (H3 confirmed offline); **CL-N1 open** (480 TipR@Rmax; H1 Span100 Train OK); S0 **done**; G1-exit-gate **done** |

## 2. Trainer×Mode — системные выводы

**Classic×N0.** На Span 50 exit-clean волны **W01** (PostTune OFF) и **W33** (PostTune ON) стабильно сходятся Train (`converged_need0` / `converged_posttune_finalized`), но Test даёт **silent Acc=7/8, Цель=нет** на всех трёх rep ([`G1_S1_PARTIAL_METRICS_2026-10-22.ru.md`](G1_S1_PARTIAL_METRICS_2026-10-22.ru.md)). Offline mid-sweep на W01-15892 ([`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md)): при `candidate_mid≈0.00241` fires=`01000101` (Acc 4/8), при thr=1 — silent 7/8; **H3 подтверждена** (штатный путь маскирует soma-fire thr=1), сильный H1 (target_hit при candidate) **нет** (peak target &lt; candidate_mid). Span 100/480 (**W02**, **W31**) после RERUN — `launch_exit=1`.

**Classic×N1.** **W13** (HIST ltz50 gen) — единственная exit-clean N1-волна; та же silent 7/8 без цели. **W09** / **W12** / pack-волна **W37** после RERUN — `launch_exit=1`, доли PASS по ним в кампанию не входят. На Span **480** (`W02_CL480_N1_PSIoff`) фенотип stall **подтверждён на HEAD**: D1 phase2 CLOSED (первый L₀≥54 = `3cefd64`); stage-2 однофакторные абляции base+(a–e) — **все 6/6** `not_converged_at_stop`, Need=1, L≈`53–54 44 1 1`, TipR `1e10×2+86M×2` ([`CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md`](CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md)). Ни Rmin-floor, ни midband-off, ни tol×1, ни γ-fixed, ни Reset-before-burst **не** sole-fix. **Next arm W3on** (`EnableRmaxLengthEscape=1`, RUN `CLN1.W3on-…19730`): L сменился на **MaxL** `100 58 1 1` (как D1 @ `3cefd64`), Need=1 / `not_converged_at_stop` — гейт W3 после `a15f4eb` объясняет stall vs MaxL, но W3 **не** SoftCold-фикс ([`CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md`](CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md)). **H1 Span100** (`W02_CL100_N1_PSIoff`, W3=off, PostTune OFF, RUN `CLN1.H1.S100-…23399`): Train **`converged_need0`**, Need=0, L=`54 48 30 1`, TipR midband `2.88M×3+86M` — stall TipR@Rmax **не** воспроизводится на 100; `quality_fail` = silent-Test ([`CL_N1_H1_SPAN100_2026-10-22.ru.md`](CL_N1_H1_SPAN100_2026-10-22.ru.md)). **`DEBT-CL-N1` остаётся open** на оси 480.

**Branch×N0 / Branch×N1.** Ни одна Branch-волна отбора не стала exit-clean после RERUN. **W04** — единственная с `launch_exit=2`; остальные Branch HIST / FastSpan (**W08**, **W10**, **W11**, **W48**) — `launch_exit=1`. Остров nextseg/preinh vs silent gen из более ранних boundary-map **не** перепроверен на exit-clean G1 S1 (нет clean Branch-волн). E1.5 показал, что исторический PASS-остров Branch×N1 **FRAGILE** (br25_nextseg 0/9 strict; tiprmin TipR 0/2; sep ~1–2%).

## 3. Таблица результатов (PARTIAL)

Канон строк G1: [`G1_S1_PARTIAL_METRICS_2026-10-22.tsv`](G1_S1_PARTIAL_METRICS_2026-10-22.tsv). Кратко exit-clean (rep3):

| Trainer×Mode | Span | NeuronModel | Mod | PostTune | Case | Acc | Цель | Train | Test |
|--------------|------|-------------|-----|----------|------|-----|------|-------|------|
| Classic×N0 | 50 | AsymRm | gen | OFF | W01_CL50_N0_PSIoff | 7/8 | нет | [`W01/…/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train) | [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test) |
| Classic×N1 | 50 | AsymRm | gen | OFF | W13_HIST_ltz50_gen | 7/8 | нет | [`W13/…/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W13/inputs/W13_HIST_ltz50_gen/Train) | [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W13/inputs/W13_HIST_ltz50_gen/Test) |
| Classic×N0 | 50 | AsymRm | gen | ON | W33_CL50_N0_PSIoff_POST | 7/8 | нет | [`W33/…/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Train) | [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Test) |

Остальные 29 case-строк TSV несут `failure_class=launch_exit_1|2` и Acc/Цель = `—`.

**CL-N1 HEAD ablations (не exit-clean G1; отдельный arm):** Classic×N1 → Span **480** → AsymRm → PSIoff → PostTune OFF; Train/Test — [`W02_CL480_N1_PSIoff/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train); все шесть RUN — SKIP_GATE / `not_evaluated_training_incomplete` — TSV [`CL_N1_HEAD_ABLATIONS_2026-10-22.tsv`](CL_N1_HEAD_ABLATIONS_2026-10-22.tsv).

**CL-N1 W3on next arm:** тот же Trainer×Mode/Span/Mod; overlay `EnableRmaxLengthEscape=1` → L=`100 58 1 1`, Need=1 — [`CL_N1_NEXT_ARM_3CEFD64_2026-10-22.tsv`](CL_N1_NEXT_ARM_3CEFD64_2026-10-22.tsv).

**CL-N1 H1 Span100:** Classic×N1 → Span **100** → AsymRm → PSIoff → PostTune OFF; Train/Test — [`W02_CL100_N1_PSIoff/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Train); `converged_need0` / Need=0 — TSV [`CL_N1_H1_SPAN100_2026-10-22.tsv`](CL_N1_H1_SPAN100_2026-10-22.tsv).

## 4. C2 vs Console (G1)

Полное сопоставление 32 case **отложено**. Для exit-clean тройки допустима точечная сверка с [`G1_predictions_2026-10-21.tsv`](G1_predictions_2026-10-21.tsv) / [`G1_vs_C2_2026-10-21.tsv`](G1_vs_C2_2026-10-21.tsv) без экстраполяции на non-exit волны. Расхождения oracle vs silent на W01/W13/W33 остаются в зоне DEBT detection/mid, не infra.

## 5. Точечные фиксы F1–F8 и физика E1

F2/F3/F4/F6 cold закрыты без регрессии Train на своих пилотах; **F5** — OPEN: paired γ=0 vs γ=1 на `W01_CL50_N1_PSIoff` ([`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md)) — оба плеча Need=0, **идентичный** silent 7/8, PASS **нет**. F7 → F2.pref; F8 done. Silent Test **не** зачтён как PASS ни на одном фиксе.

**F3 / DEBT-F3-R8 (`0755c31ca`):** `ResetNeuronBeforeTrainBurst` портирован (Classic+Branch), **CODE default off**; матричные defaults не трогали. Cold A/B W01 + `br25_nextseg` — flag 0≡1: Branch Acc 8/8 / Цель да без регрессии; Classic W01 Need=0 + silent 7/8 на обоих ([`F3_R8_AB_2026-10-22.ru.md`](F3_R8_AB_2026-10-22.ru.md)). **`DEBT-F3-R8` done.** На CL-N1 Span480 overlay Reset=1 **не** снял stall (абляция e).

**PulseLib F6/F7 (`a532db7`):** runtime-свойства `PreferConfiguredResistanceMinFloor` / `DisableMidbandWalkToRmin` / `RminLengthTolFactor` — opt-in, **defaults historical**; без overlay поведение бит-в-бит как до флагов. На W02 N1 абляции a/b/c с флагами **не** вернули `converged*`.

**E1 chain (docs-ready / offline, без нового G1 RERUN):** E1.4 предсказатель Acc-direction **6/6** на passive cable + `ideal_inh_proxy` τ=0.5 мс; E1.1d/e/**f** (single-pulse / tip multi-pulse / 4-dendrite Pack-A) **не** заменяют proxy; E1.5 задаёт хрупкость VERIFY-tol (~1–2% sep; L±1 / TipR±25%).

## 6. Controller v2 и этап 5–6

Скелет — [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md). Обогащённые входы 2026-10-22 (E1.0–E1.5, H3/H1/H4/H2, D1 `3cefd64`, **W3on MaxL≠fix**, **H1 Span100 converged**, F3-R8 A/B done, Bin tip `e49a52bf`, open decisions mid/KeepDone/proxy/F1b/`infeasible_len`; Train `sep_margin` emit **CLOSED**) — [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md). **SPEC blocked**; решение «432 v1 vs v2» и V-gate этапов 4–6 **не** блокируются ожиданием 13/13 exit-clean, но **не** опираются на drv-only SERIES_DONE; F1b senior (`DEBT-F1b`) по-прежнему блокер физики быстрого EPSP до SPEC. **`DEBT-CTRL-V2-DRAFT` open** до `CONTROLLER_V2_SPEC_*.ru.md`. CL-N1 на **480** после a–e + W3on **не** закрыт; H1 cold на 100 **DONE** (Train OK) — дальше H2 docs / 480 policy.

## 7. Риски и следующий цикл

1. **`SYNTHESIS_FINAL` не публиковать**, пока нет exit-clean большинства волн или явной смены отбора; не стартовать повторный RERUN тех же 10 волн на том же SHA.
2. **DEBT-CL-N1 open (480):** a–e не sole-fix; W3on **MaxL≠fix**; H1 показал, что на Span **100** Train сходится (`converged_need0`) — TipR@Rmax stall **480-specific** ([`CL_N1_H1_SPAN100_2026-10-22.ru.md`](CL_N1_H1_SPAN100_2026-10-22.ru.md)). Не включать W3 в SoftCold; дальше — H2 `infeasible_len` docs / policy на 480 ([`CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md`](CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md)). Bin tip `e49a52bf`.
3. **DEBT-G1-exit-gate** harness **done**; исторический G1 остаётся 3/13 exit-clean.
4. **F5** — paired W01 N1 выполнен (γ noop); следующий шаг — другой case/span или mid-диагностика, не повтор W01 без гипотезы.
5. Алгоритм: Train **`sep_margin` / `amp_be` emit** закрыт (`DEBT-S0` **done**). H3 mid-policy **зафлажена и cold-verified**. **H4 / H2 ослаблены**. **D1 phase2 CLOSED** (`3cefd64`). **`ideal_inh_proxy` intentional for SPEC** (E1.1d–g negative). **F3-R8 done** (Reset default off; BR OK / W01 silent unchanged).
6. Controller SPEC tol обязан учитывать E1.5 FRAGILE; открытые блокеры: **CL-N1**, **F5**, **F1b senior**, тег **tl-baseline**, **`DEBT-CTRL-V2-DRAFT`**; KeepDone / новый Console cold — только по явному arm.

---
*При достижении exit-clean большинства волн или смене отбора — опубликовать `SYNTHESIS_FINAL_*.ru.md` и пометить этот PARTIAL superseded. До тех пор FINAL остаётся blocked.*
