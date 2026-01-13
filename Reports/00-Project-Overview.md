# Обзор проекта Nmsdk

## Назначение проекта

**Nmsdk (Neuro Modeler SDK)** - это SDK для моделирования нейронных сетей и робототехнических систем. Проект предоставляет компонентную архитектуру для создания, конфигурирования и выполнения моделей нейронных сетей, включая импульсные нейронные сети, системы управления движением и компоненты компьютерного зрения.

## Основная архитектура

Проект построен на модульной архитектуре с двумя основными уровнями:

1. **Rdk (Core)** - ядро системы, предоставляющее:
   - Компонентную систему
   - Движок выполнения
   - Систему сериализации
   - Графическую подсистему
   - Прикладной уровень (RPC, сервер, управление проектами)

2. **Libraries** - библиотеки компонентов, реализующие конкретную функциональность:
   - Базовые компоненты (IO, матрицы, статистика)
   - Компьютерное зрение (OpenCV)
   - Импульсные нейронные сети
   - Управление движением
   - Машинное обучение (Python, TensorFlow, Darknet)
   - Работа с аппаратным обеспечением

## Структура директорий

```
Nmsdk/
├── Rdk/                    # Основной модуль (ядро)
│   ├── Core/               # Исходный код ядра
│   │   ├── Engine/         # Движок, компоненты, окружение
│   │   ├── Application/    # Приложение, RPC, сервер
│   │   ├── Graphics/       # Графика и визуализация
│   │   ├── Math/          # Математические утилиты
│   │   ├── Serialize/     # Сериализация (XML, Binary)
│   │   ├── System/        # Системные утилиты
│   │   └── Utilities/     # Вспомогательные утилиты
│   ├── Deploy/            # Заголовочные файлы для использования
│   ├── GUI/               # Графический интерфейс
│   └── ThirdParty/        # Сторонние библиотеки
│
├── Libraries/              # Библиотеки компонентов
│   ├── Rdk-BasicLib/      # Базовые компоненты
│   ├── Rdk-CvBasicLib/    # Компьютерное зрение
│   ├── Rdk-HardwareLib/   # Работа с железом
│   ├── Nmsdk-PulseLib/    # Импульсные нейронные сети
│   ├── Nmsdk-MotionControlLib/  # Управление движением
│   ├── Rdk-PyMachineLearningLib/  # Python ML интеграция
│   ├── Rdk-TensorflowLib/ # TensorFlow интеграция
│   └── Rdk-DarknetLib/    # Darknet интеграция
│
├── App/                    # Приложения
│   ├── NeuroModeler/      # Основное приложение
│   └── NeuroModelerConsole/  # Консольное приложение
│
├── Build/                  # Файлы сборки (CMake, Qt, VS, etc.)
├── Bin/                    # Скомпилированные бинарники и конфиги
├── Docs/                   # Документация
└── Tests/                  # Тесты
```

## Система сборки

Проект использует **CMake** как основную систему сборки:

- Минимальная версия CMake: 3.16
- Стандарт C++: C++20
- Поддержка Qt5 (AUTOMOC, AUTOUIC, AUTORCC)
- Платформы: Linux и Windows

### Основные цели сборки

- `rdk.static.qt` - статическая библиотека ядра Rdk
- `Rdk-BasicLib.qt` - базовая библиотека
- `Rdk-CvBasicLib.qt` - библиотека компьютерного зрения
- `Rdk-HardwareLib.qt` - библиотека работы с железом
- `Nmsdk-MotionControlLib.qt` - библиотека управления движением
- `Nmsdk-PulseLib.qt` - библиотека импульсных нейросетей
- Приложения: NeuroModeler, NeuroModelerConsole

### Выходные директории

- Исполняемые файлы: `Bin/Platform/<OS>/`
- Библиотеки: `Bin/Platform/<OS>/Lib.CMake/`

## Основные зависимости

### Внешние библиотеки

- **Qt5** (Core) - для базовой функциональности
- **OpenCV** - для компьютерного зрения (через Rdk-CvBasicLib)
- **Python** - для интеграции с Python ML библиотеками (опционально)
- **TensorFlow** - для TensorFlow интеграции (опционально)
- **Darknet** - для Darknet интеграции (опционально)

### Внутренние зависимости

```
rdk.static.qt (ядро)
    ↑
    ├── Rdk-BasicLib.qt
    ├── Rdk-CvBasicLib.qt
    ├── Rdk-HardwareLib.qt
    │
    ├── Nmsdk-PulseLib.qt
    │   ├── Rdk-BasicLib.qt
    │   └── rdk.static.qt
    │
    └── Nmsdk-MotionControlLib.qt
        ├── Rdk-BasicLib.qt
        ├── Rdk-CvBasicLib.qt
        ├── Rdk-HardwareLib.qt
        └── Nmsdk-PulseLib.qt
```

## Механизм загрузки библиотек

Библиотеки загружаются через функцию `RdkLoadPredefinedLibraries()` в файле `Libraries/Libraries.cpp`:

```cpp
bool RdkLoadPredefinedLibraries(std::list<RDK::ULibrary*> &libs_list)
{
    libs_list.push_back(&RDK::BasicLibrary);
    libs_list.push_back(&RDK::CvBasicLibrary);
    libs_list.push_back(&RDK::HardwareLibrary);
    libs_list.push_back(&NMSDK::PulseLibrary);
    libs_list.push_back(&NMSDK::MotionControlLibrary);
    // ... опциональные библиотеки
}
```

## Ключевые концепции

1. **Компонентная система** - все функциональные единицы реализованы как компоненты (UComponent)
2. **Свойства (Properties)** - механизм для параметров, состояний, входов и выходов компонентов
3. **Контейнеры (Containers)** - группировка компонентов
4. **Сети (Nets)** - соединение компонентов в вычислительные сети
5. **Окружение (Environment)** - контекст выполнения компонентов
6. **Хранилище (Storage)** - реестр компонентов и их описаний

## См. также

- [01-Rdk-Core-Structure.md](01-Rdk-Core-Structure.md) - детальное описание ядра Rdk
- [02-Libraries-Overview.md](02-Libraries-Overview.md) - обзор всех библиотек
- [09-Component-System.md](09-Component-System.md) - описание компонентной системы
- [10-Build-System.md](10-Build-System.md) - детали системы сборки

