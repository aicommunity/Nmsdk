# comp_gui Manual Final Smoke Protocol

Purpose: execute the final release gate from `Reports/comp_gui_release_checklist.md` and produce auditable evidence for switching `CONDITIONAL GO` -> `GO`.

## Preconditions

- Branch: `comp_gui` (root + relevant subrepos).
- Build is successful for verification profiles (`build`, `build-core-only`, `build-motion-off`, `build-pulse-off`).
- Preset smoke test is green:
  - `cmake --preset linux-gcc-debug-tests`
  - `cmake --build --preset linux-gcc-debug-tests`
  - `ctest --preset linux-component-gui-registry`
  - `ctest --preset linux-component-gui-lifecycle`

## Test Data Setup

Use any real project/config where component classes with registered forms are available (for example: manipulator, neuron trainer/learner, astatic gyro).

Record:
- Date/time
- Operator
- Project/config path
- Build profile used

## Scenario A: DrawEngine Entry

1. Open project in `NeuroModeler`.
2. Open DrawEngine view.
3. Right-click target component and select `GUI`.
4. Verify form opens.
5. Repeat `GUI` action on the same component and verify existing instance is activated (no duplicate window for `singleInstance=true`).

Expected:
- Open succeeds via shared component GUI service.
- Reopen activates existing form.

## Scenario B: ModernDiagram Entry

1. Open the same target component in ModernDiagram.
2. Use context menu `GUI`.
3. Verify it opens the same expected controller form.
4. Repeat action and verify single-instance reuse.

Expected:
- Same form behavior as DrawEngine path.

## Scenario C: ComponentsList Entry

1. Open ComponentsList.
2. Select same target component.
3. Trigger `GUI` action from list entrypoint.
4. Verify expected controller opens and reopens as single-instance.

Expected:
- Same form and lifecycle behavior as other entrypoints.

## Scenario D: Unregistered Class Fallback

1. Select a component class that has no dedicated registration.
2. Trigger `GUI` action from any entrypoint.
3. Verify deterministic user-facing fallback message.

Expected:
- No crash, no undefined behavior.
- Informative fallback message is shown.

## Scenario E: Session Restore (ComponentGuiLayout)

1. Open at least 3 component GUI forms from mixed entrypoints.
2. Keep one in MDI, detach one to floating, place one into grid container.
3. Save project, close project, reopen project.
4. Verify session composition is restored from `Interface.xml` section `ComponentGuiLayout`.

Expected:
- Same component forms are reopened.
- Host modes are preserved (`mdi`, `floating`, `grid`).

## Scenario F: Floating Window Visual Restore

1. Put a component GUI into floating mode.
2. Change position/size/window state.
3. Save project, close, reopen.
4. Verify restored geometry/state.

Expected:
- Floating window appears with previously saved visual parameters from `settings.qt`.

## Scenario G: Grid Splitter Restore

1. Create/resize grid rows and columns.
2. Assign components to multiple cells.
3. Save project, close, reopen.
4. Verify splitter sizes are restored.

Expected:
- Root/row splitter states match saved layout.

## Evidence Template

Fill and append to this file after execution:

```text
Execution Timestamp:
Operator:
Environment:
Project/Config:

Scenario A (DrawEngine): PASS/FAIL
Notes:

Scenario B (ModernDiagram): PASS/FAIL
Notes:

Scenario C (ComponentsList): PASS/FAIL
Notes:

Scenario D (Unregistered fallback): PASS/FAIL
Notes:

Scenario E (Session Restore): PASS/FAIL
Notes:

Scenario F (Floating Visual Restore): PASS/FAIL
Notes:

Scenario G (Grid Splitter Restore): PASS/FAIL
Notes:

Overall Result: GO / CONDITIONAL GO / NO-GO
Follow-up Actions (if any):
```

## Completion Rule

After all scenarios PASS:
1. Mark section "Manual Final Smoke (Release Gate)" as completed in `Reports/comp_gui_release_checklist.md`.
2. Update `Go / No-Go` to `GO`.
3. Add short evidence summary in `Reports/comp_gui_closure_report.md`.

---

## Execution Evidence (latest run)

Execution Timestamp: 2026-05-06 (UTC+3)  
Operator: Codex (automated stage execution)  
Environment: Linux 6.8 / headless CI-like shell environment  
Project/Config: `/home/user/Nmsdk`

Automated preconditions:
- PASS: `cmake --build build --target NeuroModeler -j4`
- PASS: `cmake --build build-core-only --target NeuroModelerConsole -j4`
- PASS: `cmake --build build-motion-off --target NeuroModeler -j4`
- PASS: `cmake --build build-pulse-off --target NeuroModeler -j4`
- PASS: preset smoke flow  
  `cmake --preset linux-gcc-debug-tests`  
  `cmake --build --preset linux-gcc-debug-tests`  
  `ctest --preset linux-component-gui-registry`
- PASS (launch smoke): `timeout 8s env QT_QPA_PLATFORM=offscreen ./Bin/Platform/Linux/NeuroModeler` reached active event loop and was terminated by timeout (`exit 124`).

Scenario A (DrawEngine): NOT EXECUTED (manual GUI interaction required)  
Notes: Requires interactive runtime actions in application UI.

Scenario B (ModernDiagram): NOT EXECUTED (manual GUI interaction required)  
Notes: Requires interactive runtime actions in application UI.

Scenario C (ComponentsList): NOT EXECUTED (manual GUI interaction required)  
Notes: Requires interactive runtime actions in application UI.

Scenario D (Unregistered fallback): NOT EXECUTED (manual GUI interaction required)  
Notes: Requires interactive runtime actions in application UI.

Overall Result: CONDITIONAL GO  
Follow-up Actions: complete scenarios A/B/C/D in interactive session and then update checklist status to full GO.

---

## Execution Evidence (manual follow-up)

Execution Timestamp: 2026-05-06 (UTC+3)  
Operator: user (interactive GUI run)  
Environment: Linux desktop runtime, real `NeuroModeler` UI session  
Project/Config: interactive project with `NNeuronTrainer`

Scenario A (DrawEngine): PASS  
Notes: `GUI` action opens dedicated form in MDI host. Repeated `GUI` action switches to existing GUI tab; no duplicate form instance.

Scenario B (ModernDiagram): NOT EXECUTED  
Notes: No explicit user confirmation in this run.

Scenario C (ComponentsList): NOT EXECUTED  
Notes: No explicit user confirmation in this run.

Scenario D (Unregistered fallback): NOT EXECUTED  
Notes: No explicit user confirmation in this run.

Overall Result: CONDITIONAL GO  
Follow-up Actions: complete scenarios B/C/D and then switch checklist to full GO.
