# Getting Started - Начало работы

## RU

### Назначение

Это руководство поможет вам быстро начать работу с Nmsdk в зависимости от вашей роли и задач.

### Для новых пользователей

#### Шаг 1: Установка

1. Следуйте инструкциям в [QuickStart.md](Overview/QuickStart.md)
2. Установите зависимости для вашей платформы
3. Соберите проект

#### Шаг 2: Первый запуск

1. Запустите NeuroModeler
2. Изучите интерфейс
3. Откройте пример проекта из `Bin/Configs/`

#### Шаг 3: Создание первого проекта

1. Создайте новый проект
2. Добавьте компоненты из библиотеки
3. Соедините компоненты
4. Запустите выполнение

**Рекомендуемые ресурсы:**
- [QuickStart.md](Overview/QuickStart.md) - быстрый старт
- [Component System](Rdk/Docs/Guides/Component-System.md) - работа с компонентами
- [GUI Overview](GUI/Overview.md) - интерфейс приложения

### Для разработчиков компонентов

#### Шаг 1: Изучите основы Rdk Core

1. [Rdk Core Overview](Rdk/Docs/Architecture/Overview.md) - обзор ядра
2. [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) - быстрый старт для разработчиков
3. [Rdk/Docs/Guides/Creating-Components.md](../Rdk/Docs/Guides/Creating-Components.md) - создание компонентов

#### Шаг 2: Создайте первый компонент

1. Следуйте руководству [Rdk/Docs/Guides/Creating-Components.md](../Rdk/Docs/Guides/Creating-Components.md)
2. Изучите примеры в [Rdk/Docs/Examples/](../Rdk/Docs/Examples/)
3. Создайте простой компонент

#### Шаг 3: Добавьте компонент в библиотеку

1. Создайте или выберите библиотеку
2. Зарегистрируйте компонент
3. Создайте ClDesc для компонента
4. Протестируйте компонент

**Рекомендуемые ресурсы:**
- [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) - быстрый старт
- [Component Development Guide](Rdk/Docs/Guides/Component-Development.md) - разработка компонентов
- [Rdk/Docs/FAQ.md](../Rdk/Docs/FAQ.md) - FAQ по Rdk Core

### Для разработчиков библиотек

#### Шаг 1: Изучите архитектуру

1. [Architecture Overview](Overview/Architecture-Overview.md) - общая архитектура
2. [Rdk Core Overview](Rdk/Docs/Architecture/Overview.md) - ядро системы
3. [Development-Guides/Library-Development.md](Development-Guides/Library-Development.md) - разработка библиотек

#### Шаг 2: Создайте структуру библиотеки

1. Создайте функцию загрузки библиотеки
2. Регистрируйте компоненты
3. Создайте документацию

#### Шаг 3: Реализуйте компоненты

1. Создайте компоненты библиотеки
2. Реализуйте сериализацию
3. Добавьте тесты

**Рекомендуемые ресурсы:**
- [Development-Guides/Library-Development.md](Development-Guides/Library-Development.md) - разработка библиотек
- [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) - быстрый старт для разработчиков
- Примеры существующих библиотек в `Libraries/`

### Для исследователей (научное использование)

#### Шаг 1: Изучите доступные библиотеки

1. [Libraries Overview](Libraries/Overview.md) - обзор всех библиотек
2. [Nmsdk-PulseLib](Libraries/Nmsdk-PulseLib.md) - импульсные нейронные сети
3. [Nmsdk-PulseLib/Docs/Scientific-Background.md](../Libraries/Nmsdk-PulseLib/Docs/Scientific-Background.md) - научный фон

#### Шаг 2: Изучите примеры конфигураций

1. `Bin/Configs/Users/User/CognitiveNavigation/` - когнитивная навигация
2. `Bin/Configs/!OldConfigs/` - различные эксперименты
3. [Nmsdk-PulseLib/Docs/Config-Templates.md](../Libraries/Nmsdk-PulseLib/Docs/Config-Templates.md) - шаблоны экспериментов

#### Шаг 3: Создайте свой эксперимент

1. Используйте существующие шаблоны
2. Адаптируйте под свои задачи
3. Запустите эксперимент

