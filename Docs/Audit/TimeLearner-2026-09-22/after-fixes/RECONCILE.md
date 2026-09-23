# Сверка исправлений с аудитом TimeLearner-2026-09-22

Дата: 2026-09-23 (follow-up F1–F5). Машинный статус: [status.json](status.json).

## Таблица ID

| ID | Статус | Доказательство |
|----|--------|----------------|
| A01 | closed | Dataset expected stim count; Branch `NeuronTimeLearnerBranch.DatasetMatrix` bind; legacy `IsPatternComplete>=4` |
| A02 | closed | `trial_observe_until_` = last_stim + LateResponseWindow |
| A03 | closed | Immutable label at BeginTrial; coincident Close→Begin→attr |
| A04 | closed | Injective per_stim C++/Python |
| A05 | closed | `metrics_version=2`, foil spikes → FP |
| A06 | closed | `last_pulse_ok` = sum(ISI); legacy retained |
| A07 | accepted | Не менялся (calibration-quality) |
| A08 | closed | `LandscapeOk` isfinite; silent mid; `PostTuneResult` |
| A09 | closed | Branch clear metrics + setup_failure; TL Search reprobe |
| A10 | closed | Branch LTZ pure; LiveMetric mode-aware |
| A11 | closed | NAxoneDelay/NPulseDelay N ticks |
| A12 | deferred | Без изменений; probe `PositiveTau…` diagnostic FAIL |
| A13 | closed | Preinh ApplyElementDefaults |
| A14 | closed | segment∩rect in router |
| A15 | closed | Console latch + AppCore exit |
| A16 | closed | `posttune_verify` provenance SHA + expect_tipr; units 15/15 |

## Probes (after-fixes)

- GUI 13/13 PASS — [gui-tests.xml](gui-tests.xml)
- CE gate 9/9 PASS (без A12) — [cpp-counterexamples.xml](cpp-counterexamples.xml)
- Branch 8/8 PASS — [branch-tests.xml](branch-tests.xml)
- Console SHA — [NeuroModelerConsole.sha256](NeuroModelerConsole.sha256)

## Этап 7 (cold replay) — partial

Прогон `posttune_verify` soft_cold → Train → gate, `quality_class=calibration-quality`.

| case | verdict |
|------|---------|
| asym50 | **PASS** mid_source=cpp fires=10000000 |
| br100_search | **PASS** search_reverted mid=cpp fires=10000000 |
| br25_on / br25_off / asym25 / br100_keep / phase6_480 | **FAIL** |

Gold Branch Test на новом Console: fires=10000000 mid≈0.0718 (inherited weights). Soft_cold Branch retrain даёт NonSeparable / fires≠expect — отдельный follow-up, не ослабление критериев.

Сводка: `_repro/POSTTUNE_VERIFY_RESULT.md` § Calibration-quality follow-up 2026-09-23.

## Follow-up

См. [follow-up-plan.md](follow-up-plan.md).
