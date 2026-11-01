# Classic×N1 HEAD ablations (план §этап 2) — W02 cold 2026-10-22

Постановка: после D1 фазы 2 ([`D1_BISECT_2026-10-22.ru.md`](D1_BISECT_2026-10-22.ru.md)) первый PulseLib с L₀≥54 = `3cefd64`, но сам stall Classic N1 на HEAD остаётся открытым (`DEBT-CL-N1` / `DEBT-D2b5-W02`). По плану аудита (§этап 2) однофакторно проверить на **текущем HEAD Console**, восстанавливает ли какая‑либо абляция `converged*` / Need=0 относительно baseline `not_converged_at_stop` на кейсе `W02_CL480_N1_PSIoff`.

Trainer×Mode: **Classic×N1**. Span: **480 мс**. NeuronModel: AsymRm (matrix W02). Mod: PSIoff. PostTune OFF (`--no-commit`, attempt-local overlays; `matrix.json` не патчили). Host: `.11` (Elder-1), до 6 параллельных Console (лимит ≤8).

**Train / Test (канон):**  
[`TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train) /  
[`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Test).

Машиночитаемая сводка: [`CL_N1_HEAD_ABLATIONS_2026-10-22.tsv`](CL_N1_HEAD_ABLATIONS_2026-10-22.tsv).

## Console / PulseLib

| Роль | sha256 (полный) | PulseLib |
|---|---|---|
| HEAD baseline (base, d, e) | `9540e64b7813ee2e735d0f570486d7fdd7de3747d7f12c7bb1665a38b3f8e45f` | `4b85c91` (F3 Reset flag already on HEAD, default off) |
| HEAD+abc flags (a, b, c) | `6adf5875080f7ee678809d3e2055cde8517fe6798cb055f368777b8ba07ac68c` | тот же tip + opt-in F6/F7 Classic properties (defaults = historical) |

Для (a)/(b)/(c) на чистом HEAD (`4b85c91`) не было runtime-свойств `PreferConfiguredResistanceMinFloor` / `DisableMidbandWalkToRmin` / `RminLengthTolFactor` (только `constexpr kRminLengthTolFactor=4`). Перед cold a/b/c в Classic добавлены UProperty с **default off / factor=4**, Console пересобран → `6adf5875…`. Поведение без overlay бит-в-бит как historical; флаги включаются только `--train-param`.

## Результаты (все 6/6 DONE)

| Ablation | Overlay | RUN_ID | Console | training_convergence | Need | L | TipR |
|---|---|---|---|---|---|---|---|
| **base** | — | `CLN1.base-11-20261022T135050Z-6642` | `9540e64b…` | `not_converged_at_stop` | 1 | `54 44 1 1` | `1e10×2 + 86M×2` |
| **(a)** Rmin=20 МОм без Rm/q | `PreferConfiguredResistanceMinFloor=1` `ConfiguredResistanceMin=2e7` | `CLN1.a-11-20261022T135934Z-14129` | `6adf5875…` | `not_converged_at_stop` | 1 | `53 44 1 1` | `1e10×2 + 86M×2` |
| **(b)** без midband walk | `DisableMidbandWalkToRmin=1` | `CLN1.b-11-20261022T140139Z-7873` | `6adf5875…` | `not_converged_at_stop` | 1 | `54 44 1 1` | `1e10×2 + 86M×2` |
| **(c)** tol×1 | `RminLengthTolFactor=1` | `CLN1.c-11-20261022T140345Z-25980` | `6adf5875…` | `not_converged_at_stop` | 1 | `54 44 1 1` | `1e10×2 + 86M×2` |
| **(d)** γ auto off | `AutoEstimateAttenuationGamma=0` | `CLN1.d-11-20261022T135256Z-4617` | `9540e64b…` | `not_converged_at_stop` | 1 | `53 44 1 1` | `1e10×2 + 86M×2` |
| **(e)** Reset-before-burst | `ResetNeuronBeforeTrainBurst=1` | `CLN1.e-11-20261022T135501Z-15980` | `9540e64b…` | `not_converged_at_stop` | 1 | `54 44 1 1` | `1e10×2 + 86M×2` |

Gate/Test: у всех SKIP_GATE / `not_evaluated_training_incomplete` (ожидаемо при `not_converged_at_stop`). Audit подтвердил overlays: (a) `rmin=2e7` + `prefer_configured_rmin_floor=1`; (b) `disable_midband_walk_to_rmin=1`; (c) `rmin_length_tol_factor=1`; (d) `auto_estimate_attenuation_gamma=0`; (e) `reset_before_train_burst=1`.

W01 (`W01_CL50_N1_PSIoff`) в этом arm **не** запускали (слоты `.11` заняты шестью W02).

## Выводы

Ни одна из пяти однофакторных абляций плана §этап 2 **не** восстановила `converged*` / Need=0 на Classic×N1 Span480 относительно baseline: все шесть прогонов заканчиваются `not_converged_at_stop` с фенотипом CL-N1 stall (L≈`53–54 44 1 1`, TipR `1e10×2 + 86M×2`). Пол Rmin=20 МОм (a) чуть сдвигает L₀ на 53 вместо 54, но Need и TipR-класс те же. Отключение midband (b), сужение tol (c), фиксированная γ (d) и Reset-before-burst (e) не меняют исход. Следствие для долга: **DEBT-CL-N1 остаётся open**; однофакторные «старые подозреваемые» A3/A6/A7/A8 на HEAD **не** являются достаточным sole-fix stall 480 мс. Дальше — не повтор тех же overlays, а смена постановки (бисекция поведения вокруг `3cefd64` / MaxL escape, Controller v2 length search, или multifactor на ином Span).

## Provenance

- Runs root: `/home/user/TLAgent-20261020/runs/`
- Lanes: `cln1-base`, `cln1-d`, `cln1-e`, `f6-rminfloor`, `f6-mid`, `f2-reset` под `$HOME/tl-agent/lanes/`
- Summaries: `$REPORTS/CL_N1_HEAD_ABLATIONS/<RUN_ID>/summary.{tsv,json}`
