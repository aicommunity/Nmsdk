# BCB -> Qt Component Form Migration Matrix

## Legend
- `QtStatus`: `ported_placeholder`, `planned`, `not_started`
- `Priority`: `A` (first wave), `B` (later)

| ComponentClass | LegacyBCBForm | TargetModule | QtStatus | Priority | BehaviorContract |
|---|---|---|---|---|---|
| NAslsNewSimplestAfferentBranchedEngineControlPM | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NAsfNewSimplestAfferentBranchedEngineControlPM | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NAslsNewSimplestAfferentBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NAsfNewSimplestAfferentBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NNewSimplestAfferentBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NSimplestAfferentBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NSimplestBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NSimplestEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| N2AsfNewSimplestAfferentBranchedEngineControl | TNewManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| N2AsfSimplestAfferentBranchedEngineControl | TNewManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NNewPositionControlElement | TNNewPositionControlElementForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NAstaticGyro | TNAstaticGyro | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NNeuronTrainer | TNNeuronTrainerForm | Libraries/Nmsdk-PulseLib/GUI/Qt | ported_placeholder | A | open by class from context menu; single instance per component |
| NNeuronLearner | (no final BCB GUI parity yet) | Libraries/Nmsdk-PulseLib/GUI/Qt | ported_placeholder | B | open by class from context menu; single instance per component |
| NModel | Core inspector | Rdk/GUI/Qt | ported_placeholder | B | reference form for pipeline validation |
| UNet | Core inspector | Rdk/GUI/Qt | ported_placeholder | B | reference form for pipeline validation |

## Notes
- Current phase focuses on infrastructure and opening path.
- Placeholder forms are intentionally lightweight and tracked in technical debt.
