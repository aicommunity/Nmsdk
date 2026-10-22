# Controller v2 — входы DRAFT (обогащение 2026-10-22)

**Статус:** **DRAFT** (богаче каркаса [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md)), **не** C++ SPEC и **не** задание на реализацию. Цель документа — связать новые evidence 2026-10-22 с машиной состояний v2 и зафиксировать открытые решения до `CONTROLLER_V2_SPEC_*.ru.md`.

**Запрет этого arm:** не трогать Console, не стартовать cold/matrix/bisect, не конкурировать с D1 W02 на PulseLib `3cefd64` (HOST_LIMIT busy).

---

## 1. Новые библиотеки физики (E1.0 / E1.1 / E1.1b)

Постановка: этап 4 контроллера опирается на измеренную/предсказанную задержку и амплитуду одиночного EPSP; scoped-проходы E1 закрыли **частичную** замену полной сетки плана без cold Train.

| Библиотека | Вердикт | Что даёт v2 | Ссылки |
|------------|---------|-------------|--------|
| **E1.0** cable vs Console | **PARTIAL** | Gen amp bias ≈ **÷1.067** (Console ниже model); AsymRm peak **не** совпадает с пассивом → нужен **oracle ×≈1.46**; timing/FWHM на якорях OK | [`E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md`](E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md) |
| **E1.1** timing L=1…100 | **PARTIAL DONE** | δ ≈ **9.48** мс/сег (Gen), **9.96** мс/сег (AsymRm) — старт bracketed `LEN_SEARCH` | [`E1_1_TIMING_LIBRARY_2026-10-22.ru.md`](E1_1_TIMING_LIBRARY_2026-10-22.ru.md), TSV |
| **E1.1b** amp Rs×N | **PARTIAL DONE** | γ(L)≈const по TipR; рычаг amp = **log Rs / N**; насыщение **N ≳ 16** (эффективно N≲8…16) | [`E1_1b_RS_N_AMP_LIBRARY_2026-10-22.ru.md`](E1_1b_RS_N_AMP_LIBRARY_2026-10-22.ru.md), TSV |

**Следствие для скелета:** шаг `LEN_SEARCH` стартует из C2 + δ(E1.1); шаг `AMP_ALIGN` — бисекция log Rs и N с потолком кратности ~16; калибровка peak — Gen×1.067 / AsymRm oracle, не «сырой» passive cable.

Trainer×Mode для probe-библиотек **N/A** (IsNeedToTrain=0 / offline); Train/Test — N/A или probe-шаблоны W01/W02/W11 (см. E1.0).

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

## 3. D1 фаза 2 (контекст CL-N1, не финал)

На Classic×N1 W02 (`W02_CL480_N1_PSIoff`) фаза 2 поиска первого L₀≥54 **CLOSED**: lo=`5308aa5`(53) … hi=`3cefd64`(L=`100 72 1 1`, MaxL escape); **первый L₀≥54 = `3cefd64`**. Источник: [`D1_BISECT_2026-10-22.ru.md`](D1_BISECT_2026-10-22.ru.md). Для v2: `infeasible_len` / MaxL overshoot и hold TipR остаются кандидатами поведения на длинных Span; числа tol — отдельно от CL-N1 stall (долг ещё open).

---

## 4. Открытые решения v2 (явный список)

Эти пункты **блокируют** перевод DRAFT→SPEC (не блокируют дальнейшее обогащение docs):

1. **`candidate_mid` на Test:** когда включать `UseCandidateMidOnNonSeparableTest` (только NonSeparable? всегда при finite candidate? never default-on до V-gate)? Default-off сохраняет G1 silent; cold PASS на flag=1 доказан, но production policy не выбрана.
2. **TipR PostTune: KeepDone vs CanonRmin:** H2 **ослаблена** (overlay + KeepDone cold W33 после pin); `DEBT-17` done. SPEC не должен зафиксировать KeepDone(3) или Canon mode=1 как sole-fix silent thr=1.
3. **`sep_margin` Train emit (`DEBT-S0-cpp-fields` gap):** residue/Done_BE уже частичны; **sep_margin на Train всё ещё gate-only** — без C++ emit Verify/rollup v2 не сможет закрыть ворота «запас ≥ предсказанный − 2 п.п.» из offline-таблиц без повторного Test-gate.
4. **F1b → `FINE_DELAY`:** перенос `NAxoneDelay` в train loop vs только финальный verify — ждёт senior docs-ready (ниже) и cold; **`DEBT-F1b` OPEN**.
5. **N0 при Span > 50 мс / 480 мс:** C2 T_max и E1.1 δ остаются; решение «чистый N0 vs N1+delay» — после согласования с D1/CL-N1 и этапом 6.

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
| Числовые tol Done / margin / residual_dt | Из exit-clean G1 + E1 cal, не из drv-only |
| Default Test mid policy | Решение §4.1 |
| Default PostTrainTipResistanceMode | Решение §4.2: H2 **ослаблена** — не брать KeepDone(3) как sole-fix silent thr=1 |
| Train `sep_margin` emit | Закрытие gap `DEBT-S0-cpp-fields` |
| Псевдокод Branch reverse-order + topology strategy | После C2↔Console точечной сверки |
| F1b cold результат | Senior + PASS×3 margin |
| D1 L₀≥54 SHA | phase2 CLOSED: первый ≥54 = **`3cefd64`** (MaxL escape); см. `D1_BISECT_2026-10-22` |

См. также: скелет §7 [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md), PARTIAL [`SYNTHESIS_PARTIAL_2026-10-22.ru.md`](SYNTHESIS_PARTIAL_2026-10-22.ru.md) §Controller.
