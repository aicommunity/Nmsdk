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
