# Native PostTune controller: ASan scoped proof

Root 44a1598a / PulseLib c8a1995 passed ten actual native tests: Classic/Branch N1/2000 Hz measured PostTune transactions and eight ownership controls; no skips, 3733.602 s. Nineteen original independent reader checks passed in 158.845 s. The later strict-container reader revision e9f3cc852 passed twenty checks on the same data in 159.205 s, without native rerun.

All 24 parent reports and their original observations/models are retained. Leak detection was disabled; this gate does not prove absence of leaks or full mode/profile/frequency coverage. Production Console ASan is a separate gate.

The mechanical recognition-scope A/B also completed on ASan: each binary ran two actual grid cases initially (the initial invocation skipped eight ownership cases and was rejected), then eight real ownership cases in recovery, plus four independent checks per set. All 28 paired CSV and eight ownership JSON controls matched exactly. These A1/A2 receipts are preserved. The older queued parent-controller ASan A1 was cancelled before checkout/build/native start after the recording-budget defect was found on normal; its cancellation receipt is retained, not labelled a native failure.

This scoped gate does not establish eight-pattern classification or independent robustness, and does not accept stage 8.
