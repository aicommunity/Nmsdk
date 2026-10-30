# SoftCold W2 — asym* после AmpNorm(b)

Дата: 2026-10-01.  
Console `b66711b5…` · PulseLib `bb438c4` (`kRminLengthTolFactor=2`).  
Log: `metrics/SOFTCOLD_w2_asym_retest.log`.

| case | TipR live | L live | Need@flag | gate | rc | bundle |
|------|-----------|--------|-----------|------|----|--------|
| asym50_preinh | `2e7×3 8.6e7` | `27 22 15 1` | 1 | 1 | **1** | `…T095822Z` |
| asym100_preinh | `2e7×3 8.6e7` | `49 41 31 1` | 1 | 1 | **1** | `…T101311Z` |
| asym100_gen | `2e7×3 8.6e7` | `54 43 27 1` | 1→report 0 | 1 | **1** | `…T103720Z` |

**Итог:** TipR@Rmin достигается (L gold-like); **Cold PASS нет**. Slack `2×SyncTol` недостаточен для Need→0 на preinh (flag_flush Need=1). Keep-slog root cause: [AMPNORM_asym50_KEEPSLOG.ru.md](AMPNORM_asym50_KEEPSLOG.ru.md).
