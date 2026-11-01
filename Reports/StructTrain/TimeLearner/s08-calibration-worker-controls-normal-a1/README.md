# Production calibration worker: normal controls

Two additional worker tests passed: actual one-model-tick interruption on both topologies restores the source and remains a diagnostic process_error/model_tick_budget_exhausted, and four native Console strict-input/mode rejections leave no output. Eleven independent tests passed: four actual portable run provenance checks (including fully rehashed wrong arguments/owned executable/missing executable mappings) and seven runtime/strict JSON regressions.

The archive retains the actual bounded-stop run manifests, complete primary snapshots and observations, strict-input raw JSON/logs, native compiler/runtime evidence and exact additional build flags. RelWithDebInfo and linker flags are now captured. Original runtime manifests are never replaced: enhanced flags and four generated compilation database entries are separate receipts against the same executable hash. Normal metadata export initially failed because compile_commands.json was disabled; after the eleven tests passed, only CMake metadata export was enabled, without recompiling/rerunning the jobs or tests. Its original exit/log and explicit recovery receipt are preserved.

The original six native Console jobs, both six-test readers and four owned CLI runs are in base normal bundle d663fd43601712cff1e203e0c1fa0ed2f8f443e7; this supplement avoids duplicating that archive.

Runtime process mappings are an initial snapshot, not a complete census of future plugins. Source training remains search_unresolved. Full ConditionSpec, Train/export/evaluate queues, complete PostTune/physical matrix and scientific evaluations remain open. Scientific verdict is null.
