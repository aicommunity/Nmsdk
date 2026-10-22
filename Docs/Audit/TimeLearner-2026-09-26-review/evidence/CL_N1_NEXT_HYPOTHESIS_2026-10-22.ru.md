# CL-N1 — следующая гипотеза (docs-ready, 2026-10-22)

Постановка: после HEAD ablations a–e (**6/6** stall) и Arm A W3on (`EnableRmaxLengthEscape=1` → MaxL `L=100 58 1 1`, Need=1) долг **`DEBT-CL-N1` / `DEBT-D2b5-W02` остаётся open**. W3on подтвердил различие фенотипов stall@54 vs MaxL@100, но **не** дал `converged*` и **не** является SoftCold-путём. Этот документ фиксирует **два конкретных кандидата** на следующий cold-arm **без запуска** Console.

Trainer×Mode якоря: **Classic×N1**. Базовый case W3on/ablations: Span **480** → AsymRm → PSIoff → PostTune OFF — Train/Test [`W02_CL480_N1_PSIoff/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train). Evidence W3on: [`CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md`](CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md). Controller DRAFT: [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md).

**Запрет этого note:** не стартовать cold / G1 RERUN / KeepDone / F1b; не включать W3 в matrix SoftCold defaults.

Инфра для будущего execute: Bin tip **`bf3e82ffe`** уже несёт E0 `--train-param` whitelist (`ResetNeuronBeforeTrainBurst`, `EnableRmaxLengthEscape`, …) на `timelearner_fix2` — overlays attempt-local без патча `matrix.json`.

---

## Кандидат H1 — multifactor на Span ≠ 480, W3=off

| Поле | Значение |
|------|----------|
| Вопрос | Сохраняется ли Classic×N1 `not_converged_at_stop` / stall-класс TipR@Rmax при **W3=off** на **короче** Span (например 100 мс), или stall специфичен для 480? Если на Span≠480 сходимость есть — multifactor (Rmin-floor × midband-off × tol) имеет смысл только там, где baseline уже не MaxL-locked. |
| Case (пример) | `W31` / HIST Classic N1 Span **100** из G1-отбора (конкретный case_id — при execute из `G1_selected_*.tsv` / matrix W0x), **не** повтор W02 480 |
| Overlay | W3 **off** (matrix default); при необходимости attempt-local multifactor из a–c **по одному фактору за RUN**, не «всё сразу» |
| PostTune | OFF (attempt-local `--force-posttrain-tuning 0`) |
| Критерий phenotype | финальный L / TipR / `training_convergence` **отличаются** от W02 stall `54 44 1 1` + Need=1 |
| Критерий fix | `converged*` / Need=0 — желателен, но не обязателен для «Span-specificity» |
| Статус | **docs-ready только**; cold **не** запущен |

Иерархия ожидаемой строки результата: Classic×N1 → Span **100** (или иной ≠480) → NeuronModel AsymRm → Mod PSIoff/gen → PostTune OFF; колонки Train/Test — из `TimeLearnerMatrix/<WAVE>/inputs/<case>/{Train,Test}`.

---

## Кандидат H2 — docs-ready acceptance: `LEN_SEARCH` / `infeasible_len` (без cold)

| Поле | Значение |
|------|----------|
| Вопрос | Как Controller v2 должен принимать MaxL-escape и stall@Rmax на длинном Span, чтобы VERIFY/`infeasible_len` не путали «плохой SoftCold» с «достигнут потолок длины»? |
| Артефакт | критерии входа в SPEC / DRAFT §`LEN_SEARCH`, **не** новый Console RUN |
| Предлагаемые acceptance (черновик) | (1) если L₀ достигло MaxL **и** Need≠0 → класс **`infeasible_len` / MaxL-hold**, не `quality_fail` SoftCold; (2) W3=1 остаётся **opt-in diagnostic**, не default SoftCold; (3) stall `L≈54` при W3=off на Span 480 — отдельный класс **bounded stall**, пока нет multifactor-доказательства на Span≠480 (H1) |
| Ссылки | скелет [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md); DRAFT inputs §3–§4; AMPNORM W3 [`AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md`](AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md) |
| Статус | **docs-ready**; SPEC по-прежнему **blocked** (`DEBT-CTRL-V2-DRAFT` open) |

---

## Приоритет и что не делать

1. **Сначала H2 в docs** (уточнить wording acceptance в DRAFT/SPEC черновике) — не требует Console.  
2. **H1 cold** — только по явному execute-arm; один case Span≠480, W3=off, ≤1 Console на `.11`.  
3. **Не** повторять a–e на W02 480; **не** «чинить» SoftCold включением W3; **не** G1 RERUN / F1b / KeepDone из этого note.

`DEBT-CL-N1` остаётся **open** до появления `converged*` на релевантном Classic×N1 case **или** до явного policy-close через SPEC `infeasible_len` (H2), согласованного senior.
