# Component Usage from Bin/ClDesc and Bin/Configs

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
