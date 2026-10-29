# Native owner configuration bindings: M40 ASan

Fixed native source root 1f819b429a292a575593203be3bfe6b42392c8c4 / PulseLib cbbf56ce541027ef8e07d6be7a1841cf513b2b8e / Rdk abc21b650471ef6d2e5ef9ba94429d34f3697323. All 16 focused ASan tests passed: Classic/Branch, construction/import, scalar/vector, conflicting and matching read-only sources. An independent JSON readback verified all 16 records, source immutability, conflict rejection before graph replacement, and matching-source success. Fixture training tolerance is 1 second for boundary isolation; no scientific selectivity verdict.

Baseline A4 root 45a70584ec6bfdd843d556ae2485249ce06a7ea4 with old PulseLib Core c7266dcb: 8 conflicting cases failed as expected and 8 matching controls passed. A3 root 2df1db4996d4ff25069d3e83f24864d880188095: 8 expected conflicting failures. These show accepted graph replacement despite owner metadata remaining externally driven, not overwrite of SetPointer sources.

A1 root 769e8d564757bc0dc6b94a143cbc8b33ce8e1be4 initially used an incorrect vector-to-vector SetPointer fixture. The native vector collector expects scalar sources; its crash and isolated A2 diagnostic are retained, not classified as an algorithm/Rdk bug. Corrected fixtures use two real scalar output sources. The fix accepts matching connected data without writing the source; conflicting mirror values fail before live graph replacement.

All logs, runtime manifests, XML, model exports/training proofs and binding records of all five attempts are retained losslessly. No core dump or executable is published. Individual editor parameter writes, controller flags/external stop, full recognition/PostTune integration and full-plan acceptance remain separate work. Rdk lifecycle bool semantics and scheduler are unchanged.
