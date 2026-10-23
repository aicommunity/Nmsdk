# Controller v2 — SPEC DRAFT (2026-10-23)

**Статус:** **SPEC DRAFT** — продвижение каркаса [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md) и входов [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md) в форму спецификации. Документ **ещё не FINAL SPEC**: открытые продуктовые решения (§8) оставляют **`DEBT-CTRL-V2-DRAFT` open** до `CONTROLLER_V2_SPEC_FINAL_*.ru.md` (или эквивалентного senior-approved FINAL). **Не** является заданием на реализацию в C++ и **не** go-ahead на cold Console.

**Постановка.** Этап 4 аудита TimeLearner требует одного контроллера Classic+Branch за флагом `ControllerVersion=2`, с разведёнными шагами поиска длины, выравнивания амплитуды, тонкой задержки, verify и калибровки mid. Evidence 2026-10-22 (E1 библиотеки, silent-Test H*, D1/CL-N1, F3-R8) достаточно, чтобы зафиксировать **нормативные** контракты exit-классов `LEN_SEARCH` и ряд intentional-политик; числовые tol Done/margin и production mid-policy ещё не закрыты — поэтому статус остаётся DRAFT относительно FINAL. Обогащение 2026-10-23 (этот arm, без cold): guidance по VERIFY/Done tol из E1.5 FRAGILE и явный список **опций** mid production policy из H3 — без объявления FINAL и без фиксации одного production-выбора.

**Запрет этого arm:** не трогать Console, не стартовать cold/matrix/bisect, не G1 RERUN / F1b cold / KeepDone; не править C++/PulseLib под этот документ.

**Опора (не drv-only SERIES_DONE):** G1 PARTIAL 3/13 exit-clean — [`G1_S1_PARTIAL_METRICS_2026-10-22.ru.md`](G1_S1_PARTIAL_METRICS_2026-10-22.ru.md), [`SYNTHESIS_PARTIAL_2026-10-22.ru.md`](SYNTHESIS_PARTIAL_2026-10-22.ru.md); CL-N1 hyp — [`CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md`](CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md).

---

## 1. Цели и ворота этапа 4

Текущее ядро v1 смешивает в одной пачке калибровку mid, оценку задержки, шаг по длине и решение о Done; это даёт ложные exact Done (F7/RminTol), «сходимость» при silent Test и неустойчивый запас 2–6% на границе разделимости. Controller v2 **обязан** разделить физически достижимую цель \(A^\*\) от локального пика на коротком L, явно классифицировать исходы `LEN_SEARCH` (не смешивать TipR@Rmax stall с silent-Test) и согласовать порядок входов Branch с той же машиной состояний, что у Classic.

**Ворота этапа 4 (из аудита, без ослабления в этом DRAFT):** в области, которую офлайн-предсказатель (C2/F1a/E1.4) считает допустимой, доля exact Done ≥ 90%, среднее число пачек до Done не хуже v1, запас не ниже предсказанного минус 2 п.п. — **при условии**, что числовой tol VERIFY учитывает E1.5 fragility (§5). Финальная численная подгонка tol — блокер FINAL (§8).

**Канон:** один общий контроллер для Classic и Branch за `ControllerVersion=2`; стратегия топологии вместо двух независимых копий тренера.

---

## 2. Нормативные входы (зафиксировано evidence)

Постановка: нижеперечисленные библиотеки и гипотезы **входят в SPEC DRAFT как обязательные входы** машины состояний; Trainer×Mode для probe-библиотек E1 — N/A (IsNeedToTrain=0 / offline), если не указано иное.

