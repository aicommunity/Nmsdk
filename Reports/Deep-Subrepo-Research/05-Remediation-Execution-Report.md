# Remediation Execution Report

## Scope

- Branch: `training_test`
- Repositories:
  - `Libraries/Nmsdk-PulseLib`
  - `Rdk`
  - `Libraries/Rdk-BasicLib` (gate-based, skipped)
  - root `Nmsdk` (final consolidation step)

## Implemented decisions

1. **LTZ threshold contract unification (Trainer)**
   - Added centralized threshold application path in `NNeuronTrainer`:
     - property update via `SetDataDirect`
     - immediate application to runtime `LTZone->Threshold`
   - Updated flows:
     - `SetLTZThreshold`
     - `SetUseFixedLTZThreshold`
     - `SetNeedToTrain`
     - training-start branch in `CalculateProcess`

2. **Timing stabilization**
   - Added safe iteration-length calculation in:
     - `NNeuronTrainer` (`GetSafeIterationLength`)
     - `NNeuronLearner` (local safe helper)
   - Added guard behavior for invalid boundary conditions (`TimeStep<=0`, non-positive derived length).

3. **Mode-6 state isolation in Trainer**
   - Kept legacy modes (`0..5`) algorithmically unchanged.
   - Marked mode `6` as the primary maintained training path and isolated behavior accordingly.

4. **Structural naming invariants**
   - Added canonical naming helpers in `NNeuronTrainer`:
     - `MakeSourceName`
     - `MakeSomaName`
     - `MakeDendriteName`
     - `MakeExcSynapsePath`
   - Applied helper-based addressing in key mode-6 mutation paths.
   - Added partial helper usage in `NNeuronLearner` for high-risk link and component addressing paths.

5. **Rdk property regression coverage**
   - Added direct update visibility test for `UProperty::SetDataDirect`.
   - Registered test target in UProperty unit-test CMake.

## Deferred / skipped by rule

- `Libraries/Rdk-BasicLib` changes were **not** applied because gate condition was not triggered:
  - No confirmed localization of current issues to data-source normalization/indexing layer after PulseLib/Rdk fixes.

