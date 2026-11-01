# TL-037 ASan regression gate

The immutable root e3fe53408b861b49c0e0ddc6c3de9acc548a9e54 / PulseLib 39810a760103d2e5d5a5b9e6ae6575290522b20c passes 37 additional native cases: transient stimulus, graph boundaries, owner policy, lifecycle/listener guards and native reconstruction. Leak detection is disabled. JUnit and lossless primary CSV/model/metadata plus source/runtime/build records are included. This is separate from the addressed twelve-case A2 gate.

All waveform report acceptance, the next PostTune candidate implementation and the full original plan remain separate. No scientific verdict or full-stage completion is claimed.
