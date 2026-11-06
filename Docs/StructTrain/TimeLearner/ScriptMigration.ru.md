Принято06.11:215 records (213 retired/2 moved),complete=false. Десять оставшихся AsymRm shell-драйверов удалены после проверок обоих workers; конфиги, модели, измерения и исходные report bodies сохранены. [Область и Git-источники](AsymRmDriverRetirement.ru.md). Ограниченный path/suffix inventory Bin теперь131; полнота всей миграции не заявляется. Ниже — хронология прежних снимков.

Принято04.11:166 records (164 retired/2 moved),complete=false. Удалены8 исторических PhaseA tools после двух actual CLI/negative/scope gates; августовские модели/конфиги/CSV/тело REPORT сохранены. [Приёмка](PhaseAToolRetirement.ru.md). Ниже — хронология прежних снимков.

Принято04.11:158 records (156 retired/2 moved), complete=false. Оба workers проверили retirement8/negative/exact16/CMake prefix и расширенный inventory15. [Согласованная приёмка](InventoryAndAuditRetirementAcceptance.ru.md). Ниже — хронология прежних pending состояний; актуальные команды поиска находятся в корневом пакете.

Candidate158: M40 подтвердил158 retrieval records, negative refusal/exact16 scope/CMake prefix. Elder gate ждёт inventory A2; source удаления8 audit tools не объединён. Accepted manifest пока150. [Readback](AuditProbeRetirementM40Readback.ru.md).

Дополнение04.11: расширенный candidate inventory обнаружил197 review candidates (189 Bin/8 root), включая пропущенный.mjs. M40 15/15, Elder pending; селектор не объединён. Manifest150 остаётся неизменным. [Readback и точные ограничения](RelatedScriptInventoryReadback.ru.md).

Текущее принятое состояние:150 records (148 retired/2 moved), complete=false. Последние9 path-selected root tools удалены после двух workers/negative/exact13 checks: [приёмка](RemainingRootToolsRetirement.ru.md). Production inventory snapshot287b75d0f2a2f5465295de5da4c82dd98892fa4c подтверждает188 Bin candidates/0 выбранных root/0 Pulse и217 property declarations. Это нижняя граница; неименованные scripts и активная Bin миграция ещё требуют review. Ниже сохранена хронология.

Текущее принятое состояние:141 records (139 retired/2 moved), complete=false. [Cable/E1 two-worker приёмка](CableFamilyRetirement.ru.md). Следующие9 root tools — candidate150, пока только M40 gate: [scope и ожидание Elder](RemainingRootToolsRetirement.ru.md). Ниже сохранена хронология прежних приёмок.

Принят04.11 пакет theory/sim:14 исторических исходников удалены без wrappers; manifest121 records (119 retired,2 moved), complete=false. Production history CLI и restored-path negative control проверены на обоих workers. [Источники и приёмка](TheoryScriptRetirement.ru.md). Общая migration ещё не завершена.

# Миграция скриптов TimeLearner

Актуально03.11:105 records (103 retired/2 moved), complete=false. Проверены оба
workers и restored-launcher negative control для11 SoftCold/OpenGaps/T2/T4 tools;
[точные SHA и границы](SoftColdLauncherRetirement.ru.md). Все старые пути удалены
без wrappers. Ни первичные данные, ни история научных выводов не удалены.
Ниже — хронология ранее принятых пакетов, а не competing current launch guide.


Исторические shell-файлы из Docs уже удалены; следующий пакет удаляет четыре
разовых Python-инструмента SoftCold/W1/W2: [обоснование и источники](DocsPythonRetirement.ru.md).
Это частичная миграция этапа 9; production runner/queue, активные анализаторы,
физические модели и остальные исторические файлы пока не перенесены.

Первый активный leaf analyzer перенесён из Bin: [Branch dynamics](BranchDynamicsMigration.ru.md).
Основной модуль и шесть старых тестов находятся в корневом пакете, оба старых
пути удалены без wrappers. Отдельный `moved_files` реестр сохраняет original
Bin commit/blob, mechanical root commit, replacement и проверенную версию.
20/20 final checks на каждом worker проверяют CLI, whole-module parity, corruption
и отказ для реально изменившегося во время чтения файла;
один неверно выбранный M40 fixture сохранён как неудачная попытка.
Это не перенос всего старого анализа и не новый научный прогон.

