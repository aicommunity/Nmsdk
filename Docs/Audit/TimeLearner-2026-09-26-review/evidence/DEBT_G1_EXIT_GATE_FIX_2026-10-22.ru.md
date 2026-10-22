# DEBT-G1-exit-gate — фикс `wait_run` / `run_series` (2026-10-22)

## Постановка

После G1 S1 RERUN drv печатал `SERIES_DONE` и `EXIT=0`, даже когда `$RUN_ID.launch.exit` содержал **1** или **2**. Причина: `wait_run.sh` ждал только **появления** файла `launch.exit` и всегда завершался с кодом 0; `run_series.sh` считал wait успешным и печатал `SERIES_DONE`.

## Изменение

| Файл | Поведение |
|------|-----------|
| [`plans/AGENT_PLAN_2026-10-20/tools/wait_run.sh`](../plans/AGENT_PLAN_2026-10-20/tools/wait_run.sh) | Читает значение `launch.exit`; при ≠0 — `exit` с этим кодом (после summarize). Невалидное содержимое → exit 2. |
| [`plans/AGENT_PLAN_2026-10-20/tools/run_series.sh`](../plans/AGENT_PLAN_2026-10-20/tools/run_series.sh) | Пробрасывает `wait_rc` в `EXIT=$?` драйвера; по умолчанию **останавливает** серию на первом ненулевом `launch.exit`. Опция `CONTINUE_ON_LAUNCH_EXIT=1` — добить remaining reps, но финальный exit всё равно ≠0. |

Копии синхронизированы в `$TOOLS` / `~/tl-agent/Nmsdk/.../tools/` для следующих cold.

## Вывод

Ложный «зелёный» drv для **новых** серий закрыт на уровне harness. Исторические G1 drv-логи не переписываются; PARTIAL rollup по-прежнему опирается на файлы `launch.exit`, не на старые `EXIT=0`. Статус DEBT-G1-exit-gate в TECH_DEBT: **done** (harness), без повторного G1 cold на этом тикете.
