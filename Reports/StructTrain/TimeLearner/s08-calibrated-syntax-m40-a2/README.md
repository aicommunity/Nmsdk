# Native calibrated-state syntax check

All six production translation units passed -fsyntax-only on M40 using the actual configured compiler command lines, with output/dependency writes removed. PulseLib commit 3d4408d4117330578d2e5e9ba0e049f8cb32ce2d; unchanged Rdk/Basic dependencies came from the recorded dependency root. The private PulseLib worktree preserved Libraries/Nmsdk-PulseLib layout. No active source/runtime was changed.

The first harness attempt is preserved separately: four API files passed, while two learner units mixed old/new PulseLib headers because the private checkout was placed outside its native layout. Duplicate-definition failures are harness failures, not six passing checks. No source patch was made to hide them.

The archive contains all per-unit compiler diagnostics, command lines, source hashes, exit statuses and checkout logs. It contains no binaries or generated reports. This checks syntax only; link, native model behavior, ASan runtime, calibrated model acceptance and stage 8 remain separate pending gates. Scientific verdict is null.
