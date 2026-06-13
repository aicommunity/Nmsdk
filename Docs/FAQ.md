# FAQ - Nmsdk

## RU

### Общие вопросы

#### Что такое Nmsdk?

Nmsdk (Neuro Modeler SDK) - это SDK для моделирования нейронных сетей и робототехнических систем. Проект предоставляет компонентную архитектуру для создания, конфигурирования и выполнения моделей нейронных сетей.

#### Какие основные подсистемы входят в Nmsdk?

1. **Rdk Core** - ядро системы (компоненты, движок, сериализация)
2. **Libraries** - библиотеки компонентов (нейронные сети, компьютерное зрение, ML)
3. **GUI** - графический интерфейс пользователя
4. **Bin** - ресурсы и конфигурации

#### Где найти обзорную информацию?

См. [Overview/README.md](Overview/README.md) - обзор проекта.

### Установка и сборка

#### Какие системные требования?

- **Linux**: Ubuntu 22.04+ или аналогичный дистрибутив
- **Windows**: Windows 10+
- **Компилятор**: GCC 9+ или MSVC 2019+
- **CMake**: 3.16+ (3.20+ для presets)
- **Qt**: Qt6 на Linux; Qt5 или Qt6 на Windows (зависит от пресета)

#### Как установить зависимости?

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y \
  build-essential cmake git g++ \
  qt6-base-dev qt6-tools-dev qt6-serialport-dev qt6-svg-dev qt6-charts-dev \
  libboost-all-dev libcurl4-openssl-dev \
  libcups2-dev libgtest-dev
```

**Windows:**
- Установите Visual Studio 2019 или новее
- Установите CMake 3.16+
- Qt5 (VS2019) или Qt6 через vcpkg (VS2022)

См. [Overview/QuickStart.md](Overview/QuickStart.md) для детальной информации.

#### Как собрать проект?

```bash
cmake --preset linux-gcc-debug-local   # Linux, preset
cmake --build --preset linux-gcc-debug
```

Или классически:

```bash
mkdir build
cd build
cmake ..
cmake --build . -j$(nproc)  # Linux
# или
cmake --build . --config Release  # Windows
```

См. [Overview/QuickStart.md](Overview/QuickStart.md) для детальной информации.

### Использование компонентов

#### Как создать первый проект?

1. Запустите NeuroModeler
2. Создайте новый проект (File → New Project)
3. Добавьте компоненты из библиотеки
4. Соедините компоненты
5. Запустите выполнение

См. [Overview/QuickStart.md](Overview/QuickStart.md) для детальной инструкции.

#### Как использовать компоненты программно?

```cpp
#include <rdk.h>

// Создание хранилища и движка
UStorage storage;
UEngine engine;
engine.SetStorage(&storage);

// Загрузка библиотек
RdkLoadPredefinedLibraries(libs);
for(auto lib : libs) {
    storage.AddCollection(lib);
}
storage.BuildStorage();

// Создание компонента
auto comp = storage.CreateComponent<UMatrixSource>("Source");
comp->FileName = "data.csv";
comp->Build();
comp->Calculate();
```

См. [Component System](../Rdk/Docs/Guides/Component-System.md) для детальной информации.

### Разработка

#### Как создать новый компонент?

См. [Rdk/Docs/Guides/Creating-Components.md](../Rdk/Docs/Guides/Creating-Components.md) - детальное руководство.

**Краткий ответ:**
1. Наследуйте от `UComponent` или его потомков
2. Реализуйте методы жизненного цикла
3. Зарегистрируйте в `UStorage`

#### Как создать новую библиотеку?

См. [Development-Guides/Library-Development.md](Development-Guides/Library-Development.md) - руководство по разработке библиотек.

### Производительность

#### Как оптимизировать производительность?

- Избегайте выделения памяти в `ACalculate()`
- Используйте кэширование результатов
- Минимизируйте копирование данных
- Используйте прямой доступ к свойствам

См. [Performance-And-Testing/Performance-Overview.md](Performance-And-Testing/Performance-Overview.md) для детальной информации.

### Интеграция

#### Как интегрировать Nmsdk в свое приложение?

1. Инициализируйте `UApplication`
2. Загрузите необходимые библиотеки
3. Создайте и настройте `UEngine`
4. Загрузите или создайте проект

См. [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) для детальной информации.

#### Как использовать компоненты из разных библиотек вместе?

Компоненты из разных библиотек могут быть соединены через свойства:
```cpp
// Компонент из Rdk-BasicLib
auto source = storage->CreateComponent<UMatrixSource>("Source");

