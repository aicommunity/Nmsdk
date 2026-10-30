# Regression Validation Report

## Validation matrix

## 1) parity-threshold
- Goal: ensure parity of threshold application semantics between `NNeuronLearner` and `NNeuronTrainer`.
- Coverage status: **code-level validated**
  - Trainer now applies threshold via centralized path that updates both property and runtime LTZone.
  - Learner and Trainer both apply training/fixed threshold transitions through explicit setter flows.

## 2) timing-sensitivity
- Goal: prevent unstable iteration-length behavior from invalid timing boundaries.
- Coverage status: **code-level validated**
  - Safe iteration-length helpers added in both classes.
  - Boundary conditions now clamp to a positive minimal iteration length.

## 3) naming-invariants
- Goal: reduce fragility of string-based component addressing.
- Coverage status: **partially implemented**
  - Canonical naming helpers introduced and applied in high-risk Trainer mode-6 paths.
  - Learner high-risk addressing points partially migrated to helper paths.

## 4) threshold-regression
- Goal: verify no silent threshold drift during train/recognition switching.
- Coverage status: **code-level validated**
  - Unified threshold writes now set property and LTZone consistently in Trainer.

## 5) debug-equivalence
- Goal: debug flag should not alter algorithmic outcome.
- Coverage status: **design-level validated**
  - New code does not introduce state mutations under debug-only branches.

## Unit-level additions

- Added test:
  - `Rdk/Tests/Unit/Engine/UProperty/Test_UProperty_DirectUpdateVisibility.cpp`
- Registered in:
  - `Rdk/Tests/Unit/Engine/UProperty/CMakeLists.txt`

## Rdk-BasicLib gate result

- Gate condition for `Rdk-BasicLib` changes: **not triggered**.
- Phase marked as **skipped**.

## Residual risk

- Full runtime parity validation across multiple real project configs still recommended after integration build and environment-level execution.

