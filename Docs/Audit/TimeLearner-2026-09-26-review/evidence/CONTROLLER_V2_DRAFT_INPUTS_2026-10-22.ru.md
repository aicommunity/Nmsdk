# Controller v2 — входы DRAFT (обогащение 2026-10-22)

**Статус:** **DRAFT** (богаче каркаса [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md)), **не** C++ SPEC и **не** задание на реализацию. Цель документа — связать evidence 2026-10-22 с машиной состояний v2 и зафиксировать открытые решения до `CONTROLLER_V2_SPEC_*.ru.md`. **`DEBT-CTRL-V2-DRAFT` остаётся open** до появления SPEC.

**Запрет этого arm:** не трогать Console, не стартовать cold/matrix/bisect, не G1 RERUN / F1b cold / KeepDone.

**Refresh SHA якорей (root `timelearner_fix2`):** E1.4 `e9a0808c8` · E1.5 `f9e83bf8c` · E1.1d `da88a998c` · E1.1e `2adf0cd35` · E1.1f offline Pack-A · **E1.1g Console Branch IR** (этот turn; proxy **не** retired) · F3 `e02f7bcaa` (PulseLib `4b85c91`) · CL-N1 HEAD ablations `6245a0c09` (PulseLib F6/F7 tip `a532db7`, defaults historical). Сводка кампании — [`SYNTHESIS_PARTIAL_2026-10-22.ru.md`](SYNTHESIS_PARTIAL_2026-10-22.ru.md) (**FINAL blocked**; `DEBT-CL-N1` open).

---

## 1. Новые библиотеки физики (E1.0 / E1.1 / E1.1b / E1.1d / E1.4 / E1.5)

Постановка: этап 4 контроллера опирается на измеренную/предсказанную задержку и амплитуду одиночного EPSP; scoped-проходы E1 закрыли **частичную** замену полной сетки плана без cold Train. После E1.5 критерий VERIFY обязан учитывать хрупкость острова PASS (~1–2% sep).

| Библиотека | Вердикт | Что даёт v2 | Ссылки / SHA |
|------------|---------|-------------|--------------|
| **E1.0** cable vs Console | **PARTIAL** | Gen amp bias ≈ **÷1.067** (Console ниже model); AsymRm peak **не** совпадает с пассивом → нужен **oracle ×≈1.46**; timing/FWHM на якорях OK | [`E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md`](E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md) |
| **E1.1** timing L=1…100 | **PARTIAL DONE** | δ ≈ **9.48** мс/сег (Gen), **9.96** мс/сег (AsymRm) — старт bracketed `LEN_SEARCH` | [`E1_1_TIMING_LIBRARY_2026-10-22.ru.md`](E1_1_TIMING_LIBRARY_2026-10-22.ru.md), TSV |
| **E1.1b** amp Rs×N | **PARTIAL DONE** | γ(L)≈const по TipR; рычаг amp = **log Rs / N**; насыщение **N ≳ 16** (эффективно N≲8…16) | [`E1_1b_RS_N_AMP_LIBRARY_2026-10-22.ru.md`](E1_1b_RS_N_AMP_LIBRARY_2026-10-22.ru.md), TSV |
| **E1.1d** NextSegInh/PSI | **PARTIAL** (`da88a998c`) | single-pulse AsymRm: PSI amp×~2.4 (FWHM≈pas); NextSeg ΔFWHM≈−9.5% @L=1, ≈pas @остров L=7 — **не** τ=0.5 мс; **не заменяет** E1.4 `ideal_inh_proxy` | [`E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.ru.md`](E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.ru.md), TSV |
| **E1.1e** multi-pulse tip IR | **PARTIAL / negative** | Pack-A ISI tip-drive: nextseg@L=7 ≈passive (last_fwhm~62–66 мс); **0/132** meet FWHM/span≲0.13; **не** retire proxy | [`E1_1e_MULTIPULSE_IR_2026-10-22.ru.md`](E1_1e_MULTIPULSE_IR_2026-10-22.ru.md), TSV |
| **E1.1f** 4-dendrite Pack-A | **PARTIAL / negative** | island L=`7 6 4 1`+TipR Pack-A: nextseg sep **−0.010 / −0.030** vs proxy **+0.074**; tgt_fwhm~58–68 мс; **не** retire proxy | [`E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.ru.md`](E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.ru.md), TSV |
| **E1.1g** Console Branch IR | **PARTIAL / negative** | Test-only TRACE @ island: nextseg FWHM **28.8–30.9 мс**, gen Acc **22.7 мс**, sep_soma **≈−0.015** ≫ proxy 2.1 мс / +0.074; **proxy intentional for SPEC** (`DEBT-E1.1f` partial-wontfix-offline) | [`E1_1g_CONSOLE_BRANCH_IR_2026-10-22.ru.md`](E1_1g_CONSOLE_BRANCH_IR_2026-10-22.ru.md), TSV |
| **E1.4** sep predictor | **PARTIAL** gate **6/6** (`e9a0808c8`) | офлайн `(tgt−max_foil)/tgt` по L/TipR/mod; gen→passive cable; nextseg/preinh→**`ideal_inh_proxy`** τ=0.5 мс при sync CV≤0.25; proxy **intentional** (E1.1d/e/f offline + E1.1g Console negative) | [`E1_4_SEPARABILITY_PREDICTOR_2026-10-22.ru.md`](E1_4_SEPARABILITY_PREDICTOR_2026-10-22.ru.md), TSV |
| **E1.5** fragility | **PARTIAL / FRAGILE** (`f9e83bf8c`) | Test-only L±1 / TipR×0.8/×1.25: br25_nextseg **0/9** strict; tiprmin TipR **0/2**; baseline `sep_ltz` **~1–2%** — tol VERIFY ≥ L±1 и TipR±25% | [`E1_5_FRAGILITY_2026-10-22.ru.md`](E1_5_FRAGILITY_2026-10-22.ru.md); `DEBT-E1.5-fragile-pass` |

