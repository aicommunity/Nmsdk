# Документация Nmsdk

## RU

Добро пожаловать в документацию проекта **Nmsdk (Neuro Modeler SDK)** - SDK для моделирования нейронных сетей и робототехнических систем.

### Быстрые ссылки

- [Быстрый старт](Overview/QuickStart.md) - начало работы с проектом
- [Обзор проекта](Overview/README.md) - общее описание проекта
- [FAQ](FAQ.md) - часто задаваемые вопросы
- [Getting Started](Getting-Started.md) - пути для разных ролей пользователей
- [Troubleshooting](Troubleshooting/Troubleshooting-Guide.md) - устранение неполадок
- [Documentation Audit](Audit/README.md) - отчёты аудита документации
- [DETAILED ClDesc / Favorites](ClDesc-Detailed-Methodology.md) — как курировать описания классов и избранные свойства
- [Генерация алиасов свойств](PropertyAliasGeneration.md) — автоген aliases vs primary Favorites

### Навигация

#### Общие разделы

- [Обзор проекта](Overview/README.md) - высокоуровневое описание Nmsdk, назначение, ключевые подсистемы
- [Быстрый старт](Overview/QuickStart.md) - быстрое начало работы с проектом
- [Getting Started](Getting-Started.md) - пути для разных ролей пользователей
- [FAQ](FAQ.md) - часто задаваемые вопросы
- [Структура исходников](Overview/File-Structure.md) - структура директорий и файлов проекта
- [Архитектура системы](Overview/Architecture-Overview.md) - верхнеуровневая архитектура с диаграммами

#### Основные компоненты

- [Rdk Core](../Rdk/Docs/Architecture/Overview.md) - ядро системы, движок, компонентная система
  - [Архитектура приложения](../Rdk/Docs/Architecture/Application-Architecture.md) - RPC, сервер, управление проектами
  - [Архитектура движка](../Rdk/Docs/Architecture/Engine-Architecture.md) - компоненты, контейнеры, свойства
  - [Графика](../Rdk/Docs/Architecture/Graphics-Architecture.md) - система графики и визуализации
  - [Сериализация](../Rdk/Docs/Architecture/Serialize-Architecture.md) - XML и бинарная сериализация
  - [Системные абстракции](../Rdk/Docs/Architecture/System-Platform-Abstraction.md) - кроссплатформенные абстракции

- [GUI](GUI/Overview.md) - графический интерфейс пользователя
  - [Справочник виджетов](GUI/Widgets-Reference.md) - описание основных виджетов
  - [Система стилей](GUI/Style-System.md) - темы и стилизация

#### Библиотеки

- [Обзор библиотек](Libraries/Overview.md) - все библиотеки компонентов
- [Rdk-BasicLib](Libraries/Rdk-BasicLib.md) - базовые компоненты
- [Rdk-CvBasicLib](Libraries/Rdk-CvBasicLib.md) - компьютерное зрение (OpenCV)
- [Rdk-HardwareLib](Libraries/Rdk-HardwareLib.md) - работа с аппаратным обеспечением
- [Nmsdk-PulseLib](Libraries/Nmsdk-PulseLib.md) - импульсные нейронные сети
- [Nmsdk-MotionControlLib](Libraries/Nmsdk-MotionControlLib.md) - управление движением

#### Сборка и развертывание

- [Система сборки](Build-And-Deploy/Build-System.md) - CMake, зависимости, процесс сборки
- [Кроссплатформенная поддержка](Build-And-Deploy/Cross-Platform.md) - Linux, Windows
- [Сборка на Windows](Build-And-Deploy/Build-Windows.md) - особенности сборки для Windows
- [Сборка на Linux](Build-And-Deploy/Build-Linux.md) - особенности сборки для Linux

#### Компоненты и конфигурация

