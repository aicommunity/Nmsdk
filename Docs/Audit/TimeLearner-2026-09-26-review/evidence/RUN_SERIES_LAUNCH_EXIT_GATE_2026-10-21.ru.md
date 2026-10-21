# run_series / wait_run — gate по `launch.exit`

**UTC:** 2026-10-21. **Контекст:** [G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md) — drv печатал `SERIES_DONE` и выходил с `EXIT=0`, хотя rep3 имел `launch.exit` 1 или 2 на 9/12 волн (ожидание только по появлению файла, без проверки значения).

**Исправление:** `wait_run.sh` после появления `$RUN_ID.launch.exit` завершает summarize как раньше, но при `queue_exit≠0` пишет `STOP: queue_exit=… (expected 0)` и выходит с тем же кодом. `run_series.sh` не печатает `SERIES_DONE`, пока для каждого rep нет файла и `launch.exit=0` (сообщения `STOP:` сохранены в том же стиле).

**TECH_DEBT (закрыт):** ложный «зелёный» drv при matrix failure — см. audit W08 и rollup partial.