**Следствие для скелета:** шаг `LEN_SEARCH` стартует из C2 + δ(E1.1); шаг `AMP_ALIGN` — бисекция log Rs и N с потолком кратности ~16; калибровка peak — Gen×1.067 / AsymRm oracle, не «сырой» passive cable. VERIFY может сверять Train `sep_margin` с E1.4-предсказанием, но **числовой tol SPEC** обязан учитывать E1.5 (остров ~1–2% sep; Done на граничном mid ложен) и **фиксирует `ideal_inh_proxy` как intentional** (E1.1d/e/f offline + E1.1g Console FWHM~29–31 мс ≫ 2.1 — **не** retire).

Trainer×Mode для probe-библиотек **N/A** (IsNeedToTrain=0 / offline); Train/Test — N/A или probe-шаблоны W01/W02/W11 (см. E1.0). E1.5 якоря — Branch×N1 tiprmin/nextseg с явными Train/Test в evidence.

---

## 2. Silent-Test гипотезы → контракт Verify/Test

Иерархия якоря: **Classic×N0** → Span **50** → NeuronModel **AsymRm / Classic** → Mod **gen** (W01/W13/W33 exit-clean); конфиги — `TimeLearnerMatrix/W0{1,13,33}/inputs/…/{Train,Test}` из G1.S1 bundles.

