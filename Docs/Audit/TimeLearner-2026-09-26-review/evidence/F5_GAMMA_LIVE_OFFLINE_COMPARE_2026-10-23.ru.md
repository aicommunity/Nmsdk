# F5 live rebuild — offline compare Span100 γ=0 vs tip-noop / H1 (2026-10-23)

## Постановка

После tip-noop paired cold Span100 (`F5.S100.0/1`, Console `f88d1852` / PulseLib `3a599a7` **без** символа F5) evidence [`F5_GAMMA_SPAN100_2026-10-22.ru.md`](F5_GAMMA_SPAN100_2026-10-22.ru.md) оставил **DEBT-F5-gamma OPEN**: XML-оверлей `CorrectAttenuationGammaForTipR` писался, но кодpath A7 в бинарнике tip не активировался. Следующий шаг кампании — **live rebuild** Console с PulseLib tip **`9efca9c`** (символ `CorrectAttenuationGammaForTipR` в бинарнике) и повтор A/B на том же case `W02_CL100_N1_PSIoff`.

Этот документ — **offline** сравнение **LIVE Arm0 γ=0** (`F5.S100L.0-…21224`) и **LIVE Arm1 γ=1** (`F5.S100L.1-…27819`) с prior tip-noop γ=0 и H1 baseline Span100. Цель: зафиксировать, что при **реальном** кодpath F5 (1) γ=0 совпадает с H1/tip-noop midband-baseline и (2) γ=1 на том же Console **не** меняет Train/Test относительно γ=0.

Иерархия: **Classic×N1 → Span 100 → AsymRm → PSIoff**, PostTune **OFF**, W3 **off**. Host `.11`. Без G1 / F1b / KeepDone / нового cold из этого docs-arm.

**Train / Test (канон):**  
[`TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Train) /  
[`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Test).

Машиночитаемая сводка: [`F5_GAMMA_LIVE_OFFLINE_COMPARE_2026-10-23.tsv`](F5_GAMMA_LIVE_OFFLINE_COMPARE_2026-10-23.tsv).

## Provenance (live rebuild)

| Поле | Значение |
|------|----------|
| root HEAD (runs) | `bae546244` (docs tip may be later; Arm manifests pin this) |
| PulseLib | **`9efca9c`** — `feat(TimeLearner): F5 CorrectAttenuationGammaForTipR on tip (A7, default off)` |
| Bin | `e49a52bf` |
| Console | `/home/user/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole` sha256 **`213e70034effa8d7…`** |
| F5 symbol in Console | **present** (`strings` / property name `CorrectAttenuationGammaForTipR`) |
| runs root | `/home/user/TLAgent-20261020/runs` |
| overlay | `--train-param CorrectAttenuationGammaForTipR=0\|1 --force-posttrain-tuning 0` |

Prior tip-noop / H1: Console **`f88d1852…`**, PulseLib **`3a599a7`** (символа F5 в бинарнике **нет**).

## Сводная таблица

**Classic×N1 → 100 ms → AsymRm → PSIoff**, PostTune OFF:

| RUN | γ | PulseLib / Console | conv | L | TipR | fail | fires | Acc |
|-----|---|--------------------|------|---|------|------|-------|-----|
| `F5.S100L.0-11-20261023T040538Z-21224` (LIVE Arm0) | **0** | `9efca9c` / `213e7003…` (**F5 yes**) | `converged_need0` | `54 48 30 1` | `2.880071e6×3+86e6` | `quality_fail` | `00000000` | 7/8 |
| `F5.S100L.1-11-20261023T052744Z-27819` (LIVE Arm1) | **1** | `9efca9c` / `213e7003…` (**F5 yes**) | `converged_need0` | `54 48 30 1` | `2.880071e6×3+86e6` | `quality_fail` | `00000000` | 7/8 |
| `F5.S100.0-11-20261022T191419Z-27970` (prior tip-noop γ=0) | 0 | `3a599a7` / `f88d1852…` (F5 **no**) | `converged_need0` | `54 48 30 1` | `2.880071e6×3+86e6` | `quality_fail` | `00000000` | 7/8 |
| `CLN1.H1.S100-11-20261022T181822Z-23399` (H1 baseline) | — (no γ overlay) | `3a599a7` / `f88d1852…` | `converged_need0` | `54 48 30 1` | `2.880071e6×3+86e6` | `quality_fail` | empty / silent | — (gate_rc=1 packaging) |
| `F5.S100.1-11-20261022T201624Z-3403` (prior tip-noop γ=1) | 1 | `3a599a7` / `f88d1852…` (F5 **no**) | `converged_need0` | `54 48 30 1` | `2.880071e6×3+86e6` | `quality_fail` | `00000000` | 7/8 |

Train/Test links для всех строк: [`…/W02_CL100_N1_PSIoff/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Train) / [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Test).

### LIVE Arm0 / Arm1 — matrix_result (бит-в-бит ≡)

Пути:

- `…/F5.S100L.0-11-20261023T040538Z-21224/W02/W02_CL100_N1_PSIoff/attempt-0001/matrix_result.json`
- `…/F5.S100L.1-11-20261023T052744Z-27819/W02/W02_CL100_N1_PSIoff/attempt-0001/matrix_result.json`

Оба плеча (overlay γ=`0` vs `1`):

- `training_convergence=converged_need0`, `IsNeedToTrain=0`
- `DendriteLength=54 48 30 1`
- `TipSynapseResistance=2880071,5552629363 ×3 + 86000000` (midband, не TipR@`1e10`)
- Test: `mode=silent`, `fires=00000000`, `acc=7`, `target_hit=0`, `test_mid_gap≈−0.001625`, `test_mid_quality=nonseparable`, `failure_class=quality_fail`, `child_rc=-15`, `gate_rc=0`
- `launch.exit=0`, queue `queue_completed_no_commit`

**γ=0 vs γ=1 delta:** нет — Train L/TipR/Need и Test fires/Acc/mid_gap/fail **идентичны**.

## Вердикт

1. **LIVE γ=0 ≡ tip-noop γ=0 ≡ H1** по Train-фенотипу (`converged_need0`, L=`54 48 30 1`, TipR `2.880071e6×3+86e6`) и silent Test `quality_fail`. Это валидный **baseline arm** при **реальном** кодpath F5 (символ в Console + PulseLib `9efca9c`), а не tip-noop «UProperty ignored».
2. **LIVE γ=0 ≡ γ=1** на том же Console/`9efca9c`: флаг `CorrectAttenuationGammaForTipR=1` **не** двигает midband Span100 / silent Test на `W02_CL100_N1_PSIoff`. Гипотеза «γ спасает N1 silent на midband» на этом case **не подтверждена** уже с активным A7.
3. Prior tip-noop γ=0≡γ=1 был ожидаем из‑за отсутствия символа F5; live rebuild **повторяет** ≡, но теперь как результат реального кодpath.
4. Silent Test остаётся **`DEBT-D2-silent-test`**. **`DEBT-F5-gamma`**: live A/B на Span100 **закрывает** вопрос «нужен rebuild tip» — rebuild сделан; γ не меняет исход на этом midband-probe. Дальнейшие F5-arms (другой Span / case) — по отдельному решению кампании, не из этого offline-снимка.

## Infra / запреты этого arm

- Docs-only: **не** kill F5 Console, **не** launch нового cold, **не** G1 / F1b / KeepDone.
- Сравнение offline по уже лежащим `matrix_result` + provenance `run_manifest.json`.
- PulseLib gitlink не трогаем в этом commit (владеет F5 agent).
