# Структура исходников проекта (File Structure)

## RU

### Обзор

Описание структуры директорий и файлов проекта Nmsdk.

### Корневая структура

```
Nmsdk/
├── Rdk/                    # Основной модуль (ядро)
│   ├── Core/               # Исходный код ядра
│   ├── Deploy/             # Заголовочные файлы для использования
│   ├── GUI/                # Графический интерфейс
│   ├── Tests/              # Тесты
│   └── ThirdParty/         # Сторонние библиотеки
│
├── Libraries/              # Библиотеки компонентов
│   ├── Rdk-BasicLib/       # Базовые компоненты
│   ├── Rdk-CvBasicLib/     # Компьютерное зрение
│   ├── Rdk-HardwareLib/    # Работа с железом
│   ├── Nmsdk-PulseLib/     # Импульсные нейронные сети
│   ├── Nmsdk-MotionControlLib/  # Управление движением
│   ├── Rdk-PyMachineLearningLib/  # Python ML интеграция
│   ├── Rdk-TensorflowLib/  # TensorFlow интеграция
│   └── Rdk-DarknetLib/     # Darknet интеграция
│
├── Bin/                    # Скомпилированные бинарники и конфиги
│   ├── Configs/            # Конфигурационные файлы
│   ├── ClDesc/             # Описания классов компонентов
│   ├── Help/               # Справочная документация
│   ├── Styles/             # Стили и темы
│   └── Platform/           # Платформенные артефакты
│
├── Build/                  # Файлы сборки (CMake, Qt, VS, etc.)
├── Docs/                   # Документация
├── Docs.old/               # Старая документация
├── Reports/                # Отчеты и анализ
└── CMakeLists.txt          # Корневой файл сборки
```

### Структура Rdk

```
Rdk/
├── Core/                   # Исходный код ядра
│   ├── Application/        # Приложение, RPC, сервер
│   │   ├── UApplication.h/cpp
│   │   ├── UEngineControl.h/cpp
│   │   ├── URpcDispatcher.h/cpp
│   │   ├── UProject.h/cpp
│   │   ├── Qt/            # Qt реализация
│   │   └── Bcb/           # Borland C++ Builder реализация
│   ├── Engine/             # Движок, компоненты, окружение
│   │   ├── UEngine.h/cpp
│   │   ├── UComponent.h/cpp
│   │   ├── UContainer.h/cpp
│   │   ├── UNet.h/cpp
│   │   ├── UStorage.h/cpp
│   │   ├── UEnvironment.h/cpp
│   │   ├── UProperty.h
│   │   └── UPropertyEndpoints.h
│   ├── Graphics/           # Графика и визуализация
│   │   ├── UGraphics.h/cpp
│   │   ├── UDrawEngine.h/cpp
│   │   ├── UBitmap.h/cpp
│   │   └── UFont.h
│   ├── Math/              # Математические утилиты
│   │   └── MVector.h      # Векторы и матрицы
│   ├── Serialize/          # Сериализация (XML, Binary)
│   │   ├── USerStorage.h
│   │   ├── USerStorageXML.h/cpp
│   │   └── USerStorageBinary.h/cpp
│   ├── System/            # Системные утилиты
│   │   ├── rdk_system.h
│   │   ├── UGenericMutex.h
│   │   ├── UGenericEvent.h
│   │   ├── UDllLoader.h
│   │   ├── Qt/            # Qt реализации
│   │   ├── Win/           # Windows реализации
│   │   └── Gcc/           # GCC/POSIX реализации
│   ├── Utilities/          # Вспомогательные утилиты
│   │   └── UIniFile.h     # Работа с INI файлами
│   └── Console/           # Консольный движок
│       └── UConsoleEngine.h/cpp
├── Deploy/                # Заголовочные файлы
│   └── Include/           # Публичные заголовки
│       ├── rdk.h
│       ├── rdk_application.h
│       └── rdk_init.h
├── GUI/                   # Графический интерфейс
│   ├── Qt/               # Qt реализация GUI
│   │   ├── UGEngineControlWidget.h/cpp
│   │   ├── UModernDiagramWidget.h/cpp
│   │   ├── UStyleManager.h/cpp
│   │   └── Styles/       # QSS и JSON темы
│   └── BCB/              # Borland C++ Builder GUI
├── Tests/                 # Тесты
│   ├── Unit/             # Юнит-тесты
│   └── Integration/      # Интеграционные тесты
└── ThirdParty/           # Сторонние библиотеки
```

**Зависимости между модулями Core:**

```mermaid
flowchart TB
    Application[Application] --> Engine[Engine]
    Application --> Serialize[Serialize]
    Engine --> Graphics[Graphics]
    Engine --> Serialize
    Engine --> System[System]
    Engine --> Math[Math]
    Graphics --> Math
    Serialize --> System
    Application --> Utilities[Utilities]
```

### Структура Libraries

Каждая библиотека следует общей структуре:

```
LibraryName/
├── Core/                  # Исходный код компонентов
│   ├── Component1.h
│   ├── Component1.cpp
│   └── ...
├── Deploy/                # Заголовочные файлы
│   └── Include/
│       └── Lib.h          # Главный заголовок
├── CMake/                 # Файлы сборки CMake
│   └── CMakeLists.txt
├── Build/                 # Файлы сборки для различных IDE
├── Docs/                  # Документация библиотеки
└── Tests/                 # Тесты библиотеки
```

### Структура Bin

```
Bin/
├── Configs/               # Конфигурационные файлы проектов
├── ClDesc/                # Описания классов компонентов (XML)
├── Help/                  # Справочная документация
│   ├── en/               # Английская версия
│   └── ru/               # Русская версия
├── Styles/                # Стили и темы GUI
└── Platform/              # Платформенные артефакты
    ├── Linux/            # Linux специфичные файлы
    └── Win/              # Windows специфичные файлы
```

### См. также

- [Архитектура системы](Architecture-Overview.md) - архитектурное описание
- [Build System](../Build-And-Deploy/Build-System.md) - система сборки

---

## EN

### Overview

Description of Nmsdk project directory and file structure.

### Root Structure

### Rdk Structure

### Libraries Structure

Each library follows a common structure.

### Bin Structure

### See Also

- [System Architecture](Architecture-Overview.md) - architectural description
- [Build System](../Build-And-Deploy/Build-System.md) - build system
