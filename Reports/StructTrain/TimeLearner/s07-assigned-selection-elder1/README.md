# Explicit assigned-wave selection (elder1)

Root f2fe81f96d68859690ae56e4ef29f5c32c549bc7: 56/56 addressed C++ tests pass without skips on this host. These cover the production ProbeRecorder, final-verification protocol/certificate binding, bounded-search regressions, invalid preflight, and real Classic/Branch wide-window probes using the native scheduler and reset. No nested model calculation is introduced.

The default IsolatedWindow rule still rejects a window containing two response maxima. AssignedBurstWave is an explicit schema-3 opt-in: the entire actual burst must have a valid ordered assignment, and the selected wave must have actual samples on both sides of its plateau inside the declared window. Predicted delay does not confirm a peak. A controlled trace verifies delayed p0 after p1 onset without relabelling it p1. Real native cases verify unchanged physical response and model identity under the two measurement policies, not successful training at large cable lengths.

Evidence envelope 2 declares peak_selection in requested and actual specifications. Auditor v3 supports envelope 1 with its original isolated semantics, rejects unknown/injected/changed policy, and checks actual neighbouring samples. All 18 Python data/corruption tests pass without skips. Four new native packets contain two invalid isolated-window observations and two valid assigned-wave observations. Invalid packets remain diagnostics and are not counted as complete valid response trials.

Backward audit rechecks 56 actual old CSV/packets and four negative model-bound training summaries from root 90d11d1990221753e6b494dbf40d83964b7d0fa3. Those primary artifacts remain in the sibling s06-native-service-elder1 package; analysis identity is recorded separately.

This is addressed acceptance, not a new full CTest run, complete physics matrix, scientific selectivity result, long-cable convergence or configured ControllerVersion=2. Ordered assignment assumes one distinguishable positive wave per stimulus with preserved order. Missing/extra/merged waves remain unresolved. Adaptive observation duration and performance of complete model identity remain separate work.

Git is the sole transfer path. SHA256SUMS covers stored files; validation.json records the hashes and sizes of uncompressed payloads. Runtime manifests include immutable source closure and actual binary/dependency hashes; executables are not committed.