// Компонент из Nmsdk-PulseLib
auto neuron = storage->CreateComponent<NPulseNeuron>("Neuron");

// Соединение
neuron->InputPulses.AttachTo(&source->Output);
```

### FAQ по сабрепозиториям

#### Rdk Core

См. [Rdk/Docs/FAQ.md](../Rdk/Docs/FAQ.md) - часто задаваемые вопросы по Rdk Core.

#### Bin (Конфигурации)

См. [Bin/Docs/FAQ.md](../Bin/Docs/FAQ.md) - часто задаваемые вопросы по конфигурациям.

#### Библиотеки

- [Nmsdk-PulseLib](../Libraries/Nmsdk-PulseLib/Docs/FAQ.md) - FAQ по импульсным нейронным сетям
- [Rdk-BasicLib](../Libraries/Rdk-BasicLib/Docs/FAQ.md) - FAQ по базовым компонентам
- [Rdk-CvBasicLib](../Libraries/Rdk-CvBasicLib/Docs/FAQ.md) - FAQ по компьютерному зрению

### Устранение неполадок

#### Где найти решения типичных проблем?

См. [Troubleshooting/Troubleshooting-Guide.md](Troubleshooting/Troubleshooting-Guide.md) - подробное руководство по устранению неполадок.

#### Компонент не работает

1. Проверьте, что компонент создан через `Storage->CreateComponent()`
2. Убедитесь, что вызваны `Default()` и `Build()`
3. Проверьте готовность компонента (`IsReady()`)
4. См. логи приложения

### Дополнительные ресурсы

- [Getting-Started.md](Getting-Started.md) - пути для разных ролей
- [Best-Practices.md](Best-Practices.md) - лучшие практики
- [Glossary.md](Glossary.md) - глоссарий терминов
- [Examples/](Examples/) - практические примеры

---

## EN

### General Questions

#### What is Nmsdk?

Nmsdk (Neuro Modeler SDK) is an SDK for neural network modeling and robotics systems. The project provides a component-based architecture for creating, configuring, and executing neural network models.

#### What are the main subsystems in Nmsdk?

1. **Rdk Core** - system core (components, engine, serialization)
2. **Libraries** - component libraries (neural networks, computer vision, ML)
3. **GUI** - graphical user interface
4. **Bin** - resources and configurations

#### Where can I find overview information?

See [Overview/README.md](Overview/README.md) - project overview.

### Installation and Build

#### What are the system requirements?

- **Linux**: Ubuntu 22.04+ or similar distribution
- **Windows**: Windows 10+
- **Compiler**: GCC 9+ or MSVC 2019+
- **CMake**: 3.16+ (3.20+ for presets)
- **Qt**: Qt6 on Linux; Qt5 or Qt6 on Windows (depends on preset)

#### How do I install dependencies?

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y \
  build-essential cmake git g++ \
  qt6-base-dev qt6-tools-dev qt6-serialport-dev qt6-svg-dev qt6-charts-dev \
  libboost-all-dev libcurl4-openssl-dev \
  libcups2-dev libgtest-dev
```

**Windows:**
- Install Visual Studio 2019 or newer
- Install CMake 3.16+
- Qt5 (VS2019) or Qt6 via vcpkg (VS2022)

See [Overview/QuickStart.md](Overview/QuickStart.md) for detailed information.

#### How do I build the project?

