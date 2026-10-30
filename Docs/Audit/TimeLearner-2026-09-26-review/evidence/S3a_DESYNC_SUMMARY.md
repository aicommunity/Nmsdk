# S3.a summary — softcold_desync cases after fix

Дата: 2026-09-27. Fix: `2026-09-27_sbm2_strip_tip1`.

| case | rc | live TipR | live L | Need XML | desync lifted |
|------|----|-----------|--------|----------|---------------|
| asym50_preinh | 1 | canon | ≈`29 22 15 1` | 1 / flat XML | **yes** |
| asym100_preinh | 1 | canon | ≈`52 43 30 1` | 1 / flat XML | **yes** |
| asym100_gen | 1 | canon | ≈`52 43 30 1` | 1 / flat XML | **yes** |

Все: `failure_class=train_incomplete` (poll401, no EOL/Save).  
Следующее: S3.b (asym25/br25/fs25/phase6) + разбор EOL / extended `-t`.
