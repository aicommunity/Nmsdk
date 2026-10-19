# Сводка cold PostTune-fix (2026-10-19)

PulseLib финал: `d52dc1c`. Dual-host `.11`≤8 / `.17`≤12. Канон группировки: [RESULT_GROUPING…](RESULT_GROUPING_HIERARCHY.ru.md).

## Политика PostTune (итог кода)

1. Ideal LandscapeOk → mid из `ComputeMidThreshold`.
2. Best-effort mid **только** при tiny-gap (все foils ниже tgt, gap&lt;1e‑4).
3. Иначе silent mid (FixedLTZ=1) для Test inference; **TipR не откатывается** автоматически (PASS×3). KeepDone TipR — явный tip-mode / PostTune OFF (A2.1) для D3 gen.

Промежуточные SHA `8575df3`/`7c814a3`/`bd11169` показали: auto KeepDone TipR чинит D3-стиль gen, но ломает PASS preinh; BestEffort при foil≥tgt даёт all-fire.

## Trainer=Branch · Mode=N1 · NeuronModel=baseline

### Span=25 · Mod gen/preinh (волна1, PL `8575df3` затем финал)

| Mod | PostTune OFF | PostTune ON (финал путь) |
|---|---|---|
| gen | fires=`10110000` detected (OFF batch) | ON early SHA: BestEffort all-fire; D3 lever = KeepDone tip-mode / OFF |
| preinh | — | N+1 silence; PASS regress на финале зелёный для peers @50/100 |

### Span=25/50/100 · PASS×3 (PL `d52dc1c`, `.17` `tl-ptfix-passx3-v4-…`)

| Mod | fires | gate |
|---|---|---|
| nextseg@25 | `10000000` | True |
| preinh@50 | `10000000` | True |
| preinh@100 | `10000000` | True |

**PASS×3 ON: 3/3 green.**

## NeuronModel=FastSpan Classic (W12) / Branch (W48)

W12 fs25/50: train_incomplete на бюджете (зафиксировано).  
W48 `BR_FS25_N1_gen` fires=`11111111` detected; `preinh` silence — smoke Need/fires есть, PASS не требовался.

## Classic W01

CL25 N0/N1 incomplete; CL50 N0 fires=`01000101` quality_fail — в сводной иерархии Classic×N0.

## Инфра

Назначения: [DUALHOST_ASSIGNMENT…](DUALHOST_ASSIGNMENT_POSTTUNE_FIX_2026-10-19.ru.md). Монитор `AGENT_LOOP_TICK_ptfix` остановлен после closeout.
