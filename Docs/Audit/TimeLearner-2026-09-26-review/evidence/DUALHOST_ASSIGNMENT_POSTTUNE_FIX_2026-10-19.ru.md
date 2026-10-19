# Dual-host назначение cold PostTune-fix (2026-10-19)

PulseLib `8575df3` · Console SHA16 `.11` `3034d0872f856d7d` · root `252e2ce6e`.  
Лимиты: `.11` PARALLEL≤8 · `.17` PARALLEL≤12.  
Канон группировки: [RESULT_GROUPING_HIERARCHY…](RESULT_GROUPING_HIERARCHY.ru.md).

## Изоляция

| Host | RUNS_ROOT | RUN_ID prefix |
|---|---|---|
| `.11` | `/home/user/TimeLearnerAudit-20261017/dualtrack/runs/n1-posttune-fix-11` | `tl-ptfix-w*-11-*` |
| `.17` | `/media/user/Data/NmsdkRuntime/TimeLearnerMatrixRuns/n1-posttune-fix-17` | `tl-ptfix-w*-17-*` |

Списки кейсов **не пересекаются**. ON/OFF пары — на одном host, суффиксы `-pton` / `-ptoff`.

## Волна 1 (контроль фикса)

| matrix_id | Mode PostTune | Host | RUN_ID |
|---|---|---|---|
| `W10_HIST_br25_gen` | ON | `.11` | `tl-ptfix-w1-11-pton-…` |
| `W10_HIST_br50_gen` | ON | `.11` | same batch ON |
| `W10_HIST_br25_gen` | OFF | `.11` | `tl-ptfix-w1-11-ptoff-…` |
| `W10_HIST_br50_gen` | OFF | `.11` | same batch OFF |
| `W10_HIST_br25_preinh` | ON | `.17` | `tl-ptfix-w1-17-pton-…` |
| `W09_HIST_asym25` | ON | `.17` | same |
| `W10_HIST_br25_preinh` | OFF | `.17` | `tl-ptfix-w1-17-ptoff-…` |
| `W09_HIST_asym25` | OFF | `.17` | same |

## Волна 2 (NeuronModel / Classic / BR-FS)

| matrix_id | Host |
|---|---|
| `W12_HIST_fs25_gen`, `W12_HIST_fs25_preinh`, `W12_HIST_fs50_gen` | `.11` |
| `W12_HIST_fs100_gen` или `W13_HIST_fs100_preinh` | `.17` |
| `W01_CL25_N0_PSIoff`, `W01_CL50_N0_PSIoff` (+ N1 short) | `.17` |
| `W48_BR_FS25_N1_gen`, `W48_BR_FS25_N1_preinh` | `.11` |

Все — парный ON затем OFF (отдельные RUN_ID).

## PASS×3 (§5)

| Case | Host |
|---|---|
| `W10_HIST_br25_nextseg` | `.17` |
| `W10_HIST_br50_preinh` | `.17` |
| `W10_HIST_br100_preinh` | `.11` |

## Монитор

`/home/user/TimeLearnerAudit-20261017/dualtrack/monitor/n1-posttune-fix/` + arm после старта Console. Тик ~15 мин. Sentinel `AGENT_LOOP_TICK_ptfix`.
