# Кроссплатформенная поддержка (Cross-Platform Support)

## RU

### Обзор

Nmsdk поддерживает сборку и выполнение на различных платформах благодаря системе абстракций в `Rdk/Core/System`.

### Поддерживаемые платформы

- **Linux** - основная платформа, полная поддержка
- **Windows** - полная поддержка через Qt и WinAPI
- **Borland C++ Builder** - поддержка для legacy приложений

### Системные абстракции

Абстракции в `Rdk/Core/System` обеспечивают единый интерфейс для:
- Потоков и синхронизации (`UGenericMutex`, `UGenericEvent`)
- Файловых операций (`rdk_system.h`)
- Загрузки библиотек (`UDllLoader`)
- Системных утилит

### Платформенные реализации

Реализации выбираются на этапе сборки через CMake:
- `System/Qt` - кроссплатформенная реализация на Qt
- `System/Win` - реализация для Windows
- `System/Gcc` - реализация для GCC/POSIX
- `System/BCB` - реализация для Borland C++ Builder
- `System/ANSI` - fallback реализация

### См. также

- [System Platform Abstraction](../Rdk/Docs/Architecture/System-Platform-Abstraction.md) - детальное описание абстракций
- [Build System](Build-System.md)
- [Reports/11-Cross-Platform-Support.md](../../Reports/11-Cross-Platform-Support.md) - детальное описание

---

## EN

### Overview

Nmsdk supports building and execution on various platforms thanks to the abstraction system in `Rdk/Core/System`.

### Supported Platforms

- **Linux** - primary platform, full support
- **Windows** - full support via Qt and WinAPI
- **Borland C++ Builder** - support for legacy applications

### System Abstractions

Abstractions in `Rdk/Core/System` provide a unified interface for:
- Threading and synchronization (`UGenericMutex`, `UGenericEvent`)
- File operations (`rdk_system.h`)
- Library loading (`UDllLoader`)
- System utilities

### Platform Implementations

Implementations are selected at build time through CMake.

### See Also

- [System Platform Abstraction](../Rdk-Core/System-Platform-Abstraction.md) - detailed abstraction description
- [Build System](Build-System.md)
- [Reports/11-Cross-Platform-Support.md](../../Reports/11-Cross-Platform-Support.md) - detailed description
