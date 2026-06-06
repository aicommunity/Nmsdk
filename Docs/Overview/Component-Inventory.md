# Component Inventory (Libraries/* registration in UStorage)

## RU

Сводный список классов, регистрируемых через `UploadClass(...)` / `CreateClassSamples(...)` в библиотеках `Libraries/*`. Получено автоматически по исходникам (`Core/*.cpp|*.h`). Повторяющиеся псевдонимы сохранены для трассировки.

## Rdk-BasicLib
- UBCLLibrary.cpp: `UModel`, `UStatisticIntMatrix`, `UStatisticDoubleMatrix`, `UFileIO`, `UIOTextConverter`, `UNoiseGenDouble`, `UNoiseGen`, `UNoiseGenInt`, `UMatrixSource`, `UScalarSource`, `UMatrixSourceTimeSeries`, `UMatrixSourceDataFile`, `UUMatrixSourceFile`, `UMatrixSourceFileSep`, `UFileDataset`
- UIOLibrary.cpp: `UFileIO`, `UIOTextConverter`

## Rdk-CvBasicLib
- Basic.cpp: `ColorConvert`, `ResizeEdges`, `RotateSimple`, `Model`, `Pipeline`, `ParallelPipeline`, `Source`, `SourceFile`, `SourceMultiFile`, `Receiver`, `Crop`, `Reduce`, `UBAFlipImageSimple`, `UMDMatrixDoubleMux`, `UMDMatrixIntMux`, `BMathOperator`, `UMatrixIntMath`, `UMatrixDoubleMath`, `UMDScalarDoubleMux`, `UMDScalarIntMux`, `DifferenceFrameSimple`, `BackgroundAvg`, `TBinarizationSimple`, `TBinarizationSimpleAdaptiveThreshold`, `TLabelingSimple`, `BackgroundExponnential`, `DeltaBackgroundExponnential`, `BackgroundSimpleAdaptive`, `UBABinarizationOtsu`, `UBABackgroundDependDiff`, `UBShowRect`, `ShowObjectsSimple`, `VideoSimulatorSimple`, `RotCameraSimulator`, `VideoSimulatorSimpleBin`, `Video3DSimulatorSimple`, `DataSimulatorSimple`, `BitmapSourceSimple`, `BitmapSourceFile`, `BStatisticSimple`, `UCRPerseptron`, `UCRDirectCompare`, `UCRDistance`, `UCRFusion`, `UCRSample`, `UCRTeacherPerseptronBP`, `UCRTeacherPerseptronDL`, `UCRConvolutionNetwork`, `UCRTeacherCVNetworkBP`, `UClassifierBase`, `UDetectorBase`, `USegmentatorBase`, `UClassifierResSaver`, `UDetResSaverPVOC`, `UCRPrincipalComponentAnalysis`, `UCRBarnesHutTSNE`, `TCaptureImageSequence`, `Capture`

## Rdk-HardwareLib
- UHardwareLibrary.cpp: `ArduinoBoard`, `ArduinoSensorSketch`, `ArduinoFirmata`, `ArduinoAdc`, `ArduinoDcDemo`
- Legacy names `Arduino`, `ADC`, `DC` — см. [Rdk-HardwareLib Component-Catalog](../../Libraries/Rdk-HardwareLib/Docs/Component-Catalog.md)


## Nmsdk-PulseLib
- NPulseLibrary.cpp: **177** зарегистрированных классов (`UploadClass`) — полный список: [Component-Catalog](../../Libraries/Nmsdk-PulseLib/Docs/Component-Catalog.md), отчёт: [Docs/Audit/Component-Gap-Report.md](../Audit/Component-Gap-Report.md)
- Семейства: `NPulseNeuron*`, `NSynapse*`, `NPulseChannel*`, `NNeuron*`, `N*Trainer*`, `N*Classifier*`, `N*Membrane*`, `N*LTZone*`, `N*Generator*`, `N*Predictor*`, `N*Stdp*`

## Nmsdk-MotionControlLib
- NMotionControlLibrary.cpp: `NDCEngine`, `NPendulumAndCart`, `NAstaticGyro`, `NManipulatorAndGyro`, `NManipulator`, `NNavMousePrimitive`, `NFrequencyReceiver`, `NManipulatorInput`, `NManipulatorInputEmulator`, `NSimpleStatistic`, `NNetworkLinksStatistic`, `NPulseReceiver`, `NSignumSeparator`, `NIntervalSeparator`, `NPosSignumSeparator`, `NNegSignumSeparator`, `NEyeRetina`, `NManipulatorSourceEmulator`, `NManipulatorSource`, `NControlObjectSource`, `NSuppressionUnit`, `NCounterNeuron`, `NObjInArea`, `NSeqComparison`, `NActuatorSignals`, `NSignalEstimation`, `NNewMotionElement`, `NEngineMotionControl`, `NEngineControlSignumAfferent`, `NEngineControlRangeAfferent`, `N2AsfNewSimplestAfferentBranchedEngineControl`, `NPositionControlElement`, `NNewPositionControlElement`, `NMultiPositionControl`, `NTrajectoryElement`, `NMazeMemory`, `NMazeMemorySimplified`, `NPCN`
- NWinAPIActLibrary.cpp: `NWPhysicalManipulator`

