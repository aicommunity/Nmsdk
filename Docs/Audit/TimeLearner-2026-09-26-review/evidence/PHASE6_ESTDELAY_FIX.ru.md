# Phase6 EstDelayPerSeg SoftCold fix

Дата: 2026-10-01.  
Связано: [TIMING_SPAN_MISMATCH.ru.md](TIMING_SPAN_MISMATCH.ru.md).

## Проблема

Archive Phase6 SoftCold-source **без** тега `EstDelayPerSeg` → runtime default `kDelayPerSegDefault=0.005`.  
При SoftCold L=1 и span 480 мс равновесие `1 + 0.480/0.005 ≈ 97` — факт SoftCold (`97 81 49 1`), не gold `49/51`.

## Правка XML (one-factor)

| case | archive Train Parameters | EstDelayPerSeg | расчёт |
|------|--------------------------|----------------|--------|
| phase6_thr_only | `EXP_480_gen_thr_only` | **0.01** | `0.480/(49−1)` |
| phase6_ltzcal_twin | `EXP_480_ltzcal_twin_gen` | **0.01** | то же |
| phase6_preinh250 | `EXP_480_preinh250_tiprmin` | **0.0096** | `0.480/(51−1)` |

Ожидание SoftCold: L≈gold (±tol), не runaway ~97.

## Retest (2026-10-01)

Console `b66711b5…` · log `metrics/SOFTCOLD_w3_phase6_retest.log`.

| case | L live | TipR live (хвост) | Need | gate | rc | bundle |
|------|--------|-------------------|------|------|----|--------|
| phase6_thr_only | **`49 41 25 1`** (≠97) | dend0/1 ceiling `1e11`, dend2≈2.3e7 | 1 | 1 | **1** | `…T110339Z` |
| phase6_preinh250 | **`53 45 28 1`** (≠97) | `1e11×3` | 1 | 1 | **1** | `…T121029Z` |
| phase6_ltzcal_twin | **`49 41 25 1`** (≠97) | dend0/1 `1e11`, dend2≈2.2e7 | 1 | 1 | **1** | `…T132330Z` |

**Итог EstDelay:** runaway L≈97 **снят**, L в окрестности gold.  
**Cold PASS:** нет (Need=1, TipR non-canon/ceiling, gate_rc=1). Extended `-t` не открывать ради L.
