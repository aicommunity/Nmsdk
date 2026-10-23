# Campaign status 2026-10-23T03:58Z

- **G1 S1 RERUN** dual-host — **closed** (PARTIAL exit policy; 3/13 exit-clean). G1 waves **not** restarted.
- **F5 paired γ (Span50)** — **done** on `.11`: `F5.paired-base-…30140` (γ=0) + `F5.paired-gamma-…10276` (γ=1), case `W01_CL50_N1_PSIoff`. Evidence: [`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md).
- **F5 Span100 γ A/B** — **done** (`SERIES_DONE` EXIT=0): `F5.S100.0-…27970` (γ=0) + `F5.S100.1-…3403` (γ=1), case `W02_CL100_N1_PSIoff`, PostTune OFF. γ=0≡γ=1 (`converged_need0`, L=`54 48 30 1`, TipR midband, silent `quality_fail`). Tip Console **без** символа F5 → кодpath A7 не активен. Evidence: [`F5_GAMMA_SPAN100_2026-10-22.ru.md`](F5_GAMMA_SPAN100_2026-10-22.ru.md). Commit `b00527a44`. **DEBT-F5-gamma OPEN** — next = rebuild Console с F5 на tip, затем повтор Span100 A/B.
- **CL-N1:** H1 Span100 executed (stall 480-specific); H2 `LEN_SEARCH` exit-classes **normative in SPEC DRAFT** (без cold). [`CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md`](CL_N1_NEXT_HYPOTHESIS_2026-10-22.ru.md); [`CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md`](CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md).
- **Controller v2:** SPEC DRAFT published (`CONTROLLER_V2_SPEC_DRAFT_2026-10-23`); **`DEBT-CTRL-V2-DRAFT` open** until FINAL (mid production, numeric tol, F1b, CL-N1@480).
- **E0** `--train-param` whitelist на Bin tip `bf3e82ff` / root bump `1792ece42` (pushed).
- Console idle: `.11` NeuroModelerConsole = **0**; free≈122 G. Host limit 8.
- Tip: root **`aa6a1e6d8`**, Bin **`e49a52bf`**, Console sha256 **`f88d1852…`**, PulseLib **`3a599a7`**.
- Still open (no auto-cold): F1b senior; CTRL FINAL SPEC; tl-baseline tag; CL-N1@480; F5 rebuild.