В старых местах не оставляются wrappers, копии или архивы исходников.
Исторические результаты и прежние критерии отчётов сохраняются.
[Машинный реестр](script_migration.json) содержит repository, полный commit SHA,
старый путь, Git blob SHA-1, SHA-256 содержимого и команду просмотра.

## Источник исторических файлов

Архивный снимок root: `b62127538694a3442771598420fd78fa7e405c8b`. Это доступный snapshot для извлечения
именно скрипта, а не доказательство того, что соответствующий эксперимент
выполнялся на этом root/PulseLib/Bin. Для научного replay требуется настоящий
исторический root с gitlinks, моделью и протоколом из реестра доказательств.

| Удалённый файл в evidence/metrics | Исторический исходник |
|---|---|
| `build_full49_20261010.sh` | [commit b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/build_full49_20261010.sh) |
| `run_full49_after_rs_20261010T064000Z.sh` | [commit b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/run_full49_after_rs_20261010T064000Z.sh) |
| `monitor_full49_after_rs_20261010T064000Z.sh` | [commit b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/monitor_full49_after_rs_20261010T064000Z.sh) |
| `run_S3_retest_after_softcold_fix.sh` | [commit b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/run_S3_retest_after_softcold_fix.sh) |
| `run_S3cd_tails.sh` | [commit b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/run_S3cd_tails.sh) |
| `run_phase2_queue.sh` | [commit b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/run_phase2_queue.sh) |
| `run_phase5_defer.sh` | [commit b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/run_phase5_defer.sh) |

Просмотр без восстановления файла в текущем дереве:

```text
git show b62127538694a3442771598420fd78fa7e405c8b:Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/build_full49_20261010.sh
```

Экспортировать исторический инструмент для исследования следует в отдельный
каталог; возвращать его на прежнее место в поддерживаемом checkout не требуется.

## Проверка удаления и ограничения

Второй пакет — исторические InhGrid SoftCold/disk-stop launchers/monitors:

| Старый путь относительно evidence | Git source |
|---|---|
| `INH_GRID_LAUNCH.sh` | [b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/INH_GRID_LAUNCH.sh) |
| `INH_GRID_LAUNCH_CASES.sh` | [b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/INH_GRID_LAUNCH_CASES.sh) |
| `inh_grid_logs/monitor_loop.sh` | [b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/inh_grid_logs/monitor_loop.sh) |
| `inh_grid_logs/monitor_diskstop_rerun.sh` | [b6212753](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/inh_grid_logs/monitor_diskstop_rerun.sh) |

Прочитаны все четыре файла и проверены архивные/current Git blobs. Они
используют старые case-prefix pools, TSV и пути кампании, а monitor disk-stop
может запускать старый auto-offload. Буквальный поиск в tracked root/submodule
scripts/docs обнаружил только сами четыре файла и исторический отчёт 24.10.
Его ссылка заменена на immutable Git source; измерения не изменены. Новые
задания эти launchers не используют и историческая серия не возобновляется.
Динамический вызов произвольного имени таким поиском не исключён.

В первом пакете каждый файл прочитан: это фиксированная историческая очередь, сборка или monitor
со старым `/home/user/Nmsdk`, датой/CASES/именами результатов. Поиск буквальных
имён по tracked root/submodule trees обнаружил только три исторических документа
и первоначальный inventory. Их команды помечены историческими; ссылки ведут
в конкретный commit. Общий поиск динамически вычисляемых имён этим не доказан.

До удаления сверены равенство archive/current Git blobs и контрольные суммы
каждого объекта. Скрипты не выполнялись. Численные тесты для удаления исторических
файлов не нужны; активный pipeline не меняется, серверные checkout/runtime не тронуты.

Остаток этапа 9: перенос действующих функций в Scripts/StructTrain/TimeLearner,
новый CLI/конфиг-адаптер и реестр для остальных Git trees. Этот пакет не означает
готовность современного запуска всех старых серий и не возобновляет серию D.

## Третий пакет: вспомогательные shell-инструменты плана20.10

