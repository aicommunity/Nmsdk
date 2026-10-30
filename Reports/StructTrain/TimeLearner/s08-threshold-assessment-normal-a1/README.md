# Native response assessment: normal gate

Producer root ad975bbeb5df18555d94329d3ee95f321921c171 / PulseLib 25cf6a5bfadc0ee72182cb924f1d0730cf6dc71b; reader 1ef44e2e6c5ce40339f9aeaa5e4426810e36844b.

All 16 native cases and 35 independent Python tests passed on Elder without skips/errors/failures. The lossless archive contains all actual potential and legacy observations, source CSV, models, 64 native assessments and runtime/gate/readback metadata. It does not contain executable binaries or generated image caches.

Extract primary.tar.xz into a new directory. Set TIMELEARNER_THRESHOLD_CANDIDATE_DIR to legacy-native and TIMELEARNER_THRESHOLD_POTENTIAL_DIR to potential-native; run the candidate, calibration, proposal and native calibration evidence test modules at the reader revision. Manifest records every member size and SHA256.

The later signed-threshold v2 changes are not tested by this snapshot. ASan acceptance, final native calibrated-state commit/export, full visual cache and stage 8 remain open. Scientific verdict is null.
