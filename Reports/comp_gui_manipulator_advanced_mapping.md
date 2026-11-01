# Manipulator Advanced Mapping (BCB -> Qt)

This mapping tracks parity migration for `TNManipulatorControlForm` and `TNewManipulatorControlForm`.

## Mapping Table

| Legacy control/action | Qt widget/action | Model/property binding | Status |
|---|---|---|---|
| `NumMotionElementsTrackBarChange` | `m_numMotionElementsSlider` | `NEngineMotionControl::NumMotionElements` | done |
| `NumControlLoopsTrackBarChange` | `m_numControlLoopsSlider` | `NEngineMotionControl::NumControlLoops` | done |
| `IIAfferentTrackBarChange` | `m_iiAfferentSlider` | `SetInternalGeneratorFrequency(...)` | done |
| `IINumAfferentTrackBarChange` | `m_iiNumAfferentSlider` | `ConnectInternalGenerators(...)` | done |
| `PACMultiplicatorTrackBarChange` | `m_pacGainSlider` | `NEngineMotionControl::PacGain` | done |
| `PACActivatorTimeTrackBarChange` | `m_pacSecretionSlider` | `NEngineMotionControl::PacSecretionTC` | done |
| `PACDeactivatorTimeTrackBarChange` | `m_pacDissociationSlider` | `NEngineMotionControl::PacDissociationTC` | done |
| `SensorDivisionComboBoxChange` | `m_sensorDivisionCombo` | `NEngineMotionControl::AfferentRangeMode` | done |
| `CheckListBox1Click` (active contours) | contour checkboxes | `NEngineMotionControl::ActiveContours` | done |
| `MomentTrackBarChange` | `m_momentSlider` | `NDCEngine::OutMoment`, `NPendulumAndCart::ExtrenalMoment` | done |
| `MovementControlTrackBarChange` | `m_movementSlider` | `NPendulumAndCart::OutXMovement` | done |
| `ControlVoltageCheckBoxClick` | `m_controlVoltageCheck` | create/break `NManipulatorInput1` link | done |
| `SaveStatsButtonClick` | `m_saveStatsButton` | `StatisticDoubleMatrix.ManualModeSwitch=true` | done |
| `NewStatsButtonClick` | `m_newStatsButton` | `ManualModeSwitch=false`, `ManualModeEnabled=true`, `Reset()` | done |
| `BranchModeCheckBoxClick` | `m_branchModeCheck` | `NEngineMotionControl::MotoneuronBranchMode` | done |
| `RenshowCellsCheckBoxClick` | `m_renshowModeCheck` | `NEngineMotionControl::RenshowMode` | done |
| `EnableStructuralAdaptationCheckBoxClick` | `m_structuralAdaptationCheck` | `NEngineMotionControl::AdaptiveStructureMode` | done |
| `UseSimpleAfferentsCheckBoxClick` | disabled checkbox in Qt | no stable cross-platform equivalent in current Qt path | explicitly_not_supported |
| `UseNewNeuronsCheckBoxClick` | disabled checkbox in Qt | no stable cross-platform equivalent in current Qt path | explicitly_not_supported |
| Hardware controls (`LoadManipulatorDll`, `DMStart/Stop/Reset`, `DMMoveServo`) | disabled hardware buttons in Qt | WinAPI hardware path not available in Linux build | explicitly_not_supported |

## Notes

- `explicitly_not_supported` controls are intentionally visible but disabled in Qt with explanatory tooltips.
- Remaining parity gap is documented in `Reports/comp_gui_technical_debt.md` (`TD-001`).
