# Shared native training service implementation checks (elder1)

The service owns reference capture, bounded search with actual native edits, and independent fresh all-input final verification through the learner's ordinary Before/After scheduler hooks. No test loop manually performs the individual controller actions. Old configurations continue through legacy control until the explicit API is called.

A1: 41 passed, one failed out of 42 cases on each host. Four Classic/Branch x N0/N1 searches, warm/reset/external-stop/budget controls passed. A forged pattern hash was rejected, but the diagnostic incorrectly claimed a changed base revision before a revision was available. The original failure is retained.

A2: 65/65 pass on each host after preserving the original error cause and distinguishing unavailable/changed revision. Includes 11 service cases, 11 bounded-kernel cases, 17 final-verification cases, four native editor regressions, 20 prior lifecycle invalidation cases and two six-input controls. Search bounds/protocol are validated before reference probes.

A3: 31/31 pass on each host. Full original reference observations, raw goals and certificate binding survive Reset/warm restart and are cleared by retarget. This is not mid-probe checkpoint or complete trained-state serialization.

A4: 39/39 pass on each host. Full probe packets, CSV, actual final model identity and state summaries retain per-candidate parameters/epochs/trial IDs, all final residuals, raw per-input references and effective readback. Each of four automatic searches performs physical edits and returns SearchUnresolved with a fresh negative certificate on its explicitly limited L=2..3 domain and sync tolerance 0.02 seconds. This does not prove physical infeasibility beyond that domain.

The separate Exact/warm control has fixed structure and explicit sync tolerance 0.2 seconds. It verifies orchestration and lifecycle, not convergence at default tolerance or selectivity. External stop and deadline retain censored evidence and do not manufacture convergence. Unknown spike count remains null.

Production root module Scripts/StructTrain/TimeLearner/native_evidence.py audits the actual C++ outputs. Twelve tests on each host check real traces/certificates plus corruption, nonfinite tokens, duplicate timestamps/IDs, incomplete windows, row permutation and false Exact. Independent audit covers 56 complete traces and four negative certificates, including candidate-to-anchor epoch/revision bindings and actual signed residuals. Analysis has its own source SHA/interpreter/module digest. It produces no recognition/evaluation verdict.

This is an addressed integration run, not a repeated full CTest or the complete mode/physics matrix. Configured ControllerVersion=2/builders, adaptive or assigned-wave window policy, dynamic Rs domains, complete state import/export, C-trim, conversion/PostTune/calibration, experiment runner and scientific controls remain required. State summaries are diagnostics, not checkpoint files. Some stop/budget controls retain diagnostic packets without CSV and are not eligible as complete response trials.

Tested source/runtime manifests are per attempt. Compressed-file checksums and uncompressed hashes are retained. Git is the sole transfer path.
