# G1 S1 — статус `launch.exit` после RERUN (2026-10-22)

**Срез (UTC):** 2026-10-21T23:30Z (локальная read-only проверка на Elder-1 `.11`; без нового Console cold, без остановки W02). **Кампания:** arm **S1**, 32 case, 3 rep на волну; отбор и хосты — [`G1_LAUNCH_S1_2026-10-21.ru.md`](G1_LAUNCH_S1_2026-10-21.ru.md), [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv).

## Постановка

После первого прохода G1 S1 exit-audit rep3 зафиксировал только **3/12** волн с **`launch.exit=0`** (W01, W13, W33 на `.11`), тогда как drv на всех двенадцати волнах напечатал **`SERIES_DONE` + `EXIT=0`** — расхождение описано в [`G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md) и [`G1_FAILURE_ANALYSIS_2026-10-21.ru.md`](/home/user/TLAgent-20261020/agent-reports/G1/G1_FAILURE_ANALYSIS_2026-10-21.ru.md) (`DEBT-G1-exit-gate`). Серия **`G1_S1_RERUN`** (`reason=launch_exit_nonzero_rerun`) была запущена 2026-10-21T16:39Z по [`G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md) для девяти волн первого прохода с **`launch.exit` ∈ {1,2}**; волны W01/W13/W33 **не** перезапускались. На срезе 2026-10-22 RERUN на `.17` и на `.11` (кроме W02) **закрыт drv как `SERIES_DONE`**, но **matrix exit audit по последнему run_id rerun по-прежнему не даёт 12/12 с `launch.exit=0`**; единственная незавершённая волна кампании — **W02 rep3 RERUN** на `.11`.

Критерий приёмки для rollup метрик и для ворот **`SYNTHESIS_FINAL`** — **`launch.exit=0`** у **последнего принятого** `run_id` на волну в `$TIMELEARNER_MATRIX_RUNS_ROOT/{run_id}.launch.exit`, а не drv-only `SERIES_DONE` ([`G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md`](G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md), [`SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md`](SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md), [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md)).

## Сводка по волнам (после RERUN или без rerun)

| Host | Wave | Серия | Последний известный run_id (rep3) | `launch.exit` (matrix) | drv post-RERUN | Комментарий |
|------|------|-------|-----------------------------------|------------------------|----------------|-------------|
| `.11` | W01 | первый проход (без RERUN) | `G1.S1.W01-11-20261021T113257Z-15892` | **0** | SERIES_DONE | «Good wave» — [`G1_S1_GOOD_WAVES_EXTRACT_2026-10-21.tsv`](/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_GOOD_WAVES_EXTRACT_2026-10-21.tsv) |
| `.11` | W02 | **RERUN rep3 в процессе** | `G1.S1.W02-11-20261021T232414Z-32270` | *(файл ещё не записан)* | rep1–2 RERUN завершены; rep3 стартовал 2026-10-21T23:25:44Z | rep1 `…164003Z-6102` **exit=1**; rep2 `…200208Z-3205` **exit=1**; активен `run_timelearner_matrix_queue.py` (read-only pgrep на срезе) |
| `.11` | W13 | первый проход | `G1.S1.W13-11-20261021T073758Z-3533` | **0** | SERIES_DONE | good wave |
| `.11` | W31 | RERUN завершён | `G1.S1.W31-11-20261021T184544Z-29973` | **1** | SERIES_DONE / EXIT=0 | все три rep RERUN с **exit=1** |
| `.11` | W33 | первый проход | `G1.S1.W33-11-20261021T120726Z-15166` | **0** | SERIES_DONE | good wave |
| `.11` | W37 | RERUN завершён | `G1.S1.W37-11-20261021T174842Z-18318` | **1** | SERIES_DONE / EXIT=0 | rep3 RERUN **exit=1** (6 case packB/packC) |
| `.17` | W04 | RERUN завершён | *(run_id на M40 — см. `$REPORTS` / runs root `.17`)* | **1** | SERIES_DONE | rep3 первого прохода уже был exit=1 ([audit](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md)); post-RERUN exit≠0 по отчёту кампании |
| `.17` | W08 | RERUN завершён | *(`.17` runs не зеркалированы на срезе docs-хоста)* | **1** | SERIES_DONE | training/eval pause на rep3 первого прохода — § W08 в exit-audit |
| `.17` | W09 | RERUN завершён | *(`.17`)* | **2** | SERIES_DONE | rep3 первого прохода exit=2 |
| `.17` | W10 | RERUN завершён | *(`.17`)* | **1** | SERIES_DONE | |
| `.17` | W11 | RERUN завершён | *(`.17`)* | **2** | SERIES_DONE | |
| `.17` | W12 | RERUN завершён | *(`.17`)* | **1** | SERIES_DONE | |
| `.17` | W48 | RERUN завершён | *(`.17`)* | **1** или **2** | SERIES_DONE | rep3 первого прохода exit=2 |