| Источник | Нормативный вклад в v2 | Статус evidence |
|----------|------------------------|-----------------|
| **C2** sync table | Старт bracketed `LEN_SEARCH`; `feasible=false` при L>MaxL | карточка C2 |
| **E1.0 / E1.1 / E1.1b** | δ≈9.48 (Gen) / 9.96 (AsymRm) мс/сег; amp Gen÷1.067, AsymRm oracle×≈1.46; рычаг amp = log Rs / N, N≲8…16 | PARTIAL |
| **E1.4** | VERIFY может сверять Train `sep_margin` с предсказанием; nextseg/preinh → **`ideal_inh_proxy`** τ=0.5 мс | PARTIAL gate 6/6 |
| **E1.5** | Tol VERIFY **обязан** учитывать хрупкость острова PASS (~1–2% sep; L±1, TipR±25%) | PARTIAL / FRAGILE |
| **E1.1d/e/f + E1.1g** | Proxy **не** retire; VERIFY-tol **не** из Console FWHM~29–31 мс / sep_soma≈−0.015 | negative / intentional |
| **H3 mid** | `UseCandidateMidOnNonSeparableTest` **default-off**; VERIFY ≠ silent Acc 7/8 = PASS | cold PASS flag=1 |
| **H2 KeepDone** | **Не** sole-fix silent thr=1; не фиксировать KeepDone(3)/Canon mode=1 как чинит silent | ослаблена |
| **H4 sep_margin** | Ослаблена как sole-cause; AMP_ALIGN дифференциальный Rs/N; Verify смотрит ranking/margin | ослаблена |
| **S0 emit** | Train `sep_margin`/`amp_be`/`done_be` в audit + harness — **DONE** (`DEBT-S0`) | closed |
| **F3 Reset** | `ResetNeuronBeforeTrainBurst` **opt-in**, CODE default off (`DEBT-F3-R8` done) | A/B safe/noop |
| **W3** | `EnableRmaxLengthEscape` **не** SoftCold default; diagnostic opt-in | W3on MaxL≠fix |
| **D1 / CL-N1** | Первый L₀≥54 = `3cefd64`; Span480 TipR@Rmax stall **open**; H1 Span100 Train `converged_need0` | 480 open |

Иерархия якорей silent-Test: **Classic×N0** → Span **50** → AsymRm → Mod **gen** — Train/Test `TimeLearnerMatrix/W0{1,13,33}/inputs/…/{Train,Test}`.  
Иерархия CL-N1: **Classic×N1** → Span **480** vs **100** → AsymRm → PSIoff → PostTune OFF — [`W02_CL480_N1_PSIoff/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train), [`W02_CL100_N1_PSIoff/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Train).

---

## 3. Машина состояний v2 (SPEC DRAFT)

Для **каждого входа** (Branch — в обратном порядке относительно v1, если сохраняется текущая семантика входов):

| Шаг | Состояние | Действие | Выход / переход |
|-----|-----------|----------|-----------------|
| 1 | `LEN_SEARCH` | Bracketed integer search L\* по **измеренной** задержке; старт из C2 + δ(E1.1) | `L*` **или** один из exit-классов §4 |
| 2 | `AMP_ALIGN` | При фиксированном L\* — бисекция/секущие по log Rs (N0: по N); цель \(A^\* = \min_k A_{\max}(k)\); потолок кратности N ~16 | Rs/N на входе |
| 3 | `FINE_DELAY` | Остаток dt после L\* — Rs в пределах amp-tol **или** аксонная задержка (**F1b**, senior blocked) | residual_dt |
| 4 | `VERIFY` | Verify-проход со всеми входами; учёт E1.4 predictor + E1.5 fragility; foil ≠ Test (Stage0) | pass / один повтор цикла / не silent-as-PASS |
| 5 | `MID_CALIB` | Mid на калибровочных foil со смещением к цели (напр. 0.75·gap), **без** CanonRmin как sole path | threshold |

**Отличия от v1 (намеренные, нормативны в DRAFT):** measured delay — источник истины для Done (F2); RminTol не маскирует exact Done (F7 → только `Done_BE`); пол Rmin из XML/устойчивости (F6), без midband→Rmin скачка; Test mid policy — явный контракт (§6), не «Acc 7/8 при thr=1 = PASS».

---

## 4. `LEN_SEARCH` — нормативные exit-классы (H2 §4.5a → SPEC DRAFT)

Постановка: после H1 Span100 (`converged_need0`) и W3on MaxL-hold на Span480 контроллер v2 **не** должен смешивать train-stall TipR@Rmax с silent-Test на уже сошедшем Train. Нижеследующая таблица — **нормативный acceptance wording** для SPEC DRAFT (перенос из DRAFT INPUTS §4.5a). Источник критериев: [`CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md`](CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md) §H2; evidence H1 / W3on / HEAD ablations. Закрытие `DEBT-CL-N1` на оси **480** требует принятия этих классов в FINAL SPEC (или senior close), **не** повторного multifactor / G1 RERUN.

