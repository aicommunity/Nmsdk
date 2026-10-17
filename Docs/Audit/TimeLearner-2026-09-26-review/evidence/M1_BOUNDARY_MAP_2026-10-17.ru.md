# M1 карта границ от seed br25_nextseg

Дата кампании: 2026-10-17. Seed host: `.17`. Root `d8302bc3`, PulseLib `2820738`, Bin `9f824fa6+`, Console SHA-256 `69e608a4…`.

## M1-B0 anchor — `tl-m1-b0-br25-nextseg-17-20261017-02`

| Case | Need | fires | Acc/FP | Вердикт |
|---|---|---|---|---|
| `W10_HIST_br25_nextseg` | 0 posttune | `10000000` | 8/8 / 0 | **PASS** |

Длины `[9,8,5,1]`, TipR `[20,20,20,86]` МОм.

## M1-B1 W10 соседи — `tl-m1-b1-w10-adj-17-20261017-01`

| Case | convergence | fires | Acc/FP | Вердикт |
|---|---|---|---|---|
| `W10_HIST_br25_preinh` | posttune Need0 | `10000000` | 8/8 / 0 | **PASS** |
| `W10_HIST_br50_gen` | posttune Need0 | `00000000` | 7/8 / 0 | silence |
| `W10_HIST_br50_nextseg` | incomplete | — | — | Incomplete |
| `W10_HIST_br100_nextseg` | incomplete | — | — | Incomplete |

Ось: **25 мс** удерживает PASS (NextSeg и preinh); **≥50 мс NextSeg** — Incomplete; gen@50 — сходимость без цели.

## M1-B2 W32/W34

| Case | convergence | fires | Acc/FP | Вердикт |
|---|---|---|---|---|
| `W32_BR25_N1_MARGIN_HALF` | incomplete | — | — | исторический PASS не воспроизведён |
| `W32_BR25_N1_MARGIN_CURRENT` | Need0 | `11111111` | 1/8 / 7 | all-fire |
| `W34_BR50_N1_PSIoff_POST` | posttune Need0 | `00000000` | 7/8 / 0 | silence (был PASS) |
| `W34_BR50_N1_PSI25_POST` | posttune Need0 | `00000000` | 7/8 / 0 | silence |

## M1-B3 W03 short parametric — `tl-m1-b3-w03-17-20261017-01`

| Case | convergence | fires | Acc/FP | Вердикт |
|---|---|---|---|---|
| `W03_BR25_N1_PSIoff` | Need0 | `11111111` | 1/8 / 7 | all-fire |
| `W03_BR25_N1_PSI25` | Need0 | `00000000` | 7/8 / 0 | silence |
| `W03_BR50_N1_PSIoff` | Need0 | `11111111` | 1/8 / 7 | all-fire |
| `W03_BR50_N1_PSI25` | Need0 | `00000000` | 7/8 / 0 | silence |

PSI off → all-fire; PSI 25 → silence (как на предыдущем снимке).

## M1-B4 N0 boundary

| Case | convergence | lengths | Вердикт |
|---|---|---|---|
| `W32_BR25_N0_MARGIN_HALF` | incomplete | `[1,1,4,1]` | Mode0 граница Incomplete |
| `W34_BR50_N0_PSIoff_POST` | incomplete | `[1,1,6,1]` | Mode0 граница Incomplete |

## Сводка острова PASS

На текущем Release устойчивы **только** Branch N1 @ **25 мс** с историческими конфигами `br25_nextseg` и `br25_preinh` (8/8 FP=0). Соседние dt/margin/PostTrain/W03 дают Incomplete, silence или all-fire. C++-фикс по M1 в этом цикле не требовался (нарушения контракта тренера не доказаны трассой).
