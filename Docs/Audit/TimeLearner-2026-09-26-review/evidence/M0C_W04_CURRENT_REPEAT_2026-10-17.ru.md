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
| `tl-m0-c-w04-86m-fix-20261018-11-36` | **Train идёт** (~iter 82): Active=2, L=`[1,1,89,1]`, N=`[1,1,78,1]`, synced=`[0,0,0,1]`, TipR все `86e6`, need=1 |

Live: якорь synced, thrash 1↔3 не виден; идёт наращивание L/N на pulse2 (N0 structural). Итог Need/длины — дописать по `ALL_DONE` (мониторинг каждые 5 мин, PID loop `2044944`).
