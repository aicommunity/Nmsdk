# CL-N1 next arm — разбор PulseLib `3cefd64` vs HEAD stall (2026-10-22)

Постановка: после D1 phase2 CLOSED ([`D1_BISECT_2026-10-22.ru.md`](D1_BISECT_2026-10-22.ru.md)) и HEAD stage-2 ablations base+(a–e) **6/6** `not_converged_at_stop` ([`CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md`](CL_N1_HEAD_ABLATIONS_2026-10-22.ru.md)) нужен **новый** arm, не повтор overlays a–e. Здесь — code-read вокруг первого измеренного L₀≥54 (`3cefd64`) и один cold-probe MaxL-related param на Classic×N1.

Trainer×Mode: **Classic×N1**. Span: **480 мс**. NeuronModel: AsymRm. Mod: PSIoff. PostTune OFF (attempt-local; `matrix.json` не патчили).

**Train / Test (канон):**  
[`TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train) /  
[`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Test).

Машиночитаемая сводка: [`CL_N1_NEXT_ARM_3CEFD64_2026-10-22.tsv`](CL_N1_NEXT_ARM_3CEFD64_2026-10-22.tsv).

## 1. Что меняет `3cefd64` (и почему D1 видит MaxL escape)

Коммит PulseLib **`3cefd64`** (`fix(ampnorm): hold TipR at MaxL overshoot (anti-bounce)`, 2026-10-07) в `ChangeSynapseResistanceStatus` (Classic + twin Branch):

1. **W3d (без смены семантики vs `c3b0226`):** при TipR@Rmax + overshoot (`dt<0`) + dwell ≥ limit + **L &lt; MaxL** — arm `DendStatus=1` / `RmaxOvershootLengthGrow` (рост длины), **без** TipR-down.
2. **Новое W3f / MaxL-hold:** при тех же условиях, но **L ≥ MaxL** — **HOLD TipR** (явный запрет paced TipR-down, который давал sterile bounce `1e11↔0.85`).
3. **W3e:** undershoot (`dt≥0`) @Rmax pre-ready — TipR-down только если L ≥ MaxL/2 и нет pending grow.

На срезе D1 i=6 (`3cefd64`) cold W02 дал L=`100 72 1 1` (MaxL escape), Need=1, `not_converged_at_stop` — длина **уходит** к потолку, в отличие от lo=`5308aa5` (L=`53 44 1 1`) и HEAD-stall `54 44 1 1`.

Важно для интерпретации бисекции: между индексами D1 i=5 (`5308aa5`) и i=6 (`3cefd64`) в истории PulseLib лежат W3c/W3d (`162e7c9`, `c3b0226`) и ряд midband/tol-коммитов; они **не** были отдельными точками карты D1. Вердикт «первый измеренный L₀≥54 = `3cefd64`» остаётся верным для **выборки карты**, но фенотип MaxL escape на i=6 опирается на **цепочку** W3c/W3d + anti-bounce hold, а не только на одну строку hold.

## 2. Почему HEAD снова stall@54, а не MaxL@100

На **`3cefd64`** предикат `at_r_max_w3` был **без** гейта `EnableRmaxLengthEscape`:

```cpp
const bool at_r_max_w3 = (rmax_w3 > 0.0 && r_old >= rmax_w3 * (1.0 - 1e-9));
```

На HEAD (`3a599a7` / tip с F3+F6/F7) тот же блок уже:

```cpp
const bool w3_enabled = IsParametricNormalization() && EnableRmaxLengthEscape.GetData();
const bool at_r_max_w3 = w3_enabled && (rmax_w3 > 0.0 && r_old >= rmax_w3 * (1.0 - 1e-9));
```

Гейт введён в **`a15f4eb`** (`feat(TimeLearner): bound parametric Rs by membrane resistance`, 2026-10-08) — **после** `3cefd64`, **до** `2bb72a3` / HEAD-stall выборки D1 i=8. `ADefault` и политика SoftCold задают **`EnableRmaxLengthEscape=false`** ([`AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md`](AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md)); в XML W02 свойства нет → runtime W3 **off**.

Следствие: на matrix-default HEAD путь W3d/W3f **мёртв**; TipR может сидеть у потолка (`1e10×2+86M×2`), а длина **не** получает forced grow → фенотип CL-N1 stall `L≈54 44 1 1`. На ungated `3cefd64` forced grow доводит L₀ до MaxL. Это **разные** плохие исходы одной оси Need≠0; ablations a–e (Rmin floor / midband / tol / γ / Reset) **не** трогают W3-гейт и потому не sole-fix.

