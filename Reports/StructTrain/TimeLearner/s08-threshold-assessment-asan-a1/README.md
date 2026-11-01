# Baseline threshold assessment: full scoped ASan gate

The long-running independent baseline completed 16 native tests and 35 reader tests (548.849 seconds), with zero skips/errors/failures and terminal 0. Native source is root ad975bbeb5df18555d94329d3ee95f321921c171 / PulseLib 25cf6a5bfadc0ee72182cb924f1d0730cf6dc71b; reader is 1ef44e2e6c5ce40339f9aeaa5e4426810e36844b. It covers N1 potential observation at 2000/20000 Hz, Classic/Branch N0/N1 threshold candidates at both frequencies, fresh destinations and recognition conversion controls. Four phase XML files and their exact combined sixteen-case set are retained.

All native and legacy companion primary JSON/CSV/models, source closure, runtime before/after, build logs and reader records are compressed losslessly. The runtime remained unchanged while the gate ran. AddressSanitizer was used with leak detection disabled; this is not leak-check acceptance. Scientific verdict is null.

This older baseline does not substitute full-matrix verification of later signed-threshold, calibrated model, grid driver, ownership fixes or production workers. Their distinct source versions and primary bundles remain separate. The full original refactoring plan is still active. All-pattern visual cache acceptance for this archived gate remains open; archived primaries permit reproduction.
