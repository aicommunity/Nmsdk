# G1 S1 — статус `launch.exit` после RERUN (2026-10-22)

**Срез (UTC):** 2026-10-22T03:05Z (после закрытия W02 RERUN rep3 на Elder-1 `.11`). **Кампания:** arm **S1**, отбор [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv) — **13 волн** / 32 case, 3 rep на волну; хосты — [`G1_LAUNCH_S1_2026-10-21.ru.md`](G1_LAUNCH_S1_2026-10-21.ru.md).

## Постановка

После первого прохода G1 S1 exit-audit rep3 зафиксировал только **3** волны с **`launch.exit=0`** (W01, W13, W33 на `.11`), тогда как drv на всех волнах напечатал **`SERIES_DONE` + `EXIT=0`** — расхождение описано в [`G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md) и [`G1_FAILURE_ANALYSIS_2026-10-21.ru.md`](/home/user/TLAgent-20261020/agent-reports/G1/G1_FAILURE_ANALYSIS_2026-10-21.ru.md) (`DEBT-G1-exit-gate`). Серия **`G1_S1_RERUN`** (`reason=launch_exit_nonzero_rerun`) была запущена 2026-10-21T16:39Z по [`G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md) для волн первого прохода с **`launch.exit` ∈ {1,2}**; волны W01/W13/W33 **не** перезапускались.

**RERUN dual-host завершён** 2026-10-22T03:05Z: последняя волна **W02 rep3** записала `launch.exit=1` для `G1.S1.W02-11-20261021T232414Z-32270`; lane offload `g1-s1-w02-rerun-done-20261022T030528Z`. На срезе **оба хоста idle** (real Console **0**, drv tmux **нет**).

Критерий приёмки для **полного** rollup кампании и для ворот **`SYNTHESIS_FINAL` по всей матрице** — **`launch.exit=0`** у **последнего принятого** `run_id` на **каждую** волну. Этот критерий **не выполнен**: RERUN **не** добавил ни одной exit-clean волны. Политика partial-report — [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md).

## Сводка по волнам (последний принятый rep3)

Правило строки: если волна входила в RERUN — берём **последний RERUN rep3**; иначе first-pass rep3. Источник кода — `$TIMELEARNER_MATRIX_RUNS_ROOT/{run_id}.launch.exit`.

| Wave | Host | last accepted run_id (rep3) | `launch.exit` | series |
|------|------|-----------------------------|---------------|--------|
| W01 | `.11` | `G1.S1.W01-11-20261021T113257Z-15892` | **0** | first-pass |
| W02 | `.11` | `G1.S1.W02-11-20261021T232414Z-32270` | **1** | RERUN |
| W04 | `.17` | `G1.S1.W04-17-20261021T165036Z-29434` | **2** | RERUN |
| W08 | `.17` | `G1.S1.W08-17-20261021T165207Z-6754` | **1** | RERUN |
| W09 | `.17` | `G1.S1.W09-17-20261021T200402Z-28218` | **1** | RERUN |
| W10 | `.17` | `G1.S1.W10-17-20261021T174515Z-6406` | **1** | RERUN |
| W11 | `.17` | `G1.S1.W11-17-20261021T192654Z-26754` | **1** | RERUN |
| W12 | `.17` | `G1.S1.W12-17-20261021T172324Z-31782` | **1** | RERUN |
| W13 | `.11` | `G1.S1.W13-11-20261021T073758Z-3533` | **0** | first-pass |
| W31 | `.11` | `G1.S1.W31-11-20261021T184544Z-29973` | **1** | RERUN |
| W33 | `.11` | `G1.S1.W33-11-20261021T120726Z-15166` | **0** | first-pass |
| W37 | `.11` | `G1.S1.W37-11-20261021T174842Z-18318` | **1** | RERUN |
| W48 | `.17` | `G1.S1.W48-17-20261021T172046Z-30713` | **1** | RERUN |

**Итог:** **3/13** волн **exit-clean** (W01, W13, W33 — только first-pass). **10/13** имеют последний `launch.exit` ∈ {1,2} после RERUN (W02/W08/W09/W10/W11/W12/W31/W37/W48 → **1**; W04 → **2**). Ранее в части тиков писали «3/12» — это **ошибка счёта**: в [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv) ровно **13** уникальных `wave`. Полная exit policy «все волны `launch.exit=0`» **не достигнута**; повторный cold RERUN по тем же волнам **не** планируется без смены SHA/алгоритма.

## Группировка по Trainer×Mode → Span (контекст для rollup)

Иерархия канона — [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md). Ниже — не Acc/Цель (метрики по non-exit волнам идут как `failure_class`), а привязка волн к осям из [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv).

**Classic×N0.** Exit-clean: **W01** (Span 50, AsymRm) и **W33** (Span 50, POST). **W02** (Span 100/480) после RERUN закрыта с **exit=1** (rep1–3 RERUN все ≠0). **W31** (Span 480, margin-current) — RERUN **exit=1**.

**Classic×N1.** **W13** (HIST ltz50 gen) — exit-clean на первом проходе. **W37** (packB/packC) — RERUN **exit=1**. На `.17` **W09** / **W12** — RERUN **exit=1**.

**Branch×N0 / Branch×N1.** **W04** (Span 480) — RERUN **exit=2**. **W08**, **W10**, **W11**, **W48** — RERUN **exit=1**.

## Ворота SYNTHESIS

Документ **`SYNTHESIS_FINAL` по полной 13-волновой матрице** остаётся **запрещён**. Разрешён путь **PARTIAL**: метрики и выводы только по exit-clean подмножеству (W01/W13/W33) плюс строки `failure_class=launch_exit_N` для остальных — см. [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md), [`G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md`](G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md).

## Связанные артефакты

| Документ | Роль |
|----------|------|
| [`G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md) | Baseline rep3 первого прохода |
| [`G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md) | Состав RERUN |
| [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md) | Решение после RERUN |
| [`G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md`](G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md) | Исторический блокер (RERUN теперь закрыт) |
| [`TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md) | DEBT-G1-exit-gate |

---
Зеркало (при sync): `/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`.
