# Сверка исправлений с аудитом TimeLearner-2026-09-22

Дата: 2026-09-23. Машинный статус: [status.json](status.json).

## Таблица ID

| ID | Статус | Доказательство |
|----|--------|----------------|
| A01 | closed | Dataset expected stim count; `IsPatternComplete` |
| A02 | closed | `trial_observe_until_` = last_stim + LateResponseWindow |
| A03 | closed | Immutable label at BeginTrial; coincident Close→Begin→attr |
| A04 | closed | Injective per_stim C++/Python |
| A05 | closed | `metrics_version=2`, foil spikes → FP |
| A06 | closed | `last_pulse_ok` = sum(ISI); legacy retained |
| A07 | accepted | Не менялся |
| A08 | closed | `LandscapeOk` isfinite; silent mid; `PostTuneResult` |
| A09 | closed | Branch clear metrics + setup_failure; TL Search reprobe |
| A10 | closed | Branch LTZ pure; LiveMetric mode-aware |
| A11 | closed | NAxoneDelay/NPulseDelay N ticks |
| A12 | deferred | Без изменений |
| A13 | closed | Preinh ApplyElementDefaults |
| A14 | closed | segment∩rect in router |
| A15 | closed | Console latch + AppCore exit |
| A16 | closed | posttune_verify unit 10/10; tipr_snapshot flag |

## Этап 7 (cold replay)

**Заблокирован:** на хосте нет `NeuroModelerConsole`. После пересборки с текущим PulseLib/Bin/Rdk/App — прогон `posttune_verify.py` V1–V6 в `_repro/runs/` с пометкой calibration-quality (A07).

## Follow-up

См. [follow-up-plan.md](follow-up-plan.md).
