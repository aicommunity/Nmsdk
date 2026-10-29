# Миграция скриптов TimeLearner

Два пакета удаления: одиннадцать исторических shell-файлов из Docs.
Это частичная миграция этапа 9; production runner/queue, активные анализаторы,
физические модели и остальные исторические файлы пока не перенесены.

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