- [Компонентная система](Components-And-Configuration/Component-System.md) - создание и использование компонентов
- [Конфигурационные файлы](Components-And-Configuration/Configuration-Files-Overview.md) - структура конфигов
- [Прямой доступ к свойствам](Components-And-Configuration/Direct-Property-Access.md) - оптимизация доступа к свойствам

#### Производительность и тестирование

- [Производительность](Performance-And-Testing/Performance-Overview.md) - оптимизации, бенчмарки
- [Стратегия тестирования](Performance-And-Testing/Testing-Strategy.md) - юнит и интеграционные тесты

#### История рефакторинга

- [Хронология рефакторинга](Refactoring-History/Refactoring-Timeline.md) - основные изменения
- [Извлеченные уроки](Refactoring-History/Lessons-Learned.md) - важные выводы и практики

#### Аудит и legacy

- [Documentation Audit](Audit/README.md) - отчёты и скрипты аудита
- [Reports/](../Reports/README.md) - исторические отчёты разработки (archive)
- [Docs.old/](../Docs.old/) - устаревшие `.doc` и Doxygen-артефакты (не поддерживаются)

### Документация в сабрепозиториях

#### Rdk Core (Ядро системы)

- [Обзор документации](../Rdk/Docs/README.md) - главная страница документации Rdk
- [Архитектура](../Rdk/Docs/Architecture.md) - детальное описание архитектуры
- [Архитектурные диаграммы](../Rdk/Docs/Architecture-Diagrams.md) - обзорные диаграммы
- [API Справочник](../Rdk/Docs/API-Reference.md) - полный справочник API
- [Детальная документация модулей](../Rdk/Docs/) - Engine, Application, Graphics, Serialize, System
  - [Движок](../Rdk/Docs/Engine-Detailed.md) - компоненты, свойства, контроллеры
  - [Приложение](../Rdk/Docs/Application-Detailed.md) - RPC, проекты, сервер
  - [Графика](../Rdk/Docs/Graphics-Detailed.md) - графика, шрифты, отрисовка
  - [Сериализация](../Rdk/Docs/Serialize-Detailed.md) - XML, Binary сериализация
  - [Система](../Rdk/Docs/System-Detailed.md) - мьютексы, события, загрузка библиотек
- [Справочники](../Rdk/Docs/) - Math, Utilities, Logging
  - [Математические библиотеки](../Rdk/Docs/Math-Libraries-Reference.md) - матрицы, векторы, фильтры Калмана
  - [Утилиты](../Rdk/Docs/Utilities-Reference.md) - исключения, файлы, временные метки
  - [Система логирования](../Rdk/Docs/Logging-System.md) - логирование
- [Руководства](../Rdk/Docs/Guides/) - создание компонентов, свойств, контроллеров
  - [Создание компонентов](../Rdk/Docs/Guides/Creating-Components.md)
  - [Создание свойств](../Rdk/Docs/Guides/Creating-Properties.md)
  - [Создание контроллеров](../Rdk/Docs/Guides/Creating-Controllers.md)
  - [Сериализация](../Rdk/Docs/Guides/Serialization-Guide.md)
  - [RPC интеграция](../Rdk/Docs/Guides/RPC-Integration.md)
  - [Многопоточность](../Rdk/Docs/Guides/Threading-Guide.md)
  - [Обработка ошибок](../Rdk/Docs/Guides/Error-Handling.md)
- [Диаграммы](../Rdk/Docs/Diagrams/) - жизненный цикл, свойства, RPC
  - [Жизненный цикл компонента](../Rdk/Docs/Diagrams/Component-Lifecycle.md)
  - [Система свойств](../Rdk/Docs/Diagrams/Property-System.md)
  - [Поток RPC](../Rdk/Docs/Diagrams/RPC-Flow.md)
- [Полный индекс документации Rdk](Submodules/Rdk-Index.md)

#### Bin (Ресурсы и конфигурации)

