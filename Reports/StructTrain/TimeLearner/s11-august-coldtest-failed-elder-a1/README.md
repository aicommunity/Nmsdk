# Failed historical cold-model frozen Test

First transfer attempt incorrectly forced learner StructureBuildMode0 in both Model and Parameters. Original inputs use Model1/Parameters0. Console completed model time and wrote CSV, then aborted (SIGABRT, free invalid pointer) during learner/storage destruction. Cached SomaNeuronAmplitude has two values instead of the required five. Process error forbids accepting this as a successful classification result.

Exact prepared inputs, post-save exports, all12 raw temporal streams, CSV, process/runtime receipts, stderr stack and supervisor failure are retained. Corrected producer preserves the original load layers and adds a native prestimulus graph/buffer/process gate. Historical C++ remains unchanged. Present-day lifecycle ownership requires separate normal/ASan verification.
