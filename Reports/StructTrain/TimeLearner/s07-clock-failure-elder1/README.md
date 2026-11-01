# Failed full maintained gate and absolute-clock sampling reproducer

The earlier root 157a5301ed418d61f4ccd86829ba483308c4300c / PulseLib e875ca53c66fee93ba18cf7f7da05a87f33d32f9 full maintained run has terminated with failure. All three Rdk groups pass; PulseLib has 430 parent cases, 22 failures, ten skips. Failed cases include configured Classic N1, six-input Branch transport and all twenty stopped-state controls. Child failures, primary observations/CSV and runtime/loaded-process manifests are retained. Successful addressed tests do not replace this failed full gate.

Root f712e8652d32f272472e036c0df8a1f34b861500 adds a reproducer without changing production physics/controller: one regular recorder control and all eight real Classic/Branch probes fail at absolute origins 131 and 1000000 seconds, 2000/20000 Hz; the dropped-frame control passes. Total ten cases, nine expected failures. On M40 this reproducer uses ASan detect_leaks=0. It localizes a false sample_gap caused by comparison slack losing the scale of subtracted absolute timestamps.

The later correction and seeded regression attempts are separate source snapshots and are not claimed as validated here. No full acceptance, scientific selectivity verdict or causal claim about historical August observations is made. Primary files are preserved but a complete independent measurement audit of this failed full run is not claimed.

Elder-1 also retains the preceding A4 preparation failure: BUILD_TESTING was disabled in that cache, so Rdk test targets were absent; no CTest ran in A4. A5 enabled it explicitly. Nothing is silently restarted or relabeled passed.
