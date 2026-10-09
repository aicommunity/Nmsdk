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
4. **Реестр SoftCold:** после матрицы — `scripts/apply_softcold_rcs_to_registry.py --rcs _repro/SOFTCOLD_HEAD_rcs.txt` (пишет **SoftCold** / **SoftColdDetail** на все строки Имени; **Working**↑ только при SoftCold PASS). Лестница Working: SoftCold > SoftColdOff > SkipTrainGold > GoldTest ≈ MatrixClone. HEAD `PASS`|`FAIL`|`NOT_RETESTED`.
5. **PASS** → те же разделы/колонки в `SUCCESSFUL_EXPERIMENTS.md`. **FAIL**-строки в таблицы PASS не класть; причины — блок «Провалы / вне PASS» (полный FAIL — в `EXPERIMENTS.md`).
6. Гипотезы без различия (soft vs strip, AutoScale) — **примечание** к SoftCold-строке, не новые «эксперименты».
7. GoldTest/MatrixClone PASS **≠** SoftCold. См. [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](../../../Docs/Audit/TimeLearner-2026-09-26-review/evidence/PROTOCOL_WORKING_VS_LASTCHECK.ru.md).
8. Full SoftCold: `PARALLEL=8` `scripts/softcold_full_matrix_parallel.sh`; W3 (`EnableRmaxLengthEscape`) off. Cold reset preserves the configured initial TipR; `--max-rs-rm` remains a diagnostic override for the derived upper bound, not an initial-Rs setting.

## Запреты

- Не создавать отдельную секцию «кампания PostTune / §A».
- Не ослаблять LandscapeOk / ok_audit пороги ради PASS.
- Не коммитить `_work/`, StatisticLog, огромные archives (см. `nmsdk-gitlinks`).
- Не писать absolute `ResistanceMin` в soft-cold XML; bounds — derived state из C++.

## Колонки строки реестра

`Имя | Алгоритм | Параметры | Working | Acc | Цель | SoftCold | SoftColdDetail | HEAD | PHASE12 | Примечание | Конфиги`