- [Обзор документации](../Bin/Docs/README.md) - главная страница документации Bin
- [Структура конфигураций](../Bin/Docs/Configs-Structure.md) - описание конфигурационных файлов
- [Структура справки](../Bin/Docs/Help-Structure.md) - структура справочной системы
- [Полный индекс документации Bin](Submodules/Bin-Index.md)

#### Библиотеки компонентов

##### Nmsdk-PulseLib
- [Обзор](../Libraries/Nmsdk-PulseLib/Docs/README.md) - главная страница документации
- [Архитектура](../Libraries/Nmsdk-PulseLib/Docs/Architecture.md) - архитектура библиотеки
- [Каталог компонентов](../Libraries/Nmsdk-PulseLib/Docs/Component-Catalog.md) - список всех компонентов
- [Примеры использования](../Libraries/Nmsdk-PulseLib/Docs/Usage-Examples.md) - практические примеры
- [API Обзор](../Libraries/Nmsdk-PulseLib/Docs/API-Overview.md) - обзор API
- [Обзор конфигураций](../Libraries/Nmsdk-PulseLib/Docs/Config-Overview.md) - конфигурационные проекты
- [Шаблоны конфигураций](../Libraries/Nmsdk-PulseLib/Docs/Config-Templates.md) - шаблоны экспериментов
- [Научный фон](../Libraries/Nmsdk-PulseLib/Docs/Scientific-Background.md) - связанные публикации
- [Документация компонентов](../Libraries/Nmsdk-PulseLib/Docs/Components/) - детальная документация по каждому компоненту

##### Nmsdk-MotionControlLib
- [Обзор](../Libraries/Nmsdk-MotionControlLib/Docs/README.md) - главная страница документации
- [Архитектура](../Libraries/Nmsdk-MotionControlLib/Docs/Architecture.md) - архитектура библиотеки
- [Каталог компонентов](../Libraries/Nmsdk-MotionControlLib/Docs/Component-Catalog.md) - список всех компонентов
- [Примеры использования](../Libraries/Nmsdk-MotionControlLib/Docs/Usage-Examples.md) - практические примеры
- [API Обзор](../Libraries/Nmsdk-MotionControlLib/Docs/API-Overview.md) - обзор API
- [Документация компонентов](../Libraries/Nmsdk-MotionControlLib/Docs/Components/) - детальная документация по каждому компоненту

##### Rdk-BasicLib
- [Обзор](../Libraries/Rdk-BasicLib/Docs/README.md) - главная страница документации
- [Архитектура](../Libraries/Rdk-BasicLib/Docs/Architecture.md) - архитектура библиотеки
- [Каталог компонентов](../Libraries/Rdk-BasicLib/Docs/Component-Catalog.md) - список всех компонентов
- [Примеры использования](../Libraries/Rdk-BasicLib/Docs/Usage-Examples.md) - практические примеры
- [API Обзор](../Libraries/Rdk-BasicLib/Docs/API-Overview.md) - обзор API
- [Документация компонентов](../Libraries/Rdk-BasicLib/Docs/Components/) - детальная документация по каждому компоненту

##### Rdk-CvBasicLib
- [Обзор](../Libraries/Rdk-CvBasicLib/Docs/README.md) - главная страница документации
- [Архитектура](../Libraries/Rdk-CvBasicLib/Docs/Architecture.md) - архитектура библиотеки
- [Каталог компонентов](../Libraries/Rdk-CvBasicLib/Docs/Component-Catalog.md) - список всех компонентов
- [Примеры использования](../Libraries/Rdk-CvBasicLib/Docs/Usage-Examples.md) - практические примеры
- [API Обзор](../Libraries/Rdk-CvBasicLib/Docs/API-Overview.md) - обзор API
- [Документация компонентов](../Libraries/Rdk-CvBasicLib/Docs/Components/) - детальная документация по каждому компоненту

