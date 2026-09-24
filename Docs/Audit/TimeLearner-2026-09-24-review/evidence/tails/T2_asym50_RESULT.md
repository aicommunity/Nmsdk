# PostTune verify result

Generated: 2026-09-24T18:39:45Z
Console: `/home/user/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole`

| case | train | Need | TipR class | TipR | FixedLTZ | gold thr | fires | mid_source | tipr_vs_snapshot | search_reverted | metrics |
|------|-------|------|------------|------|----------|----------|-------|------------|------------------|-----------------|---------|
| asym50 | exited | 1 | canon | `20000000 20000000 20000000 86000000` | 0.0100962 | 0.011759 | `10000000` | cpp | — | 0 | ok=1 n=8 acc=8 target_hit=1 fire_all=0 mode=selective fires=10000000 matches=111 |

**FAIL**: `asym50` — train_incomplete:exited.

**FAIL**: `asym50` — Need=1.
