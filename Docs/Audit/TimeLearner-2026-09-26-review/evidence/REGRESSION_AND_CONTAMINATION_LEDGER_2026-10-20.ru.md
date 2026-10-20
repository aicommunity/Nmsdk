# Ledger регрессий и контаминаций — 2026-10-20

Источник: фаза R (CODE_CONFIRM + A2/B1/E0 + D1 in progress). Правила: `invalidate` / `reinterpret` / `ruler_change`.

## Контаминации входных данных

| ID | Что | Объём | Вердикт | Действие |
|---|---|---|---|---|
| A15 | `fix_generator_tip_links` переписывал Item синапс→канал | FAIL Test **45**/353; **A3.1 A15_ACTIVE_AT_RUNTIME** ratios≈8.9/8.0/6.6/1.0 | CONTAMINATES + ACTIVE | B1 `d92d5b71` + B2 repair; dirty Test Acc **invalidate** |
| H-A15b | SoftCold `rewrite_links_to_tip1` каждый queue | Train fan-out / dangling risk | CONTAMINATES (hyp.) | B1 чинит rewrite; E2 S0↔S1 подтвердит влияние на обучение |

## Регрессии алгоритма (код d52dc1c)

| ID | Вердикт R1 | Статус фикса | Примечание |
|---|---|---|---|
| A1 DelayUseOf model-vs-meas | CONFIRMED | open → F2 | |
| A2 EstDelay abs EMA | CONFIRMED | open → F1/`UseSignedDelayEstimate` | E1 flags committed PulseLib `393463d8` |
| A3 kRminLengthTolFactor=4 | CONFIRMED | open → F7 train-param | |
| A4 absolute eps | CONFIRMED | open → F4 | |
| A5 Reset after change | CONFIRMED | open → F3 | |
| A6 midband→Rmin | CONFIRMED | open → F6 | |
| A7 gamma bias | CONFIRMED | open → F5 | |
| A8 Rmin=max(Rm)/q | CONFIRMED | open → F6 | |
| A9 train mute vs recognize | CONFIRMED | OPEN до mid-without-CanonRmin | |
| A10 multi BE | CONFIRMED | open → F2 Done_BE | |
| A11 CanonRmin + mid on Test-8 | CONFIRMED | OPEN | |
| A12–A14 | CONFIRMED | design / F8 freeze base | |
| CL-N1 stall | OPEN_NEEDS_R2→**not_in_PulseLib_window** | W01 both converged_need0; W02 both not_converged_at_stop (780 TipR1e11 / d52 TipR1e10) | |
| EstDelay seed ≠ τ | CONFIRMED | D2/E0 overlay | |
| ok_audit_v2 | RULER_CHANGE | — | исторические Acc **reinterpret**, не regression |

## Finding README #5

τ=0.25 W13/W37 infeasible — зафиксировано как физический предел (ledger), не баг тренера.

## Прогоны

| RUN | SHA Console | Случай | Статус |
|---|---|---|---|
| D1.d52dc1c-*-12466 | A0 | W02_CL480_N1_PSIoff | **not_converged_at_stop** TipR 1e10 |
| D1.d52dc1c-*-20123 | A0 | W01_CL50_N1_PSIoff | **converged_need0** |
| D1.780ffc7-*-3629 | bisect Console | W02_CL480_N1_PSIoff | **not_converged_at_stop** TipR 1e11 |
| D1.780ffc7-*-27127 | bisect Console | W01_CL50_N1_PSIoff | **converged_need0** (eval issue paused) |
| A1 .17 | A0 | br25_nextseg / preinh / br50_gen | MATCH / DEVIATION silent / DEVIATION better |
| D2.0–D2.2 .17 | A0 | W01_CL50_N1 EstDelay/gamma | running |

Обновлять по мере summarize_run.


## D1 бисекция — вердикт 2026-10-20T15:18Z

Постановка проверяла cold Classic×N1 на концах окна PulseLib `780ffc7` (i=0) и `d52dc1c` (i=11). W01_CL50_N1_PSIoff сходится (`converged_need0`) на обоих SHA. W02_CL480_N1_PSIoff на обоих SHA уходит в `not_converged_at_stop` с TipR у потолка (1e11 на i=0, 1e10 на i=11). По правилу карты D1 §2 бисекция **останавливается**: регрессии Classic N1 внутри окна PulseLib 11.09–19.10 на текущих входах нет; искать раньше 11.09, вне PulseLib или в параметрах/алгоритме (ось D2 EstDelay/γ).


## A3 runtime (2026-10-20T15:38Z)

A3.1: см. `A3_1_verdict` в agent-reports; TRACE hang после записи CSV (оба варианта). Model SHA repaired не менялся после run.
A3.2: best taps ≈ DendriteLength на 3/4 каналах → гипотеза CPP_RELINKS_TO_DENDRITELENGTH (silent soma_1 как C1).
D2.0 control .17: converged_need0.
