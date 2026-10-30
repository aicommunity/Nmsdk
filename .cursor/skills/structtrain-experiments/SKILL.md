---
name: structtrain-experiments
description: >-
  Runs StructTrain cold/PostTune experiments via posttune_verify and updates
  EXPERIMENTS.md / SUCCESSFUL_EXPERIMENTS.md by canonical algorithm. Also
  governs TimeLearner dual-track audit docs (Docs/Audit/TimeLearner-*), matrix
  queue cold runs, Branch/Classic labeling, and experiment write-ups. Use when
  the user mentions StructTrain, soft-cold, PostTune, posttune_verify, Acc,
  Цель, experiment registry, TimeLearner matrix, dualtrack, BR-D*, PASS×3,
  Classic W01, or retesting TimeLearner selectivity configs.
---

# StructTrain: эксперименты и реестр

## Когда читать

Сразу при запросах про cold/PostTune StructTrain, матрицу TimeLearner, dual-track аудит (`Docs/Audit/TimeLearner-*`), или обновление реестра. Детали case→EXP: [reference.md](reference.md). Сборка runtime — скилл `nmsdk-build`; gitlinks/тяжёлые артефакты — `nmsdk-gitlinks`.

## Требования к постановке и выводам

1. **Всегда писать постановку и выводы развернутыми предложениями.**
2. В chat-тиках, STATUS, SYNTHESIS, boundary maps и `N1_EXECUTE_*` не ограничиваться одними табличными ярлыками: к таблице или списку RUN добавлять 2–5 предложений — что проверяли, при каком Trainer/Track/Host/SHA, чем кончилось и что из этого следует для следующего шага.
3. Разделять **Trainer=Branch** и **Trainer=Classic**; не смешивать PASS×3 Branch с Classic W01 в одной «общей» таблице без колонки Trainer.
4. Cold execute только после явного «запускай» / execute; docs-ready ≠ cold start. Лимиты Console: `.11` ≤8, `.17` ≤12, если кампания dual-host.
5. PASS×3 regress не стартовать молча: либо после Branch-фикса на том же SHA, либо по явному arm.

## Иерархия группировки результатов (обязательно)

Во всех audit-отчётах и сводных таблицах группировать **сверху вниз**:

1. **Trainer × Mode** — четыре корзины: Classic×N0, Classic×N1, Branch×N0, Branch×N1.  
   N0 = чисто структурный; N1 = структурная sync + параметрическая TipR. Ярлыки кампании M0/M1 = те же Mode (`N0/N1 (равн. M0/M1 track)`).
2. **Span** — 25 / 50 / 100 / 480 мс (ось паттерна по времени).
3. **NeuronModel** — baseline / AsymRm / FastSpan / LTZ / … (**не** называть это «семьёй паттерна»: при одном Span ISI часто общий).
4. **Строки = Mod** (`gen` / `preinh` / `nextseg` / …); **колонки = PostTune ON / OFF** (+ Host, RUN_ID, SHA).
5. **Ссылки на конфиги Train и Test** — в каждой строке сводной / evidence-таблицы обязательна колонка (или явные markdown-ссылки) на каталоги **Train** и **Test**, по которым получен результат: для matrix HIST обычно `source_config` из `TimeLearnerMatrix/matrix.json` → `Bin/Configs/SpikeSamples/StructTrain/<source_config>/{Train,Test}`; для factor-variant / W01 без `source_config` — prepared inputs `TimeLearnerMatrix/<WAVE>/inputs/<case_id>/{Train,Test}` (и при необходимости указать исходный шаблон из `matrix_input_manifest.json`). Не ограничиваться одним именем EXP без пары Train/Test.

Канон: [`Docs/Audit/TimeLearner-2026-09-26-review/evidence/RESULT_GROUPING_HIERARCHY.ru.md`](../../../Docs/Audit/TimeLearner-2026-09-26-review/evidence/RESULT_GROUPING_HIERARCHY.ru.md).  
Семья Branch×FastSpan: `Bin/Configs/SpikeSamples/StructTrain/SelectivityBranchFastSpan/` (EXP `EXP_br_fs_span…`).  
PostTune (PulseLib ≥`d52dc1c`): ideal LandscapeOk → tiny-gap best-effort mid → иначе silent mid для Test inference; TipR KeepDone только явным tip-mode / PostTune OFF (не auto-revert — иначе ломается PASS×3 preinh).

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

## Matrix PostTune ON/OFF (immutable inputs)

Для парных cold ON/OFF **не** патчить `TimeLearnerMatrix/matrix.json` и **не** делать `--prepare --refresh` ради переключения PostTune: shared `TimeLearnerMatrix/<WAVE>/inputs/` иммутабельны и засоряются чужим `EnablePostTrainTuning`.

Правильный путь — attempt-local override очереди:

```bash
python3 scripts/run_timelearner_matrix_queue.py \
  --run-id <id> --waves <WAVE> --cases <CASE...> --jobs N \
  --force-posttrain-tuning 0|1 \
  --no-commit --allow-repeat
```

Флаг пишет overlay в attempt + `worker_config.enable_posttrain_tuning` (posttune_verify читает его); канонические inputs и `matrix.json` не меняются. Лаунчеры dual-host: `TimeLearnerAudit-…/dualtrack/run_ptfix_v5_complete.sh`, `run_n1_a21_ptoff.sh`. `--prepare WAVE --case-ids <missing…>` без `--refresh` — только если нет `matrix_input_manifest.json` (не гонять весь wave, если соседние snapshots дрейфуют).

## Запреты

- Не создавать отдельную секцию «кампания PostTune / §A».
- Не ослаблять LandscapeOk / ok_audit пороги ради PASS.
- Не коммитить `_work/`, StatisticLog, огромные archives (см. `nmsdk-gitlinks`).
- Не писать absolute `ResistanceMin` в soft-cold XML; bounds — derived state из C++.
- Не патчить `matrix.json` / не `--prepare --refresh` shared inputs для PostTune ON/OFF — только `--force-posttrain-tuning`.

## Колонки строки реестра

`Имя | Алгоритм | Параметры | Working | Acc | Цель | SoftCold | SoftColdDetail | HEAD | PHASE12 | Примечание | Конфиги`
