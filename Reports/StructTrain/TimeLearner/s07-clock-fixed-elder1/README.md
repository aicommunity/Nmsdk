# Absolute-clock sampling correction: addressed native and independent data checks

Native root 241db7256f0b6595b8e3d239d66d2bbd6d1a6762, PulseLib d4c0cf0b4e93cb9df23a88ddf2479685748d90c8; normal Qt5/GCC11. All 52 selected C++ cases pass with explicit test-process initial time 131 seconds. They include four recorder/final-gate controls, eight real shifted-clock Classic/Branch probes at 2000/20000 Hz, fourteen configured controls, six completed-state transports and twenty stopped-state controls, with genuine fresh child processes.

All eight clock CSV files are byte-identical before/after the C++ correction: physical dynamics and stimuli were unchanged. Only false sampling/coverage invalidation is corrected. Missing frames and unresolvable timestamp scale still fail. Sync/amplitude tolerances and Rdk scheduler/reset semantics are unchanged.

A2's native exit-status file is the C++ stage status, not overall pipeline success. Its subsequent 24-test Python stage failed four large-origin subtests: the requested-duration comparison also lost the scale of absolute endpoints. Those original failures remain archived. Python root aeff4a9d73c02b7672352ecb1b7a4b1cd8de9224 corrects that comparison and adds a one-period corruption control. A separate Python-only worktree audits the same immutable data without rebuilding or rerunning the native experiment: all 25 tests pass.

The independent audit verifies eight complete primary clock probes, six completed packages / 84 original trials and twenty stopped packages / 66 original trials. Probe auditor version is 4; invalid historical observations are not automatically recertified. Complete native/child XML, primary JSON/CSV, model packages, runtime and original/corrected Python logs are preserved.

This is addressed validation, not a successful full maintained gate, all-profile/search acceptance, completion of refactoring stages, scientific selectivity, or a causal explanation of historical August observations. New full normal gates remain separate runs.
