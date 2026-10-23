# Controller v2 — SPEC DRAFT (2026-10-23)

**Статус:** **SPEC DRAFT** — продвижение каркаса [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md) и входов [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md) в форму спецификации. Документ **ещё не FINAL SPEC**: открытые продуктовые решения (§8) оставляют **`DEBT-CTRL-V2-DRAFT` open** до `CONTROLLER_V2_SPEC_FINAL_*.ru.md` (или эквивалентного senior-approved FINAL). **Не** является заданием на реализацию в C++ и **не** go-ahead на cold Console.

**Постановка.** Этап 4 аудита TimeLearner требует одного контроллера Classic+Branch за флагом `ControllerVersion=2`, с разведёнными шагами поиска длины, выравнивания амплитуды, тонкой задержки, verify и калибровки mid. Evidence 2026-10-22 (E1 библиотеки, silent-Test H*, D1/CL-N1, F3-R8) достаточно, чтобы зафиксировать **нормативные** контракты exit-классов `LEN_SEARCH` и ряд intentional-политик; числовые tol Done/margin и production mid-policy ещё не закрыты — поэтому статус остаётся DRAFT относительно FINAL.

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

## 5. VERIFY / sep / fragility (норматив guidance)

1. **`ideal_inh_proxy` intentional.** Для nextseg/preinh при sync CV≤0.25 E1.4 использует phenomenological τ=0.5 мс. E1.1d/e/f offline и E1.1g Console Branch IR (FWHM **28.8–30.9 мс** ≫ 2.1; sep_soma **≈−0.015**) — **retire=NO**; `DEBT-E1.1f` = partial-wontfix-offline. VERIFY-tol **не** строить из E1.1d–g FWHM/sep; proxy-margin (~7%) **не** путать с Console `sep_ltz`.
2. **E1.5 fragility tol guidance.** Baseline sep острова ~**1–2%**; br25_nextseg **0/9** strict при L±1 / TipR×0.8/×1.25. Числовой tol SPEC (ещё open, §8) **обязан** оставлять запас ≥ возмущения L±1 и TipR±25% и не съедать весь margin (согласуется с E1.2 eps_amp≈1%·target). Done на граничном mid без учёта fragility — **ложный**.
3. **Emit готов, tol нет.** C++/`posttune_complete` уже пишут `sep_margin`/`amp_be`/`done_be` (`DEBT-S0` done); формула порога «запас ≥ предсказанный − …» для FINAL — open.

---

## 6. Test mid / TipR / Reset / W3 (норматив политики DRAFT)

| Тема | Норматив SPEC DRAFT | Что ещё open для FINAL |
|------|---------------------|-------------------------|
| **Mid policy (H3)** | Flag `UseCandidateMidOnNonSeparableTest` **default-off**; при NonSeparable не оставлять только `FixedLTZ=1`; silent Acc 7/8 ≠ PASS | **Production policy** (когда включать: только NonSeparable / always finite candidate / never default-on до V-gate) |
| **KeepDone / CanonRmin** | KeepDone(3) / mode=1 **не** sole-fix silent thr=1; H2 ослаблена (`DEBT-17` done) | Default `PostTrainTipResistanceMode` для v2 |
| **F3 Reset** | **Opt-in**; CODE default off; A/B: BR island OK, W01 silent unchanged | Продуктовый default в v2 XML (рекомендация: оставить off) |
| **W3** | Не SoftCold default; не sole-fix 480 | — (закрыто как policy в DRAFT) |
| **F1b → `FINE_DELAY`** | Только после senior docs-ready + cold; checklist в DRAFT INPUTS §5 | **`DEBT-F1b` OPEN**, senior blocked |

---

## 7. Конфигурация и совместимость

- Флаг: `ControllerVersion=2` (XML Train + fingerprint очереди).
- Classic и Branch: **одна** реализация + стратегия топологии.
- PostTune: вне scope этапа 4 как алгоритм; пары ON/OFF — только `--force-posttrain-tuning` (скилл structtrain-experiments).
- Отчётность: exact / `Done_BE` / Need, residue, margin, fires, Acc — Stage0; плюс **нормативные** exit-классы §4 в harness/rollup (конкретные имена полей JSON — детали реализации, не блокер формулировок).
- Bin tip с E0 `--train-param` whitelist (Reset, W3, …) — overlays attempt-local без патча `matrix.json`.

---

## 8. Что блокирует FINAL SPEC (`DEBT-CTRL-V2-DRAFT` остаётся open)

Постановка: SPEC DRAFT **продвигает** прогресс (H2 exit-классы нормативны; intentional proxy; mid default-off; KeepDone не sole-fix; F3 opt-in; W3 не SoftCold default; F1b senior-blocked явно). Ниже — решения, без которых **нельзя** объявлять `CONTROLLER_V2_SPEC_FINAL` и закрывать `DEBT-CTRL-V2-DRAFT`.

| # | Блокер FINAL | Почему |
|---|--------------|--------|
| 1 | **Mid policy production** | Default-off и cold PASS на flag=1 доказаны; когда включать в production / V-gate — open |
| 2 | **Числовой tol** Done / margin / residual_dt / VERIFY | Нужны exit-clean G1 + E1 cal + **E1.5** (~1–2% sep; L±1 / TipR±25%); emit готов, пороги нет |
| 3 | **F1b senior** (`DEBT-F1b`) | Docs-ready checklist есть; cold/пилот и решение train-loop vs verify-only — senior blocked |
| 4 | **CL-N1@480 senior/policy close** | Exit-классы §4 нормативны в DRAFT; долг на 480 open до принятия в FINAL / senior close (не через multifactor) |
| 5 | *(вторично)* Default TipR PostTune mode; псевдокод Branch reverse-order + topology после C2↔Console сверки; N0 для span>50 | Не блокируют формулировку §4, но нужны для полной миграции v1→v2 |

**Не блокеры FINAL (уже зафиксированы в этом DRAFT):** формулировки `bounded_stall_rmax` / `maxl_hold`/`infeasible_len` / `quality_fail`/`DEBT-D2` / SoftCold PASS; intentional `ideal_inh_proxy`; KeepDone ≠ sole-fix; F3 opt-in; W3 ≠ SoftCold default; Train `sep_margin` emit.

**Вывод.** `DEBT-CTRL-V2-DRAFT` **остаётся open** со ссылкой на этот файл; закрытие — только после FINAL SPEC (или явного senior supersede). Cold / C++ под этот документ **не** стартовать.

---

## 9. Связанные артефакты

| Документ | Роль |
|----------|------|
| [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md) | Каркас FSM (superseded по статусу этим SPEC DRAFT) |
| [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md) | Полные входы E1/H*/D1/F*; §4.5a исходник wording |
| [`CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md`](CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md) | Mid + margin связка |
| [`CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md`](CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md) | H1 executed; H2 → §4 этого документа |
| [`TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md) | `DEBT-CTRL-V2-DRAFT` / `DEBT-CL-N1` / `DEBT-F1b` / `DEBT-E1.5` |
| Следующий: `CONTROLLER_V2_SPEC_FINAL_*.ru.md` | Числовые tol + closed mid/F1b/CL-N1 policy |

---

## 10. Запреты (до FINAL и senior arms)

- **Не** объявлять v2 реализованным по E2/F* alone.
- **Не** менять алгоритм v1 в mainline без R8 A/B на каждый флаг.
- **Не** писать `SYNTHESIS_FINAL` по полной 13-волновой матрице при PARTIAL exit policy.
- **Не** стартовать F1b / KeepDone / G1 RERUN / multifactor Span100 из этого SPEC DRAFT.
