# Сверка хвостов с исходным аудитом (2026-09-24)

Основание: [README.md](README.md) (повторный аудит), [PLAN.ru.md](PLAN.ru.md), исполнение [TAILS_EXEC.ru.md](TAILS_EXEC.ru.md).

Коммиты кода: PulseLib `8d429e7`, Bin `d9a61e1` (ранее `4521415` + T2 docs), Console SHA `5e7829bf…`.

## Исходный вывод аудита — что изменилось

Аудит утверждал: *«до устранения R01–R07 нельзя локализовать пять cold-FAIL только в морфогенезе»*.

После T0–T2:

| Утверждение аудита | Сейчас |
|---|---|
| Нет свежих run-bundles / Console SHA | Есть: T2 bundles + `build_manifest.json` |
| Stale Test mid может выдать cpp | Asym50: mid `.0100962` ≠ archive `.0116458` (R06) |
| Timeout/NaN → Success mid | Probes: timeout→4, NaN→5, mid=1 (R03) |
| Stale Success наследуется | Stale Success→NonSeparable (R04) |
| Branch soma side-channel | `sidechannel_absent=1` (R05) |
| Gold PASS + soft_cold FAIL ⇒ только morphogenesis | **Ещё нельзя**: H2 закрыл TipR Save lag; H3 soft vs strip ещё в прогоне |

## A01–A16 ↔ R01–R07 (кратко)

| ID | Аудит | Код | Приёмка tails | Закрытие |
|---|---|---|---|---|
| A01/A03 → R01 | close-first | да | analyzer probe; scheduler `not_observed` (`d1_r01_scheduler.json`) | **частично** |
| A02 → R02 | delay≥late + censored | да | код 1.55; N=1..8 + censored (`d1_n1_to_n8.json`) | **измерение ок** |
| A04–A06 → R07 | schema/N=1/CSV v3 | да | N=1 not per_stim; censored≠silence PASS | **измерение ок** |
| A07 | accepted | — | — | accepted |
| A08–A09 → R03/R04 | SampleState/Result | да | double Finalize `probe_only` (`d1_r04_*`) | **измерение ок**; cold model FAIL отдельно |
| A10 → R05 | collector | да | branch_ltz probe | **да** (код+probe) |
| A11 | delay N ticks | да | CE + `d5_pulse_delay.txt` | **да** |
| A12 | deferred | — | — | deferred |
| A13 | Preinh ApplyDefaults | да | `d5_preinh_xml_load.json` validate+class | **да** (load path) |
| A14 | segment∩rect | да | GUI 13 | **да** |
| A15 | CLI -S / exit | да | `d5_cli_save.json` `-S` без `-x` saves | **да** (Console) |
| A16 → R06 | clean workdir/accept | да | tipr hash provenance; Need=1 still fails; H2 flush | **да** (harness) |

## T2 vs «не локализовать в morphogenesis»

1. **br25 gold** — PASS на той же сборке → baseline измерительного контура жив.
2. **br25 soft_cold** — FAIL с `result=2` NonSeparable (не Success mid) → измерение R03 сработало; landscape отрицательный.
3. Одновременно **Need=1** и **Parameters TipR = soft_cold flat**, тогда как Train flag `tipr=canon` → перенос/Save весов в XML неполный (**A16/R06-adjacent**, не чистый morphogenesis).
4. **asym50** — gate PASS + fresh mid, но accept_run FAIL из‑за Need=1 → политика приёмки аудита соблюдена.

**Вывод:** cold FAIL больше не объясняется stale mid/Success-mid; часть br25 soft_cold объясняется неотделимым landscape, часть — незакрытым Save/Need. Локализация «только морфогенез» по-прежнему **запрещена** аудитом до H2/H3.

## P2 гипотезы

| H | Результат |
|---|---|
| H1 Canon vs Keep | Keep тоже NonSeparable → Canon не единственная причина |
| H2 TipR flag≠Parameters / Need=1 Save | **закрыто**: `flush_current_train_flag`; после flush tipr=canon Need=0; FAIL = NonSeparable/gate |
| H3 soft vs strip/full init | **done** — `no_material_diff` (`T3_H3_soft_vs_strip.json`) |
| H4 AutoScale/gap | **done** — no Delay/mid/TipR/Need differs (`T3_H4_autoscale.json`); overlay skipped |

## Политика claims

`verified` только с путями в `evidence/tails/`. Семь cases PASS — только после свежих runs каждого. A07/A12 без изменений.

После H2: soft_cold FAIL относится к **отрицательному landscape (NonSeparable)** + оставшийся morphogenesis/L, а не к stale TipR-flat артефакту harness. H3 soft vs strip: **no_material_diff**. H4 AutoScale: **no differs**; overlay skipped. TipR identity: `weights_identity.tipr_sha256` в provenance (D2). D4 cold matrix: **0/6 PASS** (`D4_matrix_summary.json`); seven PASS не заявлен.