```bash
cmake --preset linux-gcc-debug-local   # Linux preset
cmake --build --preset linux-gcc-debug
```

Or the classic flow:

```bash
mkdir build
cd build
cmake ..
cmake --build . -j$(nproc)  # Linux
# or
cmake --build . --config Release  # Windows
```

See [Overview/QuickStart.md](Overview/QuickStart.md) for detailed information.

### Component Usage

#### How do I create my first project?

1. Launch NeuroModeler
2. Create a new project (File → New Project)
3. Add components from library
4. Connect components
5. Start execution

See [Overview/QuickStart.md](Overview/QuickStart.md) for detailed instructions.

#### How do I use components programmatically?

```cpp
#include <rdk.h>

// Create storage and engine
UStorage storage;
UEngine engine;
engine.SetStorage(&storage);

// Load libraries
RdkLoadPredefinedLibraries(libs);
for(auto lib : libs) {
    storage.AddCollection(lib);
}
storage.BuildStorage();

// Create component
auto comp = storage.CreateComponent<UMatrixSource>("Source");
comp->FileName = "data.csv";
comp->Build();
comp->Calculate();
```

See [Components-And-Configuration/Component-System.md](Components-And-Configuration/Component-System.md) for detailed information.

### Development

#### How do I create a new component?

See [Rdk/Docs/Guides/Creating-Components.md](../Rdk/Docs/Guides/Creating-Components.md) - detailed guide.

**Quick answer:**
1. Inherit from `UComponent` or its descendants
2. Implement lifecycle methods
3. Register in `UStorage`

#### How do I create a new library?

See [Development-Guides/Library-Development.md](Development-Guides/Library-Development.md) - library development guide.

### Performance

#### How do I optimize performance?

- Avoid memory allocation in `ACalculate()`
- Use result caching
- Minimize data copying
- Use direct property access

See [Performance-And-Testing/Performance-Overview.md](Performance-And-Testing/Performance-Overview.md) for detailed information.

### Integration

#### How do I integrate Nmsdk into my application?

1. Initialize `UApplication`
2. Load necessary libraries
3. Create and configure `UEngine`
4. Load or create project

See [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) for detailed information.

#### How do I use components from different libraries together?

Components from different libraries can be connected through properties:
```cpp
// Component from Rdk-BasicLib
auto source = storage->CreateComponent<UMatrixSource>("Source");

// Component from Nmsdk-PulseLib
auto neuron = storage->CreateComponent<NPulseNeuron>("Neuron");

// Connect
neuron->InputPulses.AttachTo(&source->Output);
```

### Subrepository FAQs

#### Rdk Core

See [Rdk/Docs/FAQ.md](../Rdk/Docs/FAQ.md) - frequently asked questions about Rdk Core.

#### Bin (Configurations)

See [Bin/Docs/FAQ.md](../Bin/Docs/FAQ.md) - frequently asked questions about configurations.

#### Libraries

- [Nmsdk-PulseLib](../Libraries/Nmsdk-PulseLib/Docs/FAQ.md) - FAQ about spiking neural networks
- [Rdk-BasicLib](../Libraries/Rdk-BasicLib/Docs/FAQ.md) - FAQ about basic components
- [Rdk-CvBasicLib](../Libraries/Rdk-CvBasicLib/Docs/FAQ.md) - FAQ about computer vision

### Troubleshooting

#### Where can I find solutions to typical problems?

See [Troubleshooting/Troubleshooting-Guide.md](Troubleshooting/Troubleshooting-Guide.md) - detailed troubleshooting guide.

#### Component doesn't work

1. Check that component is created via `Storage->CreateComponent()`
2. Ensure `Default()` and `Build()` are called
3. Check component readiness (`IsReady()`)
4. See application logs

### Additional Resources

- [Getting-Started.md](Getting-Started.md) - paths for different roles
- [Best-Practices.md](Best-Practices.md) - best practices
- [Glossary.md](Glossary.md) - glossary of terms
- [Examples/](Examples/) - practical examples
