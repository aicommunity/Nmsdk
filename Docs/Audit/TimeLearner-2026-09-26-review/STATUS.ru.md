# Статус аудита TimeLearner Cold 2026-09-26

Дата обновления: 2026-10-19 (цикл N+1 **cold closeout**; старт цикла PostTune-fix / оси NeuronModel).  
Канон группировки: [RESULT_GROUPING_HIERARCHY…](evidence/RESULT_GROUPING_HIERARCHY.ru.md).  
План: [POST_P0_SYNTHESIS…](POST_P0_SYNTHESIS_AND_NEXT_CYCLE_2026-10-19.ru.md) · execute: [N1_EXECUTE_READY…](N1_EXECUTE_READY.ru.md).  
PulseLib `20c3e22`. Хосты `.11` ≤8 / `.17` ≤12. Монитор N+1 остановлен ~11:20.  
**Sync `.17`:** 2026-10-19 root `252e2ce6e` / PulseLib `8575df3` / Bin `f8f8d49f` (= `.11` после PostTune-фикса + BranchFastSpan/W48).  
**Cold PostTune-fix (волна1 ON, dual-host):** `.11` `tl-ptfix-w1-11-pton-…` cases `br25_gen`+`br50_gen`; `.17` `tl-ptfix-w1-17-pton-…-br` case `br25_preinh`. Монитор `AGENT_LOOP_TICK_ptfix` каждые 15 мин. Назначение: [DUALHOST_ASSIGNMENT…](evidence/DUALHOST_ASSIGNMENT_POSTTUNE_FIX_2026-10-19.ru.md).

Ниже результаты сгруппированы по иерархии **Trainer×Mode → Span → NeuronModel → Mod** (колонки PostTune ON/OFF). Исторический нарратив dual-track сохранён после этой сводки и не отменяет факты таблиц.

---

## Trainer=Branch · Mode=N1 (равн. BR-M1 track)

### Span=25 мс · NeuronModel=baseline (W10 Branch)

| Mod | PostTune OFF: Need / fires / detected | PostTune ON: Need / fires / detected / notes | SHA / Host / RUN_ID |
|---|---|---|---|
| gen | 0 / `10110000` / **detected** (A2.1) | 0 / `00000000` silence; thr=`1` NonSeparable (N+1 D3) | PL `20c3e22`; OFF `.11` `tl-m1-n1-a21-ptoff-…`; ON `.17` `tl-m1-n1-d3-silence-…` |
| preinh | 0 / `00000000` / silence (A2.1); TipR×0.75 A2.3 тоже silence | 0 / `00000000` silence; thr=`1` (N+1 D3) | те же RUN |
| nextseg | — (PASS исторически с PostTune штатным путём) | **PASS** fires=`10000000` (PASS×3 d2v4) | `tl-m1-pass-regress-d2v4-17-…` / `.17` |

A2.3 (TipR×0.75 post-Need=0) у gen дал all-fire `11111111` и не снял silence у preinh: глобальный TipR-down не лечит preinh и портит уже частичный gen.

### Span=50 мс · NeuronModel=baseline

| Mod | PostTune OFF | PostTune ON | SHA / Host / RUN_ID |
|---|---|---|---|
| preinh | — | **PASS** fires=`10000000` | PASS×3 d2v4 `.17` |
| nextseg | — | Incomplete BR-D6 PeakSeen all0 L stuck1 | `tl-m1-n1-d6-br50ns-…` `.11` Need=1 |
| gen | — | исторически Need=0+silence; в cold фикса — отдельно | HIST |

### Span=100 мс · NeuronModel=baseline

| Mod | PostTune OFF | PostTune ON | SHA / Host / RUN_ID |
|---|---|---|---|
| preinh | — | **PASS** fires=`10000000` | PASS×3 d2v4 |
| nextseg | — | Incomplete BR-D6 peak-blind | M1-ext |
| gen | — | канона `br100_gen` в W10 нет (дыра матрицы) | — |

### NeuronModel=FastSpan (Branch)

Конфигов Branch×FastSpan **ещё нет** — дыра плана PostTune-цикла (`SelectivityBranchFastSpan/`, волна W48).

---

## Trainer=Branch · Mode=N0 (равн. BR-M0 track)

### Span=480 мс · NeuronModel=baseline W04

| Mod | Итог | Host / RUN_ID |
|---|---|---|
| PSIoff W04 | Need=1, peak0=0, D7_bad=0 → класс BR-D6 pulse0; BR-D7 закрыт | `.11` `tl-m0-d7-20261018-20-27` |

