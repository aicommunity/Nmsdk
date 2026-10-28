# Terminal ASan preview/API/editor regression

Root 9cb30c06515f29228716ed87f34d0e0f6b64cbc9, PulseLib 39179dac15cac5966fe0f2fadda0027c1a086ff3. The original A2 twelve-case ASan run has now terminated with twelve passes, no failures/errors; runtime 5089.73 seconds, detect_leaks=0. It includes eight real editor regressions at 2000/20000 Hz and four read-only/fixed-scaled inhibition preview controls. Its original immutable executable hash still matches the recorded runtime manifest.

The earlier scoped four-case A3 package explicitly reported this long run as pending. This supplement records its terminal outcome without rewriting that historical report. It does not test the later e875ca5 controller or schema-2 physical-decision serialization. No claim of leak freedom, completed refactoring stages, convergence or scientific selectivity is made.
