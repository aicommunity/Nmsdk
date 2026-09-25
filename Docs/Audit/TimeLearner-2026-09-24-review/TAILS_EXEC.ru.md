# Исполнение TAILS_PLAN (2026-09-24)

## T0 — Rebuild + regression floor — DONE

| Проверка | Результат | Evidence |
|---|---|---|
| Console rebuild после PulseLib `8d429e7` | SHA `5e7829bf…` (бит-идентичен предыдущей dirty-сборке R01–R07) | `_repro/build_manifest.json` |
| GUI | 13 PASS | `evidence/tails/gui.txt` |
| CE без A12 | 9 PASS | `evidence/tails/ce_no_a12.txt` |
| Branch | 8 PASS | `evidence/tails/branch.txt` |
| verifier unit | 21 PASS | `evidence/tails/verifier_unit.txt` |
| review posttune | timeout→4, NaN→5, stale Success→2, mid=1; ltz sidechannel_absent | `evidence/tails/posttune_probes.txt` |
| review analyzer | advance_window + incomplete_sample | `evidence/tails/analyzer_boundaries.txt` |
| review verifier | empty fires reject; phase9 removes stale flag; crash no salvage | `evidence/tails/verifier_probes.txt` |

Probe stubs обновлены под `SampleMetricState` / `pending_neu_*` (`Scripts/audit-probes/generate_*.py`).

## T1 — Приёмка измерения — DONE (без cold)

| Пункт | Результат |
|---|---|
| R06 e2e crash+stale Asym50 | PASS fail path; mid `.0116458` не переносится | `evidence/tails/t1_e2e_negative.json` |
| R03/R04 probes | PASS (см. T0 posttune) |
| R01 reachability | probe-уровень; scheduler frequency не инструментирован | `evidence/tails/t1_measurement.json` |
| R02/R07 | delay≥1.55 в коде; metrics schema_ok | `t1_measurement.json` + metrics_probes |

## T2 — Control runs — IN PROGRESS

Batch: `_repro/runs/T2_control_batch.sh`  
Log: `_repro/T2_control_batch_20260924T165948Z.log`

1. `br25_on --skip-train` (gold) — **rc=0** (2026-09-24T17:05:03Z); work `runs/br25_on_20260924T165949Z_work`; mid≈0.0718; evidence `evidence/tails/T2_gold_skip_train_RESULT.md`
2. `br25_on` soft_cold — **running** Train `-t 320` work `runs/br25_on_20260924T170503Z_work`
3. `asym50` cold (stale-flag isolation via clean workdir) — queued  

T3 (morphogenesis) стартует только при FAIL после T2.

## T4 — Docs / checks — DONE

- 6 EXP README: workspace/clean-workdir note добавлен  
- Preinh/Delay/CLI: `evidence/tails/t4_component_checks.json` (+ CE IntegerDelay PASS, CLI `-S` в help)  
- `status.json` обновлён; claim policy: без fresh bundles нет cold PASS  

## Критерий remediation

T0+T1 закрыты с evidence. T2 evidence появится по завершении batch (часы). Полный PASS семи cases — отдельно.

## T2 — итог (2026-09-24T18:39Z)

| Case | rc | Verdict | Ключевое |
|---|---|---|---|
| br25 gold `--skip-train` | 0 | **PASS** | fires `10000000` mid≈0.0718 cpp |
| br25 soft_cold | 1 | **FAIL** | NonSeparable; TipR params=flat; Need=1 |
| asym50 cold | 1 | **FAIL** (Need=1) | gate ok fires `10000000`; mid **0.0100962 ≠** archive `.0116458` |

R06 isolation подтверждена. Сводка: `evidence/tails/T2_summary.json`.

## T3 — H1 Canon vs Keep — DONE

KeepDone на том же soft_cold L также `result=2` NonSeparable → **Canon не единственная причина**.  
Evidence: `evidence/tails/T3_H1_canon_vs_keep.json`.

Следующие гипотезы (не в этом прогоне): soft vs strip/full init; TipR flag≠Parameters; AutoScale/gap.

## Критерий remediation

T0+T1+T2 **выполнены и задокументированы**. Полный PASS семи cases — нет. T3 начат (H1).