##### Rdk-HardwareLib
- [Обзор](../Libraries/Rdk-HardwareLib/Docs/README.md) - главная страница документации
- [Архитектура](../Libraries/Rdk-HardwareLib/Docs/Architecture.md) - архитектура библиотеки
- [Каталог компонентов](../Libraries/Rdk-HardwareLib/Docs/Component-Catalog.md) - список всех компонентов
- [Примеры использования](../Libraries/Rdk-HardwareLib/Docs/Usage-Examples.md) - практические примеры
- [API Обзор](../Libraries/Rdk-HardwareLib/Docs/API-Overview.md) - обзор API
- [Документация компонентов](../Libraries/Rdk-HardwareLib/Docs/Components/) - детальная документация по каждому компоненту


- [Полный индекс документации библиотек](Submodules/Libraries-Index.md)
- [Навигационная карта документации](Submodules/Navigation-Map.md)

---

## EN

Welcome to the documentation of **Nmsdk (Neuro Modeler SDK)** - SDK for neural network modeling and robotics systems.

### Quick Links

- [Quick Start](Overview/QuickStart.md) - getting started with the project
- [Project Overview](Overview/README.md) - general project description
- [FAQ](FAQ.md) - frequently asked questions
- [Getting Started](Getting-Started.md) - paths for different user roles
- [Troubleshooting](Troubleshooting/Troubleshooting-Guide.md) - troubleshooting guide

### Navigation

#### General Sections

- [Project Overview](Overview/README.md) - high-level description of Nmsdk, purpose, key subsystems
- [Quick Start](Overview/QuickStart.md) - quick start with the project
- [Getting Started](Getting-Started.md) - paths for different user roles
- [FAQ](FAQ.md) - frequently asked questions
- [File Structure](Overview/File-Structure.md) - project directory and file structure
- [System Architecture](Overview/Architecture-Overview.md) - top-level architecture with diagrams

#### Core Components

- [Rdk Core](../Rdk/Docs/Architecture/Overview.md) - system core, engine, component system
  - [Application Architecture](../Rdk/Docs/Architecture/Application-Architecture.md) - RPC, server, project management
  - [Engine Architecture](../Rdk/Docs/Architecture/Engine-Architecture.md) - components, containers, properties
  - [Graphics](../Rdk/Docs/Architecture/Graphics-Architecture.md) - graphics and visualization system
  - [Serialization](../Rdk/Docs/Architecture/Serialize-Architecture.md) - XML and binary serialization
  - [System Abstractions](../Rdk/Docs/Architecture/System-Platform-Abstraction.md) - cross-platform abstractions

- [GUI](GUI/Overview.md) - graphical user interface
  - [Widgets Reference](GUI/Widgets-Reference.md) - description of main widgets
  - [Style System](GUI/Style-System.md) - themes and styling

#### Libraries

- [Libraries Overview](Libraries/Overview.md) - all component libraries
- [Rdk-BasicLib](Libraries/Rdk-BasicLib.md) - basic components
- [Rdk-CvBasicLib](Libraries/Rdk-CvBasicLib.md) - computer vision (OpenCV)
- [Rdk-HardwareLib](Libraries/Rdk-HardwareLib.md) - hardware integration
- [Nmsdk-PulseLib](Libraries/Nmsdk-PulseLib.md) - spiking neural networks
- [Nmsdk-MotionControlLib](Libraries/Nmsdk-MotionControlLib.md) - motion control

#### Build and Deploy

- [Build System](Build-And-Deploy/Build-System.md) - CMake, dependencies, build process
- [Cross-Platform Support](Build-And-Deploy/Cross-Platform.md) - Linux, Windows
- [Building on Windows](Build-And-Deploy/Build-Windows.md) - Windows-specific build details
- [Building on Linux](Build-And-Deploy/Build-Linux.md) - Linux-specific build details

#### Components and Configuration

- [Component System](../Rdk/Docs/Guides/Component-System.md) - creating and using components
- [Configuration Files](Components-And-Configuration/Configuration-Files-Overview.md) - config structure
- [Direct Property Access](Components-And-Configuration/Direct-Property-Access.md) - property access optimization

