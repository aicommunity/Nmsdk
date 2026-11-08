# Protocol4 declaration versus raw admission

Source-only fixture correction after Elder206 negative9b9a38f1a5d8842ada5e167d9bdbf33bd24b6381: 111 passed, one failed, 94 not executed. The failing assertion expected protocol4 serialization to throw. It predates the explicit protocol4 declaration codec introduced by Pulse661 and retained in frozen f925.

Encoding/decoding a declared protocol is required by cold6/archive1 portability. It creates no observation, live lease or certificate. RawAdmission retains all existing rejections of Final.Arm(raw), Final.Consume(raw) and CapturedReferences.Capture(raw). It now checks schema4 roundtrip, missing composite contract rejection, incorrect legacy-schema labeling rejection, and issued/accepted zero with no certificate.

Pulse f925e37247bb987980fce80da47831a1c31d04c9 is unchanged. Same literal206 inventory; only the obsolete fixture expectation and its source hashes change. The historical negative evidence is preserved; no new numerical test was executed locally and no runtime acceptance is claimed.
