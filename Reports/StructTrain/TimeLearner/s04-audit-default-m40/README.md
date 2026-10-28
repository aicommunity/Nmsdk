# Explicit learner audit flag Default

Native M40 ASan baseline on root bde7032a2af0fe2c670453809f0baa50d25f7cd6, PulseLib 025d809f7b86cc79e18ddd711c6adc40e2396bf8 reproduces one explicit Default failure in each learner. Ordinary Build/Reset preserve enabled audit, and stock Return/Take already restores false via class image. This is not a reproduced stock reuse failure.

PulseLib 4919bac2bd359118b13310862e54bcd24492967d explicitly sets EnableTrainingAudit=false in both ADefault methods. Root 7fb92a4a57b9773ff56996cf2c7b8c75b2746cd8 passes all eight native lifecycle cases and eighteen UContainer regressions normally on each worker, and under ASan on M40 with detect_leaks=0. Physics, tolerances and the common Rdk contract are unchanged.

A2 addressed results are valid, but the subsequent full CTest command never started: JS dollar-quote replacement damaged a shell filter. The original command also misspelled an otherwise unused CMake parallel hint; actual builds explicitly used -j2 normally and -j1 under ASan. Full A3 uses the same verified immutable binary/runtime in a new output directory and is a separate pending gate. Preparation failure is not a failed scientific experiment or a completed full suite.

All source closures, logs/XML and checksums are retained through Git. No executable or credentials are stored here.
