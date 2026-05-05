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
- **Scope:** The first implementation uses `UGenericComponentControllerWidget` placeholders for MotionControl/Pulse/other libs.
- **Why not done immediately:** Full feature parity requires deep UI/logic migration from BCB forms (`TNManipulatorControlForm`, `TNNeuronTrainerForm`, etc.).
- **Risk/impact:** Users get opening support and routing now, but not full domain-specific controls.
- **Closure criteria:** Replace placeholders with dedicated Qt forms for each class group and verify behavior parity.

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
- **Status:** `open`
- **Phase target:** Phase 5
- **Scope:** No dedicated automated tests added yet for `UComponentFormRegistry` and context-menu open pipeline.
- **Why not done immediately:** Requires selecting/creating the most suitable test harness in current project.
- **Risk/impact:** Future regressions may be missed.
- **Closure criteria:** Add smoke/integration tests for: registered class open, unregistered class disabled/info, single-instance reopen.

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
