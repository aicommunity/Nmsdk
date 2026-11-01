# P0 unpatched SoftCold baseline (Console SHA 4917a2bc…)

PulseLib still has classic `kAmpNormEps` as `int` (pre Phase 1).

## SHA-matched existing wave-C / SoftCold (reuse as unpatched ref)

| case | run_id | class | notes |
|------|--------|-------|-------|
| asym50_preinh | asym50_preinh_20260925T212603Z | train_incomplete | train=exited gate_rc=0 |
| asym25_preinh | asym25_preinh_20260925T211629Z | gate_fail | done_flag_flush gate_rc=1 |
| asym100_gen | asym100_gen_20260926T002121Z | gate_fail | exited_gate_FAIL tipr=flat |
| asym100_preinh | asym100_preinh_20260926T034443Z | unknown | **no provenance.json** — re-run in P0 |
| br25_on soft-cold | br25_on_20260924T170503Z | quality/gate | Console **5e7829bf** (older) — re-run on 4917a2bc |

## Fresh P0 runs (this session)

See `P0_fresh_runs.json` / `_repro/runs/` after completion.

## Fresh P0 asym100_preinh (this session) — aborted

- work: `asym100_preinh_20260926T094337Z_work`
- Console at start: **4917a2bc** (unpatched int eps)
- After ~80 min wall: Need still **1**, no `posttune_complete.flag`, empty train log — consistent with amp-norm stall (TL-01)
- Process killed to free CPU for patched Phase 2 A/B