**Рекомендуемые ресурсы:**
- [Nmsdk-PulseLib Documentation](../Libraries/Nmsdk-PulseLib/Docs/README.md) - документация библиотеки
- [Nmsdk-PulseLib/Docs/Config-Templates.md](../Libraries/Nmsdk-PulseLib/Docs/Config-Templates.md) - шаблоны
- [Nmsdk-PulseLib/Docs/Usage-Examples.md](../Libraries/Nmsdk-PulseLib/Docs/Usage-Examples.md) - примеры

### Для интеграторов

#### Шаг 1: Изучите API

1. [Rdk/Docs/API-Reference.md](../Rdk/Docs/API-Reference.md) - полный справочник API
2. [Application Architecture](Rdk/Docs/Architecture/Application-Architecture.md) - работа с приложением
3. [Rdk/Docs/Guides/RPC-Integration.md](../Rdk/Docs/Guides/RPC-Integration.md) - интеграция RPC

#### Шаг 2: Интеграция в приложение

1. Инициализируйте `UApplication`
2. Загрузите необходимые библиотеки
3. Создайте и настройте `UEngine`

#### Шаг 3: Работа с проектами

1. Загружайте проекты из конфигураций
2. Управляйте выполнением
3. Интегрируйте RPC (если нужно)

**Рекомендуемые ресурсы:**
- [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) - быстрый старт для интеграторов
- [Rdk/Docs/API-Reference.md](../Rdk/Docs/API-Reference.md) - API справочник
- [Application Architecture](Rdk/Docs/Architecture/Application-Architecture.md) - архитектура приложения

### Чеклисты для начала работы

#### Для новых пользователей

- [ ] Проект собран и запускается
- [ ] Интерфейс изучен
- [ ] Пример проекта открыт и выполнен
- [ ] Создан первый простой проект
- [ ] Компоненты соединены и работают

#### Для разработчиков компонентов

- [ ] Изучена архитектура Rdk Core
- [ ] Понятен жизненный цикл компонента
- [ ] Создан первый простой компонент
- [ ] Компонент зарегистрирован и протестирован
- [ ] Создана документация компонента

#### Для разработчиков библиотек

- [ ] Изучена архитектура проекта
- [ ] Создана структура библиотеки
- [ ] Реализованы компоненты библиотеки
- [ ] Библиотека протестирована
- [ ] Создана документация библиотеки

#### Для исследователей

- [ ] Изучены доступные библиотеки
- [ ] Понятны примеры конфигураций
- [ ] Создан первый эксперимент
- [ ] Эксперимент выполнен успешно

#### Для интеграторов

- [ ] Изучен API Reference
- [ ] Понятна работа с Application
- [ ] Реализована базовая интеграция
- [ ] Интеграция протестирована

### Следующие шаги

- [FAQ.md](FAQ.md) - ответы на часто задаваемые вопросы
- [Best-Practices.md](Best-Practices.md) - лучшие практики
- [Troubleshooting Guide](Troubleshooting/Troubleshooting-Guide.md) - устранение неполадок
- [Examples/](Examples/) - практические примеры

---

## EN

### Purpose

This guide will help you quickly get started with Nmsdk depending on your role and tasks.

### For New Users

#### Step 1: Installation

1. Follow instructions in [QuickStart.md](Overview/QuickStart.md)
2. Install dependencies for your platform
3. Build the project

#### Step 2: First Launch

1. Launch NeuroModeler
2. Study the interface
3. Open example project from `Bin/Configs/`

#### Step 3: Creating Your First Project

1. Create a new project
2. Add components from library
3. Connect components
4. Start execution

**Recommended Resources:**
- [QuickStart.md](Overview/QuickStart.md) - quick start
- [Component System](Components-And-Configuration/Component-System.md) - working with components
- [GUI Overview](GUI/Overview.md) - application interface

### For Component Developers

#### Step 1: Learn Rdk Core Basics

1. [Rdk Core Overview](Rdk-Core/Overview.md) - core overview
2. [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) - quick start for developers
3. [Rdk/Docs/Guides/Creating-Components.md](../Rdk/Docs/Guides/Creating-Components.md) - creating components

#### Step 2: Create Your First Component

1. Follow guide [Rdk/Docs/Guides/Creating-Components.md](../Rdk/Docs/Guides/Creating-Components.md)
2. Study examples in [Rdk/Docs/Examples/](../Rdk/Docs/Examples/)
3. Create a simple component

#### Step 3: Add Component to Library

1. Create or select a library
2. Register the component
3. Create ClDesc for component
4. Test the component