Исходники доступны в root snapshot
`fa53680d62ce9dedbee464fc55418dd3f76a0ca6`, каталог
`Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20/tools`.
Удалены `cpu_gate.sh`, `find_root_for_pulselib.sh`, `launch_queue.sh`,
`make_lane.sh`, `provenance.sh`, `refresh_waves.sh`, `run_series.sh`, `wait_run.sh`.
Каждый файл прочитан целиком; archive/current blob, SHA256 и последний изменявший
commit сохранены в migration manifest. Никакие команды этих инструментов
не выполнялись, очереди и серия D не запускались.

Это прежняя tmux/queue/lanes связка с Bin/Platform, фиксированными лимитами8/12,
историческими путями и best-effort preflight. `make_lane` переносил фактические
submodule HEAD сверх root gitlinks; такой lane не является сам по себе
воспроизводимой root closure. Их наличие не подтверждало нынешний runtime/
provenance контракт. Generic read-only `find_root`/`provenance` также удалены
из исторического каталога; полноценный поддерживаемый history/runtime путь
оценивается отдельно, без обещания CLI-паритета со старым helper.

Поиск буквальных имён в tracked scripts/docs/CMake root, Bin и PulseLib
обнаружил ссылки только в исторических Docs и внутри этой удаляемой группы;
активные Scripts/Tests/App их не вызывают.18 исторических документов получили
явную пометку и immutable ссылки для упомянутых инструментов; их результаты
и старые команды как историческое свидетельство сохранены. Динамически
составленные имена такой поиск не исключает.

Приёмка: восемь старых путей отсутствуют, исходники извлекаются через `git show`
по каждой записи manifest с совпадающими хешами. Изменений native кода/физики
нет; серверные численные тесты для удаления этих исторических файлов не нужны.
Python-инструменты Docs, исторические Reports runner receipts и Bin остаются
открытой частью миграции; текущий пакет не означает завершения этапа9.

## Четвёртый пакет: старые campaign/offload shell entrypoints

Снимок root `8e4448ea2e055e8f4edb4c33fe2ad523a5467de9`, прежний каталог
`Docs/Audit/TimeLearner-2026-09-26-review/evidence/tools`: удалены
`archive_nmsdk_journals.sh`, `disk_watch_offload.sh`, `e05_dispatch.sh`,
`r0_branch_nextseg_replay.sh`, `repass_sweep.sh`, `w0_br25_seed_jitter_launch.sh`,
`w0_br25_test_tipr_jitter.sh`, `w1w2_sim_launch.sh`.

Это старые кампании и прежние offload-инструменты, а не поддерживаемые команды.
Они используют Bin/Platform, фиксированный br25 template, monkeypatch
posttune_verify/CASES, неполный overlay Train→Test, byte inequality как gate
изменения ответа либо rsync. Их алгоритмы не переносились автоматически в
новый пакет. Современные export/calibration/evaluation и runtime manifest
проверяются своим production путём; текущая diagnostic cleanup не объявляется
drop-in заменой старого архивационного скрипта.

Все восемь файлов прочитаны; буквальные ссылки найдены только в исторических
Docs. Четыре документа помечены как исторические, локальная Markdown-ссылка на
удалённый archive helper заменена immutable Git source. Измерения, численные
данные, models/configs и научные выводы не переписывались. Перестановки, jitter
и сходство сохраняют исходную историческую постановку, а не получают новый PASS.

Все27 удалённых путей проверяются через manifest: отсутствие в текущем дереве,
retrieval по полному commit и совпадение содержимого/SHA256. В root Docs больше
нет tracked `.sh` внутри TimeLearner audit; Python и остальные Git trees ещё
требуют отдельного review/migration. Старые server checkout не менялись.

## Пятый пакет: исторические NSR/NSC Python entrypoints

Удалены из текущего дерева `evidence/normsync/gen_nsr.py`, `gen_nsc.py` и
`ns_readback.py`. Repository root, retrieval snapshot
`044c76d1b1cbe35b2747285ef296ac22afe976ce`; точные пути, blob SHA1, SHA256,
размер, последний изменявший commit и команды git show записаны в
[script_migration.json](script_migration.json). Снимок извлечения не является
утверждением о версии, реально использованной в старом эксперименте.

