# comp_gui Release Checklist

Checklist for final release-readiness validation of the `comp_gui` rollout.

Status values:
- `[x]` completed and evidenced in repository
- `[ ]` pending (must be completed before release tag)
- `[~]` partially completed / requires manual confirmation

## 1) Code and Entry-point Parity

- [x] DrawEngine `GUI` action routes through shared `UComponentGuiService` flow (`UComponentGuiContext` path).
- [x] ModernDiagram entrypoint opens component forms via the same service contract.
- [x] ComponentsList entrypoint opens component forms via the same service contract.
- [x] Single-instance reuse behavior is preserved for repeated open calls.
- [x] Unregistered-class fallback path is deterministic (`nullptr` + user-facing info).

## 2) Tests and Reproducibility

- [x] `Test_ComponentGuiRegistry` includes integration-style pipeline scenarios:
  - diagram open/reopen
  - components-list open/reopen
  - drawengine open
  - unregistered fallback
- [x] Preset-based reproducible test flow exists in `CMakePresets.json`:
  - `linux-gcc-debug-tests`
  - `linux-component-gui-registry`
- [x] Separate lifecycle integration target is available and green:
  - `Test_ComponentGuiLifecycle`
  - `linux-component-gui-lifecycle`
- [x] Generated `Test_ComponentGuiRegistry` binary is ignored in `Bin/.gitignore` (clean working tree during routine checks).
- [x] Generated `Test_ComponentGuiLifecycle` binary is ignored in `Bin/.gitignore`.

## 3) Build Matrix

- [x] Default GUI profile validated (`build`, `NeuroModeler`).
- [x] Core-only profile validated (`build-core-only`, `NeuroModelerConsole`).
- [x] `NO_MOTION_CONTROL` profile validated (`build-motion-off`).
- [x] `NO_PULSELIB` profile validated (`build-pulse-off`).

## 4) Priority Form Readiness

- [x] `MotionControlManipulatorComponentControllerWidget` parity mapping documented (`Reports/comp_gui_manipulator_advanced_mapping.md`).
- [x] Unsupported manipulator legacy controls are explicitly disabled with explanatory UX.
- [x] `PulseLibNeuronTrainerComponentControllerWidget` context refresh and host lookup hardened.
- [x] `PulseLibNeuronLearnerComponentControllerWidget` dedicated controller integrated and registered.
- [~] Final decision on moving `NNeuronTrainer` / `NNeuronLearner` from `ported_partial` to `ported_real` remains a product parity decision.

## 5) Debt and Reports Synchronization

- [x] `Reports/comp_gui_technical_debt.md` synchronized (TD-001..TD-007 closed with evidence).
- [x] `Reports/comp_gui_closure_report.md` synchronized with latest evidence (DrawEngine routing + presets).
- [x] `Reports/comp_gui_bcb_qt_matrix.md` synchronized with current coverage contracts.
- [x] Testing docs include preset-based smoke-check commands.

## 6) Manual Final Smoke (Release Gate)

- [x] Execution protocol prepared: `Reports/comp_gui_manual_smoke_protocol.md`.
- [x] Open component GUI from **DrawEngine** on a real project and verify expected form activation.
- [ ] Open component GUI from **ModernDiagram** and verify same target form and reuse behavior.
- [ ] Open component GUI from **ComponentsList** and verify same target form and reuse behavior.
- [ ] Validate user-facing message for an intentionally unregistered component class.

## 7) Component GUI Interactivity (new)

- [x] Session snapshot model for component GUI is persisted in `Interface.xml` (`ComponentGuiLayout`).
- [x] Floating/grid visual state is persisted in `settings.qt` (`ComponentGui/*` keys).
- [x] Service-level detach/attach API exists for MDI <-> floating migration.
- [x] Base grid container exists with deterministic API (`setGridSize`, `assignCell`, `clearCell`, `swapCells`).
- [ ] Manual validation: save/load restores opened component GUI set and active host mode (mdi/floating/grid).
- [ ] Manual validation: floating geometry/state is restored after reopen.
- [ ] Manual validation: grid splitter layout/state is restored after reopen.

## Go / No-Go

- **Current recommendation:** `CONDITIONAL GO`
- **Condition to switch to full GO:** complete section "Manual Final Smoke (Release Gate)" on target runtime environment and append execution evidence (date, config, operator, result).
- **Latest evidence artifact:** `Reports/comp_gui_manual_smoke_protocol.md` (automated preconditions done, manual scenarios pending).
