# Пример: Создание базового компонента

## RU

### Описание задачи

Создать простой компонент, который читает данные из файла, обрабатывает их и выдает результат.

### Решение

Этот пример демонстрирует создание компонента с использованием компонентов из Rdk-BasicLib.

#### Шаг 1: Создание источника данных

```cpp
// Создание источника данных из файла
auto source = storage->CreateComponent<UMatrixSource>("DataSource");
source->FileName = "input.csv";
source->Default();
source->Build();
```

#### Шаг 2: Создание обработчика

```cpp
// Создание статистического компонента
auto processor = storage->CreateComponent<UStatisticDoubleMatrix>("Processor");
processor->InputData.AttachTo(&source->OutputMatrix);
processor->CalculateMean = true;
processor->CalculateStdDev = true;
processor->Default();
processor->Build();
```

#### Шаг 3: Создание выхода

```cpp
// Создание компонента вывода
auto output = storage->CreateComponent<UIO>("Output");
output->Input.AttachTo(&processor->Output);
output->OutputFile = "result.txt";
output->Default();
output->Build();
```

#### Шаг 4: Выполнение

```cpp
// Выполнение цикла обработки
for (int i = 0; i < 100; i++) {
    source->Calculate();
    processor->Calculate();
    output->Calculate();
}
```

### Полный пример

```cpp
#include <rdk.h>
using namespace RDK;

void ProcessData() {
    // Создание хранилища
    UStorage storage;
    
    // Загрузка библиотек
    std::list<ULibrary*> libs;
    RdkLoadPredefinedLibraries(libs);
    for(auto lib : libs) {
        storage.AddCollection(lib);
    }
    storage.BuildStorage();
    
    // Создание компонентов
    auto source = storage.CreateComponent<UMatrixSource>("Source");
    source->FileName = "data.csv";
    source->Default();
    source->Build();
    
    auto processor = storage.CreateComponent<UStatisticDoubleMatrix>("Processor");
    processor->InputData.AttachTo(&source->OutputMatrix);
    processor->CalculateMean = true;
    processor->Default();
    processor->Build();
    
    auto output = storage.CreateComponent<UIO>("Output");
    output->Input.AttachTo(&processor->Output);
    output->OutputFile = "result.txt";
    output->Default();
    output->Build();
    
    // Выполнение
    for (int i = 0; i < 100; i++) {
        source->Calculate();
        processor->Calculate();
        output->Calculate();
    }
}
```

### Объяснение ключевых моментов

1. **Загрузка библиотек** - необходимо для доступа к компонентам
2. **Создание через Storage** - все компоненты создаются через `CreateComponent()`
3. **Жизненный цикл** - `Default()`, `Build()`, `Calculate()`
4. **Соединения** - через `AttachTo()`

### Связанная документация

- [Rdk/Docs/Examples/Component-Creation-Example.md](../Rdk/Docs/Examples/Component-Creation-Example.md) - детальный пример создания компонента
- [Component System](../Rdk/Docs/Guides/Component-System.md) - компонентная система
- [Rdk-BasicLib/Docs/Usage-Examples.md](../Libraries/Rdk-BasicLib/Docs/Usage-Examples.md) - примеры использования Rdk-BasicLib

---

## EN

### Task Description

Create a simple component that reads data from a file, processes it, and outputs the result.

### Solution

This example demonstrates creating a component using components from Rdk-BasicLib.

#### Step 1: Create Data Source

```cpp
// Create data source from file
auto source = storage->CreateComponent<UMatrixSource>("DataSource");
source->FileName = "input.csv";
source->Default();
source->Build();
```

#### Step 2: Create Processor

```cpp
// Create statistical component
auto processor = storage->CreateComponent<UStatisticDoubleMatrix>("Processor");
processor->InputData.AttachTo(&source->OutputMatrix);
processor->CalculateMean = true;
processor->CalculateStdDev = true;
processor->Default();
processor->Build();
```

#### Step 3: Create Output

```cpp
// Create output component
auto output = storage->CreateComponent<UIO>("Output");
output->Input.AttachTo(&processor->Output);
output->OutputFile = "result.txt";
output->Default();
output->Build();
```

#### Step 4: Execute

```cpp
// Execute processing loop
for (int i = 0; i < 100; i++) {
    source->Calculate();
    processor->Calculate();
    output->Calculate();
}
```

### Complete Example

```cpp
#include <rdk.h>
using namespace RDK;

void ProcessData() {
    // Create storage
    UStorage storage;
    
    // Load libraries
    std::list<ULibrary*> libs;
    RdkLoadPredefinedLibraries(libs);
    for(auto lib : libs) {
        storage.AddCollection(lib);
    }
    storage.BuildStorage();
    
    // Create components
    auto source = storage.CreateComponent<UMatrixSource>("Source");
    source->FileName = "data.csv";
    source->Default();
    source->Build();
    
    auto processor = storage.CreateComponent<UStatisticDoubleMatrix>("Processor");
    processor->InputData.AttachTo(&source->OutputMatrix);
    processor->CalculateMean = true;
    processor->Default();
    processor->Build();
    
    auto output = storage.CreateComponent<UIO>("Output");
    output->Input.AttachTo(&processor->Output);
    output->OutputFile = "result.txt";
    output->Default();
    output->Build();
    
    // Execute
    for (int i = 0; i < 100; i++) {
        source->Calculate();
        processor->Calculate();
        output->Calculate();
    }
}
```

### Key Points Explanation

1. **Loading Libraries** - necessary for component access
2. **Creation via Storage** - all components created via `CreateComponent()`
3. **Lifecycle** - `Default()`, `Build()`, `Calculate()`
4. **Connections** - via `AttachTo()`

### Related Documentation

- [Rdk/Docs/Examples/Component-Creation-Example.md](../Rdk/Docs/Examples/Component-Creation-Example.md) - detailed component creation example
- [Components-And-Configuration/Component-System.md](../Components-And-Configuration/Component-System.md) - component system
- [Rdk-BasicLib/Docs/Usage-Examples.md](../Libraries/Rdk-BasicLib/Docs/Usage-Examples.md) - Rdk-BasicLib usage examples
