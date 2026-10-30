# Пример: Оптимизация производительности

## RU

### Описание задачи

Оптимизировать компонент для улучшения производительности вычислений.

### Решение

#### Проблема: Медленные вычисления

Исходный код:
```cpp
class SlowComponent : public UContainer {
protected:
    virtual bool ACalculate(void) override {
        // Выделение памяти каждый раз
        std::vector<double> buffer(1000);
        
        // Дорогие вычисления без кэширования
        double result = ExpensiveCalculation(Input());
        Output = result;
        
        return true;
    }
};
```

#### Оптимизированное решение

```cpp
class OptimizedComponent : public UContainer {
private:
    // Буфер как член класса
    std::vector<double> Buffer;
    
    // Кэш результатов
    double LastInput;
    double CachedOutput;
    bool CacheValid;

protected:
    virtual bool ADefault(void) override {
        if (!UContainer::ADefault())
            return false;
        
        // Резервирование памяти один раз
        Buffer.reserve(1000);
        CacheValid = false;
        
        return true;
    }
    
    virtual bool AReset(void) override {
        if (!UContainer::AReset())
            return false;
        
        // Инвалидация кэша при сбросе
        CacheValid = false;
        
        return true;
    }
    
    virtual bool ACalculate(void) override {
        if (!IsReady())
            return false;
        
        // Очистка буфера без перевыделения
        Buffer.clear();
        
        // Проверка кэша
        if (CacheValid && Input() == LastInput) {
            Output = CachedOutput;
            return true;
        }
        
        // Вычисление только при изменении входных данных
        double result = ExpensiveCalculation(Input());
        LastInput = Input();
        CachedOutput = result;
        CacheValid = true;
        Output = result;
        
        return true;
    }
};
```

### Объяснение оптимизаций

1. **Буфер как член класса** - избегаем выделения памяти в каждом вызове
2. **Кэширование результатов** - переиспользуем результаты при неизменных входных данных
3. **Резервирование памяти** - выделяем память один раз в `ADefault()`

### Связанная документация

- [Performance-And-Testing/Performance-Overview.md](../Performance-And-Testing/Performance-Overview.md) - обзор производительности
- [Troubleshooting/Troubleshooting-Guide.md](../Troubleshooting/Troubleshooting-Guide.md) - проблемы производительности
- [Best-Practices.md](../Best-Practices.md) - лучшие практики

---

## EN

### Task Description

Optimize a component to improve computation performance.

### Solution

#### Problem: Slow Computations

Original code:
```cpp
class SlowComponent : public UContainer {
protected:
    virtual bool ACalculate(void) override {
        // Memory allocation every time
        std::vector<double> buffer(1000);
        
        // Expensive calculations without caching
        double result = ExpensiveCalculation(Input());
        Output = result;
        
        return true;
    }
};
```

#### Optimized Solution

```cpp
class OptimizedComponent : public UContainer {
private:
    // Buffer as class member
    std::vector<double> Buffer;
    
    // Result cache
    double LastInput;
    double CachedOutput;
    bool CacheValid;

protected:
    virtual bool ADefault(void) override {
        if (!UContainer::ADefault())
            return false;
        
        // Reserve memory once
        Buffer.reserve(1000);
        CacheValid = false;
        
        return true;
    }
    
    virtual bool AReset(void) override {
        if (!UContainer::AReset())
            return false;
        
        // Invalidate cache on reset
        CacheValid = false;
        
        return true;
    }
    
    virtual bool ACalculate(void) override {
        if (!IsReady())
            return false;
        
        // Clear buffer without reallocation
        Buffer.clear();
        
        // Check cache
        if (CacheValid && Input() == LastInput) {
            Output = CachedOutput;
            return true;
        }
        
        // Calculate only when input changes
        double result = ExpensiveCalculation(Input());
        LastInput = Input();
        CachedOutput = result;
        CacheValid = true;
        Output = result;
        
        return true;
    }
};
```

### Optimization Explanations

1. **Buffer as Class Member** - avoid memory allocation in each call
2. **Result Caching** - reuse results when input data is unchanged
3. **Memory Reservation** - allocate memory once in `ADefault()`

### Related Documentation

- [Performance-And-Testing/Performance-Overview.md](../Performance-And-Testing/Performance-Overview.md) - performance overview
- [Troubleshooting/Troubleshooting-Guide.md](../Troubleshooting/Troubleshooting-Guide.md) - performance issues
- [Best-Practices.md](../Best-Practices.md) - best practices
