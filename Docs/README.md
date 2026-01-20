# Документация Nmsdk

## RU

Добро пожаловать в документацию проекта **Nmsdk (Neuro Modeler SDK)** - SDK для моделирования нейронных сетей и робототехнических систем.

### Навигация

#### Общие разделы

- [Обзор проекта](Overview/README.md) - высокоуровневое описание Nmsdk, назначение, ключевые подсистемы
- [Быстрый старт](Overview/QuickStart.md) - быстрое начало работы с проектом
- [Структура исходников](Overview/File-Structure.md) - структура директорий и файлов проекта
- [Архитектура системы](Overview/Architecture-Overview.md) - верхнеуровневая архитектура с диаграммами

#### Основные компоненты

- [Rdk Core](Rdk-Core/Overview.md) - ядро системы, движок, компонентная система
  - [Архитектура приложения](Rdk-Core/Application-Architecture.md) - RPC, сервер, управление проектами
  - [Архитектура движка](Rdk-Core/Engine-Architecture.md) - компоненты, контейнеры, свойства
  - [Графика](Rdk-Core/Graphics-Architecture.md) - система графики и визуализации
  - [Сериализация](Rdk-Core/Serialize-Architecture.md) - XML и бинарная сериализация
  - [Системные абстракции](Rdk-Core/System-Platform-Abstraction.md) - кроссплатформенные абстракции

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
- [Rdk-PyMachineLearningLib](Libraries/Rdk-PyMachineLearningLib.md) - интеграция с Python ML
- [Rdk-TensorflowLib](Libraries/Rdk-TensorflowLib.md) - интеграция с TensorFlow
- [Rdk-DarknetLib](Libraries/Rdk-DarknetLib.md) - интеграция с Darknet

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

### Документация в сабрепозиториях

- [Rdk/Docs](../Rdk/Docs/README.md) - детальная документация ядра Rdk
- [Bin/Docs](../Bin/Docs/README.md) - документация по конфигурациям и ресурсам
- Документация библиотек в соответствующих каталогах `Libraries/<LibName>/Docs/`

---

## EN

Welcome to the documentation of **Nmsdk (Neuro Modeler SDK)** - SDK for neural network modeling and robotics systems.

### Navigation

#### General Sections

- [Project Overview](Overview/README.md) - high-level description of Nmsdk, purpose, key subsystems
- [Quick Start](Overview/QuickStart.md) - quick start with the project
- [File Structure](Overview/File-Structure.md) - project directory and file structure
- [System Architecture](Overview/Architecture-Overview.md) - top-level architecture with diagrams

#### Core Components

- [Rdk Core](Rdk-Core/Overview.md) - system core, engine, component system
  - [Application Architecture](Rdk-Core/Application-Architecture.md) - RPC, server, project management
  - [Engine Architecture](Rdk-Core/Engine-Architecture.md) - components, containers, properties
  - [Graphics](Rdk-Core/Graphics-Architecture.md) - graphics and visualization system
  - [Serialization](Rdk-Core/Serialize-Architecture.md) - XML and binary serialization
  - [System Abstractions](Rdk-Core/System-Platform-Abstraction.md) - cross-platform abstractions

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
- [Rdk-PyMachineLearningLib](Libraries/Rdk-PyMachineLearningLib.md) - Python ML integration
- [Rdk-TensorflowLib](Libraries/Rdk-TensorflowLib.md) - TensorFlow integration
- [Rdk-DarknetLib](Libraries/Rdk-DarknetLib.md) - Darknet integration

#### Build and Deploy

- [Build System](Build-And-Deploy/Build-System.md) - CMake, dependencies, build process
- [Cross-Platform Support](Build-And-Deploy/Cross-Platform.md) - Linux, Windows
- [Building on Windows](Build-And-Deploy/Build-Windows.md) - Windows-specific build details
- [Building on Linux](Build-And-Deploy/Build-Linux.md) - Linux-specific build details

#### Components and Configuration

- [Component System](Components-And-Configuration/Component-System.md) - creating and using components
- [Configuration Files](Components-And-Configuration/Configuration-Files-Overview.md) - config structure
- [Direct Property Access](Components-And-Configuration/Direct-Property-Access.md) - property access optimization

#### Performance and Testing

- [Performance](Performance-And-Testing/Performance-Overview.md) - optimizations, benchmarks
- [Testing Strategy](Performance-And-Testing/Testing-Strategy.md) - unit and integration tests

#### Refactoring History

- [Refactoring Timeline](Refactoring-History/Refactoring-Timeline.md) - major changes
- [Lessons Learned](Refactoring-History/Lessons-Learned.md) - important insights and practices

### Documentation in Subrepositories

- [Rdk/Docs](../Rdk/Docs/README.md) - detailed Rdk core documentation
- [Bin/Docs](../Bin/Docs/README.md) - configuration and resources documentation
- Library documentation in respective `Libraries/<LibName>/Docs/` directories
