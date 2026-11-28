# Actual saved Classic model fixture

`learned-state.json.qz` is the exact, unmodified JSON member identified by
`descriptor.json`, compressed in Qt `qCompress` format (big-endian expanded
length followed by zlib). Its expanded SHA256 is checked before parsing.
The compressed primary bytes live in the external M40 archive identified by
`learned-state.json.qz.archive.json`; the source Git tree contains only that
reference and the descriptor. The complete original run remains archived.

Declare this exact object as a native-gate DATA input named
`classic-package6.qz` (323020 bytes, SHA256
`d58ce13f3759a9e7c38f65c2cdb3059bb7ddccbd152d7e4144564c1efa36b234`).
The gate stages it in `native-inputs` beside its owned `native` output and
verifies both the declared source and staged bytes after execution. The C++
fixtures read only that staged input and additionally check its compressed
identity, qCompress allocation length and exact expanded identity. They never
restore binaries into the source tree. A missing declaration is a failed
fixture, not a skipped or passed model replay. Linux schemas5/6 support these
inputs; Windows schemas4/7 do not yet implement recorded DATA staging.

This is an engineering saved-state replay, not a new cold training or
scientific classification result. The original run completed two image controls
and failed the next Classic package roundtrip. Its training declaration and
tolerances retain their original scope; they are not recommended new defaults.

The replay uses the actual native image registration, dataset/model import and
model export implementations. It validates the original integrity digests,
retains the exact live graph including XML, and compares storage definitions
using the production semantic image fingerprint. Storage images are model
definitions, not dynamic checkpoints. The separate `NativeImageRestSnapshot`
controls retain their exact archive comparisons and unresolved failures.
The replay frees the real model and dataset child graphs before repeating.
It does not validate the complete learner package,
reconstruct unavailable CSV measurements, run calibration, or resume training.
