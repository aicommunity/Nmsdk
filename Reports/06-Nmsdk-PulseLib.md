# Nmsdk-PulseLib - Библиотека импульсных нейронных сетей

## Назначение

**Nmsdk-PulseLib** предоставляет компоненты для моделирования импульсных нейронных сетей (Spiking Neural Networks, SNN). Библиотека включает различные модели нейронов, синапсов, каналов, механизмы обучения и классификации на основе импульсных нейросетей.

## Структура библиотеки

### Основной класс

- **NPulseLibrary** (PulseLibrary) - главный класс библиотеки, наследник `ULibrary`

## Категории компонентов

### 1. Базовые компоненты сетей

#### NNet
Базовый класс сети импульсных нейронов. Контейнер для организации нейронов и синапсов в сеть.

#### NModel
Модель импульсной нейронной сети. Высокоуровневый компонент для работы с полными моделями.

#### NLifeNet
Сеть с жизненным циклом нейронов.

### 2. Нейроны

#### NNeuron
Базовый класс нейрона.

#### NPulseNeuron
Импульсный нейрон - основной компонент для моделирования нейронов, генерирующих спайки (импульсы).

#### NPulseNeuronCommon
Общая реализация импульсного нейрона.

#### NPulseNeuronIzhikevich
Нейрон по модели Ижикевича (Izhikevich model) - эффективная модель для имитации различных типов нейронов.

#### NIntegrateAndFireNeuron
Нейрон модели "интегрировать и стрелять" (Integrate-and-Fire) - классическая модель импульсного нейрона.

#### NPulseLifeNeuron
Нейрон с жизненным циклом.

#### NNeuronLife
Жизненный цикл нейрона.

#### NAfferentNeuron
Афферентный нейрон (входной нейрон, получающий внешние сигналы).

#### NNeuronFreqGroup
Группа нейронов с частотной кодировкой.

#### NNeuronFreqGroupLayer
Слой групп нейронов с частотной кодировкой.

#### NNeuronsLayer
Слой нейронов.

### 3. Синапсы

#### NPulseSynapse
Базовый класс синапса (соединения между нейронами).

#### NPulseSynapseCommon
Общая реализация синапса.

#### NPulseSynapseStdp
Синапс с пластичностью STDP (Spike-Timing Dependent Plasticity) - механизм обучения на основе временных корреляций спайков.

#### NPulseHebbSynapse
Синапс с правилом Хебба для обучения.

#### NPulseHebbLifeSynapse
Синапс Хебба с жизненным циклом.

#### NSynapseStdp
Синапс STDP (общая реализация).

#### NSynapseClassic
Классический синапс.

#### NSynapseClassicSlv
Классический синапс с решателем.

#### NPulseSynChannel
Синаптический канал.

### 4. Каналы

#### NPulseChannel
Базовый класс канала передачи импульсов.

#### NPulseChannelCommon
Общая реализация канала.

#### NPulseChannelIzhikevich
Канал для модели Ижикевича.

#### NPulseChannelIaF
Канал для модели Integrate-and-Fire.

#### NPulseChannelCable
Кабельный канал (моделирование аксона как кабеля).

#### NPulseChannelClassic
Классический канал.

### 5. Мембраны

#### NPulseMembrane
Мембрана нейрона.

#### NPulseMembraneCommon
Общая реализация мембраны.

#### NPulseMembraneIzhikevich
Мембрана для модели Ижикевича.

### 6. Зоны

#### NPulseLTZone
Зона долгосрочной потенциации (Long-Term).

#### NPulseLTZoneCommon
Общая реализация зоны.

#### NPulseLTZoneIzhikevich
Зона для модели Ижикевича.

### 7. Генераторы импульсов

#### NPulseGenerator
Генератор импульсов (спайков).

#### NPulseGeneratorDelay
Генератор с задержкой.

#### NPulseGeneratorMulti
Множественный генератор.

#### NConstGenerator
Генератор постоянного сигнала.

#### NSinusGenerator
Генератор синусоидального сигнала.

#### NFileGenerator
Генератор из файла.

### 8. Задержки

#### NPulseDelay
Задержка импульсов.

### 9. Рецепторы и источники

#### NReceptor
Рецептор - компонент для приема внешних сигналов.

#### NSource
Источник сигналов.

#### NReceiver
Приемник сигналов.

### 10. Классификаторы

#### NClassifier
Базовый классификатор на основе импульсных нейросетей.

#### NSpikeClassifier
Классификатор спайков.

#### NPCAClassifier
Классификатор с использованием PCA.

#### NConditionedReflex
Условный рефлекс (классификация с обучением).

### 11. Обучение

#### NNeuronTrainer
Тренер нейронов.

