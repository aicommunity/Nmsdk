# comp_gui: Next Execution Plan (Stage 2 Hardening)

## Goal
Close remaining quality and rollout risks after formal debt closure by converting "agreed limitations" into validated behavior with strict evidence (`Code + Tests + Build + UX`).

## Scope
- DrawEngine entrypoint behavior for component GUI.
- Integration tests for full component GUI pipeline across entrypoints.
- Parity hardening for priority forms (`Manipulator`, `NeuronLearner`, `NeuronTrainer`).
- Controlled reopen/reclose of technical debt items with measurable exit criteria.
- Documentation synchronization (`matrix`, `technical_debt`, `closure_report`).

## Branch and Commit Policy
- Work in `comp_gui` branch in root and related subrepos.
- Atomic commits only, English messages only.
- Recommended prefixes:
  - `feat(comp-gui): ...`
  - `test(comp-gui): ...`
  - `docs(comp-gui): ...`
  - `build(comp-gui): ...`
  - `refactor(comp-gui): ...`

## Execution Flow (Risk-Minimized)

### Phase A - DrawEngine Routing (first, low blast radius)
1. Add explicit signal path from `UDrawEngineImageWidget` to the same component-GUI service contract as `ModernDiagram/ComponentsList`.
2. Build `UComponentGuiContext` with:
   - `componentLongName`
   - `componentClassName`
   - `channelIndex` (current selected channel when available)
3. Route request to `UGEngineControlWidget::openComponentGuiFromScheme`.
4. Keep user-facing fallback for unregistered classes ("No GUI form is registered...").

Acceptance:
- DrawEngine context-menu action "GUI" calls the same opening path as other entrypoints.
- Single-instance behavior is preserved (second open activates existing form).

### Phase B - Integration Test Target (second, confidence multiplier)
1. Introduce dedicated integration test target for component GUI pipeline.
2. Cover at minimum:
   - Diagram entrypoint open.
   - ComponentsList entrypoint open.
   - DrawEngine entrypoint open.
   - Reopen for `singleInstance=true`.
   - Unregistered class fallback (`nullptr` / info message path).
3. Ensure tests can run in CI-friendly mode.

Acceptance:
- New tests pass locally and in configured build presets.
- No regressions in existing unit tests.

### Phase C - Priority Parity Hardening (third, focused functional depth)
1. Re-check `MotionControlManipulatorComponentControllerWidget` against legacy behavior map.
2. Re-check `PulseLibNeuronLearnerComponentControllerWidget` and `PulseLibNeuronTrainerComponentControllerWidget` for runtime refresh/edit consistency.
3. For each known unsupported legacy control:
   - either implement now, or
   - keep disabled with explicit UX explanation and matrix evidence.

Acceptance:
- Priority forms move to `ported_real` where fully justified.
- Any remaining `ported_partial` entries are explicit, testable, and documented.

### Phase D - Debt Revalidation and Formal Close (fourth, governance)
1. Reopen only relevant TD records affected by this stage (if needed).
2. Attach evidence links per item:
   - code paths
   - tests
   - build profiles
   - UX behavior
3. Close TD items only when all acceptance checks pass.

Acceptance:
- No "closed by agreement only" entries without technical evidence.

### Phase E - Final Sync (last)
1. Update:
   - `Reports/comp_gui_bcb_qt_matrix.md`
   - `Reports/comp_gui_technical_debt.md`
   - `Reports/comp_gui_closure_report.md`
2. Add concise delta section: "what changed in this stage".
3. Prepare final verification run and summary.

Acceptance:
- Docs, code, and tests are consistent.
- Final status is reproducible from repository state.

## Verification Matrix
- Build profiles:
  - default GUI build
  - core-only profile
  - `NO_MOTION_CONTROL`
  - `NO_PULSELIB`
- Tests:
  - existing unit tests
  - new integration pipeline tests
- Manual smoke:
  - open component GUI from each entrypoint
  - verify single-instance activation
  - verify unregistered-class behavior

## Commit Plan (suggested sequence)
1. `feat(comp-gui): route DrawEngine component GUI to shared service path`
2. `test(comp-gui): add integration coverage for component GUI entrypoints`
3. `feat(comp-gui): harden priority forms parity and fallback UX`
4. `docs(comp-gui): revalidate debt statuses and sync closure evidence`

## Definition of Done
- Entry-point parity achieved across `ModernDiagram`, `ComponentsList`, and `DrawEngine`.
- Integration tests cover all key open/reopen/fallback scenarios.
- Priority forms are either fully ported or explicitly constrained with documented and tested behavior.
- Technical debt and closure artifacts are evidence-based and synchronized.

## Release Gate Artifact
- `Reports/comp_gui_release_checklist.md` is the canonical final go/no-go checklist for release-readiness.