## T3 — H2 TipR Save lag — DONE

Console `-S` пишет Parameters только после `IsCalcFinished`. Early stop после flag оставлял TipR=flat Need=1 при flag tipr=canon.

Исправление harness: `flush_current_train_flag` (текущий workdir flag → Parameters/Model). Retest: tipr_class=**canon**, Need=0; FAIL только fires/gate (NonSeparable mid=1).

Evidence: `evidence/tails/T3_H2_flag_flush_RESULT.json`.

## D1 — Измерительная приёмка — DONE

| Пункт | Evidence |
|---|---|
| R01 scheduler | `not_observed` — `evidence/tails/d1_r01_scheduler.json` |
| R02/R07 N=1..8 + censored | `evidence/tails/d1_n1_to_n8.json` (all_pass) |
| R04 double Finalize | `evidence/tails/d1_r04_double_attempt.txt` (`probe_only`) |

## D2 — Harness — DONE

| Пункт | Результат |
|---|---|
| asym50 Need=1 | нет Train flag; Finalize не за `-t 320`; `train_t→640`; `d2_asym50_need1_diag.json` |
| TipR hash provenance | `weights_identity` в `build_provenance` |
| unit | **24** PASS (`test_need1_with_gate_ok_still_fails`, `test_weights_identity_*`) |

## D3 — Morphogenesis H3/H4 — DONE

| H | Verdict | Evidence |
|---|---|---|
| H3 soft vs strip | **no_material_diff** (оба NonSeparable, TipR canon, mid=1, L=1…) | `T3_H3_soft_vs_strip.json` |
| H4 AutoScale 1 vs 0 | **no material differs** (Delay/mid/TipR/Need alike) | `T3_H4_autoscale.json` |
| Overlay | skipped (H3/H4 не локализовали) | — |

Скрипты: `_repro/runs/T3_H3_soft_vs_strip.py`, `T3_H4_autoscale.py`.

## D4 — Cold matrix — DONE (0/6 PASS)

Batch `T4_cold_matrix.sh` utc `20260924T204259Z`. All six `rc=1`. **seven_pass_claim=false**.

| case | run_id | note |
|---|---|---|
| br25_off | `br25_off_20260924T204259Z` | gate_ok; tipr other |
| asym25 | `asym25_20260924T214120Z` | gate FAIL; tipr flat |
| asym50 | `asym50_20260924T214908Z` | exited Need; tipr canon; mid cpp |
| br100_keep | `br100_keep_20260924T234016Z` | gate FAIL |
| phase6_480 | `phase6_480_20260924T234719Z` | gate FAIL; expect_fires dual 10000010 vs strict 10000000 |
| br100_search | `br100_search_20260925T015547Z` | same_reverted; fires fail expect |

Evidence: `evidence/tails/D4_matrix_summary.json`; RESULT section T4 in `_repro/POSTTUNE_VERIFY_RESULT.md`.

## D5 — Preinh / Delay / CLI — DONE

| Пункт | Evidence |
|---|---|
| Preinh XML load | `d5_preinh_xml_load.json` |
| NPulseDelay | `d5_pulse_delay.txt` |
| CLI `-S` без `-x` | `d5_cli_save.json` |

## D6 — Docs sync — DONE

status.json (Bin `85d973a+`, verifier 24, R01 `not_observed`, R04 `probe_only`, D4 0/6); TAILS_PLAN/EXEC; AUDIT_RECONCILE; POST_TRAIN_VERIFY (`flush_current_train_flag`); CONTROL_RUNS_P15; MORPHOGENESIS_P2; 7× EXP README current verdict; review-20260924 README probe commands.

**Remediation (PLAN criterion D1+D2+D3+D6):** закрыт с evidence. **Семь PASS:** нет (D4 0/6).

## D5 — Preinh / Delay / CLI — DONE

| Пункт | Evidence |
|---|---|
| Preinh XML load | `d5_preinh_xml_load.json` (validate rc=0, class `NSPNeuronGenPreinh2_5AsymRmD001C1e9`) |
| NPulseDelay | `d5_pulse_delay.txt` (bypass/buffer/reset) |
| CLI `-S` без `-x` | `d5_cli_save.json` (Project saved; process stays until kill) |
