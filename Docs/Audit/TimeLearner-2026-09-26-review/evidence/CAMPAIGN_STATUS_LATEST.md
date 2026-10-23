# Campaign status 2026-10-23T06:40Z

- **G1 S1 RERUN** dual-host — **closed** (PARTIAL exit policy; 3/13 exit-clean). G1 waves **not** restarted.
- **F5 paired γ (Span50)** — **done** on `.11`: `F5.paired-base-…30140` (γ=0) + `F5.paired-gamma-…10276` (γ=1), case `W01_CL50_N1_PSIoff`. Evidence: [`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md).
- **F5 Span100 tip-noop A/B** — **done** (`SERIES_DONE` EXIT=0): `F5.S100.0-…27970` / `F5.S100.1-…3403`, Console без символа F5. Evidence: [`F5_GAMMA_SPAN100_2026-10-22.ru.md`](F5_GAMMA_SPAN100_2026-10-22.ru.md).
- **F5 Span100 LIVE A/B** — **done** (`SERIES_DONE F5.S100L EXIT=0`): `F5.S100L.0-…21224` (γ=0) + `F5.S100L.1-…27819` (γ=1), case `W02_CL100_N1_PSIoff`, PostTune OFF, PulseLib **`9efca9c`**, Console **`213e7003…`** (символ F5 **present**). **γ=0≡γ=1** (`converged_need0`, L=`54 48 30 1`, TipR midband, silent `quality_fail`) — A7 **noop** на midband. Evidence: [`F5_GAMMA_SPAN100_LIVE_2026-10-23.ru.md`](F5_GAMMA_SPAN100_LIVE_2026-10-23.ru.md). **DEBT-F5-gamma OPEN** (no PASS / γ noop; **не** «symbol missing»). **No more F5 cold** without new hypothesis.
- **CL-N1:** H1 Span100 executed (stall 480-specific); H2 `LEN_SEARCH` exit-classes **normative in SPEC DRAFT** (без cold). [`CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md`](CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md); [`CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md`](CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md).
- **Controller v2:** SPEC DRAFT **enriched** — still **DRAFT not FINAL**; **`DEBT-CTRL-V2-DRAFT` open**. No Console cold from this arm.
- **E0** `--train-param` whitelist на Bin tip / root bump.
- Tip: root **`695b00405`** (+ upcoming gitlink bump), Bin **`e49a52bf`**, Console sha256 **`213e70034effa8d7…`**, PulseLib **`9efca9c`**.
- **tl-baseline-20261020** — **cut** → root `03c8cb9` / PulseLib `d52dc1c` / Bin `e7509263` (docs `e84797855`).
- Still open (no auto-cold): F1b senior; CTRL FINAL SPEC; CL-N1@480; F5 A7 algorithm (γ noop documented); silent-Test `DEBT-D2`.
