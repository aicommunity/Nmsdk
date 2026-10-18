# M0-C: повтор W04 Branch 480/N0 Step 86 МОм

## Что проверяли (уточнение)

Один cold-повтор **`W04_BR480_N0_PSIoff`**: Branch structural N0, overlay **`SynapseResistanceStep=86e6`**, `-t=900`, без Test quality. Цель: воспроизвести matched Step86M и классифицировать failure (баг контракта vs предел алгоритма).

## База до фикса — `tl-m0-c-w04-86m-11-20261017-01`

| Поле | Значение |
|---|---|
| convergence | `not_converged_at_stop` |
| Need / failure_reason | 1 / 0 |
| lengths / N | `[1,75,89,1]` / `[1,88,128,1]` |
| initial_amp[1] | ≈0.01583 (эталон есть) |
| iter | 440 |

## Корневая причина

Не «отсутствие amp-ref», а **ложный re-sync после structural edit**:

1. Рост L/N на пульсе 1 → `InvalidatePulseSyncAfterStructuralChange` сбрасывал `PulseSynced`.
2. На finish якоря `length_ok` проходил через старый `|Dissync|≈0` **без PeakSeen** → pulse N−2 снова `PulseSynced`, Active прыгал **1↔3**.
3. `ChangeSynapseStatus` при `MaxAmp==0`/`PeakSeen=false` трактовал «короче Initial» как +N.

## Фиксы (PulseLib `2f22c26` и предки)

| Коммит | Суть |
|---|---|
| `24de804` | PeakSeen gate на `PulseSynced`; не ±N без peak attempt |
| `cb57b08` | `InvalidPeakNoRecovery` не считает пустые окна |
| `35b805c` | защита `EstDelayPerSeg` от sentinel prev_dt |
| `80c28e8` | не травить `Dissync` IterationGap (демпфирование длины) |
| `b861f8b` | **scoped reopen**: после edit пульса k чистить sync только `≤k`, якорь оставить |
| `2f22c26` | scoped edit не сбрасывает NoImprove/LastLengthDelta; Dissync length_ok только при свежем LastAbsDt |

## Повтор после фикса

| RUN_ID | Статус |
|---|---|
| `tl-m0-c-w04-86m-fix-20261018-11-05` | остановлен (заменён после фикса роста) |
| `tl-m0-c-w04-86m-fix-20261018-11-36` | в очереди после M1 (`/tmp/dualtrack-m1m0.log`) |

Ожидаемые признаки: нет thrash Active 1↔3; после роста на 1 якорь остаётся synced; PeakSeen нужен для commit sync; NoImprove может остановить L-осцилляцию. Итог Need/длины — дописать по завершении.
