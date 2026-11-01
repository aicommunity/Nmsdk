# Bounded training implementation checks (elder1)

A2: 29 addressed tests pass, including actual Classic/Branch R normalization at 2000 and 20000 Hz. Each native case uses captured raw per-input references, one actual R edit, six fresh probes, and an independent two-input final certificate. Lengths are fixed; sync tolerance 0.2 seconds isolates R normalization and does not prove default-tolerance synchronization.

A4: 27 addressed tests pass after adding explicit deadline and shared-bank legality. Nine controlled search cases, 17 final-verification cases and a real Branch N0/N1 aliasing fixture. Coincident Branch labels share a physical bank; requested per-label values are not independent readback.

A1 preserves the failed test-helper compilation (Run name hiding). A3 preserves the failed last-writer test expectation; the corrected fixture checks actual bank identity and readback without assuming legacy Reset order. Production shared-bank legality is unchanged between A3 and A4.

Source SHAs and immutable runtime manifests belong to each attempt, not to later merge commits. Raw traces, exact observation windows, actual stimulus timestamps, references, residuals, model hashes and action history are retained. SHA256SUMS.json verifies compressed files; validation.json also records uncompressed hashes. Git alone transfers sources and evidence. These are implementation checks, not selectivity experiments, full CTest, historical replay or complete algorithm acceptance.