**Recommended Resources:**
- [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) - quick start
- [Development-Guides/Component-Development.md](Development-Guides/Component-Development.md) - component development
- [Rdk/Docs/FAQ.md](../Rdk/Docs/FAQ.md) - Rdk Core FAQ

### For Library Developers

#### Step 1: Study Architecture

1. [Architecture Overview](Overview/Architecture-Overview.md) - general architecture
2. [Rdk Core Overview](Rdk-Core/Overview.md) - system core
3. [Development-Guides/Library-Development.md](Development-Guides/Library-Development.md) - library development

#### Step 2: Create Library Structure

1. Create library loading function
2. Register components
3. Create documentation

#### Step 3: Implement Components

1. Create library components
2. Implement serialization
3. Add tests

**Recommended Resources:**
- [Development-Guides/Library-Development.md](Development-Guides/Library-Development.md) - library development
- [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) - quick start for developers
- Examples of existing libraries in `Libraries/`

### For Researchers (Scientific Use)

#### Step 1: Study Available Libraries

1. [Libraries Overview](Libraries/Overview.md) - overview of all libraries
2. [Nmsdk-PulseLib](Libraries/Nmsdk-PulseLib.md) - spiking neural networks
3. [Nmsdk-PulseLib/Docs/Scientific-Background.md](../Libraries/Nmsdk-PulseLib/Docs/Scientific-Background.md) - scientific background

#### Step 2: Study Configuration Examples

1. `Bin/Configs/Users/User/CognitiveNavigation/` - cognitive navigation
2. `Bin/Configs/!OldConfigs/` - various experiments
3. [Nmsdk-PulseLib/Docs/Config-Templates.md](../Libraries/Nmsdk-PulseLib/Docs/Config-Templates.md) - experiment templates

#### Step 3: Create Your Experiment

1. Use existing templates
2. Adapt to your tasks
3. Run experiment

**Recommended Resources:**
- [Nmsdk-PulseLib Documentation](../Libraries/Nmsdk-PulseLib/Docs/README.md) - library documentation
- [Nmsdk-PulseLib/Docs/Config-Templates.md](../Libraries/Nmsdk-PulseLib/Docs/Config-Templates.md) - templates
- [Nmsdk-PulseLib/Docs/Usage-Examples.md](../Libraries/Nmsdk-PulseLib/Docs/Usage-Examples.md) - examples

### For Integrators

#### Step 1: Study API

1. [Rdk/Docs/API-Reference.md](../Rdk/Docs/API-Reference.md) - complete API reference
2. [Rdk-Core/Application-Architecture.md](Rdk-Core/Application-Architecture.md) - working with application
3. [Rdk/Docs/Guides/RPC-Integration.md](../Rdk/Docs/Guides/RPC-Integration.md) - RPC integration

#### Step 2: Application Integration

1. Initialize `UApplication`
2. Load necessary libraries
3. Create and configure `UEngine`

#### Step 3: Working with Projects

1. Load projects from configurations
2. Manage execution
3. Integrate RPC (if needed)

**Recommended Resources:**
- [Rdk/Docs/Getting-Started.md](../Rdk/Docs/Getting-Started.md) - quick start for integrators
- [Rdk/Docs/API-Reference.md](../Rdk/Docs/API-Reference.md) - API reference
- [Rdk-Core/Application-Architecture.md](Rdk-Core/Application-Architecture.md) - application architecture

### Getting Started Checklists

#### For New Users

- [ ] Project built and launches
- [ ] Interface studied
- [ ] Example project opened and executed
- [ ] First simple project created
- [ ] Components connected and working

#### For Component Developers

- [ ] Rdk Core architecture studied
- [ ] Component lifecycle understood
- [ ] First simple component created
- [ ] Component registered and tested
- [ ] Component documentation created

#### For Library Developers

- [ ] Project architecture studied
- [ ] Library structure created
- [ ] Library components implemented
- [ ] Library tested
- [ ] Library documentation created

#### For Researchers

- [ ] Available libraries studied
- [ ] Configuration examples understood
- [ ] First experiment created
- [ ] Experiment executed successfully

#### For Integrators

- [ ] API Reference studied
- [ ] Application usage understood
- [ ] Basic integration implemented
- [ ] Integration tested

### Next Steps

- [FAQ.md](FAQ.md) - frequently asked questions
- [Best-Practices.md](Best-Practices.md) - best practices
- [Troubleshooting Guide](Troubleshooting/Troubleshooting-Guide.md) - troubleshooting
- [Examples/](Examples/) - practical examples