#### Reference Materials

- [Best Practices](Best-Practices.md) - development best practices
- [Glossary](Glossary.md) - glossary of terms
- [FAQ](FAQ.md) - frequently asked questions

#### Performance and Testing

- [Performance](Performance-And-Testing/Performance-Overview.md) - optimizations, benchmarks
- [Testing Strategy](Performance-And-Testing/Testing-Strategy.md) - unit and integration tests

#### Refactoring History

- [Refactoring Timeline](Refactoring-History/Refactoring-Timeline.md) - major changes
- [Lessons Learned](Refactoring-History/Lessons-Learned.md) - important insights and practices

#### Community and Support

- [Community](Community.md) - community and support
- [Examples](Examples/) - practical usage examples

### Documentation in Subrepositories

#### Rdk Core (System Core)

- [Documentation Overview](../Rdk/Docs/README.md) - main Rdk documentation page
- [Architecture](../Rdk/Docs/Architecture.md) - detailed architecture description
- [Architecture Diagrams](../Rdk/Docs/Architecture-Diagrams.md) - overview diagrams
- [API Reference](../Rdk/Docs/API-Reference.md) - complete API reference
- [Detailed Module Documentation](../Rdk/Docs/) - Engine, Application, Graphics, Serialize, System
  - [Engine](../Rdk/Docs/Engine-Detailed.md) - components, properties, controllers
  - [Application](../Rdk/Docs/Application-Detailed.md) - RPC, projects, server
  - [Graphics](../Rdk/Docs/Graphics-Detailed.md) - graphics, fonts, rendering
  - [Serialization](../Rdk/Docs/Serialize-Detailed.md) - XML, Binary serialization
  - [System](../Rdk/Docs/System-Detailed.md) - mutexes, events, library loading
- [References](../Rdk/Docs/) - Math, Utilities, Logging
  - [Math Libraries](../Rdk/Docs/Math-Libraries-Reference.md) - matrices, vectors, Kalman filters
  - [Utilities](../Rdk/Docs/Utilities-Reference.md) - exceptions, files, timestamps
  - [Logging System](../Rdk/Docs/Logging-System.md) - logging
- [Guides](../Rdk/Docs/Guides/) - creating components, properties, controllers
  - [Creating Components](../Rdk/Docs/Guides/Creating-Components.md)
  - [Creating Properties](../Rdk/Docs/Guides/Creating-Properties.md)
  - [Creating Controllers](../Rdk/Docs/Guides/Creating-Controllers.md)
  - [Serialization](../Rdk/Docs/Guides/Serialization-Guide.md)
  - [RPC Integration](../Rdk/Docs/Guides/RPC-Integration.md)
  - [Threading](../Rdk/Docs/Guides/Threading-Guide.md)
  - [Error Handling](../Rdk/Docs/Guides/Error-Handling.md)
- [Diagrams](../Rdk/Docs/Diagrams/) - lifecycle, properties, RPC
  - [Component Lifecycle](../Rdk/Docs/Diagrams/Component-Lifecycle.md)
  - [Property System](../Rdk/Docs/Diagrams/Property-System.md)
  - [RPC Flow](../Rdk/Docs/Diagrams/RPC-Flow.md)
- [Complete Rdk Documentation Index](Submodules/Rdk-Index.md)

#### Bin (Resources and Configurations)

- [Documentation Overview](../Bin/Docs/README.md) - main Bin documentation page
- [Configuration Structure](../Bin/Docs/Configs-Structure.md) - configuration files description
- [Help Structure](../Bin/Docs/Help-Structure.md) - help system structure
- [Complete Bin Documentation Index](Submodules/Bin-Index.md)

#### Component Libraries

