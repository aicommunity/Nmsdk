# Physical domain evidence: aligned 2000/20000 Hz before/after control

Root 37c57e1a3573328a670ebf260652a5db42b0ce7c, PulseLib 34a00239cf9a368961daef9c0cca7106c3cb9b3c. Immutable normal A1 runtime reused after its completed run. The exact twenty-case filter/order of the original normal controller matrix is restored: fourteen arithmetic cases, four searches at 2000/20000 Hz, two Branch bank controls. All twenty pass.

All 68 original primary trial CSV and probe JSON files are byte-identical to the earlier e875ca5 controller matrix (baseline evidence 1969585a72d3d09d6e6583f443d980e717575046). Independent measurement audit validates all 68 trials; independent physical audit recomputes all fifteen schema-2 domain records. Thus the new serialization has not changed these measured dynamics or controller results.

The first A1 before/after comparison used a different selected test set: twenty Branch geometry records therefore had different environment absolute times and attempt IDs; 24 preceding search records were byte-exact. This aligned A2 control resolves that comparison. It does not silently rewrite either original attempt and is not a scientific order/ITI robustness experiment.

The six direct preview/inhibition records and fifteen corruption controls are in the separate A1 package. No convergence, scientific selectivity, all-stage completion or support for untested physics is inferred here.
