# Controller v2 — SPEC FINAL (дендритный контур, 2026-10-23)

> **Историческая спецификация; не текущий контракт реализации.** Принятый
> [план рефакторинга](../../../StructTrain/TimeLearner/RefactoringPlan.ru.md)
> пересматривает общую амплитудную цель, автоматические числовые tolerances,
> объединение Done и качества распознавания, а также обязательную robustness
> как условие convergence. Исходная цель — CapturedPerInput. Численные остатки,
> scientific evaluation и устойчивость к изменению протокола учитываются
> раздельно. Текст ниже сохраняет историческое решение от 23.10.

**Статус:** **SPEC FINAL** для дендритного Controller v2 (Classic+Branch, `ControllerVersion=2`). Закрывает блокеры mid A–D, числовые tol VERIFY/Done и policy CL-N1@480 из [`CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md`](CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md). **Не** является go-ahead на merge C++ v2 без отдельного R8 A/B; **не** включает аксонный тренер F1b (фаза A после ворот D / H0).

**Постановка.** Evidence 2026-10-20…23 (E1.0–E1.5, H2/H3 silent-Test, D1/CL-N1 H1, F3-R8, стратегия 23.10, H0a τ(Cm) table) достаточно, чтобы зафиксировать production-выбор mid, константы tol и классификацию stall на Span480 без ожидания axon PASS. Все нормативные разделы DRAFT §1–§4, §5 guidance, §6 default-off / KeepDone / F3 / W3 **наследуются**; ниже — только решения, которые переводят DRAFT → FINAL.

---

## 1. Mid production policy (закрытие §6.1 A–D)

**Выбор: C + A (V-gate).**

1. **Production / SoftCold / matrix default:** `UseCandidateMidOnNonSeparableTest=0` (**опция C** — never default-on до V-gate). Сохраняет сравнимость G1 и baseline silent thr=1 как известный фенотип, не как PASS.
2. **Когда Test уже NonSeparable / silent-mid path:** разрешён attempt-local / diagnostic overlay flag=1 (**опция A**), который по H3 cold восстанавливает finite `candidate_mid` и честные foil fires, **не** меняя `PostTuneResult=NonSeparable` и **не** объявляя Цель.
3. **Опции B и D:** B (always finite) — **отклонена** до отдельного SoftCold A/B на PASS-острове; D (diagnostic-only) subsumed в C+A (flag=1 только overlay/V-gate, не SoftCold XML default).
4. **VERIFY:** silent Acc 7/8 при thr=1 = `quality_fail` (`DEBT-D2`), **не** SoftCold PASS. KeepDone(3)/CanonRmin **не** sole-fix.

**Следствие для `DEBT-D2-silent-test`:** mid policy закрыта; silent-Test остаётся `quality_fail` до улучшения разделимости (H0/H0b / фаза A), не до переключения mid default-on.

---

## 2. Числовые tol VERIFY / Done (закрытие §5)

Опора: остров Console `sep_ltz` ~1–2% (E1.5); eps_amp предложение E1.2; survive L±1 / TipR±25% как FRAGILE evidence; proxy-margin ≠ `sep_ltz`.

| Константа | Значение FINAL | Обоснование |
|-----------|----------------|-------------|
| `eps_amp` | **1% · A\*** (целевая амплитуда входа) | E1.2 repeatability; сравнимо с островом, но применяется к amp-align, не съедает sep целиком |
| `eps_margin_verify` | **max(0.005, 0.25 · sep_ltz_baseline)** абсолютный пол остатка после tol | Не съедать весь остров ~1–2%: после tol обязан остаться ≥0.5 п.п. или ¼ измеренного baseline sep |
| `eps_residual_dt` | **1 / f_sample** (при 20 кГц = **0.05 мс**) | Один такт; FINE_DELAY дендритный Rs-only в пределах amp-tol, иначе потолок → фаза A |
| `survive_L` | **обязателен** unit-shift L±1 на каждом входе без потери target_hit | E1.5 FRAGILE |
| `survive_TipR` | **обязателен** глобальный TipR ×0.8 и ×1.25 без потери target_hit | E1.5 FRAGILE |
| Proxy vs Console | VERIFY-порог **на Console `sep_ltz` / fires / ranking**; `ideal_inh_proxy` — только predictor gate, не число Done | E1.4 / E1.1f intentional |

**Exact Done:** Need=0 **и** VERIFY pass по таблице выше **и** не silent thr=1. `Done_BE` — best-effort без маскировки RminTol (F7).

---

## 3. CL-N1@480 policy (закрытие §4 → FINAL)

1. На **Classic×N1 × Span480** при W3=off, Need≠0, TipR@Rmax: exit-класс **`bounded_stall_rmax`** — **принят в FINAL** как ожидаемый потолок текущей дендритной машины на 480, не как «баг SoftCold».
2. При L=MaxL и Need≠0: **`maxl_hold` / `infeasible_len`**.
3. **W3** (`EnableRmaxLengthEscape`) = diagnostic opt-in, **не** SoftCold default, **не** sole-fix 480.
4. H1 Span100 (`converged_need0` + silent) = **`quality_fail`**, не эскалация в `infeasible_len`.
5. Multifactor / G1 full RERUN ради train-stall на 480 — **запрещены** этим FINAL.

На H0b@480 с согласованной τ(Cm): если Train не Done при MaxL — это **потолок карты дендрита**, вход в фазу A, не mid-flight axon в Classic/Branch.

---

## 4. Наследование и вне scope

- Наследуется DRAFT: FSM §3, exit-классы wording, F3 opt-in, intentional proxy, Stage0 emit (`DEBT-S0`).
- **F1b / аксонный тренер:** вне дендритного FINAL; см. [`STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md`](STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md), [`F1B_EXPLAINER_AND_STATUS_2026-10-23.ru.md`](F1B_EXPLAINER_AND_STATUS_2026-10-23.ru.md).
- C++ реализация v2 — **после** этого FINAL + R8 A/B на каждый флаг (запрет DRAFT §10 сохраняется).

---

## 5. Закрытие долгов (документально)

| Долг | Статус после FINAL |
|------|--------------------|
| `DEBT-CTRL-V2-DRAFT` | **closed** → этот файл |
| `DEBT-CL-N1` | **partial-closed**: policy FINAL на 480; runtime stall остаётся картографированным потолком |
| `DEBT-D2-silent-test` | **partial-closed**: mid production = C+A; silent = `quality_fail` до улучшения физики/аксона |
| `DEBT-F1b` | **OPEN** (фаза A) |
| `DEBT-H0-tau-cm` | сужается к H0b cold / DENDRITE_MAP (см. карту) |
