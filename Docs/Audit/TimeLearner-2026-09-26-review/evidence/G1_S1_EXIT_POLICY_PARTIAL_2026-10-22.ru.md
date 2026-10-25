# G1 S1 — политика exit после RERUN (PARTIAL)

**Дата:** 2026-10-22. **Статус:** принятое операционное решение для AGENT_PLAN docs-arm (без нового Console cold). Постановка и выводы — развёрнутыми предложениями.

## Постановка

Серия **`G1_S1_RERUN`** была запущена, чтобы проверить, является ли массовый `launch.exit≠0` на первом проходе G1 S1 случайным сбоем очереди/инфраструктуры или устойчивым исходом качества/остановки на текущем SHA. Критерий «полная кампания готова к `SYNTHESIS_FINAL`» требовал **`launch.exit=0` на последнем принятом run_id каждой волны** ([`G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md`](G1_S1_METRICS_BLOCKED_UNTIL_RERUN_2026-10-21.ru.md)).

После закрытия последней волны (**W02** RERUN rep3, `launch.exit=1`, offload `g1-s1-w02-rerun-done-20261022T030528Z`) таблица [`G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`](G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md) показывает: **3/13** волн exit-clean (W01, W13, W33), **10/13** с последним `launch.exit` ∈ {1,2}. Ни одна RERUN-волна не стала exit-clean. Оба хоста idle.

## Решение

1. **Не** запускать повторный cold RERUN тех же 10 волн на том же SHA без смены алгоритма/патча (F5 paired, silent-Test, CL-N1) или явного нового arm.
2. **Не** писать `SYNTHESIS_FINAL` как будто матрица 13 волн / 32 case полностью exit-clean.
3. **Разрешить** `SYNTHESIS_PARTIAL` / обновление PARTIAL rollup со строгой маркировкой:
   - метрики Acc/Цель / C2↔Console — **только** по волнам с `launch.exit=0` (сейчас W01, W13, W33) и их case из [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv);
   - для волн с `launch.exit≠0` — строка с `failure_class=launch_exit_N` (и краткий reason из queue/summary), **без** зачёта PASS×3 / converged доли в финальные проценты кампании;
   - группировка Trainer×Mode → Span → NeuronModel → Mod с колонками Train/Test — обязательна; PostTune ON/OFF — если применимо.
4. **DEBT-G1-exit-gate** остаётся **open**: drv по-прежнему печатает `SERIES_DONE`/`EXIT=0` при `launch.exit≠0`; чинить `run_series.sh` — отдельный infra-тикет, не блокер для PARTIAL docs.
5. Финальный G1 vs C2 по **всей** выбранной матрице — **отложен** до появления exit-clean большинства волн или явной смены отбора.

## Что из этого следует

RERUN доказал, что ложный «зелёный» drv и ненулевой `launch.exit` — **не** одноразовый glitch очереди: те же волны снова закрываются с кодами 1/2. Дальнейший прогресс плана смещается на (а) PARTIAL rollup + honest SYNTHESIS outline fill, (б) открытые DEBT алгоритма (silent-Test, CL-N1, F5 paired γ), (в) Controller v2 / V-gate без претензии на полную G1 exit-clean матрицу.

## Связанные артефакты

- [`G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`](G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md)
- [`G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md`](G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md)
- [`SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md`](SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md)
- [`TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md)
