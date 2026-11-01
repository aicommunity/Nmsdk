# Статус кампании 2026-10-21 ~05:14 MSK

Оба хоста **idle** (Console=0, tmux E2 пуст). `.11` Avail≈234 ГБ; `.17` корень Avail≈76 ГБ (снова у порога soft-cold 80 ГБ), Data≈1.7 ТБ свободно.

## E2 R8×3 — SERIES_DONE

Все 12 серий (`S0/S1/S2` × `W01/W02/W04/W10`) дошли до `SERIES_DONE` / `EXIT=0` (по 3 launch на серию). Ниже — последние **успешные** cold-сравнения (rep3 W01 упал `worker_exit=1` / incomplete — совпало с Avail корня &lt;80 ГБ).

### Classic×N0 W01 — Train/Test `W01/inputs/W01_CL50_N0_PSIoff/{Train,Test}`

| Arm | Rep1–2 (типично) | L | TipR | fires |
|---|---|---|---|---|
| S0 / S1 / S2 | converged_need0 | 27 22 15 1 | 86 М×4 | silent 00000000 |

**Вывод:** S0↔S1↔S2 по W01_N0 **эквивалентны** (та же L/@Rmin/silent). Rep3 infra-fail не меняет картину эквивалентности.

### Classic×N1 W02 — `W02/inputs/W02_CL480_N1_PSIoff/{Train,Test}`

| Arm | Исход | L | TipR |
|---|---|---|---|
| S0 / S1 / S2 | **not_converged_at_stop** | 54 44 1 1 | 1e10 1e10 86 М 86 М |

**Вывод:** CL-N1 stall воспроизводится на всех трёх плечах одинаково — не регрессия E1 vs baseline.

### Branch×N1 W04 — `W04/inputs/W04_BR100_N1_PSIoff/{Train,Test}`

| Arm | Train | L | fires | failure |
|---|---|---|---|---|
| S0 / S1 / S2 | converged_need0 | 24 19 11 1 | 11111111 | quality_fail (gate_ok) |

### Branch HIST W10 (последний rep)

| Mod | Train | L | fires | fail |
|---|---|---|---|---|
| br25_nextseg / br50_preinh / br100_preinh | converged_posttune_finalized | 7 6 4 1 / 15 12 6 1 / 21 18 11 1 | 10000000 | ok |
| br25_gen / br25_preinh | converged_posttune_finalized | 7 6 4 1 / 16 13 3 1 | silent | quality_fail |

S0=S1=S2 совпадают по строкам — **E2 эквивалентность** на W10 держится.

## F* на `.11` (закрыто ранее)

F2/F3/F6mid/F4/F6-floor: cold Need=0 на W01 Classic×N1; F4/F6-floor TipR≠все@Rmin; silent-Test DEBT. F5 ещё OPEN.

## Дальше по плану

G1 gate по E2-результатам; F5; silent-Test; Controller/SYNTHESIS. Перед любым новым cold на `.17` — снова освободить корень &gt;80 ГБ (offload lanes/`_repro`).
