# Статус аудита TimeLearner Cold 2026-09-26

Дата обновления: 2026-10-16 22:49 MSK.

## Текущий этап расследования

Основной аудит исторических результатов и подтверждённых дефектов выполнен; текущая работа — выборочная проверка исправленной Release-сборки, отдельно для сходимости C++-обучения и качества классификации. Полный повтор матрицы не запускается.

**Обновление 22:49 MSK:** контрольный Classic W01/50/N0 с step-down исправлением завершён. C++-обучение сошлось до сохранённого `Need=0` после перехода на принятый нижний count `N=98`; Test-gate завершился штатно, но результат классификации — `NonSeparable`, цель не обнаружена, Acc `7/8`, FP `0/7`. Исходники и бинарник оставались неизменны; входные копии Train/Test совпадают с парной попыткой, а изменение рабочей копии Train-конфига отражает запись результата обучения. Подробности и SHA артефактов: [результат запуска](../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/diagnostics/w01_classic_structural_2026-10-16/README.ru.md). Это выборочная проверка исправления, а не завершение всего аудита сходимости.

- Ветка расследования: `codex/historical_view`; новые коммиты локальные, push пока не выполнялся. Экспериментальный исходный снимок: root `16d87dd`, PulseLib `56a5962`, Bin `cfc5bcf`, Rdk `b3b2472`.
- Основной текущий разбор результатов и ограничений причинного вывода: [ATTENUATION_GAMMA_AND_STRUCTURAL_STEP_2026-10-16.ru.md](evidence/ATTENUATION_GAMMA_AND_STRUCTURAL_STEP_2026-10-16.ru.md).
- `.11`: Branch W04/100/N1 PSI off повторно достиг `Need=0`; Test снова дал импульс на всех восьми паттернах (`Acc=1/8`, FP `7/7`). Архив старого full-matrix запуска показывает совпадение фактических Train/Test Model и Parameters, кроме диагностического `DebugModeFlag`; старый запуск после `iter=100` застрял с невалидными пиками и Rs ниже нового no-crossing floor. Причинность пока требует изоляции, поскольку менялись и другие правила Branch.
- `.11`: два положительных контроля W10 завершены на Release, RUN_ID `w10-positive-controls-16d87dd-20261016-01`; оба обучения достигли `converged_posttune_finalized`. Сопоставление точного исторического протокола показало: `br25_nextseg` снова дал 8/8, FP=0; `br50_gen` сошёлся, но C++ Test-mid теперь `NonSeparable` (`mid=1`), поэтому цель не сработала, Acc=7/8. У `br50_gen` исторический C++ Test-mid был разделяющим (`mid=0.0549386`), 8/8. Входные Train/Test-файлы совпадают побайтно с исторической матрицей; отличие наблюдается в обученном состоянии, не в выборе другого шаблона.
- `.17`: все повторы завершились; при проверке в 21:22 MSK активных `NeuroModelerConsole` не было. Classic W01/50/N0 Step=86 МОм и с включённым квантованным acceptance остановились с `Need=1` и без C++-отказа; Test не запускался. Branch W04/480/N0 остановился с `Need=1` для Step=86 МОм и Step=1 ГОм при `-t=900`, а также для Step=1 ГОм при `-t=1200`; Test не запускался. Длины/метрики и RunID внесены в основной отчёт и пакет diagnostics. На `.17` осталось около 2.2 ТиБ свободного места; idle tmux не выполняет обучение.
- `.11`: при проверке в 21:23 MSK активных `NeuroModelerConsole` не было; сохранена idle tmux-сессия сборки. На системном диске около 151 ГиБ свободно.
- Текущий вывод: W01/50/N0 с каноническим Step=1 ГОм достиг `Need=0` только через best-effort при `N=128` и не обнаружил цель (`Acc=7/8`, FP=0). На Step=86 МОм EOL амплитуды не достигнут даже с `AcceptQuantizedAmpUnderTarget=1`: повторяемый нижний/верхний bracket не подтверждён. Branch W04/480/N0 на проверенных Step/лимитах не синхронизировался; `MaxDendriteLength=100` буквально не достигнут (максимум 91). Неполные случаи не имеют результатов классификации.
- Анализ полного W01 audit уточнил причину. Для измеренного `N=99`, `L=15`, `Rs=86 МОм` и того же импульса есть 122 точных валидных измерения `0.0150701376` после `Neuron->Reset()` и 55 точных `0.0134861214` без reset; цель `0.0143095308`. Структура не менялась, но динамические начальные условия чередуются: reset вызывается после структурной мутации, а между неизменившимися итерациями его нет.
- В этой же трассе tracker подтвердил нижний `N=98` для соседней верхней точки `N=99`, однако Classic оставил текущий верхний count 99 без шага вниз (`synapse_status=0`), после чего warm-state наблюдение сбросило bracket. Classic-only правка теперь интегрирует переход к уже принятому нижнему count; C++ unit-проверка собрана, `PulseLib_StorageComponents` прошёл в Release. Контрольный W01 Step=86 МОм/quantized повтор на `.17` выполняется; Branch не менялся — сохранённых Branch-трасс с включённым quantized acceptance не найдено.
- Полная трасса исходного 401-итерационного повтора сохранена вместе с provenance. Дальнейшие коммиты по этому активному плану оставлять локальными без push.
- В 22:24 MSK этот Classic W01/50/N0 повтор был ещё активен на `iter=127`; это историческая промежуточная отметка, заменённая терминальным результатом выше. Финальная запись: переход `N=99→98` на итерации 138, обе EOL истинны на итерации 139, сохранён `Need=0`; Test завершился `NonSeparable`, цель отсутствует, Acc `7/8`, FP `0/7`. Сырой audit SHA `321cbca6…`, размер 292768 байт; тяжёлая трасса остаётся на Data-диске `.17`.
- Восстановлена сетевая доступность обоих экспериментальных серверов через `.12`: `.17` доступен, Classic повтор остаётся активным; `.11` отвечает по SSH через `.17`, активных `NeuroModelerConsole` на нём не обнаружено. Его старая tmux-сессия сборки сейчас стоит в shell prompt; данных или артефактов не удалял.
- Сверка основных каталогов `/home/user/Nmsdk` выявила устаревшие и грязные checkout: на `.17` root `c0ce4280` отстаёт от upstream на 215 коммитов, локально изменены gitlinks PulseLib/Bin и Integration test, есть `EventsLog`; на `.11` root `14783af1` отстаёт на 218 коммитов, изменён тот же Integration test и лежит набор старых untracked metrics/monitor outputs. На `.11` обычный `git status` также упирается в недоступный Rdk submodule path, ведущий в удалённый worktree. Эти каталоги не обновлялись и не очищались; точечный запуск идёт в изолированном worktree `.17`, а не в них.
- Снимок работающего worktree `.17` `16d87dd` — предок локального root `b91616e` на 20 коммитов до текущего документального коммита; его PulseLib `56a5962` — предок локального `7c8f6f2`, содержащего Classic step-down fix. Bin `cfc5bcf` отстаёт от локального `ab882f23` на шесть коммитов (архив результатов и diagnostics, правка теста безопасности runner). Для этого повтора отдельно сверены SHA всех восьми входов Train/Test: они совпадают с предыдущей W01/50/N0 попыткой; различие root/Bin не меняет алгоритм PulseLib или входы данного случая.

Изменённый uncommitted `Test_PulseLib_TimeLearnerResistance.cpp` на `.11` содержит 41 тестовый case; все эти имена уже присутствуют в текущем локальном файле. Содержимое на сервере оставлено нетронутым, а локальный вариант сохраняет дополнительные тесты текущей ветки плюс новый тест Classic step-down.

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
