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

## Retest

`posttune_verify --case phase6_{thr_only,preinh250,ltzcal_twin}` (train_t=900) + монитор 10 м.  
Extended `-t` не открывать, пока L не в окрестности gold.

## После retest

(заполнить: Need, TipR, L live, gate_rc)
