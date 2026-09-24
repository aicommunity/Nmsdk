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
