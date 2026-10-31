# Native threshold JSON roundtrip and Qt 5 owner lifetime

Elder: six native cases and six independent reader tests passed on root 8cfd72eb17c8b762eea590afa6018dfa363f932a / PulseLib dd7cd4fd9982682403bc7799e61c0527f7d461d2. The fixture serializes/parses each finite-domain candidate before native import, including negative zero. The reader checks complete legacy/new control sets, source primary CSV and the sole permitted physical edit. Eighteen additional package audits cover the baseline and final data; these are not independent training repetitions.

The baseline two-case gate passed too: a signed-zero serialization defect was not observed. The code correction addresses a separate Qt 5 C++ lifetime violation: auto retained QJsonValueRef into a destroyed temporary calibration object in the owner importer. An owning QJsonValue now survives that expression. Passing baseline tests do not make the dangling reference valid; no sanitizer-detected crash is claimed.

The lossless archive includes source models/CSV, raw observations, native XML/logs, before/after runtime manifests, reader evidence, and a receipt for deduplication of twenty inactive static-library caches. Every cache replacement was hash-verified and hardlinked to a surviving byte-identical file; no primary data were deleted. Binary caches and bulk plots are excluded.

ASan for this revision is a separate pending gate. Full calibration grid execution, PostTune transaction, independent Test, the complete mode/profile matrix and stage 8 remain open. Scientific verdict is null.