---

## EN

Summary list of classes registered via `UploadClass(...)` / `CreateClassSamples(...)` in libraries `Libraries/*`. Generated automatically from source files (`Core/*.cpp|*.h`). Duplicate aliases are kept for traceability.

## Rdk-BasicLib

- UBCLLibrary.cpp: `UModel`, `UStatisticIntMatrix`, `UStatisticDoubleMatrix`, `UFileIO`, `UIOTextConverter`, `UNoiseGenDouble`, `UNoiseGen`, `UNoiseGenInt`, `UMatrixSource`, `UScalarSource`, `UMatrixSourceTimeSeries`, `UMatrixSourceDataFile`, `UUMatrixSourceFile`, `UMatrixSourceFileSep`, `UFileDataset`
- UIOLibrary.cpp: `UFileIO`, `UIOTextConverter`

## Rdk-CvBasicLib

- Basic.cpp: `ColorConvert`, `ResizeEdges`, `RotateSimple`, `Model`, `Pipeline`, `ParallelPipeline`, `Source`, `SourceFile`, `SourceMultiFile`, `Receiver`, `Crop`, `Reduce`, `UBAFlipImageSimple`, `UMDMatrixDoubleMux`, `UMDMatrixIntMux`, `BMathOperator`, `UMatrixIntMath`, `UMatrixDoubleMath`, `UMDScalarDoubleMux`, `UMDScalarIntMux`, `DifferenceFrameSimple`, `BackgroundAvg`, `TBinarizationSimple`, `TBinarizationSimpleAdaptiveThreshold`, `TLabelingSimple`, `BackgroundExponnential`, `DeltaBackgroundExponnential`, `BackgroundSimpleAdaptive`, `UBABinarizationOtsu`, `UBABackgroundDependDiff`, `UBShowRect`, `ShowObjectsSimple`, `VideoSimulatorSimple`, `RotCameraSimulator`, `VideoSimulatorSimpleBin`, `Video3DSimulatorSimple`, `DataSimulatorSimple`, `BitmapSourceSimple`, `BitmapSourceFile`, `BStatisticSimple`, `UCRPerseptron`, `UCRDirectCompare`, `UCRDistance`, `UCRFusion`, `UCRSample`, `UCRTeacherPerseptronBP`, `UCRTeacherPerseptronDL`, `UCRConvolutionNetwork`, `UCRTeacherCVNetworkBP`, `UClassifierBase`, `UDetectorBase`, `USegmentatorBase`, `UClassifierResSaver`, `UDetResSaverPVOC`, `UCRPrincipalComponentAnalysis`, `UCRBarnesHutTSNE`, `TCaptureImageSequence`, `Capture`

## Rdk-HardwareLib

- UHardwareLibrary.cpp: `ArduinoBoard`, `ArduinoSensorSketch`, `ArduinoFirmata`, `ArduinoAdc`, `ArduinoDcDemo`
- Legacy names `Arduino`, `ADC`, `DC` — see [Rdk-HardwareLib Component-Catalog](../../Libraries/Rdk-HardwareLib/Docs/Component-Catalog.md)

## Nmsdk-PulseLib

- NPulseLibrary.cpp: **177** registered classes (`UploadClass`) — full list: [Component-Catalog](../../Libraries/Nmsdk-PulseLib/Docs/Component-Catalog.md), report: [Docs/Audit/Component-Gap-Report.md](../Audit/Component-Gap-Report.md)
- Families: `NPulseNeuron*`, `NSynapse*`, `NPulseChannel*`, `NNeuron*`, `N*Trainer*`, `N*Classifier*`, `N*Membrane*`, `N*LTZone*`, `N*Generator*`, `N*Predictor*`, `N*Stdp*`

## Nmsdk-MotionControlLib

- NMotionControlLibrary.cpp: `NDCEngine`, `NPendulumAndCart`, `NAstaticGyro`, `NManipulatorAndGyro`, `NManipulator`, `NNavMousePrimitive`, `NFrequencyReceiver`, `NManipulatorInput`, `NManipulatorInputEmulator`, `NSimpleStatistic`, `NNetworkLinksStatistic`, `NPulseReceiver`, `NSignumSeparator`, `NIntervalSeparator`, `NPosSignumSeparator`, `NNegSignumSeparator`, `NEyeRetina`, `NManipulatorSourceEmulator`, `NManipulatorSource`, `NControlObjectSource`, `NSuppressionUnit`, `NCounterNeuron`, `NObjInArea`, `NSeqComparison`, `NActuatorSignals`, `NSignalEstimation`, `NNewMotionElement`, `NEngineMotionControl`, `NEngineControlSignumAfferent`, `NEngineControlRangeAfferent`, `N2AsfNewSimplestAfferentBranchedEngineControl`, `NPositionControlElement`, `NNewPositionControlElement`, `NMultiPositionControl`, `NTrajectoryElement`, `NMazeMemory`, `NMazeMemorySimplified`, `NPCN`
- NWinAPIActLibrary.cpp: `NWPhysicalManipulator`

---
