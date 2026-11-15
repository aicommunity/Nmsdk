# Actual saved Classic model fixture

`learned-state.json.qz` is the exact, unmodified JSON member identified by
`descriptor.json`, compressed in Qt `qCompress` format (big-endian expanded
length followed by zlib). Its expanded SHA256 is checked before parsing.
The complete original run remains in the referenced Git primary archive.

This is an engineering N=2 saved-state replay, not a new cold training or
scientific classification result. The original run completed two image controls
and failed the next Classic package roundtrip. Its training declaration and
tolerances retain their original scope; they are not recommended new defaults.

The replay uses the actual native image registration, dataset/model import and
model export implementations. It compares the whole model archive without
discarding XML fields or hashes, then frees the real model and dataset child
graphs before repeating. It does not validate the complete learner package,
reconstruct unavailable CSV measurements, run calibration, or resume training.
