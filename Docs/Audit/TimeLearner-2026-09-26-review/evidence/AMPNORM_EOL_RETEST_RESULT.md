# AmpNorm / EOL — selective retest + W3 D smoke

Console SHA16: `ae9ec66806aa854c` (W3 Rmax-escape rebuild).  
PulseLib: `9b63613`. SoftCold full matrix W4 started 2026-10-04T13:47:49Z.

## Keep PASS
| case | rc |
|------|----|
| asym50 | 0 |
| ltz50_gen | 0 |
| br50_gen | 0 |

## W1 E
| case | rc | note |
|------|----|------|
| asym100_preinh | **0** | PASS |
| fs50_preinh | 1 | TipR@Rmin + flag; gate rc=1 |
| ltz25_gen | 1 | gate |
| asym100_gen | 1 | gate |
| ltz100_gen | 1 | gate |

## W2 B
| case | rc | note |
|------|----|------|
| fs25_gen | **0** | PASS |
| fs25_preinh | **0** | PASS |
| br25_preinh | 1 | Branch ActivePulse/length |
| br480_nextseg | 1 | Branch |
| br480_tiprmin | 1 | L=1,61,89 tipr_settled=0 |

## N
| br25_on | 1 | expected NonSeparable / gate |

## W3 D smoke (Rmax dwell escape active — TipR leaves 1e11 briefly)
| case | rc | note |
|------|----|------|
| phase6_480 | 1 | TipR oscillates 1e11↔8.5e10; amp_dt≈−0.06 |
| tn_classic | 1 | same ceiling pattern |
| pa00_baseline | 1 | same |
| ltz25_preinh | 1 | runaway/D |

## Code landed
- W1: EOL @Rmin predicates; overshoot@Rmin raise; length_settled@Rmin×4
- W2 base: midband NoImprove→Rmin floor; Branch: no midband_walk, near/far NoImprove
- W3: RmaxDwell escape (any dt); length_settled slack at Rmax

## Artifacts
- Selective RCS: `Bin/.../_repro/AMPNORM_EOL_retest_rcs.txt`
- W0 SNAP: `AMPNORM_EOL_W0_SNAP.md`
- Full matrix W4 log: `metrics/SOFTCOLD_full_matrix_w4.log`

## SoftCold W4 aborted (2026-10-05)

Aborted at **22/49** (5 PASS / 17 FAIL), current Train was `psi35_400` (23/49).  
Reason: stop for EstDelay/W3/parallel rematrix plan.  
Partial RCS: `_repro/SOFTCOLD_HEAD_rcs_w4_partial_20261005.txt`.  
Pre-fix Console SHA: `ae9ec66806aa854c` · PulseLib: `9b63613`.

## Rematrix smoke (Console `8589daff…`)

| case | rc | note |
|------|----|------|
| asym50 | **0** | keep PASS |
| ltz50_gen | **0** | keep PASS |
| br50_gen | **0** | keep PASS |
| fs25_gen | **0** | keep PASS |
| pa00_baseline | 1 | **L=`49 41 25`** (EstDelay OK, ≠97); TipR@Rmax Need=1 |
| br25_off | **0** | SoftColdOff fires expect fixed |

W3: pa00 TipR stays at ceiling without 1e11↔8.5e10 oscillation under `amp_dt<0`.

## SoftCold rematrix PARALLEL 49×6 (DONE 2026-10-05→06)

| | |
|--|--|
| Console SHA16 | `8589daff6d131c9b` |
| PulseLib | `b32d715` (RmaxDwell only dt≥0) |
| Bin | `e2c6f79`+ (EstDelay/harness/parallel; flock-deadlock fix post-join) |
| Log | `metrics/SOFTCOLD_full_matrix_parallel.log` |
| RCS | `_repro/SOFTCOLD_HEAD_rcs.txt` (49/49 merged) |
| PASS / FAIL | **13 / 36** |

**PASS:** `asym50_preinh`, `asym25_preinh`, `asym50`, `br25_off`, `fs25_gen`, `br50_gen`, `br100_preinh`, `br25_nextseg`, `br50_preinh`, `fs100_preinh`, `fs25_preinh`, `asym100_preinh`, `ltz50_gen`.

Keep-PASS не регрессировали. EstDelay PhaseA: `pa00`/`pa01` live L=`49 41 25` (≠97). W3: нет 1e11↔8.5e10 step-down при dt&lt;0@Rmax (hold). Registry apply: один раз после join (снят nested flock deadlock).

Корзины FAIL: см. [SOFTCOLD_CONVERGENCE_AUDIT.ru.md](SOFTCOLD_CONVERGENCE_AUDIT.ru.md) (срез rematrix).
