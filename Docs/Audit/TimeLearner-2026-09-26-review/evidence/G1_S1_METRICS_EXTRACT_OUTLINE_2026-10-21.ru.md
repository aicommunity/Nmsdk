# G1 S1 — черновик извлечения метрик (read-only)

**Срез:** 2026-10-21 после tick 124 exit-audit. **Не запускать** новые train/matrix run.

## Целевой артеfact

TSV по образцу [`E2_matrix_2026-10-21.tsv`](E2_matrix_2026-10-21.tsv):  
`arm,wave,rep,run_id,queue_status,case,training_convergence,DendriteLength,TipSynapseResistance,FixedLTZThreshold,fires,failure_class,separation_or_detection`.

## Входы

| Host | `TIMELEARNER_MATRIX_RUNS_ROOT` | ASSIGNMENTS / drv |
|------|----------------------------------|-------------------|
| `.11` | `$HOME/TLAgent-20261020/runs` | `$HOME/TLAgent-20261020/agent-reports/drv-G1.S1.W*.log`, `$REPORTS/ASSIGNMENTS.tsv` |
| `.17` | `/media/user/Data/TLAgent-20261020/runs` | `/media/user/Data/TLAgent-20261020/agent-reports/drv-G1.S1.W*.log` |

Per-wave lane paths в ASSIGNMENTS (`st=`); после offload — runs + `matrix_result.json` / script-logs под `{run_id}/`.

## Инструменты (существующие)

- `tools/summarize_run.py` (Nmsdk / lane) — колонки convergence, dendrite, fires, sep/det (см. E2 cards).
- `queue_status.json`, `run_manifest.json` под `{run_id}/` — статус queue, selected cases.
- Gate: **только rep3 run_id из [`G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md)**; для `launch.exit≠0` — строка с `failure_class=launch_exit_N`, метрики case по факту наличия result.

## Фазы (read-only)

1. **Inventory:** 32 case × rep3 run_id (из drv) + `launch.exit` + `queue_status`.
2. **Pilot extract:** W01/W13/W33 (exit=0) — проверить pipeline summarize на одном run_id.
3. **Full batch:** rsync или SSH summarize по всем run_id; merge → `G1_matrix_2026-10-21.tsv`.
4. **Rollup:** группировка Trainer×Mode → Span → NeuronModel → Mod; сверка с [`G1_predictions_2026-10-21.tsv`](G1_predictions_2026-10-21.tsv).

## Блокер

9/12 rep3 с `launch.exit` 1/2 — финальная матрица G1 S1 **неполная** до rerun или осознанного partial-report с пометкой non-exit waves.

---
Зеркало: `/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md`.
