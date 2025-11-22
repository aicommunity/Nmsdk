# Обзор библиотек

## Введение

Библиотеки в папке `Libraries/` содержат реализацию конкретных компонентов, расширяющих базовую функциональность ядра Rdk. Каждая библиотека представляет собой набор компонентов, объединенных общей тематикой.

## Список библиотек

### Основные библиотеки

1. **Rdk-BasicLib** - Базовые компоненты для работы с данными
2. **Rdk-CvBasicLib** - Компоненты компьютерного зрения на базе OpenCV
3. **Rdk-HardwareLib** - Работа с аппаратным обеспечением (Arduino и др.)
4. **Nmsdk-PulseLib** - Импульсные нейронные сети
5. **Nmsdk-MotionControlLib** - Управление движением и робототехника

### Библиотеки машинного обучения

6. **Rdk-PyMachineLearningLib** - Интеграция с Python ML библиотеками
7. **Rdk-TensorflowLib** - Интеграция с TensorFlow
8. **Rdk-DarknetLib** - Интеграция с Darknet

## Назначение библиотек

### Rdk-BasicLib

**Назначение:** Базовые компоненты для работы с данными, IO операциями, матрицами и статистикой.

**Основные категории компонентов:**
- Ввод-вывод данных (UIO, UFileIO)
- Матрицы и источники данных (UMatrixSource, UFileDataset)
- Статистика (UStatistic)
- Генераторы шума (UNoise, UNoiseGen)
- Модели (UModel)

**См. детали:** [03-Rdk-BasicLib.md](03-Rdk-BasicLib.md)

### Rdk-CvBasicLib

**Назначение:** Компоненты компьютерного зрения на базе OpenCV.

**Основные категории компонентов:**
- Захват видео (TCapture, TCaptureCamera)
- Обработка изображений (UBA* компоненты)
- Детекторы объектов (UDetectorBase, UBAObjectDetector)
- Классификаторы (UCRClassifier, UCRPerseptron)
- Нейронные сети (UCRConvolutionNetwork)
- Сегментация (USegmentatorBase)

**См. детали:** [04-Rdk-CvBasicLib.md](04-Rdk-CvBasicLib.md)

### Rdk-HardwareLib

**Назначение:** Работа с аппаратным обеспечением, в первую очередь с Arduino.

**Основные категории компонентов:**
- Подключение к Arduino (UArduinoConnect)
- Управление Arduino (UArduinoControl)
- Датчики (UAdcSensor)
- Демо контроллеры (UDcControlDemo)

**См. детали:** [05-Rdk-HardwareLib.md](05-Rdk-HardwareLib.md)

### Nmsdk-PulseLib

**Назначение:** Импульсные нейронные сети (Spiking Neural Networks).

**Основные категории компонентов:**
- Нейроны (NPulseNeuron, NIntegrateAndFireNeuron)
- Синапсы (NPulseSynapse, NSynapseStdp)
- Каналы (NPulseChannel, NPulseChannelIzhikevich)
- Генераторы импульсов (NPulseGenerator)
- Классификаторы (NClassifier, NSpikeClassifier)
- Обучение (NNeuronTrainer, NSynapseTrainer)

**См. детали:** [06-Nmsdk-PulseLib.md](06-Nmsdk-PulseLib.md)

### Nmsdk-MotionControlLib

**Назначение:** Управление движением, робототехника, системы управления.

**Основные категории компонентов:**
- Двигатели (NDCEngine)
- Манипуляторы (NManipulator, NManipulatorAndGyro)
- Контроль позиции (NPositionControlElement, NMultiPositionControl)
- Траектории (NTrajectoryElement)
- Ретина глаза (NEyeRetina)
- Гироскопы (NAstaticGyro)

**См. детали:** [07-Nmsdk-MotionControlLib.md](07-Nmsdk-MotionControlLib.md)

### Rdk-PyMachineLearningLib

**Назначение:** Интеграция с Python библиотеками машинного обучения.

**Основные категории компонентов:**
- Классификаторы (TPyClassifierTrainer, TPyUBitmapClassifier)
- Детекторы объектов (TPyObjectDetector, TPyObjectDetectorYolo)
- Сегментаторы (TPySegmentator, TPySegmentatorUNet)
- Базовый компонент (TPyComponent)

**См. детали:** [08-ML-Libraries.md](08-ML-Libraries.md)

### Rdk-TensorflowLib

**Назначение:** Интеграция с TensorFlow.