| Exit-класс (**норматив SPEC DRAFT**) | Когда выставлять | Не путать с | Evidence |
|--------------------------------------|------------------|-------------|----------|
| **`bounded_stall_rmax`** | W3=off, Need≠0, TipR@`Rmax`/`1e10`, `not_converged_at_stop`, L₀ в corridor без MaxL-escape | SoftCold `quality_fail`; «универсальный Classic×N1 fail» | HEAD a–e на Span**480** |
| **`maxl_hold` / `infeasible_len`** | L достигло MaxL **и** Need≠0 (в т.ч. W3on escape) | `bounded_stall_rmax` (разный tip-класс); silent-Test | W3on `L=100 58 1 1` Need=1 |
| **`quality_fail` / silent-Test (`DEBT-D2`)** | Train `converged_need0` (Need=0), Test silent / nonseparable / fires≈0 | любой `infeasible_len` / stall@Rmax | H1 Span**100**; F5 Span100 γ noop |
| **SoftCold PASS** | Need=0 **и** Test target_hit / Acc цель | Acc 7/8 при silent thr=1 | **не** закрывать CL-N1 этим классом на 480 |

**Policy (норматив DRAFT → обязателен в FINAL без ослабления):**

1. W3 (`EnableRmaxLengthEscape`) = **opt-in diagnostic**, **не** SoftCold default; не sole-fix CL-N1(480).
2. C2 `T_max` + E1.1 δ остаются входом `LEN_SEARCH`.
3. Shorter-span Need=0+silent **не** эскалировать в `infeasible_len`.
4. Multifactor a–c на Span100 **не** планировать ради train stall (Train уже сходится на H1).

**Вывод.** H2 acceptance wording в этом документе считается **нормативным для SPEC DRAFT**; перевод в FINAL SPEC блокируется остальными решениями §8 (в т.ч. senior/policy close CL-N1@480), а не отсутствием формулировок exit-классов.

---

## 5. VERIFY / Done — numeric tol guidance (E1.5; ещё не FINAL thresholds)

Постановка: шаг `VERIFY` и критерий exact/`Done_BE` обязаны опираться на измеренный запас разделимости и на хрупкость исторического PASS-острова. Ниже — **нормативный guidance** для SPEC DRAFT (вход в формулу FINAL), а не закрытые числа порогов. Источник fragility: [`E1_5_FRAGILITY_2026-10-22.ru.md`](E1_5_FRAGILITY_2026-10-22.ru.md) (Test-only L±1 / TipR×0.8/×1.25; вердикт **FRAGILE**).

### 5.1 Различать proxy-margin и Console `sep_ltz`

1. **`ideal_inh_proxy` intentional (не регрессировать).** Для nextseg/preinh при sync CV≤0.25 E1.4 использует phenomenological τ=0.5 мс. E1.1d/e/f offline и E1.1g Console Branch IR (FWHM **28.8–30.9 мс** ≫ 2.1; sep_soma **≈−0.015**) — **retire=NO**; `DEBT-E1.1f` = partial-wontfix-offline. VERIFY-tol **не** строить из E1.1d–g FWHM/sep.
2. **Два разных «margin».** E1.4 `ideal_inh_proxy` даёт **proxy-margin ~7%** на офлайн-предсказателе; Console peaks / `ltz_potential_max` на живом острове дают **`sep_ltz` ~1–2%** (tiprmin ≈+1.77%, br25_nextseg ≈+1.11%). SPEC **обязан** явно различать эти величины: порог Done/VERIFY, завязанный на proxy ~7%, **не** означает, что Console `sep_ltz` уже имеет такой же запас. Смешивать proxy-margin с `sep_ltz` в одной формуле tol без пересчёта — запрещено в DRAFT wording.

### 5.2 Остров PASS ~1–2%; tol не съедает весь запас

