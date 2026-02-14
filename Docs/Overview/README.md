# Обзор проекта Nmsdk

## RU

### Назначение проекта

**Nmsdk (Neuro Modeler SDK)** - это SDK для моделирования нейронных сетей и робототехнических систем. Проект предоставляет компонентную архитектуру для создания, конфигурирования и выполнения моделей нейронных сетей, включая:

- Импульсные нейронные сети (Spiking Neural Networks)
- Системы управления движением и робототехника
- Компоненты компьютерного зрения на базе OpenCV
- Работа с аппаратным обеспечением (Arduino и др.)

### Ключевые подсистемы

1. **Rdk (Core)** - ядро системы
   - Компонентная система
   - Движок выполнения
   - Система сериализации (XML, Binary)
   - Графическая подсистема
   - Прикладной уровень (RPC, сервер, управление проектами)

2. **Libraries** - библиотеки компонентов
   - Базовые компоненты (IO, матрицы, статистика)
   - Компьютерное зрение (OpenCV)
   - Импульсные нейронные сети
   - Управление движением
   - Работа с аппаратным обеспечением

3. **GUI** - графический интерфейс пользователя
   - Qt-based интерфейс
   - Визуальный редактор компонентов
   - Мониторинг выполнения
   - Управление проектами

4. **Bin** - ресурсы и конфигурации
   - Конфигурационные файлы
   - Описания компонентов (ClDesc)
   - Справка пользователя
   - Стили и темы

### Основные термины

- **Компонент (Component)** - базовая функциональная единица системы
- **Свойство (Property)** - параметр, состояние, вход или выход компонента
- **Контейнер (Container)** - группа компонентов
- **Сеть (Net)** - соединение компонентов в вычислительную сеть
- **Окружение (Environment)** - контекст выполнения компонентов
- **Хранилище (Storage)** - реестр компонентов и их описаний
- **Движок (Engine)** - управление выполнением компонентов

### Быстрый старт

1. См. [Quick Start](QuickStart.md) для быстрого начала работы с проектом
2. См. [Система сборки](../Build-And-Deploy/Build-System.md) для установки зависимостей и сборки проекта
3. См. [Компонентная система](../Rdk/Docs/Guides/Component-System.md) для понимания работы с компонентами
4. См. [Обзор библиотек](../Libraries/Overview.md) для выбора нужных библиотек

### Структура проекта

- [Структура исходников](File-Structure.md) - описание структуры директорий и файлов проекта

### Дополнительная информация

- [Архитектура системы](Architecture-Overview.md) - детальное описание архитектуры
- [Rdk Core](../Rdk/Docs/Architecture/Overview.md) - документация ядра
- [GUI](../GUI/Overview.md) - документация интерфейса

---

## EN

### Project Purpose

**Nmsdk (Neuro Modeler SDK)** is an SDK for neural network modeling and robotics systems. The project provides a component-based architecture for creating, configuring, and executing neural network models, including:

- Spiking Neural Networks
- Motion control systems and robotics
- Computer vision components based on OpenCV
- Hardware integration (Arduino, etc.)

### Key Subsystems

1. **Rdk (Core)** - system core
   - Component system
   - Execution engine
   - Serialization system (XML, Binary)
   - Graphics subsystem
   - Application layer (RPC, server, project management)

2. **Libraries** - component libraries
   - Basic components (IO, matrices, statistics)
   - Computer vision (OpenCV)
   - Spiking neural networks
   - Motion control
   - Hardware integration

3. **GUI** - graphical user interface
   - Qt-based interface
   - Visual component editor
   - Execution monitoring
   - Project management

4. **Bin** - resources and configurations
   - Configuration files
   - Component descriptions (ClDesc)
   - User help
   - Styles and themes

### Key Terms

- **Component** - basic functional unit of the system
- **Property** - parameter, state, input or output of a component
- **Container** - group of components
- **Net** - connection of components into a computational network
- **Environment** - execution context for components
- **Storage** - registry of components and their descriptions
- **Engine** - component execution management

### Quick Start

1. See [Quick Start](QuickStart.md) for quick start with the project
2. See [Build System](../Build-And-Deploy/Build-System.md) for dependency installation and project build
3. See [Component System](../Components-And-Configuration/Component-System.md) to understand working with components
4. See [Libraries Overview](../Libraries/Overview.md) to choose needed libraries

### Project Structure

- [File Structure](File-Structure.md) - project directory and file structure description

### Additional Information

- [System Architecture](Architecture-Overview.md) - detailed architecture description
- [Rdk Core](../Rdk-Core/Overview.md) - core documentation
- [GUI](../GUI/Overview.md) - interface documentation