Все8 Python-файлов normsync прочитаны целиком. Два генератора задают фиксированные
группы кампании25.10, старые абсолютные executable/workspace paths и legacy
параметры. gen_nsc импортирует gen_nsr через /home/user/normsync. ns_readback
выполняет обход файлов при import, скрывает ошибки чтения/JSON и распознаёт
PostTune по текстовой эвристике. Он не может служить современным доказательством
валидной effective configuration. Паритет действующего нового readback CLI
с этим одноразовым инструментом не заявляется.

Буквальный поиск трёх имён по root, Bin и PulseLib обнаружил только сами файлы,
импорт gen_nsr внутри gen_nsc и записи первоначального inventory. Действующих
callers не найдено; динамическое построение имён такой поиск не исключает.
Inventory сохраняет исходный snapshot и получает явную disposition
retired_historical со ссылкой на migration manifest. Wrappers/копии на старых
путях не оставлены. Остальные5 normsync-моделей и анализаторов не удаляются:
их назначение и возможный перенос требуют отдельной проверки.

Приёмка этого пакета: совпадение current/archive blobs до удаления, доступность
архивных commits в Git, отсутствие трёх путей в новом tree, проверка retrieval
SHA256/размеров и повторный поиск callers. Старые программы не запускаются,
численные результаты и активный runtime не меняются. Это частичное выполнение
этапа9; остальные Python, Bin, PulseLib и Reports entrypoints остаются открытыми.

Пятый пакет проверен на Elder по root
8e11fd5f9e2c2c2750e3d34f905e1c128202f647: все30 записей retired_files
из manifest (включая27 прежних shell) извлекаются из Git с точными SHA256,
размерами и blob IDs; в новом tree их пути отсутствуют. В Scripts/Tests/App/
Apps/CMake root буквальных callers трёх новых имён нет. Receipt и точный
источник read-only проверки опубликованы commit
f2be2fe6e865ab1bdf4593cc18345cf8812bd1f4, каталог
Reports/StructTrain/TimeLearner/s09-retired-normsync-elder-a1.
После получения через Git локально перепроверены receipt hashes и все30 blobs.
Это статическая Git/migration приёмка; численные/компиляционные тесты
не выполнялись и не требуются для удаления этих одноразовых исторических файлов.

## Шестой пакет: исторические normsync анализаторы и standalone модель

Все пять оставшихся Python и связанный C source прочитаны целиком:
`aggregate.py`, `normsync_audit.py`, `model.py`, `rs_delay_sim.py`,
`window_shift_sim.py`, `segsim.c`. Они удаляются без wrappers/копий из
`Docs/Audit/TimeLearner-2026-09-26-review/evidence/normsync`.
Retrieval snapshot —970fde1a0b13cf4d29b1c19659d423dd9899ebfe; для каждого
файла manifest содержит полный commit, blob, SHA256 и размер. Теперь в
retired_files36 записей; complete=false сохраняется.

Это исторический пакет гипотез25.10, а не активный native анализ. Audit
сопоставляет legacy iteration logs и старые peak_valid/anchor поля без
современной полноты/revision. Aggregate молча пропускает нулевой/отсутствующий
span. Standalone драйвер не проверяет subprocess return code, использует
четыре входа и target-first margin; sweep-скрипты выполняются при import,
привязаны к локальному ./segsim и фиксированным JSON outputs. Window shift
является линейной суперпозицией для гипотезы о загрязнении окна, а не native
learning proof. segsim не входит в production CMake и не проверяет storage.

Поиск буквальных callers в Scripts/Tests/App/Apps/CMake root не обнаружил
действующих ссылок. Import model внутри самого старого пакета удаляется вместе
с ним; одноимённая другая модель theory/sim этим пакетом не затрагивается.
Это ограничение буквального поиска, не доказательство отсутствия любых
динамически составленных имён в сторонних пользовательских сценариях.

Все JSON и исторический NORMALIZATION_SYNC отчёт сохраняются; в отчёт добавлена
ссылка на полный исходный Git-каталог и пределы старого E0 сравнения. Его числа
и прежние научные выводы не переписаны. Современный scorer/контроллер не
объявляются drop-in заменой исторической аппроксимации. Статическая приёмка
проверяет Git retrieval всех36 записей, отсутствие удалённых путей и сохранность
неисполняемых normsync artifacts; серверный receipt ещё требуется. Этап9
в целом остаётся открытым, включая другие Docs/Bin/PulseLib/Reports tools.

