# Статус аудита TimeLearner Cold 2026-09-26

Дата обновления: 2026-10-16 20:07 MSK.

## Текущий этап расследования

Основной аудит исторических результатов и подтверждённых дефектов выполнен; текущая работа — выборочная проверка исправленной Release-сборки, отдельно для сходимости C++-обучения и качества классификации. Полный повтор матрицы не запускается.

- Ветка расследования: `codex/historical_view`; актуальный локальный root HEAD `31767d7`. Экспериментальный исходный снимок: root `16d87dd`, PulseLib `56a5962`, Bin `cfc5bcf`, Rdk `b3b2472`.
- Основной текущий разбор результатов и ограничений причинного вывода: [ATTENUATION_GAMMA_AND_STRUCTURAL_STEP_2026-10-16.ru.md](evidence/ATTENUATION_GAMMA_AND_STRUCTURAL_STEP_2026-10-16.ru.md).
- `.11`: Branch W04/100/N1 PSI off достиг `Need=0`, но Test дал импульс на всех восьми паттернах (`Acc=1/8`, FP `7/7`); цель обнаружена, разделение не прошло.
- `.17`: продолжаются два опыта — Classic W01/50/N0 Step=86 МОм (poll 324/401) и Branch W04/480/N0 Step=1 ГОм с `-t=1200` (poll 272/401). На последнем снимке оба имели `Need=1` без C++-отказа и ещё не дошли до Test.
- После завершения активных повторов остаётся разобрать сравнение с историей, выполнить только необходимые точечные контроли, обновить итоговую классификацию причин и зафиксировать документы/результаты коммитом.

Ниже сохранён исторический снимок SoftCold full49 от 2026-10-09; он не описывает текущую кодовую базу или текущий статус обучения.

## Политика обучения (исторический срез на 2026-10-09)

| | |
|--|--|
| PulseLib | `b5229e4` (`rsrm-min-20261008`) |
| Console SHA16 | `39edc03c82665dba` |
| W3 (`EnableRmaxLengthEscape`) | **off** — TipR@Rmax + overshoot → `failure_reason=1`, без length-escape |
| Tip-R bounds | derived: `ResistanceMin/Max` из `MaxSynapseToMembraneResistanceRatio` |
| Обоснование | [`RSRM_MIN_RATIO_FOLLOWUP_2026-10-08.ru.md`](evidence/RSRM_MIN_RATIO_FOLLOWUP_2026-10-08.ru.md) · [`RSRM_D_RETEST_2026-10-08.ru.md`](evidence/RSRM_D_RETEST_2026-10-08.ru.md) |

## Исторический SoftCold full49 HEAD (результат на 2026-10-09)

| | |
|--|--|
| Итог | **0 PASS / 49 FAIL** |
| Console / PulseLib / Bin | `39edc03c82665dba` / `b5229e4` / `6a7ef63a` · PARALLEL=8 |
| RCS / LOG | [`SOFTCOLD_HEAD_rcs.txt`](../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_HEAD_rcs.txt) · [`SOFTCOLD_full_matrix_20261009T001408Z.log`](evidence/metrics/SOFTCOLD_full_matrix_20261009T001408Z.log) |
| SNAP / аудит | [`SOFTCOLD_FULL49_SNAP.md`](evidence/SOFTCOLD_FULL49_SNAP.md) · [`SOFTCOLD_CONVERGENCE_AUDIT.ru.md`](evidence/SOFTCOLD_CONVERGENCE_AUDIT.ru.md) |
| Корзины SNAP | D=24 · B=19 · E=2 · G=2 · N=1 · other=1 |

Доминирует `failure_class=train_incomplete` (`Need=1` до конца `-t`). Подмножество — `cpp_training_failure_1` (TipR@Rmax при W3 off).

Подробный план повторной диагностики причин 0/49, исправления отчётного контура и условных C++-правок: [SOFTCOLD_FULL49_DIAGNOSIS_AND_REMEDIATION.plan.md](evidence/SOFTCOLD_FULL49_DIAGNOSIS_AND_REMEDIATION.plan.md). Он отдельно учитывает прежние 13 PASS, 12 терминальных `ResistanceMax`-отказов, 36 случаев `Need=1` без C++ failure и неизвестный исход `br100_search`.

## Реестр

- Колонки: **Working** / **SoftCold** / **SoftColdDetail** — [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](evidence/PROTOCOL_WORKING_VS_LASTCHECK.ru.md).
- SoftCold-колонки применены из RCS (`apply_softcold_rcs_to_registry.py`); Working↑ только при SoftCold PASS (на этом срезе — ни у кого).
- LandscapeOk / Acc / fires / Need→0 **не** ослаблять.
