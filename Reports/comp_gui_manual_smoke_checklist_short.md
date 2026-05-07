# comp_gui Manual Smoke Checklist (Short)

Estimated time: 2-3 minutes.

## 1. Prepare

- Start `NeuroModeler`.
- Open a real project/config with at least one component that has a registered GUI form (for example: `NNeuronTrainer`, `NNeuronLearner`, `NAstaticGyro`, or a manipulator class).

## 2. DrawEngine Entry

- In DrawEngine, right-click the selected component and choose `GUI`.
- Verify the form opens.
- Trigger `GUI` again for the same component.
- Verify single-instance behavior: existing form is activated, no duplicate window appears.

## 3. ModernDiagram Entry

- Select the same component in ModernDiagram.
- Open `GUI` from context menu.
- Verify the same expected form opens.
- Trigger `GUI` again and verify single-instance reuse (no duplicate).

## 4. ComponentsList Entry

- Select the same component in ComponentsList.
- Trigger `GUI`.
- Verify the form opens/activates with behavior equivalent to DrawEngine and ModernDiagram.

## 5. Unregistered-Class Fallback

- Select a component class without dedicated registration.
- Trigger `GUI`.
- Verify deterministic user-facing info message is shown.
- Verify there is no crash or undefined behavior.

## 6. Finalize Evidence

- Fill results in `Reports/comp_gui_manual_smoke_protocol.md` (PASS/FAIL + notes + date + operator).
- Mark manual smoke items completed in `Reports/comp_gui_release_checklist.md`.
- If all scenarios pass, switch overall status to `GO`.

## 7. DnD + Grid UX

- Drag MDI component GUI tab outside window -> verify floating detach.
- Drag floating component GUI by left drag-handle onto MDI header area -> verify attach back to MDI on release.
- Drag floating component GUI by left drag-handle into grid cell -> verify placement.
- Drag component GUI from grid cell back to MDI header area -> verify source cell is cleared after successful attach.
- Trigger `Move to Grid...` and select existing grid -> verify no repeated rows/cols prompt.
- Trigger `Window -> Component GUI Grid...` -> verify single dialog is used.
