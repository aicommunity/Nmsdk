# Dual-host назначение cold PostTune-fix (2026-10-19, кампания v5 — финал)

PulseLib финал `d52dc1c`. Console SHA16 (оба хоста после sync): `d2862a42fa266145`.  
Лимиты: `.11` PARALLEL≤8 · `.17` PARALLEL≤12.  
Канон группировки: [RESULT_GROUPING_HIERARCHY.ru.md](RESULT_GROUPING_HIERARCHY.ru.md).  
Сводная: [POSTTUNE_FIX_COLD_SUMMARY_2026-10-19.ru.md](POSTTUNE_FIX_COLD_SUMMARY_2026-10-19.ru.md).

## Изоляция

| Host | RUNS_ROOT | RUN_ID prefix |
|---|---|---|
| `.11` | `/home/user/TimeLearnerAudit-20261017/dualtrack/runs/n1-posttune-fix-11` | `tl-ptfix-v5-11-pt{on\|off}-…-<WAVE>` |
| `.17` | `/media/user/Data/NmsdkRuntime/TimeLearnerMatrixRuns/n1-posttune-fix-17` | `tl-ptfix-v5-17-pt{on\|off}-…-<WAVE>` |

Launcher: `TimeLearnerAudit-…/dualtrack/run_ptfix_v5_complete.sh` (+ ручные W48 дозапуски при disk/pause).

## Фактические RUN_ID (v5)

### Host `.11`

| matrix_id | ON | OFF |
|---|---|---|
| `W10_HIST_br25_gen`, `W10_HIST_br50_gen` | `tl-ptfix-v5-11-pton-20261019-17-23-W10` | `tl-ptfix-v5-11-ptoff-20261019-19-37-W10` |
| `W12_HIST_fs25_gen`, `fs25_preinh`, `fs50_gen` | `…-pton-…-17-23-W12` | `…-ptoff-…-19-37-W12` |
| `W48_BR_FS25_N1_gen`, `preinh` | `…-pton-…-18-42-W48` | `…-ptoff-…-20-47-W48` |

### Host `.17`

| matrix_id | ON | OFF |
|---|---|---|
| `W10_HIST_br25_preinh` | `tl-ptfix-v5-17-pton-20261019-17-25-W10` | `…-ptoff-…-20-46-W10` |
| PASS×3 `br25_nextseg`, `br50_preinh`, `br100_preinh` | **reuse** `tl-ptfix-passx3-v4-17-20261019-16-40` | `…-ptoff-…-20-46-W10` |
| `W09_HIST_asym25` | `…-pton-…-17-25-W09` | `…-ptoff-…-20-46-W09` |
| `W11_HIST_asym25_preinh` | `…-pton-…-17-25-W11` | `…-ptoff-…-20-46-W11` |
| `W12_HIST_fs100_gen` | `…-pton-…-17-25-W12` | `…-ptoff-…-20-46-W12` |
| `W01_CL25_N0`, `CL50_N0`, `CL25_N1` | `…-pton-…-17-25-W01` | `…-ptoff-…-20-46-W01` |

## Монитор

Остановлен после closeout v5 (`/tmp/ptfix_v5_monitor_loop.pid`). Sentinel был `AGENT_LOOP_TICK_ptfix`.
