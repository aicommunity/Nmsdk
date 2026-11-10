# Saved Branch C0 package6 fixture

Real saved learned-solo package from completed cold Train/export in an engineering N2 case. The surrounding test later hit a 4GiB OOM; this fixture does not assert whole-case success or complete runtime provenance. It includes original model/storage definitions, C0 baseline, dataset and embedded exact primary observations. SyncTolerance=0.2 is an engineering setting, not the default0.02 or a classification result.

The qCompress-compatible container preserves every byte of the original UTF8 JSON; descriptor.json records source commits, attempt, sizes and SHA256. Replay is distinct from cold retraining and does not replace the failed cold roundtrip.
