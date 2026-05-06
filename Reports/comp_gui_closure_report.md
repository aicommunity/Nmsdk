# comp_gui Closure Report

## Scope

This report summarizes closure evidence for `TD-001..TD-007` after the detailed execution plan rollout.

## Evidence by TD

### TD-001
- **Code:** Dedicated controllers for `NNeuronLearner`, `NNeuronTrainer`, `NAstaticGyro`, `NNewPositionControlElement`, and manipulator group.
- **Matrix:** `Reports/comp_gui_bcb_qt_matrix.md` updated (no learner placeholder remains).
- **UX:** Unsupported manipulator advanced items are explicit and disabled, not ambiguous.
- **Mapping:** `Reports/comp_gui_manipulator_advanced_mapping.md`.

### TD-002
- **Code:** Existing MDI-host policy in `UGEngineControlWidget` + `UComponentGuiService` retained as accepted target.
- **Behavior:** Single-instance reuse policy remains active for repeated open calls.

### TD-003
- **Code:** Registration coverage confirmed for Basic/CvBasic/Hardware registration units.
- **Matrix:** Non-priority classes (`NModel`, `NCvImageSource`, `NHardwareDevice`, `UNet`) synchronized with effective contracts.

### TD-004
- **Code:** Service/registry tests in `Rdk/Tests/Unit/Test_ComponentGuiRegistry.cpp` include `ComponentGuiPipeline` scenarios.
- **Validation:** Diagram, components list, and DrawEngine context paths are covered for open/reopen/fallback behavior.
- **Stability:** Generated test binary is ignored in `Bin/.gitignore` (`Test_ComponentGuiRegistry`) to avoid false dirty state during routine verification.
- **Reproducibility:** `CMakePresets.json` now includes linux build/test presets for this path (`linux-gcc-debug-tests`, `linux-component-gui-registry`).

### TD-005
- **Code:** Per-library rollout options added in `UGEngineControlWidget` and `UComponentGuiBootstrap`.
- **Settings/Env:** Global + library-level keys and env overrides implemented.
- **Docs:** `Docs/GUI/Overview.md` updated.

### TD-006
- **Code:** DrawEngine `GUI` action builds `UComponentGuiContext` and emits `openComponentGuiRequested` through `UDrawEngineWidget`.
- **UX:** DrawEngine opens component forms via the same shared service path as ModernDiagram/ComponentsList.

### TD-007
- **Code:** Introduced `Nmsdk-MotionControlLib.core` + `Nmsdk-MotionControlLib.qt` and `Nmsdk-PulseLib.core` + `Nmsdk-PulseLib.qt`.
- **Build Profiles:** Successful builds validated for:
  - default GUI build (`build`)
  - core-only (`build-core-only`)
  - motion-control-off macro profile (`build-motion-off`)
  - pulse-lib-off macro profile (`build-pulse-off`)

## Final State

- Technical debt statuses are synchronized to `closed` in `Reports/comp_gui_technical_debt.md`.
- Migration matrix is synchronized to actual component GUI coverage.
- Component GUI rollout is globally and per-library configurable.
- DrawEngine entrypoint parity and integration-style pipeline test coverage are part of closure evidence.
