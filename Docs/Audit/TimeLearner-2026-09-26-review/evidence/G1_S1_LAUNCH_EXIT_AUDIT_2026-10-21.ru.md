# G1 S1 — аудит `launch.exit` (rep3, финальная rerun-серия)

**Срез (UTC):** 2026-10-21T16:36Z (tick 124). **Источник:** `$TIMELEARNER_MATRIX_RUNS_ROOT/{run_id}.launch.exit` (не каталог `runs/{run_id}/launch.exit`). Drv: `SERIES_DONE` + `EXIT=0` на всех 12 волнах — **не эквивалентно** успешному matrix exit.

## Таблица wave → rep3 `launch.exit`

| Host | Wave | run_id (rep3) | launch.exit | drv post-rep3 |
|------|------|---------------|-------------|---------------|
| `.11` | W01 | `G1.S1.W01-11-20261021T113257Z-15892` | **0** | SERIES_DONE / EXIT=0 |
| `.11` | W02 | `G1.S1.W02-11-20261021T124609Z-28711` | **1** | SERIES_DONE / EXIT=0 |
| `.11` | W13 | `G1.S1.W13-11-20261021T073758Z-3533` | **0** | SERIES_DONE / EXIT=0 |
| `.11` | W31 | `G1.S1.W31-11-20261021T082847Z-7074` | **1** | SERIES_DONE / EXIT=0 |
| `.11` | W33 | `G1.S1.W33-11-20261021T120726Z-15166` | **0** | SERIES_DONE / EXIT=0 |
| `.11` | W37 | `G1.S1.W37-11-20261021T080827Z-9751` | **1** | SERIES_DONE / EXIT=0 |
| `.17` | W04 | `G1.S1.W04-17-20261021T130651Z-903` | **1** | SERIES_DONE / EXIT=0 |
| `.17` | W08 | `G1.S1.W08-17-20261021T132542Z-11858` | **1** | SERIES_DONE / EXIT=0 |
| `.17` | W09 | `G1.S1.W09-17-20261021T123435Z-16055` | **2** | SERIES_DONE / EXIT=0 |
| `.17` | W10 | `G1.S1.W10-17-20261021T073606Z-8279` | **1** | SERIES_DONE / EXIT=0 |
| `.17` | W11 | `G1.S1.W11-17-20261021T093736Z-2093` | **2** | SERIES_DONE / EXIT=0 |
| `.17` | W12 | `G1.S1.W12-17-20261021T070005Z-2620` | **1** | SERIES_DONE / EXIT=0 |
| `.17` | W48 | `G1.S1.W48-17-20261021T092155Z-30428` | **2** | SERIES_DONE / EXIT=0 |

**Итого:** **3/12** волн с `launch.exit=0` (W01, W13, W33 на `.11`). Остальные rep3 завершились с кодом **1** или **2** при «зелёном» drv.

## W08 (критично)

- Файл: `/media/user/Data/TLAgent-20261020/runs/G1.S1.W08-17-20261021T132542Z-11858.launch.exit` → **1**.
- `queue_status.json`: `status=paused_after_training_or_evaluation_issue`, wave W08 `runner_exit=1`, `training_stop_cases=1`, `completed_checkpoint_required`.
- `launch.log`: `PAUSED after W08: training non-convergence/refusal or evaluation error`.
- Активного `timelearner_matrix` / wait_run на срезе **нет**; queue **не** «жива», прогон **завершён с ошибкой**.
- **Риск ложного SERIES_DONE:** **подтверждён** — `run_series.sh` дождался файла `launch.exit`, drv записал `EXIT=0` без gate по значению exit (см. [`G1_FAILURE_ANALYSIS_2026-10-21.ru.md`](/home/user/TLAgent-20261020/agent-reports/G1/G1_FAILURE_ANALYSIS_2026-10-21.ru.md)).

## Вывод для rollup / метрик

- **Исполнение серий drv:** 12/12 `SERIES_DONE`.
- **Matrix exit audit (rep3):** **не пройден** для 9/12 волн; кампания **не** готова к финальному G1 vs C2 без rerun/разбора или выборочного extract только по `launch.exit=0` (3 волны / подмножество case).

---
Зеркало: `/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`.
