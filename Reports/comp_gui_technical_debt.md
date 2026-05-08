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

### TD-008 - Advanced tab-host interactions for component GUI
- **Status:** `open`
- **ID:** `TD-008`
- **Phase discovered:** Phase 6/7 (tab-host migration validation)
- **Context:** Base tab-host is functional but intentionally minimal to keep migration deterministic.
- **Decision:** Defer advanced interaction layer until core lifecycle is fully stabilized in production use.
- **Phase target:** Follow-up after tab-host stabilization
- **Scope:** Add richer tab-host DnD ergonomics (cross-host previews, tab reorder persistence, bulk move actions).
- **Deferred reason:** Excluded from core migration to keep host lifecycle + restore compatibility deterministic in first rollout.
- **Target phase/commit for closure:** Next hardening cycle after post-migration regression pass.
- **Risk if deferred:** UX remains functional but less discoverable/efficient for complex multi-host workflows.
- **Verification evidence needed:** Manual DnD UX matrix + targeted unit tests for tab reorder/persistence.
- **Return condition:** Enable after base `mdi/floating/tab-host/secondary-host` restore matrix is fully stable.
- **Current baseline:** `UComponentGuiTabHostWidget` provides deterministic add/remove context flow and basic DnD payload routing.

### TD-009 - Full stale-key garbage collection in settings.qt
- **Status:** `open`
- **ID:** `TD-009`
- **Phase discovered:** Phase 4 (persistence redesign)
- **Context:** Migration adds new key space while preserving compatibility readers for old keys.
- **Decision:** Keep conservative stale-key cleanup now; postpone aggressive recursive pruning.
- **Phase target:** Follow-up hardening
- **Scope:** Aggressive cleanup of obsolete `ComponentGui/Floating/*`, `ComponentGui/Grid/*`, and `ComponentGui/TabHost/*` keys that no longer map to active sessions/containers.
- **Deferred reason:** Base stale-key cleanup is implemented for known sessions/hosts; deferred part is migration-safe aggressive cleanup (deep recursive pruning + compatibility backup/rollback strategy).
- **Target phase/commit for closure:** Dedicated persistence hardening phase after migration freeze.
- **Risk if deferred:** Settings file may accumulate obsolete keys and increase restore ambiguity in edge cases.
- **Verification evidence needed:** Before/after snapshot diff of `settings.qt` across repeated open/close cycles.
- **Return condition:** Add migration-safe cleanup pass with backup/snapshot in dedicated hardening stage.

### TD-010 - Native dock migration hardening for component GUI
- **Status:** `in_progress`
- **ID:** `TD-010`
- **Phase discovered:** Current migration rollout
- **Context:** Native dock migration completed functionally, but requires broader runtime evidence to close confidently.
- **Decision:** Keep item open until desktop manual validation fully confirms stability across user scenarios.
- **Phase target:** Current stabilization cycle
- **Scope:** Replace custom floating/DnD wrapper paths with native `QDockWidget` host lifecycle (dock/floating/reattach) while preserving tab-host roundtrip compatibility.
- **Impact:** Reduces nondeterministic DnD behavior and style regressions during detach/attach; requires expanded regression matrix for dock + tab-host/secondary-host transitions.
- **Owner:** Codex + user validation on desktop runtime
- **Target phase/commit for closure:** First post-merge stabilization commit with manual evidence links.
- **Risk if deferred:** Potential uncovered platform-specific DnD edge cases during extended usage.
- **Verification evidence needed:** Manual smoke protocol with pass logs for float/reattach/tab-host/secondary-host flows.
- **Exit criteria:** Native dock cycle passes unit/lifecycle tests, manual drag float/reattach works without style loss, technical debt item moved to `closed` with evidence links.

### TD-011 - Legacy config migration strictness
- **Status:** `open`
- **ID:** `TD-011`
- **Phase discovered:** Phase 4 (compatibility adapter implementation)
- **Context:** Loader now maps legacy `grid` records to tab-host, but strict schema auditing is intentionally permissive.
- **Decision:** Accept permissive compatibility fallback now; defer strict migration validation tooling.
- **Phase target:** Post-migration hardening
- **Scope:** Improve strict migration coverage for older `ComponentGuiLayout` schemas and mixed legacy keys (`Grid_*`, old host mode values).
- **Deferred reason:** Full backward-matrix tooling would delay core host migration delivery.
- **Target phase/commit for closure:** Compatibility hardening task in next regression cycle.
- **Risk if deferred:** Rare historical layouts may restore to default placement rather than exact legacy arrangement.
- **Impact if deferred:** Some rare legacy combinations may restore to default host target instead of exact historical placement.
- **Verification evidence needed:** Dedicated compatibility regression set with archived legacy configs.