**Основные категории компонентов:**
- Классификаторы (UTfClassifier)
- Детекторы (UTfDetector, UTfSqDetector)
- Базовый компонент (UTfComponent)
- Сессии TensorFlow (ttfsession)

**См. детали:** [08-ML-Libraries.md](08-ML-Libraries.md)

### Rdk-DarknetLib

**Назначение:** Интеграция с Darknet.

**Основные категории компонентов:**
- Детекторы объектов (TDarknetObjectDetector)
- Классификаторы (TDarknetUBitmapClassifier)

**См. детали:** [08-ML-Libraries.md](08-ML-Libraries.md)

## Зависимости между библиотеками

```
rdk.static.qt (ядро)
    │
    ├── Rdk-BasicLib.qt
    │   └── Зависит от: rdk.static.qt
    │
    ├── Rdk-CvBasicLib.qt
    │   └── Зависит от: rdk.static.qt, OpenCV
    │
    ├── Rdk-HardwareLib.qt
    │   └── Зависит от: rdk.static.qt
    │
    ├── Nmsdk-PulseLib.qt
    │   ├── Зависит от: rdk.static.qt, Rdk-BasicLib.qt
    │   └── Использует: ODE Solver (опционально)
    │
    └── Nmsdk-MotionControlLib.qt
        ├── Зависит от: rdk.static.qt
        ├── Зависит от: Rdk-BasicLib.qt
        ├── Зависит от: Rdk-CvBasicLib.qt
        ├── Зависит от: Rdk-HardwareLib.qt
        └── Зависит от: Nmsdk-PulseLib.qt
```

Библиотеки ML (PyMachineLearningLib, TensorflowLib, DarknetLib) являются опциональными и зависят от наличия соответствующих внешних библиотек.

## Механизм загрузки библиотек

Библиотеки загружаются через функцию `RdkLoadPredefinedLibraries()` в файле `Libraries/Libraries.cpp`:

```cpp
bool RdkLoadPredefinedLibraries(std::list<RDK::ULibrary*> &libs_list)
{
    // Базовые библиотеки
    libs_list.push_back(&RDK::BasicLibrary);
    libs_list.push_back(&RDK::CvBasicLibrary);
    libs_list.push_back(&RDK::HardwareLibrary);
    
    // Опциональные ML библиотеки
    #ifdef RDK_USE_PYTHON
    libs_list.push_back(&RDK::PyMachineLearningLib);
    #endif
    
    #ifdef RDK_USE_TENSORFLOW
    libs_list.push_back(&RDK::TensorflowLib);
    #endif
    
    // Библиотеки NMSDK
    libs_list.push_back(&NMSDK::PulseLibrary);
    libs_list.push_back(&NMSDK::MotionControlLibrary);
    
    return true;
}
```

## Структура библиотеки

Каждая библиотека следует общей структуре:

```
LibraryName/
├── Core/              # Исходный код компонентов
│   ├── Component1.h
│   ├── Component1.cpp
│   └── ...
├── Deploy/
│   └── Include/
│       └── Lib.h      # Главный заголовочный файл библиотеки
├── CMake/
│   └── CMakeLists.txt # Файл сборки CMake
├── Build/             # Файлы сборки для различных IDE
└── Tests/             # Тесты библиотеки
```

## Регистрация компонентов

Каждая библиотека наследуется от `ULibrary` и реализует метод `CreateClassSamples()`, который регистрирует компоненты библиотеки в хранилище (UStorage):

```cpp
class MyLibrary: public ULibrary
{
public:
    MyLibrary(void);
    virtual void CreateClassSamples(UStorage *storage);
};
```

## См. также

- [03-Rdk-BasicLib.md](03-Rdk-BasicLib.md) - Детали базовой библиотеки
- [04-Rdk-CvBasicLib.md](04-Rdk-CvBasicLib.md) - Детали библиотеки компьютерного зрения
- [05-Rdk-HardwareLib.md](05-Rdk-HardwareLib.md) - Детали библиотеки работы с железом
- [06-Nmsdk-PulseLib.md](06-Nmsdk-PulseLib.md) - Детали библиотеки импульсных нейросетей
- [07-Nmsdk-MotionControlLib.md](07-Nmsdk-MotionControlLib.md) - Детали библиотеки управления движением
- [08-ML-Libraries.md](08-ML-Libraries.md) - Детали ML библиотек
- [09-Component-System.md](09-Component-System.md) - Описание компонентной системы