Серверная статическая проверка завершена на Elder:36/36 retrieval records,
все5 оставшихся normsync JSON byte-identical исходному snapshot, удалённых
путей в новом Git tree нет; буквальных root production callers не найдено.
Receipt опубликован в58be4e41c2d095318d3260e634769f9b42d101b4,
Reports/StructTrain/TimeLearner/s09-retired-normsync-model-elder-a1.
HEAD серверной рабочей копии не менялся; выполнены только чтение Git-объектов
и публикация receipt через отдельный index. Код фактической проверки приложен
как verification-source.txt. Численные результаты заново не рассчитывались.


## Bin Phase12: удаление исторических shell launchers

В отдельной feature удалены6 shell-файлов старых волн1/2/3/5/6, включая
wave3 resume. Source snapshot Bin — `6304b4a2bc4117c54c185a917850c7f65771c163`;
полные пути, blob SHA-1, content SHA-256, last-change commits и retrieval commands
добавлены в script_migration.json. Wrapper/copy на прежнем месте не оставляется.
Bin feature commit `fd54fda2fbc1e0a96ae377789322d0804571b3a6` меняет только эти
шесть launchers и архивную оговорку/ссылки в _repro/README.md. Модели, конфиги,
таблицы и критерии исторических результатов не переписываются.

Прочитаны все шесть программ. Они фиксируют старый /home/user/Nmsdk workspace,
имена campaign cases и legacy phase12_validate.py. Wave1, помимо запуска,
восстанавливает вручную выбранный TipR, правит прежние badges и коммитит отчёты;
последующие waves смешивают выбранные повторные обучения, clones и gate rebuild.
Это retrieval исторического tooling, не provenance его отдельных экспериментов.
Общий Python validator и специализированные helpers не удалены этим пакетом;
они требуют собственного review/migration. Новая серияD не запускается.

Буквальный поиск по pinned root76afaeb/Bin6304b4a/PulseLib456a5ab дал30 ссылок
в root inventory snapshots,5 в Bin _repro/README и0 в PulseLib. Executable callers
с буквальными именами не обнаружены. Динамические имена/внешние пользовательские
сценарии этим не исключены. README теперь явно является историческим разделом;
ссылки для просмотра shell source указывают на immutable Bin commit.

Для проверки manifest по всем трём Git trees добавлен root CLI:

```text
python3 -m Scripts.StructTrain.TimeLearner history verify-migration ROOT_COMMIT \
  --root ROOT_REPOSITORY --bin-repository BIN_REPOSITORY \
  --pulselib-repository PULSE_REPOSITORY --output NEW_RECEIPT.json
```

Команда не checkout-ит commits, не исполняет и не восстанавливает scripts.
Она сверяет source commit/blob/content/size, отсутствие каждого old_path в
точной root/child closure и существование moved replacement в корневом пакете.
Root revision aliases разрешаются без изменения исходной записи. Неизвестные
repositories/actions, unsafe paths, повреждённый digest, оставшийся old_path
или отсутствующий replacement запрещают положительный receipt. Замена
копий не доказывает runtime parity; tool явно оставляет full migration и
runtime equivalence неподтверждёнными. Существующий history resolve сохранён.

Локальная read-only Git сверка исходного root b2e7af4ad8a941186132af73c4b47a7f3288c62a
проверила все44 records:42 retired и2 moved. Новые numerical tests не проводились;
на момент подготовки серверное повторение ожидалось из-за недоступности
jump host; результат после восстановления приведён ниже. История предыдущих36 records и их адресные server receipts выше
сохраняются. Полный этап9 остаётся открытым.


Дополнительно подготовлен отрицательный Git fixture
`39e91647e34a87afbfc4661ee7c149ad910ffd27`: manifest объявляет42 retirements,
но Bin gitlink намеренно оставлен6304b4a, где шесть Phase12 paths ещё существуют.
Это только metadata fixture, не runtime-конфигурация эксперимента. Текущий
verifiera07a907c0ab8bf630599a97d39a7ad2e3f298f59 возвратил2 с
migration_old_path_still_present и не создал положительный receipt. Исходный
положительный snapshotb2e7af4ad проверялся исправленным verifier; сам b2e7af4ad
содержал ошибочный вызов file-only JSON reader для Git bytes. Исправление
parse_json_bytes сохранено отдельным commit413fd842c. Локальная проверка —
подготовительная, не замена требуемой серверной приёмки.

