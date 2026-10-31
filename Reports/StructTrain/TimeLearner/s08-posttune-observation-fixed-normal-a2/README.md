# TL-037 corrected native observation gate: normal A2

Root e3fe53408b861b49c0e0ddc6c3de9acc548a9e54 / PulseLib 39810a760103d2e5d5a5b9e6ae6575290522b20c: 12/12 actual cases pass, 220.780 seconds. Eight fault-injection regressions include stale Result, stale same-cardinality sample states, absent foil and NaN. Four real legacy-scheduler physical free-runs cover Classic/Branch at 2000/20000 Hz with all soma/input samples and two patterns each. Independent primary reader: 5/5, 4.165 seconds, without skips. Model settling or a V2 calibration certificate is not inferred. Source legacy result can remain BestEffort.

The cancelled A1 incorrectly built a NativeTrainingOwned physical fixture and bypassed legacy ACalculate; full 49-case A1 is not accepted. Its partial logs, precise owned-process cancellation receipt and diagnostics are retained. A2 uses actual legacy construction and asserts native ownership is absent. No production fix was relaxed to make the fixture pass.

All physical CSV, complete metadata, JUnit, class/profile readbacks, source closure and immutable runtime/build records are lossless. The additional 37 regressions and ASan acceptance are tracked separately; no stage is declared complete here. Full-scale figures are generated in M40 cache from these primaries; only selected figures and metadata belong in Git.
