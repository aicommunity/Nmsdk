# F5 CorrectAttenuationGammaForTipR — paired cold (2026-10-22)

## Постановка

После закрытия **G1_S1_RERUN** и при нулевой загрузке real **NeuroModelerConsole** на Elder-1 (`.11`, `pgrep -f NeuroModelerConsole=0`) и M40 `.17` (SSH `10.245.1.17`, то же) выполнена **парная** soft-cold серия на **том же case**, что и one-shot F5 от 2026-10-21: **Classic×N1**, Span **50**, AsymRm **gen**, PostTune **OFF**, `W01_CL50_N1_PSIoff`. PulseLib **`6d746ac`**, Console sha256 **`745d6061…`**, lane `f5-paired`, последовательно на `.11` (`HOST_LIMIT=8`, `jobs=1`), без перезапуска G1 RERUN.

Оверлей очереди (канон E0): `--train-param CorrectAttenuationGammaForTipR=0|1` в attempt-local Train; канонические inputs не менялись.

| Arm | RUN_ID | `CorrectAttenuationGammaForTipR` | `launch.exit` |
|-----|--------|----------------------------------|---------------|
| A baseline | `F5.paired-base-11-20261022T031312Z-30140` | **0** (явный default) | **0** |
| B γ | `F5.paired-gamma-11-20261022T034517Z-10276` | **1** | **0** |

Конфиги matrix (Train / Test): [`TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSIoff/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSIoff/Train), [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSIoff/Test) (фактический checkout lane: `/home/user/tl-agent/lanes/f5-paired/Nmsdk/Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSIoff/`).

Сводки launch: `$REPORTS/F5/<RUN_ID>/summary.tsv` (копия кампании под `/home/user/TLAgent-20261020/agent-reports/F5/`).

## Результаты (Trainer×Mode → Span → NeuronModel)

**Classic×N1 → 50 ms → AsymRm → gen**, PostTune OFF:

| Arm | Need | L (DendriteLength) | TipR после Train (×3 trainable + tip1) | test_mid_gap | fires | Acc | Цель | failure_class |
|-----|------|--------------------|----------------------------------------|--------------|-------|-----|------|---------------|
| baseline γ=0 | 0 | 25 22 15 1 | 2.88M, 5.55G, 2.88M, 5.55G, 2.88M, 5.55G, **86M** | −0.00389 | `00000000` | 7/8 | **нет** | `quality_fail` |
| γ=1 | 0 | 25 22 15 1 | **идентично** baseline | −0.00389 | `00000000` | 7/8 | **нет** | `quality_fail` |

Обучение на обоих плечах: `training_convergence=converged_need0`. Test: `mode=silent`, `target_hit=0`, `test_mid_quality=nonseparable`, `child_rc=-15` (grace gate, как в prior F5/E2). **Побочных различий между γ=0 и γ=1 на этом case нет** — бит-в-бит те же TipR, длины, mid-gap и fires.

One-shot **2026-10-21** `F5.gamma-11-20261021T053512Z-6091` (только γ=1) даёт **ту же** matrix-строку метрик; paired rerun подтверждает воспроизводимость, а не регрессию overlay.

## Выводы

1. **Paired сравнение выполнено** (DEBT-F5-gamma: блок «нет baseline на том же case» снят), но **A7 PASS не достигнут**: оба плеча — Need=0 при **silent Test** и `quality_fail`; Acc 7/8 **не** зачитывается как цель.
2. Флаг **`CorrectAttenuationGammaForTipR=1` не меняет** исход на `W01_CL50_N1_PSIoff` при PulseLib `6d746ac` относительно явного γ=0; гипотеза «γ спасает N1 silent» **не подтверждена** на этом пилоте.
3. **Вердикт F5 / DEBT-F5-gamma: OPEN** — фикс не закрыт как рабочий; следующий шаг по R3 — другой span/case (например W04 из очереди) или углубление mid/TipR, не повтор того же W01 без новой гипотезы.

## Infra (срез старта)

| Host | Console (real) | Disk |
|------|----------------|------|
| `.11` Elder-1 | 0 | Avail ≈ 179 G `/` |
| `.17` M40 | 0 | Data Avail ≈ 743 G |

Серия завершена на срезе **2026-10-22 ~07:24 MSK**: оба `launch.exit=0`, real Console **0**, tmux **drv-F5_paired** снят; в `paired_series.log` строки `SERIES_DONE F5.paired` **нет** (drv пишет только LAUNCH-блоки), факт закрытия — по exit-файлам и отсутствию drv/wait_run.
