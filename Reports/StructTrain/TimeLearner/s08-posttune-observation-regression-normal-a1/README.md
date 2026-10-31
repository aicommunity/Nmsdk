# TL-037 normal regression and stronger primary analysis

The immutable A2 binary root e3fe53408b861b49c0e0ddc6c3de9acc548a9e54 / PulseLib 39810a760103d2e5d5a5b9e6ae6575290522b20c passes 37 additional native cases (318.086 seconds): transient stimulus, graph boundaries, owner policy, lifecycle/listener guards and native reconstruction. These are separate from the twelve addressed A2 cases, not a rerun of one 49-case invocation. Negative-control error log lines are retained; JUnit has no failures/errors/skips.

Reader a153c052af7cfd2953e2fe2a1ce087bc7b5f2cc7 passes six checks (5.867 seconds), including direct replay of both actual sample peaks from all raw CSV rows and rejection of a forged finite peak. This strengthens analysis of the same four physical traces without new simulation or figure regeneration. The earlier five-check receipt and running renderer source remain separate snapshots.

Bin 97dd1943 metadata validation covers two XML documents and four source-declared ptPubState properties (258); it is not a native UI/runtime test. Failed transport assertion A1 and corrected ASCII-escaped JSON A2 are both preserved; valid UTF-8 repository content did not change during that correction.

All native primary traces, metadata, models, runtime/source closure and logs are lossless. Full visual reports for these regression waveforms and ASan scope remain separately tracked, as does the full original refactoring plan. No scientific verdict is claimed.