##### Nmsdk-PulseLib
- [Overview](../Libraries/Nmsdk-PulseLib/Docs/README.md) - main documentation page
- [Architecture](../Libraries/Nmsdk-PulseLib/Docs/Architecture.md) - library architecture
- [Component Catalog](../Libraries/Nmsdk-PulseLib/Docs/Component-Catalog.md) - list of all components
- [Usage Examples](../Libraries/Nmsdk-PulseLib/Docs/Usage-Examples.md) - practical examples
- [API Overview](../Libraries/Nmsdk-PulseLib/Docs/API-Overview.md) - API overview
- [Configuration Overview](../Libraries/Nmsdk-PulseLib/Docs/Config-Overview.md) - configuration projects
- [Configuration Templates](../Libraries/Nmsdk-PulseLib/Docs/Config-Templates.md) - experiment templates
- [Scientific Background](../Libraries/Nmsdk-PulseLib/Docs/Scientific-Background.md) - related publications
- [Component Documentation](../Libraries/Nmsdk-PulseLib/Docs/Components/) - detailed documentation for each component

##### Nmsdk-MotionControlLib
- [Overview](../Libraries/Nmsdk-MotionControlLib/Docs/README.md) - main documentation page
- [Architecture](../Libraries/Nmsdk-MotionControlLib/Docs/Architecture.md) - library architecture
- [Component Catalog](../Libraries/Nmsdk-MotionControlLib/Docs/Component-Catalog.md) - list of all components
- [Usage Examples](../Libraries/Nmsdk-MotionControlLib/Docs/Usage-Examples.md) - practical examples
- [API Overview](../Libraries/Nmsdk-MotionControlLib/Docs/API-Overview.md) - API overview
- [Component Documentation](../Libraries/Nmsdk-MotionControlLib/Docs/Components/) - detailed documentation for each component

##### Rdk-BasicLib
- [Overview](../Libraries/Rdk-BasicLib/Docs/README.md) - main documentation page
- [Architecture](../Libraries/Rdk-BasicLib/Docs/Architecture.md) - library architecture
- [Component Catalog](../Libraries/Rdk-BasicLib/Docs/Component-Catalog.md) - list of all components
- [Usage Examples](../Libraries/Rdk-BasicLib/Docs/Usage-Examples.md) - practical examples
- [API Overview](../Libraries/Rdk-BasicLib/Docs/API-Overview.md) - API overview
- [Component Documentation](../Libraries/Rdk-BasicLib/Docs/Components/) - detailed documentation for each component

##### Rdk-CvBasicLib
- [Overview](../Libraries/Rdk-CvBasicLib/Docs/README.md) - main documentation page
- [Architecture](../Libraries/Rdk-CvBasicLib/Docs/Architecture.md) - library architecture
- [Component Catalog](../Libraries/Rdk-CvBasicLib/Docs/Component-Catalog.md) - list of all components
- [Usage Examples](../Libraries/Rdk-CvBasicLib/Docs/Usage-Examples.md) - practical examples
- [API Overview](../Libraries/Rdk-CvBasicLib/Docs/API-Overview.md) - API overview
- [Component Documentation](../Libraries/Rdk-CvBasicLib/Docs/Components/) - detailed documentation for each component

##### Rdk-HardwareLib
- [Overview](../Libraries/Rdk-HardwareLib/Docs/README.md) - main documentation page
- [Architecture](../Libraries/Rdk-HardwareLib/Docs/Architecture.md) - library architecture
- [Component Catalog](../Libraries/Rdk-HardwareLib/Docs/Component-Catalog.md) - list of all components
- [Usage Examples](../Libraries/Rdk-HardwareLib/Docs/Usage-Examples.md) - practical examples
- [API Overview](../Libraries/Rdk-HardwareLib/Docs/API-Overview.md) - API overview
- [Component Documentation](../Libraries/Rdk-HardwareLib/Docs/Components/) - detailed documentation for each component


- [Complete Libraries Documentation Index](Submodules/Libraries-Index.md)
- [Documentation Navigation Map](Submodules/Navigation-Map.md)