---

## Trainer=Classic · Mode=N0

### Span=25 мс · NeuronModel=baseline W01

| Mod | PostTune / Test | Итог | Host / RUN_ID |
|---|---|---|---|
| PSIoff | N+1 cold | Need=1, incomplete (`CL-stall-short`) | `.17` `tl-cl-n1-w01-20261019-10-04` |

### Span=50 мс · NeuronModel=baseline W01

| Mod | PostTune / Test | Итог | Host / RUN_ID |
|---|---|---|---|
| PSIoff | N+1 cold | Need=0, fires=`00000000`, `cpp_nonseparable` (`CL-Need0-silent`) | `.17` `tl-cl-n1-w01-…` |

### NeuronModel=AsymRm / FastSpan

AsymRm и FastSpan Classic — в HIST матрице; в cold N+1 не входили. Мини-сетка для PostTune-фикса — см. план §4 B/C.

---

## Trainer=Classic · Mode=N1

Исторически broken path (`CL-N1-stall`); в мини-набор N+1 **не** входил. Для контроля фикса — ≥1 short N1 в §4D (допустимо broken как исход).

---

## Дефекты и инфраструктура (кратко)

| Дефект | Итог |
|---|---|
| BR-D7 / BR-D2 / P4 sync | ✅ закрыты |
| BR-D3 / BR-D6 | открыты (PostTune mid / peak-blind) |
| A2.4 thr=1 | следующий разбор runtime vs репортёр |
| PASS×3 | **не** arm’ился в N+1 closeout — ждать Branch PostTune-фикс / явный arm |

Артефакты: [SYNTHESIS…](POST_P0_SYNTHESIS_AND_NEXT_CYCLE_2026-10-19.ru.md), [ALGORITHM…](ALGORITHM_UNDERSTANDING_AND_NEXT_PLAN_2026-10-18.ru.md), [M0-C](evidence/M0C_W04_CURRENT_REPEAT_2026-10-17.ru.md), [M1 Branch](evidence/M1_BOUNDARY_MAP_2026-10-17.ru.md), [Classic](evidence/CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md), [иерархия](evidence/RESULT_GROUPING_HIERARCHY.ru.md).

## Сводка dual-track (2026-10-17/18) — историческая

**M1 (Mode=1):** seed `W10_HIST_br25_nextseg` на `.17` — Need=0, 8/8, FP=0. Сосед `br25_preinh` тоже PASS. Границы: NextSeg@50/100 Incomplete; `br50_gen`/W34 N1 — Need=0+silence; W32 MARGIN_HALF Incomplete (исторический PASS не удержан); W03 — all-fire (PSI off) / silence (PSI 25); N0 boundary Incomplete.

**M0 (Mode=0):** повтор `W04_BR480_N0_PSIoff` Step=86 МОм на `.11` — Need=1, lengths `[1,75,89,1]`, failure_reason=0, Test не оценивался; совпадает с matched Step86M. Amp-ref на входе 1 есть, пик на активном этапе слаб/невалиден, best_effort=0, MaxLen не достигнут → класс *ограничение алгоритма/протокола под тестовыми условиями*.

Историческая сводка матрицы 312 и ранние W10-контроли ниже сохранены для контекста.

Полная матрица из 312 опытов выполнена на предыдущем снимке исходников; она дала 32 обучения с `Need=0`, 9 завершений после PostTrain, 16 отказов тренера и 255 случаев незавершения к остановке. Качество отдельно: 4 PASS, 25 FAIL, 12 ошибок оценщика; 271 случай не оценивался. Эти числа не следует переносить на текущую ветку.

На `.17` завершён ограниченный повтор двух Branch W10 контролей на Release Console: `br25_nextseg` сошёлся и прошёл C++ Test калибровку (цель обнаружена, 8/8, FP=0); `br50_gen` тоже сошёлся, но C++ Test сообщил `NonSeparable` и цель не обнаружил (7/8 совпадений, FP=0). Дополнительные оценки по порогу из Train дают all-fire в обоих случаях и не должны подменять Test результат. Подробности, входные SHA, время и визуальные графики: [ре-аудит 17 октября](RE_AUDIT_CURRENT_STATE_2026-10-17.ru.md) и [Word-отчёт W10](reports/W10_CURRENT_BRANCH_CONTROLS_2026-10-17.docx).

