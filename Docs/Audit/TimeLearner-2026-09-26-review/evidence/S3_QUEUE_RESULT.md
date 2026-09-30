# SoftCold S3.a+S3.b — итог очереди (2026-09-27)

Fix: `softcold_fix=2026-09-27_sbm2_strip_tip1`.  
Скрипт: `metrics/run_S3_retest_after_softcold_fix.sh` → **DONE** 2026-09-27T23:57:16Z.  
RC: [SOFTCOLD_DEFER_rcs_after_softcold_fix.txt](SOFTCOLD_DEFER_rcs_after_softcold_fix.txt)

| case | rc | failure_class | tipr (XML/report) | note |
|------|----|---------------|-------------------|------|
| asym50_preinh | 1 | train_incomplete | flat* | desync lifted (live TipR→canon) |
| asym100_preinh | 1 | train_incomplete | flat* | same |
| asym100_gen | 1 | train_incomplete | flat* | same |
| asym25_preinh | 1 | gate_fail | **canon** | Train Done; NonSeparable mid |
| br25_on | 1 | gate_fail | **canon** | Train Done; NonSeparable |
| fs25_gen | 1 | train_incomplete | other | |
| phase6_thr_only | 1 | train_incomplete | other | |
| phase6_preinh250 | 1 | train_incomplete | other | |
| phase6_ltzcal_twin | 1 | train_incomplete | other | |

\* XML flat из‑за no Save; live traces/tipr_live показывали рост — см. [S3a_DESYNC_SUMMARY.md](S3a_DESYNC_SUMMARY.md).

**Вывод:** SoftCold topology/SBM-фикс снимает `timing_softcold_desync`. Cold PASS не получен; дальше — EOL/extended `-t` (S3.d) и при необходимости полная DEFER (S3.c).
