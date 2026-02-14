# Best Practices - Лучшие практики

## RU

### Назначение

Этот документ агрегирует лучшие практики разработки для проекта Nmsdk из различных источников документации.

### Общие принципы разработки

1. **Следование архитектуре** - используйте существующие паттерны и структуры
2. **Документирование** - документируйте все публичные API и важные решения
3. **Тестирование** - создавайте тесты для новой функциональности
4. **Производительность** - учитывайте производительность с самого начала

### Разработка компонентов

#### Инициализация свойств

- Всегда инициализируйте свойства в конструкторе
- Устанавливайте значения по умолчанию в `ADefault()`
- Валидируйте параметры в `ABuild()`

**Пример:**
```cpp
MyComponent::MyComponent()
    : UContainer()
    , MyParam("MyParam", this, 1.0, nullptr, false)
{
}

bool MyComponent::ADefault(void) {
    if (!UContainer::ADefault())
        return false;
    MyParam = 1.0; // Значение по умолчанию
    return true;
}

bool MyComponent::ABuild(void) {
    if (!UContainer::ABuild())
        return false;
    // Валидация
    if (MyParam() < 0.0) {
        Logger->LogMessageEx(RDK_EX_ERROR, GetName(), __FUNCTION__,
                            "MyParam must be positive");
        return false;
    }
    return true;
}
```

**См. также:**
- [Component Development Guide](Rdk/Docs/Guides/Component-Development.md) - детальное руководство
- [Rdk/Docs/Guides/Creating-Components.md](../Rdk/Docs/Guides/Creating-Components.md) - создание компонентов

#### Управление памятью

- Используйте `UEPtr` для подкомпонентов
- Избегайте выделения памяти в `ACalculate()` - используйте буферы как члены класса
- Очищайте ресурсы в деструкторе

**Пример:**
```cpp
class OptimizedComponent : public UContainer {
private:
    std::vector<double> Buffer; // Буфер как член класса
    
protected:
    virtual bool ADefault(void) override {
        Buffer.reserve(1000); // Резервирование один раз
        return true;
    }
    
    virtual bool ACalculate(void) override {
        Buffer.clear(); // Очистка без перевыделения
        // Использование буфера
        return true;
    }
};
```

**См. также:**
- [Performance-And-Testing/Performance-Overview.md](Performance-And-Testing/Performance-Overview.md) - производительность
- [Troubleshooting/Troubleshooting-Guide.md](Troubleshooting/Troubleshooting-Guide.md) - проблемы с памятью

#### Обработка ошибок

- Всегда проверяйте возвращаемые значения базовых методов
- Используйте `RDK_THROW` для генерации исключений
- Логируйте ошибки через `Logger->LogMessageEx()`
- Возвращайте `false` из методов жизненного цикла при ошибках

**Пример:**
```cpp
virtual bool ACalculate(void) override {
    if (!IsReady()) {
        Logger->LogMessageEx(RDK_EX_WARNING, GetName(), __FUNCTION__,
                            "Component not ready");
        return false;
    }
    
    try {
        // Вычисления
        PerformCalculations();
    } catch (const RDK::UException& ex) {
        Logger->LogMessageEx(RDK_EX_ERROR, GetName(), __FUNCTION__,
                            std::string("RDK Exception: ") + ex.what());
        return false;
    }
    
    return true;
}
```

**См. также:**
- [Rdk/Docs/Guides/Error-Handling.md](../Rdk/Docs/Guides/Error-Handling.md) - обработка ошибок

#### Потокобезопасность

- Для многопоточного использования используйте `thread_safe=true` при создании свойств
- Используйте мьютексы для защиты критических секций
- Избегайте глобальных состояний

**Пример:**
```cpp
// Потокобезопасное свойство
UProperty<double, MyComponent, ptPubState> SafeData;

MyComponent::MyComponent()
    : SafeData("SafeData", this, 0.0, nullptr, true) // thread_safe=true
{
}
```

**См. также:**
- [Rdk/Docs/Guides/Threading-Guide.md](../Rdk/Docs/Guides/Threading-Guide.md) - многопоточность
- [Rdk/Docs/Examples/Threading-Example.md](../Rdk/Docs/Examples/Threading-Example.md) - пример

### Производительность

#### Кэширование результатов

- Кэшируйте результаты дорогих вычислений
- Инвалидируйте кэш при изменении входных данных
- Используйте флаги валидности кэша

**Пример:**
```cpp
class CachedComponent : public UContainer {
private:
    double LastInput;
    double CachedOutput;
    bool CacheValid;

protected:
    virtual bool AReset(void) override {
        CacheValid = false; // Инвалидация кэша
        return true;
    }
    
    virtual bool ACalculate(void) override {
        if (CacheValid && Input() == LastInput) {
            Output = CachedOutput;
            return true;
        }
        
        // Вычисление только при изменении
        double result = ExpensiveCalculation(Input());
        LastInput = Input();
        CachedOutput = result;
        CacheValid = true;
        Output = result;
        return true;
    }
};
```

