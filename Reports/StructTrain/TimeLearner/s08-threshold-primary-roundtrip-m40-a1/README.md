# Primary threshold bundle roundtrip on M40

A fresh sparse checkout of published root 766740035c1ced53d75fbce3d1aa4602b753b4f4 fetched the compact Elder bundle through Git.
All 308 archive members were verified by path, regular-file type, size and SHA256 before extraction.
The production calibrate select and confirm commands re-analysed all four native controls from extracted primary CSV/models/observations.
All eight result JSON objects equal the archived reference objects. The fields named *_byte_semantics_equal report parsed JSON equality, not a raw output byte comparison.
No simulator or native import was run in this readback; the ASan native gate and complete stage-8 acceptance remain separate.
Source data are losslessly preserved in ../s08-threshold-potential-normal-a3/primary.tar.xz; this receipt does not duplicate them.