**Итог на срезе:** **3/12** волн кампании (первый проход) остаются **exit-clean** без RERUN — W01, W13, W33. **Девять** волн из rerun-набора уже получили drv **`SERIES_DONE`**, но **последний `launch.exit` ≠ 0**: W04, W08, W09, W10, W11, W12, W31, W37, W48 (W31/W37 — файлы на `.11`; `.17` — по закрытию RERUN на M40, коды 1/2 как у rep3 первого прохода в [`G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md)). **W02** — **единственная** волна RERUN, которая на срезе **ещё не завершила rep3** (`G1.S1.W02-11-20261021T232414Z-32270`, `launch.exit` отсутствует). Полная exit policy **12/12 `launch.exit=0`** не выполнена; **`SYNTHESIS_FINAL`** и финальный G1 vs C2 **ждут** (см. [`G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md`](G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md)).

## Группировка по Trainer×Mode → Span (контекст для rollup)

Иерархия канона — [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md). Ниже — не метрики Acc/Цель (они заблокированы до exit-clean extract — [`G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md`](G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md)), а **привязка волн к осям** и Train/Test inputs из [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv) / [`G1_selected_rerun_launch_exit.tsv`](/home/user/TLAgent-20261020/agent-reports/G1/G1_selected_rerun_launch_exit.tsv).

**Classic×N0 (Span 50 / 100 / 480).** Волна **W01** (Span 50, `W01_CL50_N0_PSIoff`, AsymRm) и **W33** (Span 50, POST) остаются единственными exit-clean Classic×N0 на срезе вместе с good-wave extract. **W02** (Span 100 и 480, AsymRm / baseline NeuronModel) — та же ось Classic×N0, но все завершённые rep RERUN дали **exit=1** (`not_converged_at_stop` на rep1–2 — см. summaries `G1.S1.W02-11-20261021T200208Z-3205` в `$REPORTS/G1/`); rep3 RERUN ещё не записал `launch.exit`. **W31** (Classic×N0, Span 480, margin-current mod) после RERUN закрыта drv, но rep3 **`launch.exit=1`**.

**Classic×N1.** **W37** (packB/packC, Span 25/100) — шесть case Classic×N1/N0 смешения в одной волне; post-RERUN rep3 **exit=1**. На `.17` **W09** (5× HIST Classic×N1 и Branch×N1) и **W12** (phase6 twin) завершили RERUN с **exit≠0**.

**Branch×N0 / Branch×N1.** **W04**, **W08** (Span 480), **W10** (Span 25/50, HIST branch mods), **W11**, **W48** (FastSpan family по NeuronModel AsymRm, mods gen/nextseg) — все в rerun-наборе `.17`; после RERUN drv **`SERIES_DONE`**, matrix exit audit **не** пройден (коды 1 или 2). **W13** (Classic×N1 HIST ltz50 **gen**) — exit-clean на первом проходе, RERUN не требовался.

## Ворота SYNTHESIS и частичный rollup

Документ **`SYNTHESIS_FINAL`** и обновление [`G1_S1_PARTIAL_ROLLUP_2026-10-21.ru.md`](G1_S1_PARTIAL_ROLLUP_2026-10-21.ru.md) до статуса FINAL **остаются заблокированы**, пока не выполнена **полная exit policy**: 12/12 волн с **`launch.exit=0`** на последнем run_id (или явное согласование partial-report только по good-wave подмножеству — сейчас **3 волны / 4 case** Classic good extract, не полная матрица 32 case). Частичный TSV [`G1_matrix_2026-10-21.tsv`](G1_matrix_2026-10-21.tsv) отражает **rep3 первого прохода** и **не** заменяет post-RERUN exit-audit.

После появления `launch.exit` у **W02 rep3** следующий **read-only** шаг: пересчитать таблицу run_id→exit для всех 12 волн, обновить этот note, затем — по [`G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md`](G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md) — extract только для exit=0 волн или failure_class для остальных; rollup Trainer×Mode → Span → NeuronModel → Mod с ссылками Train/Test.

## Связанные артефакты

| Документ | Роль |
|----------|------|
| [`G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md) | Baseline rep3 первого прохода (3/12 exit=0) |
| [`G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md) | Состав RERUN `.11` / `.17` |
| [`G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md`](G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md) | Что блокирует G1 vs C2 и PASS×3 |
| [`G1_S1_PARTIAL_ROLLUP_2026-10-21.ru.md`](G1_S1_PARTIAL_ROLLUP_2026-10-21.ru.md) | PARTIAL drv rollup (до post-RERUN exit) |
| [`TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md) | DEBT-G1-exit-gate |

---
Зеркало (при sync): `/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`.
