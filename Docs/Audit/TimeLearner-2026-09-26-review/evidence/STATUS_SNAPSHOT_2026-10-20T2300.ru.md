# Статус кампании 2026-10-20 ~23:00 MSK

Оба хоста **idle** (Console=0, tmux пуст). Диск `.11` ~240 ГБ свободно, `.17` Data ~1.8 ТБ свободно.

## Trainer×Mode → результаты (закрытые cold)

### Classic×N1 W01 (AsymRm, PostTune OFF)

| Run | Исход | L | TipR | Test |
|---|---|---|---|---|
| D2b.0 E1 defaults | converged_need0 | 25 22 15 1 | @Rmin | silent 00000000 |
| F2.pref PreferMeasured+MarkRminBE | converged_need0 | 25 22 15 1 | @Rmin | gate hang |
| F2.reset ResetBeforeBurst | converged_need0 | 25 22 15 1 | @Rmin | gate hang |
| **F6.mid** DisableMidbandWalk | **converged_need0** | **25 22 15 1** | **@Rmin** | silent 00000000 (gate_ok, child_rc=-15) |
| D2b.1 RminTol=1 | Need=1 stall | ≈27… | @Rmin, abs_dt>tol | — |

Train/Test: `TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSIoff/{Train,Test}`.

**Вывод:** F6 midband-off на W01 **не меняет** финал относительно defaults (та же L/@Rmin/silent) — на этом кейсе TipR@Rmin достигается и без midband→Rmin.

### Classic×N0 W01 — E2 S0/S1/S2

| Run | Исход | L | TipR | Test |
|---|---|---|---|---|
| E2.S0 / S1 / S2 | все **converged_need0** | **27 22 15 1** | **86 МОм ×4** | silent 00000000 |

Три плеча E2 на W01_N0 **эквивалентны** по L/TipR/fires (silent). Полный R8 ещё не стартовал.

### Classic×N1 W02 / Branch W10

| Run | Исход |
|---|---|
| D2b.5 W02 Signed+RminTol | not_converged L=54 44 1 1 |
| D2b.6 Branch EstDelayInit=0.01 | not_converged L=3 3 2 1 |
| D2b.7 Branch control | converged_posttune_finalized L=7 6 4 1, silent |

## Открыто дальше

F4/F5 патчи; F6 Rmin=XML floor (вторая часть A8); E2 полный R8; Done_BE audit на новом Console; silent-Test DEBT; G1/Controller.
