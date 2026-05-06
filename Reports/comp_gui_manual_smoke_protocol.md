# comp_gui Manual Final Smoke Protocol

Purpose: execute the final release gate from `Reports/comp_gui_release_checklist.md` and produce auditable evidence for switching `CONDITIONAL GO` -> `GO`.

## Preconditions

- Branch: `comp_gui` (root + relevant subrepos).
- Build is successful for verification profiles (`build`, `build-core-only`, `build-motion-off`, `build-pulse-off`).
- Preset smoke test is green:
  - `cmake --preset linux-gcc-debug-tests`
  - `cmake --build --preset linux-gcc-debug-tests`
  - `ctest --preset linux-component-gui-registry`

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

Overall Result: GO / CONDITIONAL GO / NO-GO
Follow-up Actions (if any):
```

## Completion Rule

After all scenarios PASS:
1. Mark section "Manual Final Smoke (Release Gate)" as completed in `Reports/comp_gui_release_checklist.md`.
2. Update `Go / No-Go` to `GO`.
3. Add short evidence summary in `Reports/comp_gui_closure_report.md`.
