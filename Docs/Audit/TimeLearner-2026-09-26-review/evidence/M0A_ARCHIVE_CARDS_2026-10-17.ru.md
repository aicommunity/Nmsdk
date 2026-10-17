# M0-A: карточки архивных гипотез TimeLearner

Дата: 2026-10-17. Кампания dual-track. Срез исполнения: ветка `timelearner_fix`, root `d70cf5efa`, PulseLib `282073834` (содержит `da307d3`+фиксы), Bin `9dae5ed6d` (содержит `f1318005`).

Хосты: **`.11` = эта рабочая машина** (`/home/user/Nmsdk`, ветка `timelearner_fix`). `.17` = `10.245.1.17` (SSH `user`, тот же путь репозитория). Параллель: M1/короткие на `.17` (≤12), M0/длинные на `.11` (≤8), либо наоборот при загрузке.

## 1. Branch segment-order / stale-command

| Commit | Тема | Статус vs `2820738` | Ожидание | Мин. проверка |
|---|---|---|---|---|
| `10a9549` | Fix Branch segment-order liveness | уже вошло | порядок сегментов восстанавливается отдельно от sync | C++ `BranchSegmentOrderTransitionTest`; трасса W04 |
| `e4e0274` | repair order after exhausted amp collapse | уже вошло | order-repair после amp collapse | те же tests |
| `d09d72c` | Branch timing audit + order-repair error | уже вошло | отказ на MaxLen если порядок не восстановить | tests + W04 refusal path |
| `a79c80b` | clear stale structural commands | уже вошло | после structural edit нет stale command | `BranchStructuralSyncInvalidationTest` |

**Вывод:** повторно переносить patch не нужно. Остаётся причинная сверка в реальных W04 трассах (этап M0-B).

## 2. Structural dead-tip / amp-reference

| Commit | Тема | Classic | Branch | Статус |
|---|---|---|---|---|
| `4d66db5` | recover structural dead tips to cap | да | да | уже вошло; `StructuralDeadTipRecoveryTest` |
| `56a5962` | capture unit amp reference before topology edits | да | да | уже вошло; `TimeLearnerAmpReferenceTest` |
| `7c8f6f2` | step down to accepted structural amp count | да | — | уже вошло (Classic step-down) |

**Вывод:** early dead-tip при N≪128 исправлен. Post-fix W04 N0 всё ещё Need=1 — причина не MaxLen и не «забытый» dead-tip patch.

## 3. Rs floors / no-crossing

| Элемент | Статус | Примечание |
|---|---|---|
| `NNeuronTimeLearnerResistanceBounds.h` + `ComputeNoCrossingResistanceFloor` | уже вошло в текущий PulseLib | вызывается из Classic/Branch |
| Применение floor в `NormalizationMode=0` | не считать действующим без доказательства | interim: floor параметрического режима не гарантирует ограничение в structural |
| Архивный rsfloor-current / `.11` diff | частично вошло / не проверено построчно vs `2820738` | кандидат; не переносить пакетом |

## 4. Gamma / per-input gamma

| Элемент | Статус |
|---|---|
| W04 gamma configs / ablation JSON в diagnostics | не проверено причинно на текущем SHA |
| `BranchAttenuationGammaTest` | в коде |

Вывод причинный только при совпадающих входах/коде/Console.

## 5. Dataset / sample-burst / AutoSave / runner post-flag

| Гипотеза | Статус |
|---|---|
| Dataset sample-burst (архив `.17` PulseLib) | не проверено; отдельная гипотеза |
| AutoSave частота (sep13-source) | не проверено |
| Runner SIGTERM после grace при Need=0 | подтверждено как infra, не отмена сходимости |

## 6. Сохранённые W04 structural N0 на Data `.17` (для M0-B)

| Условие | RUN / путь | Need | Длины | Failure | Test |
|---|---|---|---|---|---|
| Step 1 ГОм PSIoff | `.../branch480-n0-matched-step1g/.../W04_BR480_N0_PSIoff` | 1 | `[1,67,89,1]` | incomplete | not evaluated |
| Step 86 МОм PSIoff | `.../branch480-n0-matched-step86m/.../W04_BR480_N0_PSIoff` | 1 | `[1,75,89,1]` | incomplete | not evaluated |
| Исторический Step 86 МОм (diagnostics) | `branch_w04_480_n0_single_synapse_ref_2026-10-16` | 1 | `[1,75,89,1]` | time_limit | not evaluated |

MaxLen=100 не достигнут. Карточки закрывают этап A для запуска M0-B по audit-логам этих попыток.
