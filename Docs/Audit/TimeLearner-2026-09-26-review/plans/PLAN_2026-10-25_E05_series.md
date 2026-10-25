# E05 series (E0–E5): dendrite length limits at dt = 0.5 ms

Branch `plan/2026-10-25-dendrite-limits`. Parent plan: `PLAN_2026-10-25_dendrite_limits.md`.
Integration step is fixed: DefaultTimeStep = 2000 (dt = 0.5 ms) in Train and Test (the templates ship 20000; e05_job patches both Project.ini).
No new model classes; per-config overrides only (PulseLib 29c7ead: Override{MembraneCapacity,Exc/InhMembraneResistance,Exc/InhSynapseResistance}; DynamicsLog{Head,Every,ComponentState}).

## E0 — Console vs segsim kernel (done 2026-10-25)
Subthreshold probe (TipR0 2e9 signal minus 1e15 reference, inhibition off), one dendrite of length L, dt = 0.5 ms.
Result `evidence/E05/E0/E0_console_vs_segsim_dt2000.tsv`: t_peak and FWHM coincide with segsim for all C in {7.5e-11, 1e-10, 2.5e-10} and L in {50, 200, 400};
delay per segment = tau - dt (0.25 / 0.5 / 2.0 ms). Amplitude ratio Console/segsim = 0.72–0.80 (L 50) and 0.36–0.40 (L 200–400): L-dependent input-side scale, compensated by TipR learning.
Decision: delay parameters are used as planned (no retuning); the amplitude factor is an open item.

## Points (Classic and Branch, preinh, N1, pton; 3 seeds = TipR jitter 0 / +0.013 / -0.011 on the last tip)
| id | span | C | inhibition Rm / Rs | MaxDL | EstDelayPerSeg | expected L | expected |
|---|---|---|---|---|---|---|---|
| E1 | S100 | 2.5e-10 (class) | 1e8 / 8.6e8 (class) | 100 | class (0.002) | 51/43/26/1 | FAIL, m(S/4) 0.01–0.02 |
| E2 | S100 | 7.5e-11 | 1e7 / 8.6e7 | 450 | 0.00025 | 400/334/200/1 | Classic 0.13, Branch 0.11 |
| E3off | S100 | 7.5e-11 | off (InhRs 1e15) | 450 | 0.00025 | 400/334/200/1 | ~0.09 / 0.078, FAIL |
| E3weak | S100 | 7.5e-11 | 1e8 / 8.6e8 | 450 | 0.00025 | 400/334/200/1 | ~0.09 / 0.078, FAIL |
| E4 | S100 | 1e-10 | 1e7 / 8.6e7 | 250 | 0.0005 | 200/168/101/1 | Classic 0.098, Branch 0.084 |
| E4off | S100 | 1e-10 | off | 250 | 0.0005 | 200/168/101/1 | control |
| E5 | S50 | 7.5e-11 | 1e7 / 8.6e7 | 500 | 0.00025 | 200/166/100/1 | FAIL 0.06–0.08 |
| E5off | S50 | 7.5e-11 | off | 500 | 0.00025 | 200/166/100/1 | control |

Soft cold reset starts every run at L = 1 1 1 1 with flat TipR 8.6e7; the L column is the expected learned length, not the start.
E5 discrepancy: the review gives MaxDL 250, the task gives ~500. 250 does not fit L = 200 plus overshoot at 0.25 ms/seg for S50, so 500 is used; E5 at 250 can be appended to the queue.
Branch: EstDelayPerSeg is an internal adaptive estimate (init 0.005 s/seg, EMA). With tau 0.75 ms the 20x wrong start deadlocks the d2 peak window (smoke E2_b: L = 1/1/9/1 for 300 iterations, peak_valid d2 = 0). PulseLib adds `InitEstDelayPerSeg` (<= 0 keeps 0.005); e05_job sets it to the point's EstDelayPerSeg for Branch. Branch jobs started before that use the old binary and are diagnostic only.

## Per-run controls
- Test with target first (MatrixClasses gate), plus qA/qB: targets at positions 1/7 and 2/7 -> m(S/4), m(S/8), target detection.
- iti6: order permutation [3, target, rest], Delay 6.0 s final test -> m8_iti6.
- Template ITI: Delay/IterationGap 1.5 s (>= 300 ms S100, >= 200 ms S50).
- Readback: Train/Test XML (class, overrides, MaxDL, L, EstDelayPerSeg/InitEstDelayPerSeg, DefaultTimeStep) after template patch, after soft reset (POST_RESET) and NeuronClassOverrides in the EventsLog (BuildStructure and PostTune rebuild).
- Step: `now=` increments of 5e-4 in TrainingDynamics (dyn_now_min_step).
- Metrics reported: sep_margin, m(S/4), m(S/8), m8, target detection, Done_exact / Done_BE, final L. Saturation is not convergence; Acc is not used.

## Execution
Per-host dispatcher `evidence/tools/e05_dispatch.sh ROOT` (setsid/nohup, own session): queue `ROOT/queue.tsv` (`label<TAB>json`, append any time), `dispatch.log`, `launch.tsv`, `STOP` file.
Slots = nproc; other campaigns' Consoles are counted, and while a REPASS_ITI6 process is alive its slots are reserved (6 on .11, 10 on .17). Starts only with MemAvailable >= 4 GB, no swap activity, system disk < 90 %, Data free >= 5 %; DISK_LOW is only signalled.
Roots: .11 `~/e05_runs/series`, .17 `$DATA/runs/E05_series`. Queues: `evidence/E05/queues/`.
