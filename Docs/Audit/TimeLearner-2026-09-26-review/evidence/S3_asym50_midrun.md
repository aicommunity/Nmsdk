# S3 mid-run note — asym50_preinh after softcold_fix

UTC start: 2026-09-27T07:14:37Z  
work: `_repro/runs/asym50_preinh_20260927T071438Z_work`

| wall | sim≈ | L (trace) | TipR (trace) | Need(XML) | flag |
|------|------|-----------|--------------|-----------|------|
| ~30 s | 3.7 s | `9 9 1 1` | left flat | 1 | 0 |
| ~6 min | 18 s | `27 22 15 1` | `2e7×3 8.6e7` canon | 1 | 0 |
| ~26 min | 62 s | `27 22 15 1` settled | canon settled | 1 | 0 |

**Снятие `timing_softcold_desync`:** подтверждено (рост + TipR→canon).  
Parameters XML still cold until NM `-S` / flag (ожидаемо).  
ETA full `-t 640` ≈4–5 h wall if Need не сбросится раньше.