При аудите визуальных файлов добавлен W03-сет из четырёх параметрических Branch-прогонов 25/50 мс и PSI off/25 на предыдущем снимке исходников. Все четыре достигли `Need=0`, но качество не прошло: PSI off дал all-fire (1/8, FP=7), PSI 25 — silence без целевого импульса (7/8, FP=0). Console в каждом случае получила `SIGTERM` после 90-секундного ожидания выхода; это отдельная проблема runner/post-flag и не отменяет факт `Need=0`. Исходные прогоны не записывали соматический потенциал; отчет показывает события и явно отмечает отсутствие осциллограммы. Этот W03-сет не является повтором на актуальной ветке: [визуальный W03-отчёт](reports/W03_BRANCH_PARAMETRIC_SHORT_2026-10-17_PREVIOUS_SOURCE.docx).

Найден W04 Branch/480/N0 повтор с `Need=1` на лимите 900; качество не оценивалось. Активных Console на серверах после этих попыток не обнаружено. Основные root checkout `.11` и `.17` синхронизированы с опубликованной `codex/historical_view`; gitlinks Bin `f1318005` и PulseLib `da307d3` одинаковы. На `.17` намеренно сохранена ссылка из Bin к существующему run bundle на Data-диске. Старые зарегистрированные worktree удалены после сохранения патчей и конфигов. **Все изменения, помещённые в архивы, остаются кандидатами на дополнительное исследование, а не отвергнутыми вариантами.** Подробные SHA, архивы и оставшиеся задачи: [ре-аудит 17 октября](RE_AUDIT_CURRENT_STATE_2026-10-17.ru.md).

Подтверждённая правка Bin для сокращения глубины путей матричных input overlays и чтения старого формата отчётом закоммичена как `f1318005` и отправлена в origin. Проверено: 51 Python-тест и ручной тест обнаружения конфигов обоих форматов.

Для полного снимка результатов и незакоммиченных изменений см. [ре-аудит текущего состояния](RE_AUDIT_CURRENT_STATE_2026-10-17.ru.md). Записи ниже сохраняют исторический контекст и промежуточные статусы, они не заменяют эту сводку.

## Предыдущий активный этап расследования (историческая запись)

На момент записи основной аудит исторических результатов и подтверждённых дефектов считался завершённым, а выборочные проверки исправленной Release-сборки продолжались отдельно для сходимости C++-обучения и качества классификации. Это историческое описание; текущая точка остановки и нерешённые вопросы приведены выше и в плане дальнейших исследований.

**Обновление 22:58 MSK:** контрольный Classic W01/50/N0 с step-down исправлением завершён. C++-обучение сошлось до сохранённого `Need=0` после перехода на принятый нижний count `N=98`; Test-gate завершился штатно, но результат классификации — `NonSeparable`, цель не обнаружена, Acc `7/8`, FP `0/7`. Исходники и бинарник оставались неизменны; входные копии Train/Test совпадают с парной попыткой, а изменение рабочей копии Train-конфига отражает запись результата обучения. Подробности и SHA артефактов: [результат запуска](../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/diagnostics/w01_classic_structural_2026-10-16/README.ru.md). Это выборочная проверка исправления, а не завершение всего аудита сходимости.

При повторной сверке `.17` найден и занесён в журнал более ранний Branch W04/480/N0 запуск на предке текущего снимка: он дошёл до лимита 900 с `Need=1`, без C++-отказа и без Test; валидным остался только четвёртый пик, длины `[1,75,89,1]`. В конце активен индекс 1. Branch выбирает импульсы в обратном порядке `3→2→1→0`, поэтому индекс 0 при этой остановке ещё не дошёл до своего этапа; его длина 1 сама по себе не доказывает ошибку выбора роста. Краткая сводка: [результат Branch W04](../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/diagnostics/branch_w04_480_n0_single_synapse_ref_2026-10-16/result_summary.json).

На момент проверки в 22:55 MSK на `.11` и `.17` активных `NeuroModelerConsole` не было. На `.11` оставалась idle tmux-сессия сборки; на `.17` — idle shell в отдельном worktree и сохранённые данные на Data-диске. Результаты и логи не удалялись.

- Ветка расследования: `codex/historical_view`; обновления по результату step-down и найденному Branch-запуску отправлены в `origin/codex/historical_view`; актуальные gitlink-коммиты PulseLib `7c8f6f2`, Bin `193a4e98`. Экспериментальный исходный снимок: root `16d87dd`, PulseLib `56a5962`, Bin `cfc5bcf`, Rdk `b3b2472`.
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
