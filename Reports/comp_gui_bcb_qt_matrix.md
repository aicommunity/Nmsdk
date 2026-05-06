# BCB -> Qt Component Form Migration Matrix

## Legend
- `QtStatus`: `ported_placeholder`, `ported_real`, `ported_partial`, `planned`, `not_started`
- `Priority`: `A` (first wave), `B` (later)

| ComponentClass | LegacyBCBForm | TargetModule | QtStatus | Priority | BehaviorContract |
|---|---|---|---|---|---|
| NAslsNewSimplestAfferentBranchedEngineControlPM | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| NAsfNewSimplestAfferentBranchedEngineControlPM | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| NAslsNewSimplestAfferentBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| NAsfNewSimplestAfferentBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| NNewSimplestAfferentBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| NSimplestAfferentBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| NSimplestBranchedEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| NSimplestEngineControl | TNManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| N2AsfNewSimplestAfferentBranchedEngineControl | TNewManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| N2AsfSimplestAfferentBranchedEngineControl | TNewManipulatorControlForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; partial parity for model controls (`NumMotionElements`, `NumControlLoops`, PAC, active contours, II afferent, stats, moment/movement) |
| NNewPositionControlElement | TNNewPositionControlElementForm | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_real | A | open by class from context menu; single instance per component; grid reflects generator/learned state and editable generator frequencies |
| NAstaticGyro | TNAstaticGyro | Libraries/Nmsdk-MotionControlLib/GUI/Qt | ported_real | A | open by class from context menu; single instance per component; displays alpha/betta/gamma (rad + deg) from the model |
| NNeuronTrainer | TNNeuronTrainerForm | Libraries/Nmsdk-PulseLib/GUI/Qt | ported_partial | A | open by class from context menu; single instance per component; edits trainer parameters via component properties; UI parity is partial |
| NNeuronLearner | (no final BCB GUI parity yet) | Libraries/Nmsdk-PulseLib/GUI/Qt | ported_partial | B | open by class from context menu; single instance per component; dedicated Qt controller supports main learner parameters and reset/calculate actions |
| NCvImageSource | CvBasic generic panel | Libraries/Rdk-CvBasicLib/GUI/Qt | ported_partial | B | open by class from context menu; single instance per component; generic inspector widget is used |
| NHardwareDevice | Hardware generic panel | Libraries/Rdk-HardwareLib/GUI/Qt | ported_partial | B | open by class from context menu; single instance per component; generic inspector widget is used |
| NModel | Core/Basic inspector | Rdk/GUI/Qt + Libraries/Rdk-BasicLib/GUI/Qt | ported_partial | B | open by class from context menu; single instance per component; generic inspector widget is used |
| UNet | Core inspector | Rdk/GUI/Qt | ported_partial | B | reference form for pipeline validation with generic inspector widget |

## Notes
- Current phase focuses on infrastructure and opening path.
- Placeholder forms are intentionally lightweight and tracked in technical debt.