3. **Масштаб острова.** Baseline Console `sep_ltz` на исторических PASS (Branch×N1 tiprmin / nextseg) лежит в полосе **~1–2%**. Это и есть практический «бюджет» разделимости на границе, с которым конкурирует любой числовой tol Done/VERIFY.
4. **Не съедать margin.** Числовой tol SPEC (ещё open, §8) **не должен** быть сопоставим со всем островом: допуск порядка E1.2 **eps_amp≈1%·target** уже сравним с `sep_ltz` ~1–2%, поэтому tol, который «съедает» весь запас, делает exact Done на граничном mid **ложным**. Guidance: оставлять несъеденный остаток margin после tol (конкретная формула «≥ predicted − Δ» — блокер FINAL).
5. **Emit готов, пороги нет.** C++/`posttune_complete` уже пишут `sep_margin`/`amp_be`/`done_be` (`DEBT-S0` done); финальная подгонка порога — open до exit-clean G1 + cal E1 + senior approve чисел.

### 5.3 Survive L±1 и TipR±25% (E1.5 FRAGILE)

6. **Критерий устойчивости (guidance → обязанность FINAL).** Done/VERIFY **обязан** требовать запас, достаточный, чтобы режим **переживал** единичный сдвиг **L±1** по входу и глобальный масштаб **TipR ±25%** (×0.8 / ×1.25), иначе Done на граничном mid без учёта fragility считается ложным. Evidence: br25_nextseg — **0/9** strict PASS под любым из этих возмущений; tiprmin — TipR-scale **0/2**, часть L-осей (L1+1, L2−1, L3+1) тоже ломает selective.
7. **Частичная устойчивость ≠ отсутствие требования.** tiprmin терпимее к L0±1 и части L1/L2 (5/9 strict hold), но это **не** отменяет требование «survive L±1 / TipR±25%» для tol: хрупкий nextseg-остров показывает нижнюю границу, на которую должен ориентироваться критерий VERIFY в v2.
8. **sep>0 при silent.** На E1.5 часто `sep_ltz>0` при fires=`00000000` после L-сдвига — FixedLTZ оказывается не в середине tgt/foil. Поэтому VERIFY смотрит **ranking/fires/margin**, а не один знак `sep_ltz`.