**См. также:**
- [Performance-And-Testing/Performance-Overview.md](Performance-And-Testing/Performance-Overview.md) - производительность

#### Избегание выделения памяти

- Используйте буферы как члены класса
- Резервируйте память в `ADefault()` или `ABuild()`
- Переиспользуйте буферы в `ACalculate()`

**См. также:**
- [Troubleshooting/Troubleshooting-Guide.md](Troubleshooting/Troubleshooting-Guide.md) - проблемы производительности

### Тестирование

#### Unit тесты

- Создавайте unit тесты для каждого компонента
- Тестируйте все методы жизненного цикла
- Тестируйте обработку ошибок
- Тестируйте граничные случаи

**Пример:**
```cpp
#include <gtest/gtest.h>

TEST(MyComponentTest, DefaultTest) {
    UStorage storage;
    auto comp = storage.CreateComponent<MyComponent>("Test");
    comp->Default();
    EXPECT_EQ(comp->MyParam(), 1.0); // Проверка значения по умолчанию
}
```

**См. также:**
- [Performance-And-Testing/Testing-Strategy.md](Performance-And-Testing/Testing-Strategy.md) - стратегия тестирования
- [Rdk/Docs/Tests.md](../Rdk/Docs/Tests.md) - структура тестов

### Сериализация

#### Версионирование

- Всегда добавляйте версию при сериализации
- Реализуйте миграцию для старых версий
- Валидируйте загруженные данные

**Пример:**
```cpp
virtual bool Save(USerStorageXML &xml) override {
    xml.Add("Version", 2); // Текущая версия
    // Сохранение данных
    return true;
}

virtual bool Load(USerStorageXML &xml) override {
    int version = xml.GetInt("Version", 1);
    if (version >= 2) {
        // Загрузка новой версии
    } else {
        // Миграция старой версии
        MigrateFromVersion1(xml);
    }
    return true;
}
```

**См. также:**
- [Rdk/Docs/Guides/Serialization-Guide.md](../Rdk/Docs/Guides/Serialization-Guide.md) - сериализация
- [Rdk/Docs/Examples/Serialization-Example.md](../Rdk/Docs/Examples/Serialization-Example.md) - пример

### Документация

#### Структура документации компонента

- Назначение компонента
- UML диаграммы (классы, последовательность, состояния)
- Описание свойств
- Описание методов
- Примеры использования

**См. также:**
- [Overview/Component-Doc-Template.md](Overview/Component-Doc-Template.md) - шаблон документации
- [Rdk-BasicLib/Docs/README.md](../Libraries/Rdk-BasicLib/Docs/README.md) - пример структуры

### Анти-паттерны (что не делать)

#### ❌ Не создавайте компоненты без регистрации

```cpp
// ❌ Неправильно
MyComponent* comp = new MyComponent();
comp->Calculate(); // Ошибка: Id=0

// ✅ Правильно
auto comp = storage->CreateComponent<MyComponent>("MyComp");
comp->Default();
comp->Build();
comp->Calculate();
```

#### ❌ Не выделяйте память в ACalculate()

```cpp
// ❌ Неправильно
virtual bool ACalculate(void) override {
    std::vector<double> buffer(1000); // Выделение каждый раз
    // ...
}

// ✅ Правильно
class MyComponent : public UContainer {
private:
    std::vector<double> Buffer; // Буфер как член класса
};
```

#### ❌ Не игнорируйте ошибки

```cpp
// ❌ Неправильно
virtual bool ACalculate(void) override {
    try {
        PerformCalculation();
    } catch (...) {
        // Пустой catch - скрывает ошибки
    }
    return true;
}

// ✅ Правильно
virtual bool ACalculate(void) override {
    try {
        PerformCalculation();
    } catch (const RDK::UException& ex) {
        Logger->LogMessageEx(RDK_EX_ERROR, GetName(), __FUNCTION__,
                            ex.what());
        return false;
    }
    return true;
}
```

### Дополнительные ресурсы

- [Component Development Guide](Rdk/Docs/Guides/Component-Development.md) - детальное руководство по разработке компонентов
- [Development-Guides/Library-Development.md](Development-Guides/Library-Development.md) - разработка библиотек
- [Rdk/Docs/Guides/](../Rdk/Docs/Guides/) - руководства по Rdk Core
- [Performance-And-Testing/Performance-Overview.md](Performance-And-Testing/Performance-Overview.md) - производительность

---

## EN

### Purpose

This document aggregates best practices for Nmsdk project development from various documentation sources.

### General Development Principles

1. **Follow Architecture** - use existing patterns and structures
2. **Documentation** - document all public APIs and important decisions
3. **Testing** - create tests for new functionality
4. **Performance** - consider performance from the start

### Component Development

#### Property Initialization

- Always initialize properties in constructor
- Set default values in `ADefault()`
- Validate parameters in `ABuild()`

**Example:**
```cpp
MyComponent::MyComponent()
    : UContainer()
    , MyParam("MyParam", this, 1.0, nullptr, false)
{
}

bool MyComponent::ADefault(void) {
    if (!UContainer::ADefault())
        return false;
    MyParam = 1.0; // Default value
    return true;
}
```