#### NNeuronLearner
Обучающийся нейрон.

#### NSynapseTrainer
Тренер синапсов.

#### NSynapseTrainerStdp
Тренер синапсов с STDP.

### 12. Перцептроны

#### NPulsePerseptron
Импульсный перцептрон.

### 13. Предсказатели

#### NPredictor
Предсказатель на основе импульсных нейросетей.

#### NStatePredictor
Предсказатель состояния.

#### NMExtrapolator
Экстраполятор движения.

### 14. Ассоциации

#### NAssociationFormer
Формирователь ассоциаций.

### 15. Рефлексы

#### NPainReflexSimple
Простой болевой рефлекс.

### 16. Данные и паттерны

#### NPattern
Паттерн (образец) для обучения и классификации.

#### NDataset
Датасет для обучения.

### 17. Логические операции

#### NLogicalNot
Логическое НЕ.

#### NSum
Сумматор сигналов.

### 18. Мышцы и эффекторы

#### NMuscle
Мышца - эффектор для управления движением.

#### NEyeMuscle
Мышца глаза.

### 19. PAC (Pulse Activity Counter)

#### NPac
Счетчик активности импульсов.

### 20. Решатель ODE

#### NOdeSolver
Решатель обыкновенных дифференциальных уравнений (ODE) для моделирования динамики нейронов. Используется опционально при наличии библиотеки ODE Solver.

## Модели нейронов

### Модель Ижикевича (Izhikevich)

Эффективная модель, способная имитировать различные типы нейронов:
- Регулярно спайкующие
- Быстро спайкующие
- Медленно спайкующие
- И другие типы

Компоненты:
- `NPulseNeuronIzhikevich`
- `NPulseChannelIzhikevich`
- `NPulseMembraneIzhikevich`
- `NPulseLTZoneIzhikevich`

### Модель Integrate-and-Fire

Классическая модель импульсного нейрона:
- `NIntegrateAndFireNeuron`
- `NPulseChannelIaF`

### Классические модели

- `NSynapseClassic` - классический синапс
- `NPulseChannelClassic` - классический канал

## Механизмы обучения

### STDP (Spike-Timing Dependent Plasticity)

Обучение на основе временных корреляций спайков:
- `NPulseSynapseStdp`
- `NSynapseStdp`
- `NSynapseTrainerStdp`

### Правило Хебба

Обучение по правилу Хебба:
- `NPulseHebbSynapse`
- `NPulseHebbLifeSynapse`

### Обучение нейронов

- `NNeuronTrainer` - тренер нейронов
- `NNeuronLearner` - обучающийся нейрон

## Использование

Библиотека автоматически загружается при инициализации:

```cpp
libs_list.push_back(&NMSDK::PulseLibrary);
```

## Зависимости

- **rdk.static.qt** - ядро Rdk (обязательно)
- **Rdk-BasicLib.qt** - базовая библиотека для источников данных и статистики (обязательно)
- **ODE Solver** - опционально, для `NOdeSolver` компонента

## Зависимости от этой библиотеки

- **Nmsdk-MotionControlLib** - использует импульсные нейросети для управления движением

## Примеры использования

### Создание простой сети

```cpp
// Создание сети
NNet* net = storage->CreateComponent<NNet>();

// Создание нейронов
NPulseNeuronIzhikevich* neuron1 = storage->CreateComponent<NPulseNeuronIzhikevich>();
NPulseNeuronIzhikevich* neuron2 = storage->CreateComponent<NPulseNeuronIzhikevich>();

// Создание синапса
NPulseSynapseStdp* synapse = storage->CreateComponent<NPulseSynapseStdp>();

// Соединение компонентов
net->AddComponent(neuron1);
net->AddComponent(neuron2);
net->AddComponent(synapse);
// Настройка соединений...
```

### Генератор импульсов

```cpp
// Создание генератора
NPulseGenerator* generator = storage->CreateComponent<NPulseGenerator>();
// Настройка частоты и параметров
```

### Классификатор

```cpp
// Создание классификатора
NClassifier* classifier = storage->CreateComponent<NClassifier>();
// Обучение и классификация
```

## Файлы библиотеки

Библиотека содержит 140 файлов (70 .cpp, 70 .h) в директории `Core/`, реализующих все перечисленные компоненты.

## См. также

- [02-Libraries-Overview.md](02-Libraries-Overview.md) - обзор всех библиотек
- [03-Rdk-BasicLib.md](03-Rdk-BasicLib.md) - базовая библиотека (зависимость)
- [07-Nmsdk-MotionControlLib.md](07-Nmsdk-MotionControlLib.md) - библиотека управления движением (использует PulseLib)

