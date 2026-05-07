# Component GUI Migration Technical Debt

This file tracks unresolved migration items for the `comp_gui` branch.

## Status legend
- `open` - not implemented yet
- `in_progress` - partially implemented
- `closed` - implemented and verified

## Items

### TD-001 - Real Qt ports for legacy BCB controllers
- **Status:** `closed`
- **Phase target:** Phase 4 / Phase 5
- **Scope:** Dedicated widgets cover `NAstaticGyro`, `NNewPositionControlElement`, `NNeuronTrainer`, `NNeuronLearner`, and manipulator class groups (`TNManipulatorControlForm`/`TNewManipulatorControlForm`). Advanced mapping is fixed in `Reports/comp_gui_manipulator_advanced_mapping.md`.
- **Resolution:** Unsupported legacy controls are explicitly marked as `explicitly_not_supported` with deterministic UI behavior (disabled + explanation), which closes ambiguity for users and maintainers.
- **Evidence:** Dedicated widget files and registry wiring in MotionControl/PulseLib plus updated matrix entries.

### TD-002 - Dedicated tab hosting policy in MDI
- **Status:** `closed`
- **Phase target:** Phase 5
- **Scope:** Component forms are opened through existing MDI-host behavior in `UGEngineControlWidget`/`UComponentGuiService` with single-instance reuse.
- **Resolution:** Current MDI policy is accepted as target behavior for Qt migration branch; no additional tab-refactor required in this rollout.
- **Evidence:** Stable `openComponentGuiFromScheme` path and repeated open reuse behavior in service pipeline.

### TD-003 - Extended class coverage for non-priority libraries
- **Status:** `closed`
- **Phase target:** Phase 4B
- **Scope:** Matrix synchronized with current registration coverage in Basic/CvBasic/Hardware.
- **Resolution:** Registered non-priority classes are explicitly represented in matrix with `ported_partial` contracts.
- **Evidence:** Registration files in `Libraries/Rdk-BasicLib/GUI/Qt`, `Libraries/Rdk-CvBasicLib/GUI/Qt`, `Libraries/Rdk-HardwareLib/GUI/Qt` + matrix updates.

### TD-004 - Tests for registration and GUI open path
- **Status:** `closed`
- **Phase target:** Phase 5
- **Scope:** Service/registry smoke coverage is in place; entrypoint behavior is validated for diagram, components list, and DrawEngine contexts.
- **Resolution:** Integration-style tests cover open/reopen/close-reopen/fallback scenarios through the shared service contract.
- **Evidence:** `Rdk/Tests/Unit/Test_ComponentGuiRegistry.cpp` (`ComponentGuiPipeline.*`, including `CloseAndReopenCreatesNewInstance`), stable `build-tests` execution, ignored generated binary in `Bin/.gitignore` (`Test_ComponentGuiRegistry`), and reproducible `CMakePresets.json` test flow (`linux-gcc-debug-tests` + `linux-component-gui-registry`).

### TD-007 - Incremental core/qt split for MotionControl/PulseLib
- **Status:** `closed`
- **Phase target:** Phase 6
- **Scope:** Distinct targets introduced for MotionControl/PulseLib (`*.core` + `*.qt` interface target).
- **Resolution:** Target split implemented and validated with profile builds (`GUI full`, `core-only`, `NO_MOTION_CONTROL`, `NO_PULSELIB`).
- **Evidence:** Updated submodule CMake files and successful profile builds in `build-core-only`, `build-motion-off`, `build-pulse-off`.

### TD-005 - Feature-flag rollout for component GUI
- **Status:** `closed`
- **Phase target:** Phase 6
- **Scope:** Global and per-library switches are implemented in `UGEngineControlWidget` and `UComponentGuiBootstrap`.
- **Resolution:** Registration is now gated by global + per-library flags with env override priority.
- **Evidence:** `EnableComponentSpecialFormsQt.*` settings keys, `NMSDK_ENABLE_COMPONENT_SPECIAL_FORMS_QT_*` env overrides, and docs update in `Docs/GUI/Overview.md`.

### TD-006 - Legacy entrypoint parity outside modern diagram
- **Status:** `closed`
- **Phase target:** Phase 5
- **Scope:** DrawEngine path now uses the same component-GUI open contract as modern entrypoints.
- **Resolution:** Replaced explicit disable policy with context-based open request (`UComponentGuiContext`) routed to shared `UComponentGuiService`.
- **Evidence:** `Rdk/GUI/Qt/UDrawEngineImageWidget.*`, `Rdk/GUI/Qt/UDrawEngineWidget.*`, and `UGEngineControlWidget::openComponentGuiFromScheme`.

### TD-008 - Advanced grid interactions for component GUI
- **Status:** `open`
- **Phase target:** Follow-up after first full interactivity rollout
- **Scope:** Add drag-and-drop between grid cells, richer cell-level toolbar actions, and nested tabs inside one grid cell.
- **Deferred reason:** Excluded from first implementation to keep lifecycle persistence (`save -> close -> open`) stable and avoid regressions in MDI host activation.
- **Return condition:** Enable when base grid persistence and detach/attach flow are stable across integration target and manual smoke.
- **Current baseline:** `UComponentGuiGridContainerWidget` supports deterministic API `setGridSize/assignCell/clearCell/swapCells`, splitter resize persistence, and context restore.

### TD-009 - Full stale-key garbage collection in settings.qt
- **Status:** `open`
- **Phase target:** Follow-up hardening
- **Scope:** Aggressive cleanup of obsolete `ComponentGui/Floating/*` and `ComponentGui/Grid/*` keys that no longer map to active sessions/containers.
- **Deferred reason:** Base stale-key cleanup is implemented for known sessions/grids; deferred part is migration-safe aggressive cleanup (deep recursive pruning + compatibility backup/rollback strategy).
- **Return condition:** Add migration-safe cleanup pass with backup/snapshot in dedicated hardening stage.

### TD-010 - Native dock migration hardening for component GUI
- **Status:** `in_progress`
- **Phase target:** Current stabilization cycle
- **Scope:** Replace custom floating/DnD wrapper paths with native `QDockWidget` host lifecycle (dock/floating/reattach) while preserving grid roundtrip compatibility.
- **Decision:** Execute migration incrementally with compatibility fallback for test MDI harness; remove cursor-based `IgnoreAction` business logic from production paths.
- **Impact:** Reduces nondeterministic DnD behavior and style regressions during detach/attach; requires expanded regression matrix for dock + grid transitions.
- **Owner:** Codex + user validation on desktop runtime
- **Exit criteria:** Native dock cycle passes unit/lifecycle tests, manual drag float/reattach works without style loss, technical debt item moved to `closed` with evidence links.
