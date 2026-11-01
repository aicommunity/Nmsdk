# E1.3 — релаксация сомы после пачки (Reset vs пауза)

Постановка: измерить время возврата сомы к покою после EPSP-пачки и проверить, объясняет ли **мембранная** релаксация систематический сдвиг амплитуды Reset vs no-Reset из E1.2 (settled ≈ **−28 %** на AsymRm L=10 / TipR=8.6×10⁷ / ISI=2 с; план [`TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) §E1.3 и открытый вопрос §294 про τ≥1 с). Trainer×Mode для probe-физики **N/A**; конфиги **Train/Test** — probe-only (`IsNeedToTrain=0`): AsymRm — шаблон Test [`TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test) (пара Train рядом); FastSpan optional — [`W46/…/W46_HIST_FAST_D002_C2_5E10/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W46/inputs/W46_HIST_FAST_D002_C2_5E10/Test). G1 RERUN / F1b cold / KeepDone W33 **не** запускались. MaxSpikesPerFeature поднят через [`tools/e1_2_repeatability.py`](tools/e1_2_repeatability.py) (для dual n_packs=2 достаточно).

**Протокол:** (1) одиночный импульс → τ_relax (log-fit mid-decay), t_to_1 %, t_to_noise; (2) dual-pulse pause-sweep 0.1…5 с → amp_bias = 100·(pack1−pack0)/pack0 без Reset между пачками. **Console sha256:** `4a0658f34736bf0575f051d6ee790e9342f5df8ebf904956640fbeaaa7fdc5d7` (тот же, что E1.2). Хост: Elder-1, `LD_LIBRARY_PATH=$HOME/tl-agent/lib` (glog 0.4). Скрипт: [`tools/e1_3_relaxation.py`](tools/e1_3_relaxation.py).

## Метрики релаксации (decay)

| NeuronModel | L | TipR | τ_relax | t_to_1% | t_to_noise | res @ 0.5 с | Train/Test |
|-------------|--:|-----:|--------:|--------:|-----------:|------------:|------------|
| `NSPNeuronGenAsymRmD001C1e9` | 10 | 8.6e7 | **26.0 мс** | **128.5 мс** | **165.9 мс** | **−0.42 %** пика | W01_CL50_N0_PSIoff |
| `NSPNeuronGenD002C25e11` (opt.) | 10* | 8.6e7 | **6.0 мс** | **30 мс** | **38.5 мс** | ~0 | W46_HIST_FAST… |

\*FastSpan: lengths `10,10,10,1` (у шаблона W46 max L на d4 = 1). Fit R² ≈ 0.992 на обеих моделях. Одиночный `test_trace` обрывается на **t_end≈1.5 с** (окно анализатора), поэтому остатки ≥1.55 с читаются из dual-pulse.

Вывод по decay: пассивный возврат сомы к покою на AsymRm занимает **≪ 1 с** (τ≈26 мс; к 0.5 с остаток \<1 % пика). Это **не** масштаб τ≥1 с из гипотезы §294 для носителя gap Reset/no-Reset.

## Pause-sweep (amp pack1 vs pack0)

| NeuronModel | pause с | pack0 peak | pack1 peak | bias % | note |
|-------------|--------:|-----------:|-----------:|-------:|------|
| AsymRm | 0.10 | 0.002191 | — | — | pack1 invalid: pause ≲ t_peak (перекрытие EPSP) |
| AsymRm | 0.25 | 0.002212 | 0.001591 | **−28.0** | |
| AsymRm | 0.50 | 0.002212 | 0.001587 | **−28.3** | |
| AsymRm | 1.00 | 0.002212 | 0.001601 | **−27.6** | |
| AsymRm | 1.55 | 0.002212 | 0.001605 | **−27.4** | порог аудита «≥1.55 с» |
| AsymRm | 2.00 | 0.002212 | 0.001600 | **−27.7** | якорь E1.2 ISI=2 с |
| AsymRm | 5.00 | 0.002212 | 0.001598 | **−27.7** | bias **не** исчезает |
| FastSpan | 2.00 | 0.009108 | 0.011101 | **+21.9** | знак противоположный AsymRm |

На AsymRm bias **плоский ≈ −27.4…−28.3 %** на всём диапазоне пауз **0.25…5 с**: увеличение паузы после возврата сомы к baseline **не** восстанавливает амплитуду Reset. Pack0 dual совпадает с reset mean E1.2 (0.00221157) bit-identical; pack1 @ 2 с совпадает с settled E1.2 (0.00159959).

## Ответ на вопрос «объясняет ли релаксация −28 % / 10 % W01?»

**Нет.** Мембранная релаксация (τ≈26 мс, t_to_1%≈0.13 с) заканчивается задолго до пауз 1.55–5 с, а amp-bias при этих паузах остаётся **≈−28 %**. Носитель нестационарности — **не** остаточный потенциал сомы, а состояние с памятью ≥5 с (кандидаты: асимметричный Rm / генератор / LTZ-смежное; отдельный state-probe вне scope E1.3). Расхождение A5/W01 train (~10 %) того же класса, что probe −28 % на AsymRm L=10: лечится не «подождать τ», а **Reset**.

## Импликация F3

[`F3`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) (`ResetNeuronBeforeTrainBurst` / `Neuron->Reset()` перед обучающей пачкой) **подтверждается как обязательный** для детерминированной amp-калибровки: альтернатива «никогда Reset, но пауза по E1.3» **не работает** при паузах ≤5 с на AsymRm. Режим «пауза вместо Reset» потребовал бы τ_state ≫5 с, которого на соме нет.

Связь: E1.2 [`E1_2_REPEATABILITY_2026-10-22.ru.md`](E1_2_REPEATABILITY_2026-10-22.ru.md) → E1.3 (этот файл) → F3 A/B на cold.

## Вердикт

| Критерий §E1.3 | Статус |
|----------------|--------|
| τ_relax / t_to_1% / t_to_noise (AsymRm L=10) | **DONE** |
| Pause-sweep vs E1.2 bias | **DONE** (0.25…5 с, bias≈−28 %) |
| Объясняет ли membrane E1.2/W01 gap? | **Нет** |
| FastSpan | **OPTIONAL DONE** (τ≈6 мс; @2 с bias **+22 %**) |
| Полный NeuronModel-sweep плана | **PENDING** (вне scoped) |
| **Итог E1.3** | **DONE (scoped)** |

**Машиночитаемо:** [`E1_3_RELAXATION_2026-10-22.tsv`](E1_3_RELAXATION_2026-10-22.tsv), [`E1_3_PAUSE_SWEEP_2026-10-22.tsv`](E1_3_PAUSE_SWEEP_2026-10-22.tsv), [`E1_3_RELAXATION_2026-10-22.json`](E1_3_RELAXATION_2026-10-22.json). Рантайм: `$HOME/TLAgent-20261020/scratch/E1_3/`, `agent-reports/E1_3_20261022/`.
