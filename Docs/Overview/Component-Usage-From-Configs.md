# Component Usage from Bin/ClDesc and Bin/Configs

## RU

Быстрый срез того, какие компоненты реально встречаются в `Bin/ClDesc/**` и `Bin/Configs/**` (по тегам/атрибутам `Class` / `ClassName`). Можно использовать для приоритезации документации и примеров.

## Источники
- `Bin/ClDesc/**` — найдено 243 уникальных `ClassName`.
- `Bin/Configs/**` — найдено 170 уникальных `Class` / `ClassName`.

## Пересечение (примеры ключевых семейств)
- Базовые/математика/видео: `UMatrixSource*`, `UStatistic*`, `UNoiseGen*`, `ColorConvert`, `Crop`, `Reduce`, `TBinarizationSimple`, `UCR*` (PCA/TSNE/персептрон и т.д.), `VideoSimulatorSimple`, `RotCameraSimulator`, `BStatisticSimple`.
- SNN / PulseLib: огромный перечень нейронов/синапсов/каналов/мембран/тренеров, включая `NPulseNeuron*`, `NSynapse*`, `NPulseChannel*`, `NNeuron*`, `N*Trainer*`, `N*Membrane*`, `N*LTZone*`, `N*Generator*`, `N*Predictor*`, `N*Life*`, `N*Hebb*`, `N*Stdp*`, `NClassifier`, `NSpikeClassifier`, `NPCAClassifier`.
- MotionControlLib: `NDCEngine`, `NEngineMotionControl`, `NManipulator*`, `NEyeRetina`, `NPendulumAndCart`, `NMultiPositionControl`, `NTrajectoryElement`, `NPulseReceiver`, `NFrequencyReceiver`, `NMazeMemory*`, `NSignumSeparator/IntervalSeparator`, `NActuatorSignals`, `NSignalEstimation`, `NPCN`.
- HardwareLib: `Arduino`, `ADC`, `DC`.

## Где совпадает регистрация и использование (приоритет для подробной документации)
- Rdk-BasicLib / CvBasicLib: большинство классов, встречающихся в конфигах, зарегистрированы (см. `Docs/Overview/Component-Inventory.md`).
- Nmsdk-PulseLib: значительная часть длинного списка из регистрации фигурирует в `Configs`/`ClDesc`; приоритет — ядро (нейроны/синапсы/каналы, тренировочные компоненты, классификаторы).
- Nmsdk-MotionControlLib: основные контроллеры/сенсоры/эффекторы и навигация встречаются в `Configs`.
- HardwareLib: базовые `Arduino/ADC/DC` — есть в регистрациях, встречаются в описаниях, но в `Configs` явно не подсвечены (возможна интеграция через другие файлы).

## Наблюдения и рекомендации
1. **Фокус первых итераций** — компоненты, реально встречающиеся в `Configs/ClDesc` (выше перечислены основные семьи). Для них нужны: полное описание, диаграммы, примеры конфигов.
2. **SNN и Motion Control** — большие семейства; стоит группировать по семействам (нейроны, синапсы, каналы, тренеры, классификаторы, рефлексы, предикторы) и покрывать их батчами.
4. **Оставить след использования** — в документации компонентов указывать примеры из `Bin/Configs` (для сабрепо — текст пути, для корня — активная ссылка).

Эта выжимка нужна для этапов группировки и приоритезации в библиотечных проходах.

---

## EN

A quick snapshot of which components actually appear in `Bin/ClDesc/**` and `Bin/Configs/**` (by `Class` / `ClassName` tags/attributes). Use for prioritizing documentation and examples.

## Sources
- `Bin/ClDesc/**` — 243 unique `ClassName` values found.
- `Bin/Configs/**` — 170 unique `Class` / `ClassName` values found.

## Overlap (key families)
- Basic/math/video: `UMatrixSource*`, `UStatistic*`, `UNoiseGen*`, `ColorConvert`, `Crop`, `Reduce`, `TBinarizationSimple`, `UCR*` (PCA/TSNE/perceptron, etc.), `VideoSimulatorSimple`, `RotCameraSimulator`, `BStatisticSimple`.
- SNN / PulseLib: large set of neurons/synapses/channels/membranes/trainers, including `NPulseNeuron*`, `NSynapse*`, `NPulseChannel*`, `NNeuron*`, `N*Trainer*`, `N*Membrane*`, `N*LTZone*`, `N*Generator*`, `N*Predictor*`, `N*Life*`, `N*Hebb*`, `N*Stdp*`, `NClassifier`, `NSpikeClassifier`, `NPCAClassifier`.
- MotionControlLib: `NDCEngine`, `NEngineMotionControl`, `NManipulator*`, `NEyeRetina`, `NPendulumAndCart`, `NMultiPositionControl`, `NTrajectoryElement`, `NPulseReceiver`, `NFrequencyReceiver`, `NMazeMemory*`, `NSignumSeparator/IntervalSeparator`, `NActuatorSignals`, `NSignalEstimation`, `NPCN`.
- HardwareLib: `Arduino`, `ADC`, `DC`.

## Where registration and usage align (priority for detailed docs)
- Rdk-BasicLib / CvBasicLib: most classes seen in configs are registered (see `Docs/Overview/Component-Inventory.md`).
- Nmsdk-PulseLib: a large part of the long registration list appears in `Configs`/`ClDesc`; priority — core (neurons/synapses/channels, training components, classifiers).
- Nmsdk-MotionControlLib: main controllers/sensors/effectors and navigation appear in `Configs`.
- HardwareLib: basic `Arduino/ADC/DC` — registered, appear in descriptions, but not highlighted explicitly in `Configs` (integration may go through other files).

## Observations and recommendations
1. **Focus of early iterations** — components actually present in `Configs/ClDesc` (main families listed above). They need full descriptions, diagrams, and config examples.
2. **SNN and Motion Control** — large families; group by family (neurons, synapses, channels, trainers, classifiers, reflexes, predictors) and cover in batches.
4. **Leave a usage trail** — in component docs, cite examples from `Bin/Configs` (text path in subrepos, active link in the root repo).

This summary supports grouping and prioritization in library documentation passes.
