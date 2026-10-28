# Diagnostic stopped TimeLearner states: M40 ASan

A1 (root 659ec066db6ac279ae97d118e778bb5b827bf6a4, PulseLib c943a32) passed 2/16 native cases and failed 14: the newly added incomplete-capture guard resurrected an old plan after explicit target invalidation and storage reuse. This is a regression introduced in this implementation branch, not evidence against historical August learning. Primary trace completeness was not claimed for A1.

A2 (root f199c40c000c6118f61267439f8fe92dbf33c313, PulseLib 652c8f3) passes all 16 native cases under ASan, detect_leaks=0. Both topologies cover early/partial external stop, model-time/search budget, an edited model, incomplete final sweep, rejected probe and model change during incomplete capture. Imported physical graphs and frozen samples match; every parent verifies a fresh-process import and byte-identical frozen CSV. Warm restart retains complete goals or enforces the original model for incomplete capture.

Ten Python mutation/audit tests pass against 54 actual primary JSON/CSV trials, including six invalid/censored attempts. The independent audit does not claim convergence or scientific selectivity. Python was run explicitly from an immutable root f199c40 worktree after native termination: the original combined shell command exited after the native phase and did not launch Python.

A later 20-case integrity/N0/configured-V2 extension is a separate pending attempt, not included in this acceptance. Full maintained suites, cross-host stopped replay, calibrated/recognition/PostTune transfer, production runner and the scientific matrix remain open. All source closures and raw/stored SHA256 records are retained. No binaries or credentials are published.
