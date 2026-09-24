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
| Gold PASS + soft_cold FAIL ⇒ только morphogenesis | **Ещё нельзя**: есть Save/Need=1 и TipR flag≠Parameters |

## A01–A16 ↔ R01–R07 (кратко)

| ID | Аудит | Код | Приёмка tails | Закрытие |
|---|---|---|---|---|
| A01/A03 → R01 | close-first | да | analyzer probe; scheduler freq нет | **частично** |
| A02 → R02 | delay≥late + censored | да | код 1.55; Dataset→CSV e2e N=1..8 нет | **частично** |
| A04–A06 → R07 | schema/N=1/CSV v3 | да | metrics_probes; нет полного N=1..8 e2e | **частично** |
| A07 | accepted | — | — | accepted |
| A08–A09 → R03/R04 | SampleState/Result | да | posttune probes + Branch 8/8 | **измерение ок**; cold model FAIL отдельно |
| A10 → R05 | collector | да | branch_ltz probe | **да** (код+probe) |
| A11 | delay N ticks | да | CE IntegerDelay PASS | **да** (точечно) |
| A12 | deferred | — | — | deferred |
| A13 | Preinh ApplyDefaults | да | static count; полный Storage/XML нет | **частично** |
| A14 | segment∩rect | да | GUI 13 | **да** |
| A15 | CLI -S / exit | да | help + static; не GUI multi-channel | **частично** |
| A16 → R06 | clean workdir/accept | да | e2e+unit+T2 isolation; TipR Save lag | **частично** |

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
| H2 TipR flag≠Parameters / Need=1 Save | **следующая** |
| H3 soft vs strip/full init | очередь |
| H4 AutoScale/gap | очередь |

## Политика claims

`verified` только с путями в `evidence/tails/`. Семь cases PASS — только после свежих runs каждого. A07/A12 без изменений.
