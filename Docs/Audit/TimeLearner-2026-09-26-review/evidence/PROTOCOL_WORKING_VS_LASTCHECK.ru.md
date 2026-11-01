# Working vs SoftCold — контракт колонок реестра

Дата: 2026-10-08 (после миграции SoftCold-колонок).

## Зачем

PASS **GoldTest** / **MatrixClone** не означает, что **SoftCold** (обучение C++ с нуля) работает. Старая колонка **LastCheck** путала: на gold-строке оставался `GoldTest PASS`, хотя SoftCold для того же Имени уже прогоняли.

## Колонки (актуальные)

| Колонка | Смысл |
|---------|--------|
| **Working** + **Acc** + **Цель** | Самый сильный протокол с HEAD **PASS** и его метрики |
| **SoftCold** | Вердикт последней SoftCold-матрицы для Имени: `PASS` / `FAIL` / `—` |
| **SoftColdDetail** | `case`, `tipr_class`, `failure_class`, `gate_rc`, `train_status`, notes, bucket |

Лестница Working: `SoftCold` > `SoftColdOff` > `SkipTrainGold` > `GoldTest` ≈ `MatrixClone` > `none`.

## Пример

| Имя | Working | Acc | SoftCold | SoftColdDetail (сокр.) |
|-----|---------|-----|----------|------------------------|
| EXP_br_span25…gen | SkipTrainGold | 8/8 | **FAIL** | case=br25_on; fc=gate_fail; bucket=N; also br25_off:PASS |
| EXP_span50ms…preinh | SoftCold | 8/8 | **PASS** | case=asym50_preinh; tipr=canon; fc=ok |

Сводка всех 49 case: § «SoftCold last matrix» в [`EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md).  
Apply: `scripts/apply_softcold_rcs_to_registry.py`. Миграция: `scripts/migrate_experiments_softcold_columns.py`.