**See Also:**
- [Development-Guides/Component-Development.md](Development-Guides/Component-Development.md) - detailed guide
- [Rdk/Docs/Guides/Creating-Components.md](../Rdk/Docs/Guides/Creating-Components.md) - creating components

#### Memory Management

- Use `UEPtr` for subcomponents
- Avoid memory allocation in `ACalculate()` - use buffers as class members
- Clean up resources in destructor

**See Also:**
- [Performance-And-Testing/Performance-Overview.md](Performance-And-Testing/Performance-Overview.md) - performance
- [Troubleshooting/Troubleshooting-Guide.md](Troubleshooting/Troubleshooting-Guide.md) - memory issues

#### Error Handling

- Always check return values of base methods
- Use `RDK_THROW` to generate exceptions
- Log errors through `Logger->LogMessageEx()`
- Return `false` from lifecycle methods on errors

**See Also:**
- [Rdk/Docs/Guides/Error-Handling.md](../Rdk/Docs/Guides/Error-Handling.md) - error handling

#### Thread Safety

- For multithreaded use, use `thread_safe=true` when creating properties
- Use mutexes to protect critical sections
- Avoid global state

**See Also:**
- [Rdk/Docs/Guides/Threading-Guide.md](../Rdk/Docs/Guides/Threading-Guide.md) - multithreading
- [Rdk/Docs/Examples/Threading-Example.md](../Rdk/Docs/Examples/Threading-Example.md) - example

### Performance

#### Result Caching

- Cache results of expensive calculations
- Invalidate cache when input data changes
- Use cache validity flags

**See Also:**
- [Performance-And-Testing/Performance-Overview.md](Performance-And-Testing/Performance-Overview.md) - performance

#### Avoiding Memory Allocation

- Use buffers as class members
- Reserve memory in `ADefault()` or `ABuild()`
- Reuse buffers in `ACalculate()`

**See Also:**
- [Troubleshooting/Troubleshooting-Guide.md](Troubleshooting/Troubleshooting-Guide.md) - performance issues

### Testing

#### Unit Tests

- Create unit tests for each component
- Test all lifecycle methods
- Test error handling
- Test edge cases

**See Also:**
- [Performance-And-Testing/Testing-Strategy.md](Performance-And-Testing/Testing-Strategy.md) - testing strategy
- [Rdk/Docs/Tests.md](../Rdk/Docs/Tests.md) - test structure

### Serialization

#### Versioning

- Always add version when serializing
- Implement migration for old versions
- Validate loaded data

**See Also:**
- [Rdk/Docs/Guides/Serialization-Guide.md](../Rdk/Docs/Guides/Serialization-Guide.md) - serialization
- [Rdk/Docs/Examples/Serialization-Example.md](../Rdk/Docs/Examples/Serialization-Example.md) - example

### Documentation

#### Component Documentation Structure

- Component purpose
- UML diagrams (classes, sequence, states)
- Property descriptions
- Method descriptions
- Usage examples

**See Also:**
- [Overview/Component-Doc-Template.md](Overview/Component-Doc-Template.md) - documentation template
- [Rdk-BasicLib/Docs/README.md](../Libraries/Rdk-BasicLib/Docs/README.md) - structure example

### Anti-Patterns (What Not to Do)

#### ❌ Don't Create Components Without Registration

```cpp
// ❌ Wrong
MyComponent* comp = new MyComponent();
comp->Calculate(); // Error: Id=0

// ✅ Correct
auto comp = storage->CreateComponent<MyComponent>("MyComp");
comp->Default();
comp->Build();
comp->Calculate();
```

#### ❌ Don't Allocate Memory in ACalculate()

```cpp
// ❌ Wrong
virtual bool ACalculate(void) override {
    std::vector<double> buffer(1000); // Allocation every time
    // ...
}

// ✅ Correct
class MyComponent : public UContainer {
private:
    std::vector<double> Buffer; // Buffer as class member
};
```

#### ❌ Don't Ignore Errors

```cpp
// ❌ Wrong
virtual bool ACalculate(void) override {
    try {
        PerformCalculation();
    } catch (...) {
        // Empty catch - hides errors
    }
    return true;
}

// ✅ Correct
virtual bool ACalculate(void) override {
    try {
        PerformCalculation();
    } catch (const RDK::UException& ex) {
        Logger->LogMessageEx(RDK_EX_ERROR, GetName(), __FUNCTION__,
                            ex.what());
        return false;
    }
    return true;
}
```

### Additional Resources

- [Development-Guides/Component-Development.md](Development-Guides/Component-Development.md) - detailed component development guide
- [Development-Guides/Library-Development.md](Development-Guides/Library-Development.md) - library development
- [Rdk/Docs/Guides/](../Rdk/Docs/Guides/) - Rdk Core guides
- [Performance-And-Testing/Performance-Overview.md](Performance-And-Testing/Performance-Overview.md) - performance