`2bb72a3` (restore configured cold-start) снимает Rm-derived cold TipR init — влияет на старт Rs, но **не** объясняет сам факт MaxL escape на i=6 vs stall на HEAD при W3=off.

## 3. Гипотеза cold Arm A (MaxL-related param)

| Поле | Значение |
|------|----------|
| Вопрос | Восстанавливает ли **`EnableRmaxLengthEscape=1`** на HEAD фенотип роста L₀≫54 / MaxL-escape (как на `3cefd64`), отличаясь от baseline stall `54 44 1 1`? |
| Case | `W02_CL480_N1_PSIoff` |
| Overlay | `--train-param EnableRmaxLengthEscape=1` (attempt-local; inputs immutable) |
| Host | `.11` (Elder-1), 1 Console |
| Критерий **phenotype** | финальный L₀ **≥ 70** или L₀=`100` / явный MaxL-класс vs baseline `54` |
| Критерий **fix** (вторичный) | `converged*` / Need=0 — **не** обязателен; W3 **не** SoftCold-путь (политика 2026-10-08) |

Arm B (иной Span) **не** запускали: Arm A различил фенотипы.

## 4. Cold Arm A — результат

| Поле | Значение |
|------|----------|
| RUN_ID | `CLN1.W3on-11-20261022T163105Z-19730` |
| Console sha256 | `f88d1852c5fc40b3…` (полный `f88d1852c5fc40b3e7ed58b6c79633d0d768f6ae5d9a2915e0e0d8f2893ee688`) |
| PulseLib | `3a599a7` |
| Overlay audit | `EnableRmaxLengthEscape=1` (Train Parameters/Model + `runtime_input_overrides.json`) |
| launch.exit | `1` (train incomplete — ожидаемо) |
| training_convergence | `not_converged_at_stop` |
| Need | `1` (`IsNeedToTrain=1`; fail_notes `Need=1`) |
| L (after) | **`100 58 1 1`** (MaxL escape) |
| TipR (after) | `1e10 1e10 86M 86M` |
| Gate/Test | SKIP / `not_evaluated_training_incomplete` |
| Train / Test | [`…/W02_CL480_N1_PSIoff/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train) / [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Test) |

### Сводная таблица (иерархия)

| Trainer×Mode | Span | NeuronModel | Mod | PostTune | Overlay | RUN_ID | training_convergence | Need | L | TipR | Train | Test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Classic×N1 | 480 | AsymRm | PSIoff | OFF | — (HEAD stall baseline, ablation base) | `CLN1.base-11-20261022T135050Z-6642` | `not_converged_at_stop` | 1 | `54 44 1 1` | `1e10×2+86M×2` | [`Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train) | [`Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Test) |
| Classic×N1 | 480 | AsymRm | PSIoff | OFF | `EnableRmaxLengthEscape=1` | `CLN1.W3on-11-20261022T163105Z-19730` | `not_converged_at_stop` | 1 | **`100 58 1 1`** | `1e10×2+86M×2` | [`Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train) | [`Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Test) |

## 5. Выводы

Критерий **phenotype** Arm A **выполнен**: на HEAD Console с PulseLib `3a599a7` overlay W3=1 сменил CL-N1 stall `L≈54 44 1 1` на **MaxL escape** `L=100 58 1 1` (класс D1 @ `3cefd64`), при тех же Need=1 / `not_converged_at_stop` / TipR `1e10×2+86M×2`. Это подтверждает code-read: после `a15f4eb` length-escape завязан на `EnableRmaxLengthEscape`, а matrix-default W3=off объясняет HEAD-stall без роста L₀ к MaxL.

Критерий **fix** **не** выполнен: W3=1 **не** sole-fix сходимости и **не** SoftCold-путь ([`AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md`](AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md)). **`DEBT-CL-N1` / `DEBT-D2b5-W02` остаются open.** Дальше — не повтор a–e и не «включить W3 в матрицу как фикс»; кандидаты: Controller v2 `LEN_SEARCH` / `infeasible_len` при MaxL, multifactor на ином Span при W3=off, или явная policy-постановка отдельно от SoftCold.

## Provenance

- PulseLib: `3cefd64` / W3c–W3d chain; gate `a15f4eb`; HEAD tip `3a599a7`
- Console: `f88d1852…` (workspace `Bin/Platform/Linux/NeuroModelerConsole`)
- Runs root: `/home/user/TLAgent-20261020/runs/`
- Lane: `cln1-w3b` under `$HOME/tl-agent/lanes/` (queue scripts с `--train-param`; matrix inputs W02 immutable)
- matrix_result: `…/CLN1.W3on-11-20261022T163105Z-19730/W02/W02_CL480_N1_PSIoff/attempt-0001/matrix_result.json`
