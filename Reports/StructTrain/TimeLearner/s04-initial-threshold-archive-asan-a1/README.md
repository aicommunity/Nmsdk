# Native initial-threshold physical archive: ASan18

Root 63d861e823aea132625b22f3702ac11c3d1e7320; Pulse541bf89.
M40 Qt6/GCC13, -O1 -g1 AddressSanitizer, leak detection disabled.
All18 actual native tests pass, including four post-construction graph and
paired response roundtrips Classic/Branch x2000/20000Hz. Actual libasan mappings
are recorded. The original closed ASan14 SDK/build was reused with only the
test CPP changed; the original runtime bytes and realpaths are unchanged.
No training/certification/calibration or independent classification is claimed.
Calibrated recognition-state ModelSpec2 roundtrip and full stages4/5 remain open.
