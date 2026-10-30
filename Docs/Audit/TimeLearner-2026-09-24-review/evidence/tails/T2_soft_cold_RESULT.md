# PostTune verify result

Generated: 2026-09-24T17:11:41Z
Console: `/home/user/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole`

| case | train | Need | TipR class | TipR | FixedLTZ | gold thr | fires | mid_source | tipr_vs_snapshot | search_reverted | metrics |
|------|-------|------|------------|------|----------|----------|-------|------------|------------------|-----------------|---------|
| br25_on | done_gate_FAIL_gate_rc=1 | 1 | flat | `86000000 86000000 86000000 86000000` | 1 | 0.07179975 | `` | missing | — | 0 | gate_rc=1 |

**FAIL**: `br25_on` — train_incomplete:done_gate_FAIL_gate_rc=1.

**FAIL**: `br25_on` — fires_missing.

**FAIL**: `br25_on` — gate_fail.

**FAIL**: `br25_on` — tipr_class=flat expect=canon.

**FAIL**: `br25_on` — gate_rc=1.
