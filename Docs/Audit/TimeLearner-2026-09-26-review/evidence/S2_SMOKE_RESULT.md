# SoftCold smoke S2 — 2026-09-27

Console `ec86430e…`. Fix: `softcold_fix=2026-09-27_sbm2_strip_tip1`.

## S2.1 Unit

`python3 …/tests/test_softcold_fix_unit.py` — **OK** (SBM all→2, tip-1, contract).

## S2.2 asym50_preinh

| | |
|--|--|
| Pass | **yes** (growth ~30 s wall) |
| L | `9 1 1 1` |
| TipR[0] | ≈5.76e7 (left flat 8.6e7) |
| SBM | `["2","2"]`, max_seg=1 |
| Report | [S2_smoke_asym50.json](S2_smoke_asym50.json) · work `…/asym50_preinh_smoke_20260927T071048Z_work` |

Previously: TipR flat + L=1 for entire ~3.3 h poll budget (`timing_softcold_desync`).

## S2.3 asym25_preinh

| | |
|--|--|
| Pass | **yes** (growth ~30 s wall; control not regress) |
| L | `9 1 1 1` |
| TipR[0] | ≈5.76e7 |
| Report | [S2_smoke_asym25_preinh.json](S2_smoke_asym25_preinh.json) |

## Verdict

S2 **PASS** → proceed S3 full SoftCold retest (`run_S3_retest_after_softcold_fix.sh`).
