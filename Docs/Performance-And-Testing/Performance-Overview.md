# Обзор производительности (Performance Overview)

## RU

### Обзор

Оптимизации производительности и результаты бенчмарков проекта Nmsdk.

### Основные оптимизации

- Оптимизация доступа к свойствам компонентов
- Кэширование активных компонентов
- Оптимизация вычислений в движке

### Поток данных в критичных участках

#### Оптимизированный доступ к свойствам

```mermaid
flowchart TB
    Component[UComponent]
    PropertyCache[Кэш свойств]
    DirectAccess[Прямой доступ]
    Property[UProperty]
    
    Component --> PropertyCache
    PropertyCache --> DirectAccess
    DirectAccess --> Property
    
    style PropertyCache fill:#10B981,color:#fff
    style DirectAccess fill:#10B981,color:#fff
```

**Оптимизация:** Кэширование указателей на свойства для избежания поиска по имени на каждом обращении.

#### Кэширование активных компонентов

```mermaid
sequenceDiagram
    participant Container as UContainer
    participant Cache as ActiveComponentsCache
    participant Comp1 as Component1
    participant Comp2 as Component2
    
    Container->>Cache: UpdateActiveComponentsCache()
    Cache->>Cache: Фильтрация активных компонентов
    
    loop Вычисление
        Container->>Cache: GetActiveComponents()
        Cache->>Comp1: ACalculate()
        Cache->>Comp2: ACalculate()
    end
```

**Оптимизация:** Кэширование списка активных компонентов для избежания повторной фильтрации на каждом шаге.

#### Оптимизация вычислений движка

```mermaid
flowchart LR
    Env[UEnvironment]
    Order[ComputationOrder]
    Comp1[Component1]
    Comp2[Component2]
    Comp3[Component3]
    
    Env --> Order
    Order --> Comp1
    Comp1 --> Comp2
    Comp2 --> Comp3
    
    style Order fill:#5B8DEF,color:#fff
```

**Оптимизация:** Предварительное вычисление порядка выполнения компонентов для минимизации зависимостей.

### Бенчмарки

Результаты бенчмарков доступны в отчетах:
- [Performance_Benchmarks_GetData_Optimization.md](../../Reports/Performance_Benchmarks_GetData_Optimization.md)
- [Reports/Performance/](../../Reports/Performance/)

### См. также

- [Testing Strategy](Testing-Strategy.md)
- [Direct Property Access](../Components-And-Configuration/Direct-Property-Access.md)

---

## EN

### Overview

Performance optimizations and benchmark results for the Nmsdk project.

### Main Optimizations

- Component property access optimization
- Active component caching
- Engine computation optimization

### Data Flow in Critical Sections

#### Optimized Property Access

```mermaid
flowchart TB
    Component[UComponent]
    PropertyCache[Property Cache]
    DirectAccess[Direct Access]
    Property[UProperty]
    
    Component --> PropertyCache
    PropertyCache --> DirectAccess
    DirectAccess --> Property
    
    style PropertyCache fill:#10B981,color:#fff
    style DirectAccess fill:#10B981,color:#fff
```

**Optimization:** Caching property pointers to avoid name-based lookup on each access.

#### Active Component Caching

```mermaid
sequenceDiagram
    participant Container as UContainer
    participant Cache as ActiveComponentsCache
    participant Comp1 as Component1
    participant Comp2 as Component2
    
    Container->>Cache: UpdateActiveComponentsCache()
    Cache->>Cache: Filter active components
    
    loop Calculation
        Container->>Cache: GetActiveComponents()
        Cache->>Comp1: ACalculate()
        Cache->>Comp2: ACalculate()
    end
```

**Optimization:** Caching list of active components to avoid repeated filtering on each step.

#### Engine Computation Optimization

```mermaid
flowchart LR
    Env[UEnvironment]
    Order[ComputationOrder]
    Comp1[Component1]
    Comp2[Component2]
    Comp3[Component3]
    
    Env --> Order
    Order --> Comp1
    Comp1 --> Comp2
    Comp2 --> Comp3
    
    style Order fill:#5B8DEF,color:#fff
```

**Optimization:** Pre-computing component execution order to minimize dependencies.

### Benchmarks

Benchmark results available in reports:
- [Performance_Benchmarks_GetData_Optimization.md](../../Reports/Performance_Benchmarks_GetData_Optimization.md)
- [Reports/Performance/](../../Reports/Performance/)

### See Also

- [Testing Strategy](Testing-Strategy.md)
- [Direct Property Access](../Components-And-Configuration/Direct-Property-Access.md)
