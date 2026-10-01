# Working vs LastCheck — контракт колонок реестра

Дата: 2026-10-01.

## Зачем

PASS **GoldTest** / **MatrixClone** не означает, что **SoftCold** (обучение C++ с нуля) работает. Одна колонка «Протокол» это смешивала.

## Колонки

| Колонка | Смысл |
|---------|--------|
| **Working** | Самый сильный протокол с HEAD **PASS** для канонического **Имени** |
| **LastCheck** | Протокол **этой** строки проверки + вердикт |

Лестница: `SoftCold` > `SoftColdOff` > `SkipTrainGold` > `GoldTest` ≈ `MatrixClone` > `none`.

## Примеры

| Имя | Working | LastCheck (пример строки) |
|-----|---------|---------------------------|
| EXP_br_span25…gen | SkipTrainGold | GoldTest PASS — на gold-строке; Working выше из-за SkipTrainGold PASS |
| EXP_span50ms…preinh | GoldTest | SoftCold FAIL (B_need1) — cold не PASS |

Файлы: [`EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md), [`SUCCESSFUL_EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md).  
Миграция: `scripts/migrate_registry_working_lastcheck.py`.