**Вывод §5.** Guidance по tol в SPEC DRAFT зафиксирован (остров ~1–2%; не съедать margin; survive L±1/TipR±25%; proxy ≠ `sep_ltz`; proxy intentional). **Числовые константы порогов остаются блокером FINAL** (§8 #2), а не закрываются этим разделом.

---

## 6. Test mid / TipR / Reset / W3 (норматив политики DRAFT)

| Тема | Норматив SPEC DRAFT | Что ещё open для FINAL |
|------|---------------------|-------------------------|
| **Mid policy (H3)** | Flag `UseCandidateMidOnNonSeparableTest` **default-off**; при NonSeparable restore fires доказан; silent Acc 7/8 ≠ PASS — см. §6.1 | **Production policy** — список опций §6.1, выбор **OPEN** |
| **KeepDone / CanonRmin** | KeepDone(3) / mode=1 **не** sole-fix silent thr=1; H2 silent-ось ослаблена (`DEBT-17` done); silent evidence: [`SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md`](SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md), [`SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md`](SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md) | Default `PostTrainTipResistanceMode` для v2 |
| **F3 Reset** | **Opt-in**; CODE default off; A/B: BR island OK, W01 silent unchanged | Продуктовый default в v2 XML (рекомендация: оставить off) |
| **W3** | Не SoftCold default; не sole-fix 480 | — (закрыто как policy в DRAFT) |
| **F1b → аксонный тренер / `FINE_DELAY`** | Стратегия 23.10: F1b **не** блокер дендритного FINAL; фаза A после ворот H0 (τ via Cm). Checklist DRAFT INPUTS §5 + [`STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md`](STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md) | **`DEBT-F1b` OPEN** (фаза A); дендритный FINAL: mid/tol/CL-N1@480 |

### 6.1 Mid policy — default-off, H3 restore, production options (OPEN)

Постановка: silent-Test на Classic×N0 Span50 AsymRm/gen (W01 и реплики W13/W33) показал, что при NonSeparable штатный path оставляет `FixedLTZ=PostTrainSilentThreshold` (1.0) и даёт Acc 7/8 при fires=`00000000`, тогда как finite `candidate_mid` честно поднимает foil fires. Это меняет **честность фенотипа**, но **не** восстанавливает Цель (H1 strong fail: peak target &lt; candidate_mid). Источники: [`MID_POLICY_H3_2026-10-22.ru.md`](MID_POLICY_H3_2026-10-22.ru.md), [`MID_POLICY_H3_COLD_2026-10-22.ru.md`](MID_POLICY_H3_COLD_2026-10-22.ru.md), [`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md), [`SILENT_TEST_W13_W33_MID_2026-10-22.ru.md`](SILENT_TEST_W13_W33_MID_2026-10-22.ru.md), [`CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md`](CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md).

**Уже нормативно в SPEC DRAFT (не ослаблять):**

1. **`UseCandidateMidOnNonSeparableTest` default-off** — CODE/XML default остаётся `0`; G1 silent thr=1 при flag=0 сохраняется как известный baseline.
2. **Когда NonSeparable + flag=1:** cold PASS доказал restore: `FixedLTZ`/`mid` ← `candidate_mid` (≈0.00241 на W01), fires=`01000101`, Acc 4/8, Цель нет, `PostTuneResult` остаётся NonSeparable (`result=2`), `test_mid_policy=candidate`. VERIFY **не** трактует silent Acc 7/8 при thr=1 как selectivity PASS.
3. **KeepDone не sole-fix** silent thr=1; **не** фиксировать KeepDone(3)/Canon mode=1 как «чинит» silent (см. таблицу выше).
4. **H2 `LEN_SEARCH` exit-классы §4 уже нормативны** — mid-policy arm **не** регрессирует и не переписывает wording `bounded_stall_rmax` / `maxl_hold` / `quality_fail` / SoftCold PASS.

**Production policy — OPEN; явные опции для FINAL (выбрать одну или зафиксировать V-gate комбинацию):**

| Опция | Смысл | За / против (evidence) |
|-------|--------|-------------------------|
| **A. Только NonSeparable** | Включать flag=1 **только** когда Test уже NonSeparable / silent-mid path; иначе default-off | Ближе к текущему флагу; честный phenotyp без смены result; не чинит Цель (H1) |
| **B. Always finite candidate** | Всегда подставлять finite `candidate_mid` на Test, даже вне NonSeparable | Максимальная «честность» mid; риск сдвинуть PASS-острова и SoftCold; **не** доказано cold |
| **C. Never default-on до V-gate** | Production/SoftCold держит flag=0, пока отдельный V-gate (margin/fires/ranking) не одобрит opt-in | Сохраняет G1 comparable; требует явного gate-контракта в FINAL |
| **D. Diagnostic-only** | Flag=1 только в harness/overlay diagnostic; никогда в SoftCold default XML | Минимальный риск регрессии; silent Acc 7/8 остаётся в поле до `DEBT-D2` |

**Вывод §6.1.** Default-off и cold restore при NonSeparable **закрыты как факт evidence**; **какая опция A–D (или смесь C+A) станет production** — блокер FINAL (§8 #1). Этот SPEC DRAFT **не** выбирает опцию.

---

## 7. Конфигурация и совместимость

- Флаг: `ControllerVersion=2` (XML Train + fingerprint очереди).
- Classic и Branch: **одна** реализация + стратегия топологии.
- PostTune: вне scope этапа 4 как алгоритм; пары ON/OFF — только `--force-posttrain-tuning` (скилл structtrain-experiments).
- Отчётность: exact / `Done_BE` / Need, residue, margin, fires, Acc — Stage0; плюс **нормативные** exit-классы §4 в harness/rollup (конкретные имена полей JSON — детали реализации, не блокер формулировок).
- Bin tip с E0 `--train-param` whitelist (Reset, W3, …) — overlays attempt-local без патча `matrix.json`.

---

## 8. Что блокирует FINAL SPEC (`DEBT-CTRL-V2-DRAFT` остаётся open)

Постановка: SPEC DRAFT **продвигает** прогресс (H2 exit-классы нормативны; intentional proxy; mid default-off + H3 restore; KeepDone не sole-fix; F3 opt-in; W3 не SoftCold default; F1b senior-blocked явно; **tol guidance §5** и **опции mid §6.1** зафиксированы без выбора FINAL чисел/опции). Ниже — решения, без которых **нельзя** объявлять `CONTROLLER_V2_SPEC_FINAL` и закрывать `DEBT-CTRL-V2-DRAFT`.

| # | Блокер FINAL | Почему |
|---|--------------|--------|
| 1 | **Mid policy production** | Default-off и cold PASS на flag=1 доказаны; **выбор опции A–D §6.1** (или V-gate смесь) — open |
| 2 | **Числовой tol** Done / margin / residual_dt / VERIFY | Guidance §5 есть (остров ~1–2%; не съедать margin; survive L±1/TipR±25%; proxy ≠ `sep_ltz`); **константы порогов** ещё нет (нужны exit-clean G1 + E1 cal + senior) |
| 3 | **F1b senior** (`DEBT-F1b`) — **фаза A (аксоны)** | **Уточнение 23.10:** не блокер **дендритного** FINAL SPEC; отдельный аксонный тренер после ворот H0. Docs-ready checklist сохраняется; cold только senior + (H0 done \| override) |
| 4 | **CL-N1@480 senior/policy close** | Exit-классы §4 нормативны в DRAFT; долг на 480 open до принятия в FINAL / senior close (не через multifactor) |
| 5 | *(вторично)* Default TipR PostTune mode; псевдокод Branch reverse-order + topology после C2↔Console сверки; N0 для span>50 | Не блокируют формулировку §4/§5/§6.1, но нужны для полной миграции v1→v2 |

**Не блокеры FINAL (уже зафиксированы в этом DRAFT):** формулировки `bounded_stall_rmax` / `maxl_hold`/`infeasible_len` / `quality_fail`/`DEBT-D2` / SoftCold PASS; intentional `ideal_inh_proxy`; KeepDone ≠ sole-fix; F3 opt-in; W3 ≠ SoftCold default; Train `sep_margin` emit; E1.5 tol **guidance** (без чисел); mid default-off + список production-опций.

**Вывод.** `DEBT-CTRL-V2-DRAFT` **остаётся open** со ссылкой на этот файл; закрытие — только после FINAL SPEC (или явного senior supersede). Cold / C++ под этот документ **не** стартовать.

---

## 9. Связанные артефакты

| Документ | Роль |
|----------|------|
| [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md) | Каркас FSM (superseded по статусу этим SPEC DRAFT) |
| [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md) | Полные входы E1/H*/D1/F*; §4.5a исходник wording |
| [`CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md`](CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md) | Mid + margin связка |
| [`E1_5_FRAGILITY_2026-10-22.ru.md`](E1_5_FRAGILITY_2026-10-22.ru.md) | Остров ~1–2%; L±1 / TipR±25% FRAGILE → §5 |
| [`MID_POLICY_H3_COLD_2026-10-22.ru.md`](MID_POLICY_H3_COLD_2026-10-22.ru.md) | Cold flag=1 restore → §6.1 |
| [`CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md`](CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md) | H1 executed; H2 → §4 этого документа |
| [`F5_GAMMA_SPAN100_2026-10-22.ru.md`](F5_GAMMA_SPAN100_2026-10-22.ru.md) | Опциональный cross-link: Span100 γ noop / `quality_fail` (tip без F5 symbol; `DEBT-F5-gamma` open) |
| [`F5_GAMMA_LIVE_OFFLINE_COMPARE_2026-10-23.ru.md`](F5_GAMMA_LIVE_OFFLINE_COMPARE_2026-10-23.ru.md) | Опциональный cross-link (sibling arm): live vs offline γ compare — **не** вход в tol/mid этого DRAFT |
| [`TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md) | `DEBT-CTRL-V2-DRAFT` / `DEBT-CL-N1` / `DEBT-F1b` (фаза A) / `DEBT-H0-tau-cm` / `DEBT-E1.5` |
| [`STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md`](STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md) | τ(Cm) per Span → аксоны; F1b не отменён |
| [`../plans/CURSOR_PLAN_INDEX.ru.md`](../plans/CURSOR_PLAN_INDEX.ru.md) | Архив Cursor-плана ↔ аудит |
| Следующий: `CONTROLLER_V2_SPEC_FINAL_*.ru.md` | Числовые tol + mid A–D + CL-N1@480 (+ F1b вне дендритного FINAL) |

---

## 10. Запреты (до FINAL и senior arms)

- **Не** объявлять v2 реализованным по E2/F* alone.
- **Не** менять алгоритм v1 в mainline без R8 A/B на каждый флаг.
- **Не** писать `SYNTHESIS_FINAL` по полной 13-волновой матрице при PARTIAL exit policy.
- **Не** стартовать F1b / KeepDone / G1 RERUN / multifactor Span100 из этого SPEC DRAFT.
