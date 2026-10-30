# Глоссарий терминологии компонентов Nmsdk

## RU

### Назначение

Этот глоссарий содержит расшифровку терминологии, используемой в именах компонентов библиотек Nmsdk. Он помогает понять значение префиксов, аббревиатур и суффиксов в названиях компонентов.

---

## Префиксы компонентов

### Базовые префиксы библиотек

| Префикс | Значение | Описание | Примеры |
|---------|----------|----------|---------|
| `N` | Nmsdk | Компоненты библиотеки Nmsdk (нейронные сети, импульсные модели) | `NNeuron`, `NSource`, `NNet` |
| `U` | Universal / Rdk | Базовые классы Rdk Framework | `UNet`, `UIO`, `UComponent` |
| `T` | Template | Шаблонные классы | `TPyComponent`, `TPyObjectDetector` |

### Префиксы типов сигналов и моделей

| Префикс | Значение | Описание | Примеры |
|---------|----------|----------|---------|
| `NC` | **C**ontinuous (непрерывный, классический) | Компоненты с непрерывными входами/выходами (не импульсные) | `NCNeuron`, `NCMembrane`, `NCLTZone`, `NCPac`, `NCGenerator`, `NCSynChannel` |
| `NP` | **P**ulse (импульсный) | Компоненты с импульсными входами/выходами | `NPulseGenerator`, `NPulseNeuron`, `NPulseMembrane`, `NPLTZone`, `NPGenerator` |
| `NPLT` | **P**ulse **LT** Zone | Импульсная низкопороговая зона | `NPLTZone`, `NPulseLTZoneCommon` |
| `NPSimple` | **P**ulse **Simple** | Простая импульсная версия компонента | `NPSimpleLTZone` |
| `NSP` | **S**imple **P**ulse | Простой импульсный компонент | `NSPLifeHebbNeuron`, `NSPMinNeuron`, `NSPDendriteLifeHebbNeuron` |
| `NContinues` | **Continues** (Continuous) | Непрерывный вариант компонента | `NContinuesSAfferentNeuron`, `NContinuesSynRenshowCell` |

### Префиксы структуры и вариантов

| Префикс | Значение | Описание | Примеры |
|---------|----------|----------|---------|
| `NS` | **S**imple или **S**tandard | Простой вариант или стандартный/классический вариант | `NSimpleAfferentNeuron`, `NSAfferentNeuron`, `NSource` |
| `NSimple` | **Simple** | Простой вариант компонента | `NSimpleAfferentNeuron` |

---

## Аббревиатуры

### Общие аббревиатуры

