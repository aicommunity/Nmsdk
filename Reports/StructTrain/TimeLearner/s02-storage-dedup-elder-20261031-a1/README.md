# Verified Elder cache deduplication

Removed only 214 byte-identical duplicate native-result files (739918187 bytes) from the completed s08-native-posttune-controller-normal-a2/native cache. Before deletion all files were compared against the committed primary manifest at 7ee932184d091bd068495f91be2464cdc0e6103f; the complete 907-member Git extraction on M40 was independently rechecked (1712971486 bytes), and no active cwd/fd reader used the target. The compressed Git archive and verified full M40 copy are retained. No unique primary data were removed.

Elder free bytes increased from 406204416 to 1146679296. Original command paths remain historical; reanalysis should use the portable Git extraction on M40 recorded in the receipt.

The completed N0 normal corpus was subsequently reconstructed from commit 437c92cd28471b8a11f73f037c4aa44a58ad3b6c on M40 Data. All 220 archived files / 604878849 bytes were checked twice. After checking the source against the committed manifest and verifying no active reader, 206 duplicate native files / 604854174 bytes were removed from Elder. Free bytes increased from 1140523008 to 1745907712. See n0-offload-deduplication-receipt.json. The immutable Git archive, M40 full copy, and Elder terminal logs are retained.
