# Миграция скриптов TimeLearner

Четыре пакета удаления: двадцать семь исторических shell-файлов из Docs.
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
