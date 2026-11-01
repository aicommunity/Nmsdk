# G1 S1 — что заблокировано до завершения RERUN

**Срез (UTC):** 2026-10-21T17:20Z (read-only, без новых Console и без остановки `G1_S1_RERUN`).

После exit-audit rep3 кампания **не** считается matrix-complete: из двенадцати волн только **W01, W13 и W33** на `.11` имеют **`launch.exit=0`** на третьем повторе ([`G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md)). Серия **`G1_S1_RERUN`** (`reason=launch_exit_nonzero_rerun`) уже крутится на `.11` (W02, W31, W37) и на `.17` (W04, W08, W09, W10, W11, W12, W48); на срезе часть rerun-launch ещё **без `matrix_result.json`** (инфраструктурный exit 1/2 до обучения) или **в процессе** (например W48: последний `…171841Z-23995` с `launch.exit=1`).

## Что уже можно использовать в docs

- **Полный extract «хороших» волн:** [`G1_S1_GOOD_WAVES_EXTRACT_2026-10-21.tsv`](G1_S1_GOOD_WAVES_EXTRACT_2026-10-21.tsv) — три повтора × три волны (9 строк), Acc/Цель/Need/fires и пары Train/Test.
- **Частичная матрица rep3:** [`G1_matrix_2026-10-21.tsv`](G1_matrix_2026-10-21.tsv) — все 32 case; для `launch.exit≠0` метрики помечены `failure_class=launch_exit_*` или `no_matrix_result` (W09/W11/W48 rep3 без JSON на `.17`).
- **Сравнение с C2 (модель):** [`G1_vs_C2_2026-10-21.tsv`](G1_vs_C2_2026-10-21.tsv) — колонки `m_oracle`/`feasible` из [`G1_predictions_2026-10-21.tsv`](G1_predictions_2026-10-21.tsv); факт G1 — по rep3 там, где есть JSON.

## Что остаётся заблокировано

1. **Финальный G1 vs C2 по кампании** — нужны **12/12** волн с **`launch.exit=0`** на последнем принятом run_id (rep3 rerun или согласованный rep), иначе доли `converged_*` / pass по ячейкам Trainer×Mode → Span будут смещены.
2. **W09, W11, W48 (rep3)** — каталоги run на `.17` **без** `matrix_result.json`; до успешного rerun нельзя заполнить Acc/Цель по case (в TSV стоят прочерки и `metrics_blocked_no_result_json`).
3. **W37 rerun на `.11`** — последние launch (`…170720Z-16807`) **NO_RESULTS** локально; опираться на rep3 `…080827Z-9751` (exit 1, все six case `not_converged_at_stop`) до появления exit=0 rerun.
4. **PASS×3 / медианы по case** — три повтора осмысленно сводить только для волн с тремя успешными matrix exit; сейчас это **только** W01/W13/W33 (все три rep с exit=0 дают одинаковый silent Test 7/8).
5. **Обновление [`G1_S1_PARTIAL_ROLLUP_2026-10-21.ru.md`](G1_S1_PARTIAL_ROLLUP_2026-10-21.ru.md)** в статус FINAL — после закрытия RERUN и повторного exit-audit.

## Следующий read-only шаг после RERUN

Пересчитать `launch.exit` по **последнему** run_id на волну (не drv `SERIES_DONE`), прогнать `summarize_run.py` по `$TIMELEARNER_MATRIX_RUNS_ROOT/{run_id}`, обновить `G1_matrix_*` и `G1_vs_C2_*`, затем rollup по иерархии из [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md).

---
Зеркало: `/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md` (при sync).
