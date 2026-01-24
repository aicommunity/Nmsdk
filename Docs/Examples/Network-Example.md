# Пример: Создание сети компонентов

## RU

### Описание задачи

Создать сеть компонентов, которая обрабатывает данные из нескольких источников и агрегирует результаты.

### Решение

#### Создание сети с несколькими источниками

```cpp
#include <rdk.h>
using namespace RDK;

void CreateNetwork() {
    UStorage storage;
    // ... загрузка библиотек ...
    
    // Источник 1
    auto source1 = storage.CreateComponent<UMatrixSource>("Source1");
    source1->FileName = "data1.csv";
    source1->Default();
    source1->Build();
    
    // Источник 2
    auto source2 = storage.CreateComponent<UMatrixSource>("Source2");
    source2->FileName = "data2.csv";
    source2->Default();
    source2->Build();
    
    // Обработчик 1
    auto processor1 = storage.CreateComponent<UStatisticDoubleMatrix>("Processor1");
    processor1->InputData.AttachTo(&source1->OutputMatrix);
    processor1->Default();
    processor1->Build();
    
    // Обработчик 2
    auto processor2 = storage.CreateComponent<UStatisticDoubleMatrix>("Processor2");
    processor2->InputData.AttachTo(&source2->OutputMatrix);
    processor2->Default();
    processor2->Build();
    
    // Агрегатор (используя контейнер)
    auto aggregator = storage.CreateComponent<UNet>("Aggregator");
    aggregator->Default();
    aggregator->Build();
    
    // Выполнение
    for (int i = 0; i < 100; i++) {
        source1->Calculate();
        source2->Calculate();
        processor1->Calculate();
        processor2->Calculate();
    }
}
```

### Использование конфигурационного файла

См. [Bin/Docs/Examples/Config-Example.md](../Bin/Docs/Examples/Config-Example.md) для примера создания сети через XML конфигурацию.

### Связанная документация

- [Components-And-Configuration/Component-System.md](../Components-And-Configuration/Component-System.md) - компонентная система
- [Rdk-Core/Engine-Architecture.md](../Rdk-Core/Engine-Architecture.md) - архитектура движка
- [Bin/Docs/Examples/Config-Example.md](../Bin/Docs/Examples/Config-Example.md) - примеры конфигураций

---

## EN

### Task Description

Create a component network that processes data from multiple sources and aggregates results.

### Solution

#### Creating Network with Multiple Sources

```cpp
#include <rdk.h>
using namespace RDK;

void CreateNetwork() {
    UStorage storage;
    // ... load libraries ...
    
    // Source 1
    auto source1 = storage.CreateComponent<UMatrixSource>("Source1");
    source1->FileName = "data1.csv";
    source1->Default();
    source1->Build();
    
    // Source 2
    auto source2 = storage.CreateComponent<UMatrixSource>("Source2");
    source2->FileName = "data2.csv";
    source2->Default();
    source2->Build();
    
    // Processor 1
    auto processor1 = storage.CreateComponent<UStatisticDoubleMatrix>("Processor1");
    processor1->InputData.AttachTo(&source1->OutputMatrix);
    processor1->Default();
    processor1->Build();
    
    // Processor 2
    auto processor2 = storage.CreateComponent<UStatisticDoubleMatrix>("Processor2");
    processor2->InputData.AttachTo(&source2->OutputMatrix);
    processor2->Default();
    processor2->Build();
    
    // Aggregator (using container)
    auto aggregator = storage.CreateComponent<UNet>("Aggregator");
    aggregator->Default();
    aggregator->Build();
    
    // Execute
    for (int i = 0; i < 100; i++) {
        source1->Calculate();
        source2->Calculate();
        processor1->Calculate();
        processor2->Calculate();
    }
}
```

### Using Configuration File

See [Bin/Docs/Examples/Config-Example.md](../Bin/Docs/Examples/Config-Example.md) for example of creating network via XML configuration.

### Related Documentation

- [Components-And-Configuration/Component-System.md](../Components-And-Configuration/Component-System.md) - component system
- [Rdk-Core/Engine-Architecture.md](../Rdk-Core/Engine-Architecture.md) - engine architecture
- [Bin/Docs/Examples/Config-Example.md](../Bin/Docs/Examples/Config-Example.md) - configuration examples