После восстановления VPN серверная сверка завершена на обоих workers:
44/44 source records, положительная проверка отсутствия старых путей и
отрицательный fixture39e9164 (exit2, положительный receipt не создан).
Receipts93d88621e25f43ea0fe9ecd841b53f38e274bbee (M40) и
30818dfb3a59a01c0eac63b2f9fc0bf6bc086fd2 (Elder) опубликованы в Git.
На Elder первая попытка корректно отклонена из-за Bin worktree alias;
следующая читает точные Bin Git objects из изолированного repository,
не меняя старые checkout. Это не attestation фактического Bin дерева старых
запусков. [Диагностика и защита](SourceWorktreeIdentity.ru.md).
Bin feature fd54fda объединена в develop merge commit
14a88195a8a5538d3a2f5c0657981488e38829b7; root записывает этот gitlink.
Шесть Phase12 shell scripts отсутствуют, wrappers не оставлены. Полный этап9
открыт: прочие активные tools и исторические исполняемые файлы ещё требуют миграции.

Дополнение: четыре исторических Docs Python tools удалены с проверкой на
обоих workers. В production migration manifest теперь46 retired и2 moved
records; все48 проверены по точным Git trees/content hashes и restored-path
negative fixture. [Источники, ограничения и proofs](DocsPythonRetirement.ru.md).
Полный перенос активного анализа и остальных исторических скриптов не завершён.


Плановые инструменты20 октября: ещё16 historical files удалены;64 records,
production Git-приёмка всех64 записей и restored-path negative fixture пройдена на обоих workers. [Причины и точные источники](PlanToolRetirement.ru.md).

Следующий независимый подэтап:17 исторических Bin AsymRm pilot/finish/scale/
sweep launchers удалены, восемь отчётов помечены историческими. Manifest81
records (79 retired +2 moved), server metadata приёмка пройдена на обоих workers;
все archive members проверены, restored-Bin negative fixture отклонён.
[Исходники, review и ограничения](AsymRmLauncherRetirement.ru.md).


Следующий адресный подэтап:13 исторических Reports job.py/runner.sh удаляются
без wrappers. Manifest94 records (92 retired +2 moved); all primary payloads
сохранены. [Исходники, current directory checksums и требуемая приёмка](ReportLauncherRetirement.ru.md).
На момент подготовки серверная проверка этого94-record snapshot ещё не выполнена.

Приёмка94-record snapshot завершена на обоих workers: production CLI и
restored-Reports-launcher negative fixture; оба10-member архива и380 exact Git
source hashes независимо сверены. Подробные SHA — в ReportLauncherRetirement.
Это не завершение полного этапа9.


Следующий пакет удаляет11 исторических SoftCold/OpenGaps/T2/T4 shell entrypoints
без wrappers; [источники, consumers и приёмка](SoftColdLauncherRetirement.ru.md).
Manifest105:103 retired/2 moved; complete=false. Текущие skill/reference копии
переходят на root CLI. Это не удаление первичных данных и не запуск старых волн.

Следующий пакет удаляет два исторических Branch br480 Phase9/Phase10 Python
retry entrypoints, без wrappers; source/caller review и точные retrieval records
описаны в [BranchRetryRetirement](BranchRetryRetirement.ru.md). Manifest107:
105 retired/2 moved; complete=false. Phase8 сохраняется из-за действующих
legacy consumers. Серверная приёмка нового107-record snapshot пока pending.

Приёмка107-record snapshot завершена на обоих workers, включая restored-Python
negative fixture. Все20 members и380 Git source hashes на worker независимо
проверены. [SHA и исправление ошибочного текстового scope17/14 на фактический5/4](BranchRetryRetirement.ru.md).
Полный этап9 остаётся частичным.


Текущий принятый manifest после [удаления двух исторических генераторов сеток](GridGeneratorRetirement.ru.md):186 records (184 retired/2 moved), complete=false. На обоих серверах production retrieval186, exact scope и restored-path negative прошли; generated configs/manifest/results не изменены. Прежние числа выше относятся к своим историческим снимкам. Нижняя граница remaining Bin candidates161; активные analyzers/runner и вся широкая миграция остаются открытыми.
