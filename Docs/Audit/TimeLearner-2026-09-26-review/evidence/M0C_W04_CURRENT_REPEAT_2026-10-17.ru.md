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

## Корневая причина (контракт sync)

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

## Повтор после фикса — `tl-m0-c-w04-86m-fix-20261018-11-36` (финал)

Хост `.11`, PulseLib `2f22c26`, Console `0b25d88f…`. Fingerprint `7ff558e90…`.

| Поле | Значение |
|---|---|
| convergence | `not_converged_at_stop` |
| stop | worker poll ceiling (~401×30 s ≈ 3.3 ч wall); `child_rc=-15` |
| Need / failure_reason | 1 / 0 |
| lengths / N | `[49,97,89,1]` / `[86,128,128,1]` |
| synced | `[0,1,1,1]` (pulse0 не закрыт) |
| TipR | все `86e6` (flat Rmax, Mode=0 / PostTune off) |
| last iter | 351, Active=0, amp0≈2e-7 |

### Прогресс vs база

| | База `.17-01` | После фиксов `11-36` |
|---|---|---|
| Thrash Active 1↔3 | да (контракт) | **нет** |
| Pulse2/1 synced | нет (застрял раньше) | **да** (N=128) |
| Pulse0 | L=1 | L=49, N=86 mid-cap |
| Need=0 | нет | нет (остановлен на росте pulse0) |

**Вердикт:** баг контракта sync/PeakSeen **снят** (монотонный reverse-train 2→1→0). Остаток — **предел/стоимость N0-структуры**: на каждом пульсе L замирает, затем долгий N→128 при коллапсе amp; wall-time/polls кончаются до sync pulse0.

## Сводка

M0-C больше не «сломанный Active». Следующий рычаг — ускорить/ограничить фазу +N при amp-collapse (best-effort раньше, меньший cap, или TipR/Mode=1 на N0), плюс поднять budget прогона для доказательства Need=0.

## P0 early BE — abort D7 — `tl-m0-c-w04-86m-p0-20261018-18-20`

Хост `.11`, PulseLib `e23f2e9`, Console `9d8da6ad`. Early amp-collapse floor N=8 сработал на pulse1, но:

| Поле | Значение |
|---|---|
| L / N | `[1,65,89,1]` / `[1,8,128,1]` |
| synced / BE | `[0,0,1,1]` / `[0,1,1,0]` |
| stop | **MANUAL_STOP** — idle deadlock |

**D7:** `DendBestEffortSynced[1]=1` при `L[1]=65 ≤ L[2]=89`. Sync commit требует `L[k]>L[k+1]` → PulseSynced никогда не ставится, ±L не продолжается.  
**Фикс P0b:** Mode=0 early BE (и NoImprove BE) только если `!segment_order_violation`; иначе `request_segment_order_repair` (+L).

## P0b cold после D7 — `tl-m0-d7-20261018-20-27`

Хост `.11`, isolated `RUNS_ROOT=…/postp0-m0-d7/`, Console `67cd0825` (D7 local).

| Этап | L / N / sync / BE |
|---|---|
| pulse2 close | `…,89,1` / `…,128,1` / `…,1,1` / `…,1,0` |
| pulse1 close | `[?,97,89,1]` / `[?,12,128,1]` / `[0,1,1,1]` / `[0,1,1,0]` — BE только после `L[1]=97>89` |
| pulse0 stall | `[81,97,89,1]` N=`[12,12,128,1]` PeakSeen0=`0` — **не D7** (BE=0, D7_bad=0) |

**Вердикт D7:** deadlock снят. Остаток M0 — peak-blind на pulse0 (как класс D6), не BE∧¬seg_ok.

## Финал P0b cold — `matrix_result` (2026-10-19)

| Поле | Значение |
|---|---|
| convergence | `not_converged_at_stop` |
| Need / failure_class | 1 / `train_incomplete` |
| L / N | `[81,97,89,1]` / `[12,12,128,1]` |
| synced / BE / peak | `[0,1,1,1]` / `[0,1,1,0]` / `[0,1,1,1]` |
| TipR | flat `86e6` (Mode=0) |
| iters / D7_bad | 441 / **0** |
| child_rc | 0 (train exited incomplete) |

**Итог M0 Post-P0:** D7 закрыт на cold. Need=0 **не** достигнут — класс **D6 peak-blind pulse0** (Active=0, PeakSeen[0]=0 при sync 1..2). Дальше — diagnostic peak0, не повтор D7.
