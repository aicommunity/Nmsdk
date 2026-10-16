# Статус аудита TimeLearner Cold 2026-09-26

Дата обновления: 2026-10-16 21:23 MSK.

## Текущий этап расследования

Основной аудит исторических результатов и подтверждённых дефектов выполнен; текущая работа — выборочная проверка исправленной Release-сборки, отдельно для сходимости C++-обучения и качества классификации. Полный повтор матрицы не запускается.

- Ветка расследования: `codex/historical_view`; документы аудита коммитятся локально, push не выполнялся. Экспериментальный исходный снимок: root `16d87dd`, PulseLib `56a5962`, Bin `cfc5bcf`, Rdk `b3b2472`.
- Основной текущий разбор результатов и ограничений причинного вывода: [ATTENUATION_GAMMA_AND_STRUCTURAL_STEP_2026-10-16.ru.md](evidence/ATTENUATION_GAMMA_AND_STRUCTURAL_STEP_2026-10-16.ru.md).
- `.11`: Branch W04/100/N1 PSI off повторно достиг `Need=0`; Test снова дал импульс на всех восьми паттернах (`Acc=1/8`, FP `7/7`). Архив старого full-matrix запуска показывает совпадение фактических Train/Test Model и Parameters, кроме диагностического `DebugModeFlag`; старый запуск после `iter=100` застрял с невалидными пиками и Rs ниже нового no-crossing floor. Причинность пока требует изоляции, поскольку менялись и другие правила Branch.
- `.11`: два положительных контроля W10 завершены на Release, RUN_ID `w10-positive-controls-16d87dd-20261016-01`; оба обучения достигли `converged_posttune_finalized`. Сопоставление точного исторического протокола показало: `br25_nextseg` снова дал 8/8, FP=0; `br50_gen` сошёлся, но C++ Test-mid теперь `NonSeparable` (`mid=1`), поэтому цель не сработала, Acc=7/8. У `br50_gen` исторический C++ Test-mid был разделяющим (`mid=0.0549386`), 8/8. Входные Train/Test-файлы совпадают побайтно с исторической матрицей; отличие наблюдается в обученном состоянии, не в выборе другого шаблона.
- `.17`: все повторы завершились; при проверке в 21:22 MSK активных `NeuroModelerConsole` не было. Classic W01/50/N0 Step=86 МОм и с включённым квантованным acceptance остановились с `Need=1` и без C++-отказа; Test не запускался. Branch W04/480/N0 остановился с `Need=1` для Step=86 МОм и Step=1 ГОм при `-t=900`, а также для Step=1 ГОм при `-t=1200`; Test не запускался. Длины/метрики и RunID внесены в основной отчёт и пакет diagnostics. На `.17` осталось около 2.2 ТиБ свободного места; idle tmux не выполняет обучение.
- `.11`: при проверке в 21:23 MSK активных `NeuroModelerConsole` не было; сохранена idle tmux-сессия сборки. На системном диске около 151 ГиБ свободно.
- Текущий вывод: W01/50/N0 с каноническим Step=1 ГОм достиг `Need=0` только через best-effort при `N=128` и не обнаружил цель (`Acc=7/8`, FP=0). На Step=86 МОм EOL амплитуды не достигнут даже с `AcceptQuantizedAmpUnderTarget=1`: повторяемый нижний/верхний bracket не подтверждён. Branch W04/480/N0 на проверенных Step/лимитах не синхронизировался; `MaxDendriteLength=100` буквально не достигнут (максимум 91). Неполные случаи не имеют результатов классификации.
- Следующий диагностический шаг — проверить вариацию пика при одинаковом структурном состоянии (`N`, длины, `Rs`, входной импульс), затем отдельно решить, есть ли дефект измерения/учёта либо нужна другая политика квантованного acceptance. До этого изменения C++-логики не обоснованы. Основной отчёт и компактные артефакты готовы к фиксации; push не выполнялся.

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
