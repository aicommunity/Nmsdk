# Component GUI Migration Technical Debt

This file tracks unresolved migration items for the `comp_gui` branch.

## Status legend
- `open` - not implemented yet
- `in_progress` - partially implemented
- `closed` - implemented and verified

## Items

### TD-001 - Real Qt ports for legacy BCB controllers
- **Status:** `in_progress`
- **Phase target:** Phase 4 / Phase 5
- **Scope:** Dedicated widgets now cover `NAstaticGyro`, `NNewPositionControlElement`, `NNeuronTrainer`, and manipulator class groups (`TNManipulatorControlForm`/`TNewManipulatorControlForm`) with partial parity. Remaining placeholder in Priority A/B wave is `NNeuronLearner`; manipulator hardware and advanced parity is still incomplete.
- **Why not done immediately:** Full feature parity requires deep UI/logic migration from BCB forms (`TNManipulatorControlForm`, `TNNeuronTrainerForm`, etc.).
- **Risk/impact:** Routing/opening is available and key manipulator model controls are available, but WinAPI hardware actions and full advanced block parity are missing.
- **Closure criteria:** Replace `NNeuronLearner` placeholder and finish manipulator parity gaps (hardware integration where applicable and advanced `TNewManipulatorControlForm` block) with verified model bindings and single-instance reuse.

### TD-002 - Dedicated tab hosting policy in MDI
- **Status:** `open`
- **Phase target:** Phase 5
- **Scope:** Current implementation opens component forms as windows from `UComponentGuiService`.
- **Why not done immediately:** Existing host container has mixed Dock/MDI custom widget behavior and needs careful refactor.
- **Risk/impact:** UX differs from BCB tabbed controller mode.
- **Closure criteria:** Add explicit tab policy with stable reuse behavior per `componentLongName + channel`.

### TD-003 - Extended class coverage for non-priority libraries
- **Status:** `in_progress`
- **Phase target:** Phase 4B
- **Scope:** Added starter mappings for Basic/CvBasic/Hardware; class list coverage is not exhaustive.
- **Why not done immediately:** Full class inventory per library should be validated with domain owners.
- **Risk/impact:** Some components still won't show `GUI...` menu action.
- **Closure criteria:** Matrix coverage is complete and tested for all target classes.

### TD-004 - Tests for registration and GUI open path
- **Status:** `in_progress`
- **Phase target:** Phase 5
- **Scope:** Smoke unit-tests for `UComponentFormRegistry` and `UComponentGuiService` have been added in Rdk tests; GUI/context-menu pipeline is still covered only manually.
- **Why not done immediately:** Full GUI pipeline tests require interactive/Qt GUI harness which is out of scope for the current phase.
- **Risk/impact:** Core registry/service contracts are guarded; context-menu wiring regressions may still slip through without integration tests.
- **Closure criteria:** Add integration tests that drive context-menu entrypoints (diagram + components list) and verify registered/unregistered/single-instance behavior end-to-end.

### TD-007 - Incremental core/qt split for MotionControl/PulseLib
- **Status:** `in_progress`
- **Phase target:** Phase 6
- **Scope:** Initial CMake options (`NMSDK_MOTIONCONTROLLIB_BUILD_CORE_ONLY`, `NMSDK_PULSELIB_BUILD_CORE_ONLY`) added to allow building libraries without Qt GUI helpers; actual separation of targets and CI matrix are not implemented yet.
- **Why not done immediately:** Requires careful dependency analysis and CI configuration to avoid breaking existing Qt builds.
- **Risk/impact:** Current builds are unchanged by default; headless/core-only scenarios still need refinement and verification.
- **Closure criteria:** Introduce distinct `*.core` targets, wire them into CI matrix (core-only vs qt), and update app/linking configuration accordingly.

### TD-005 - Feature-flag rollout for component GUI
- **Status:** `in_progress`
- **Phase target:** Phase 6
- **Scope:** Basic flag support added in `UGEngineControlWidget` (`EnableComponentSpecialFormsQt`, env override: `NMSDK_ENABLE_COMPONENT_SPECIAL_FORMS_QT`), but staged per-library rollout is not implemented yet.
- **Why not done immediately:** First step was global on/off gate to avoid regressions; granular rollout requires additional registration partitioning.
- **Risk/impact:** Feature can be globally disabled, but no fine-grained library-level control yet.
- **Closure criteria:** Add per-library rollout switches and document deployment profiles.

### TD-006 - Legacy entrypoint parity outside modern diagram
- **Status:** `in_progress`
- **Phase target:** Phase 5
- **Scope:** `UComponentsListWidget*` entrypoints are wired; legacy draw-engine path still has `GUI (not implemented)`.
- **Why not done immediately:** Priority was given to modern diagram + components list workflow.
- **Risk/impact:** Users in legacy visualization path may still see incomplete GUI behavior.
- **Closure criteria:** Decide scope for `UDrawEngineImageWidget` and implement/disable consistently with user-facing behavior.