| Аббревиатура | Полное значение | Описание | Примеры компонентов |
|--------------|----------------|----------|---------------------|
| `IO` | **I**nput/**O**utput (ввод-вывод) | Компоненты для ввода/вывода данных | `UIO`, `UFileIO`, `UIOConverter`, `UIOTextConverter` |
| `LT` | **L**ow **T**hreshold (низкопороговая зона) | Зона с низким порогом активации | `NCLTZone`, `NPLTZone`, `NPulseLTZoneCommon` |
| `PAC` | **P**ulse **A**ctivity **C**ounter (счетчик активности импульсов) | Компонент для подсчета активности импульсов | `NPac`, `NCPac` |
| `STDP` | **S**pike-**T**iming **D**ependent **P**lasticity | Пластичность, зависящая от времени спайков | `NSynapseStdp`, `NPulseMembraneIaFStdp` |
| `IaF` | **I**ntegrate and **F**ire | Модель "интегрировать и стрелять" | `NPulseChannelIaF`, `NPulseMembraneIaF`, `NIntegrateAndFireNeuron` |
| `Hebb` | **Hebb**ian | Геббовская пластичность (обучение по правилу Хебба) | `NPHebbNeuron`, `NSPLifeHebbNeuron`, `NPNeuronHebbMembrane` |
| `Bio` | **Bio**logical | Биологическая модель | `NPExcChannelBio`, `NPInhChannelBio`, `NPMembraneBio`, `NPulseMembraneIaFStdp` |
| `Syn` | **Syn**apse | Синапс | `NCSynChannel`, `NPSynChannel`, `NSynapseStdp` |
| `Exc` | **Exc**itatory | Возбуждающий | `NPExcChannel`, `NCSynExcChannel`, `NPExcChannelBio` |
| `Inh` | **Inh**ibitory | Тормозной | `NPInhChannel`, `NCSynInhChannel`, `NPInhChannelBio` |

### Аббревиатуры моделей нейронов

| Аббревиатура | Полное значение | Описание | Примеры |
|--------------|----------------|----------|---------|
| `SP` | **S**pike **P**attern | Паттерн спайков | `NSynSPNeuron`, `NSPNeuronGen` |
| `LP` | **L**ong **P**attern | Длинный паттерн | `NSynLPNeuron` |
| `TCN` | **T**emporal **C**onvolutional **N**etwork | Временная сверточная сеть | `NSynTCNNeuron` |
| `Renshow` | **Renshow** Cell | Клетка Реншоу | `NSynRenshowCell`, `NContinuesSynRenshowCell` |
| `Motoneuron` | **Motoneuron** | Мотонейрон | `NSynMotoneuron`, `NContinuesSynMotoneuron` |

---

## Суффиксы

### Общие суффиксы

| Суффикс | Значение | Описание | Примеры |
|---------|----------|----------|---------|
| `Common` | Общий/базовый | Базовый вариант компонента | `NPulseNeuronCommon`, `NPulseLTZoneCommon`, `NPulseChannelCommon` |
| `Generator` | Генератор | Компонент для генерации сигналов | `NPulseGenerator`, `NCGenerator`, `NSinusGenerator` |
| `Receptor` | Рецептор | Компонент для приема внешних сигналов | `NReceptor` |
| `Membrane` | Мембрана | Мембрана нейрона | `NPulseMembrane`, `NCMembrane`, `NPulseMembraneIaF` |
| `Channel` | Канал | Ионный канал | `NPulseChannel`, `NCSynChannel`, `NPExcChannel` |
| `Synapse` | Синапс | Синапс между нейронами | `NSynapseStdp`, `NPSynapse` |
| `Neuron` | Нейрон | Нейрон | `NCNeuron`, `NPulseNeuron`, `NAfferentNeuron` |
| `LTZone` | Low Threshold Zone | Низкопороговая зона | `NCLTZone`, `NPLTZone`, `NPulseLTZoneCommon` |
| `Trainer` | Тренер | Компонент для обучения | `NSynapseTrainerStdp`, `NNeuronTrainer` |
| `Classifier` | Классификатор | Компонент для классификации | `NClassifier`, `NSpikeClassifier`, `NPCAClassifier` |
| `Detector` | Детектор | Компонент для детекции | `TPyObjectDetector`, `UTfDetector` |
| `Segmentator` | Сегментатор | Компонент для сегментации | `TPySegmentator`, `TPySegmentatorUNet` |

---

## Примеры использования терминологии

### Пример 1: Расшифровка имени `NCNeuron`

- `N` — компонент библиотеки Nmsdk
- `C` — **C**ontinuous (непрерывный, классический)
- `Neuron` — нейрон

**Итого:** Классический нейрон с непрерывными входами/выходами (не импульсный)

### Пример 2: Расшифровка имени `NPLTZone`

- `N` — компонент библиотеки Nmsdk
- `P` — **P**ulse (импульсный)
- `LT` — **L**ow **T**hreshold (низкопороговая зона)
- `Zone` — зона

**Итого:** Импульсная низкопороговая зона (с импульсными входами/выходами)

### Пример 3: Расшифровка имени `UIO`

- `U` — базовый класс Rdk Framework
- `IO` — **I**nput/**O**utput (ввод-вывод)

**Итого:** Базовый класс для компонентов ввода/вывода данных

### Пример 4: Расшифровка имени `NPulseMembraneIaFStdp`

- `N` — компонент библиотеки Nmsdk
- `Pulse` — импульсный
- `Membrane` — мембрана
- `IaF` — **I**ntegrate and **F**ire (интегрировать и стрелять)
- `Stdp` — **S**pike-**T**iming **D**ependent **P**lasticity

**Итого:** Импульсная мембрана с моделью Integrate and Fire и пластичностью STDP

### Пример 5: Расшифровка имени `NSPLifeHebbNeuron`

- `N` — компонент библиотеки Nmsdk
- `S` — **S**imple (простой)
- `P` — **P**ulse (импульсный)
- `Life` — жизненный цикл
- `Hebb` — **Hebb**ian (геббовская пластичность)
- `Neuron` — нейрон

**Итого:** Простой импульсный нейрон с жизненным циклом и геббовской пластичностью

---

## Иерархия компонентов

### Базовые классы

```
UNet (Rdk Framework)
├── UIO (ввод-вывод)
│   ├── UFileIO
│   └── UIOConverter
│       └── UIOTextConverter
├── NNet (базовая сеть Nmsdk)
│   ├── NNeuron (базовый нейрон)
│   │   ├── NCNeuron (классический)
│   │   └── NPulseNeuron (импульсный)
│   └── NSource (источник сигналов)
│       ├── NPulseGenerator
│       └── NReceptor
└── TPyComponent (Python интеграция)
    ├── TPyObjectDetector
    └── TPySegmentator
```

### Типы сигналов

- **Continuous (NC)**: Непрерывные сигналы, классические нейронные сети
- **Pulse (NP)**: Импульсные сигналы, спайковые нейронные сети

---

## См. также

- [Component-Catalog.md](Nmsdk-PulseLib/Docs/Component-Catalog.md) — каталог компонентов Nmsdk-PulseLib
- [Architecture.md](Nmsdk-PulseLib/Docs/Architecture.md) — архитектура библиотеки
- Документация компонентов в `Libraries/*/Docs/Components/`

---

## EN

### Purpose

This glossary contains terminology used in component names across Nmsdk libraries. It helps understand the meaning of prefixes, abbreviations, and suffixes in component names.

---

## Component Prefixes

### Base Library Prefixes

| Prefix | Meaning | Description | Examples |
|--------|---------|------------|----------|
| `N` | Nmsdk | Nmsdk library components (neural networks, spiking models) | `NNeuron`, `NSource`, `NNet` |
| `U` | Universal / Rdk | Base classes from Rdk Framework | `UNet`, `UIO`, `UComponent` |
| `T` | Template | Template classes | `TPyComponent`, `TPyObjectDetector` |

### Signal Type and Model Prefixes

| Prefix | Meaning | Description | Examples |
|--------|---------|------------|----------|
| `NC` | **C**ontinuous | Components with continuous inputs/outputs (non-spiking) | `NCNeuron`, `NCMembrane`, `NCLTZone`, `NCPac`, `NCGenerator`, `NCSynChannel` |
| `NP` | **P**ulse | Components with spiking inputs/outputs | `NPulseGenerator`, `NPulseNeuron`, `NPulseMembrane`, `NPLTZone`, `NPGenerator` |
| `NPLT` | **P**ulse **LT** Zone | Spiking low-threshold zone | `NPLTZone`, `NPulseLTZoneCommon` |
| `NPSimple` | **P**ulse **Simple** | Simple spiking version | `NPSimpleLTZone` |
| `NSP` | **S**imple **P**ulse | Simple spiking component | `NSPLifeHebbNeuron`, `NSPMinNeuron`, `NSPDendriteLifeHebbNeuron` |
| `NContinues` | **Continues** (Continuous) | Continuous variant | `NContinuesSAfferentNeuron`, `NContinuesSynRenshowCell` |

### Structure and Variant Prefixes

| Prefix | Meaning | Description | Examples |
|--------|---------|------------|----------|
| `NS` | **S**imple or **S**tandard | Simple variant or standard/classic variant | `NSimpleAfferentNeuron`, `NSAfferentNeuron`, `NSource` |
| `NSimple` | **Simple** | Simple variant | `NSimpleAfferentNeuron` |

---

## Abbreviations

### General Abbreviations

| Abbreviation | Full Meaning | Description | Component Examples |
|--------------|-------------|-------------|-------------------|
| `IO` | **I**nput/**O**utput | Data input/output components | `UIO`, `UFileIO`, `UIOConverter`, `UIOTextConverter` |
| `LT` | **L**ow **T**hreshold | Low-threshold activation zone | `NCLTZone`, `NPLTZone`, `NPulseLTZoneCommon` |
| `PAC` | **P**ulse **A**ctivity **C**ounter | Pulse activity counter component | `NPac`, `NCPac` |
| `STDP` | **S**pike-**T**iming **D**ependent **P**lasticity | Spike-timing dependent plasticity | `NSynapseStdp`, `NPulseMembraneIaFStdp` |
| `IaF` | **I**ntegrate and **F**ire | Integrate and fire model | `NPulseChannelIaF`, `NPulseMembraneIaF`, `NIntegrateAndFireNeuron` |
| `Hebb` | **Hebb**ian | Hebbian plasticity (Hebb's rule learning) | `NPHebbNeuron`, `NSPLifeHebbNeuron`, `NPNeuronHebbMembrane` |
| `Bio` | **Bio**logical | Biological model | `NPExcChannelBio`, `NPInhChannelBio`, `NPMembraneBio` |
| `Syn` | **Syn**apse | Synapse | `NCSynChannel`, `NPSynChannel`, `NSynapseStdp` |
| `Exc` | **Exc**itatory | Excitatory | `NPExcChannel`, `NCSynExcChannel`, `NPExcChannelBio` |
| `Inh` | **Inh**ibitory | Inhibitory | `NPInhChannel`, `NCSynInhChannel`, `NPInhChannelBio` |

### Neuron Model Abbreviations

| Abbreviation | Full Meaning | Description | Examples |
|--------------|-------------|-------------|----------|
| `SP` | **S**pike **P**attern | Spike pattern | `NSynSPNeuron`, `NSPNeuronGen` |
| `LP` | **L**ong **P**attern | Long pattern | `NSynLPNeuron` |
| `TCN` | **T**emporal **C**onvolutional **N**etwork | Temporal convolutional network | `NSynTCNNeuron` |
| `Renshow` | **Renshow** Cell | Renshow cell | `NSynRenshowCell`, `NContinuesSynRenshowCell` |
| `Motoneuron` | **Motoneuron** | Motoneuron | `NSynMotoneuron`, `NContinuesSynMotoneuron` |

---

## Suffixes

### General Suffixes

| Suffix | Meaning | Description | Examples |
|--------|---------|------------|----------|
| `Common` | Common/base | Base variant of component | `NPulseNeuronCommon`, `NPulseLTZoneCommon`, `NPulseChannelCommon` |
| `Generator` | Generator | Signal generation component | `NPulseGenerator`, `NCGenerator`, `NSinusGenerator` |
| `Receptor` | Receptor | External signal reception component | `NReceptor` |
| `Membrane` | Membrane | Neuron membrane | `NPulseMembrane`, `NCMembrane`, `NPulseMembraneIaF` |
| `Channel` | Channel | Ion channel | `NPulseChannel`, `NCSynChannel`, `NPExcChannel` |
| `Synapse` | Synapse | Synapse between neurons | `NSynapseStdp`, `NPSynapse` |
| `Neuron` | Neuron | Neuron | `NCNeuron`, `NPulseNeuron`, `NAfferentNeuron` |
| `LTZone` | Low Threshold Zone | Low-threshold zone | `NCLTZone`, `NPLTZone`, `NPulseLTZoneCommon` |
| `Trainer` | Trainer | Training component | `NSynapseTrainerStdp`, `NNeuronTrainer` |
| `Classifier` | Classifier | Classification component | `NClassifier`, `NSpikeClassifier`, `NPCAClassifier` |
| `Detector` | Detector | Detection component | `TPyObjectDetector`, `UTfDetector` |
| `Segmentator` | Segmentator | Segmentation component | `TPySegmentator`, `TPySegmentatorUNet` |

---

## Usage Examples

### Example 1: Decoding `NCNeuron`

- `N` — Nmsdk library component
- `C` — **C**ontinuous (non-spiking)
- `Neuron` — neuron

**Result:** Classic neuron with continuous inputs/outputs (non-spiking)

### Example 2: Decoding `NPLTZone`

- `N` — Nmsdk library component
- `P` — **P**ulse (spiking)
- `LT` — **L**ow **T**hreshold
- `Zone` — zone

**Result:** Spiking low-threshold zone (with spiking inputs/outputs)

### Example 3: Decoding `UIO`

- `U` — Rdk Framework base class
- `IO` — **I**nput/**O**utput

**Result:** Base class for data input/output components

### Example 4: Decoding `NPulseMembraneIaFStdp`

- `N` — Nmsdk library component
- `Pulse` — spiking
- `Membrane` — membrane
- `IaF` — **I**ntegrate and **F**ire
- `Stdp` — **S**pike-**T**iming **D**ependent **P**lasticity

**Result:** Spiking membrane with Integrate and Fire model and STDP plasticity

### Example 5: Decoding `NSPLifeHebbNeuron`

- `N` — Nmsdk library component
- `S` — **S**imple
- `P` — **P**ulse (spiking)
- `Life` — life cycle
- `Hebb` — **Hebb**ian plasticity
- `Neuron` — neuron

**Result:** Simple spiking neuron with life cycle and Hebbian plasticity

---

## Component Hierarchy

### Base Classes

```
UNet (Rdk Framework)
├── UIO (input/output)
│   ├── UFileIO
│   └── UIOConverter
│       └── UIOTextConverter
├── NNet (Nmsdk base network)
│   ├── NNeuron (base neuron)
│   │   ├── NCNeuron (classic)
│   │   └── NPulseNeuron (spiking)
│   └── NSource (signal source)
│       ├── NPulseGenerator
│       └── NReceptor
└── TPyComponent (Python integration)
    ├── TPyObjectDetector
    └── TPySegmentator
```

### Signal Types

- **Continuous (NC)**: Continuous signals, classic neural networks
- **Pulse (NP)**: Spiking signals, spiking neural networks

---

## See Also

- [Component-Catalog.md](Nmsdk-PulseLib/Docs/Component-Catalog.md) — Nmsdk-PulseLib component catalog
- [Architecture.md](Nmsdk-PulseLib/Docs/Architecture.md) — library architecture
- Component documentation in `Libraries/*/Docs/Components/`
