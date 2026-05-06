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
- **Resolution:** Integration-style tests cover open/reopen/fallback scenarios through the shared service contract.
- **Evidence:** `Rdk/Tests/Unit/Test_ComponentGuiRegistry.cpp` (`ComponentGuiPipeline.*`) and stable `build-tests` execution.

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
