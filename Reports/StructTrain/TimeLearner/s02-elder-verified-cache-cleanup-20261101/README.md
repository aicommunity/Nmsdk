Verified Elder duplicate/cache cleanup, 2026-11-01

Removed two abandoned temporary Git GC pack files after no open handles remained: 250044416 and 239501312 bytes; complete object packs/indexes were untouched. Automatic gc disabled only in the owned source clone after its second disk-full failure.

Removed twenty raw JSON duplicates over10MiB from the closed production owned PostTune corpus, 556261102 bytes. Every file matched the complete published archive52d0c1ffaa961a7d65ee8bc244a22fb798319359e6711090f68d9ec7c8e04b95 byte-for-byte. All1452 archive members were independently verified from Git on M40 before removal. Source proof eeeac0a53d450e5e00a201e9081d630f83444145 retains all unique bytes. Restore the named members before rerunning a reader against this raw Elder corpus. Original run manifests remain unchanged and do not assert that an offloaded raw path is still materialized.

Historical user data and unique primary data were preserved. Available root filesystem space after cleanup:759MiB (df rounded). Per-file paths, sizes and SHA256 are recorded in the receipts.
