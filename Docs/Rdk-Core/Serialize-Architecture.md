# Архитектура сериализации (Serialization Architecture)

## RU

### Обзор

Модуль `Rdk/Core/Serialize` предоставляет систему сериализации данных и компонентов в различных форматах.

### Основные компоненты

#### USerStorage

Базовое хранилище данных для сериализации.

**Основные функции:**
- Сохранение и загрузка данных
- Управление форматами сериализации

#### USerStorageXML

XML хранилище для человекочитаемого формата.

**Основные функции:**
- Сериализация в XML
- Десериализация из XML
- Валидация XML структуры

#### USerStorageBinary

Бинарное хранилище для эффективного хранения.

**Основные функции:**
- Бинарная сериализация
- Бинарная десериализация
- Оптимизация размера данных

### Форматы сериализации

#### XML сериализация

Используется для:
- Конфигурационных файлов
- Проектов
- Человекочитаемых данных

**Пример структуры:**

```xml
<Component>
  <Name>MyComponent</Name>
  <Properties>
    <Property name="Value" type="double">42.0</Property>
  </Properties>
</Component>
```

#### Бинарная сериализация

Используется для:
- Эффективного хранения больших объемов данных
- Быстрой загрузки проектов
- Оптимизации производительности

### Сериализация компонентов

#### UXMLEnvSerialize

XML сериализация окружения и компонентов.

**Основные функции:**
- Сериализация компонентов в XML
- Сериализация контейнеров
- Сериализация сетей компонентов

#### UBinaryEnvSerialize

Бинарная сериализация окружения и компонентов.

**Основные функции:**
- Бинарная сериализация компонентов
- Бинарная сериализация контейнеров
- Оптимизация размера

### Сериализация свойств

Свойства компонентов автоматически сериализуются при сохранении компонента.

**Типы сериализуемых свойств:**
- Параметры (`ptParameter`)
- Состояния (`ptState`)
- Входы и выходы (`ptInput`, `ptOutput`)

### См. также

- [Engine Architecture](Engine-Architecture.md)
- [Component System](../Components-And-Configuration/Component-System.md)
- [Rdk Core Overview](Overview.md)

---

## EN

### Overview

The `Rdk/Core/Serialize` module provides a serialization system for data and components in various formats.

### Main Components

#### USerStorage

Base data storage for serialization.

#### USerStorageXML

XML storage for human-readable format.

#### USerStorageBinary

Binary storage for efficient storage.

### Serialization Formats

#### XML Serialization

Used for:
- Configuration files
- Projects
- Human-readable data

#### Binary Serialization

Used for:
- Efficient storage of large data volumes
- Fast project loading
- Performance optimization

### Component Serialization

#### UXMLEnvSerialize

XML serialization of environment and components.

#### UBinaryEnvSerialize

Binary serialization of environment and components.

### Property Serialization

Component properties are automatically serialized when saving a component.

### See Also

- [Engine Architecture](Engine-Architecture.md)
- [Component System](../Components-And-Configuration/Component-System.md)
- [Rdk Core Overview](Overview.md)
