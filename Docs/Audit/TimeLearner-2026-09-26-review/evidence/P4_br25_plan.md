# Phase 4 — Branch br25 SoftCold diagnostics

**Status:** in progress / evidence-first (no morphogenesis code change)

## Existing evidence (do not re-run H1–H4 unless incomplete)

| Run | Bundle / note |
|-----|----------------|
| B0 SkipTrainGold PASS | `br25_on_20260924T165949Z` (frozen weights) |
| B1 soft-cold Canon FAIL NonSeparable | `br25_on_20260924T170503Z` (Console 5e7829bf) |
| H1 Keep FAIL | docs tails T3_H1 |
| H3 soft≡strip | T3_H3 |
| H4 AutoScale 0≡1 | T3_H4 |

## Interpretation tree (open)

1. Peak present? → check Dataset/Generator/LTZ
2. Anchor after reset? → `cold_reset_contract.json` expects Branch L=`1 1 1 0`
3. dt vs length apply → `ChangeDendriteStatus` L3513 / `ApplyPending` L3112 / `FinishTrainingIteration` L5162
4. Growth without separability → `LandscapeOk` (do not weaken)
5. Need=0 + NonSeparable → quality FAIL (not PASS)

## Fresh B1 on patched Console

See `P4_br25_B1.md` after `posttune_verify --case br25_on` completes on Console `ec86430e…`.
