# План: классификация SoftCold FAIL + отложенный retest с увеличенным `-t`

Статус: **done** (все P0 extended Need=1; дальше не множить `-t` → AmpNorm fix).  
Манифест: `EXTENDED_TIME_MANIFEST.txt` — fs25 `-t 640` + asym50/100 `-t 1280`. Phase6 **не** в P0.  
Итог: 4/4 `rc=1`; fs25 TipR mid-band dend2; asym* TipR@Rmin + Need=1.  
Harness: `posttune_verify --train-t` / `--max-polls`.

## 0. Уточнение после timing-разбора (2026-09-27)

См. [TIMING_SPAN_MISMATCH.ru.md](TIMING_SPAN_MISMATCH.ru.md).

| timing_tag | Extended `-t`? |
|------------|----------------|
| `timing_ok_budget` (fs25_gen, …) | **Да** — P0 манифест |
| `timing_softcold_desync` (asym50/100) | **Нет**, пока soft-cold/SBM не починен |
| `timing_est_delay_vs_span` (phase6_*) | Только 1× probe; не жечь ×4 |
| `timing_n/a_quality` (asym25, br25) | Нет |

Манифест P0 сейчас: только `fs25_gen` (+ будущие fs* с тем же паттерном). Phase6 убраны из P0 extended.

## 1. Таксономия провалов (уже разобранные)

| subtype | failure_class | Смысл | Лечится большим `-t`? |
|---------|---------------|-------|------------------------|
| **A_nonseparable_mid** | `gate_fail` | Need=0, tipr=canon, FLAG `result=2` `landscape_ok=0` mid=1 | **Нет** — Train уже Done; проблема mid/LandscapeOk |
| **B_tipr_frozen_cold** | `train_incomplete` | Need=1, TipR=`86e6×4`, L=`1 1 1 1` за весь budget | **Частично / сомнительно** — сначала проверить, стартует ли TipR вообще; иначе не время |
| **B_partial_growth_need1** | `train_incomplete` | Need=1, L/TipR уже выросли (часто ≈gold), нет flag Done | **Да — приоритет** — похоже на нехватку sim-time до `EndOfLearning` |

Машиночитаемый снимок текущих кейсов: [`FAIL_TAXONOMY.json`](FAIL_TAXONOMY.json).

### Уже классифицированные кейсы

| case | train_t сейчас | subtype | Notes |
|------|----------------|---------|-------|
| `asym25_preinh` | 160 | A_nonseparable_mid | Не в extended-time queue |
| `br25_on` | 320 | A_nonseparable_mid | Не в extended-time queue |
| `asym50_preinh` | 640 | B_tipr_frozen_cold | Probe×2 time **или** отдельная диагностика TipR-start |
| `asym100_preinh` | 640 | B_tipr_frozen_cold | то же |
| `asym100_gen` | 640 | B_tipr_frozen_cold | то же |
| `fs25_gen` | 160 | B_partial_growth_need1 | **P0 extended**: L=gold, TipR почти gold, Test Acc 8/8 |
| `phase6_thr_only` | 900 | B_partial_growth_need1 | **P0 extended** |
| `phase6_preinh250` | 900 | B_partial_growth_need1 | **P0 extended** |
| `phase6_ltzcal_twin` | 900 | B_partial_growth_need1 | **P0 extended** |

По мере окончания Phase 5: для каждого нового FAIL дописать строку в JSON + таблицу (скрипт ниже).

## 2. Политика повторов с увеличенным временем

### Делать (очередь `extended_time`)

1. Все **B_partial_growth_need1** после стабильной классификации.
2. Кандидаты из Phase 5 с тем же паттерном (L выросла / TipR не flat / Need=1 / нет `posttune_complete.flag`).
3. Опциональный **probe** для B_tipr_frozen: один кейс (`asym50_preinh`) с ×2 — если TipR так и flat → **не** жечь wall-clock на ×4; завести отдельный bugdoc «TipR never starts».

### Не делать через больший `-t`

- **A_*** (NonSeparable / silent mid при Need=0) — сначала quality/mid research, не budget.
- PASS / gate_fail при уже Need=0 и usable mid.

### Множители (предложение)

| Базовый train_t | Extended train_t | max_polls* |
|-----------------|------------------|------------|
| 160 | **640** (×4) | 801 |
| 320 | **960** (×3) | 801 |
| 640 | **1280** (×2) | 801 |
| 900 | **1800** (×2) | 1001 |

\* Сейчас `wait_train` по умолчанию `max_polls=401` (~3.3 h wall при 30 s). Для extended **обязательно** поднять polls, иначе −t вырастет, а harness убьёт NM раньше по poll-cap (как asym50).

Правило: `max_polls >= ceil(expected_wall_s / 30) + 50`, где wall roughly ∝ train_t × cost_per_sim_second (для fs25: t=160 → ~48 min wall ⇒ ~0.3 min wall / sim-s).

## 3. Как запустить позже (не сейчас)

Не менять дефолтные `CASES[].train_t` в реестре «тихо». Отдельный прогон:

```bash
# черновик API (реализовать перед прогоном):
#   SOFTCOLD_TRAIN_T_MULT=4 SOFTCOLD_MAX_POLLS=801 \
#   python3 .../posttune_verify.py --case fs25_gen
# или batch:
#   scripts/softcold_extended_time_batch.sh
```

Минимальная доработка harness (когда дойдём до исполнения):

1. CLI/env: `--train-t-override` / `SOFTCOLD_TRAIN_T` и `--max-polls` / `SOFTCOLD_MAX_POLLS`.
2. В provenance писать `train_t_effective`, `max_polls`, `retest_class=extended_time`.
3. Строки EXPERIMENTS: тот же Имя EXP, протокол `SoftCold+PostTune`, примечание `extended_t=…` (не новый алгоритм).

Манифест очереди (заполнить после Phase 5):

`Bin/Configs/SpikeSamples/StructTrain/_repro/EXTENDED_TIME_MANIFEST.txt` — по одному case на строку.

Черновик P0 манифеста **уже сейчас**:

```
fs25_gen
phase6_thr_only
phase6_preinh250
phase6_ltzcal_twin
```

После Phase 5 добавить все новые `B_partial_growth_need1`; `fs25_preinh` / `fs50_*` / `ltz*` — по факту taxonomy.

## 4. Критерии успеха extended-retest

| Исход | Значение |
|-------|----------|
| Need=0 + tipr=canon + gate PASS | Cold PASS — обновить EXPERIMENTS/SUCCESSFUL |
| Need=0 + tipr=canon + gate_fail NonSeparable | Переклассифицировать в **A_***; время больше не крутить |
| Need=1, L/TipR ближе к gold | Ещё один шаг ×2 **один раз**, потом stop |
| Need=1, TipR всё ещё flat cold | **B_tipr_frozen** confirmed; stop extended; отдельная диагностика |

## 5. Чеклист (исполнение)

- [x] SoftCold S3.c/d / DEFER queue завершена (`DONE_TAILS`)  
- [x] Harness `--train-t` + `--max-polls`  
- [x] P0 extended прогнан (fs25+asym50/100_*)  
- [x] PARALLEL=1; phase6 не в extended  
- [x] LandscapeOk не ослабляли  
- [x] Stop extended: Need=1 на всех → [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md)

## 6. Обновление taxonomy после каждого FAIL

```bash
python3 Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/refresh_fail_taxonomy.py
# (создать при исполнении; логика уже прототип в сессии → FAIL_TAXONOMY.json)
```

Пока скрипта нет — вручную дописывать в JSON/таблицу §1 после каждого `SOFTCOLD_DEFER_rcs` END.
