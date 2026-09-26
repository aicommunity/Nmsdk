---
name: structtrain-experiments
description: >-
  Runs StructTrain cold/PostTune experiments via posttune_verify and updates
  EXPERIMENTS.md / SUCCESSFUL_EXPERIMENTS.md by canonical algorithm. Use when
  the user mentions StructTrain, soft-cold, PostTune, posttune_verify, Acc,
  Цель, experiment registry, or retesting TimeLearner selectivity configs.
---

# StructTrain: эксперименты и реестр

## Когда читать

Сразу при запросах про cold/PostTune StructTrain или обновление реестра. Детали case→EXP: [reference.md](reference.md).

## Ось учёта

- Реестр ведётся по **алгоритму + параметрам** (каноническое **Имя** EXP), не по кампании retest.
- `…_posttune` / `_off` / `_keep` / `_search` — **work-клоны**, не отдельные алгоритмы; в таблице — ссылка в Конфиги.
- Разные протоколы одного канона — **соседние строки** с тем же Именем.
- PHASE12 `VALIDATED` ≠ HEAD PASS. Narrative фиксов — не ось реестра.

Документы:

- [`Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md)
- [`Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md)
- Контракт: [`POST_TRAIN_VERIFY.ru.md`](../../../Bin/Configs/SpikeSamples/StructTrain/POST_TRAIN_VERIFY.ru.md)
- Narrative: [`Docs/Audit/TimeLearner-2026-09-24-review/EXPERIMENTS_AFTER_FIXES.ru.md`](../../../Docs/Audit/TimeLearner-2026-09-24-review/EXPERIMENTS_AFTER_FIXES.ru.md)

## Workflow

1. **Сборка runtime** — скилл `nmsdk-build`; зафиксировать sha256 Console, PulseLib, Bin.
2. **Прогон** из корня Nmsdk / StructTrain scripts:
   ```bash
   python3 Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py --case <case>
   # GoldTest (NOT_RETESTED, без Train):
   python3 Bin/Configs/SpikeSamples/StructTrain/scripts/gold_retest_batch.py \
     --manifest Bin/Configs/SpikeSamples/StructTrain/_repro/NOT_RETESTED_manifest_YYYYMMDD.txt
   ```
   По умолчанию: clean workdir. **Не** `--allow-salvage` / `--use-archive-inplace` без явной просьбы.
3. **Метрики:** Acc `N/8`, Цель `да`/`нет`/`—`, fires, Need, mid, Result/NonSeparable; bundle `_repro/runs/<id>/`.
4. **Реестр:** обновить/добавить строку у **канонического Имени** с протоколом (`GoldTest` | `SoftCold+PostTune` | `SkipTrainGold` | `SoftCold+PostTuneOff` | `MatrixClone`) и HEAD `PASS`|`FAIL`|`NOT_RETESTED`.
5. **PASS** → та же логика в `SUCCESSFUL_EXPERIMENTS.md`. **FAIL** — только в `EXPERIMENTS.md`.
6. Гипотезы без различия (soft vs strip, AutoScale) — **примечание** к SoftCold-строке, не новые «эксперименты».

## Запреты

- Не создавать отдельную секцию «кампания PostTune / §A».
- Не ослаблять LandscapeOk / ok_audit пороги ради PASS.
- Не коммитить `_work/`, StatisticLog, огромные archives (см. `nmsdk-gitlinks`).

## Колонки строки реестра

`Имя | Алгоритм | Параметры | Протокол | Acc | Цель | Режим | HEAD | PHASE12 | Примечание | Конфиги`
