# W01 gate verdict (2026-10-11)

- Host: 10.245.1.17
- RUN_ID: run-17-20261011T103939Z-445814
- Console sha256: 51da1f19a4414ba56547ece66faef1cbc336c7f1014bf972d8a559c82078f306
- training_stop_cases: 6 (all CL25 + CL50 N1)
- evaluation_error_cases: 2 (CL50 N0 PSIoff/PSI25 — converged_need0, gate `fires_missing` / `gate_rc=1`)
- quality_failure_cases: 0
- Decision: **PAUSE** dual-host parallel split per protocol (systematic non-convergence on short/N1 cells). Do not start W02/W04 until diagnosis.
- Diagnosis: [W01_DIAGNOSIS_20261011.md](W01_DIAGNOSIS_20261011.md) — N1 path broken (peak/TipR blow-up, no synapse growth); CL25 N0 amp/sync stall within `train_t=160`; CL50 N0 reaches Need=0 but gate fails (LTZ→1 / fires_missing).