| Гипотеза | Статус 2026-10-22 | Вход в v2 DRAFT |
|----------|-------------------|-----------------|
| **H3** mid-policy | Flag `UseCandidateMidOnNonSeparableTest` **default-off**; cold **PASS** (flag=1 → fires=`01000101`) | Явный Test-threshold contract: при NonSeparable не оставлять только `FixedLTZ=1` | [`MID_POLICY_H3_COLD_2026-10-22.ru.md`](MID_POLICY_H3_COLD_2026-10-22.ru.md) |
| **H1** / **H1-weak** | Strong fail (target_hit=0 при candidate_mid); weak: thr=1 маскирует foil fires; W13/W33 replicate | VERIFY ≠ «silent Acc 7/8 = PASS»; ranking/margin обязателен | [`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md), [`SILENT_TEST_W13_W33_MID_2026-10-22.ru.md`](SILENT_TEST_W13_W33_MID_2026-10-22.ru.md) |
| **H4** sep_margin | **Ослаблена** как sole-cause flat CanonRmin | AMP_ALIGN дифференциальный Rs/N; Verify смотрит sep_margin | [`SILENT_TEST_H4_MARGIN_2026-10-22.ru.md`](SILENT_TEST_H4_MARGIN_2026-10-22.ru.md) |
| **H2** KeepDone vs CanonRmin | **Ослаблена** (TipR overlay thr=1 silent; KeepDone W33 после pin: TipR flat `86M×4`, Need=1, SKIP_GATE; `DEBT-17` done) | Не фиксировать KeepDone(3) / mode=1 как «чинит silent thr=1» в SPEC | [`SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md`](SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md), [`SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md`](SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md) |

Краткая связка: [`CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md`](CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md).

---

## 3. D1 фаза 2 + F3 Reset (контекст, не финал SPEC)

**D1 / CL-N1.** На Classic×N1 W02 (`W02_CL480_N1_PSIoff`) фаза 2 поиска первого L₀≥54 **CLOSED**: lo=`5308aa5`(53) … hi=`3cefd64`(L=`100 72 1 1`, MaxL escape); **первый L₀≥54 = `3cefd64`**. Источник: [`D1_BISECT_2026-10-22.ru.md`](D1_BISECT_2026-10-22.ru.md). **HEAD stage-2 ablations (`6245a0c09`):** base+(a–e) — **6/6** `not_converged_at_stop` (Need=1, L≈`53–54 44 1 1`); ни Rmin-floor / midband-off / tol×1 / γ-fixed / Reset **не** sole-fix — [`CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md`](CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md). Для v2: `infeasible_len` / MaxL overshoot и hold TipR остаются кандидатами поведения на длинных Span; числа tol — отдельно от CL-N1 stall (**`DEBT-CL-N1` open**).

**F3 / A5 (`e02f7bcaa`, PulseLib `4b85c91` + tip `3a599a7`).** Флаг `ResetNeuronBeforeTrainBurst` портирован на `timelearner_fix2` (Classic+Branch `BeginTrainingIteration`), **CODE default off**; матричные defaults не трогали. **`DEBT-F3-R8` done** — cold A/B flag=0 vs 1: Branch `br25_nextseg` без регрессии при flag=1; W01 Classic silent без изменения — [`F3_R8_AB_2026-10-22.ru.md`](F3_R8_AB_2026-10-22.ru.md). Для скелета §5.3: Reset остаётся **опциональным** (default off); E1.3 показал, что пауза ≤5 с не заменяет Reset.

---

## 4. Открытые решения v2 (явный список)

Эти пункты **блокируют** перевод DRAFT→SPEC (не блокируют дальнейшее обогащение docs). **`DEBT-CTRL-V2-DRAFT` notes refreshed** этим документом; **не закрывать** долг, пока нет `CONTROLLER_V2_SPEC_*.ru.md`.

1. **`candidate_mid` на Test (mid policy):** когда включать `UseCandidateMidOnNonSeparableTest` (только NonSeparable? всегда при finite candidate? never default-on до V-gate)? Default-off сохраняет G1 silent; cold PASS на flag=1 доказан, но **production policy ещё open**.
2. **TipR PostTune: KeepDone vs CanonRmin:** H2 **по-прежнему ослаблена** (overlay + KeepDone cold W33 после pin); `DEBT-17` done. SPEC **не** должен зафиксировать KeepDone(3) или Canon mode=1 как sole-fix silent thr=1.
3. **`sep_margin` / `amp_be` Train emit** — **CLOSED** (`DEBT-S0` done): C++ пишет `sep_margin`/`sep_gap`/`sep_tgt`/`sep_max_foil` + `amp_be`/`done_be` в Train audit + `posttune_complete.flag`; harness → `matrix_result.json` ([`S0_CPP_EMIT_2026-10-22.ru.md`](S0_CPP_EMIT_2026-10-22.ru.md)). **Числовой tol** «запас ≥ предсказанный − …» для SPEC **ещё open** и **обязан учитывать E1.5**: baseline sep острова ~**1–2%**; tol не должен съедать весь запас (согласуется с E1.2 eps_amp≈1%·target). Ideal_inh proxy E1.4 даёт более широкий margin (~7%), чем Console peaks — не путать proxy-margin с Console `sep_ltz`.
4. **F1b → `FINE_DELAY`:** перенос `NAxoneDelay` в train loop vs только финальный verify — ждёт senior docs-ready (§5) и cold; **`DEBT-F1b` OPEN**.
5. **N0 при Span > 50 мс / 480 мс:** C2 T_max и E1.1 δ остаются; решение «чистый N0 vs N1+delay» — после согласования с D1/CL-N1 и этапом 6.
6. **F3 Reset в train loop:** default-off CODE готов; A/B **`DEBT-F3-R8` done** (BR island OK / W01 silent unchanged) — включать ли Reset в v2 по умолчанию остаётся продуктовым выбором (рекомендация: оставить opt-in).
7. **`ideal_inh_proxy` intentional for SPEC (закрыто как измеренная замена):** E1.1d/e/f offline **и** E1.1g Console Branch IR (FWHM **28.8–30.9 мс** ≫ 2.1; sep_soma **≈−0.015**) — **retire=NO**; `DEBT-E1.1f` **partial-wontfix-offline**. SPEC nextseg/preinh держит τ=0.5 мс phenomenological; VERIFY-tol **не** из E1.1d–g FWHM/sep.

---

## 5. F1b — docs-ready checklist (без Console pilot)

**DEBT-F1b остаётся OPEN.** Cold / Console **не** стартовать, пока senior не утвердит пункты ниже. Канон карточки: [`F1_fast_epsp_pilot.md`](../plans/AGENT_PLAN_2026-10-20/cards/F1_fast_epsp_pilot.md) §F1b (+ чеклист в карточке).

| # | Что утвердить | Зачем |
|---|----------------|-------|
| 1 | Единицы и дискретизация `NAxoneDelay` (шаг ≥ 20 kHz) | Иначе d_k неразличим от FWHM |
| 2 | XML: Classic Test, 4× L=1 AsymRmD001C25e12 + delay на каждом пути; wiring check | Без нового типа конфига pilot невалиден |
| 3 | Порог mid: max(foil)…target по `ltz_potential`; два порядка паттернов | Критерий запаса 0.08 / 0.15 |
| 4 | Host/runtime: на `.17` держать pin glog **0.4** (`DEBT-17` done); не ломать pin при sync Console | Иначе снова EmitToGlog smash |
| 5 | Связь с v2: только verify vs train-loop `FINE_DELAY` | Решение §4.4 |

После approve — отдельный execute-arm; этот документ **не** является go-ahead на cold.

---

## 6. Что остаётся для SPEC (после DRAFT)

| Артефакт / пробел | Нужно для SPEC |
|-------------------|----------------|
| Числовые tol Done / margin / residual_dt | Из exit-clean G1 + E1 cal + **E1.5 fragility (~1–2% sep; L±1 / TipR±25%)**, не из drv-only |
| Default Test mid policy | Решение §4.1 — **ещё open** |
| Default PostTrainTipResistanceMode | Решение §4.2: H2 **ослаблена** — не брать KeepDone(3) как sole-fix silent thr=1 |
| Train `sep_margin` / `amp_be` emit | **DONE** (C+++harness; `DEBT-S0` closed); SPEC tol ещё open |
| Inh-ядра для nextseg/preinh | E1.1d/e/f offline + E1.1g Console **negative**; **`ideal_inh_proxy` intentional for SPEC** (`DEBT-E1.1f` partial-wontfix-offline) |
| F3 Reset default в v2 | A/B done (`DEBT-F3-R8`); CODE default off; opt-in recommended |
| Псевдокод Branch reverse-order + topology strategy | После C2↔Console точечной сверки |
| F1b cold результат | Senior + PASS×3 margin |
| D1 L₀≥54 SHA | phase2 CLOSED: первый ≥54 = **`3cefd64`** (MaxL escape); см. `D1_BISECT_2026-10-22` |

См. также: скелет §5–§7 [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md), PARTIAL [`SYNTHESIS_PARTIAL_2026-10-22.ru.md`](SYNTHESIS_PARTIAL_2026-10-22.ru.md) §Controller, TECH_DEBT `DEBT-CTRL-V2-DRAFT` / `DEBT-E1.5-fragile-pass` / `DEBT-F3-R8`.
